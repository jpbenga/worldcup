"""Explainable team-strength Poisson calibrator for the isolated V0.9 experiment."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any

MODEL_VERSION = "calibrated_simple_poisson_v0.9"
MODEL_FAMILY = "historical_calibrated_simple_poisson"


@dataclass(frozen=True)
class CalibrationConfig:
    min_team_matches: int = 5
    smoothing_weight: float = 8.0
    xg_min: float = 0.2
    xg_max: float = 3.5


class CalibratedSimplePoisson:
    """Fit smoothed home/away attack and defence rates from completed matches."""

    def __init__(self, config: CalibrationConfig | None = None) -> None:
        self.config = config or CalibrationConfig()
        self.global_home_goals = 0.0
        self.global_away_goals = 0.0
        self.teams: dict[str, dict[str, float | int]] = {}
        self.train_matches = 0

    @staticmethod
    def _smoothed_rate(total: float, matches: int, global_rate: float, weight: float) -> float:
        return (total + weight * global_rate) / (matches + weight)

    def fit(self, matches: list[dict[str, Any]]) -> "CalibratedSimplePoisson":
        if not matches:
            raise ValueError("At least one training match is required")
        self.train_matches = len(matches)
        self.global_home_goals = sum(float(match["home_score"]) for match in matches) / len(matches)
        self.global_away_goals = sum(float(match["away_score"]) for match in matches) / len(matches)
        stats: dict[str, dict[str, float | int]] = defaultdict(
            lambda: {
                "home_matches": 0,
                "away_matches": 0,
                "home_goals_for": 0.0,
                "home_goals_against": 0.0,
                "away_goals_for": 0.0,
                "away_goals_against": 0.0,
            }
        )
        for match in matches:
            home, away = str(match["home_team"]), str(match["away_team"])
            home_goals, away_goals = float(match["home_score"]), float(match["away_score"])
            stats[home]["home_matches"] += 1
            stats[home]["home_goals_for"] += home_goals
            stats[home]["home_goals_against"] += away_goals
            stats[away]["away_matches"] += 1
            stats[away]["away_goals_for"] += away_goals
            stats[away]["away_goals_against"] += home_goals

        weight = self.config.smoothing_weight
        teams: dict[str, dict[str, float | int]] = {}
        for team, raw in stats.items():
            home_matches = int(raw["home_matches"])
            away_matches = int(raw["away_matches"])
            home_for = self._smoothed_rate(float(raw["home_goals_for"]), home_matches, self.global_home_goals, weight)
            home_against = self._smoothed_rate(
                float(raw["home_goals_against"]), home_matches, self.global_away_goals, weight
            )
            away_for = self._smoothed_rate(float(raw["away_goals_for"]), away_matches, self.global_away_goals, weight)
            away_against = self._smoothed_rate(
                float(raw["away_goals_against"]), away_matches, self.global_home_goals, weight
            )
            home_attack_strength = home_for / self.global_home_goals
            home_defense_weakness = home_against / self.global_away_goals
            away_attack_strength = away_for / self.global_away_goals
            away_defense_weakness = away_against / self.global_home_goals
            aggregate_defense_weakness = (home_defense_weakness + away_defense_weakness) / 2
            teams[team] = {
                "matches": home_matches + away_matches,
                "home_matches": home_matches,
                "away_matches": away_matches,
                "attack_strength": (home_attack_strength + away_attack_strength) / 2,
                "defense_strength": 1 / aggregate_defense_weakness,
                "home_attack_strength": home_attack_strength,
                "home_defense_weakness": home_defense_weakness,
                "away_attack_strength": away_attack_strength,
                "away_defense_weakness": away_defense_weakness,
                "sparse_team": home_matches + away_matches < self.config.min_team_matches,
            }
        self.teams = teams
        return self

    def predict_expected_goals(self, home_team: str, away_team: str) -> tuple[float, float, dict[str, Any]]:
        if not self.teams:
            raise ValueError("Model must be fitted before prediction")
        home = self.teams.get(home_team)
        away = self.teams.get(away_team)
        home_attack = float(home["home_attack_strength"]) if home else 1.0
        home_defense = float(home["home_defense_weakness"]) if home else 1.0
        away_attack = float(away["away_attack_strength"]) if away else 1.0
        away_defense = float(away["away_defense_weakness"]) if away else 1.0
        raw_home_xg = self.global_home_goals * home_attack * away_defense
        raw_away_xg = self.global_away_goals * away_attack * home_defense
        home_xg = min(self.config.xg_max, max(self.config.xg_min, raw_home_xg))
        away_xg = min(self.config.xg_max, max(self.config.xg_min, raw_away_xg))
        metadata = {
            "home_team_seen_in_train": home is not None,
            "away_team_seen_in_train": away is not None,
            "home_team_matches": int(home["matches"]) if home else 0,
            "away_team_matches": int(away["matches"]) if away else 0,
            "home_team_sparse": bool(home["sparse_team"]) if home else True,
            "away_team_sparse": bool(away["sparse_team"]) if away else True,
            "xg_was_capped": home_xg != raw_home_xg or away_xg != raw_away_xg,
            "terrain_neutral_handling": "unknown_not_modeled",
            "competition_handling": "shared_global_rates_no_competition_parameter",
        }
        return home_xg, away_xg, metadata

    def parameters(self) -> dict[str, Any]:
        return {
            "model_version": MODEL_VERSION,
            "model_family": MODEL_FAMILY,
            "trained_on": "historical_train_matches.json",
            "historically_calibrated": True,
            "status": "experimental",
            "global_home_goals": self.global_home_goals,
            "global_away_goals": self.global_away_goals,
            "smoothing": {
                "min_team_matches": self.config.min_team_matches,
                "smoothing_weight": self.config.smoothing_weight,
            },
            "xg_bounds": {"min": self.config.xg_min, "max": self.config.xg_max},
            "teams": self.teams,
        }
