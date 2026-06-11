"""Independent-Poisson score distribution and analytical markets for V2."""

from __future__ import annotations

import math
from typing import Any


def poisson(goals: int, lam: float) -> float:
    return math.exp(-lam) * lam**goals / math.factorial(goals)


def score_distribution(home_lambda: float, away_lambda: float, max_goals: int = 7) -> dict[str, float]:
    raw = {
        f"{home}-{away}": poisson(home, home_lambda) * poisson(away, away_lambda)
        for home in range(max_goals + 1)
        for away in range(max_goals + 1)
    }
    total = sum(raw.values())
    return {score: probability / total for score, probability in raw.items()}


def score_tuple(score: str) -> tuple[int, int]:
    home, away = score.split("-", maxsplit=1)
    return int(home), int(away)


def analytical_markets(matrix: dict[str, float]) -> dict[str, float]:
    values = {
        "home_win": 0.0, "draw": 0.0, "away_win": 0.0, "over_0_5": 0.0, "over_1_5": 0.0,
        "over_2_5": 0.0, "over_3_5": 0.0, "btts_yes": 0.0, "clean_sheet_home": 0.0,
        "clean_sheet_away": 0.0, "team_home_over_0_5": 0.0, "team_away_over_0_5": 0.0,
        "team_home_over_1_5": 0.0, "team_away_over_1_5": 0.0,
    }
    for score, probability in matrix.items():
        home, away = score_tuple(score)
        values["home_win" if home > away else "away_win" if away > home else "draw"] += probability
        for line in (0.5, 1.5, 2.5, 3.5):
            values[f"over_{str(line).replace('.', '_')}"] += probability * (home + away > line)
        values["btts_yes"] += probability * (home > 0 and away > 0)
        values["clean_sheet_home"] += probability * (away == 0)
        values["clean_sheet_away"] += probability * (home == 0)
        values["team_home_over_0_5"] += probability * (home > 0)
        values["team_away_over_0_5"] += probability * (away > 0)
        values["team_home_over_1_5"] += probability * (home > 1)
        values["team_away_over_1_5"] += probability * (away > 1)
    values.update(
        {
            "double_chance_1X": values["home_win"] + values["draw"],
            "double_chance_X2": values["away_win"] + values["draw"],
            "double_chance_12": values["home_win"] + values["away_win"],
            "draw_no_bet_home": values["home_win"] / max(1e-12, values["home_win"] + values["away_win"]),
            "draw_no_bet_away": values["away_win"] / max(1e-12, values["home_win"] + values["away_win"]),
            "under_1_5": 1 - values["over_1_5"],
            "under_2_5": 1 - values["over_2_5"],
            "under_3_5": 1 - values["over_3_5"],
            "btts_no": 1 - values["btts_yes"],
            "both_teams_to_score_yes": values["btts_yes"],
            "both_teams_to_score_no": 1 - values["btts_yes"],
        }
    )
    return values


def top_scores(matrix: dict[str, float], limit: int = 5) -> list[dict[str, Any]]:
    return [{"score": score, "probability": probability} for score, probability in sorted(matrix.items(), key=lambda x: x[1], reverse=True)[:limit]]
