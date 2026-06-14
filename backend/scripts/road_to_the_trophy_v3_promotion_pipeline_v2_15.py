"""Promote Tournament Simulation V3 as the canonical Road to the Trophy engine."""

from __future__ import annotations

import copy
import shutil
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, utc_now, write_json
from backend.simulation.tournament_engine_v3 import current_elos, historical_matches, match_prediction, profiles

ROUND_LABELS = {
    "round_of_32": "16es de finale",
    "round_of_16": "8es de finale",
    "quarter_finals": "Quarts de finale",
    "semi_finals": "Demi-finales",
    "final": "Finale",
}


def publish(name: str, payload: dict[str, Any]) -> None:
    generated = DATA_DIR / "generated" / name
    write_json(payload, generated)
    shutil.copy2(generated, DATA_DIR / "snapshots" / name)
    shutil.copy2(generated, FRONTEND_DATA_DIR / name)


def public_explanation(prediction: dict[str, Any]) -> dict[str, Any]:
    favorite = prediction["favorite"]
    other = prediction["team_b"] if favorite == prediction["team_a"] else prediction["team_a"]
    factors = prediction["explanation"]["key_factors"]
    advantages = [row["factor"] for row in factors if row["advantage"] == favorite]
    probability = prediction["advance_probabilities"]["team_a"] if favorite == prediction["team_a"] else prediction["advance_probabilities"]["team_b"]
    return {
        "headline": f"{favorite} est favori grâce à " + " et ".join(advantages[:2]).lower() + ".",
        "favorite": favorite,
        "favorite_probability": probability,
        "upset_context": f"{other} conserve une chance de passer, notamment dans les scénarios serrés ou après un nul en 90 minutes.",
        "measured_factors": factors,
        "missing_context": prediction["explanation"]["missing_context"],
        "method": "Confrontation tête-à-tête fondée sur les forces mesurables disponibles.",
    }


def table_from_matches(teams: list[str], matches: list[dict[str, Any]]) -> list[dict[str, Any]]:
    table = {team: {"team": team, "played": 0, "wins": 0, "draws": 0, "losses": 0, "goals_for": 0, "goals_against": 0, "points": 0} for team in teams}
    for match in matches:
        home, away = match["home_team"], match["away_team"]
        home_goals, away_goals = map(int, match["score"].split("-"))
        for team, goals_for, goals_against in ((home, home_goals, away_goals), (away, away_goals, home_goals)):
            row = table[team]
            row["played"] += 1
            row["goals_for"] += goals_for
            row["goals_against"] += goals_against
            row["wins"] += goals_for > goals_against
            row["draws"] += goals_for == goals_against
            row["losses"] += goals_for < goals_against
            row["points"] += 3 if goals_for > goals_against else 1 if goals_for == goals_against else 0
    order = sorted(table.values(), key=lambda row: (row["points"], row["goals_for"] - row["goals_against"], row["goals_for"]), reverse=True)
    for rank, row in enumerate(order, 1):
        row["rank"] = rank
        row["goal_difference"] = row["goals_for"] - row["goals_against"]
    return order


def build_official_view_model(representative_override: dict[str, Any] | None = None) -> dict[str, Any]:
    visual = load_json(DATA_DIR / "generated" / "road_to_the_trophy_view_model_v2_13_1B.json")
    representative = representative_override or load_json(DATA_DIR / "generated" / "representative_tournament_scenario_v3_v2_14.json")
    simulation = load_json(DATA_DIR / "generated" / "tournament_simulation_engine_v3_results_v2_14.json")
    elos, team_profiles = current_elos(), profiles(historical_matches())
    assets = {team["name"]: team for group in load_json(FRONTEND_DATA_DIR / "worldcup_groups.json") for team in group["teams"]}

    groups = copy.deepcopy(visual["groups"])
    group_by_team: dict[str, str] = {}
    for group in groups:
        path = representative["group_stage"][group["group"]]
        path_matches = path["matches"]
        for match, source in zip(group["matches"], path_matches):
            match["score"] = source["score"]
            match["score_label"] = "Score réel verrouillé" if source["locked"] else "Projection SimuAI"
            match["detail_label"] = "Résultat officiel" if source["locked"] else "Scénario Road to the Trophy"
            match["status"] = "real" if source["locked"] else "projected"
            match["display_status"] = match["status"]
        standings = table_from_matches([team["name"] for team in group["teams"]], group["matches"])
        standings_by_team = {row["team"]: row for row in standings}
        for team in group["teams"]:
            row = standings_by_team[team["name"]]
            group_by_team[team["name"]] = group["group"]
            team["current_rank"] = row["rank"]
            team["played"] = row["played"]
            team["points"] = row["points"]
            team["qualification_probability"] = simulation["round_of_32_probabilities"].get(team["name"], 0)
        group["knockout_links"] = []

    rounds = []
    explanations: dict[str, Any] = {}
    for round_index, (key, label) in enumerate(ROUND_LABELS.items()):
        source_matches = representative[key] if key != "final" else [representative["final"]]
        matches = []
        for index, source in enumerate(source_matches, 1):
            team_a, team_b = source["team_a"], source["team_b"]
            prediction = match_prediction(team_a, team_b, elos, team_profiles, "knockout")
            match_id = f"v3_{key}_{index}"
            explanation = public_explanation(prediction)
            winner_probability = prediction["advance_probabilities"]["team_a"] if source["winner"] == team_a else prediction["advance_probabilities"]["team_b"]
            favorite = prediction["favorite"]
            explanation["scenario_outcome"] = {
                "winner": source["winner"],
                "winner_probability": winner_probability,
                "is_upset": source["winner"] != favorite,
                "note": (
                    f"Surprise dans ce parcours complet : {source['winner']} se qualifie malgré une probabilité de {winner_probability:.1%}. "
                    "Ce résultat a été tiré par la simulation; il reste possible mais n'est pas présenté comme le favori."
                    if source["winner"] != favorite
                    else f"{source['winner']} se qualifie dans ce parcours avec une probabilité tête-à-tête de {winner_probability:.1%}."
                ),
            }
            explanations[match_id] = explanation
            match = {
                "match_id": match_id,
                "status": "projected",
                "display_status": "projected",
                "confirmation_status": "to_confirm",
                "official": False,
                "team_a": team_a,
                "team_b": team_b,
                "team_a_logo_url": assets[team_a].get("logo_url"),
                "team_b_logo_url": assets[team_b].get("logo_url"),
                "team_a_win_probability": prediction["advance_probabilities"]["team_a"],
                "team_b_win_probability": prediction["advance_probabilities"]["team_b"],
                "projected_winner": source["winner"],
                "projected_winner_probability": winner_probability,
                "is_upset": source["winner"] != favorite,
                "round": key,
                "round_label": label,
                "next_match_id": f"v3_{list(ROUND_LABELS)[round_index + 1]}_{(index + 1) // 2}" if key != "final" else None,
                "source_groups": sorted({group_by_team.get(team_a, ""), group_by_team.get(team_b, "")} - {""}),
                "explanation": explanation,
            }
            matches.append(match)
            if key == "round_of_32":
                for group in groups:
                    if group["group"] in match["source_groups"]:
                        group["knockout_links"].append(match_id)
        rounds.append({"key": key, "label": label, "matches": matches})

    semi_finals = rounds[-2]["matches"]
    third_teams = [
        match["team_b"] if match["projected_winner"] == match["team_a"] else match["team_a"]
        for match in semi_finals
    ]
    third_prediction = match_prediction(third_teams[0], third_teams[1], elos, team_profiles, "knockout")
    third_explanation = public_explanation(third_prediction)
    third_place = {
        "match_id": "v3_third_place",
        "status": "projected",
        "display_status": "projected",
        "official": False,
        "team_a": third_teams[0],
        "team_b": third_teams[1],
        "team_a_win_probability": third_prediction["advance_probabilities"]["team_a"],
        "team_b_win_probability": third_prediction["advance_probabilities"]["team_b"],
        "projected_winner": third_prediction["favorite"],
        "round": "third_place",
        "round_label": "Petite finale",
        "explanation": third_explanation,
    }
    explanations[third_place["match_id"]] = third_explanation

    paths: dict[str, Any] = {}
    for group in groups:
        for team in group["teams"]:
            name = team["name"]
            knockout_path = []
            for round_row in rounds:
                match = next((row for row in round_row["matches"] if name in (row["team_a"], row["team_b"])), None)
                if match:
                    opponent = match["team_b"] if name == match["team_a"] else match["team_a"]
                    probability = match["team_a_win_probability"] if name == match["team_a"] else match["team_b_win_probability"]
                    knockout_path.append({"match_id": match["match_id"], "round": round_row["label"], "opponent": opponent, "advance_probability": probability, "projected_winner": match["projected_winner"], "explanation": match["explanation"]})
            if name in third_teams:
                opponent = third_teams[1] if name == third_teams[0] else third_teams[0]
                probability = third_place["team_a_win_probability"] if name == third_teams[0] else third_place["team_b_win_probability"]
                knockout_path.append({"match_id": third_place["match_id"], "round": third_place["round_label"], "opponent": opponent, "advance_probability": probability, "projected_winner": third_place["projected_winner"], "explanation": third_explanation})
            paths[name] = {
                "team": name, "group": group["group"], "logo_url": team.get("logo_url"), "current_rank": team["current_rank"],
                "points": team["points"], "qualification_probability": simulation["round_of_32_probabilities"].get(name, 0),
                "champion_probability": simulation["champion_probabilities"].get(name, 0), "group_matches": group["matches"], "knockout_path": knockout_path,
            }

    final_match = rounds[-1]["matches"][0]
    winner = representative["champion"]
    official = {
        "version": "v2.15", "feature_name": "Road to the Trophy", "engine_status": "official",
        "engine_name": "SimuAI Tournament Engine V3", "generated_at": utc_now(), "simulation_count": 50000,
        "matches_total_target": 104, "known_group_matches": 72, "target_knockout_matches": 32,
        "scenario_status_label": "Scénario SimuAI", "result_summary": visual["result_summary"],
        "projected_winner": {"team": winner, "probability": simulation["champion_probabilities"][winner], "group": group_by_team[winner], "logo_url": assets[winner].get("logo_url")},
        "projected_final": {"teams": [{"team": final_match["team_a"]}, {"team": final_match["team_b"]}], "status": "projected"},
        "group_stage": {"groups": 12, "matches": 72, "method": "Résultats réels verrouillés puis matchs restants simulés à chaque parcours."},
        "knockout": {"rounds": 5, "matches": 32, "method": "head_to_head_match_model", "official_mapping": False},
        "groups": groups, "rounds": rounds, "third_place": third_place, "team_paths": paths,
        "match_explanations": explanations, "scenario_controls": visual["scenario_controls"], "status_legend": visual["status_legend"],
        "official_mapping": False, "method": {"group_stage": "dynamic_group_simulation", "knockout": "head_to_head_match_model", "full_tournament_paths": True},
        "legacy": {"visible_in_ui": False, "available_for_audit": True}, "limitations": simulation["limitations"],
    }
    official["public_scenario"] = {"winner_projected": official["projected_winner"], "final_projected": official["projected_final"], "group_stage": official["group_stage"], "knockout": official["knockout"], "team_paths": paths, "match_explanations": explanations}
    return official


def promote() -> tuple[dict[str, Any], dict[str, Any]]:
    official = build_official_view_model()
    publish("road_to_the_trophy_official_view_model_v2_15.json", official)
    engine = {
        "version": "v2.15", "feature_name": "Road to the Trophy", "public_engine_name": "SimuAI Tournament Engine V3",
        "engine_status": "official", "source_engine": "tournament_simulation_engine_v3", "simulation_count": 50000,
        "active_public_scenario": "v3", "legacy_engines_visible_in_ui": False, "predictions_engine_unchanged": True,
        "road_to_the_trophy_view_model": official, "method_summary": "50 000 tournois complets; groupes variables; éliminations simulées en tête-à-tête.",
        "regeneration_required": False, "limitations": official["limitations"],
    }
    publish("road_to_the_trophy_engine.json", engine)
    return engine, official


if __name__ == "__main__":
    promote()
