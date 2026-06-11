"""Run validation-selected isolated draw-calibration and Dixon-Coles challengers."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.calibration.challengers import (
    BASE_MODEL_VERSION,
    DIXON_COLES_MODEL_VERSION,
    DRAW_MODEL_VERSION,
    apply_dixon_coles_rho,
    apply_draw_calibration,
    evaluate_challenger_predictions,
    metric_deltas,
    promising_guardrails,
    select_draw_factor,
    select_rho,
)
from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, utc_now, write_json

VERSION = "v1.2"
PROMOTION_RECOMMENDATION = "do_not_promote_yet"


def publish_results(payload: dict[str, Any]) -> None:
    generated = DATA_DIR / "generated" / "challenger_results_v1_2.json"
    snapshot = DATA_DIR / "snapshots" / "challenger_results_v1_2.json"
    frontend = FRONTEND_DATA_DIR / "challenger_results_v1_2.json"
    write_json(payload, generated)
    snapshot.parent.mkdir(parents=True, exist_ok=True)
    frontend.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(generated, snapshot)
    shutil.copy2(generated, frontend)


def assert_historical_alignment(predictions: list[dict[str, Any]], matches: list[dict[str, Any]], split: str) -> None:
    if any(match.get("season") == 2026 or match.get("is_future_fixture") for match in matches):
        raise ValueError(f"Future or 2026 fixtures found in {split}")
    if {item["match_id"] for item in predictions} != {item["match_id"] for item in matches}:
        raise ValueError(f"V0.9 predictions do not align with {split} historical matches")


def challenger_result(
    selected_params: dict[str, float],
    validation: dict[str, Any],
    test: dict[str, Any],
    baseline_validation: dict[str, Any],
    baseline_test: dict[str, Any],
    trials: list[dict[str, Any]],
    notes: list[str],
) -> dict[str, Any]:
    gates = promising_guardrails(validation, test, baseline_validation, baseline_test)
    return {
        "selected_params": selected_params,
        "selection_basis": "minimum validation log loss among candidates passing documented validation guardrails",
        "validation_trials": trials,
        "validation": validation,
        "test": test,
        "delta_vs_v0_9": {
            "validation": metric_deltas(validation, baseline_validation),
            "test": metric_deltas(test, baseline_test),
        },
        "guardrails": gates,
        "passed_guardrails": all(gates.values()),
        "candidate_for_future_combination": all(gates.values()),
        "notes": notes,
    }


def render_report(results: dict[str, Any]) -> str:
    def challenger_section(key: str, title: str) -> str:
        item = results["challengers"][key]
        validation, test = item["validation"], item["test"]
        params = ", ".join(f"`{name}={value}`" for name, value in item["selected_params"].items())
        gates = "\n".join(f"- [{'x' if passed else ' '}] {name}" for name, passed in item["guardrails"].items())
        rows = "\n".join(
            f"| {split.title()} | {metrics['accuracy_1x2']:.4f} | {metrics['log_loss_1x2']:.4f} | "
            f"{metrics['brier_score_1x2']:.4f} | {metrics['draw_calibration_gap']:+.4f} | "
            f"{metrics['top_3_score_hit_rate']:.4f} | {metrics['modal_1_1_rate']:.4f} | "
            f"{metrics['high_confidence_wrong_predictions']} |"
            for split, metrics in (("validation", validation), ("test", test))
        )
        deltas = item["delta_vs_v0_9"]["test"]
        return f"""## {title}

- Selected on validation only: {params}
- Test was used only after parameter selection: `true`
- Passed all prudential guardrails: `{str(item['passed_guardrails']).lower()}`
- Candidate for future combination: `{str(item['candidate_for_future_combination']).lower()}`

| Split | Accuracy | Log loss | Brier | Draw gap | Top-3 | Modal 1-1 | High-conf wrong |
|---|---:|---:|---:|---:|---:|---:|---:|
{rows}

Test deltas versus V0.9 (challenger minus base): log loss `{deltas['log_loss_1x2']:+.4f}`,
Brier `{deltas['brier_score_1x2']:+.4f}`, accuracy `{deltas['accuracy_1x2']:+.4f}`,
top-3 `{deltas['top_3_score_hit_rate']:+.4f}`, absolute draw-gap
`{deltas['draw_calibration_gap']:+.4f}`, modal 1-1 `{deltas['modal_1_1_rate']:+.4f}`,
and high-confidence wrong `{deltas['high_confidence_wrong_predictions']:+d}`.

### Guardrails

{gates}
"""

    base = results["v0_9_reference"]
    prototype = results["prototype_reference"]
    ranking = "\n".join(
        f"{index}. `{item['challenger']}` — test log loss `{item['test_log_loss_1x2']:.4f}`, "
        f"Brier `{item['test_brier_score_1x2']:.4f}`, all guardrails `{str(item['passed_guardrails']).lower()}`"
        for index, item in enumerate(results["ranking"], start=1)
    )
    return f"""# Isolated Calibration Challenger Results V1.2

## Objective and boundaries

V1.2 implements only the two first isolated challengers accepted in V1.1:
Draw-Calibrated Poisson and Dixon-Coles Rho Optimized. Both reuse fixed V0.9
historical predictions. Parameters are selected on the chronological validation
split only, and the test split is used only for final evaluation.

The active engine, World Cup 2026 predictions and main UX are unchanged. No
combined challenger is implemented and no model is promoted.

## V0.9 and V1.1 reminder

V0.9 remains the experimental base model. Its test log loss is
`{base['test']['log_loss_1x2']:.4f}`, Brier is `{base['test']['brier_score_1x2']:.4f}`,
and draw calibration gap is `{base['test']['draw_calibration_gap']:+.4f}`.
The available neutral prototype reference has test log loss
`{prototype['test']['log_loss_1x2']:.4f}` and Brier
`{prototype['test']['brier_score_1x2']:.4f}`.
V1.1 prioritized draw calibration first and Dixon-Coles rho optimization
second, with promotion blocked pending isolated evidence and human review.

## Validation-only selection method

- Draw factor grid: `1.05, 1.10, 1.15, 1.20, 1.25, 1.30, 1.35, 1.40, 1.50`.
- Rho grid: `-0.20, -0.15, -0.10, -0.05, 0.00, 0.05, 0.10`.
- Selection objective: minimum validation log loss among candidates passing
  the documented challenger-specific validation guardrails.
- Test metrics never influence parameter selection.

{challenger_section('draw_calibrated_poisson', 'Challenger A — Draw-Calibrated Poisson')}
{challenger_section('dixon_coles_rho_optimized', 'Challenger B — Dixon-Coles Rho Optimized')}
## Comparison and honest conclusion

{ranking}

{chr(10).join(f"- {item}" for item in results['recommendations'])}

## Decision

- Status: `experimental`
- Promotion recommendation: `{results['promotion_recommendation']}`
- Combined challenger implemented: `false`
- Active engine replaced: `false`
- World Cup 2026 predictions modified: `false`

No challenger is promoted by this experiment. Any future combination remains
conditional on isolated guardrails and a separate human decision.
"""


def main() -> None:
    generated = DATA_DIR / "generated"
    normalized = DATA_DIR / "normalized"
    base_predictions = {
        split: load_json(generated / f"historical_{split}_predictions_calibrated_v0_9.json")
        for split in ("validation", "test")
    }
    matches = {split: load_json(normalized / f"historical_{split}_matches.json") for split in ("validation", "test")}
    for split in ("validation", "test"):
        assert_historical_alignment(base_predictions[split], matches[split], split)

    # Reports are loaded as required inputs; enriched V1.2 metrics are recomputed consistently for all comparisons.
    source_reports = {
        split: load_json(generated / f"calibration_{split}_report_v0_9.json") for split in ("validation", "test")
    }
    prototype_comparison = load_json(generated / "calibrated_vs_prototype_comparison_v0_9.json")
    baseline = {
        split: evaluate_challenger_predictions(base_predictions[split], split, BASE_MODEL_VERSION)
        for split in ("validation", "test")
    }

    draw_factor, draw_trials = select_draw_factor(base_predictions["validation"], baseline["validation"])
    draw_predictions = {
        split: apply_draw_calibration(base_predictions[split], draw_factor) for split in ("validation", "test")
    }
    draw_metrics = {
        split: evaluate_challenger_predictions(draw_predictions[split], split, DRAW_MODEL_VERSION)
        for split in ("validation", "test")
    }

    rho, rho_trials = select_rho(base_predictions["validation"], baseline["validation"])
    rho_predictions = {split: apply_dixon_coles_rho(base_predictions[split], rho) for split in ("validation", "test")}
    rho_metrics = {
        split: evaluate_challenger_predictions(rho_predictions[split], split, DIXON_COLES_MODEL_VERSION)
        for split in ("validation", "test")
    }

    for split in ("validation", "test"):
        write_json(draw_predictions[split], generated / f"historical_{split}_predictions_draw_calibrated_v1_2.json")
        write_json(rho_predictions[split], generated / f"historical_{split}_predictions_dixon_coles_v1_2.json")

    challengers = {
        "draw_calibrated_poisson": challenger_result(
            {"draw_factor": draw_factor},
            draw_metrics["validation"],
            draw_metrics["test"],
            baseline["validation"],
            baseline["test"],
            draw_trials,
            ["Only 1X2 probabilities are adjusted; the V0.9 score matrix and exact-score rankings are preserved."],
        ),
        "dixon_coles_rho_optimized": challenger_result(
            {"rho": rho},
            rho_metrics["validation"],
            rho_metrics["test"],
            baseline["validation"],
            baseline["test"],
            rho_trials,
            ["Score matrices are regenerated from fixed V0.9 xG; no xG parameter is retrained."],
        ),
    }
    ranking = sorted(
        (
            {
                "challenger": name,
                "test_log_loss_1x2": item["test"]["log_loss_1x2"],
                "test_brier_score_1x2": item["test"]["brier_score_1x2"],
                "passed_guardrails": item["passed_guardrails"],
                "candidate_for_future_combination": item["candidate_for_future_combination"],
            }
            for name, item in challengers.items()
        ),
        key=lambda item: item["test_log_loss_1x2"],
    )
    candidates = [item["challenger"] for item in ranking if item["candidate_for_future_combination"]]
    results = {
        "generated_at": utc_now(),
        "version": VERSION,
        "status": "experimental",
        "promotion_recommendation": PROMOTION_RECOMMENDATION,
        "base_model": BASE_MODEL_VERSION,
        "selection_policy": "validation_only",
        "test_used_for_parameter_selection": False,
        "v0_9_reference": baseline,
        "source_v0_9_reports": source_reports,
        "prototype_reference": {
            split: prototype_comparison[split]["prototype"] for split in ("validation", "test")
        },
        "challengers": challengers,
        "ranking": ranking,
        "recommendations": [
            "Do not promote either challenger; promotion_recommendation remains do_not_promote_yet.",
            (
                f"Eligible for a future isolated-component combination review: {', '.join(candidates)}."
                if candidates
                else "Neither challenger passes every prudential gate for a future combination."
            ),
        ],
        "next_steps": [
            "Complete human review of V1.2 metrics and validation-only selection evidence.",
            "Keep the combined challenger deferred until an explicit post-review decision.",
        ],
        "combined_challenger_implemented": False,
        "active_engine_replaced": False,
        "world_cup_2026_predictions_modified": False,
    }
    publish_results(results)
    (PROJECT_ROOT / "docs" / "CHALLENGER_RESULTS_V1_2.md").write_text(render_report(results), encoding="utf-8")
    print(
        f"Selected draw_factor={draw_factor:.2f} and rho={rho:.2f} on validation only; "
        "published isolated V1.2 challenger results."
    )


if __name__ == "__main__":
    main()
