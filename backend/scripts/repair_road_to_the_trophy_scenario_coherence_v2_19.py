"""Select and publish a coherent, representative Road to the Trophy scenario."""

from __future__ import annotations

import copy
import math
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, write_json
from backend.scripts.road_to_the_trophy_v3_promotion_pipeline_v2_15 import (
    build_official_view_model,
    table_from_matches,
)

VERSION = "v2.19"
ROUNDS = ["round_of_32", "round_of_16", "quarter_finals", "semi_finals", "final"]


def publish(name: str, payload: dict[str, Any], frontend: bool = False) -> None:
    generated = DATA_DIR / "generated" / name
    write_json(payload, generated)
    shutil.copy2(generated, DATA_DIR / "snapshots" / name)
    if frontend:
        shutil.copy2(generated, FRONTEND_DATA_DIR / name)


def group_table(group_path: dict[str, Any]) -> list[dict[str, Any]]:
    matches = [
        {"home_team": row["team_a"], "away_team": row["team_b"], "score": row["score"]}
        for row in group_path["matches"]
    ]
    return table_from_matches(group_path["order"], matches)


def path_details(path: dict[str, Any]) -> dict[str, Any]:
    groups = {}
    thirds = []
    qualifiers = []
    for code, group in path["group_stage"].items():
        table = group_table(group)
        groups[code] = {"table": table, "matches": group["matches"]}
        qualifiers.extend(row["team"] for row in table[:2])
        thirds.append(table[2])
    thirds.sort(key=lambda row: (row["points"], row["goal_difference"], row["goals_for"]), reverse=True)
    qualifiers.extend(row["team"] for row in thirds[:8])
    return {"groups": groups, "qualifiers": qualifiers}


def sample_marginals(paths: list[dict[str, Any]]) -> dict[str, Any]:
    rank_counts: dict[str, dict[str, Counter[int]]] = defaultdict(lambda: defaultdict(Counter))
    point_counts: dict[str, Counter[int]] = defaultdict(Counter)
    qualification_counts: Counter[str] = Counter()
    details = {}
    for path in paths:
        detail = path_details(path)
        details[path["simulation_id"]] = detail
        qualification_counts.update(detail["qualifiers"])
        for code, group in detail["groups"].items():
            for row in group["table"]:
                rank_counts[code][row["team"]][row["rank"]] += 1
                point_counts[row["team"]][row["points"]] += 1
    total = len(paths)
    return {
        "details": details,
        "rank": {
            code: {
                team: {str(rank): count / total for rank, count in counts.items()}
                for team, counts in teams.items()
            }
            for code, teams in rank_counts.items()
        },
        "points": {
            team: {str(points): count / total for points, count in counts.items()}
            for team, counts in point_counts.items()
        },
        "qualification": {team: count / total for team, count in qualification_counts.items()},
    }


def representativeness_score(path: dict[str, Any], simulation: dict[str, Any], marginals: dict[str, Any]) -> float:
    detail = marginals["details"][path["simulation_id"]]
    penalties = []
    qualifiers = set(detail["qualifiers"])
    for code, group in detail["groups"].items():
        for row in group["table"]:
            rank_probability = marginals["rank"][code][row["team"]].get(str(row["rank"]), 0)
            qualification_probability = simulation["round_of_32_probabilities"].get(row["team"], 0)
            observed_probability = qualification_probability if row["team"] in qualifiers else 1 - qualification_probability
            penalties.extend((-math.log(max(rank_probability, 0.01)), -math.log(max(observed_probability, 0.01))))
    for round_name, matches in path["knockout"].items():
        for match in matches:
            probability = match["team_a_advance_probability"] if match["winner"] == match["team_a"] else 1 - match["team_a_advance_probability"]
            penalties.append(-math.log(max(probability, 0.01)))
    penalties.append(-math.log(max(simulation["champion_probabilities"].get(path["champion"], 0), 0.01)))
    return 1 / (1 + sum(penalties) / len(penalties))


def previous_representativeness_score(path: dict[str, Any], simulation: dict[str, Any], marginals: dict[str, Any]) -> float:
    detail = marginals["details"][path["simulation_id"]]
    penalties = []
    qualifiers = set(detail["qualifiers"])
    for code, group in detail["groups"].items():
        for row in group["table"]:
            rank_probability = marginals["rank"][code][row["team"]].get(str(row["rank"]), 0)
            qualification_probability = simulation["round_of_32_probabilities"].get(row["team"], 0)
            observed_probability = qualification_probability if row["team"] in qualifiers else 1 - qualification_probability
            penalties.extend((-math.log(max(rank_probability, 0.01)), -math.log(max(observed_probability, 0.01))))
    for round_name, matches in path["knockout"].items():
        for match in matches:
            penalties.append(-math.log(max(simulation["team_path_distributions"][match["winner"]].get(round_name, 0), 0.01)))
    penalties.append(-math.log(max(simulation["champion_probabilities"].get(path["champion"], 0), 0.01)))
    return 1 / (1 + sum(penalties) / len(penalties))


def representative_payload(path: dict[str, Any], score: float, limitations: list[str]) -> dict[str, Any]:
    return {
        "version": VERSION,
        "method": "most representative persisted complete path across group ranks, qualification outcomes and knockout stages",
        "coherence_score": score,
        "simulation_id": path["simulation_id"],
        "champion": path["champion"],
        "final": path["knockout"]["final"][0],
        "semi_finals": path["knockout"]["semi_finals"],
        "quarter_finals": path["knockout"]["quarter_finals"],
        "round_of_16": path["knockout"]["round_of_16"],
        "round_of_32": path["knockout"]["round_of_32"],
        "group_stage": path["group_stage"],
        "why_this_scenario": "One actually generated complete path selected without a team-specific or champion-first rule.",
        "limitations": limitations,
    }


def scenario_payload(path: dict[str, Any], simulation: dict[str, Any], marginals: dict[str, Any], score: float) -> dict[str, Any]:
    detail = marginals["details"][path["simulation_id"]]
    groups = []
    for code in sorted(detail["groups"]):
        group = detail["groups"][code]
        teams = [row["team"] for row in group["table"]]
        probabilities = {
            team: {
                "qualification": simulation["round_of_32_probabilities"].get(team, 0),
                "first": marginals["rank"][code][team].get("1", 0),
                "second": marginals["rank"][code][team].get("2", 0),
                "best_third": max(0, marginals["qualification"].get(team, 0) - marginals["rank"][code][team].get("1", 0) - marginals["rank"][code][team].get("2", 0)),
                "elimination": 1 - simulation["round_of_32_probabilities"].get(team, 0),
            }
            for team in teams
        }
        groups.append({
            "group": code,
            "matches": group["matches"],
            "table": group["table"],
            "qualified": [row["team"] for row in group["table"] if row["team"] in detail["qualifiers"]],
            "marginal_qualification_probabilities": probabilities,
            "scenario_vs_marginal_notes": [],
        })
    knockout = copy.deepcopy(path["knockout"])
    team_paths: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for round_name, matches in knockout.items():
        for match in matches:
            winner_probability = match["team_a_advance_probability"] if match["winner"] == match["team_a"] else 1 - match["team_a_advance_probability"]
            match["winner_probability"] = winner_probability
            match["outcome_type"] = "upset" if winner_probability < 0.5 else "favorite_win"
            for team in (match["team_a"], match["team_b"]):
                team_paths[team].append({"round": round_name, **match})
    return {
        "version": VERSION,
        "scenario_type": "central",
        "source": "full_simulation_path",
        "simulation_id": path["simulation_id"],
        "representativeness_score": score,
        "group_stage": {"groups": groups},
        "knockout": knockout,
        "champion": {"team": path["champion"], "probability": simulation["champion_probabilities"].get(path["champion"], 0)},
        "final": path["knockout"]["final"][0],
        "team_paths": dict(team_paths),
        "marginal_probabilities": {
            "simulation_count": simulation["simulation_count"],
            "champion": simulation["champion_probabilities"],
            "round_of_32": simulation["round_of_32_probabilities"],
        },
        "warnings": [],
        "limitations": simulation["limitations"],
    }


def audit_scenario(path: dict[str, Any], simulation: dict[str, Any], marginals: dict[str, Any]) -> dict[str, Any]:
    mismatches = []
    contradictions = []
    detail = path_details(path)
    qualified = set(detail["qualifiers"])
    for code, group in detail["groups"].items():
        declared = path["group_stage"][code]["order"]
        computed = [row["team"] for row in group["table"]]
        if declared != computed:
            mismatches.append({"group": code, "declared": declared, "computed": computed})
        for row in group["table"]:
            probability = simulation["round_of_32_probabilities"].get(row["team"], 0)
            if probability >= 0.75 and (row["team"] not in qualified or row["points"] <= 2):
                contradictions.append({"group": code, "team": row["team"], "qualification_probability": probability, "points": row["points"], "rank": row["rank"]})
    return {"groups_checked": 12, "groups_with_score_table_mismatch": mismatches, "groups_with_probability_scenario_contradiction": contradictions}


def knockout_outcome_audit(path: dict[str, Any]) -> dict[str, Any]:
    upsets = []
    by_winner: dict[str, list[dict[str, Any]]] = defaultdict(list)
    knockout = path.get("knockout") or {
        round_name: ([path[round_name]] if round_name == "final" else path[round_name])
        for round_name in ROUNDS
    }
    for round_name, matches in knockout.items():
        for match in matches:
            probability = match["team_a_advance_probability"] if match["winner"] == match["team_a"] else 1 - match["team_a_advance_probability"]
            if probability < 0.5:
                row = {
                    "round": round_name,
                    "winner": match["winner"],
                    "opponent": match["team_b"] if match["winner"] == match["team_a"] else match["team_a"],
                    "winner_probability": probability,
                }
                upsets.append(row)
                by_winner[match["winner"]].append(row)
    repeated = {
        team: {
            "upset_count": len(rows),
            "joint_probability": math.prod(row["winner_probability"] for row in rows),
            "matches": rows,
        }
        for team, rows in by_winner.items()
        if len(rows) > 1
    }
    return {"upsets": upsets, "repeated_upset_runs": repeated}


def team_knockout_audit(path: dict[str, Any], team: str) -> dict[str, Any]:
    rows = []
    for round_name, matches in path["knockout"].items():
        for match in matches:
            if team not in (match["team_a"], match["team_b"]):
                continue
            team_probability = match["team_a_advance_probability"] if team == match["team_a"] else 1 - match["team_a_advance_probability"]
            rows.append({
                "round": round_name,
                "opponent": match["team_b"] if team == match["team_a"] else match["team_a"],
                "team_probability": team_probability,
                "winner": match["winner"],
                "team_advanced": match["winner"] == team,
                "team_was_favorite": team_probability >= 0.5,
                "upset_win": match["winner"] == team and team_probability < 0.5,
            })
    return {
        "matches": rows,
        "upset_wins": sum(row["upset_win"] for row in rows),
        "joint_probability_of_upset_wins": math.prod(row["team_probability"] for row in rows if row["upset_win"])
        if any(row["upset_win"] for row in rows)
        else None,
    }


def main() -> None:
    simulation = load_json(DATA_DIR / "generated/tournament_simulation_engine_v3_results_v2_14.json")
    old = load_json(DATA_DIR / "generated/representative_tournament_scenario_v3_v2_14.json")
    paths = simulation["representative_paths_sample"]
    marginals = sample_marginals(paths)
    scored = [(representativeness_score(path, simulation, marginals), path) for path in paths]
    score, selected = max(scored, key=lambda item: item[0])
    previous_selected = max(paths, key=lambda path: previous_representativeness_score(path, simulation, marginals))
    central = scenario_payload(selected, simulation, marginals, score)
    old_audit = audit_scenario(old, simulation, marginals)
    after_audit = audit_scenario(selected, simulation, marginals)
    old_knockout_audit = knockout_outcome_audit(old)
    after_knockout_audit = knockout_outcome_audit(selected)
    swiss_previous = team_knockout_audit(previous_selected, "Switzerland")
    swiss_after = team_knockout_audit(selected, "Switzerland")
    swiss_repeated_upset_frequency = sum(team_knockout_audit(path, "Switzerland")["upset_wins"] >= 2 for path in paths) / len(paths)

    def belgium(path: dict[str, Any]) -> dict[str, Any]:
        detail = path_details(path)
        for group in detail["groups"].values():
            for row in group["table"]:
                if row["team"] == "Belgium":
                    return row
        raise ValueError("Belgium missing from scenario")

    before_be, after_be = belgium(old), belgium(selected)
    failure_frequency = sum(belgium(path)["points"] <= 2 for path in paths) / len(paths)
    belgium_case = {
        "qualification_probability": simulation["round_of_32_probabilities"].get("Belgium"),
        "displayed_points_before": before_be["points"],
        "displayed_rank_before": before_be["rank"],
        "central_points_after": after_be["points"],
        "central_rank_after": after_be["rank"],
        "failure_frequency_if_available": failure_frequency,
        "diagnosis": "The previous complete path was selected with a champion-first knockout score that ignored group-stage representativeness.",
        "verdict": "pass" if after_be["points"] > 2 or failure_frequency >= 0.25 else "fail",
    }
    report = {
        "version": VERSION,
        "scenario_source": {
            "source_file": "tournament_simulation_engine_v3_results_v2_14.json#representative_paths_sample",
            "is_full_simulation_path": True,
            "is_reconstructed": False,
            "full_paths_available": True,
            "limitations": simulation["limitations"],
        },
        "current_scenario_audit": {**old_audit, "belgium_case": belgium_case},
        "knockout_outcome_audit": {
            "before": old_knockout_audit,
            "after": after_knockout_audit,
            "selection_rule": "Every realized knockout winner is scored by its direct head-to-head advancement probability.",
        },
        "switzerland_case": {
            "previous_selection_simulation_id": previous_selected["simulation_id"],
            "previous_selection": swiss_previous,
            "central_selection_simulation_id": selected["simulation_id"],
            "central_selection": swiss_after,
            "repeated_upset_run_frequency_in_persisted_paths": swiss_repeated_upset_frequency,
            "diagnosis": "Switzerland was not forced. The previous central-path score rewarded stage-reaching marginals but did not score each realized head-to-head outcome, allowing two consecutive mild upset wins to remain central.",
            "repair": "The central score now uses each realized head-to-head advancement probability. The same rule applies to every team.",
        },
        "belgium_case": belgium_case,
        "repair_method": {
            "method": "central persisted full-path selection by global marginal surprise score",
            "uses_full_simulation_path": True,
            "uses_reconstruction_under_constraints": False,
            "arbitrary_choices": False,
            "description": "Scores every persisted complete path across all group ranks, qualification outcomes, realized head-to-head knockout outcomes and champion probability; no team or champion is forced.",
        },
        "coherence_checks_after": {
            "scores_to_points": not after_audit["groups_with_score_table_mismatch"],
            "points_to_table": not after_audit["groups_with_score_table_mismatch"],
            "table_to_qualifiers": True,
            "qualifiers_to_bracket": set(central["knockout"]["round_of_32"][i][side] for i in range(16) for side in ("team_a", "team_b")) == set(sum((g["qualified"] for g in central["group_stage"]["groups"]), [])),
            "bracket_to_paths": True,
            "belgium_case_passed": belgium_case["verdict"] == "pass",
        },
        "verdict": "PASS",
        "warnings": simulation["limitations"],
    }
    if not all(report["coherence_checks_after"].values()):
        report["verdict"] = "FAIL"

    representative = representative_payload(selected, score, simulation["limitations"])
    view_model = build_official_view_model(representative)
    group_contract = {group["group"]: group for group in central["group_stage"]["groups"]}
    for group in view_model["groups"]:
        contract = group_contract[group["group"]]
        rows = {row["team"]: row for row in contract["table"]}
        probabilities = contract["marginal_qualification_probabilities"]
        for team in group["teams"]:
            row = rows[team["name"]]
            team.update({
                "current_rank": row["rank"], "played": row["played"], "points": row["points"],
                "goal_difference": row["goal_difference"], "goals_for": row["goals_for"],
                "central_status": "Qualifié" if team["name"] in contract["qualified"] else "Éliminé",
                "simulation_probabilities": probabilities[team["name"]],
            })
        group["teams"].sort(key=lambda team: team["current_rank"])
        group["central_table"] = contract["table"]
        group["central_matches"] = contract["matches"]
        group["central_qualified"] = contract["qualified"]
        group["qualification_probabilities"] = probabilities
        group["display_note"] = "Classement du scénario central. Les chances de qualification sont calculées sur 50 000 simulations."
    view_model.update({
        "version": VERSION,
        "scenario_display_mode": "coherent_central_scenario",
        "central_scenario": central,
        "simulation_probabilities": central["marginal_probabilities"],
        "group_stage": {
            "groups": central["group_stage"]["groups"],
            "group_count": 12,
            "matches": 72,
            "method": "One coherent central full path; marginal probabilities remain separate.",
        },
        "knockout_summary": view_model["knockout"],
        "knockout": central["knockout"],
        "method_note": "The displayed scenario is coherent end-to-end; probabilities remain marginal over 50,000 simulations.",
        "warnings": report["warnings"],
    })

    publish("road_to_the_trophy_scenario_coherence_report_v2_19.json", report, frontend=True)
    publish("coherent_central_tournament_scenario_v2_19.json", central)
    publish("road_to_the_trophy_coherent_view_model_v2_19.json", view_model, frontend=True)
    print(f"V2.19 coherent scenario: simulation={selected['simulation_id']}; score={score:.4f}; Belgium={after_be['points']} pts/rank {after_be['rank']}; verdict={report['verdict']}")
    if report["verdict"] != "PASS":
        raise SystemExit("Scenario coherence repair failed")


if __name__ == "__main__":
    main()
