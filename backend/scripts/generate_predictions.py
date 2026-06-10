"""Generate baseline and experimental Elo-adjusted predictions."""

from __future__ import annotations

import argparse
import sys
from typing import Any

from pipeline_utils import DATA_DIR, MODEL_VERSION, PROJECT_ROOT, load_json, utc_now, write_json

sys.path.insert(0, str(PROJECT_ROOT))

from backend.markets.market_derivation import derive_markets
from backend.prediction.elo_adjusted_model import MODEL_FAMILY, MODEL_VERSION as ELO_MODEL_VERSION, adjust_expected_goals
from backend.prediction.elo_features import get_match_elo_features
from backend.prediction.expected_goals import compute_lambdas
from backend.score_matrix.score_matrix import generate_score_matrix, top_exact_scores

MAX_GOALS = 5
RHO = -0.05
ENGINE = {
    "name": "Prototype Prediction Engine",
    "version": "0.5.0",
    "status": "experimental",
    "historically_calibrated": False,
    "description": (
        "Simple prototype engine used to generate score matrices and derived markets. "
        "It is not yet trained or calibrated on historical competitions."
    ),
}


def score_probability(score: str, probability: float) -> dict[str, object]:
    home_goals, away_goals = (int(value) for value in score.split("-", maxsplit=1))
    return {"score": score, "home_goals": home_goals, "away_goals": away_goals, "probability": probability}


def confidence_from_markets(markets: dict[str, object]) -> str:
    strongest_outcome = max(float(markets[name]) for name in ("home_win", "draw", "away_win"))
    if strongest_outcome >= 0.65:
        return "high"
    if strongest_outcome >= 0.45:
        return "medium"
    return "low"


def baseline_expected_goals(match: dict[str, object]) -> tuple[float, float]:
    inputs = match["model_inputs"]
    if not isinstance(inputs, dict):
        raise ValueError(f"Missing model_inputs for {match['match_id']}")
    home_xg = 0.6 * float(inputs["home_recent_goals_for"]) + 0.4 * float(inputs["away_recent_goals_against"])
    away_xg = 0.6 * float(inputs["away_recent_goals_for"]) + 0.4 * float(inputs["home_recent_goals_against"])
    return compute_lambdas(
        home_xg,
        away_xg,
        delta_elo=float(inputs["home_elo"]) - float(inputs["away_elo"]),
        home_field_advantage=0,
        w_elo=0.6,
    )


def prediction_from_expected_goals(
    match: dict[str, object],
    generated_at: str,
    home_xg: float,
    away_xg: float,
    model_version: str,
    model_family: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, object]:
    matrix = generate_score_matrix(home_xg, away_xg, max_goals=MAX_GOALS, rho=RHO)
    derived = derive_markets(matrix)
    markets = {key: value for key, value in derived.items() if key != "top_exact_scores"}
    prediction_id = (
        f"pred_{match['match_id']}_{model_version}" if model_family else f"pred_{match['match_id']}_v{model_version}"
    )
    prediction = {
        "prediction_id": prediction_id,
        "match_id": match["match_id"],
        "generated_at": generated_at,
        "model_version": model_version,
        "prediction_version": f"v{model_version}",
        "data_source_type": match["source_type"],
        "is_real_data": bool(match["is_real_fixture"]),
        "engine": ENGINE,
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
    if model_family:
        prediction["model_family"] = model_family
        prediction["engine_status"] = "experimental"
        prediction["historically_calibrated"] = False
    if extra:
        prediction.update(extra)
    return prediction


def generate_baseline_prediction(match: dict[str, object], generated_at: str) -> dict[str, object]:
    home_xg, away_xg = baseline_expected_goals(match)
    return prediction_from_expected_goals(match, generated_at, home_xg, away_xg, MODEL_VERSION)


def generate_elo_prediction(match: dict[str, object], generated_at: str) -> dict[str, object]:
    baseline_home_xg, baseline_away_xg = baseline_expected_goals(match)
    elo_features = get_match_elo_features(str(match["home_team"]), str(match["away_team"]))
    model_inputs = adjust_expected_goals(
        baseline_home_xg,
        baseline_away_xg,
        elo_features["home_elo"] if isinstance(elo_features["home_elo"], int) else None,
        elo_features["away_elo"] if isinstance(elo_features["away_elo"], int) else None,
    )
    return prediction_from_expected_goals(
        match,
        generated_at,
        float(model_inputs["adjusted_home_xg"]),
        float(model_inputs["adjusted_away_xg"]),
        ELO_MODEL_VERSION,
        MODEL_FAMILY,
        {"elo_features": elo_features, "model_inputs": model_inputs},
    )


def generate_models(model: str) -> None:
    matches = load_json(DATA_DIR / "normalized" / "matches.json")
    generated_at = utc_now()
    if model in {"baseline", "both"}:
        baseline = [generate_baseline_prediction(match, generated_at) for match in matches]
        write_json(baseline, DATA_DIR / "generated" / "predictions.json")
        write_json(baseline, DATA_DIR / "generated" / "predictions_baseline.json")
        print(f"Generated {len(baseline)} baseline predictions.")
    if model in {"elo", "both"}:
        elo = [generate_elo_prediction(match, generated_at) for match in matches]
        write_json(elo, DATA_DIR / "generated" / "predictions_elo.json")
        print(f"Generated {len(elo)} experimental Elo predictions.")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=("baseline", "elo", "both"), default="baseline")
    args = parser.parse_args(argv)
    generate_models(args.model)


if __name__ == "__main__":
    main()
