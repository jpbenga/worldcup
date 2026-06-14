"""Validate the V2.19 coherent Road to the Trophy scenario contract."""

from __future__ import annotations

import hashlib
import shutil
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, write_json

VERSION = "v2.19"


def same(*paths: str) -> bool:
    values = []
    for name in paths:
        path = ROOT / name
        if not path.exists():
            return False
        values.append(hashlib.sha256(path.read_bytes()).hexdigest())
    return len(set(values)) == 1


def publish(payload: dict[str, Any]) -> None:
    name = "road_to_the_trophy_scenario_coherence_validation_v2_19.json"
    generated = DATA_DIR / "generated" / name
    write_json(payload, generated)
    shutil.copy2(generated, DATA_DIR / "snapshots" / name)
    shutil.copy2(generated, FRONTEND_DATA_DIR / name)


def main() -> None:
    report = load_json(DATA_DIR / "generated/road_to_the_trophy_scenario_coherence_report_v2_19.json")
    scenario = load_json(DATA_DIR / "generated/coherent_central_tournament_scenario_v2_19.json")
    view_model = load_json(DATA_DIR / "generated/road_to_the_trophy_coherent_view_model_v2_19.json")
    groups = scenario.get("group_stage", {}).get("groups", [])
    qualifiers = {team for group in groups for team in group.get("qualified", [])}
    first_round = scenario.get("knockout", {}).get("round_of_32", [])
    first_round_teams = {match[side] for match in first_round for side in ("team_a", "team_b")}
    group_shapes = len(groups) == 12 and all(len(group.get("matches", [])) == 6 and len(group.get("table", [])) == 4 for group in groups)
    group_tables = all(
        [row["rank"] for row in group["table"]] == [1, 2, 3, 4]
        and all(row["played"] == 3 for row in group["table"])
        for group in groups
    )
    group_display_sorted = all(
        [team["current_rank"] for team in group["teams"]] == [1, 2, 3, 4]
        for group in view_model.get("groups", [])
    )
    outcomes_explained = all(
        match.get("projected_winner") in (match.get("team_a"), match.get("team_b"))
        and isinstance(match.get("is_upset"), bool)
        and bool(match.get("explanation", {}).get("scenario_outcome", {}).get("note"))
        for round_row in view_model.get("rounds", [])
        for match in round_row.get("matches", [])
    )
    progression = True
    rounds = scenario.get("knockout", {})
    names = ["round_of_32", "round_of_16", "quarter_finals", "semi_finals", "final"]
    for current, following in zip(names, names[1:]):
        winners = {match["winner"] for match in rounds.get(current, [])}
        entrants = {match[side] for match in rounds.get(following, []) for side in ("team_a", "team_b")}
        progression = progression and winners == entrants
    checks = {
        "report_present_and_passed": report.get("verdict") == "PASS",
        "central_scenario_present": scenario.get("source") == "full_simulation_path",
        "coherent_view_model_present": view_model.get("scenario_display_mode") == "coherent_central_scenario",
        "groups_and_matches_complete": group_shapes,
        "scores_to_points": report.get("coherence_checks_after", {}).get("scores_to_points") is True,
        "points_to_table": report.get("coherence_checks_after", {}).get("points_to_table") is True and group_tables,
        "group_display_sorted_by_rank": group_display_sorted,
        "table_to_qualifiers": report.get("coherence_checks_after", {}).get("table_to_qualifiers") is True,
        "qualifiers_to_bracket": qualifiers == first_round_teams and len(first_round_teams) == 32,
        "bracket_to_paths": progression and report.get("coherence_checks_after", {}).get("bracket_to_paths") is True,
        "belgium_case_audited": report.get("belgium_case", {}).get("verdict") == "pass",
        "no_arbitrary_choice": report.get("repair_method", {}).get("arbitrary_choices") is False,
        "marginal_probabilities_separated": bool(view_model.get("central_scenario")) and bool(view_model.get("simulation_probabilities")),
        "knockout_outcomes_explicitly_explained": outcomes_explained,
        "active_predictions_unchanged": same("backend/data/generated/predictions.json", "backend/data/snapshots/predictions.json", "frontend/src/assets/data/predictions.json"),
        "quant_hybrid_v2_2_unchanged": same("backend/data/generated/quant_engine_v2_2_results.json", "backend/data/snapshots/quant_engine_v2_2_results.json"),
        "optuna_unchanged": same("backend/data/generated/optuna_study_summary_v2_2.json", "backend/data/snapshots/optuna_study_summary_v2_2.json"),
        "road_to_the_trophy_v3_unchanged": view_model.get("engine_name") == "SimuAI Tournament Engine V3",
        "browser_has_no_api_football_secret": "API_FOOTBALL_KEY" not in (ROOT / "frontend/src/app/services/worldcup.service.ts").read_text(encoding="utf-8")
        and "x-apisports-key" not in (ROOT / "frontend/src/app/services/worldcup.service.ts").read_text(encoding="utf-8"),
    }
    blocking = [name for name, passed in checks.items() if not passed]
    payload = {
        "version": VERSION,
        "passed": not blocking,
        "groups_validated": len(groups),
        "belgium_case_passed": checks["belgium_case_audited"],
        "scores_to_points": checks["scores_to_points"],
        "points_to_table": checks["points_to_table"],
        "table_to_qualifiers": checks["table_to_qualifiers"],
        "qualifiers_to_bracket": checks["qualifiers_to_bracket"],
        "marginal_probabilities_separated": checks["marginal_probabilities_separated"],
        "arbitrary_choices": not checks["no_arbitrary_choice"],
        "active_predictions_unchanged": checks["active_predictions_unchanged"],
        "checks": checks,
        "blocking_issues": blocking,
        "warnings": report.get("warnings", []),
    }
    publish(payload)
    print(f"V2.19 scenario coherence validation: {'PASS' if payload['passed'] else 'FAIL'}")
    if blocking:
        raise SystemExit(f"Blocking issues: {blocking}")


if __name__ == "__main__":
    main()
