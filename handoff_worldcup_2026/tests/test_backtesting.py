from recycled_code.backtesting.backtester import backtest_predictions, market_won

def test_backtester_validates_simple_market():
    assert market_won("home_or_draw", 1, 1)
    report = backtest_predictions(
        [{"match_id": "one", "market": "home_win"}, {"match_id": "two", "market": "btts_yes"}],
        [{"match_id": "one", "home_score": 2, "away_score": 0, "status": "finished"}, {"match_id": "two", "home_score": 1, "away_score": 0, "status": "finished"}],
    )
    assert report["tested"] == 2
    assert report["won"] == 1
    assert report["by_market"]["home_win"]["hit_rate"] == 1.0
