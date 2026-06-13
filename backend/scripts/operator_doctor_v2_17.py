import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from backend.scripts.operator_utils_v2_17 import operator_audit, publish

audit = operator_audit()
report = {
    **audit,
    "checks": {
        "environment": "pass" if all(audit["environment"][key] for key in ("python_available", "node_available", "npm_available")) else "fail",
        "data": "pass" if all(audit["critical_data"].values()) else "fail",
        "road_to_the_trophy": "pass" if audit["critical_data"]["backend/data/generated/road_to_the_trophy_engine.json"] else "fail",
        "refresh_status": audit["last_refresh"].get("status", "unknown"),
        "git_status": "warning" if audit["git_status"]["dirty"] else "pass",
    },
    "engines": {"pre_match": "quant_hybrid_v2.2", "road_to_the_trophy": "SimuAI Tournament Engine V3"},
    "next_command": "python3 backend/scripts/run_operator_refresh_v2_17.py --dry-run",
}
publish("operator_doctor_report_v2_17.json", report)
print("SimuMondial Operator Doctor")
for label in ("environment", "data", "road_to_the_trophy", "refresh_status", "git_status"):
    print(f"{label.replace('_', ' ').title()}: {report['checks'][label].upper()}")
print(f"Next command: {report['next_command']}")
