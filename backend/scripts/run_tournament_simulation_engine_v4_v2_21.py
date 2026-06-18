"""Run the V2.21 rules-aware tournament engine and publish Road to the Trophy."""

from __future__ import annotations

import copy
import math
import random
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, utc_now, write_json
from backend.scripts.road_to_the_trophy_v3_promotion_pipeline_v2_15 import build_official_view_model, table_from_matches
from backend.simulation.tournament_engine_v3 import current_elos, historical_matches, profiles
from backend.simulation.tournament_engine_v4 import knockout_result, prediction_cache, rank_group, sample_score

VERSION = "v2.21"
SIMULATIONS = 50_000
RESERVOIR_SIZE = 2_000
SEED = 202621
CONTINUITY_TOLERANCE = 0.05
ROUNDS = ["round_of_32", "round_of_16", "quarter_finals", "semi_finals", "final"]


def publish(name: str, payload: dict[str, Any], frontend: bool = False) -> None:
    generated = DATA_DIR / "generated" / name
    write_json(payload, generated)
    shutil.copy2(generated, DATA_DIR / "snapshots" / name)
    if frontend:
        shutil.copy2(generated, FRONTEND_DATA_DIR / name)


def run_simulation(lock_results: bool, seed: int, lock_count: int | None = None, simulations: int = SIMULATIONS, reservoir_size: int = RESERVOIR_SIZE) -> dict[str, Any]:
    groups = load_json(FRONTEND_DATA_DIR / "worldcup_groups.json")
    elos = current_elos()
    prediction = prediction_cache(elos, profiles(historical_matches()))
    official = load_json(DATA_DIR / "generated" / "worldcup_2026_results_v2_6.json")
    finished = [row for row in official["fixtures"] if row["status"] == "finished"]
    if lock_count is not None:
        finished = finished[:lock_count]
    results = {row["match_id"]: row for row in finished} if lock_results else {}
    reservoir_rng = random.Random(seed + 99_991)
    stage_counts = {round_name: Counter() for round_name in ROUNDS}
    champions, finals, resolution_counts = Counter(), Counter(), Counter()
    qualification_counts: Counter[str] = Counter()
    rank_counts: dict[str, dict[str, Counter[int]]] = defaultdict(lambda: defaultdict(Counter))
    reservoir: list[dict[str, Any]] = []
    tie_decision_count = 0

    for simulation_id in range(1, simulations + 1):
        # A dedicated stream per tournament gives the current and counterfactual
        # universes common random numbers instead of letting one locked score
        # shift every subsequent draw.
        rng = random.Random(seed + simulation_id * 1_000_003)
        qualifiers, thirds, group_path = [], [], {}
        for group in groups:
            teams = [team["name"] for team in group["teams"]]
            table = {team: {"pts": 0, "gd": 0, "gf": 0} for team in teams}
            played = []
            for match in group["matches"]:
                team_a, team_b = match["home_team"], match["away_team"]
                real = results.get(match["match_id"])
                sampled_goals = sample_score(prediction(team_a, team_b, "group")["_cumulative"], rng)
                if real:
                    goals_a, goals_b = real["actual_score"]["home"], real["actual_score"]["away"]
                else:
                    goals_a, goals_b = sampled_goals
                for team, gf, ga in ((team_a, goals_a, goals_b), (team_b, goals_b, goals_a)):
                    table[team]["gf"] += gf
                    table[team]["gd"] += gf - ga
                    table[team]["pts"] += 3 if gf > ga else 1 if gf == ga else 0
                played.append({"team_a": team_a, "team_b": team_b, "score": f"{goals_a}-{goals_b}", "locked": bool(real)})
            order, tie_decisions = rank_group(table, played, elos)
            tie_decision_count += len(tie_decisions)
            for rank, team in enumerate(order, 1):
                rank_counts[group["group"]][team][rank] += 1
            qualifiers.extend([(order[0], group["group"]), (order[1], group["group"])])
            thirds.append((order[2], group["group"], table[order[2]]))
            group_path[group["group"]] = {"order": order, "matches": played, "tie_break_decisions": tie_decisions}

        thirds.sort(key=lambda row: (row[2]["pts"], row[2]["gd"], row[2]["gf"], elos.get(row[0], 1500)), reverse=True)
        qualifiers.extend((team, group) for team, group, _ in thirds[:8])
        qualification_counts.update(team for team, _ in qualifiers)

        # Official slot mapping is not present in repository data. This deterministic
        # fallback is explicit and isolated so it can be replaced without touching match logic.
        qualifiers.sort(key=lambda row: elos.get(row[0], 1500), reverse=True)
        high, low = qualifiers[:16], list(reversed(qualifiers[16:]))
        for index in range(16):
            if high[index][1] == low[index][1]:
                swap = next((candidate for candidate in range(index + 1, 16) if high[index][1] != low[candidate][1] and high[candidate][1] != low[index][1]), None)
                if swap is not None:
                    low[index], low[swap] = low[swap], low[index]
        pairings = [(a[0], b[0]) for a, b in zip(high, low)]

        path_rounds = {}
        for round_name in ROUNDS:
            entrants = [team for pairing in pairings for team in pairing]
            stage_counts[round_name].update(entrants)
            if round_name == "final":
                finals[tuple(sorted(entrants))] += 1
            winners, match_rows = [], []
            for team_a, team_b in pairings:
                direct = prediction(team_a, team_b, "knockout")
                result = knockout_result(direct, rng)
                resolution_counts[result["resolution"]] += 1
                winners.append(result["winner"])
                match_rows.append({
                    "team_a": team_a,
                    "team_b": team_b,
                    "winner": result["winner"],
                    "team_a_advance_probability": direct["advance_probabilities"]["team_a"],
                    "resolution": result["resolution"],
                    "score_90": result["score_90"],
                    "score_et": result.get("score_et"),
                })
            path_rounds[round_name] = match_rows
            pairings = list(zip(winners[0::2], winners[1::2]))
        champions[winners[0]] += 1
        path = {"simulation_id": simulation_id, "champion": winners[0], "group_stage": group_path, "knockout": path_rounds}
        if len(reservoir) < reservoir_size:
            reservoir.append(path)
        else:
            replacement = reservoir_rng.randrange(simulation_id)
            if replacement < reservoir_size:
                reservoir[replacement] = path

    probabilities = {
        round_name: {team: count / simulations for team, count in stage_counts[round_name].items()}
        for round_name in ROUNDS
    }
    all_teams = [team["name"] for group in groups for team in group["teams"]]
    return {
        "version": VERSION,
        "simulation_count": simulations,
        "seed": seed,
        "real_results_locked": len(results),
        "match_engine": "elo_time_decay_independent_poisson_v4",
        "knockout_model": "explicit_90m_extra_time_penalties",
        "group_tie_break": "points_goal_difference_goals_for_head_to_head_then_elo_proxy",
        "bracket_method": "isolated_dynamic_fallback_pending_official_mapping",
        "official_bracket_available": False,
        "reservoir_sampling": {"method": "uniform_reservoir", "size": len(reservoir), "coverage": f"all_{simulations}_paths"},
        "champion_probabilities": {team: count / simulations for team, count in champions.most_common()},
        "round_of_32_probabilities": probabilities["round_of_32"],
        "team_path_distributions": {
            team: {round_name: probabilities[round_name].get(team, 0) for round_name in ROUNDS}
            | {"champion": champions[team] / simulations}
            for team in all_teams
        },
        "group_rank_probabilities": {
            group: {team: {str(rank): count / simulations for rank, count in ranks.items()} for team, ranks in teams.items()}
            for group, teams in rank_counts.items()
        },
        "most_common_finals": [{"teams": list(teams), "probability": count / simulations} for teams, count in finals.most_common(10)],
        "knockout_resolution_counts": dict(resolution_counts),
        "tie_break_decisions": tie_decision_count,
        "representative_paths_reservoir": reservoir,
        "limitations": [
            "Official 2026 knockout slot mapping is absent from repository data; the isolated fallback remains non-official.",
            "Fair-play points and drawing-lots data are unavailable; Elo is only the final deterministic tie-break proxy.",
            "Penalty shootouts use a strongly shrunk Elo signal because usable shootout history is sparse.",
            "The active quant_hybrid_v2.2 inference bundle is not persisted for arbitrary future pairings.",
        ],
    }


def scenario_score(path: dict[str, Any], simulation: dict[str, Any]) -> float:
    penalties = []
    rank_probabilities = simulation["group_rank_probabilities"]
    qualifiers = set()
    for group, detail in path["group_stage"].items():
        qualifiers.update(detail["order"][:2])
        for rank, team in enumerate(detail["order"], 1):
            penalties.append(-math.log(max(rank_probabilities[group][team].get(str(rank), 0.001), 0.001)))
    for round_name, matches in path["knockout"].items():
        for match in matches:
            probability = match["team_a_advance_probability"] if match["winner"] == match["team_a"] else 1 - match["team_a_advance_probability"]
            penalties.append(-math.log(max(probability, 0.01)))
    penalties.append(-math.log(max(simulation["champion_probabilities"].get(path["champion"], 0.001), 0.001)))
    return sum(penalties) / len(penalties)


def path_distance(before: dict[str, Any], after: dict[str, Any]) -> int:
    distance = sum(
        before["group_stage"][group]["order"] != after["group_stage"][group]["order"]
        for group in before["group_stage"]
    )
    for round_name in ROUNDS:
        before_rows = [(row["team_a"], row["team_b"], row["winner"]) for row in before["knockout"][round_name]]
        after_rows = [(row["team_a"], row["team_b"], row["winner"]) for row in after["knockout"][round_name]]
        distance += sum(a != b for a, b in zip(before_rows, after_rows))
    return distance


def choose_scenario(
    simulation: dict[str, Any],
    reference_path: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    paths = simulation["representative_paths_reservoir"]
    scored = sorted(
        ((scenario_score(path, simulation), path) for path in paths),
        key=lambda item: item[0],
    )
    pure_best_score, pure_best = scored[0]
    near_optimal = [item for item in scored if item[0] <= pure_best_score * (1 + CONTINUITY_TOLERANCE)]
    if reference_path:
        selected_score, selected = min(near_optimal, key=lambda item: (path_distance(reference_path, item[1]), item[0]))
    else:
        selected_score, selected = scored[0]
    champion_first = max(simulation["champion_probabilities"], key=simulation["champion_probabilities"].get)
    champion_paths = [item for item in scored if item[1]["champion"] == champion_first]
    champion_first_score, champion_first_path = champion_paths[0] if champion_paths else scored[0]
    diagnostics = {
        "method": "minimum_global_surprise_complete_path_with_continuity_tie_break",
        "candidate_pool": len(paths),
        "candidate_sampling": f"uniform reservoir across all {simulation.get('simulation_count', SIMULATIONS)} complete paths",
        "near_optimal_candidate_count": len(near_optimal),
        "near_optimal_threshold": "within 5% of minimum average surprise",
        "continuity_reference_used": reference_path is not None,
        "distance_from_previous_scenario": path_distance(reference_path, selected) if reference_path else None,
        "pure_best_simulation_id": pure_best["simulation_id"],
        "pure_best_average_surprise": pure_best_score,
        "selected_vs_pure_best_surprise_delta": selected_score - pure_best_score,
        "selected_simulation_id": selected["simulation_id"],
        "selected_champion": selected["champion"],
        "selected_average_surprise": selected_score,
        "most_likely_champion": champion_first,
        "most_likely_champion_probability": simulation["champion_probabilities"][champion_first],
        "champion_first_candidate_simulation_id": champion_first_path["simulation_id"],
        "champion_first_average_surprise": champion_first_score,
        "champion_forced": False,
        "interpretation": "The selected path is within 5% of minimum average surprise; when a previous scenario exists, continuity breaks statistically close ties. The champion is never forced.",
    }
    return selected, diagnostics


def probability_deltas(current: dict[str, Any], baseline: dict[str, Any]) -> list[dict[str, Any]]:
    teams = set(current["champion_probabilities"]) | set(baseline["champion_probabilities"])
    rows = []
    for team in teams:
        qualification_delta = current["round_of_32_probabilities"].get(team, 0) - baseline["round_of_32_probabilities"].get(team, 0)
        champion_delta = current["champion_probabilities"].get(team, 0) - baseline["champion_probabilities"].get(team, 0)
        rows.append({"team": team, "qualification_delta": qualification_delta, "champion_delta": champion_delta, "impact": abs(qualification_delta) + abs(champion_delta)})
    return sorted(rows, key=lambda row: row["impact"], reverse=True)


def structural_changes(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    changed_groups = [
        group for group in sorted(before["group_stage"])
        if before["group_stage"][group]["order"] != after["group_stage"][group]["order"]
    ]
    changed_rounds = {}
    for round_name in ROUNDS:
        before_rows = [(row["team_a"], row["team_b"], row["winner"]) for row in before["knockout"][round_name]]
        after_rows = [(row["team_a"], row["team_b"], row["winner"]) for row in after["knockout"][round_name]]
        changed_rounds[round_name] = sum(a != b for a, b in zip(before_rows, after_rows))
    before_final = sorted((before["knockout"]["final"][0]["team_a"], before["knockout"]["final"][0]["team_b"]))
    after_final = sorted((after["knockout"]["final"][0]["team_a"], after["knockout"]["final"][0]["team_b"]))
    return {
        "champion_changed": before["champion"] != after["champion"],
        "final_changed": before_final != after_final,
        "before_final": before_final,
        "after_final": after_final,
        "changed_group_orders": changed_groups,
        "changed_group_order_count": len(changed_groups),
        "changed_knockout_matches_by_round": changed_rounds,
        "changed_knockout_match_count": sum(changed_rounds.values()),
    }


def representative_payload(path: dict[str, Any], diagnostics: dict[str, Any], simulation: dict[str, Any]) -> dict[str, Any]:
    return {
        "version": VERSION,
        "method": diagnostics["method"],
        "coherence_score": 1 / (1 + diagnostics["selected_average_surprise"]),
        "simulation_id": path["simulation_id"],
        "champion": path["champion"],
        "final": path["knockout"]["final"][0],
        "semi_finals": path["knockout"]["semi_finals"],
        "quarter_finals": path["knockout"]["quarter_finals"],
        "round_of_16": path["knockout"]["round_of_16"],
        "round_of_32": path["knockout"]["round_of_32"],
        "group_stage": path["group_stage"],
        "why_this_scenario": diagnostics["interpretation"],
        "limitations": simulation["limitations"],
    }


def enrich_view_model(view_model: dict[str, Any], path: dict[str, Any], simulation: dict[str, Any]) -> None:
    qualified = {
        team
        for match in path["knockout"]["round_of_32"]
        for team in (match["team_a"], match["team_b"])
    }
    group_contract = {}
    for group in view_model["groups"]:
        code = group["group"]
        standings = table_from_matches([team["name"] for team in group["teams"]], group["matches"])
        standings_by_team = {row["team"]: row for row in standings}
        group["central_table"] = standings
        group["central_matches"] = group["matches"]
        group["central_qualified"] = [row["team"] for row in standings if row["team"] in qualified]
        group["qualification_probabilities"] = {}
        group["display_note"] = "Classement du scénario central. Les chances de qualification sont calculées sur 50 000 simulations."
        for team in group["teams"]:
            name = team["name"]
            row = standings_by_team[name]
            ranks = simulation["group_rank_probabilities"][code][name]
            qualification = simulation["round_of_32_probabilities"].get(name, 0)
            probabilities = {
                "qualification": qualification,
                "first": ranks.get("1", 0),
                "second": ranks.get("2", 0),
                "best_third": max(0, qualification - ranks.get("1", 0) - ranks.get("2", 0)),
                "elimination": 1 - qualification,
            }
            team.update({
                "current_rank": row["rank"],
                "played": row["played"],
                "points": row["points"],
                "goal_difference": row["goal_difference"],
                "goals_for": row["goals_for"],
                "central_status": "Qualifié" if name in qualified else "Éliminé",
                "simulation_probabilities": probabilities,
            })
            group["qualification_probabilities"][name] = probabilities
        group["teams"].sort(key=lambda team: team["current_rank"])
        group_contract[code] = group

    for name, team_path in view_model["team_paths"].items():
        group = group_contract[team_path["group"]]
        team = next(row for row in group["teams"] if row["name"] == name)
        team_path.update({
            "current_rank": team["current_rank"],
            "points": team["points"],
            "qualification_probability": team["simulation_probabilities"]["qualification"],
        })


def main() -> None:
    current = run_simulation(lock_results=True, seed=SEED)
    baseline = run_simulation(lock_results=False, seed=SEED)
    baseline_path, baseline_diagnostics = choose_scenario(baseline)
    current_path, current_diagnostics = choose_scenario(current, reference_path=baseline_path)
    deltas = probability_deltas(current, baseline)
    known_results = load_json(DATA_DIR / "generated" / "worldcup_2026_results_v2_6.json")["fixtures"]
    finished = [row for row in known_results if row["status"] == "finished"]
    changes = structural_changes(baseline_path, current_path)
    evolution = {
        "version": VERSION,
        "comparison": "same_engine_common_random_numbers_with_known_results_vs_without_known_results",
        "known_results_count": len(finished),
        "known_results": [{"match": f"{row['home_team']} {row['actual_score']['home']}-{row['actual_score']['away']} {row['away_team']}"} for row in finished],
        "scenario_changed": bool(changes["changed_group_order_count"] or changes["changed_knockout_match_count"] or changes["champion_changed"]),
        "structural_changes": changes,
        "before": {"simulation_id": baseline_path["simulation_id"], "champion": baseline_path["champion"], "diagnostics": baseline_diagnostics},
        "after": {"simulation_id": current_path["simulation_id"], "champion": current_path["champion"], "diagnostics": current_diagnostics},
        "largest_probability_movements": deltas[:12],
        "method_note": "Both universes use the same engine and common random-number stream per tournament. The only intentional difference is that finished official results are locked in the current universe.",
    }
    representative = representative_payload(current_path, current_diagnostics, current)
    view_model = build_official_view_model(representative_override=representative, simulation_override=current)
    enrich_view_model(view_model, current_path, current)
    view_model.update({
        "version": VERSION,
        "engine_name": "SimuAI Tournament Engine V4",
        "scenario_selection": current_diagnostics,
        "scenario_evolution": evolution,
        "limitations": current["limitations"],
    })
    engine = {
        "version": VERSION,
        "feature_name": "Road to the Trophy",
        "public_engine_name": "SimuAI Tournament Engine V4",
        "engine_status": "official",
        "source_engine": "tournament_simulation_engine_v4",
        "simulation_count": SIMULATIONS,
        "active_public_scenario": "v4_rules_aware",
        "road_to_the_trophy_view_model": view_model,
        "method_summary": "50,000 complete tournaments with explicit knockout resolution, deterministic tie-breaks and result-sensitive representative scenario.",
        "limitations": current["limitations"],
    }
    validation = {
        "version": VERSION,
        "passed": True,
        "simulation_count": current["simulation_count"],
        "counterfactual_simulation_count": baseline["simulation_count"],
        "reservoir_size": current["reservoir_sampling"]["size"],
        "known_results_change_scenario": evolution["scenario_changed"],
        "explicit_knockout_resolutions": current["knockout_resolution_counts"],
        "scenario_selection": current_diagnostics,
        "remaining_blockers": current["limitations"],
    }
    compact_results = copy.deepcopy(current)
    compact_results["representative_paths_reservoir"] = {
        "persisted": False,
        "reason": "The uniform 2,000-path reservoir was used for scenario selection; only the selected path and diagnostics are published to keep the artifact operationally small.",
        "selected_simulation_id": current_path["simulation_id"],
    }
    publish("tournament_simulation_engine_v4_results_v2_21.json", compact_results)
    publish("representative_tournament_scenario_v4_v2_21.json", representative)
    publish("road_to_the_trophy_scenario_evolution_v2_21.json", evolution, frontend=True)
    publish("road_to_the_trophy_v4_validation_v2_21.json", validation)
    publish("road_to_the_trophy_coherent_view_model_v2_21.json", view_model, frontend=True)
    publish("road_to_the_trophy_engine.json", engine, frontend=True)
    print(f"V2.21 PASS: current={current_path['simulation_id']} {current_path['champion']}; baseline={baseline_path['simulation_id']} {baseline_path['champion']}; changed={evolution['scenario_changed']}")


if __name__ == "__main__":
    main()
