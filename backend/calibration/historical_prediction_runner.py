"""Generate historical predictions from fitted expected-goals models."""

from __future__ import annotations

from typing import Any, Callable

from backend.calibration.calibration_metrics import actual_outcome
from backend.markets.market_derivation import derive_markets
from backend.score_matrix.score_matrix import generate_score_matrix

MAX_GOALS = 8
RHO = -0.05


def score_probability(score: str, probability: float) -> dict[str, Any]:
    home_goals, away_goals = (int(value) for value in score.split("-", maxsplit=1))
    return {"score": score, "home_goals": home_goals, "away_goals": away_goals, "probability": probability}


def predict_matches(
    matches: list[dict[str, Any]],
    expected_goals: Callable[[str, str], tuple[float, float, dict[str, Any]]],
    model_version: str,
    model_family: str,
    historically_calibrated: bool,
) -> list[dict[str, Any]]:
    predictions = []
    for match in matches:
        home_xg, away_xg, metadata = expected_goals(str(match["home_team"]), str(match["away_team"]))
        matrix = generate_score_matrix(home_xg, away_xg, max_goals=MAX_GOALS, rho=RHO)
        derived = derive_markets(matrix)
        markets = {key: value for key, value in derived.items() if key != "top_exact_scores"}
        top_scores = [score_probability(str(item["score"]), float(item["probability"])) for item in derived["top_exact_scores"]]
        predicted_1x2 = max(
            (("home", markets["home_win"]), ("draw", markets["draw"]), ("away", markets["away_win"])),
            key=lambda item: item[1],
        )[0]
        actual_1x2 = actual_outcome(int(match["home_score"]), int(match["away_score"]))
        predictions.append(
            {
                "match_id": match["match_id"],
                "model_version": model_version,
                "model_family": model_family,
                "historically_calibrated": historically_calibrated,
                "status": "experimental",
                "competition": match["competition"],
                "kickoff_at": match["kickoff_at"],
                "home_team": match["home_team"],
                "away_team": match["away_team"],
                "actual_home_score": match["home_score"],
                "actual_away_score": match["away_score"],
                "predicted_home_xg": home_xg,
                "predicted_away_xg": away_xg,
                "score_matrix": [score_probability(score, probability) for score, probability in matrix.items()],
                "markets": markets,
                "top_scores": top_scores,
                "predicted_1x2": predicted_1x2,
                "actual_1x2": actual_1x2,
                "is_correct_1x2": predicted_1x2 == actual_1x2,
                "prediction_metadata": metadata,
            }
        )
    return predictions
