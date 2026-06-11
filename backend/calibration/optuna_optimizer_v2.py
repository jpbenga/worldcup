"""Validation-only Optuna search for the V2 hybrid 1X2 core."""

from __future__ import annotations

import math
from typing import Any

import optuna
from optuna.pruners import MedianPruner
from optuna.samplers import TPESampler

from backend.calibration.feature_builder_v2 import build_chronological_features
from backend.calibration.internal_rating_v2 import RatingConfig
from backend.calibration.score_distribution_v2 import analytical_markets, score_distribution, top_scores
from backend.calibration.xg_engine_v2 import expected_goals
from backend.calibration.xgboost_market_models_v2 import predict_multiclass, train_multiclass


def rating_config(params: dict[str, Any]) -> RatingConfig:
    return RatingConfig(
        scale=float(params["rating_scale"]),
        k_factor=float(params["rating_k_factor"]),
        goal_margin_multiplier=bool(params["goal_margin_multiplier"]),
        competition_weighting=bool(params["competition_weighting"]),
        context_advantage=float(params["context_advantage"]),
    )


def xgb_params(params: dict[str, Any]) -> dict[str, Any]:
    return {key: params[key] for key in ("max_depth", "eta", "subsample", "colsample_bytree", "min_child_weight", "lambda", "alpha", "num_boost_round")}


def xg_params(params: dict[str, Any]) -> dict[str, float]:
    return {
        "base_home_goals": float(params["base_home_goals"]),
        "base_away_goals": float(params["base_away_goals"]),
        "beta_rating": float(params["beta_rating"]),
        "rating_factor_cap": float(params["rating_factor_cap"]),
        "recent_weight": float(params["recent_weight"]),
        "strength_weight": float(params["strength_weight"]),
        "lambda_min": 0.2,
        "lambda_max": 4.0,
    }


def suggest(trial: optuna.Trial) -> dict[str, Any]:
    recent = trial.suggest_float("recent_weight", 0.10, 0.40, step=0.05)
    strength = trial.suggest_float("strength_weight", 0.35, 0.70, step=0.05)
    if recent + strength > 0.9:
        strength = 0.9 - recent
    return {
        "rating_scale": trial.suggest_categorical("rating_scale", [350, 400, 450]),
        "rating_k_factor": trial.suggest_categorical("rating_k_factor", [15, 20, 25, 30]),
        "goal_margin_multiplier": trial.suggest_categorical("goal_margin_multiplier", [False, True]),
        "competition_weighting": trial.suggest_categorical("competition_weighting", [False, True]),
        "context_advantage": trial.suggest_categorical("context_advantage", [0, 35, 60]),
        "base_home_goals": trial.suggest_float("base_home_goals", 1.15, 1.55, step=0.05),
        "base_away_goals": trial.suggest_float("base_away_goals", 0.95, 1.35, step=0.05),
        "beta_rating": trial.suggest_float("beta_rating", 0.10, 0.50, step=0.05),
        "rating_factor_cap": trial.suggest_categorical("rating_factor_cap", [0.20, 0.30, 0.40]),
        "recent_weight": recent,
        "strength_weight": strength,
        "blend_weight_xgb": trial.suggest_float("blend_weight_xgb", 0.35, 0.80, step=0.05),
        "max_depth": trial.suggest_categorical("max_depth", [2, 3, 4]),
        "eta": trial.suggest_categorical("eta", [0.01, 0.03, 0.05, 0.08]),
        "subsample": trial.suggest_categorical("subsample", [0.7, 0.85, 1.0]),
        "colsample_bytree": trial.suggest_categorical("colsample_bytree", [0.7, 0.85, 1.0]),
        "min_child_weight": trial.suggest_categorical("min_child_weight", [1, 3, 5, 8]),
        "lambda": trial.suggest_categorical("lambda", [0.5, 1.0, 2.0, 5.0]),
        "alpha": trial.suggest_categorical("alpha", [0.0, 0.25, 0.5, 1.0]),
        "num_boost_round": trial.suggest_categorical("num_boost_round", [50, 100, 200, 350]),
    }


def validation_components(
    rows: list[dict[str, Any]], xgb_probabilities: list[list[float]], params: dict[str, Any]
) -> dict[str, float]:
    log_loss = brier = secondary_brier = 0.0
    modal_1_1 = clear = aligned = high_wrong = 0
    blend = float(params["blend_weight_xgb"])
    for row, xgb_probs in zip(rows, xgb_probabilities):
        home_lam, away_lam, _ = expected_goals(row["features"], xg_params(params))
        matrix = score_distribution(home_lam, away_lam)
        market = analytical_markets(matrix)
        poisson_probs = [market["home_win"], market["draw"], market["away_win"]]
        probabilities = [blend * xgb_probs[i] + (1 - blend) * poisson_probs[i] for i in range(3)]
        actual = int(row["labels"]["outcome_1x2"])
        log_loss -= math.log(max(1e-15, probabilities[actual]))
        brier += sum((probability - float(i == actual)) ** 2 for i, probability in enumerate(probabilities))
        predicted = max(range(3), key=lambda i: probabilities[i])
        high_wrong += int(probabilities[predicted] >= 0.60 and predicted != actual)
        modal = top_scores(matrix, 1)[0]["score"]
        modal_1_1 += int(modal == "1-1")
        ordered = sorted(probabilities, reverse=True)
        if ordered[0] - ordered[1] >= 0.08:
            clear += 1
            home, away = (int(value) for value in str(modal).split("-"))
            aligned += int((predicted == 0 and home > away) or (predicted == 2 and away > home) or (predicted == 1 and home == away))
        secondary_brier += (market["over_2_5"] - row["labels"]["over_2_5"]) ** 2
    count = len(rows)
    modal_rate = modal_1_1 / count
    alignment = aligned / clear if clear else 0.0
    return {
        "log_loss_1x2": log_loss / count,
        "brier_score_1x2": brier / count,
        "modal_1_1_rate": modal_rate,
        "clear_favorite_score_alignment_rate": alignment,
        "high_confidence_wrong_rate": high_wrong / count,
        "secondary_over_2_5_brier": secondary_brier / count,
        "penalty_modal_1_1": max(0.0, modal_rate - 0.40) * 0.20,
        "penalty_bad_favorite_alignment": max(0.0, 0.50 - alignment) * 0.20,
        "penalty_high_confidence_wrong": high_wrong / count * 0.10,
        "penalty_bad_secondary_markets": secondary_brier / count * 0.10,
    }


def optimize(split_matches: dict[str, list[dict[str, Any]]], n_trials: int = 100) -> tuple[dict[str, Any], dict[str, Any]]:
    def objective(trial: optuna.Trial) -> float:
        params = suggest(trial)
        rows, _, _, _, _ = build_chronological_features(split_matches, rating_config(params))
        model = train_multiclass(rows["train"], xgb_params(params))
        probabilities = predict_multiclass(model, rows["validation"])
        components = validation_components(rows["validation"], probabilities, params)
        objective_value = (
            components["log_loss_1x2"]
            + 0.75 * components["brier_score_1x2"]
            + components["penalty_modal_1_1"]
            + components["penalty_bad_favorite_alignment"]
            + components["penalty_high_confidence_wrong"]
            + components["penalty_bad_secondary_markets"]
        )
        trial.set_user_attr("objective_components", components)
        trial.set_user_attr("effective_params", params)
        return objective_value

    study = optuna.create_study(direction="minimize", sampler=TPESampler(seed=2026), pruner=MedianPruner())
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    study.optimize(objective, n_trials=n_trials, catch=(Exception,))
    completed = [trial for trial in study.trials if trial.value is not None]
    top = sorted(completed, key=lambda item: item.value)[:20]
    summary = {
        "mode": "quick" if n_trials <= 300 else "full",
        "n_trials": len(study.trials),
        "completed_trials": len(completed),
        "failed_trials": len(study.trials) - len(completed),
        "best_trial": study.best_trial.number,
        "best_value": study.best_value,
        "best_params": study.best_trial.user_attrs["effective_params"],
        "objective_components": study.best_trial.user_attrs["objective_components"],
        "top_20_trials": [
            {"number": trial.number, "value": trial.value, "params": trial.params, "objective_components": trial.user_attrs.get("objective_components")}
            for trial in top
        ],
    }
    return study.best_trial.user_attrs["effective_params"], summary
