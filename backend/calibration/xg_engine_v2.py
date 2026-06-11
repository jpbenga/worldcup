"""Expected-goals intensity model driven by chronological pre-match features."""

from __future__ import annotations

import math
from typing import Any


DEFAULT_XG_PARAMS = {
    "base_home_goals": 1.35,
    "base_away_goals": 1.15,
    "beta_rating": 0.22,
    "rating_factor_cap": 0.35,
    "recent_weight": 0.35,
    "strength_weight": 0.55,
    "lambda_min": 0.2,
    "lambda_max": 4.0,
}


def expected_goals(features: dict[str, float], params: dict[str, float]) -> tuple[float, float, dict[str, Any]]:
    rating_raw = math.exp(float(params["beta_rating"]) * features["rating_diff"] / 400.0)
    cap = float(params["rating_factor_cap"])
    rating_home = min(1 + cap, max(1 - cap, rating_raw))
    rating_away = min(1 + cap, max(1 - cap, 1 / rating_raw))
    recent_weight = float(params["recent_weight"])
    strength_weight = float(params["strength_weight"])
    home_recent = (features["home_recent_goals_for"] + features["away_recent_goals_against"]) / 2
    away_recent = (features["away_recent_goals_for"] + features["home_recent_goals_against"]) / 2
    home_strength = features["home_attack_strength"] * features["away_defense_weakness"]
    away_strength = features["away_attack_strength"] * features["home_defense_weakness"]
    raw_home = float(params["base_home_goals"]) * (
        (1 - recent_weight - strength_weight) + recent_weight * home_recent / 1.35 + strength_weight * home_strength
    ) * rating_home
    raw_away = float(params["base_away_goals"]) * (
        (1 - recent_weight - strength_weight) + recent_weight * away_recent / 1.35 + strength_weight * away_strength
    ) * rating_away
    lower, upper = float(params["lambda_min"]), float(params["lambda_max"])
    home = min(upper, max(lower, raw_home))
    away = min(upper, max(lower, raw_away))
    return home, away, {
        "raw_home_lambda": raw_home,
        "raw_away_lambda": raw_away,
        "rating_factor_home": rating_home,
        "rating_factor_away": rating_away,
        "home_lambda_clipped": home != raw_home,
        "away_lambda_clipped": away != raw_away,
    }


def lambda_audit(pairs: list[tuple[float, float, dict[str, Any]]]) -> dict[str, Any]:
    differences = [abs(home - away) for home, away, _ in pairs]
    return {
        "average_abs_lambda_diff": sum(differences) / len(differences),
        "share_abs_lambda_diff_gt_0_10": sum(value > 0.10 for value in differences) / len(differences),
        "share_abs_lambda_diff_gt_0_20": sum(value > 0.20 for value in differences) / len(differences),
        "share_abs_lambda_diff_gt_0_30": sum(value > 0.30 for value in differences) / len(differences),
        "lambda_diff_distribution": differences,
        "clipped_lambda_count": sum(meta["home_lambda_clipped"] or meta["away_lambda_clipped"] for _, _, meta in pairs),
    }
