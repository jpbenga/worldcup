"""Generate a score matrix and aggregate common football markets."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from recycled_code.markets.market_derivation import derive_markets
from recycled_code.score_matrix.score_matrix import generate_score_matrix

markets = derive_markets(generate_score_matrix(1.70, 1.15, rho=-0.05))
for name in ("home_win", "draw", "away_win", "home_or_draw", "over_2_5", "under_2_5", "btts_yes", "btts_no"):
    print(f"{name}: {markets[name]:.2%}")
print("Top scores:", markets["top_exact_scores"])
