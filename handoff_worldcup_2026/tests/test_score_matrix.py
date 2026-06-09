import pytest
from recycled_code.score_matrix.score_matrix import generate_score_matrix, top_exact_scores

def test_score_matrix_contains_normalized_probabilities():
    matrix = generate_score_matrix(1.7, 1.1, max_goals=8, rho=-0.05)
    assert matrix
    assert all(0 <= probability <= 1 for probability in matrix.values())
    assert sum(matrix.values()) == pytest.approx(1.0)
    assert len(top_exact_scores(matrix, 5)) == 5
