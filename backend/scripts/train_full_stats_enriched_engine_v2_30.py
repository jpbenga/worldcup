"""Train and evaluate the V2.30 full stats-enriched production candidate."""

from __future__ import annotations

import copy
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.full_stats_engine_v2_30_utils import (
    DATA_DIR,
    FRONTEND_DATA_DIR,
    adjusted_matrix,
    adjusted_probs,
    feature_edge,
    load_feature_index,
    markets_from_matrix,
    metric_delta,
    publish,
    rows_for,
    score_rows,
    top_scores_from_matrix,
)
from backend.scripts.pipeline_utils import load_json, write_json

OUTPUT = "full_stats_enriched_engine_v2_30_results.json"
CANDIDATE_OUTPUT = "predictions_full_stats_candidate_v2_30.json"


def segment_metrics(rows: list[dict[str, Any]], features: dict[str, dict[str, Any]], alpha: float, coverage_aware: bool) -> dict[str, Any]:
    selectors: dict[str, Callable[[dict[str, Any]], bool]] = {
        "with_xg_lag": lambda r: features[r["match_id"]]["coverage"]["home_xg_matches_last5"] > 0 and features[r["match_id"]]["coverage"]["away_xg_matches_last5"] > 0,
        "without_xg_lag": lambda r: not (features[r["match_id"]]["coverage"]["home_xg_matches_last5"] > 0 and features[r["match_id"]]["coverage"]["away_xg_matches_last5"] > 0),
        "with_rich_stats": lambda r: features[r["match_id"]]["coverage"]["home_stats_matches_last5"] >= 2 and features[r["match_id"]]["coverage"]["away_stats_matches_last5"] >= 2,
        "without_rich_stats": lambda r: features[r["match_id"]]["coverage"]["home_stats_matches_last5"] < 2 or features[r["match_id"]]["coverage"]["away_stats_matches_last5"] < 2,
        "recent_competitions": lambda r: int(r["season"]) >= 2024,
        "older_competitions": lambda r: int(r["season"]) < 2024,
        "strong_favorites": lambda r: max(r["markets"]["home_win"], r["markets"]["away_win"]) >= 0.60,
        "balanced_matches": lambda r: max(r["markets"]["home_win"], r["markets"]["away_win"]) < 0.45,
        "large_actual_wins": lambda r: abs(r["actual_home_score"] - r["actual_away_score"]) >= 3,
    }
    return {name: score_rows([row for row in rows if selector(row)], features, alpha, coverage_aware) for name, selector in selectors.items()}


def trial_payload(model_key: str, alpha: float, coverage_aware: bool, validation: list[dict[str, Any]], baseline: dict[str, Any], features: dict[str, dict[str, Any]]) -> dict[str, Any]:
    metrics = score_rows(validation, features, alpha, coverage_aware)
    return {
        "model_key": model_key,
        "params": {"alpha": alpha, "coverage_aware": coverage_aware},
        "validation_metrics": metrics,
        "delta_vs_quant_hybrid_v2_2": metric_delta(metrics, baseline),
    }


def choose_candidate(trials: list[dict[str, Any]], baseline: dict[str, Any]) -> dict[str, Any]:
    non_zero = [trial for trial in trials if float(trial["params"]["alpha"]) > 0]
    safe = [
        trial for trial in non_zero
        if trial["validation_metrics"]["log_loss_1x2"] <= baseline["log_loss_1x2"] * 1.03
        and trial["validation_metrics"]["brier_score_1x2"] <= baseline["brier_score_1x2"] * 1.03
        and trial["validation_metrics"]["accuracy_1x2"] >= baseline["accuracy_1x2"] - 0.03
    ]
    # Product rule: select a non-zero stats model when it clears safety gates, then prefer validation log loss.
    return min(safe or non_zero or trials, key=lambda trial: (trial["validation_metrics"]["log_loss_1x2"], -float(trial["params"]["alpha"])))


def enrich_prediction(prediction: dict[str, Any], feature: dict[str, Any], alpha: float, coverage_aware: bool) -> dict[str, Any]:
    out = copy.deepcopy(prediction)
    p = adjusted_probs(prediction, feature, alpha, coverage_aware)
    matrix = adjusted_matrix(prediction, feature, alpha)
    matrix_markets = markets_from_matrix(matrix)
    original_markets = out.get("markets", {})
    markets = dict(original_markets)
    markets.update(matrix_markets)
    markets["home_win"] = p["home"]
    markets["draw"] = p["draw"]
    markets["away_win"] = p["away"]
    markets["double_chance_1X"] = p["home"] + p["draw"]
    markets["double_chance_X2"] = p["draw"] + p["away"]
    markets["double_chance_12"] = p["home"] + p["away"]
    markets["draw_no_bet_home"] = p["home"] / max(1e-9, p["home"] + p["away"])
    markets["draw_no_bet_away"] = p["away"] / max(1e-9, p["home"] + p["away"])
    out.update({
        "prediction_id": f"{prediction.get('prediction_id', prediction['match_id'])}_full_stats_v2_30",
        "model_version": "stats_enriched_full_v2.30",
        "engine_version": "stats_enriched_full_v2.30_candidate",
        "engine_status": "production_candidate_not_active",
        "active_engine_replaced": False,
        "baseline_engine_version": prediction.get("engine_version"),
        "full_stats_overlay": {
            "alpha": alpha,
            "coverage_aware": coverage_aware,
            "edge": feature_edge(feature),
            "coverage": feature["coverage"],
            "source": "full_stats_lagged_features_v2_30",
        },
        "markets": markets,
        "score_matrix": {
            "match_id": prediction["match_id"],
            "max_goals": 7,
            "probabilities": matrix,
            "source": "stats_enriched_full_v2_30_adjusted_matrix",
        },
        "top_scores": top_scores_from_matrix(matrix, 5),
        "confidence": "high" if max(p.values()) >= 0.60 else "medium" if max(p.values()) >= 0.45 else "low",
    })
    return out


def publish_candidate_predictions(features: dict[str, dict[str, Any]], alpha: float, coverage_aware: bool) -> list[dict[str, Any]]:
    predictions = load_json(DATA_DIR / "generated" / "predictions.json")
    candidate = [enrich_prediction(prediction, features[prediction["match_id"]], alpha, coverage_aware) for prediction in predictions]
    target = DATA_DIR / "generated" / CANDIDATE_OUTPUT
    write_json(candidate, target)
    for directory in (DATA_DIR / "snapshots", FRONTEND_DATA_DIR):
        write_json(candidate, directory / CANDIDATE_OUTPUT)
    return candidate


def main() -> None:
    features = load_feature_index()
    feature_data = load_json(DATA_DIR / "generated" / "full_stats_lagged_features_v2_30.json")
    validation, test = rows_for("validation"), rows_for("test")
    baseline_val = score_rows(validation, features, 0.0, True)
    baseline_test = score_rows(test, features, 0.0, True)
    grids = {
        "stats_enriched_full_v2_30": {"alphas": [0.02, 0.05, 0.10, 0.20, 0.35, 0.50], "coverage_aware": False},
        "ensemble_quant_plus_stats_v2_30": {"alphas": [0.02, 0.05, 0.10, 0.20, 0.35], "coverage_aware": True},
        "coverage_aware_full_stats_v2_30": {"alphas": [0.02, 0.05, 0.10, 0.20, 0.35, 0.50], "coverage_aware": True},
    }
    trials = []
    for model_key, config in grids.items():
        for alpha in config["alphas"]:
            trials.append(trial_payload(model_key, alpha, bool(config["coverage_aware"]), validation, baseline_val, features))
    selected = choose_candidate(trials, baseline_val)
    alpha = float(selected["params"]["alpha"])
    coverage_aware = bool(selected["params"]["coverage_aware"])
    candidate_val = score_rows(validation, features, alpha, coverage_aware)
    candidate_test = score_rows(test, features, alpha, coverage_aware)
    model_comparison = {
        "A_quant_hybrid_v2_2_active": {"validation": baseline_val, "test": baseline_test},
        "B_stats_enriched_full_v2_30": {
            "best_trial": min([t for t in trials if t["model_key"] == "stats_enriched_full_v2_30"], key=lambda t: t["validation_metrics"]["log_loss_1x2"]),
        },
        "C_ensemble_quant_plus_stats": {
            "best_trial": min([t for t in trials if t["model_key"] == "ensemble_quant_plus_stats_v2_30"], key=lambda t: t["validation_metrics"]["log_loss_1x2"]),
        },
        "D_coverage_aware_full_stats": {
            "best_trial": min([t for t in trials if t["model_key"] == "coverage_aware_full_stats_v2_30"], key=lambda t: t["validation_metrics"]["log_loss_1x2"]),
        },
    }
    candidate_predictions = publish_candidate_predictions(features, alpha, coverage_aware)
    comparison = {
        "selected_model_key": selected["model_key"],
        "selected_params": selected["params"],
        "delta_validation": metric_delta(candidate_val, baseline_val),
        "delta_test": metric_delta(candidate_test, baseline_test),
        "test_log_loss_degradation_pct": round((candidate_test["log_loss_1x2"] / baseline_test["log_loss_1x2"] - 1) * 100, 6),
        "test_brier_degradation_pct": round((candidate_test["brier_score_1x2"] / baseline_test["brier_score_1x2"] - 1) * 100, 6),
        "test_accuracy_delta_points": round((candidate_test["accuracy_1x2"] - baseline_test["accuracy_1x2"]) * 100, 6),
    }
    payload = {
        "version": "v2.30",
        "candidate_name": "stats_enriched_full_v2.30",
        "training_method": "bounded logit and score-matrix overlay using complete lagged API-Football stats cache; no Optuna rerun",
        "feature_collection": feature_data["source_collection"],
        "feature_coverage": feature_data["coverage_summary"],
        "feature_policy": feature_data["feature_policy"],
        "models_compared": model_comparison,
        "selection_policy": {
            "user_rule": "Prefer the richer-data engine unless a serious technical blocker is present.",
            "validation_safety_gates": {
                "log_loss_degradation_max_pct": 3,
                "brier_degradation_max_pct": 3,
                "accuracy_drop_max_points": 3,
            },
            "selected_non_zero_stats_model": True,
        },
        "splits": {"validation": len(validation), "test": len(test), "trials": len(trials)},
        "metrics": {
            "validation": {"quant_hybrid_v2_2": baseline_val, "full_stats_candidate": candidate_val},
            "test": {"quant_hybrid_v2_2": baseline_test, "full_stats_candidate": candidate_test},
            "segments": {
                "validation": segment_metrics(validation, features, alpha, coverage_aware),
                "test": segment_metrics(test, features, alpha, coverage_aware),
            },
            "trials": trials,
        },
        "comparison_to_quant_hybrid_v2_2": comparison,
        "candidate_predictions": {
            "generated": True,
            "matches": len(candidate_predictions),
            "path": f"backend/data/generated/{CANDIDATE_OUTPUT}",
            "active_predictions_overwritten": False,
        },
        "warnings": ["No Optuna was run; V2.30 uses bounded validation-selected overlays to isolate the value of the full stats cache."],
    }
    publish(payload, OUTPUT, frontend=False)
    print(
        "V2.30 full stats candidate: "
        f"model={selected['model_key']} alpha={alpha} coverage_aware={coverage_aware}"
    )


if __name__ == "__main__":
    main()
