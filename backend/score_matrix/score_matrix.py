"""Autonomous Poisson/Dixon-Coles score-matrix generator recycled from the prototype."""

from __future__ import annotations

import math
from collections.abc import Mapping

ScoreMatrix = dict[str, float]


def poisson_probability(goals: int, expected_goals: float) -> float:
    if goals < 0 or expected_goals < 0:
        raise ValueError("goals and expected_goals must be non-negative")
    return math.exp(-expected_goals) * expected_goals**goals / math.factorial(goals)


def dixon_coles_adjustment(
    home_goals: int, away_goals: int, home_lambda: float, away_lambda: float, rho: float
) -> float:
    if (home_goals, away_goals) == (0, 0):
        return 1.0 - home_lambda * away_lambda * rho
    if (home_goals, away_goals) == (0, 1):
        return 1.0 + home_lambda * rho
    if (home_goals, away_goals) == (1, 0):
        return 1.0 + away_lambda * rho
    if (home_goals, away_goals) == (1, 1):
        return 1.0 - rho
    return 1.0


def normalize_score_matrix(matrix: Mapping[str, float]) -> ScoreMatrix:
    total = sum(matrix.values())
    if total <= 0:
        raise ValueError("Score matrix must have a positive probability mass")
    return {score: probability / total for score, probability in matrix.items()}


def generate_score_matrix(
    home_expected_goals: float,
    away_expected_goals: float,
    max_goals: int = 8,
    rho: float = 0.0,
    normalize: bool = True,
) -> ScoreMatrix:
    """Return probabilities for every score from 0-0 through max_goals-max_goals."""
    if home_expected_goals < 0 or away_expected_goals < 0:
        raise ValueError("Expected goals must be non-negative")
    if max_goals < 0:
        raise ValueError("max_goals must be non-negative")
    matrix: ScoreMatrix = {}
    for home_goals in range(max_goals + 1):
        for away_goals in range(max_goals + 1):
            probability = (
                poisson_probability(home_goals, home_expected_goals)
                * poisson_probability(away_goals, away_expected_goals)
                * dixon_coles_adjustment(home_goals, away_goals, home_expected_goals, away_expected_goals, rho)
            )
            if probability < 0:
                raise ValueError("rho produced a negative score probability")
            matrix[f"{home_goals}-{away_goals}"] = probability
    return normalize_score_matrix(matrix) if normalize else matrix


def top_exact_scores(matrix: Mapping[str, float], limit: int = 5) -> list[dict[str, float | str]]:
    if limit < 0:
        raise ValueError("limit must be non-negative")
    return [
        {"score": score, "probability": probability}
        for score, probability in sorted(matrix.items(), key=lambda item: item[1], reverse=True)[:limit]
    ]
