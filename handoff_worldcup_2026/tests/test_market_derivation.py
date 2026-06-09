import pytest
from recycled_code.markets.market_derivation import derive_markets
from recycled_code.score_matrix.score_matrix import generate_score_matrix

def test_complementary_markets_sum_to_one():
    markets = derive_markets(generate_score_matrix(1.7, 1.1))
    assert markets["home_win"] + markets["draw"] + markets["away_win"] == pytest.approx(1.0)
    assert markets["btts_yes"] + markets["btts_no"] == pytest.approx(1.0)
    assert markets["over_2_5"] + markets["under_2_5"] == pytest.approx(1.0)
