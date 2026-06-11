"""Conditional active-engine deployment adapter for V2."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from backend.calibration.feature_builder_v2 import TeamHistory, build_feature_row
from backend.calibration.historical_replay_v2 import OUTCOME_NAMES
from backend.calibration.internal_rating_v2 import InternalRating
from backend.calibration.score_distribution_v2 import analytical_markets, score_distribution, top_scores
from backend.calibration.xg_engine_v2 import expected_goals
from backend.calibration.xgboost_market_models_v2 import predict_multiclass
from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, write_json


def active_predictions(
    fixtures: list[dict[str, Any]],
    model: Any,
    params: dict[str, Any],
    xg_params: dict[str, float],
    rating: InternalRating,
    history: TeamHistory,
    generated_at: str,
) -> list[dict[str, Any]]:
    rows = []
    for fixture in fixtures:
        synthetic = fixture | {"home_score": 0, "away_score": 0, "competition_tier": "major_tournament"}
        rows.append(build_feature_row(synthetic, "active_2026", rating, history))
    xgb_probabilities = predict_multiclass(model, rows)
    predictions = []
    for fixture, row, xgb_probs in zip(fixtures, rows, xgb_probabilities):
        home_lambda, away_lambda, lambda_meta = expected_goals(row["features"], xg_params)
        matrix = score_distribution(home_lambda, away_lambda)
        markets = analytical_markets(matrix)
        poisson = [markets["home_win"], markets["draw"], markets["away_win"]]
        blend = float(params["blend_weight_xgb"])
        hybrid = [blend * xgb_probs[index] + (1 - blend) * poisson[index] for index in range(3)]
        markets.update({"home_win": hybrid[0], "draw": hybrid[1], "away_win": hybrid[2]})
        strongest = max(hybrid)
        predictions.append(
            {
                "prediction_id": f"pred_{fixture['match_id']}_quant_hybrid_v2.0",
                "match_id": fixture["match_id"],
                "generated_at": generated_at,
                "model_version": "quant_hybrid_v2.0",
                "prediction_version": "v2.0",
                "engine_version": "quant_hybrid_v2.0",
                "engine_status": "active",
                "historically_calibrated": True,
                "data_source_type": fixture["source_type"],
                "is_real_data": True,
                "predicted_home_xg": home_lambda,
                "predicted_away_xg": away_lambda,
                "xgb_1x2": dict(zip(OUTCOME_NAMES, xgb_probs)),
                "poisson_1x2": dict(zip(OUTCOME_NAMES, poisson)),
                "markets": markets,
                "confidence": "high" if strongest >= 0.65 else "medium" if strongest >= 0.45 else "low",
                "top_scores": top_scores(matrix, 5),
                "score_matrix": {
                    "match_id": fixture["match_id"],
                    "max_goals": 7,
                    "probabilities": [
                        {
                            "score": score,
                            "home_goals": int(score.split("-")[0]),
                            "away_goals": int(score.split("-")[1]),
                            "probability": probability,
                        }
                        for score, probability in matrix.items()
                    ],
                },
                "prediction_metadata": {"features": row["features"], "lambda": lambda_meta, "pre_match_only": True},
            }
        )
    return predictions


def deploy_active_predictions(predictions: list[dict[str, Any]], project_root: Path) -> dict[str, Any]:
    archive = DATA_DIR / "archived" / "pre_v2_0_active_predictions"
    archive.mkdir(parents=True, exist_ok=True)
    active_names = ("predictions.json", "predictions_baseline.json", "predictions_elo.json", "model_comparison.json")
    for folder in (DATA_DIR / "generated", DATA_DIR / "snapshots", FRONTEND_DATA_DIR):
        for name in active_names:
            source = folder / name
            if source.exists():
                shutil.copy2(source, archive / f"{folder.name}_{name}")
    for target in (DATA_DIR / "generated" / "predictions.json", DATA_DIR / "snapshots" / "predictions.json", FRONTEND_DATA_DIR / "predictions.json"):
        write_json(predictions, target)
    return {"active_engine_replacement": True, "archive_path": str(archive.relative_to(project_root))}
