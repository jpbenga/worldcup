"""Compare the V0.9 calibrated experiment with the neutral prototype baseline."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.calibration.calibration_metrics import evaluate_predictions
from backend.calibration.historical_prediction_runner import predict_matches
from backend.calibration.simple_poisson_calibrator import MODEL_VERSION
from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, utc_now, write_json

PROTOTYPE_VERSION = "prototype_neutral_v0.5"
PROTOTYPE_FAMILY = "neutral_prototype_poisson"


def neutral_expected_goals(home_team: str, away_team: str) -> tuple[float, float, dict[str, Any]]:
    return 1.35, 1.35, {"input_basis": "neutral_prototype_defaults", "home_team": home_team, "away_team": away_team}


def publish(filename: str, payload: Any) -> None:
    generated = DATA_DIR / "generated" / filename
    snapshot = DATA_DIR / "snapshots" / filename
    frontend = FRONTEND_DATA_DIR / filename
    write_json(payload, generated)
    snapshot.parent.mkdir(parents=True, exist_ok=True)
    frontend.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(generated, snapshot)
    shutil.copy2(generated, frontend)


def delta(prototype: dict[str, Any], calibrated: dict[str, Any]) -> dict[str, float]:
    return {
        metric: float(calibrated[metric]) - float(prototype[metric])
        for metric in (
            "accuracy_1x2",
            "log_loss_1x2",
            "brier_score_1x2",
            "exact_score_accuracy",
            "top_3_score_hit_rate",
        )
    }


def render_report(comparison: dict[str, Any]) -> str:
    def row(split: str, metric: str) -> str:
        values = comparison[split]
        return (
            f"| {split.title()} | {metric} | {values['prototype'][metric]:.4f} | "
            f"{values['calibrated'][metric]:.4f} | {values['delta'][metric]:+.4f} |"
        )

    rows = "\n".join(
        row(split, metric)
        for split in ("validation", "test")
        for metric in ("accuracy_1x2", "log_loss_1x2", "brier_score_1x2", "exact_score_accuracy", "top_3_score_hit_rate")
    )
    return f"""# Calibration Experiment V0.9

## Objective and isolation

V0.9 trains an explainable simple Poisson model on the `917` historical train
matches, evaluates it on the chronological validation and test splits, and
compares it with the neutral `1.35 / 1.35` prototype. It remains separate from
the active World Cup 2026 engine and does not modify future predictions.

## Model

The **Calibrated Simple Poisson Model v0.9** estimates global home/away scoring
rates plus smoothed team home/away attack and defence strengths. Smoothing
weight is `8`, sparse-team threshold is `5`, and expected goals are bounded to
`0.2–3.5`. Unknown teams fall back to global rates. Elo, competition effects,
neutral-site context and recent form are not modeled.

## Chronological evaluation

The model is trained on `917` matches involving `159` teams from
`2014-06-12` through `2021-06-23`. Validation contains `196` matches and test
contains `198`; both are later than the training period.

| Split | Metric | Prototype | Calibrated | Delta calibrated - prototype |
|---|---|---:|---:|---:|
{rows}

Lower is better for log loss and Brier score. Higher is better for accuracy
and score hit rates. The calibrated model improves 1X2 accuracy, log loss and
Brier score on both splits. It does not improve validation exact-score
accuracy, slightly reduces test exact-score accuracy, and leaves test top-3
score hit rate unchanged.

## Calibrated score and goal results

- Validation exact score accuracy: `{comparison['validation']['calibrated']['exact_score_accuracy']:.4f}`
- Validation top-3 score hit rate: `{comparison['validation']['calibrated']['top_3_score_hit_rate']:.4f}`
- Validation average predicted goals: `{comparison['validation']['calibrated']['average_predicted_home_goals']:.4f}` home / `{comparison['validation']['calibrated']['average_predicted_away_goals']:.4f}` away
- Validation average actual goals: `{comparison['validation']['calibrated']['average_actual_home_goals']:.4f}` home / `{comparison['validation']['calibrated']['average_actual_away_goals']:.4f}` away
- Test exact score accuracy: `{comparison['test']['calibrated']['exact_score_accuracy']:.4f}`
- Test top-3 score hit rate: `{comparison['test']['calibrated']['top_3_score_hit_rate']:.4f}`
- Test average predicted goals: `{comparison['test']['calibrated']['average_predicted_home_goals']:.4f}` home / `{comparison['test']['calibrated']['average_predicted_away_goals']:.4f}` away
- Test average actual goals: `{comparison['test']['calibrated']['average_actual_home_goals']:.4f}` home / `{comparison['test']['calibrated']['average_actual_away_goals']:.4f}` away

## Decision

- Decision: `{comparison['decision']}`
- Promotion recommendation: `{comparison['promotion_recommendation']}`
- Active engine replaced: `false`

The experiment is not promoted automatically. The dataset remains
medium-sufficiency; competition composition changes across chronological
splits, and AET/PEN, neutral-site and mixed-scope semantics remain unresolved.

## Next step

Review the validation/test deltas and segmented errors manually before a V1.0
experiment. A next challenger should test competition-aware or chronological
form features without touching the active engine.
"""


def main() -> None:
    comparison: dict[str, Any] = {
        "generated_at": utc_now(),
        "prototype_model_version": PROTOTYPE_VERSION,
        "calibrated_model_version": MODEL_VERSION,
    }
    for split in ("validation", "test"):
        matches = load_json(DATA_DIR / "normalized" / f"historical_{split}_matches.json")
        calibrated_predictions = load_json(
            DATA_DIR / "generated" / f"historical_{split}_predictions_calibrated_v0_9.json"
        )
        match_ids = {match["match_id"] for match in matches}
        prediction_ids = {prediction["match_id"] for prediction in calibrated_predictions}
        if len(calibrated_predictions) != len(matches) or prediction_ids != match_ids:
            raise ValueError(f"Calibrated predictions do not align with the {split} split")
        prototype_predictions = predict_matches(matches, neutral_expected_goals, PROTOTYPE_VERSION, PROTOTYPE_FAMILY, False)
        prototype = evaluate_predictions(
            prototype_predictions,
            split,
            PROTOTYPE_VERSION,
            ["Neutral fixed 1.35 / 1.35 xG baseline; not historically calibrated."],
        )
        calibrated = evaluate_predictions(calibrated_predictions, split, MODEL_VERSION)
        comparison[split] = {"prototype": prototype, "calibrated": calibrated, "delta": delta(prototype, calibrated)}
    comparison["decision"] = "experimental_only"
    comparison["promotion_recommendation"] = "do_not_promote_yet"
    comparison["active_engine_replaced"] = False
    comparison["world_cup_2026_predictions_modified"] = False
    publish("calibrated_vs_prototype_comparison_v0_9.json", comparison)
    (PROJECT_ROOT / "docs" / "CALIBRATION_EXPERIMENT_V0_9.md").write_text(render_report(comparison), encoding="utf-8")
    print("Compared calibrated V0.9 with the neutral prototype on validation and test.")


if __name__ == "__main__":
    main()
