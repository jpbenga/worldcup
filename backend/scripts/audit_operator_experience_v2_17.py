import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from backend.scripts.operator_utils_v2_17 import operator_audit, publish
from backend.scripts.pipeline_utils import utc_now

audit = operator_audit()
publish("operator_experience_audit_v2_17.json", audit)
publish("operator_refresh_manifest_v2_17.json", {
    "version": "v2.17", "generated_at": utc_now(), "mode": "dry-run", "simulations": 50000,
    "steps": [{"name": "matchday_refresh_v2_10", "status": "planned"}, {"name": "validate_matchday_refresh_v2_10", "status": "optional"}],
    "validation": {"requested": False, "status": "not_run"}, "critical_outputs": {},
    "active_predictions_changed": False, "road_to_the_trophy_engine_changed": False,
    "warnings": ["Initial operator plan; no refresh command executed."], "errors": [],
}, frontend=True)
print(f"Operator experience audit: {audit['operator_readiness'].upper()}")
