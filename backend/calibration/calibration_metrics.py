"""Evaluation metrics for historical probabilistic football predictions."""

from __future__ import annotations

import math
from collections import Counter
from typing import Any

OUTCOMES = ("home", "draw", "away")


def actual_outcome(home_score: int, away_score: int) -> str:
    if home_score > away_score:
        return "home"
    if home_score < away_score:
        return "away"
    return "draw"


def evaluate_predictions(
    predictions: list[dict[str, Any]], split: str, model_version: str, limitations: list[str] | None = None
) -> dict[str, Any]:
    if not predictions:
        raise ValueError("At least one prediction is required")
    epsilon = 1e-15
    correct_1x2 = exact_hits = top_3_hits = 0
    log_loss = brier = real_probability = 0.0
    predicted_home_goals = predicted_away_goals = actual_home_goals = actual_away_goals = 0.0
    modal_scores: Counter[str] = Counter()
    bucket_stats: dict[str, dict[str, float | int]] = {}
    for prediction in predictions:
        outcome = str(prediction["actual_1x2"])
        markets = prediction["markets"]
        probabilities = {
            "home": float(markets["home_win"]),
            "draw": float(markets["draw"]),
            "away": float(markets["away_win"]),
        }
        probability = probabilities[outcome]
        correct_1x2 += int(prediction["predicted_1x2"] == outcome)
        log_loss -= math.log(max(epsilon, min(1.0 - epsilon, probability)))
        brier += sum((probabilities[key] - float(key == outcome)) ** 2 for key in OUTCOMES)
        real_probability += probability
        actual_score = f"{prediction['actual_home_score']}-{prediction['actual_away_score']}"
        exact_hits += int(prediction["top_scores"][0]["score"] == actual_score)
        top_3_hits += int(actual_score in {item["score"] for item in prediction["top_scores"][:3]})
        modal_scores[str(prediction["top_scores"][0]["score"])] += 1
        predicted_home_goals += float(prediction["predicted_home_xg"])
        predicted_away_goals += float(prediction["predicted_away_xg"])
        actual_home_goals += float(prediction["actual_home_score"])
        actual_away_goals += float(prediction["actual_away_score"])
        predicted_outcome = str(prediction["predicted_1x2"])
        predicted_probability = probabilities[predicted_outcome]
        lower = min(0.9, int(predicted_probability * 10) / 10)
        label = f"{lower:.1f}-{lower + 0.1:.1f}"
        bucket = bucket_stats.setdefault(label, {"matches": 0, "probability_sum": 0.0, "realized_sum": 0.0})
        bucket["matches"] += 1
        bucket["probability_sum"] += predicted_probability
        bucket["realized_sum"] += float(predicted_outcome == outcome)

    count = len(predictions)
    calibration_buckets = {
        label: {
            "matches": int(values["matches"]),
            "average_predicted_outcome_probability": values["probability_sum"] / int(values["matches"]),
            "realized_rate": values["realized_sum"] / int(values["matches"]),
        }
        for label, values in sorted(bucket_stats.items())
    }
    return {
        "model_version": model_version,
        "split": split,
        "matches": count,
        "accuracy_1x2": correct_1x2 / count,
        "log_loss_1x2": log_loss / count,
        "brier_score_1x2": brier / count,
        "exact_score_accuracy": exact_hits / count,
        "top_3_score_hit_rate": top_3_hits / count,
        "average_real_result_probability": real_probability / count,
        "average_predicted_home_goals": predicted_home_goals / count,
        "average_predicted_away_goals": predicted_away_goals / count,
        "average_actual_home_goals": actual_home_goals / count,
        "average_actual_away_goals": actual_away_goals / count,
        "modal_score_distribution": dict(modal_scores.most_common()),
        "calibration_buckets": calibration_buckets,
        "limitations": limitations or [],
    }
