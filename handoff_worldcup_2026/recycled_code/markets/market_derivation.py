"""Minimal market derivation added around the recycled score-matrix representation."""

from __future__ import annotations

from collections.abc import Mapping

from ..score_matrix.score_matrix import top_exact_scores


def _score(score: str) -> tuple[int, int]:
    try:
        home, away = score.split("-", maxsplit=1)
        return int(home), int(away)
    except (ValueError, AttributeError) as exc:
        raise ValueError(f"Invalid score key: {score!r}") from exc


def derive_markets(matrix: Mapping[str, float], exact_score_limit: int = 5) -> dict[str, object]:
    """Aggregate 1X2, double chance, totals, BTTS, and top exact scores."""
    total_mass = sum(matrix.values())
    if total_mass <= 0:
        raise ValueError("Score matrix must have a positive probability mass")
    probabilities = {score: probability / total_mass for score, probability in matrix.items()}

    home_win = draw = away_win = btts_yes = 0.0
    overs = {0.5: 0.0, 1.5: 0.0, 2.5: 0.0, 3.5: 0.0}
    for score, probability in probabilities.items():
        home, away = _score(score)
        if home > away:
            home_win += probability
        elif home == away:
            draw += probability
        else:
            away_win += probability
        if home > 0 and away > 0:
            btts_yes += probability
        for line in overs:
            if home + away > line:
                overs[line] += probability

    return {
        "home_win": home_win,
        "draw": draw,
        "away_win": away_win,
        "home_or_draw": home_win + draw,
        "away_or_draw": away_win + draw,
        "no_draw": home_win + away_win,
        "over_0_5": overs[0.5],
        "over_1_5": overs[1.5],
        "over_2_5": overs[2.5],
        "over_3_5": overs[3.5],
        "under_2_5": 1.0 - overs[2.5],
        "under_3_5": 1.0 - overs[3.5],
        "btts_yes": btts_yes,
        "btts_no": 1.0 - btts_yes,
        "top_exact_scores": top_exact_scores(probabilities, exact_score_limit),
    }
