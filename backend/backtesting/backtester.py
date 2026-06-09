"""Small chronological-friendly market backtester adapted from prototype backtest scripts."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Mapping


def market_won(market: str, home_score: int, away_score: int) -> bool:
    total = home_score + away_score
    outcomes = {
        "home_win": home_score > away_score,
        "draw": home_score == away_score,
        "away_win": away_score > home_score,
        "home_or_draw": home_score >= away_score,
        "away_or_draw": away_score >= home_score,
        "no_draw": home_score != away_score,
        "btts_yes": home_score > 0 and away_score > 0,
        "btts_no": home_score == 0 or away_score == 0,
    }
    if market in outcomes:
        return outcomes[market]
    if market.startswith(("over_", "under_")):
        direction, raw_line = market.split("_", maxsplit=1)
        line = float(raw_line.replace("_", "."))
        return total > line if direction == "over" else total < line
    if market.startswith("exact_"):
        return market.removeprefix("exact_").replace("_", "-") == f"{home_score}-{away_score}"
    raise ValueError(f"Unsupported market: {market}")


def backtest_predictions(
    predictions: Iterable[Mapping[str, object]], results: Iterable[Mapping[str, object]]
) -> dict[str, object]:
    """Match predictions to finished results and report validation by selected market."""
    results_by_id = {
        str(result["match_id"]): result
        for result in results
        if result.get("status", "finished") == "finished"
    }
    details: list[dict[str, object]] = []
    by_market: defaultdict[str, dict[str, int]] = defaultdict(lambda: {"tested": 0, "won": 0})
    for prediction in predictions:
        match_id = str(prediction["match_id"])
        result = results_by_id.get(match_id)
        if result is None:
            continue
        market = str(prediction["market"])
        won = market_won(market, int(result["home_score"]), int(result["away_score"]))
        by_market[market]["tested"] += 1
        by_market[market]["won"] += int(won)
        details.append({"match_id": match_id, "market": market, "won": won})
    tested = len(details)
    won = sum(int(detail["won"]) for detail in details)
    market_summary = {
        market: {**counts, "hit_rate": counts["won"] / counts["tested"]}
        for market, counts in by_market.items()
    }
    return {"tested": tested, "won": won, "hit_rate": won / tested if tested else 0.0, "by_market": market_summary, "details": details}
