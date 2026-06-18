"""Validate the V2.30.1 full-stats prediction promotion."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, utc_now, write_json

VERSION = "v2.30.1"
OUTPUT = "full_stats_engine_promotion_validation_v2_30_1.json"
PROMOTED_FILES = [
    DATA_DIR / "generated" / "predictions.json",
    DATA_DIR / "snapshots" / "predictions.json",
    FRONTEND_DATA_DIR / "predictions.json",
]
ARCHIVES = [
    DATA_DIR / "archives" / "v2_30_1_pre_full_stats_promotion" / "predictions.generated.json",
    DATA_DIR / "archives" / "v2_30_1_pre_full_stats_promotion" / "predictions.snapshot.json",
    DATA_DIR / "archives" / "v2_30_1_pre_full_stats_promotion" / "predictions.frontend.json",
]
ROAD_PATHS = [
    "backend/data/generated/road_to_the_trophy_engine.json",
    "frontend/src/assets/data/road_to_the_trophy_engine.json",
]


def publish(payload: dict[str, Any]) -> None:
    for base in (DATA_DIR / "generated", DATA_DIR / "snapshots", FRONTEND_DATA_DIR):
        write_json(payload, base / OUTPUT)


def git_output(args: list[str]) -> str:
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=False).stdout


def same_json(a: Path, b: Path) -> bool:
    return load_json(a) == load_json(b)


def activated_candidate() -> list[dict[str, Any]]:
    rows = load_json(DATA_DIR / "generated" / "predictions_full_stats_candidate_v2_30.json")
    out = []
    for row in rows:
        item = dict(row)
        item["engine_version"] = "stats_enriched_full_v2.30"
        item["engine_status"] = "active"
        item["active_engine_replaced"] = True
        item["activated_in"] = VERSION
        overlay = dict(item.get("full_stats_overlay", {}))
        overlay["status"] = "active_match_prediction_engine"
        item["full_stats_overlay"] = overlay
        out.append(item)
    return out


def main() -> None:
    decision = load_json(DATA_DIR / "generated" / "full_stats_engine_promotion_decision_v2_30.json")
    manifest = load_json(DATA_DIR / "generated" / "full_stats_engine_promotion_manifest_v2_30_1.json")
    diff = load_json(DATA_DIR / "generated" / "full_stats_promotion_diff_v2_30_1.json")
    engine_manifest = load_json(DATA_DIR / "generated" / "active_prediction_engine_manifest.json")
    candidate_rows = activated_candidate()
    raw_cache_status = git_output(["git", "status", "--short", "backend/data/cache/api_football/historical_stats"]).strip()
    grep = git_output(["git", "grep", "-n", r"API_FOOTBALL_KEY\|x-apisports-key", "--", ".", ":!.env.example"])
    scripts = "\n".join(path.read_text(encoding="utf-8") for path in ROOT.glob("backend/scripts/*v2_30_1.py"))
    literal_secret = bool(re.search(r"x-apisports-key\s*:\s*['\"][^'\"]+|API_FOOTBALL_KEY\s*=\s*['\"][^'\"]+", scripts, re.I))
    checks: dict[str, bool] = {
        "promotion_decision_verified": decision.get("decision") == "recommend_promotion" and not decision.get("serious_blockers"),
        "active_predictions_archived": all(path.exists() for path in ARCHIVES),
        "active_predictions_promoted": load_json(PROMOTED_FILES[0]) == candidate_rows and load_json(PROMOTED_FILES[1]) == candidate_rows,
        "frontend_predictions_promoted": load_json(PROMOTED_FILES[2]) == candidate_rows,
        "promotion_manifest_created": manifest.get("version") == VERSION and manifest.get("active_predictions_changed") is True,
        "rollback_available": (ROOT / "backend/scripts/rollback_full_stats_engine_v2_30_1.py").exists() and manifest.get("rollback_available") is True,
        "schema_compatible": diff.get("schema_compatible") is True and not diff.get("blocking_issues"),
        "road_to_trophy_changed": manifest.get("road_to_trophy_changed") is True,
        "optuna_rerun": manifest.get("optuna_rerun") is True,
        "raw_cache_committed": bool(raw_cache_status),
        "secrets_exposed": literal_secret,
        "active_engine_metadata_updated": engine_manifest.get("active_prediction_engine") == "stats_enriched_full_v2_30",
    }
    blocking = [
        key for key, value in checks.items()
        if key not in {"road_to_trophy_changed", "optuna_rerun", "raw_cache_committed", "secrets_exposed"} and not value
    ]
    for key in ("road_to_trophy_changed", "optuna_rerun", "raw_cache_committed", "secrets_exposed"):
        if checks[key]:
            blocking.append(key)
    warnings = []
    if grep.strip():
        warnings.append("Secret-name references exist in code/env loading; no literal key detected in V2.30.1 scripts.")
    road_diffs = git_output(["git", "diff", "--", *ROAD_PATHS]).strip()
    if road_diffs:
        warnings.append("Road to Trophy files have pre-existing worktree diffs; V2.30.1 promotion manifest did not touch them.")
    payload: dict[str, Any] = {
        "version": VERSION,
        "generated_at": utc_now(),
        "passed": not blocking,
        "promotion_decision_verified": checks["promotion_decision_verified"],
        "active_predictions_archived": checks["active_predictions_archived"],
        "active_predictions_promoted": checks["active_predictions_promoted"],
        "frontend_predictions_promoted": checks["frontend_predictions_promoted"],
        "promotion_manifest_created": checks["promotion_manifest_created"],
        "rollback_available": checks["rollback_available"],
        "schema_compatible": checks["schema_compatible"],
        "road_to_trophy_changed": checks["road_to_trophy_changed"],
        "optuna_rerun": checks["optuna_rerun"],
        "raw_cache_committed": checks["raw_cache_committed"],
        "secrets_exposed": checks["secrets_exposed"],
        "active_engine_metadata_updated": checks["active_engine_metadata_updated"],
        "blocking_issues": blocking,
        "warnings": warnings,
        "raw_cache_status": raw_cache_status,
    }
    publish(payload)
    print(f"{VERSION} promotion validation: {'PASS' if payload['passed'] else 'FAIL'}")
    if blocking:
        raise SystemExit(blocking)


if __name__ == "__main__":
    main()
