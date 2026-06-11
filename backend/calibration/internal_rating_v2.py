"""Chronological internal football rating with predict-observe-update semantics."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class RatingConfig:
    initial_rating: float = 1500.0
    scale: float = 400.0
    k_factor: float = 20.0
    goal_margin_multiplier: bool = True
    competition_weighting: bool = True
    context_advantage: float = 0.0


def competition_weight(match: dict[str, Any]) -> float:
    if str(match.get("competition_tier")) == "qualification":
        return 0.85
    return 1.0


class InternalRating:
    def __init__(self, config: RatingConfig) -> None:
        self.config = config
        self.ratings: dict[str, float] = {}
        self.timeline: list[dict[str, Any]] = []

    def rating(self, team: str) -> float:
        return self.ratings.get(team, self.config.initial_rating)

    def expected_home(self, home: str, away: str) -> float:
        diff = self.rating(home) - self.rating(away) + self.config.context_advantage
        return 1.0 / (1.0 + 10 ** (-diff / self.config.scale))

    def update(self, match: dict[str, Any], split: str) -> dict[str, Any]:
        home, away = str(match["home_team"]), str(match["away_team"])
        pre_home, pre_away = self.rating(home), self.rating(away)
        expected = self.expected_home(home, away)
        home_score, away_score = int(match["home_score"]), int(match["away_score"])
        actual = 1.0 if home_score > away_score else 0.0 if home_score < away_score else 0.5
        margin = min(2.0, math.log(abs(home_score - away_score) + 1)) if self.config.goal_margin_multiplier else 1.0
        weight = competition_weight(match) if self.config.competition_weighting else 1.0
        change = self.config.k_factor * margin * weight * (actual - expected)
        self.ratings[home] = pre_home + change
        self.ratings[away] = pre_away - change
        record = {
            "match_id": match["match_id"],
            "split": split,
            "kickoff_at": match["kickoff_at"],
            "home_team": home,
            "away_team": away,
            "pre_home_rating": pre_home,
            "pre_away_rating": pre_away,
            "expected_home": expected,
            "actual_home_result": actual,
            "rating_change": change,
            "post_home_rating": self.ratings[home],
            "post_away_rating": self.ratings[away],
        }
        self.timeline.append(record)
        return record

    def parameters(self) -> dict[str, Any]:
        return asdict(self.config)
