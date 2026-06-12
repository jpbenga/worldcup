"""Shared score-matrix audit and challenger helpers for V2.8."""

from __future__ import annotations

import math
import shutil
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, write_json

ROOT = Path(__file__).resolve().parents[2]
VERSION = "v2.8"
ENGINE = "quant_hybrid_v2.2"
FAVORITE_BUCKETS = ((0.0, 0.55), (0.55, 0.60), (0.60, 0.65), (0.65, 0.70), (0.70, 1.01))


def publish(payload: Any, name: str) -> None:
    target = DATA_DIR / "generated" / name
    write_json(payload, target)
    shutil.copy2(target, DATA_DIR / "snapshots" / name)
    shutil.copy2(target, FRONTEND_DATA_DIR / name)


def entries_to_matrix(item: dict[str, Any]) -> dict[tuple[int, int], float]:
    raw = item["score_matrix"]
    entries = raw["probabilities"] if isinstance(raw, dict) else raw
    return {tuple(map(int, row["score"].split("-"))): float(row["probability"]) for row in entries}


def matrix_to_entries(matrix: dict[tuple[int, int], float]) -> list[dict[str, Any]]:
    return [
        {"score": f"{h}-{a}", "home_goals": h, "away_goals": a, "probability": p}
        for (h, a), p in sorted(matrix.items())
    ]


def normalize(matrix: dict[tuple[int, int], float]) -> dict[tuple[int, int], float]:
    total = sum(matrix.values())
    return {score: probability / total for score, probability in matrix.items()}


def probability(matrix: dict[tuple[int, int], float], predicate: Callable[[int, int], bool]) -> float:
    return sum(value for (home, away), value in matrix.items() if predicate(home, away))


def expected_goals(matrix: dict[tuple[int, int], float]) -> tuple[float, float]:
    return (
        sum(home * value for (home, _), value in matrix.items()),
        sum(away * value for (_, away), value in matrix.items()),
    )


def outcome_probabilities(matrix: dict[tuple[int, int], float]) -> dict[str, float]:
    return {
        "home": probability(matrix, lambda h, a: h > a),
        "draw": probability(matrix, lambda h, a: h == a),
        "away": probability(matrix, lambda h, a: a > h),
    }


def favorite_info(probabilities: dict[str, float]) -> tuple[str, float]:
    side = "home" if probabilities["home"] >= probabilities["away"] else "away"
    return side, probabilities[side]


def score_outcome(score: tuple[int, int]) -> str:
    return "home" if score[0] > score[1] else "away" if score[1] > score[0] else "draw"


def ordered_scores(matrix: dict[tuple[int, int], float], limit: int = 10) -> list[dict[str, Any]]:
    return [
        {"score": f"{score[0]}-{score[1]}", "probability": probability}
        for score, probability in sorted(matrix.items(), key=lambda item: item[1], reverse=True)[:limit]
    ]


def top_compatible_score(matrix: dict[tuple[int, int], float], favorite_side: str) -> dict[str, Any]:
    candidates = [(score, p) for score, p in matrix.items() if score_outcome(score) == favorite_side]
    score, value = max(candidates, key=lambda item: item[1])
    return {"score": f"{score[0]}-{score[1]}", "probability": value}


def matrix_markets(matrix: dict[tuple[int, int], float]) -> dict[str, float]:
    outcome = outcome_probabilities(matrix)
    decisive = max(outcome["home"] + outcome["away"], 1e-12)
    return {
        **outcome,
        "over_2_5": probability(matrix, lambda h, a: h + a >= 3),
        "under_2_5": probability(matrix, lambda h, a: h + a <= 2),
        "btts_yes": probability(matrix, lambda h, a: h > 0 and a > 0),
        "home_scores": probability(matrix, lambda h, a: h > 0),
        "away_scores": probability(matrix, lambda h, a: a > 0),
        "home_scores_2_plus": probability(matrix, lambda h, a: h >= 2),
        "away_scores_2_plus": probability(matrix, lambda h, a: a >= 2),
        "home_win_by_1": probability(matrix, lambda h, a: h - a == 1),
        "away_win_by_1": probability(matrix, lambda h, a: a - h == 1),
        "home_win_by_2_plus": probability(matrix, lambda h, a: h - a >= 2),
        "away_win_by_2_plus": probability(matrix, lambda h, a: a - h >= 2),
        "three_plus_total": probability(matrix, lambda h, a: h + a >= 3),
        "dnb_home": outcome["home"] / decisive,
        "dnb_away": outcome["away"] / decisive,
    }


def modal_distribution(matrices: list[dict[tuple[int, int], float]]) -> tuple[dict[str, int], dict[str, int]]:
    scores: Counter[str] = Counter()
    totals: Counter[str] = Counter()
    for matrix in matrices:
        modal = max(matrix, key=matrix.get)
        scores[f"{modal[0]}-{modal[1]}"] += 1
        total = sum(modal)
        totals[str(total) if total <= 2 else "3+"] += 1
    return dict(scores.most_common()), {key: totals[key] for key in ("0", "1", "2", "3+")}


def bucket_name(probability_value: float) -> str:
    for low, high in FAVORITE_BUCKETS:
        if low <= probability_value < high:
            return f"{low:.2f}-{min(high, 1):.2f}"
    return "unknown"


def brier_1x2(probabilities: dict[str, float], actual: str) -> float:
    return sum((probabilities[key] - int(key == actual)) ** 2 for key in ("home", "draw", "away"))


def score_log_loss(matrix: dict[tuple[int, int], float], actual: tuple[int, int]) -> float:
    return -math.log(max(matrix.get(actual, 1e-12), 1e-12))


def historical_metrics(
    rows: list[dict[str, Any]], matrices: list[dict[tuple[int, int], float]], include_buckets: bool = True
) -> dict[str, Any]:
    aggregate: defaultdict[str, float] = defaultdict(float)
    by_bucket: defaultdict[str, list[int]] = defaultdict(list)
    actual_scores: Counter[str] = Counter()
    modal_scores, modal_totals = modal_distribution(matrices)
    actual_totals: Counter[str] = Counter()
    for index, (row, matrix) in enumerate(zip(rows, matrices)):
        actual = (int(row["actual_home_score"]), int(row["actual_away_score"]))
        actual_outcome = "home" if actual[0] > actual[1] else "away" if actual[1] > actual[0] else "draw"
        actual_scores[f"{actual[0]}-{actual[1]}"] += 1
        actual_total = sum(actual)
        actual_totals[str(actual_total) if actual_total <= 2 else "3+"] += 1
        ordered = [score for score, _ in sorted(matrix.items(), key=lambda item: item[1], reverse=True)]
        modal = ordered[0]
        markets = matrix_markets(matrix)
        probs = {key: markets[key] for key in ("home", "draw", "away")}
        favorite_side, favorite_probability = favorite_info(
            {"home": row["markets"]["home_win"], "draw": row["markets"]["draw"], "away": row["markets"]["away_win"]}
        )
        favorite_won = actual_outcome == favorite_side
        actual_margin = abs(actual[0] - actual[1]) if favorite_won else 0
        predicted_margin = abs(modal[0] - modal[1]) if score_outcome(modal) == favorite_side else 0
        aggregate["exact"] += actual == modal
        aggregate["top3"] += actual in ordered[:3]
        aggregate["top5"] += actual in ordered[:5]
        aggregate["score_log_loss"] += score_log_loss(matrix, actual)
        aggregate["total_goals_exact"] += sum(modal) == actual_total
        aggregate["over_2_5_brier"] += (markets["over_2_5"] - int(actual_total >= 3)) ** 2
        aggregate["one_x_two_accuracy"] += max(probs, key=probs.get) == actual_outcome
        aggregate["one_x_two_brier"] += brier_1x2(probs, actual_outcome)
        dnb_side = "home" if markets["dnb_home"] >= markets["dnb_away"] else "away"
        dnb_outcome = "push" if actual_outcome == "draw" else "win" if actual_outcome == dnb_side else "loss"
        aggregate[f"dnb_{dnb_outcome}"] += 1
        aggregate["favorite_actual_margin"] += actual_margin
        aggregate["favorite_predicted_modal_margin"] += predicted_margin
        aggregate["favorite_probability"] += favorite_probability
        aggregate["favorite_win"] += favorite_won
        aggregate["favorite_2_plus_actual"] += favorite_won and actual_margin >= 2
        aggregate["favorite_2_plus_probability"] += markets[f"{favorite_side}_win_by_2_plus"]
        by_bucket[bucket_name(favorite_probability)].append(index)
    n = len(rows)
    wins, losses, pushes = aggregate["dnb_win"], aggregate["dnb_loss"], aggregate["dnb_push"]
    metrics = {
        "matches": n,
        "exact_score_accuracy": aggregate["exact"] / n,
        "top_3_accuracy": aggregate["top3"] / n,
        "top_5_accuracy": aggregate["top5"] / n,
        "score_log_loss": aggregate["score_log_loss"] / n,
        "total_goals_accuracy": aggregate["total_goals_exact"] / n,
        "over_2_5_brier": aggregate["over_2_5_brier"] / n,
        "one_x_two_accuracy": aggregate["one_x_two_accuracy"] / n,
        "one_x_two_brier": aggregate["one_x_two_brier"] / n,
        "dnb_win_excluding_pushes": wins / (wins + losses),
        "dnb_non_loss_including_pushes": (wins + pushes) / n,
        "actual_average_favorite_margin": aggregate["favorite_actual_margin"] / n,
        "modal_average_favorite_margin": aggregate["favorite_predicted_modal_margin"] / n,
        "average_favorite_probability": aggregate["favorite_probability"] / n,
        "actual_favorite_win_rate": aggregate["favorite_win"] / n,
        "favorite_calibration_gap": aggregate["favorite_win"] / n - aggregate["favorite_probability"] / n,
        "actual_favorite_2_plus_rate": aggregate["favorite_2_plus_actual"] / n,
        "predicted_favorite_2_plus_probability": aggregate["favorite_2_plus_probability"] / n,
        "actual_score_distribution": dict(actual_scores.most_common()),
        "modal_score_distribution": modal_scores,
        "modal_total_goals_distribution": modal_totals,
        "actual_total_goals_distribution": {key: actual_totals[key] for key in ("0", "1", "2", "3+")},
    }
    if include_buckets:
        metrics["favorite_bucket_performance"] = {
            name: historical_metrics([rows[i] for i in indexes], [matrices[i] for i in indexes], False) | {"bucket": name}
            for name, indexes in by_bucket.items()
        }
    return metrics
