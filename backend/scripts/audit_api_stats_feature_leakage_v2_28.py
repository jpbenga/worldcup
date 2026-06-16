"""Audit V2.28 lagged API statistics features for temporal leakage."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, write_json

OUTPUT = "api_stats_feature_leakage_audit_v2_28.json"
SOURCE = DATA_DIR / "generated" / "api_stats_lagged_features_v2_28.json"


def publish(payload: dict[str, Any]) -> None:
    target = DATA_DIR / "generated" / OUTPUT
    write_json(payload, target)
    shutil.copy2(target, DATA_DIR / "snapshots" / OUTPUT)
    shutil.copy2(target, FRONTEND_DATA_DIR / OUTPUT)


def main() -> None:
    data = load_json(SOURCE)
    violations = []
    checked = 0
    for row in data["features"]:
        target = row["date"]
        source_date = row.get("max_source_date")
        checked += int(row.get("source_date_count", 0))
        if source_date and source_date >= target:
            violations.append({"match_id": row["match_id"], "target_date": target, "max_source_date": source_date})
        if not row.get("leakage_safe"):
            violations.append({"match_id": row["match_id"], "target_date": target, "reason": "row leakage_safe flag is false"})
    payload = {
        "version": "v2.28", "passed": not violations,
        "matches_checked": len(data["features"]), "features_checked": checked,
        "leakage_violations": violations, "lineup_timestamp_risks": [],
        "warnings": ["Lineups are excluded from V2.28 model features until a pre-match publication timestamp is proven."],
    }
    publish(payload)
    print(f"V2.28 API stats leakage audit: {'PASS' if payload['passed'] else 'FAIL'}; checked={checked}")
    if violations:
        raise SystemExit("Temporal leakage detected")


if __name__ == "__main__":
    main()
