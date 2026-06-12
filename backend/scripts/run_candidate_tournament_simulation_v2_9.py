"""Run the non-active V2.8 candidate matrix through conditioned group simulation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, load_json
from backend.scripts.v2_9_dual_matrix_utils import CANDIDATE_VERSION, ENGINE, VERSION, joined_candidate_matches, locked_results, publish, utc_now
from backend.simulation.worldcup_tournament_simulator_v2_6 import simulate_conditioned


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--simulations", type=int, default=50000)
    args = parser.parse_args(argv)
    locked = locked_results()
    simulated = simulate_conditioned(joined_candidate_matches(), locked, args.simulations)
    active = load_json(DATA_DIR / "generated" / "worldcup_tournament_simulation_conditioned_v2_6.json")
    payload = {
        "generated_at": utc_now(), "version": VERSION, "engine_version": ENGINE, "candidate_version": CANDIDATE_VERSION,
        "candidate_status": "alternative_non_active", "simulation_count": args.simulations, "fixture_count": 72,
        "finished_matches_locked": len(locked), "future_matches_simulated": 72 - len(locked),
        "group_stage_simulation_available": True, "full_tournament_simulation_available": False,
        "teams": simulated["teams"], "groups": simulated["groups"],
        "qualification_probabilities": {team: row["qualification_probability"] for team, row in simulated["teams"].items()},
        "group_rank_probabilities": {team: {key: value for key, value in row.items() if key.startswith("finish_")} for team, row in simulated["teams"].items()},
        "qualification_rule": active["qualification_rule"],
        "limitations": [
            "Projection alternative non active; this is not the official tournament forecast.",
            "Finished official results are locked; live matches are not locked.",
            "Group stage only; no knockout bracket is invented.",
            "Monte Carlo deltas include bounded sampling variation.",
        ],
    }
    publish(payload, "worldcup_tournament_simulation_candidate_v2_9.json")
    (ROOT / "docs" / "WORLDCUP_TOURNAMENT_SIMULATION_CANDIDATE_V2_9.md").write_text(f"""# World Cup Tournament Simulation Candidate V2.9

V2.9 ran `{args.simulations:,}` group-stage simulations with the V2.8 alternative score matrix. `{len(locked)}` finished official result(s) are locked and `{72-len(locked)}` future match(es) are simulated.

This is a **Projection alternative**, **Non active**, and not the official tournament forecast. The active V2.6 conditioned simulation remains the product reference. The candidate simulation exists to measure how less-conservative score distributions affect qualification, group ranks, goal difference and the projected-campaign proxy.

The simulation covers the group stage only. No knockout bracket, opponent or champion probability is invented. Monte Carlo variation remains present even though active and candidate runs share the same deterministic seed.
""", encoding="utf-8")
    print(json.dumps({"simulations": args.simulations, "locked": len(locked), "future": 72-len(locked)}))


if __name__ == "__main__":
    main()
