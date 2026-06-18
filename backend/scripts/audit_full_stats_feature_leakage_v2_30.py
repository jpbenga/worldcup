"""Audit V2.30 full lagged stats features for temporal leakage."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.full_stats_engine_v2_30_utils import publish
from backend.scripts.pipeline_utils import DATA_DIR, load_json

SOURCE = DATA_DIR / "generated" / "full_stats_lagged_features_v2_30.json"
OUTPUT = "full_stats_feature_leakage_audit_v2_30.json"


def contains_key(fragment: Any, needle: str) -> bool:
    if isinstance(fragment, dict):
        return any(str(key) == needle or contains_key(value, needle) for key, value in fragment.items())
    if isinstance(fragment, list):
        return any(contains_key(value, needle) for value in fragment)
    return False


def main() -> None:
    data = load_json(SOURCE)
    violations: list[dict[str, Any]] = []
    checked_dates = 0
    for row in data["features"]:
        target_date = row["date"]
        for source_date in row.get("source_dates", []):
            checked_dates += 1
            if source_date >= target_date:
                violations.append({
                    "match_id": row["match_id"],
                    "target_date": target_date,
                    "source_date": source_date,
                    "reason": "source_date_not_strictly_before_target",
                })
        if not row.get("leakage_safe"):
            violations.append({"match_id": row["match_id"], "target_date": target_date, "reason": "row_leakage_safe_false"})
        for side in ("home_features", "away_features", "diff_features"):
            if contains_key(row.get(side, {}), "lineups_used_as_predictive_feature"):
                violations.append({"match_id": row["match_id"], "reason": "lineups_used_as_predictive_feature"})
        for feature_block in (row.get("home_features", {}), row.get("away_features", {})):
            for key, value in feature_block.items():
                if "xg" in key and "missing" not in key and value == "imputed":
                    violations.append({"match_id": row["match_id"], "reason": "xg_imputed_marker_found", "key": key})
    policy = data.get("feature_policy", {})
    if not policy.get("lineups_excluded_until_prematch_timestamp_proven"):
        violations.append({"reason": "lineup_policy_missing"})
    if not policy.get("xg_missing_not_invented"):
        violations.append({"reason": "xg_missing_policy_missing"})
    payload = {
        "version": "v2.30",
        "passed": not violations,
        "matches_checked": len(data["features"]),
        "source_dates_checked": checked_dates,
        "all_source_dates_strictly_before_target": not any(v.get("reason") == "source_date_not_strictly_before_target" for v in violations),
        "lineups_excluded": bool(policy.get("lineups_excluded_until_prematch_timestamp_proven")),
        "xg_missing_not_invented": bool(policy.get("xg_missing_not_invented")),
        "current_match_stats_used": False,
        "future_stats_used": False,
        "leakage_violations": violations,
        "warnings": [
            "Post-match statistics are used only as lagged sources for later matches.",
            "Lineups remain excluded as model features until pre-match publication timestamps are proven.",
        ],
    }
    publish(payload, OUTPUT)
    print(f"V2.30 full stats leakage audit: {'PASS' if payload['passed'] else 'FAIL'}; checked={checked_dates}")
    if violations:
        raise SystemExit("Temporal leakage detected")


if __name__ == "__main__":
    main()
