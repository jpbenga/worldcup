"""Validate the V2.29 respectful full historical API-Football collector."""

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

OUTPUT = "api_football_full_collection_validation_v2_29.json"
COLLECTOR = ROOT / "backend" / "scripts" / "collect_api_football_historical_stats_full_v2_29.py"
SUMMARY = DATA_DIR / "generated" / "api_football_full_collection_summary_v2_29.json"
MANIFEST = DATA_DIR / "generated" / "api_football_historical_stats_collection_manifest_v2_29.json"
RAW_CACHE = "backend/data/cache/api_football/historical_stats"
PROTECTED = [
    "backend/data/generated/predictions.json",
    "backend/data/snapshots/predictions.json",
    "frontend/src/assets/data/predictions.json",
    "backend/data/generated/quant_engine_v2_2_results.json",
    "backend/data/generated/optuna_study_summary_v2_2.json",
    "backend/scripts/run_tournament_simulation_engine_v4_v2_21.py",
    "backend/simulation/tournament_engine_v3.py",
    "backend/simulation/tournament_engine_v4.py",
]


def publish(payload: dict[str, Any]) -> None:
    target = DATA_DIR / "generated" / OUTPUT
    write_json(payload, target)
    shutil.copy2(target, DATA_DIR / "snapshots" / OUTPUT)
    shutil.copy2(target, FRONTEND_DATA_DIR / OUTPUT)


def main() -> None:
    text = COLLECTOR.read_text(encoding="utf-8") if COLLECTOR.exists() else ""
    manifest = load_json(MANIFEST) if MANIFEST.exists() else {}
    summary = load_json(SUMMARY) if SUMMARY.exists() else {}
    protected_diff = subprocess.run(["git", "diff", "--", *PROTECTED], cwd=ROOT, text=True, capture_output=True).stdout
    staged_cache = subprocess.run(["git", "status", "--short", RAW_CACHE], cwd=ROOT, text=True, capture_output=True).stdout
    grep_cache = subprocess.run(["git", "ls-files", RAW_CACHE], cwd=ROOT, text=True, capture_output=True).stdout
    secret = bool(re.search(r"x-apisports-key\s*:\s*['\"][^'\"]+|API_FOOTBALL_KEY\s*=\s*['\"][^'\"]+", text, re.I))
    checks = {
        "collector_exists": COLLECTOR.exists(),
        "dry_run_ok": bool(manifest) and manifest.get("dry_run") in (True, False),
        "resume_supported": "--resume" in text and "resume_enabled" in text,
        "cache_first": "--use-cache" in text and "mark_from_cache" in text,
        "max_live_calls_enforced": "max_live_calls reached" in text and "live_calls_this_run" in text,
        "single_worker_default": '"concurrency": 1' in text or "'concurrency': 1" in text,
        "sleep_between_calls": "sleep_seconds" in text and "time.sleep" in text,
        "retry_after_supported": "Retry-After" in text and "respect_retry_after" in text,
        "exponential_backoff_with_jitter": "2 ** attempt" in text and "random.uniform" in text,
        "circuit_breaker": "circuit_breaker_open" in text and "consecutive_errors >= 5" in text,
        "raw_cache_not_committed": not grep_cache and not any(line.startswith(("A ", "M ")) for line in staged_cache.splitlines()),
        "summary_generated": bool(summary),
        "secrets_exposed": secret,
        "public_engine_changed": bool(protected_diff),
        "active_predictions_changed": bool(protected_diff),
    }
    blocking = [key for key, value in checks.items() if key not in {"secrets_exposed", "public_engine_changed", "active_predictions_changed"} and not value]
    if secret:
        blocking.append("secrets_exposed")
    if protected_diff:
        blocking.append("protected_files_changed")
    payload = {
        "version": "v2.29",
        "generated_at": utc_now(),
        "passed": not blocking,
        **checks,
        "blocking_issues": blocking,
        "warnings": [
            "Mini live run is intentionally capped; full 12,248-unit collection must be repeated over multiple sessions.",
            "Raw cache is local and intentionally ignored by git.",
        ],
    }
    publish(payload)
    print(f"V2.29 full collection validation: {'PASS' if payload['passed'] else 'FAIL'}")
    if blocking:
        raise SystemExit(blocking)


if __name__ == "__main__":
    main()
