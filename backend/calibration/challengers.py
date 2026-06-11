"""Isolated, validation-selected calibration challengers for V1.2."""

from __future__ import annotations

import copy
import math
from collections import Counter
from typing import Any, Iterable

from backend.markets.market_derivation import derive_markets
from backend.score_matrix.score_matrix import generate_score_matrix

BASE_MODEL_VERSION = "calibrated_simple_poisson_v0.9"
DRAW_MODEL_VERSION = "draw_calibrated_poisson_v1.2"
DIXON_COLES_MODEL_VERSION = "dixon_coles_rho_optimized_v1.2"
DRAW_FACTOR_GRID = (1.05, 1.10, 1.15, 1.20, 1.25, 1.30, 1.35, 1.40, 1.50)
RHO_GRID = (-0.20, -0.15, -0.10, -0.05, 0.00, 0.05, 0.10)
OUTCOMES = ("home", "draw", "away")
MARKET_KEYS = {"home": "home_win", "draw": "draw", "away": "away_win"}


def _predicted_outcome(markets: dict[str, Any]) -> str:
    return max(OUTCOMES, key=lambda outcome: float(markets[MARKET_KEYS[outcome]]))


def _score_probability(score: str, probability: float) -> dict[str, Any]:
    home_goals, away_goals = (int(value) for value in score.split("-", maxsplit=1))
    return {"score": score, "home_goals": home_goals, "away_goals": away_goals, "probability": probability}


def _metadata(prediction: dict[str, Any], model_version: str, selected_params: dict[str, float]) -> dict[str, Any]:
    updated = copy.deepcopy(prediction)
    updated["model_version"] = model_version
    updated["base_model_version"] = BASE_MODEL_VERSION
    updated["status"] = "experimental"
    updated["promotion_recommendation"] = "do_not_promote_yet"
    updated["selected_params"] = selected_params
    return updated


def apply_draw_calibration(predictions: list[dict[str, Any]], draw_factor: float) -> list[dict[str, Any]]:
    """Multiply draw probabilities and renormalize the V0.9 1X2 market."""
    if draw_factor <= 0:
        raise ValueError("draw_factor must be positive")
    calibrated = []
    for source in predictions:
        prediction = _metadata(source, DRAW_MODEL_VERSION, {"draw_factor": draw_factor})
        markets = copy.deepcopy(source["markets"])
        home = float(markets["home_win"])
        draw = float(markets["draw"]) * draw_factor
        away = float(markets["away_win"])
        normalizer = home + draw + away
        home, draw, away = home / normalizer, draw / normalizer, away / normalizer
        markets.update(
            {
                "home_win": home,
                "draw": draw,
                "away_win": away,
                "home_or_draw": home + draw,
                "away_or_draw": away + draw,
                "no_draw": home + away,
            }
        )
        prediction["markets"] = markets
        prediction["predicted_1x2"] = _predicted_outcome(markets)
        prediction["is_correct_1x2"] = prediction["predicted_1x2"] == prediction["actual_1x2"]
        prediction["prediction_metadata"] = {
            **copy.deepcopy(source.get("prediction_metadata", {})),
            "challenger_adjustment": "draw_probability_multiplier",
            "score_matrix_preserved_from_base_model": True,
        }
        calibrated.append(prediction)
    return calibrated


def apply_dixon_coles_rho(predictions: list[dict[str, Any]], rho: float, max_goals: int = 8) -> list[dict[str, Any]]:
    """Regenerate score matrices and markets from fixed V0.9 xG with a selected rho."""
    regenerated = []
    for source in predictions:
        prediction = _metadata(source, DIXON_COLES_MODEL_VERSION, {"rho": rho})
        matrix = generate_score_matrix(
            float(source["predicted_home_xg"]), float(source["predicted_away_xg"]), max_goals=max_goals, rho=rho
        )
        derived = derive_markets(matrix)
        prediction["score_matrix"] = [_score_probability(score, probability) for score, probability in matrix.items()]
        prediction["markets"] = {key: value for key, value in derived.items() if key != "top_exact_scores"}
        prediction["top_scores"] = [
            _score_probability(str(item["score"]), float(item["probability"])) for item in derived["top_exact_scores"]
        ]
        prediction["predicted_1x2"] = _predicted_outcome(prediction["markets"])
        prediction["is_correct_1x2"] = prediction["predicted_1x2"] == prediction["actual_1x2"]
        prediction["prediction_metadata"] = {
            **copy.deepcopy(source.get("prediction_metadata", {})),
            "challenger_adjustment": "dixon_coles_rho",
            "score_matrix_preserved_from_base_model": False,
        }
        regenerated.append(prediction)
    return regenerated


def evaluate_challenger_predictions(predictions: list[dict[str, Any]], split: str, model_version: str) -> dict[str, Any]:
    """Calculate the V1.2 aggregate calibration and score metrics."""
    if not predictions:
        raise ValueError("At least one prediction is required")
    count = len(predictions)
    correct = exact = top_3 = draws = predicted_draws = high_confidence_wrong = 0
    favorite_wins = 0
    log_loss = brier = real_probability = draw_probability = favorite_probability = 0.0
    modal_scores: Counter[str] = Counter()
    for prediction in predictions:
        actual = str(prediction["actual_1x2"])
        probabilities = {
            outcome: float(prediction["markets"][market_key]) for outcome, market_key in MARKET_KEYS.items()
        }
        predicted = _predicted_outcome(prediction["markets"])
        actual_probability = probabilities[actual]
        correct += int(predicted == actual)
        log_loss -= math.log(max(1e-15, min(1 - 1e-15, actual_probability)))
        brier += sum((probabilities[outcome] - float(outcome == actual)) ** 2 for outcome in OUTCOMES)
        real_probability += actual_probability
        draws += int(actual == "draw")
        predicted_draws += int(predicted == "draw")
        draw_probability += probabilities["draw"]
        confidence = probabilities[predicted]
        high_confidence_wrong += int(confidence >= 0.60 and predicted != actual)
        favorite = max(("home", "away"), key=lambda outcome: probabilities[outcome])
        favorite_probability += probabilities[favorite]
        favorite_wins += int(actual == favorite)
        actual_score = f"{prediction['actual_home_score']}-{prediction['actual_away_score']}"
        modal = str(prediction["top_scores"][0]["score"])
        modal_scores[modal] += 1
        exact += int(modal == actual_score)
        top_3 += int(actual_score in {str(item["score"]) for item in prediction["top_scores"][:3]})

    draw_actual_rate = draws / count
    average_draw_probability = draw_probability / count
    return {
        "model_version": model_version,
        "split": split,
        "matches": count,
        "accuracy_1x2": correct / count,
        "log_loss_1x2": log_loss / count,
        "brier_score_1x2": brier / count,
        "exact_score_accuracy": exact / count,
        "top_3_score_hit_rate": top_3 / count,
        "average_real_result_probability": real_probability / count,
        "draw_actual_rate": draw_actual_rate,
        "draw_predicted_rate": predicted_draws / count,
        "draw_probability_average": average_draw_probability,
        "draw_calibration_gap": draw_actual_rate - average_draw_probability,
        "favorite_actual_win_rate": favorite_wins / count,
        "favorite_predicted_win_rate": favorite_probability / count,
        "modal_score_distribution": dict(modal_scores.most_common()),
        "modal_1_1_rate": modal_scores["1-1"] / count,
        "high_confidence_wrong_predictions": high_confidence_wrong,
    }


def metric_deltas(challenger: dict[str, Any], baseline: dict[str, Any]) -> dict[str, float | int]:
    """Return challenger-minus-V0.9 deltas; negative is better for losses and gaps."""
    return {
        "accuracy_1x2": float(challenger["accuracy_1x2"]) - float(baseline["accuracy_1x2"]),
        "log_loss_1x2": float(challenger["log_loss_1x2"]) - float(baseline["log_loss_1x2"]),
        "brier_score_1x2": float(challenger["brier_score_1x2"]) - float(baseline["brier_score_1x2"]),
        "exact_score_accuracy": float(challenger["exact_score_accuracy"]) - float(baseline["exact_score_accuracy"]),
        "top_3_score_hit_rate": float(challenger["top_3_score_hit_rate"]) - float(baseline["top_3_score_hit_rate"]),
        "draw_calibration_gap": abs(float(challenger["draw_calibration_gap"]))
        - abs(float(baseline["draw_calibration_gap"])),
        "modal_1_1_rate": float(challenger["modal_1_1_rate"]) - float(baseline["modal_1_1_rate"]),
        "high_confidence_wrong_predictions": int(challenger["high_confidence_wrong_predictions"])
        - int(baseline["high_confidence_wrong_predictions"]),
    }


def select_draw_factor(
    validation_predictions: list[dict[str, Any]], baseline_metrics: dict[str, Any], grid: Iterable[float] = DRAW_FACTOR_GRID
) -> tuple[float, list[dict[str, Any]]]:
    """Select draw factor using validation log loss among settings passing prudent guards."""
    trials = []
    for factor in grid:
        metrics = evaluate_challenger_predictions(
            apply_draw_calibration(validation_predictions, factor), "validation", DRAW_MODEL_VERSION
        )
        guards = {
            "brier_not_materially_worse": metrics["brier_score_1x2"] <= baseline_metrics["brier_score_1x2"] + 0.01,
            "accuracy_drop_at_most_2_points": metrics["accuracy_1x2"] >= baseline_metrics["accuracy_1x2"] - 0.02,
            "predicted_draw_rate_closer": abs(metrics["draw_actual_rate"] - metrics["draw_predicted_rate"])
            < abs(baseline_metrics["draw_actual_rate"] - baseline_metrics["draw_predicted_rate"]),
        }
        trials.append({"params": {"draw_factor": factor}, "metrics": metrics, "selection_guardrails": guards})
    eligible = [trial for trial in trials if all(trial["selection_guardrails"].values())]
    selected = min(eligible or trials, key=lambda trial: trial["metrics"]["log_loss_1x2"])
    return float(selected["params"]["draw_factor"]), trials


def select_rho(
    validation_predictions: list[dict[str, Any]], baseline_metrics: dict[str, Any], grid: Iterable[float] = RHO_GRID
) -> tuple[float, list[dict[str, Any]]]:
    """Select rho using validation log loss among settings passing prudent guards."""
    trials = []
    for rho in grid:
        metrics = evaluate_challenger_predictions(
            apply_dixon_coles_rho(validation_predictions, rho), "validation", DIXON_COLES_MODEL_VERSION
        )
        guards = {
            "modal_1_1_not_increased": metrics["modal_1_1_rate"] <= baseline_metrics["modal_1_1_rate"],
            "brier_not_materially_worse": metrics["brier_score_1x2"] <= baseline_metrics["brier_score_1x2"] + 0.01,
            "top_3_drop_at_most_2_points": metrics["top_3_score_hit_rate"]
            >= baseline_metrics["top_3_score_hit_rate"] - 0.02,
        }
        trials.append({"params": {"rho": rho}, "metrics": metrics, "selection_guardrails": guards})
    eligible = [trial for trial in trials if all(trial["selection_guardrails"].values())]
    selected = min(eligible or trials, key=lambda trial: trial["metrics"]["log_loss_1x2"])
    return float(selected["params"]["rho"]), trials


def promising_guardrails(
    validation: dict[str, Any], test: dict[str, Any], baseline_validation: dict[str, Any], baseline_test: dict[str, Any]
) -> dict[str, bool]:
    """Apply the V1.1 prudential success gates without promoting a model."""
    return {
        "test_log_loss_improves_by_0_01": test["log_loss_1x2"] <= baseline_test["log_loss_1x2"] - 0.01,
        "test_brier_improves_by_0_01": test["brier_score_1x2"] <= baseline_test["brier_score_1x2"] - 0.01,
        "draw_gap_reduced_validation": abs(validation["draw_calibration_gap"])
        < abs(baseline_validation["draw_calibration_gap"]),
        "draw_gap_reduced_test": abs(test["draw_calibration_gap"]) < abs(baseline_test["draw_calibration_gap"]),
        "validation_log_loss_improved": validation["log_loss_1x2"] < baseline_validation["log_loss_1x2"],
        "validation_brier_improved": validation["brier_score_1x2"] < baseline_validation["brier_score_1x2"],
        "accuracy_guardrail_validation": validation["accuracy_1x2"] >= baseline_validation["accuracy_1x2"] - 0.01,
        "accuracy_guardrail_test": test["accuracy_1x2"] >= baseline_test["accuracy_1x2"] - 0.01,
        "top_3_guardrail_validation": validation["top_3_score_hit_rate"]
        >= baseline_validation["top_3_score_hit_rate"] - 0.01,
        "top_3_guardrail_test": test["top_3_score_hit_rate"] >= baseline_test["top_3_score_hit_rate"] - 0.01,
        "modal_1_1_reduced": test["modal_1_1_rate"] < baseline_test["modal_1_1_rate"],
        "high_confidence_wrong_not_increased_validation": validation["high_confidence_wrong_predictions"]
        <= baseline_validation["high_confidence_wrong_predictions"],
        "high_confidence_wrong_not_increased_test": test["high_confidence_wrong_predictions"]
        <= baseline_test["high_confidence_wrong_predictions"],
    }
