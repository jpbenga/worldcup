"""Create deterministic chronological 70/15/15 splits without training a model."""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from historical_data_utils import publish
from pipeline_utils import DATA_DIR, load_json, write_json


def stats(items: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "matches": len(items),
        "date_min": items[0]["kickoff_at"] if items else None,
        "date_max": items[-1]["kickoff_at"] if items else None,
        "competitions": dict(Counter(item["competition"] for item in items)),
        "seasons": dict(Counter(str(item["season"]) for item in items)),
    }


def main() -> None:
    matches: list[dict[str, Any]] = load_json(DATA_DIR / "normalized" / "historical_matches_expanded.json")
    matches = sorted(matches, key=lambda item: (item["kickoff_at"], item["api_football_fixture_id"]))
    total = len(matches)
    train_end = int(total * 0.70)
    validation_end = train_end + int(total * 0.15)
    train, validation, test = matches[:train_end], matches[train_end:validation_end], matches[validation_end:]
    outputs = {
        "historical_train_matches.json": train,
        "historical_validation_matches.json": validation,
        "historical_test_matches.json": test,
    }
    for filename, payload in outputs.items():
        write_json(payload, DATA_DIR / "normalized" / filename)

    split_stats = {"train": stats(train), "validation": stats(validation), "test": stats(test)}
    split_ids = [{item["api_football_fixture_id"] for item in split} for split in (train, validation, test)]
    report = {
        "split_method": "chronological_70_15_15",
        "total_matches": total,
        "train_matches": len(train),
        "validation_matches": len(validation),
        "test_matches": len(test),
        "train_date_min": split_stats["train"]["date_min"],
        "train_date_max": split_stats["train"]["date_max"],
        "validation_date_min": split_stats["validation"]["date_min"],
        "validation_date_max": split_stats["validation"]["date_max"],
        "test_date_min": split_stats["test"]["date_min"],
        "test_date_max": split_stats["test"]["date_max"],
        "competitions_by_split": {key: value["competitions"] for key, value in split_stats.items()},
        "seasons_by_split": {key: value["seasons"] for key, value in split_stats.items()},
        "leakage_checks": {
            "future_2026_fixtures_excluded": all(item["season"] != 2026 for item in matches),
            "date_order_valid": (
                not train
                or not validation
                or not test
                or train[-1]["kickoff_at"] <= validation[0]["kickoff_at"] <= validation[-1]["kickoff_at"] <= test[0]["kickoff_at"]
            ),
            "duplicate_fixture_ids_across_splits": bool(
                (split_ids[0] & split_ids[1]) or (split_ids[0] & split_ids[2]) or (split_ids[1] & split_ids[2])
            ),
        },
    }
    write_json(report, DATA_DIR / "generated" / "historical_dataset_split_report.json")
    publish("historical_dataset_split_report.json", report)
    (PROJECT_ROOT / "docs" / "HISTORICAL_DATASET_SPLIT.md").write_text(
        f"""# Historical Dataset Split

## Method

Strict deterministic chronological split: first 70% train, next 15%
validation, final 15% test. No randomization, model training or prediction
evaluation occurs in this step.

## Counts and ranges

- Train: `{len(train)}` — `{report['train_date_min']}` to `{report['train_date_max']}`
- Validation: `{len(validation)}` — `{report['validation_date_min']}` to `{report['validation_date_max']}`
- Test: `{len(test)}` — `{report['test_date_min']}` to `{report['test_date_max']}`

## Leakage checks

`{report['leakage_checks']}`

Competition composition differs by period and must be considered in future
calibration experiments.
""",
        encoding="utf-8",
    )
    print(f"Created chronological splits: train={len(train)}, validation={len(validation)}, test={len(test)}.")


if __name__ == "__main__":
    main()
