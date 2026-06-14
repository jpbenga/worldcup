"""Validate the V2.21.1 Road to the Trophy UI regression hotfix."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, utc_now, write_json

VERSION = "v2.21.1"
CRITICAL = [
    "backend/data/generated/predictions.json",
    "backend/data/snapshots/predictions.json",
    "frontend/src/assets/data/predictions.json",
    "backend/data/generated/quant_engine_v2_2_results.json",
    "backend/data/generated/optuna_study_summary_v2_2.json",
]


def publish(name: str, payload: dict[str, Any]) -> None:
    generated = DATA_DIR / "generated" / name
    write_json(payload, generated)
    shutil.copy2(generated, DATA_DIR / "snapshots" / name)
    shutil.copy2(generated, FRONTEND_DATA_DIR / name)


def main() -> None:
    view = load_json(FRONTEND_DATA_DIR / "road_to_the_trophy_coherent_view_model_v2_21.json")
    audit = load_json(DATA_DIR / "generated" / "road_to_the_trophy_ui_contract_audit_v2_21_1.json")
    groups = view.get("groups", [])
    template = (ROOT / "frontend/src/app/pages/simulation/simulation.component.html").read_text()
    service = (ROOT / "frontend/src/app/services/worldcup.service.ts").read_text()
    adapter = (ROOT / "frontend/src/app/services/road-to-the-trophy.adapter.ts").read_text()
    critical_diff = subprocess.run(["git", "diff", "--quiet", "--", *CRITICAL], cwd=ROOT).returncode
    empty_cards = sum(not group.get("teams") or not group.get("matches") for group in groups)
    checks = {
        "consumed_file_exists": (FRONTEND_DATA_DIR / "road_to_the_trophy_coherent_view_model_v2_21.json").exists(),
        "groups_available": len(groups) == 12,
        "four_teams_per_group": all(len(group.get("teams", [])) == 4 for group in groups),
        "tables_have_rows": all(len(group.get("central_table", [])) >= 4 for group in groups),
        "matches_available": all(bool(group.get("matches")) for group in groups),
        "no_empty_group_cards": empty_cards == 0,
        "champion_available": bool(view.get("projected_winner", {}).get("team")),
        "final_available": len(view.get("projected_final", {}).get("teams", [])) == 2,
        "bracket_rounds_available": len(view.get("rounds", [])) == 5,
        "team_paths_available": len(view.get("team_paths", {})) == 48,
        "real_result_impact_available": bool(view.get("scenario_evolution")),
        "adapter_used": "adaptRoadToTheTrophy" in service,
        "adapter_supports_variants": all(field in adapter for field in ("standings", "central_table", "centralTable", "central_matches", "centralMatches", "qualificationProbabilities", "marginal_qualification_probabilities")),
        "compact_empty_state_present": "contract-error" in template and "ui_contract_valid === false" in template,
        "empty_group_layout_guard_present": "group.teams.length && group.matches.length" in template,
        "broken_banner_spacing_absent": "tournoi.Classement" not in template,
        "active_predictions_unchanged": critical_diff == 0,
        "contract_audit_passed": audit.get("verdict") == "PASS",
    }
    blocking = [name for name, passed in checks.items() if not passed]
    payload = {
        "version": VERSION,
        "generated_at": utc_now(),
        "passed": not blocking,
        "groups_available": len(groups),
        "empty_group_cards": empty_cards,
        "tables_have_rows": checks["tables_have_rows"],
        "matches_available": checks["matches_available"],
        "layout_guardrails": checks["compact_empty_state_present"] and checks["empty_group_layout_guard_present"],
        "ui_contract_valid": checks["contract_audit_passed"] and checks["adapter_used"],
        "active_predictions_unchanged": checks["active_predictions_unchanged"],
        "quant_hybrid_unchanged": checks["active_predictions_unchanged"],
        "optuna_rerun": False,
        "retrain_run": False,
        "checks": checks,
        "blocking_issues": blocking,
        "warnings": ["Angular CSS budget warning remains non-blocking."] if not blocking else [],
    }
    publish("road_to_the_trophy_ui_regression_validation_v2_21_1.json", payload)
    print(f"V2.21.1 UI regression validation: {'PASS' if payload['passed'] else 'FAIL'}")
    if blocking:
        raise SystemExit(f"Road to the Trophy UI regression validation failed: {blocking}")


if __name__ == "__main__":
    main()
