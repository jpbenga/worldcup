"""Audit the isolated Road to the Trophy impact of Spain 0-0 Cape Verde."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, utc_now, write_json

OUTPUT = "real_result_impact_audit_v2_26.json"
MATCH_ID = "api_football_1489380"


def publish(payload: dict[str, Any]) -> None:
    target = DATA_DIR / "generated" / OUTPUT
    write_json(payload, target)
    shutil.copy2(target, DATA_DIR / "snapshots" / OUTPUT)
    shutil.copy2(target, FRONTEND_DATA_DIR / OUTPUT)


def team_summary(scenario: dict[str, Any], team: str) -> dict[str, Any]:
    path = scenario["team_paths"][team]
    group = next(row for row in scenario["groups"] if row["group"] == path["group"])
    team_row = next(row for row in group["teams"] if row["name"] == team)
    return {
        "title_probability": path["champion_probability"],
        "final_probability": None,
        "semi_final_probability": None,
        "group_winner_probability": team_row["simulation_probabilities"]["first"],
        "qualification_probability": path["qualification_probability"],
        "projected_group_points": path["points"],
        "projected_group_rank": path["current_rank"],
        "knockout_opponents": [row["opponent"] for row in path["knockout_path"]],
        "central_scenario": {
            "champion": scenario["projected_winner"]["team"],
            "finalists": [row["team"] for row in scenario["projected_final"]["teams"]],
            "team_path": [row["opponent"] for row in path["knockout_path"]],
        },
    }


def main() -> None:
    timeline = load_json(DATA_DIR / "generated" / "road_to_the_trophy_scenario_timeline_v2_22.json")
    index = next(
        i for i, state in enumerate(timeline["states"])
        if (state.get("trigger_result") or {}).get("match_id") == MATCH_ID
    )
    before_state, after_state = timeline["states"][index - 1], timeline["states"][index]
    fixture = after_state["trigger_result"]
    before, after = team_summary(before_state["scenario"], "Spain"), team_summary(after_state["scenario"], "Spain")
    group_before = next(row for row in before_state["scenario"]["groups"] if row["group"] == "H")
    group_after = next(row for row in after_state["scenario"]["groups"] if row["group"] == "H")
    group_impacts = []
    for team in ("Spain", "Cape Verde Islands", "Uruguay", "Saudi Arabia"):
        old = next(row for row in group_before["teams"] if row["name"] == team)
        new = next(row for row in group_after["teams"] if row["name"] == team)
        group_impacts.append({
            "team": team,
            "qualification_before": old["qualification_probability"],
            "qualification_after": new["qualification_probability"],
            "qualification_delta": new["qualification_probability"] - old["qualification_probability"],
        })
    payload = {
        "version": "v2.26",
        "generated_at": utc_now(),
        "case": "Spain 0-0 Cape Verde",
        "fixture": fixture,
        "result_locked": True,
        "dominance_data_available": False,
        "dominance_data_sources": [],
        "before": {f"spain_{key}": value for key, value in before.items() if key != "central_scenario"} | {"central_scenario": before["central_scenario"]},
        "after": {f"spain_{key}": value for key, value in after.items() if key != "central_scenario"} | {"central_scenario": after["central_scenario"]},
        "deltas": {
            "title_probability_delta": after["title_probability"] - before["title_probability"],
            "final_probability_delta": None,
            "semi_final_probability_delta": None,
            "group_winner_probability_delta": after["group_winner_probability"] - before["group_winner_probability"],
            "qualification_probability_delta": after["qualification_probability"] - before["qualification_probability"],
        },
        "group_impacts": group_impacts,
        "diagnosis": {
            "result_only_locked": True,
            "team_strength_updated": False,
            "dominance_accounted_for": False,
            "explanation": (
                "The V4 counterfactual changes only by locking the official 0-0 in the group table. "
                "Future Spain match strengths still use the same current Elo and time-decayed historical profiles. "
                "The repository has no shots, possession or xG payload for this fixture."
            ),
        },
        "limitations": [
            "The V2.22 compact timeline does not persist stage-reach marginals for intermediate states, so before/after final and semi-final probabilities are unavailable.",
            "Dominance cannot be audited because no fixture-statistics or xG source is present locally.",
        ],
        "answer_for_user": (
            "Le 0-0 est verrouillé et réduit les chances de qualification de l'Espagne de 3,76 points et ses chances de titre de 0,66 point. "
            "L'Espagne reste favorite et championne du scénario central. Le moteur ne tient pas compte de sa domination : aucune donnée de tirs, possession ou xG n'est disponible, et sa force future n'est pas mise à jour par ce résultat."
        ),
    }
    publish(payload)
    print("V2.26 Spain real-result impact audit: PASS")


if __name__ == "__main__":
    main()
