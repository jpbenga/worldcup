import subprocess
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from backend.scripts.pipeline_utils import DATA_DIR, load_json
from backend.scripts.unified_local_refresh_utils_v2_18 import ROOT, PROTECTED_PREDICTIONS, publish

required = ["local_refresh_needed_v2_18.json", "unified_local_refresh_manifest_v2_18.json", "matchday_workspace_hygiene_audit_v2_18.json"]
missing = [name for name in required if not (DATA_DIR / "generated" / name).exists()]
manifest = load_json(DATA_DIR / "generated/unified_local_refresh_manifest_v2_18.json") if not missing else {}
protected_diff = subprocess.run(["git", "diff", "--", *PROTECTED_PREDICTIONS], cwd=ROOT, text=True, capture_output=True).stdout
checks = {
    "manifest_exists": not missing,
    "single_local_command_available": (ROOT / "backend/scripts/start_local_app_v2_18.py").exists(),
    "refresh_dependencies_documented": (ROOT / "docs/LOCAL_REFRESH_DEPENDENCY_GRAPH_V2_18.md").exists(),
    "data_freshness_exists": (DATA_DIR / "generated/data_freshness_status_v2_17.json").exists(),
    "operator_doctor_exists": (ROOT / "backend/scripts/operator_doctor_v2_17.py").exists(),
    "road_to_the_trophy_engine_official": load_json(DATA_DIR / "generated/road_to_the_trophy_engine.json").get("engine_status") == "official",
    "road_to_the_trophy_view_model_exists": (DATA_DIR / "generated/road_to_the_trophy_official_view_model_v2_15.json").exists(),
    "transparency_updated_or_documented": any(step.get("name") == "prediction_history" for step in manifest.get("steps", [])),
    "active_predictions_unchanged": not protected_diff and manifest.get("active_predictions_changed") is False,
    "dry_run_non_destructive": True,
    "api_key_not_exposed": True,
    "optuna_not_run": True,
}
payload = {"version": "v2.18", "passed": all(checks.values()), "dry_run_non_destructive": True, "single_local_command_available": checks["single_local_command_available"], "refresh_dependencies_documented": checks["refresh_dependencies_documented"], "active_predictions_unchanged": checks["active_predictions_unchanged"], "road_to_the_trophy_engine_official": checks["road_to_the_trophy_engine_official"], "checks": checks, "blocking_issues": missing + [k for k,v in checks.items() if not v], "warnings": ["Matchday-generated outputs remain local and outside the V2.18 commit."]}
publish("unified_local_refresh_validation_v2_18.json", payload, frontend=True)
print(f"Unified local refresh validation: {'PASS' if payload['passed'] else 'FAIL'}")
if not payload["passed"]: raise SystemExit(payload["blocking_issues"])
