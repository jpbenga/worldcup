"""Audit top-score diversity without changing prediction probabilities."""

from __future__ import annotations

import shutil
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, PROJECT_ROOT, load_json, write_json


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def distribution(predictions: list[dict[str, Any]]) -> dict[str, int]:
    return dict(sorted(Counter(prediction["top_scores"][0]["score"] for prediction in predictions).items()))


def main() -> None:
    baseline = load_json(DATA_DIR / "generated" / "predictions_baseline.json")
    elo = load_json(DATA_DIR / "generated" / "predictions_elo.json")
    comparison = load_json(DATA_DIR / "generated" / "model_comparison.json")
    matches = load_json(DATA_DIR / "normalized" / "matches.json")
    baseline_dist = distribution(baseline)
    elo_dist = distribution(elo)
    total = len(matches)
    baseline_xg = [prediction.get("model_inputs", {}).get("baseline_home_xg") for prediction in baseline]
    elo_inputs = [prediction.get("model_inputs", {}) for prediction in elo]
    elo_diffs = [prediction.get("elo_features", {}).get("elo_diff") for prediction in elo]
    max_delta = max((abs(value) for item in comparison for value in item["deltas"].values()), default=0.0)
    one_one_baseline = baseline_dist.get("1-1", 0) / total if total else 0.0
    one_one_elo = elo_dist.get("1-1", 0) / total if total else 0.0
    warning = (
        "Predictions are highly concentrated on 1-1 because every real fixture currently receives the same "
        "neutral baseline expected goals. Elo adjusts markets but does not change the modal score."
    )
    audit = {
        "generated_at": utc_now(),
        "total_matches": total,
        "baseline_top_score_distribution": baseline_dist,
        "elo_top_score_distribution": elo_dist,
        "one_one_count_baseline": baseline_dist.get("1-1", 0),
        "one_one_count_elo": elo_dist.get("1-1", 0),
        "one_one_rate_baseline": one_one_baseline,
        "one_one_rate_elo": one_one_elo,
        "top_score_changed_count": sum(item["baseline_top_score"] != item["elo_top_score"] for item in comparison),
        "elo_unavailable_count": sum(not item["elo_available"] for item in comparison),
        "average_absolute_elo_diff": round(
            sum(abs(value) for value in elo_diffs if isinstance(value, int))
            / max(1, sum(isinstance(value, int) for value in elo_diffs)),
            2,
        ),
        "max_delta": max_delta,
        "baseline_home_xg_unique": sorted({value for value in baseline_xg if isinstance(value, (int, float))}),
        "elo_adjusted_home_xg_range": [
            min(item["adjusted_home_xg"] for item in elo_inputs),
            max(item["adjusted_home_xg"] for item in elo_inputs),
        ],
        "elo_adjusted_away_xg_range": [
            min(item["adjusted_away_xg"] for item in elo_inputs),
            max(item["adjusted_away_xg"] for item in elo_inputs),
        ],
        "is_highly_uniform": one_one_baseline >= 0.8 or one_one_elo >= 0.8,
        "engine_warning": warning,
        "recommendations": [
            "Keep the current engine marked as experimental and not historically calibrated.",
            "Replace neutral baseline xG with validated team-specific historical features in a future phase.",
            "Expose Elo and xG inputs so users can understand the uniform top-score output.",
            "Do not force artificial score diversity.",
        ],
    }
    generated = DATA_DIR / "generated" / "prediction_diversity_audit.json"
    snapshot = DATA_DIR / "snapshots" / "prediction_diversity_audit.json"
    frontend = FRONTEND_DATA_DIR / "prediction_diversity_audit.json"
    write_json(audit, generated)
    shutil.copy2(generated, snapshot)
    shutil.copy2(generated, frontend)

    doc = PROJECT_ROOT / "docs" / "PREDICTION_ENGINE_AUDIT_V0_5.md"
    doc.write_text(
        f"""# Prediction Engine Audit V0.5

## Result

- Matches audited: `{total}`
- Baseline top-score distribution: `{baseline_dist}`
- Elo top-score distribution: `{elo_dist}`
- Baseline 1-1 rate: `{one_one_baseline:.1%}`
- Elo 1-1 rate: `{one_one_elo:.1%}`
- Top scores changed by Elo: `{audit['top_score_changed_count']}`
- Elo unavailable: `{audit['elo_unavailable_count']}`
- Maximum market delta: `{max_delta:.4f}`

## Diagnosis

{warning}

This is not a sorting bug or a missing-Elo fallback. The active real-data
baseline assigns neutral `1.35 / 1.35` expected goals to every fixture because
validated historical team features are not yet available. The moderate Elo
layer changes market probabilities, but does not change the most likely score.

## Decision

Do not force diversity and do not present these predictions as calibrated.
Keep the prototype visible, expose its inputs, and replace neutral baseline
features only when validated historical data is available.
""",
        encoding="utf-8",
    )
    print(f"Audited {total} predictions; baseline 1-1 rate={one_one_baseline:.1%}, Elo 1-1 rate={one_one_elo:.1%}.")


if __name__ == "__main__":
    main()
