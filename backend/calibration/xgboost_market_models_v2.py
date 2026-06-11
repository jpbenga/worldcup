"""Regularized XGBoost models for 1X2 and binary football markets."""

from __future__ import annotations

from typing import Any

import numpy as np
import xgboost as xgb

from backend.calibration.feature_builder_v2 import FEATURE_NAMES, feature_matrix

BINARY_TARGETS = [
    "over_1_5", "over_2_5", "over_3_5", "btts_yes", "home_team_scores", "away_team_scores",
    "home_over_1_5", "away_over_1_5", "double_chance_1X", "double_chance_X2", "double_chance_12",
    "draw_no_bet_home_non_loss", "draw_no_bet_away_non_loss",
]


def dmatrix(rows: list[dict[str, Any]], target: str | None = None) -> xgb.DMatrix:
    labels = None if target is None else [row["labels"][target] for row in rows]
    return xgb.DMatrix(np.asarray(feature_matrix(rows), dtype=float), label=labels, feature_names=FEATURE_NAMES)


def base_params(params: dict[str, Any]) -> dict[str, Any]:
    return {
        "max_depth": int(params["max_depth"]),
        "eta": float(params["eta"]),
        "subsample": float(params["subsample"]),
        "colsample_bytree": float(params["colsample_bytree"]),
        "min_child_weight": float(params["min_child_weight"]),
        "lambda": float(params["lambda"]),
        "alpha": float(params["alpha"]),
        "seed": 2026,
        "nthread": 1,
        "verbosity": 0,
    }


def train_multiclass(train: list[dict[str, Any]], params: dict[str, Any]) -> xgb.Booster:
    config = base_params(params) | {"objective": "multi:softprob", "num_class": 3, "eval_metric": "mlogloss"}
    return xgb.train(config, dmatrix(train, "outcome_1x2"), num_boost_round=int(params["num_boost_round"]))


def predict_multiclass(model: xgb.Booster, rows: list[dict[str, Any]]) -> list[list[float]]:
    return model.predict(dmatrix(rows)).tolist()


def train_binary_models(train: list[dict[str, Any]], params: dict[str, Any]) -> dict[str, xgb.Booster]:
    config = base_params(params) | {"objective": "binary:logistic", "eval_metric": "logloss"}
    return {
        target: xgb.train(config, dmatrix(train, target), num_boost_round=int(params["num_boost_round"]))
        for target in BINARY_TARGETS
    }


def predict_binary_models(models: dict[str, xgb.Booster], rows: list[dict[str, Any]]) -> dict[str, list[float]]:
    matrix = dmatrix(rows)
    return {target: model.predict(matrix).tolist() for target, model in models.items()}


def feature_importance(models: dict[str, xgb.Booster]) -> dict[str, dict[str, float]]:
    return {name: model.get_score(importance_type="gain") for name, model in models.items()}
