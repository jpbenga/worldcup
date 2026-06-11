"""Train and evaluate the isolated V0.9 historical calibration experiment."""

from __future__ import annotations

import argparse
import shutil
import sys
from collections import Counter
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.calibration.calibration_metrics import evaluate_predictions
from backend.calibration.historical_prediction_runner import predict_matches
from backend.calibration.simple_poisson_calibrator import MODEL_FAMILY, MODEL_VERSION, CalibratedSimplePoisson
from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, utc_now, write_json

LIMITATIONS = [
    "Experimental first calibration; it is not the active or promoted prediction engine.",
    "The model uses goals and team identity only, without Elo, venue neutrality, form, or competition parameters.",
    "AET/PEN score semantics and mixed-scope competition rows remain unresolved.",
    "The chronological split changes competition composition over time.",
]


def publish(filename: str, payload: Any) -> None:
    snapshot = DATA_DIR / "snapshots" / filename
    frontend = FRONTEND_DATA_DIR / filename
    write_json(payload, snapshot)
    frontend.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(snapshot, frontend)


def training_summary(train: list[dict[str, Any]], model: CalibratedSimplePoisson) -> dict[str, Any]:
    return {
        "model_version": MODEL_VERSION,
        "model_family": MODEL_FAMILY,
        "trained_on": "historical_train_matches.json",
        "historically_calibrated": True,
        "status": "experimental",
        "train_matches": len(train),
        "train_teams": len({match[key] for match in train for key in ("home_team", "away_team")}),
        "date_min": min(match["kickoff_at"] for match in train),
        "date_max": max(match["kickoff_at"] for match in train),
        "competitions": dict(Counter(match["competition"] for match in train)),
        "global_home_goals": model.global_home_goals,
        "global_away_goals": model.global_away_goals,
        "limitations": LIMITATIONS,
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-only", action="store_true")
    parser.add_argument("--evaluate-validation", action="store_true")
    parser.add_argument("--evaluate-test", action="store_true")
    args = parser.parse_args(argv)
    evaluate_validation = not args.train_only and (args.evaluate_validation or not args.evaluate_test)
    evaluate_test = not args.train_only and (args.evaluate_test or not args.evaluate_validation)

    normalized = DATA_DIR / "normalized"
    train: list[dict[str, Any]] = load_json(normalized / "historical_train_matches.json")
    validation: list[dict[str, Any]] = load_json(normalized / "historical_validation_matches.json")
    test: list[dict[str, Any]] = load_json(normalized / "historical_test_matches.json")
    if any(match.get("season") == 2026 or match.get("is_future_fixture") for match in train + validation + test):
        raise ValueError("Future or 2026 fixtures must not enter the calibration experiment")

    model = CalibratedSimplePoisson().fit(train)
    write_json(model.parameters(), DATA_DIR / "generated" / "calibrated_model_v0_9_params.json")
    summary = training_summary(train, model)
    write_json(summary, DATA_DIR / "generated" / "calibrated_model_v0_9_training_summary.json")
    reports: dict[str, Any] = {}

    for split, matches, enabled in (("validation", validation, evaluate_validation), ("test", test, evaluate_test)):
        if not enabled:
            continue
        predictions = predict_matches(matches, model.predict_expected_goals, MODEL_VERSION, MODEL_FAMILY, True)
        report = evaluate_predictions(predictions, split, MODEL_VERSION, LIMITATIONS)
        write_json(predictions, DATA_DIR / "generated" / f"historical_{split}_predictions_calibrated_v0_9.json")
        write_json(report, DATA_DIR / "generated" / f"calibration_{split}_report_v0_9.json")
        reports[split] = report

    status = {
        "generated_at": utc_now(),
        "experiment": "V0.9 — First Calibration Experiment on Historical Dataset",
        "model_version": MODEL_VERSION,
        "model_family": MODEL_FAMILY,
        "historically_calibrated": True,
        "status": "experimental",
        "active_engine_replaced": False,
        "world_cup_2026_predictions_modified": False,
        "trained_on": "historical_train_matches.json",
        "train_matches": len(train),
        "validation_report": reports.get("validation"),
        "test_report": reports.get("test"),
        "promotion_recommendation": "do_not_promote_yet",
        "limitations": LIMITATIONS,
    }
    publish("calibration_experiment_status_v0_9.json", status)
    print(
        f"Trained {MODEL_VERSION} on {len(train)} matches; "
        f"validation={'yes' if evaluate_validation else 'no'}, test={'yes' if evaluate_test else 'no'}."
    )


if __name__ == "__main__":
    main()
