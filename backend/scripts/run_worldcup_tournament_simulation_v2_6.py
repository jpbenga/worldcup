"""Run a 50,000-scenario group simulation conditioned on finished results."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, load_json, utc_now
from backend.scripts.v2_6_live_utils import ENGINE_VERSION, VERSION, publish, release_matches
from backend.simulation.worldcup_tournament_simulator_v2_6 import simulate_conditioned


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--simulations", type=int, default=50000)
    args = parser.parse_args(argv)
    results = load_json(DATA_DIR / "generated" / "worldcup_2026_results_v2_6.json")
    locked = {item["match_id"]: (int(item["actual_score"]["home"]), int(item["actual_score"]["away"])) for item in results["fixtures"] if item["status"] == "finished" and item["actual_score"]["home"] is not None}
    simulated = simulate_conditioned(release_matches(), locked, args.simulations)
    prior = load_json(DATA_DIR / "generated" / "worldcup_tournament_simulation_v2_4.json")
    teams = simulated["teams"]
    changes = {team: item["qualification_probability"] - prior["qualification_probabilities"][team] for team, item in teams.items()}
    report = {
        "generated_at": utc_now(), "version": VERSION, "engine_version": ENGINE_VERSION, "simulation_count": args.simulations,
        "fixture_count": 72, "finished_matches_locked": len(locked), "future_matches_simulated": 72 - len(locked),
        "group_stage_simulation_available": True, "full_tournament_simulation_available": False,
        "teams": teams, "groups": simulated["groups"],
        "qualification_probabilities": {team: item["qualification_probability"] for team, item in teams.items()},
        "group_rank_probabilities": {team: {key: value for key, value in item.items() if key.startswith("finish_")} for team, item in teams.items()},
        "changes_vs_v2_4": changes,
        "largest_rises": sorted(changes.items(), key=lambda item: item[1], reverse=True)[:5],
        "largest_falls": sorted(changes.items(), key=lambda item: item[1])[:5],
        "qualification_rule": prior["qualification_rule"],
        "limitations": ["Live matches are not locked.", "No knockout bracket is invented.", *prior["limitations"][2:]],
    }
    publish(report, "worldcup_tournament_simulation_conditioned_v2_6.json")
    (ROOT / "docs" / "WORLDCUP_TOURNAMENT_SIMULATION_CONDITIONED_V2_6.md").write_text(
        f"""# World Cup Tournament Simulation Conditioned V2.6

V2.6 ran `{args.simulations:,}` group-stage scenarios with `{len(locked)}` finished match(es) locked to their official score and `{72-len(locked)}` future match(es) sampled from frozen pre-match matrices. Live matches are never treated as final.

Largest qualification rises versus V2.4: `{report["largest_rises"]}`. Largest falls: `{report["largest_falls"]}`. The comparison also includes Monte Carlo variation; no model probability was retrained or rewritten.
""", encoding="utf-8")
    print(f"V2.6 conditioned simulation: locked={len(locked)}, simulated={72-len(locked)}")


if __name__ == "__main__":
    main()
