"""Moderate experimental Elo adjustment layered on top of baseline expected goals."""

from __future__ import annotations

DEFAULT_ELO_WEIGHT = 0.20
MAX_ELO_FACTOR = 0.35
MODEL_VERSION = "elo_v0.4.0"
MODEL_FAMILY = "elo_adjusted"


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))


def adjust_expected_goals(
    baseline_home_xg: float,
    baseline_away_xg: float,
    home_elo: int | None,
    away_elo: int | None,
    weight: float = DEFAULT_ELO_WEIGHT,
) -> dict[str, float | bool | str]:
    """Apply a bounded Elo adjustment, with exact baseline fallback."""
    if baseline_home_xg < 0 or baseline_away_xg < 0:
        raise ValueError("Expected goals must be non-negative")
    if not 0 <= weight <= 1:
        raise ValueError("Elo weight must be between 0 and 1")

    elo_available = home_elo is not None and away_elo is not None
    elo_factor = clamp((home_elo - away_elo) / 400.0, -MAX_ELO_FACTOR, MAX_ELO_FACTOR) if elo_available else 0.0
    return {
        "model_version": MODEL_VERSION,
        "model_family": MODEL_FAMILY,
        "elo_weight": weight,
        "elo_available": elo_available,
        "elo_factor": elo_factor,
        "baseline_home_xg": baseline_home_xg,
        "baseline_away_xg": baseline_away_xg,
        "adjusted_home_xg": baseline_home_xg * (1.0 + elo_factor * weight),
        "adjusted_away_xg": baseline_away_xg * (1.0 - elo_factor * weight),
    }
