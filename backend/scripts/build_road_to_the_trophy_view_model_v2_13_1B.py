"""Build the rich frontend view model for the Road to the Trophy tournament atlas."""

from __future__ import annotations

import shutil
import sys
from collections import Counter
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
ROUND_KEYS = list(ROUND_LABELS)


def publish(payload: dict[str, Any]) -> None:
    generated = DATA_DIR / "generated" / OUTPUT
    write_json(payload, generated)
    shutil.copy2(generated, DATA_DIR / "snapshots" / OUTPUT)
    shutil.copy2(generated, FRONTEND_DATA_DIR / OUTPUT)


def group_state(rows: list[dict[str, Any]]) -> str:
    probabilities = sorted((row["qualification_probability"] for row in rows), reverse=True)
    cutoff_gap = probabilities[2] - probabilities[3]
    return "stable" if cutoff_gap >= 0.28 else "open" if cutoff_gap >= 0.12 else "volatile"


def match_view(match: dict[str, Any]) -> dict[str, Any]:
    score = match["display"]["card_primary_score"]
    return {
        "match_id": match["match_id"],
        "group": match["group"],
        "matchday": match["matchday"],
        "kickoff_at": match["kickoff_at"],
        "venue": match["venue"],
        "status": "real" if match["status"] in ("finished", "live") else "projected",
        "match_status": match["status"],
        "home_team": match["home_team"],
        "away_team": match["away_team"],
        "home_team_logo_url": match["home_team_logo_url"],
        "away_team_logo_url": match["away_team_logo_url"],
        "score": score,
        "score_label": "Score officiel" if match["status"] == "finished" else "Prono SimuAI",
        "detail_label": match["display"]["card_secondary_label"],
        "prediction": {
            "score": match["prediction"]["score_modal"],
            "favorite": match["prediction"]["favorite_label"],
            "favorite_probability": match["prediction"]["confidence"]["favorite_probability"],
            "confidence": match["prediction"]["confidence"]["level"],
        },
    }


def main() -> None:
    groups = load_json(FRONTEND_DATA_DIR / "worldcup_groups.json")
    scenario = load_json(DATA_DIR / "generated" / "living_worldcup_scenario_v2_13.json")
    engine = load_json(DATA_DIR / "generated" / "road_to_the_trophy_scenario_engine_v2_13_1B.json")
    mapping = load_json(DATA_DIR / "generated" / "worldcup_2026_official_bracket_mapping_v2_13_1B.json")
    credibility = load_json(DATA_DIR / "generated" / "road_to_the_trophy_simulation_credibility_audit_v2_13_1B.json")
    match_state = load_json(DATA_DIR / "generated" / "worldcup_match_state_view_model_v2_7.json")
    live = load_json(DATA_DIR / "generated" / "worldcup_live_group_standings_v2_7.json")
    simulation = load_json(DATA_DIR / "generated" / "worldcup_tournament_simulation_conditioned_v2_6.json")
    qualifiers = scenario["group_stage"]["projected_qualifiers"]
    matches_by_group: dict[str, list[dict[str, Any]]] = {code: [] for code in "ABCDEFGHIJKL"}
    for match in match_state["matches"]:
        matches_by_group[match["group"]].append(match_view(match))
    assets = {team["name"]: team for group in groups for team in group["teams"]}

    group_views = []
    team_paths: dict[str, dict[str, Any]] = {}
    for group in groups:
        code = group["group"]
        projected = [team for team in qualifiers if team["group"] == code]
        standings = live["groups"][code]["standings"]
        standings_by_team = {row["team"]: row for row in standings}
        team_rows = []
        for team in group["teams"]:
            name = team["name"]
            probabilities = simulation["teams"][name]
            standing = standings_by_team[name]
            team_row = {
                **team,
                "current_rank": standing["rank"],
                "points": standing["points"],
                "played": standing["played"],
                "goal_difference": standing["goal_difference"],
                "qualification_probability": probabilities["qualification_probability"],
                "finish_first_probability": probabilities["finish_first_probability"],
                "finish_second_probability": probabilities["finish_second_probability"],
                "finish_third_probability": probabilities["finish_third_probability"],
                "projected_qualifier": any(row["team"] == name for row in projected),
            }
            team_rows.append(team_row)
            team_paths[name] = {
                "team": name,
                "logo_url": team["logo_url"],
                "group": code,
                "current_rank": standing["rank"],
                "points": standing["points"],
                "qualification_probability": probabilities["qualification_probability"],
                "group_matches": [
                    match for match in matches_by_group[code] if name in (match["home_team"], match["away_team"])
                ],
                "knockout_path": engine["team_paths"].get(name, []),
            }
        group_views.append(
            {
                "group": code,
                "label": group["group_label"],
                "state": group_state(team_rows),
                "teams": team_rows,
                "matches": matches_by_group[code],
                "standings": standings,
                "played_matches": [match for match in matches_by_group[code] if match["match_status"] == "finished"],
                "upcoming_matches": [match for match in matches_by_group[code] if match["match_status"] != "finished"],
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
    for round_index, (key, label) in enumerate(ROUND_LABELS.items()):
        matches = []
        for index, match in enumerate(scenario["knockout_path"]["rounds"][key]):
            next_match_id = None
            if round_index < len(ROUND_KEYS) - 1:
                next_match_id = scenario["knockout_path"]["rounds"][ROUND_KEYS[round_index + 1]][index // 2]["match_id"]
            matches.append(
                {
                    **match,
                    "round": key,
                    "round_label": label,
                    "display_status": "projected",
                    "confirmation_status": "to_confirm",
                    "next_match_id": next_match_id,
                    "source_groups": sorted(
                        {simulation["teams"][team]["group"].replace("Group ", "") for team in (match["team_a"], match["team_b"])}
                    ),
                }
            )
        rounds.append({"key": key, "label": label, "matches": matches})

    all_group_matches = [match for group in group_views for match in group["matches"]]
    status_counts = Counter(match["status"] for match in all_group_matches)
    third_place = {
        "match_id": "projected_third_place",
        "round": "third_place",
        "round_label": "Petite finale",
        "display_status": "to_confirm",
        "official": False,
        "team_a": "Perdant demi-finale 1",
        "team_b": "Perdant demi-finale 2",
    }
    payload = {
        "version": "v2.13.1B",
        "feature_name": "Road to the Trophy",
        "generated_at": utc_now(),
        "scenario_status_label": scenario["scenario_status_label"],
        "simulation_count": scenario["simulations"],
        "matches_total_target": 104,
        "known_group_matches": 72,
        "target_knockout_matches": 32,
        "match_status_counts": {**status_counts, "to_confirm": 32},
        "result_summary": scenario["result_summary"],
        "projected_winner": scenario["tournament_winner_projected"],
        "projected_final": scenario["final_projected"],
        "group_stage": {"groups": group_views},
        "knockout": {
            "official_bracket_available": False,
            "rounds": {round_item["key"]: round_item["matches"] for round_item in rounds},
            "third_place": [third_place],
        },
        "groups": group_views,
        "rounds": rounds,
        "third_place": third_place,
        "team_paths": team_paths,
        "scenario_controls": {
            "available_modes": ["overview", "team_focus", "group_focus", "round_focus"],
            "status_filters": ["all", "real", "projected", "to_confirm"],
        },
        "status_legend": {
            "real": "Résultat réel",
            "projected": "Projection SimuAI",
            "to_confirm": "Slot à confirmer",
        },
        "official_mapping": mapping,
        "credibility_audit": {
            "verdict": credibility["verdict"],
            "execution_evidence": credibility["execution_evidence"],
            "calibration": {
                "lower_elo_projected_winner_count": credibility["calibration"]["lower_elo_projected_winner_count"],
                "projected_match_count": credibility["calibration"]["projected_match_count"],
                "france_vs_switzerland": credibility["calibration"]["france_vs_switzerland"],
            },
        },
        "limitations": engine["limitations"],
    }
    publish(payload)
    print("Road to the Trophy rich tournament atlas view model published.")


if __name__ == "__main__":
    main()
