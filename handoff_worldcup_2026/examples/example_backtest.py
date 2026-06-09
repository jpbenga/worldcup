"""Validate fictional pre-match signals against finished results."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from recycled_code.backtesting.backtester import backtest_predictions

predictions = [
    {"match_id": "match_001", "market": "home_or_draw", "probability": 0.78},
    {"match_id": "match_002", "market": "btts_yes", "probability": 0.62},
]
results = [
    {"match_id": "match_001", "home_score": 2, "away_score": 1, "status": "finished"},
    {"match_id": "match_002", "home_score": 1, "away_score": 0, "status": "finished"},
]
print(backtest_predictions(predictions, results))
