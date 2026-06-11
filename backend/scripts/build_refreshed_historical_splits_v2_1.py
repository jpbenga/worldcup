"""Create deterministic chronological V2.1 splits without fitting any model."""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, write_json
from backend.scripts.v2_1_data_utils import base_report, days_since, load, publish, write_doc


def split_stats(items: list[dict[str, Any]]) -> dict[str, Any]:
    teams = {str(item["home_team"]) for item in items} | {str(item["away_team"]) for item in items}
    return {
        "matches": len(items),
        "date_min": items[0]["kickoff_at"] if items else None,
        "date_max": items[-1]["kickoff_at"] if items else None,
        "competitions": dict(Counter(str(item["competition"]) for item in items)),
        "teams": len(teams),
    }


def main() -> None:
    matches = sorted(
        load(DATA_DIR / "normalized" / "historical_matches_refreshed_v2_1.json"),
        key=lambda item: (item["kickoff_at"], item["api_football_fixture_id"]),
    )
    train_end = int(len(matches) * 0.70)
    validation_end = train_end + int(len(matches) * 0.15)
    splits = {"train": matches[:train_end], "validation": matches[train_end:validation_end], "test": matches[validation_end:]}
    for name, items in splits.items():
        write_json(items, DATA_DIR / "normalized" / f"historical_{name}_matches_v2_1.json")
    stats = {name: split_stats(items) for name, items in splits.items()}
    old_report = load(DATA_DIR / "generated" / "historical_dataset_split_report.json")
    ids = {name: {item["api_football_fixture_id"] for item in items} for name, items in splits.items()}
    report = base_report() | {
        "split_method": "chronological_70_15_15",
        "total_matches": len(matches),
        "train": stats["train"],
        "validation": stats["validation"],
        "test": stats["test"],
        "test_freshness_days": days_since(stats["test"]["date_max"]),
        "comparison_with_old_splits": {
            "old_total_matches": old_report["total_matches"],
            "new_total_matches": len(matches),
            "old_train_matches": old_report["train_matches"],
            "new_train_matches": len(splits["train"]),
            "old_validation_matches": old_report["validation_matches"],
            "new_validation_matches": len(splits["validation"]),
            "old_test_matches": old_report["test_matches"],
            "new_test_matches": len(splits["test"]),
            "old_test_date_max": old_report["test_date_max"],
            "new_test_date_max": stats["test"]["date_max"],
        },
        "leakage_checks": {
            "date_order_valid": stats["train"]["date_max"] <= stats["validation"]["date_min"] <= stats["validation"]["date_max"] <= stats["test"]["date_min"],
            "duplicate_fixture_ids_across_splits": bool(ids["train"] & ids["validation"] or ids["train"] & ids["test"] or ids["validation"] & ids["test"]),
            "future_world_cup_2026_fixtures_excluded": all(not (item["competition_id"] == 1 and item["season"] == 2026) for item in matches),
            "random_split_used": False,
        },
    }
    publish("historical_splits_v2_1_report.json", report)
    write_doc(
        "HISTORICAL_SPLITS_V2_1.md",
        f"""# Historical Splits V2.1

V2.1 creates a deterministic chronological `70/15/15` split without model
training, randomization or parameter selection.

- Train: `{stats['train']['matches']}` matches, `{stats['train']['date_min']}` to `{stats['train']['date_max']}`
- Validation: `{stats['validation']['matches']}` matches, `{stats['validation']['date_min']}` to `{stats['validation']['date_max']}`
- Test: `{stats['test']['matches']}` matches, `{stats['test']['date_min']}` to `{stats['test']['date_max']}`
- Test freshness: `{report['test_freshness_days']}` days

The previous split contained `{old_report['total_matches']}` matches and ended
at `{old_report['test_date_max']}`. The refreshed split contains
`{len(matches)}` matches and ends at `{stats['test']['date_max']}`. Competition
and team composition per split, exact date boundaries and leakage checks are
retained in the JSON report.
""",
    )
    print(f"V2.1 splits: train={len(splits['train'])}, validation={len(splits['validation'])}, test={len(splits['test'])}.")


if __name__ == "__main__":
    main()
