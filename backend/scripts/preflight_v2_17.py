"""Run non-destructive checks before a SimuMondial commit or push."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.operator_utils_v2_17 import CRITICAL_ASSETS, CRITICAL_DATA, operator_audit, publish

PROTECTED = [
    "backend/data/generated/predictions.json", "backend/data/snapshots/predictions.json",
    "frontend/src/assets/data/predictions.json", "backend/data/generated/quant_engine_v2_2_results.json",
    "backend/data/generated/optuna_study_summary_v2_2.json", "backend/data/generated/road_to_the_trophy_engine.json",
    "frontend/src/assets/data/road_to_the_trophy_engine.json",
]


def command(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(list(args), cwd=ROOT, text=True, capture_output=True)


audit = operator_audit()
protected_diff = command("git", "diff", "--", *PROTECTED).stdout
tracked_forbidden = command("git", "ls-files").stdout.splitlines()
forbidden = [path for path in tracked_forbidden if any(part in path for part in ("node_modules/", "/dist/", "/build/", "/venv/", "__pycache__")) or path.endswith((".pyc", ".env", ".idx"))]
large = [str(path.relative_to(ROOT)) for path in ROOT.rglob("*") if path.is_file() and ".git" not in path.parts and "node_modules" not in path.parts and path.stat().st_size > 10 * 1024 * 1024]
ui_diff = command("git", "diff", "--name-only", "--", "frontend/src").stdout.splitlines()
checks = {
    "operator_doctor_acceptable": audit["operator_readiness"] in ("pass", "warning"),
    "critical_data_present": all((ROOT / path).exists() for path in CRITICAL_DATA + CRITICAL_ASSETS),
    "documentation_validation_present": (ROOT / "backend/data/generated/documentation_cleanup_validation_v2_16.json").exists(),
    "active_predictions_and_road_to_trophy_unchanged": not protected_diff,
    "no_forbidden_tracked_files": not forbidden,
    "no_unexpected_large_files": not large,
    "api_key_not_printed": audit["api_key"]["value_printed"] is False,
}
payload = {
    "version": "v2.17", "passed": all(checks.values()), "checks": checks,
    "blocking_issues": [key for key, passed in checks.items() if not passed],
    "warnings": audit["warnings"] + (["Frontend changed: run Angular build and tests."] if ui_diff else []),
    "frontend_build_required": bool(ui_diff), "git_status": audit["git_status"],
    "forbidden_tracked_files": forbidden, "large_files": large,
}
publish("preflight_report_v2_17.json", payload)
print(f"Preflight V2.17: {'PASS' if payload['passed'] else 'FAIL'}")
if payload["blocking_issues"]:
    raise SystemExit(f"Blocking issues: {payload['blocking_issues']}")
