"""Build progressive Road to the Trophy states and readable result-driven diffs."""

from __future__ import annotations

import copy
import shutil
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, utc_now, write_json
from backend.scripts.road_to_the_trophy_v3_promotion_pipeline_v2_15 import build_official_view_model
from backend.scripts.run_tournament_simulation_engine_v4_v2_21 import (
    SEED,
    choose_scenario,
    enrich_view_model,
    representative_payload,
    run_simulation,
)

TIMELINE_REPLAY_SIMULATIONS = 2_000
TIMELINE_RESERVOIR_SIZE = 400


def publish(name: str, payload: dict[str, Any]) -> None:
    target = DATA_DIR / "generated" / name
    write_json(payload, target)
    shutil.copy2(target, DATA_DIR / "snapshots" / name)
    shutil.copy2(target, FRONTEND_DATA_DIR / name)


def compact_scenario(view: dict[str, Any], locked_results_count: int) -> dict[str, Any]:
    return {
        "simulation_count": view.get("simulation_count", 50_000),
        "scenario_status_label": view.get("scenario_status_label", "Scénario SimuAI"),
        "result_summary": {**view.get("result_summary", {}), "finished_matches": locked_results_count},
        "projected_winner": view["projected_winner"],
        "projected_final": view["projected_final"],
        "groups": view["groups"],
        "rounds": view["rounds"],
        "third_place": view["third_place"],
        "team_paths": view["team_paths"],
    }


def group_order(scenario: dict[str, Any], code: str) -> list[str]:
    group = next(row for row in scenario["groups"] if row["group"] == code)
    return [team["name"] for team in group["teams"]]


def knockout_rows(scenario: dict[str, Any]) -> dict[str, tuple[str, str, str]]:
    return {
        match["match_id"]: (match["team_a"], match["team_b"], match["projected_winner"])
        for round_row in scenario["rounds"]
        for match in round_row["matches"]
    }


def scenario_diff(before: dict[str, Any], after: dict[str, Any], trigger: dict[str, Any]) -> dict[str, Any]:
    groups_changed = [
        code for code in sorted(group["group"] for group in before["groups"])
        if group_order(before, code) != group_order(after, code)
    ]
    before_knockout, after_knockout = knockout_rows(before), knockout_rows(after)
    bracket_changes = [
        {"match_id": match_id, "before": list(before_knockout.get(match_id, ())), "after": list(after_knockout.get(match_id, ()))}
        for match_id in sorted(set(before_knockout) | set(after_knockout))
        if before_knockout.get(match_id) != after_knockout.get(match_id)
    ]
    qualification_changes = []
    for team, current_path in after["team_paths"].items():
        old_path = before["team_paths"].get(team, {})
        delta = current_path.get("qualification_probability", 0) - old_path.get("qualification_probability", 0)
        title_delta = current_path.get("champion_probability", 0) - old_path.get("champion_probability", 0)
        if abs(delta) >= 0.005 or abs(title_delta) >= 0.001:
            qualification_changes.append({"team": team, "qualification_delta": delta, "title_delta": title_delta, "reason": "Résultat réel verrouillé"})
    qualification_changes.sort(key=lambda row: abs(row["qualification_delta"]) + abs(row["title_delta"]), reverse=True)
    team_path_changes = [
        {"team": team, "before": [step["opponent"] for step in before["team_paths"].get(team, {}).get("knockout_path", [])], "after": [step["opponent"] for step in after["team_paths"].get(team, {}).get("knockout_path", [])]}
        for team in after["team_paths"]
        if [step["opponent"] for step in before["team_paths"].get(team, {}).get("knockout_path", [])] != [step["opponent"] for step in after["team_paths"].get(team, {}).get("knockout_path", [])]
    ]
    champion_before, champion_after = before["projected_winner"]["team"], after["projected_winner"]["team"]
    final_before = [row["team"] for row in before["projected_final"]["teams"]]
    final_after = [row["team"] for row in after["projected_final"]["teams"]]
    probability_impact = sum(abs(row["qualification_delta"]) + abs(row["title_delta"]) for row in qualification_changes[:4])
    importance = min(100, round(len(groups_changed) * 12 + len(bracket_changes) * 3 + len(team_path_changes) + probability_impact * 80 + (25 if champion_before != champion_after else 0)))
    result_label = f"{trigger['home_team']} {trigger['actual_score']['home']}-{trigger['actual_score']['away']} {trigger['away_team']}"
    return {
        "trigger_result": trigger,
        "summary": {
            "headline": f"{result_label} {'change le champion projeté.' if champion_before != champion_after else 'fait évoluer le parcours sans changer le champion projeté.'}",
            "groups_changed": len(groups_changed),
            "knockout_matches_changed": len(bracket_changes),
            "team_paths_changed": len(team_path_changes),
            "champion_changed": champion_before != champion_after,
            "final_changed": final_before != final_after,
        },
        "group_changes": groups_changed,
        "qualification_changes": qualification_changes[:12],
        "bracket_changes": bracket_changes,
        "team_path_changes": team_path_changes,
        "champion_change": {"before": champion_before, "after": champion_after, "changed": champion_before != champion_after},
        "final_change": {"before": final_before, "after": final_after, "changed": final_before != final_after},
        "importance_score": importance,
        "impact_label": "fort" if importance >= 55 else "moyen" if importance >= 25 else "faible",
        "stable_facts": ["Champion projeté stable"] if champion_before == champion_after else [],
    }


def main() -> None:
    results = load_json(DATA_DIR / "generated/worldcup_2026_results_v2_6.json")
    finished = [row for row in results["fixtures"] if row["status"] == "finished"]
    current_view = load_json(DATA_DIR / "generated/road_to_the_trophy_coherent_view_model_v2_21.json")
    states, previous_path = [], None
    for locked_count in range(len(finished)):
        simulation = run_simulation(
            lock_results=True,
            seed=SEED,
            lock_count=locked_count,
            simulations=TIMELINE_REPLAY_SIMULATIONS,
            reservoir_size=TIMELINE_RESERVOIR_SIZE,
        )
        path, diagnostics = choose_scenario(simulation, reference_path=previous_path)
        representative = representative_payload(path, diagnostics, simulation)
        view = build_official_view_model(representative_override=representative, simulation_override=simulation)
        enrich_view_model(view, path, simulation)
        state_id = "baseline" if locked_count == 0 else f"after_result_{locked_count:03d}"
        trigger = None if locked_count == 0 else finished[locked_count - 1]
        states.append({
            "state_id": state_id,
            "label": "Avant résultats réels" if locked_count == 0 else f"Après {trigger['home_team']} {trigger['actual_score']['home']}-{trigger['actual_score']['away']} {trigger['away_team']}",
            "locked_results_count": locked_count,
            "trigger_result": trigger,
            "scenario": compact_scenario(view, locked_count),
        })
        previous_path = path
        print(f"[STATE] {state_id}: {path['champion']}")
    states.append({
        "state_id": "current",
        "label": "Maintenant",
        "locked_results_count": len(finished),
        "trigger_result": finished[-1] if finished else None,
        "scenario": compact_scenario(current_view, len(finished)),
    })
    diffs = []
    for before, after in zip(states, states[1:]):
        diff = scenario_diff(before["scenario"], after["scenario"], after["trigger_result"])
        diff.update({"from_state_id": before["state_id"], "to_state_id": after["state_id"]})
        diffs.append(diff)
    payload = {
        "version": "v2.22",
        "generated_at": utc_now(),
        "feature_name": "Road to the Trophy",
        "timeline_type": "scenario_evolution",
        "simulation_count": 50_000,
        "intermediate_state_simulation_count": TIMELINE_REPLAY_SIMULATIONS,
        "intermediate_state_reservoir_size": TIMELINE_RESERVOIR_SIZE,
        "states": states,
        "diffs": diffs,
        "current_state_id": "current",
        "public_scenario_unique": True,
        "common_random_streams": True,
        "limitations": ["Intermediate states are regenerated during a forced refresh; the public current scenario remains the canonical V4 state."],
    }
    publish("road_to_the_trophy_scenario_timeline_v2_22.json", payload)
    print(f"V2.22 scenario timeline: {len(states)} states, {len(diffs)} diffs")


if __name__ == "__main__":
    main()
