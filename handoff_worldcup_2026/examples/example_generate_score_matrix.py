"""Generate and display the five most likely scores for two fictional teams."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from recycled_code.score_prediction.expected_goals import compute_lambdas
from recycled_code.score_matrix.score_matrix import generate_score_matrix, top_exact_scores

home_lambda, away_lambda = compute_lambdas(1.65, 1.10, delta_elo=85, w_xg=0.95, w_elo=0.6, home_field_advantage=40)
matrix = generate_score_matrix(home_lambda, away_lambda, max_goals=8, rho=-0.05)
print(f"Équipe A xG ajusté: {home_lambda:.2f}; Équipe B: {away_lambda:.2f}")
for score in top_exact_scores(matrix):
    print(f"{score['score']}: {score['probability']:.2%}")
