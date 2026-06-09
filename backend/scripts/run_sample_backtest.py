"""Evaluate selected markets from the generated sample predictions."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "backend" / "data"
sys.path.insert(0, str(PROJECT_ROOT))

from backend.backtesting.backtester import backtest_predictions, market_won

MARKETS_TO_TEST = ("home_win", "home_or_draw", "over_1_5", "btts_yes")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    predictions = load_json(DATA_DIR / "predictions.json")
    results = load_json(DATA_DIR / "sample_results.json")
    results_by_id = {result["match_id"]: result for result in results if result["status"] == "finished"}
    evaluated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    signals = [
        {
            "match_id": prediction["match_id"],
            "market": market_name,
            "probability": prediction["markets"][market_name],
        }
        for prediction in predictions
        for market_name in MARKETS_TO_TEST
    ]
    summary = backtest_predictions(signals, results)

    details = []
    for prediction in predictions:
        result = results_by_id.get(prediction["match_id"])
        if result is None:
            continue
        for market_name in MARKETS_TO_TEST:
            validated = market_won(market_name, int(result["home_score"]), int(result["away_score"]))
            details.append(
                {
                    "match_id": prediction["match_id"],
                    "prediction_version": prediction["prediction_version"],
                    "generated_at": prediction["generated_at"],
                    "market_name": market_name,
                    "predicted_probability": prediction["markets"][market_name],
                    "actual_result": validated,
                    "validated": validated,
                    "real_result": {
                        "home_score": result["home_score"],
                        "away_score": result["away_score"],
                    },
                    "evaluated_at": evaluated_at,
                }
            )

    output = {"summary": summary, "results": details}
    output_path = DATA_DIR / "backtest_results.json"
    output_path.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Backtested {summary['tested']} signals: {summary['won']} validated, {summary['tested'] - summary['won']} not validated")
    for market, market_summary in summary["by_market"].items():
        print(f"- {market}: {market_summary['won']}/{market_summary['tested']} ({market_summary['hit_rate']:.1%})")
    print(f"Saved complete history in {output_path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
