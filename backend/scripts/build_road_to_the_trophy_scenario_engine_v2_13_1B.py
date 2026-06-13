"""Publish the interactive Road to the Trophy scenario contract."""

from __future__ import annotations

import shutil
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, utc_now, write_json

VERSION = "v2.13.1B"


def publish(name: str, payload: dict[str, Any]) -> None:
    generated = DATA_DIR / "generated" / name
    write_json(payload, generated)
    shutil.copy2(generated, DATA_DIR / "snapshots" / name)
    shutil.copy2(generated, FRONTEND_DATA_DIR / name)


def main() -> None:
    scenario = load_json(DATA_DIR / "generated" / "living_worldcup_scenario_v2_13.json")
    paths = load_json(DATA_DIR / "generated" / "representative_tournament_paths_v2_13.json")
    team_paths: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for round_name, matches in scenario["knockout_path"]["rounds"].items():
        for match in matches:
            for team, opponent, probability in (
                (match["team_a"], match["team_b"], match["team_a_win_probability"]),
                (match["team_b"], match["team_a"], match["team_b_win_probability"]),
            ):
                team_paths[team].append(
                    {
                        "round": round_name,
                        "match_id": match["match_id"],
                        "opponent": opponent,
                        "advance_probability": probability,
                        "projected_to_advance": match["projected_winner"] == team,
                    }
                )

    engine = {
        "version": VERSION,
        "generated_at": utc_now(),
        "scenario_source": "living_worldcup_scenario_v2_13",
        "simulation_count": scenario["simulations"],
        "full_simulated_paths_available": False,
        "representative_scenario_method": "coherent_fixed_derived_bracket_most_likely_advancement_path",
        "projected_winner": scenario["tournament_winner_projected"],
        "most_common_final": paths["most_common_final"],
        "round_matchups": scenario["knockout_path"]["rounds"],
        "team_paths": dict(sorted(team_paths.items())),
        "limitations": [
            "The source simulation did not persist all 50,000 complete tournament paths.",
            "The representative path is coherent inside one simulation-derived projected bracket.",
            "Official knockout fixtures and best-third assignments are not available yet.",
        ],
    }
    mapping = {
        "version": VERSION,
        "generated_at": utc_now(),
        "official_bracket_available": False,
        "expected_knockout_matches": 32,
        "discovered_official_knockout_matches": 0,
        "expected_match_numbers": {"from": 73, "to": 104},
        "required_rounds": {
            "round_of_32": 16,
            "round_of_16": 8,
            "quarter_finals": 4,
            "semi_finals": 2,
            "third_place": 1,
            "final": 1,
        },
        "fallback": "simulation_derived_projection",
        "missing_official_components": [
            "Official fixtures for matches 73 to 104",
            "Official group-position to round-of-32 slot mapping",
            "Confirmed best-third assignment combinations",
        ],
    }
    publish("road_to_the_trophy_scenario_engine_v2_13_1B.json", engine)
    publish("worldcup_2026_official_bracket_mapping_v2_13_1B.json", mapping)
    print("Road to the Trophy scenario engine and mapping published.")


if __name__ == "__main__":
    main()
