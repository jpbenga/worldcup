"""Validate the V2.27.1 historical API-Football coverage audit."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, utc_now, write_json

OUTPUT = "api_football_historical_coverage_validation_v2_27_1.json"
PROTECTED = [
    "backend/data/generated/predictions.json", "backend/data/snapshots/predictions.json",
    "frontend/src/assets/data/predictions.json", "backend/data/generated/quant_engine_v2_2_results.json",
    "backend/data/generated/optuna_study_summary_v2_2.json", "backend/scripts/run_tournament_simulation_engine_v4_v2_21.py",
    "backend/simulation/tournament_engine_v3.py", "backend/simulation/tournament_engine_v4.py",
]
REQUIRED = [
    "historical_competition_coverage_v2_27_1.json", "historical_api_sample_fixtures_v2_27_1.json",
    "api_football_historical_stats_coverage_v2_27_1.json", "api_football_historical_coverage_matrix_v2_27_1.json",
    "api_stats_algorithm_readiness_answer_v2_27_1.json",
]


def publish(payload: dict[str, Any]) -> None:
    target = DATA_DIR / "generated" / OUTPUT
    write_json(payload, target)
    shutil.copy2(target, DATA_DIR / "snapshots" / OUTPUT)
    shutil.copy2(target, FRONTEND_DATA_DIR / OUTPUT)


def main() -> None:
    values = {name: load_json(DATA_DIR / "generated" / name) for name in REQUIRED}
    discovery, sample, audit, matrix, answer = values.values()
    protected_diff = subprocess.run(["git", "diff", "--", *PROTECTED], cwd=ROOT, text=True, capture_output=True).stdout
    scripts = "\n".join(path.read_text(encoding="utf-8") for path in ROOT.glob("backend/scripts/*v2_27_1.py"))
    secret = bool(re.search(r"x-apisports-key\s*:\s*['\"][^'\"]+|API_FOOTBALL_KEY\s*=\s*['\"][^'\"]+", scripts, re.I))
    checks = {
        "historical_competitions_discovered": bool(discovery["competition_seasons"]),
        "sample_fixtures_selected": bool(sample["selected_fixtures"]),
        "historical_api_coverage_audited": bool(audit["coverage_by_fixture"]),
        "coverage_matrix_generated": bool(matrix["matrix"]),
        "algorithm_readiness_answer_generated": bool(answer["answer"]["short_answer"]),
        "xg_checked": "xg_available_rate" in audit["coverage_summary"],
        "statistics_checked": "statistics_available_rate" in audit["coverage_summary"],
        "events_checked": "events_available_rate" in audit["coverage_summary"],
        "lineups_checked": "lineups_available_rate" in audit["coverage_summary"],
        "players_checked": "players_available_rate" in audit["coverage_summary"],
        "quota_safe": audit["live_calls_used"] <= audit["max_live_calls"] and sample["sampling_policy"]["quota_safe"],
        "public_engine_changed": bool(protected_diff),
        "active_predictions_unchanged": not protected_diff,
        "no_secret_exposed": not secret,
    }
    blocking = [key for key, value in checks.items() if key != "public_engine_changed" and not value]
    payload = {
        "version": "v2.27.1", "generated_at": utc_now(), "passed": not blocking and not checks["public_engine_changed"],
        **checks, "blocking_issues": blocking + (["public_engine_changed"] if checks["public_engine_changed"] else []),
        "warnings": audit["warnings"],
    }
    publish(payload)
    print(f"V2.27.1 historical coverage validation: {'PASS' if payload['passed'] else 'FAIL'}")
    if not payload["passed"]:
        raise SystemExit(payload["blocking_issues"])


if __name__ == "__main__":
    main()
