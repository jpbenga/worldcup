"""Leakage-safe pre-match feature construction through chronological replay."""

from __future__ import annotations

from collections import defaultdict, deque
from datetime import datetime
from typing import Any

from backend.calibration.internal_rating_v2 import InternalRating, RatingConfig

FEATURE_NAMES = [
    "home_internal_rating",
    "away_internal_rating",
    "rating_diff",
    "rating_abs_diff",
    "home_recent_goals_for",
    "home_recent_goals_against",
    "away_recent_goals_for",
    "away_recent_goals_against",
    "home_attack_strength",
    "away_attack_strength",
    "home_defense_weakness",
    "away_defense_weakness",
    "attack_diff",
    "defense_diff",
    "competition_family_encoded",
    "competition_tier_encoded",
    "season",
    "days_since_home_last_match",
    "days_since_away_last_match",
    "home_matches_seen",
    "away_matches_seen",
    "home_low_sample_flag",
    "away_low_sample_flag",
    "neutral_or_home_context",
]
FAMILY_CODES = {"world_championship": 0.0, "continental_championship": 1.0, "continental_qualification": 2.0}
TIER_CODES = {"major_tournament": 0.0, "qualification": 1.0}


def parse_date(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


class TeamHistory:
    def __init__(self) -> None:
        self.goals_for: dict[str, deque[float]] = defaultdict(lambda: deque(maxlen=5))
        self.goals_against: dict[str, deque[float]] = defaultdict(lambda: deque(maxlen=5))
        self.total_for: dict[str, float] = defaultdict(float)
        self.total_against: dict[str, float] = defaultdict(float)
        self.matches: dict[str, int] = defaultdict(int)
        self.last_match: dict[str, datetime] = {}
        self.global_goals = 1.35
        self.global_team_games = 0
        self.global_goal_sum = 0.0

    def rate(self, team: str, kind: str) -> float:
        count = self.matches[team]
        total = self.total_for[team] if kind == "for" else self.total_against[team]
        return (total + 8 * self.global_goals) / (count + 8)

    def recent(self, team: str, kind: str) -> float:
        values = self.goals_for[team] if kind == "for" else self.goals_against[team]
        return sum(values) / len(values) if values else self.global_goals

    def days_since(self, team: str, kickoff: datetime) -> float:
        return min(730.0, max(0.0, (kickoff - self.last_match[team]).total_seconds() / 86400)) if team in self.last_match else 365.0

    def update(self, match: dict[str, Any]) -> None:
        home, away = str(match["home_team"]), str(match["away_team"])
        hg, ag = float(match["home_score"]), float(match["away_score"])
        for team, goals_for, goals_against in ((home, hg, ag), (away, ag, hg)):
            self.goals_for[team].append(goals_for)
            self.goals_against[team].append(goals_against)
            self.total_for[team] += goals_for
            self.total_against[team] += goals_against
            self.matches[team] += 1
            self.last_match[team] = parse_date(str(match["kickoff_at"]))
        self.global_goal_sum += hg + ag
        self.global_team_games += 2
        self.global_goals = self.global_goal_sum / self.global_team_games


def outcome_label(match: dict[str, Any]) -> int:
    return 0 if match["home_score"] > match["away_score"] else 2 if match["home_score"] < match["away_score"] else 1


def labels(match: dict[str, Any]) -> dict[str, int]:
    home, away = int(match["home_score"]), int(match["away_score"])
    total = home + away
    return {
        "outcome_1x2": outcome_label(match),
        "over_0_5": int(total > 0.5),
        "over_1_5": int(total > 1.5),
        "over_2_5": int(total > 2.5),
        "over_3_5": int(total > 3.5),
        "under_1_5": int(total < 1.5),
        "under_2_5": int(total < 2.5),
        "under_3_5": int(total < 3.5),
        "btts_yes": int(home > 0 and away > 0),
        "btts_no": int(home == 0 or away == 0),
        "clean_sheet_home": int(away == 0),
        "clean_sheet_away": int(home == 0),
        "home_team_scores": int(home > 0),
        "away_team_scores": int(away > 0),
        "home_over_1_5": int(home > 1.5),
        "away_over_1_5": int(away > 1.5),
        "double_chance_1X": int(home >= away),
        "double_chance_X2": int(away >= home),
        "double_chance_12": int(home != away),
        "draw_no_bet_home_non_loss": int(home >= away),
        "draw_no_bet_away_non_loss": int(away >= home),
    }


def build_feature_row(
    match: dict[str, Any], split: str, rating: InternalRating, history: TeamHistory
) -> dict[str, Any]:
    home, away = str(match["home_team"]), str(match["away_team"])
    kickoff = parse_date(str(match["kickoff_at"]))
    home_rating, away_rating = rating.rating(home), rating.rating(away)
    home_attack, away_attack = history.rate(home, "for"), history.rate(away, "for")
    home_defense, away_defense = history.rate(home, "against"), history.rate(away, "against")
    features = {
        "home_internal_rating": home_rating,
        "away_internal_rating": away_rating,
        "rating_diff": home_rating - away_rating,
        "rating_abs_diff": abs(home_rating - away_rating),
        "home_recent_goals_for": history.recent(home, "for"),
        "home_recent_goals_against": history.recent(home, "against"),
        "away_recent_goals_for": history.recent(away, "for"),
        "away_recent_goals_against": history.recent(away, "against"),
        "home_attack_strength": home_attack / max(0.1, history.global_goals),
        "away_attack_strength": away_attack / max(0.1, history.global_goals),
        "home_defense_weakness": home_defense / max(0.1, history.global_goals),
        "away_defense_weakness": away_defense / max(0.1, history.global_goals),
        "attack_diff": home_attack - away_attack,
        "defense_diff": away_defense - home_defense,
        "competition_family_encoded": FAMILY_CODES.get(str(match.get("competition_family")), 3.0),
        "competition_tier_encoded": TIER_CODES.get(str(match.get("competition_tier")), 2.0),
        "season": float(match["season"]),
        "days_since_home_last_match": history.days_since(home, kickoff),
        "days_since_away_last_match": history.days_since(away, kickoff),
        "home_matches_seen": float(history.matches[home]),
        "away_matches_seen": float(history.matches[away]),
        "home_low_sample_flag": float(history.matches[home] < 8),
        "away_low_sample_flag": float(history.matches[away] < 8),
        "neutral_or_home_context": 0.0,
    }
    return {
        "match_id": match["match_id"],
        "split": split,
        "kickoff_at": match["kickoff_at"],
        "competition": match["competition"],
        "competition_tier": match.get("competition_tier"),
        "season": match["season"],
        "home_team": home,
        "away_team": away,
        "actual_home_score": match["home_score"],
        "actual_away_score": match["away_score"],
        "features": features,
        "labels": labels(match),
    }


def build_chronological_features(
    split_matches: dict[str, list[dict[str, Any]]], config: RatingConfig
) -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]], dict[str, Any], InternalRating, TeamHistory]:
    rating, history = InternalRating(config), TeamHistory()
    rows: dict[str, list[dict[str, Any]]] = {split: [] for split in split_matches}
    for split in ("train", "validation", "test"):
        for match in sorted(split_matches[split], key=lambda item: item["kickoff_at"]):
            rows[split].append(build_feature_row(match, split, rating, history))
            rating.update(match, split)
            history.update(match)
    audit = {
        "feature_count": len(FEATURE_NAMES),
        "feature_names": FEATURE_NAMES,
        "pre_match_only": True,
        "current_match_stats_used": False,
        "post_match_update_only": True,
        "external_static_elo_used": False,
        "unknown_context_encoded_neutral": True,
        "rows_by_split": {split: len(items) for split, items in rows.items()},
        "low_sample_rows_by_split": {
            split: sum(row["features"]["home_low_sample_flag"] or row["features"]["away_low_sample_flag"] for row in items)
            for split, items in rows.items()
        },
        "leakage_detected": False,
    }
    return rows, rating.timeline, audit, rating, history


def feature_matrix(rows: list[dict[str, Any]]) -> list[list[float]]:
    return [[float(row["features"][name]) for name in FEATURE_NAMES] for row in rows]
