"""Validation-only conservative Optuna search for the V2.2 limited retrain."""

from __future__ import annotations

import math

import optuna
from optuna.samplers import TPESampler

from backend.calibration.feature_builder_v2_2 import build_chronological_features
from backend.calibration.internal_rating_v2_2 import RatingConfig
from backend.calibration.score_distribution_v2_2 import analytical_markets, score_distribution, top_scores
from backend.calibration.xg_engine_v2_2 import expected_goals
from backend.calibration.xgboost_market_models_v2_2 import predict_multiclass, train_multiclass


def rating_config(p):
    return RatingConfig(
        initial_rating=float(p["initial_rating"]), scale=float(p["rating_scale"]),
        k_factor=float(p["rating_k_factor"]), goal_margin_multiplier=True,
        competition_weighting=bool(p["competition_weighting"]), context_advantage=float(p["context_advantage"]),
    )


def xgb_params(p):
    return {k: p[k] for k in ("max_depth", "eta", "subsample", "colsample_bytree", "min_child_weight", "lambda", "alpha", "num_boost_round")}


def xg_params(p):
    return {
        "base_home_goals": float(p["base_goals"]) + 0.10,
        "base_away_goals": float(p["base_goals"]) - 0.10,
        "beta_rating": float(p["beta_rating"]), "rating_factor_cap": float(p["rating_factor_cap"]),
        "recent_weight": float(p["recent_weight"]), "strength_weight": float(p["strength_weight"]),
        "smoothing": float(p["smoothing"]), "low_sample_threshold": float(p["low_sample_threshold"]),
        "extra_low_sample_smoothing": float(p["extra_low_sample_smoothing"]),
        "lambda_min": 0.2, "lambda_max": 4.0,
    }


def suggest(t):
    recent = t.suggest_categorical("recent_weight", [0.15, 0.25, 0.35])
    strength = t.suggest_categorical("strength_weight", [0.4, 0.5, 0.6])
    return {
        "initial_rating": t.suggest_categorical("initial_rating", [1400, 1500]),
        "rating_scale": t.suggest_categorical("rating_scale", [350, 400, 450]),
        "rating_k_factor": t.suggest_categorical("rating_k_factor", [15, 20, 25, 30]),
        "goal_margin_multiplier": True,
        "competition_weighting": t.suggest_categorical("competition_weighting", [False, True]),
        "context_advantage": t.suggest_categorical("context_advantage", [0, 25, 35]),
        "base_goals": t.suggest_categorical("base_goals", [1.15, 1.25, 1.35]),
        "smoothing": t.suggest_categorical("smoothing", [6, 10, 14, 18]),
        "beta_rating": t.suggest_categorical("beta_rating", [0.10, 0.18, 0.25, 0.35, 0.45]),
        "rating_factor_cap": t.suggest_categorical("rating_factor_cap", [0.20, 0.30, 0.40, 0.50]),
        "low_sample_threshold": t.suggest_categorical("low_sample_threshold", [5, 8, 10]),
        "extra_low_sample_smoothing": t.suggest_categorical("extra_low_sample_smoothing", [0, 8, 12]),
        "recent_weight": recent, "strength_weight": min(strength, 0.9 - recent),
        "blend_weight_xgb": t.suggest_categorical("blend_weight_xgb", [0.35, 0.45, 0.55, 0.65]),
        "max_depth": t.suggest_categorical("max_depth", [2, 3]),
        "eta": t.suggest_categorical("eta", [0.01, 0.03, 0.05]),
        "subsample": t.suggest_categorical("subsample", [0.7, 0.85, 1.0]),
        "colsample_bytree": t.suggest_categorical("colsample_bytree", [0.7, 0.85, 1.0]),
        "min_child_weight": t.suggest_categorical("min_child_weight", [3, 5, 8, 12]),
        "lambda": t.suggest_categorical("lambda", [1.0, 2.0, 5.0, 8.0]),
        "alpha": t.suggest_categorical("alpha", [0.25, 0.5, 1.0, 2.0]),
        "num_boost_round": t.suggest_categorical("num_boost_round", [50, 100, 200, 300]),
    }


def components(rows, probs, p):
    ll = brier = secondary = 0.0
    modal = clear = aligned = wrong = 0
    diffs = []
    blend = float(p["blend_weight_xgb"])
    for row, xp in zip(rows, probs):
        hl, al, _ = expected_goals(row["features"], xg_params(p))
        diffs.append(abs(hl - al))
        matrix = score_distribution(hl, al)
        market = analytical_markets(matrix)
        pp = [market["home_win"], market["draw"], market["away_win"]]
        ps = [blend * xp[i] + (1 - blend) * pp[i] for i in range(3)]
        actual = int(row["labels"]["outcome_1x2"])
        ll -= math.log(max(1e-15, ps[actual]))
        brier += sum((v - float(i == actual)) ** 2 for i, v in enumerate(ps))
        pred = max(range(3), key=lambda i: ps[i])
        wrong += int(ps[pred] >= .60 and pred != actual)
        score = top_scores(matrix, 1)[0]["score"]
        modal += int(score == "1-1")
        ordered = sorted(ps, reverse=True)
        if ordered[0] - ordered[1] >= .08:
            clear += 1
            h, a = map(int, score.split("-"))
            aligned += int((pred == 0 and h > a) or (pred == 2 and a > h) or (pred == 1 and h == a))
        secondary += (market["over_2_5"] - row["labels"]["over_2_5"]) ** 2
    n = len(rows)
    return {"log_loss_1x2": ll/n, "brier_score_1x2": brier/n, "modal_1_1_rate": modal/n,
            "clear_favorite_score_alignment_rate": aligned/clear if clear else 0.0,
            "high_confidence_wrong_rate": wrong/n, "secondary_over_2_5_brier": secondary/n,
            "average_abs_lambda_diff": sum(diffs)/n}


def optimize(splits, n_trials=500):
    def objective(t):
        p = suggest(t)
        rows, *_ = build_chronological_features(splits, rating_config(p))
        model = train_multiclass(rows["train"], xgb_params(p), rows["validation"])
        train = components(rows["train"], predict_multiclass(model, rows["train"]), p)
        val = components(rows["validation"], predict_multiclass(model, rows["validation"]), p)
        gap = max(0.0, val["log_loss_1x2"] - train["log_loss_1x2"] - .12)
        value = (val["log_loss_1x2"] + .75*val["brier_score_1x2"] +
                 max(0., val["modal_1_1_rate"]-.38)*.25 +
                 max(0., .55-val["clear_favorite_score_alignment_rate"])*.25 +
                 val["high_confidence_wrong_rate"]*.10 + val["secondary_over_2_5_brier"]*.10 +
                 gap*.75 + max(0., .25-val["average_abs_lambda_diff"])*.20)
        t.set_user_attr("effective_params", p)
        t.set_user_attr("validation_components", val)
        t.set_user_attr("train_validation_log_loss_gap", val["log_loss_1x2"]-train["log_loss_1x2"])
        return value
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    study = optuna.create_study(direction="minimize", sampler=TPESampler(seed=2026))
    study.optimize(objective, n_trials=n_trials, catch=(Exception,))
    best = study.best_trial
    top = sorted((x for x in study.trials if x.value is not None), key=lambda x: x.value)[:20]
    return best.user_attrs["effective_params"], {
        "version": "v2.2", "mode": "quick" if n_trials == 150 else "full" if n_trials == 1500 else "standard",
        "n_trials": len(study.trials), "completed_trials": len([x for x in study.trials if x.value is not None]),
        "best_trial": best.number, "best_value": best.value, "best_params": best.user_attrs["effective_params"],
        "objective_components": best.user_attrs["validation_components"],
        "train_validation_log_loss_gap": best.user_attrs["train_validation_log_loss_gap"],
        "test_used_for_selection": False,
        "top_20_trials": [{"number": x.number, "value": x.value, "params": x.params} for x in top],
    }
