"""Validate the V2.17 production-readiness operator workflow."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.operator_utils_v2_17 import publish
from backend.scripts.pipeline_utils import DATA_DIR, load_json

required = [
    "operator_experience_audit_v2_17.json", "operator_doctor_report_v2_17.json",
    "operator_refresh_manifest_v2_17.json", "data_freshness_status_v2_17.json", "preflight_report_v2_17.json",
]
missing = [name for name in required if not (DATA_DIR / "generated" / name).exists()]
audit = load_json(DATA_DIR / "generated" / "operator_experience_audit_v2_17.json") if not missing else {}
refresh = load_json(DATA_DIR / "generated" / "operator_refresh_manifest_v2_17.json") if not missing else {}
freshness = load_json(DATA_DIR / "generated" / "data_freshness_status_v2_17.json") if not missing else {}
preflight = load_json(DATA_DIR / "generated" / "preflight_report_v2_17.json") if not missing else {}
checks = {
    "operator_audit_exists": not missing,
    "operator_doctor_acceptable": audit.get("operator_readiness") in ("pass", "warning"),
    "refresh_wrapper_safe": refresh.get("active_predictions_changed") is False and refresh.get("road_to_the_trophy_engine_changed") is False,
    "freshness_status_available": freshness.get("data_status") in ("fresh", "stale", "unknown"),
    "preflight_pass": preflight.get("passed") is True,
    "operations_runbook_updated": "Daily operator workflow" in (ROOT / "docs/OPERATIONS_RUNBOOK.md").read_text(encoding="utf-8"),
    "v2_16_human_validation_recorded": "Documentation cleanup accepted" in (ROOT / "docs/VALIDATION_LOG.md").read_text(encoding="utf-8"),
    "active_predictions_unchanged": preflight.get("checks", {}).get("active_predictions_and_road_to_trophy_unchanged") is True,
    "road_to_the_trophy_engine_unchanged": preflight.get("checks", {}).get("active_predictions_and_road_to_trophy_unchanged") is True,
    "api_key_not_printed": audit.get("api_key", {}).get("value_printed") is False,
}
payload = {
    "version": "v2.17", "passed": all(checks.values()),
    "operator_doctor": audit.get("operator_readiness", "fail"),
    "refresh_wrapper": "pass" if checks["refresh_wrapper_safe"] else "fail",
    "data_freshness_status": "warning" if freshness.get("data_status") != "fresh" else "pass",
    "preflight": "pass" if preflight.get("passed") else "fail",
    "active_predictions_unchanged": checks["active_predictions_unchanged"],
    "road_to_the_trophy_engine_unchanged": checks["road_to_the_trophy_engine_unchanged"],
    "checks": checks, "blocking_issues": missing + [key for key, passed in checks.items() if not passed],
    "warnings": audit.get("warnings", []) + ([freshness.get("operator_message")] if freshness.get("data_status") != "fresh" else []),
}
publish("production_readiness_validation_v2_17.json", payload, frontend=True)
print(f"Production readiness V2.17: {'PASS' if payload['passed'] else 'FAIL'}")
if not payload["passed"]:
    raise SystemExit(f"Validation failed: {payload['blocking_issues']}")
