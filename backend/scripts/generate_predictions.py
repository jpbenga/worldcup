"""Generate provenance-aware predictions from normalized match data."""

from __future__ import annotations

import sys

from pipeline_utils import DATA_DIR, MODEL_VERSION, PROJECT_ROOT, load_json, utc_now, write_json

sys.path.insert(0, str(PROJECT_ROOT))

from backend.markets.market_derivation import derive_markets
from backend.prediction.expected_goals import compute_lambdas
from backend.score_matrix.score_matrix import generate_score_matrix, top_exact_scores

MAX_GOALS = 5
RHO = -0.05


def score_probability(score: str, probability: float) -> dict[str, object]:
    home_goals, away_goals = (int(value) for value in score.split("-", maxsplit=1))
    return {
        "score": score,
        "home_goals": home_goals,
        "away_goals": away_goals,
        "probability": probability,
    }


def confidence_from_markets(markets: dict[str, object]) -> str:
    strongest_outcome = max(float(markets[name]) for name in ("home_win", "draw", "away_win"))
    if strongest_outcome >= 0.65:
        return "high"
    if strongest_outcome >= 0.45:
        return "medium"
    return "low"


def generate_prediction(match: dict[str, object], generated_at: str) -> dict[str, object]:
    inputs = match["model_inputs"]
    if not isinstance(inputs, dict):
        raise ValueError(f"Missing model_inputs for {match['match_id']}")

    home_xg = 0.6 * float(inputs["home_recent_goals_for"]) + 0.4 * float(inputs["away_recent_goals_against"])
    away_xg = 0.6 * float(inputs["away_recent_goals_for"]) + 0.4 * float(inputs["home_recent_goals_against"])
    home_lambda, away_lambda = compute_lambdas(
        home_xg,
        away_xg,
        delta_elo=float(inputs["home_elo"]) - float(inputs["away_elo"]),
        home_field_advantage=0,
        w_elo=0.6,
    )
    matrix = generate_score_matrix(home_lambda, away_lambda, max_goals=MAX_GOALS, rho=RHO)
    derived = derive_markets(matrix)
    markets = {key: value for key, value in derived.items() if key != "top_exact_scores"}

    return {
        "prediction_id": f"pred_{match['match_id']}_v{MODEL_VERSION}",
        "match_id": match["match_id"],
        "generated_at": generated_at,
        "model_version": MODEL_VERSION,
        "prediction_version": f"v{MODEL_VERSION}",
        "data_source_type": match["source_type"],
        "is_real_data": bool(match["is_real_fixture"]),
        "score_matrix": {
            "match_id": match["match_id"],
            "max_goals": MAX_GOALS,
            "probabilities": [score_probability(score, probability) for score, probability in matrix.items()],
        },
        "markets": markets,
        "confidence": confidence_from_markets(markets),
        "top_scores": [
            score_probability(str(item["score"]), float(item["probability"]))
            for item in top_exact_scores(matrix, limit=5)
        ],
    }


def main() -> None:
    input_path = DATA_DIR / "normalized" / "matches.json"
    output_path = DATA_DIR / "generated" / "predictions.json"
    matches = load_json(input_path)
    generated_at = utc_now()
    predictions = [generate_prediction(match, generated_at) for match in matches]
    write_json(predictions, output_path)
    print(f"Generated {len(predictions)} predictions in {output_path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
