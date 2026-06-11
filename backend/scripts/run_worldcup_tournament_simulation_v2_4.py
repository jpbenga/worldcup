"""Run the V2.4 World Cup group-stage tournament simulation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, load_json, utc_now
from backend.scripts.v2_4_release_utils import ENGINE_VERSION, VERSION, publish
from backend.simulation.worldcup_tournament_simulator_v2_4 import simulate_groups


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--simulations", type=int, default=50000)
    args = parser.parse_args(argv)
    rc = load_json(DATA_DIR / "generated" / "worldcup_2026_predictions_release_candidate_v2_4.json")
    matches = rc["matches"] if isinstance(rc, dict) else rc
    if len(matches) != 72 or any(match.get("stage") != "group" for match in matches):
        raise SystemExit("V2.4 simulation requires exactly the 72 available group-stage fixtures.")
    result = simulate_groups(matches, args.simulations)
    teams = result["teams"]
    payload = {
        "generated_at": utc_now(), "version": VERSION, "engine_version": ENGINE_VERSION, "simulation_count": args.simulations,
        "fixture_count": len(matches), "full_tournament_simulation_available": False, "group_stage_simulation_available": True,
        "teams": teams, "groups": result["groups"],
        "qualification_probabilities": {team: item["qualification_probability"] for team, item in teams.items()},
        "group_rank_probabilities": {team: {key: value for key, value in item.items() if key.startswith("finish_")} for team, item in teams.items()},
        "qualification_rule": "Top two in each of 12 groups plus the eight best third-placed teams.",
        "limitations": ["Only 72 group-stage fixtures are available.", "No knockout bracket is invented.", "Ties use points, goal difference, goals scored, then a seeded random tie-break because complete official tie-break inputs are unavailable."],
    }
    publish(payload, "worldcup_tournament_simulation_v2_4.json")
    top_qual = sorted(payload["qualification_probabilities"].items(), key=lambda item: item[1], reverse=True)[:10]
    (ROOT / "docs" / "WORLDCUP_TOURNAMENT_SIMULATION_V2_4.md").write_text(
        f"""# World Cup Tournament Simulation V2.4

V2.4 runs `{args.simulations:,}` deterministic-seed tournament simulations from the 72 active group-stage score matrices. It calculates each team's probability of finishing first, second, third or fourth, qualifying through the top two or best-third route, and being eliminated in the group.

Full tournament simulation available: `false`. The repository does not contain knockout fixtures or a complete bracket, so V2.4 does not invent one. Qualification follows the 2026 group rule: the top two in each of 12 groups plus the eight best third-placed teams.

Top qualification probabilities: `{top_qual}`. Tie resolution uses points, goal difference and goals scored, then a seeded random tie-break because complete official disciplinary and head-to-head tie-break inputs are unavailable.
""", encoding="utf-8")
    print(f"V2.4 simulation complete: {args.simulations} simulations, {len(matches)} fixtures, {len(teams)} teams")


if __name__ == "__main__":
    main()
