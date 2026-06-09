"""Expected-goal helpers extracted from drc-prototype/optimizer.py and xg-backtest.js."""

from __future__ import annotations


def club_elo_win_probability(delta_elo: float) -> float:
    """Convert an Elo difference into a home-win strength probability."""
    return 1.0 / (10.0 ** (-delta_elo / 400.0) + 1.0)


def compute_lambdas(
    home_xg: float,
    away_xg: float,
    delta_elo: float = 0.0,
    w_xg: float = 1.0,
    w_elo: float = 1.0,
    home_field_advantage: float = 0.0,
) -> tuple[float, float]:
    """Modulate baseline team xG with Elo strength and home-field advantage."""
    if home_xg < 0 or away_xg < 0:
        raise ValueError("Expected goals must be non-negative")
    home_strength = club_elo_win_probability(delta_elo + home_field_advantage)
    away_strength = 1.0 - home_strength
    home_lambda = home_xg * w_xg * ((home_strength / 0.5) ** w_elo)
    away_lambda = away_xg * w_xg * ((away_strength / 0.5) ** w_elo)
    return max(home_lambda, 0.01), max(away_lambda, 0.01)


def rolling_xg_baselines(
    home_for: list[float],
    home_against: list[float],
    away_for: list[float],
    away_against: list[float],
    window: int = 8,
    attack_weight: float = 0.6,
) -> tuple[float, float]:
    """Build matchup xG baselines using the prototype's rolling attack/defence blend."""
    if not 0 <= attack_weight <= 1:
        raise ValueError("attack_weight must be between 0 and 1")
    series = (home_for, home_against, away_for, away_against)
    if window <= 0 or any(len(values) < window for values in series):
        raise ValueError("Each history must contain at least `window` observations")

    def mean_tail(values: list[float]) -> float:
        tail = values[-window:]
        return sum(tail) / window

    defence_weight = 1.0 - attack_weight
    return (
        mean_tail(home_for) * attack_weight + mean_tail(away_against) * defence_weight,
        mean_tail(away_for) * attack_weight + mean_tail(home_against) * defence_weight,
    )
