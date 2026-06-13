"""Build the frontend view model for the interactive Road to the Trophy page."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, utc_now, write_json

OUTPUT = "road_to_the_trophy_view_model_v2_13_1B.json"
ROUND_LABELS = {
    "round_of_32": "16es de finale",
    "round_of_16": "8es de finale",
    "quarter_finals": "Quarts de finale",
    "semi_finals": "Demi-finales",
    "final": "Finale",
}


def publish(payload: dict[str, Any]) -> None:
    generated = DATA_DIR / "generated" / OUTPUT
    write_json(payload, generated)
    shutil.copy2(generated, DATA_DIR / "snapshots" / OUTPUT)
    shutil.copy2(generated, FRONTEND_DATA_DIR / OUTPUT)


def main() -> None:
    groups = load_json(FRONTEND_DATA_DIR / "worldcup_groups.json")
    scenario = load_json(DATA_DIR / "generated" / "living_worldcup_scenario_v2_13.json")
    engine = load_json(DATA_DIR / "generated" / "road_to_the_trophy_scenario_engine_v2_13_1B.json")
    mapping = load_json(DATA_DIR / "generated" / "worldcup_2026_official_bracket_mapping_v2_13_1B.json")
    qualifiers = scenario["group_stage"]["projected_qualifiers"]

    group_views = []
    for group in groups:
        code = group["group"]
        projected = [team for team in qualifiers if team["group"] == code]
        group_views.append(
            {
                "group": code,
                "label": group["group_label"],
                "teams": group["teams"],
                "matches": group["matches"],
                "standings": group["standings"],
                "standings_available": group["standings_available"],
                "projected_qualifiers": projected,
                "knockout_links": sorted(
                    {
                        match["match_id"]
                        for match in scenario["knockout_path"]["rounds"]["round_of_32"]
                        for team in projected
                        if team["team"] in (match["team_a"], match["team_b"])
                    }
                ),
            }
        )

    rounds = []
    for key, label in ROUND_LABELS.items():
        rounds.append(
            {
                "key": key,
                "label": label,
                "matches": [
                    {**match, "display_status": "projected", "confirmation_status": "to_confirm"}
                    for match in scenario["knockout_path"]["rounds"][key]
                ],
            }
        )

    publish(
        {
            "version": "v2.13.1B",
            "generated_at": utc_now(),
            "title": "Road to the Trophy",
            "scenario_status_label": scenario["scenario_status_label"],
            "simulation_count": scenario["simulations"],
            "target_match_count": 104,
            "result_summary": scenario["result_summary"],
            "projected_winner": scenario["tournament_winner_projected"],
            "projected_final": scenario["final_projected"],
            "groups": group_views,
            "rounds": rounds,
            "third_place": {"status": "to_confirm", "official": False, "match": None},
            "team_paths": engine["team_paths"],
            "status_filters": ["all", "real", "projected", "to_confirm"],
            "official_mapping": mapping,
            "limitations": engine["limitations"],
        }
    )
    print("Road to the Trophy view model published.")


if __name__ == "__main__":
    main()
