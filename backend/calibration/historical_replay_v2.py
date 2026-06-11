"""Build V2 historical predictions and evaluate replay/coherence metrics."""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from typing import Any

from backend.calibration.score_distribution_v2 import analytical_markets, score_distribution, top_scores
from backend.calibration.xg_engine_v2 import expected_goals, lambda_audit

OUTCOME_NAMES = ("home", "draw", "away")


def build_predictions(
    rows: list[dict[str, Any]], xgb_probabilities: list[list[float]], params: dict[str, Any], xg_params: dict[str, float]
) -> list[dict[str, Any]]:
    predictions, lambda_pairs = [], []
    blend = float(params["blend_weight_xgb"])
    for row, xgb_probs in zip(rows, xgb_probabilities):
        home_lambda, away_lambda, lambda_meta = expected_goals(row["features"], xg_params)
        lambda_pairs.append((home_lambda, away_lambda, lambda_meta))
        matrix = score_distribution(home_lambda, away_lambda)
        markets = analytical_markets(matrix)
        poisson_probs = [markets["home_win"], markets["draw"], markets["away_win"]]
        hybrid = [blend * xgb_probs[i] + (1 - blend) * poisson_probs[i] for i in range(3)]
        markets.update({"home_win": hybrid[0], "draw": hybrid[1], "away_win": hybrid[2]})
        predictions.append(
            {
                "match_id": row["match_id"],
                "model_version": "quant_hybrid_v2.0",
                "engine_version": "quant_hybrid_v2.0",
                "status": "experimental",
                "split": row["split"],
                "kickoff_at": row["kickoff_at"],
                "competition": row["competition"],
                "competition_tier": row["competition_tier"],
                "season": row["season"],
                "home_team": row["home_team"],
                "away_team": row["away_team"],
                "actual_home_score": row["actual_home_score"],
                "actual_away_score": row["actual_away_score"],
                "actual_1x2": OUTCOME_NAMES[int(row["labels"]["outcome_1x2"])],
                "predicted_home_xg": home_lambda,
                "predicted_away_xg": away_lambda,
                "xgb_1x2": {"home": xgb_probs[0], "draw": xgb_probs[1], "away": xgb_probs[2]},
                "poisson_1x2": {"home": poisson_probs[0], "draw": poisson_probs[1], "away": poisson_probs[2]},
                "markets": markets,
                "top_scores": top_scores(matrix, 5),
                "score_matrix": [{"score": score, "probability": probability} for score, probability in matrix.items()],
                "prediction_metadata": {"features": row["features"], "lambda": lambda_meta, "pre_match_only": True},
            }
        )
    audit = lambda_audit(lambda_pairs)
    for prediction in predictions:
        prediction["lambda_audit_summary"] = {key: value for key, value in audit.items() if key != "lambda_diff_distribution"}
    return predictions


def evaluate_predictions(predictions: list[dict[str, Any]]) -> dict[str, Any]:
    count = len(predictions)
    correct = exact = top2 = top3 = top5 = draws = predicted_draws = hcw = favorite_wins = 0
    logloss = brier = real_prob = draw_prob = favorite_prob = predicted_goals = actual_goals = 0.0
    modal = Counter()
    lambda_diffs = []
    clipped = 0
    for item in predictions:
        probabilities = [float(item["markets"]["home_win"]), float(item["markets"]["draw"]), float(item["markets"]["away_win"])]
        actual = OUTCOME_NAMES.index(item["actual_1x2"])
        predicted = max(range(3), key=lambda i: probabilities[i])
        correct += int(predicted == actual)
        logloss -= math.log(max(1e-15, probabilities[actual]))
        brier += sum((probability - float(i == actual)) ** 2 for i, probability in enumerate(probabilities))
        real_prob += probabilities[actual]
        draws += int(actual == 1)
        predicted_draws += int(predicted == 1)
        draw_prob += probabilities[1]
        favorite = 0 if probabilities[0] >= probabilities[2] else 2
        favorite_prob += probabilities[favorite]
        favorite_wins += int(actual == favorite)
        hcw += int(probabilities[predicted] >= 0.60 and predicted != actual)
        actual_score = f"{item['actual_home_score']}-{item['actual_away_score']}"
        scores = [score["score"] for score in item["top_scores"]]
        modal[scores[0]] += 1
        exact += int(actual_score == scores[0])
        top2 += int(actual_score in scores[:2])
        top3 += int(actual_score in scores[:3])
        top5 += int(actual_score in scores[:5])
        predicted_goals += item["predicted_home_xg"] + item["predicted_away_xg"]
        actual_goals += item["actual_home_score"] + item["actual_away_score"]
        lambda_diffs.append(abs(item["predicted_home_xg"] - item["predicted_away_xg"]))
        clipped += int(item["prediction_metadata"]["lambda"]["home_lambda_clipped"] or item["prediction_metadata"]["lambda"]["away_lambda_clipped"])
    draw_actual, draw_average = draws / count, draw_prob / count
    favorite_actual, favorite_average = favorite_wins / count, favorite_prob / count
    return {
        "matches": count, "accuracy_1x2": correct / count, "log_loss_1x2": logloss / count,
        "brier_score_1x2": brier / count, "exact_score_accuracy": exact / count,
        "top_2_score_hit_rate": top2 / count, "top_3_score_hit_rate": top3 / count, "top_5_score_hit_rate": top5 / count,
        "average_real_result_probability": real_prob / count, "draw_actual_rate": draw_actual,
        "draw_predicted_rate": predicted_draws / count, "draw_probability_average": draw_average,
        "draw_calibration_gap": draw_actual - draw_average, "favorite_actual_win_rate": favorite_actual,
        "favorite_predicted_win_rate": favorite_average, "favorite_calibration_gap": favorite_actual - favorite_average,
        "modal_score_distribution": dict(modal.most_common()), "modal_1_1_rate": modal["1-1"] / count,
        "high_confidence_wrong_predictions": hcw, "average_predicted_goals": predicted_goals / count,
        "average_actual_goals": actual_goals / count, "predicted_vs_actual_goal_gap": (predicted_goals - actual_goals) / count,
        "average_abs_lambda_diff": sum(lambda_diffs) / count,
        "share_abs_lambda_diff_gt_0_10": sum(value > .10 for value in lambda_diffs) / count,
        "share_abs_lambda_diff_gt_0_20": sum(value > .20 for value in lambda_diffs) / count,
        "share_abs_lambda_diff_gt_0_30": sum(value > .30 for value in lambda_diffs) / count,
        "clipped_lambda_count": clipped,
    }


def coherence_audit(predictions: list[dict[str, Any]], examples: int = 15) -> dict[str, Any]:
    aligned = clear = clear_aligned = favorite_1_1 = clear_draw_modal = 0
    misaligned = []
    for item in predictions:
        probs = [item["markets"]["home_win"], item["markets"]["draw"], item["markets"]["away_win"]]
        predicted = max(range(3), key=lambda i: probs[i])
        home, away = (int(value) for value in item["top_scores"][0]["score"].split("-"))
        score_outcome = 0 if home > away else 2 if away > home else 1
        is_aligned = predicted == score_outcome
        aligned += is_aligned
        favorite_1_1 += int(predicted != 1 and item["top_scores"][0]["score"] == "1-1")
        ordered = sorted(probs, reverse=True)
        is_clear = ordered[0] - ordered[1] >= 0.08
        clear += is_clear
        clear_aligned += int(is_clear and is_aligned)
        clear_draw_modal += int(is_clear and score_outcome == 1)
        if is_clear and not is_aligned and len(misaligned) < examples:
            misaligned.append({"match_id": item["match_id"], "home_team": item["home_team"], "away_team": item["away_team"], "modal_score": item["top_scores"][0]["score"], "probabilities": probs})
    count = len(predictions)
    return {
        "favorite_score_alignment_rate": aligned / count,
        "clear_favorite_matches": clear,
        "clear_favorite_score_alignment_rate": clear_aligned / clear if clear else None,
        "share_clear_favorites_with_draw_modal_score": clear_draw_modal / clear if clear else None,
        "share_favorites_with_1_1_modal_score": favorite_1_1 / count,
        "examples_misaligned_matches": misaligned,
    }


def segment_metrics(predictions: list[dict[str, Any]]) -> dict[str, Any]:
    def grouped(fn: Any) -> dict[str, Any]:
        groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for item in predictions:
            groups[fn(item)].append(item)
        return {name: evaluate_predictions(items) for name, items in sorted(groups.items())}
    return {
        "performance_by_competition": grouped(lambda x: str(x["competition"])),
        "performance_by_competition_tier": grouped(lambda x: str(x["competition_tier"])),
        "performance_by_season": grouped(lambda x: str(x["season"])),
        "performance_by_low_sample_teams": grouped(lambda x: "low_sample" if x["prediction_metadata"]["features"]["home_low_sample_flag"] or x["prediction_metadata"]["features"]["away_low_sample_flag"] else "non_low_sample"),
        "performance_by_clear_favorite_matches": grouped(lambda x: "clear_favorite" if sorted([x["markets"]["home_win"], x["markets"]["draw"], x["markets"]["away_win"]], reverse=True)[0] - sorted([x["markets"]["home_win"], x["markets"]["draw"], x["markets"]["away_win"]], reverse=True)[1] >= .08 else "not_clear_favorite"),
        "performance_by_balanced_matches": grouped(lambda x: "balanced" if abs(x["prediction_metadata"]["features"]["rating_diff"]) < 50 else "unbalanced"),
    }
