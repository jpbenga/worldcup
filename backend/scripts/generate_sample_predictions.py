"""Generate sample prediction snapshots from canonical match JSON."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "backend" / "data"
sys.path.insert(0, str(PROJECT_ROOT))

from backend.markets.market_derivation import derive_markets
from backend.prediction.expected_goals import compute_lambdas
from backend.score_matrix.score_matrix import generate_score_matrix, top_exact_scores

MAX_GOALS = 5
RHO = -0.05
PREDICTION_VERSION = "sample-v1"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


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
    home_xg = 0.6 * float(match["home_recent_goals_for"]) + 0.4 * float(match["away_recent_goals_against"])
    away_xg = 0.6 * float(match["away_recent_goals_for"]) + 0.4 * float(match["home_recent_goals_against"])
    home_lambda, away_lambda = compute_lambdas(
        home_xg,
        away_xg,
        delta_elo=float(match["home_elo"]) - float(match["away_elo"]),
        home_field_advantage=0,
        w_elo=0.6,
    )
    matrix = generate_score_matrix(home_lambda, away_lambda, max_goals=MAX_GOALS, rho=RHO)
    derived = derive_markets(matrix)
    markets = {key: value for key, value in derived.items() if key != "top_exact_scores"}
    probabilities = [score_probability(score, probability) for score, probability in matrix.items()]
    top_scores = [
        score_probability(str(item["score"]), float(item["probability"]))
        for item in top_exact_scores(matrix, limit=5)
    ]

    return {
        "match_id": match["match_id"],
        "generated_at": generated_at,
        "prediction_version": PREDICTION_VERSION,
        "score_matrix": {
            "match_id": match["match_id"],
            "max_goals": MAX_GOALS,
            "probabilities": probabilities,
        },
        "markets": markets,
        "confidence": confidence_from_markets(markets),
        "top_scores": top_scores,
    }


def main() -> None:
    matches = load_json(DATA_DIR / "sample_matches.json")
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    predictions = [generate_prediction(match, generated_at) for match in matches]
    output_path = DATA_DIR / "predictions.json"
    output_path.write_text(json.dumps(predictions, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Generated {len(predictions)} predictions in {output_path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
