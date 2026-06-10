"""Evaluate generated predictions against mock finished results."""

from __future__ import annotations

import sys

from pipeline_utils import DATA_DIR, PROJECT_ROOT, load_json, utc_now, write_json

sys.path.insert(0, str(PROJECT_ROOT))

from backend.backtesting.backtester import backtest_predictions, market_won

MARKETS_TO_TEST = ("home_win", "home_or_draw", "over_1_5", "btts_yes")


def main() -> None:
    predictions = load_json(DATA_DIR / "generated" / "predictions.json")
    results = load_json(DATA_DIR / "mock" / "sample_results.json")
    results_by_id = {result["match_id"]: result for result in results if result["status"] == "finished"}
    evaluated_at = utc_now()
    signals = [
        {"match_id": prediction["match_id"], "market": market, "probability": prediction["markets"][market]}
        for prediction in predictions
        for market in MARKETS_TO_TEST
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
                    "prediction_id": prediction["prediction_id"],
                    "model_version": prediction["model_version"],
                    "generated_at": prediction["generated_at"],
                    "market_name": market_name,
                    "predicted_probability": prediction["markets"][market_name],
                    "actual_result": validated,
                    "validated": validated,
                    "real_result": {"home_score": result["home_score"], "away_score": result["away_score"]},
                    "evaluated_at": evaluated_at,
                    "source_type": prediction["data_source_type"],
                    "is_real_data": prediction["is_real_data"],
                }
            )

    output_path = DATA_DIR / "evaluated" / "backtest_results.json"
    write_json({"summary": summary, "results": details}, output_path)
    print(
        f"Backtested {summary['tested']} signals: {summary['won']} validated, "
        f"{summary['tested'] - summary['won']} not validated"
    )
    print(f"Saved complete history in {output_path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
