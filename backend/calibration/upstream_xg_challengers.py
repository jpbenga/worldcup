"""Isolated weighted Simple Poisson challengers for upstream xG experiments."""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from datetime import datetime
from typing import Any, Callable

from backend.calibration.calibration_metrics import actual_outcome
from backend.calibration.challengers import evaluate_challenger_predictions
from backend.markets.market_derivation import derive_markets
from backend.score_matrix.score_matrix import generate_score_matrix

BASE_MODEL_VERSION = "calibrated_simple_poisson_v0.9"
COMPETITION_MODEL_VERSION = "competition_weighted_xg_v1.4"
TIME_DECAY_MODEL_VERSION = "time_decay_xg_v1.4"
LOW_SAMPLE_MODEL_VERSION = "low_sample_fallback_xg_v1.4"
ELO_DIAGNOSTIC_MODEL_VERSION = "elo_prior_xg_v1.4_diagnostic"
MODEL_FAMILY = "isolated_upstream_weighted_simple_poisson"
RHO = -0.05
MAX_GOALS = 8
BASE_SMOOTHING_WEIGHT = 8.0
XG_MIN = 0.2
XG_MAX = 3.5

COMPETITION_WEIGHT_GRID = (
    {
        "major_tournament_weight": 1.0,
        "continental_championship_weight": 0.9,
        "qualifier_weight": 0.75,
        "friendly_weight": 0.4,
    },
    {
        "major_tournament_weight": 1.0,
        "continental_championship_weight": 0.85,
        "qualifier_weight": 0.65,
        "friendly_weight": 0.3,
    },
    {
        "major_tournament_weight": 1.0,
        "continental_championship_weight": 1.0,
        "qualifier_weight": 0.8,
        "friendly_weight": 0.5,
    },
)
TIME_DECAY_HALF_LIVES = (12, 24, 36, 48)
LOW_SAMPLE_GRID = (
    {"low_sample_threshold": 5, "extra_smoothing_weight": 8},
    {"low_sample_threshold": 8, "extra_smoothing_weight": 12},
    {"low_sample_threshold": 10, "extra_smoothing_weight": 16},
)
ELO_DIAGNOSTIC_PARAMS = {"elo_prior_weight": 0.15, "elo_diff_scale": 400, "elo_factor_cap": 0.25}


def parse_date(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def competition_weight(match: dict[str, Any], params: dict[str, float]) -> float:
    family = str(match.get("competition_family", ""))
    tier = str(match.get("competition_tier", ""))
    if family == "friendly":
        return float(params["friendly_weight"])
    if "qualification" in family or tier == "qualification":
        return float(params["qualifier_weight"])
    if family == "continental_championship":
        return float(params["continental_championship_weight"])
    return float(params["major_tournament_weight"])


def time_decay_weight(match: dict[str, Any], target_date: datetime, half_life_months: float) -> float:
    match_date = parse_date(str(match["kickoff_at"]))
    if match_date > target_date:
        raise ValueError("Training match occurs after the prediction date")
    age_months = (target_date - match_date).total_seconds() / (30.4375 * 24 * 60 * 60)
    return 0.5 ** (age_months / half_life_months)


class WeightedSimplePoisson:
    """Fit the V0.9 model form with explicit match weights and sparse-team smoothing."""

    def __init__(self, low_sample_threshold: int = 0, extra_smoothing_weight: float = 0.0) -> None:
        self.low_sample_threshold = low_sample_threshold
        self.extra_smoothing_weight = extra_smoothing_weight
        self.global_home_goals = 0.0
        self.global_away_goals = 0.0
        self.teams: dict[str, dict[str, Any]] = {}
        self.effective_sample_weight = 0.0
        self.effective_sample_size = 0.0

    @staticmethod
    def _smoothed(total: float, weight_sum: float, global_rate: float, smoothing: float) -> float:
        return (total + smoothing * global_rate) / (weight_sum + smoothing)

    def fit(self, matches: list[dict[str, Any]], weights: list[float] | None = None) -> "WeightedSimplePoisson":
        if not matches:
            raise ValueError("At least one training match is required")
        weights = weights or [1.0] * len(matches)
        if len(weights) != len(matches) or any(weight <= 0 for weight in weights):
            raise ValueError("A positive weight is required for every training match")
        total_weight = sum(weights)
        self.effective_sample_weight = total_weight
        self.effective_sample_size = total_weight**2 / sum(weight**2 for weight in weights)
        self.global_home_goals = sum(float(match["home_score"]) * weight for match, weight in zip(matches, weights)) / total_weight
        self.global_away_goals = sum(float(match["away_score"]) * weight for match, weight in zip(matches, weights)) / total_weight
        stats: dict[str, dict[str, float | int]] = defaultdict(
            lambda: {
                "raw_matches": 0,
                "home_weight": 0.0,
                "away_weight": 0.0,
                "home_goals_for": 0.0,
                "home_goals_against": 0.0,
                "away_goals_for": 0.0,
                "away_goals_against": 0.0,
            }
        )
        for match, weight in zip(matches, weights):
            home, away = str(match["home_team"]), str(match["away_team"])
            home_goals, away_goals = float(match["home_score"]), float(match["away_score"])
            stats[home]["raw_matches"] += 1
            stats[away]["raw_matches"] += 1
            stats[home]["home_weight"] += weight
            stats[away]["away_weight"] += weight
            stats[home]["home_goals_for"] += home_goals * weight
            stats[home]["home_goals_against"] += away_goals * weight
            stats[away]["away_goals_for"] += away_goals * weight
            stats[away]["away_goals_against"] += home_goals * weight

        teams = {}
        for team, raw in stats.items():
            raw_matches = int(raw["raw_matches"])
            low_sample = self.low_sample_threshold > 0 and raw_matches < self.low_sample_threshold
            smoothing = BASE_SMOOTHING_WEIGHT + (self.extra_smoothing_weight if low_sample else 0.0)
            home_weight, away_weight = float(raw["home_weight"]), float(raw["away_weight"])
            home_for = self._smoothed(float(raw["home_goals_for"]), home_weight, self.global_home_goals, smoothing)
            home_against = self._smoothed(
                float(raw["home_goals_against"]), home_weight, self.global_away_goals, smoothing
            )
            away_for = self._smoothed(float(raw["away_goals_for"]), away_weight, self.global_away_goals, smoothing)
            away_against = self._smoothed(
                float(raw["away_goals_against"]), away_weight, self.global_home_goals, smoothing
            )
            teams[team] = {
                "matches": raw_matches,
                "effective_match_weight": home_weight + away_weight,
                "home_attack_strength": home_for / self.global_home_goals,
                "home_defense_weakness": home_against / self.global_away_goals,
                "away_attack_strength": away_for / self.global_away_goals,
                "away_defense_weakness": away_against / self.global_home_goals,
                "low_sample_handled": low_sample,
                "smoothing_weight": smoothing,
            }
        self.teams = teams
        return self

    def predict_expected_goals(self, home_team: str, away_team: str) -> tuple[float, float, dict[str, Any]]:
        home, away = self.teams.get(home_team), self.teams.get(away_team)
        raw_home_xg = self.global_home_goals * (
            float(home["home_attack_strength"]) if home else 1.0
        ) * (float(away["away_defense_weakness"]) if away else 1.0)
        raw_away_xg = self.global_away_goals * (
            float(away["away_attack_strength"]) if away else 1.0
        ) * (float(home["home_defense_weakness"]) if home else 1.0)
        home_xg = min(XG_MAX, max(XG_MIN, raw_home_xg))
        away_xg = min(XG_MAX, max(XG_MIN, raw_away_xg))
        return home_xg, away_xg, {
            "home_team_seen_in_train": home is not None,
            "away_team_seen_in_train": away is not None,
            "home_team_matches": int(home["matches"]) if home else 0,
            "away_team_matches": int(away["matches"]) if away else 0,
            "home_team_effective_match_weight": float(home["effective_match_weight"]) if home else 0.0,
            "away_team_effective_match_weight": float(away["effective_match_weight"]) if away else 0.0,
            "home_low_sample_handled": bool(home["low_sample_handled"]) if home else True,
            "away_low_sample_handled": bool(away["low_sample_handled"]) if away else True,
            "low_sample_handled": bool(not home or not away or home["low_sample_handled"] or away["low_sample_handled"]),
            "xg_was_capped": home_xg != raw_home_xg or away_xg != raw_away_xg,
        }


def score_probability(score: str, probability: float) -> dict[str, Any]:
    home_goals, away_goals = (int(value) for value in score.split("-", maxsplit=1))
    return {"score": score, "home_goals": home_goals, "away_goals": away_goals, "probability": probability}


def prediction_record(
    match: dict[str, Any],
    home_xg: float,
    away_xg: float,
    metadata: dict[str, Any],
    model_version: str,
    selected_params: dict[str, Any],
) -> dict[str, Any]:
    matrix = generate_score_matrix(home_xg, away_xg, max_goals=MAX_GOALS, rho=RHO)
    derived = derive_markets(matrix)
    markets = {key: value for key, value in derived.items() if key != "top_exact_scores"}
    top_scores = [score_probability(str(item["score"]), float(item["probability"])) for item in derived["top_exact_scores"]]
    predicted = max((("home", markets["home_win"]), ("draw", markets["draw"]), ("away", markets["away_win"])), key=lambda item: item[1])[0]
    actual = actual_outcome(int(match["home_score"]), int(match["away_score"]))
    return {
        "match_id": match["match_id"],
        "model_version": model_version,
        "base_model_version": BASE_MODEL_VERSION,
        "model_family": MODEL_FAMILY,
        "historically_calibrated": True,
        "status": "experimental",
        "promotion_recommendation": "do_not_promote_yet",
        "selected_params": selected_params,
        "competition": match["competition"],
        "competition_tier": match.get("competition_tier"),
        "competition_family": match.get("competition_family"),
        "season": match["season"],
        "kickoff_at": match["kickoff_at"],
        "home_team": match["home_team"],
        "away_team": match["away_team"],
        "actual_home_score": match["home_score"],
        "actual_away_score": match["away_score"],
        "predicted_home_xg": home_xg,
        "predicted_away_xg": away_xg,
        "score_matrix": [score_probability(score, probability) for score, probability in matrix.items()],
        "markets": markets,
        "top_scores": top_scores,
        "predicted_1x2": predicted,
        "actual_1x2": actual,
        "is_correct_1x2": predicted == actual,
        "prediction_metadata": metadata,
    }


def predict_with_model(
    matches: list[dict[str, Any]], model: WeightedSimplePoisson, model_version: str, selected_params: dict[str, Any]
) -> list[dict[str, Any]]:
    return [
        prediction_record(match, *model.predict_expected_goals(str(match["home_team"]), str(match["away_team"])), model_version, selected_params)
        for match in matches
    ]


def predict_time_decay(
    train: list[dict[str, Any]], matches: list[dict[str, Any]], half_life_months: int
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    predictions, effective_sizes, effective_weights = [], [], []
    for match in matches:
        target = parse_date(str(match["kickoff_at"]))
        weights = [time_decay_weight(train_match, target, half_life_months) for train_match in train]
        model = WeightedSimplePoisson().fit(train, weights)
        home_xg, away_xg, metadata = model.predict_expected_goals(str(match["home_team"]), str(match["away_team"]))
        metadata.update({"half_life_months": half_life_months, "effective_sample_size": model.effective_sample_size})
        predictions.append(
            prediction_record(match, home_xg, away_xg, metadata, TIME_DECAY_MODEL_VERSION, {"half_life_months": half_life_months})
        )
        effective_sizes.append(model.effective_sample_size)
        effective_weights.append(model.effective_sample_weight)
    return predictions, {
        "average_effective_sample_size": sum(effective_sizes) / len(effective_sizes),
        "min_effective_sample_size": min(effective_sizes),
        "max_effective_sample_size": max(effective_sizes),
        "average_effective_sample_weight": sum(effective_weights) / len(effective_weights),
    }


def apply_elo_prior(
    matches: list[dict[str, Any]],
    model: WeightedSimplePoisson,
    elo_ratings: dict[str, float],
    params: dict[str, float] = ELO_DIAGNOSTIC_PARAMS,
) -> list[dict[str, Any]]:
    predictions = []
    for match in matches:
        home_team, away_team = str(match["home_team"]), str(match["away_team"])
        home_xg, away_xg, metadata = model.predict_expected_goals(home_team, away_team)
        home_elo, away_elo = elo_ratings.get(home_team), elo_ratings.get(away_team)
        if home_elo is not None and away_elo is not None:
            raw = ((home_elo - away_elo) / float(params["elo_diff_scale"])) * float(params["elo_prior_weight"])
            factor = min(float(params["elo_factor_cap"]), max(-float(params["elo_factor_cap"]), raw))
            home_xg = min(XG_MAX, max(XG_MIN, home_xg * (1 + factor)))
            away_xg = min(XG_MAX, max(XG_MIN, away_xg * (1 - factor)))
        else:
            factor = 0.0
        metadata.update(
            {
                "temporal_leakage_risk": True,
                "elo_available_for_both_teams": home_elo is not None and away_elo is not None,
                "elo_factor": factor,
                "elo_evidence": "current_static_snapshot_used_on_historical_matches",
            }
        )
        predictions.append(prediction_record(match, home_xg, away_xg, metadata, ELO_DIAGNOSTIC_MODEL_VERSION, params))
    return predictions


def evaluate_metrics(predictions: list[dict[str, Any]], split: str, model_version: str) -> dict[str, Any]:
    metrics = evaluate_challenger_predictions(predictions, split, model_version)
    average_predicted = sum(float(item["predicted_home_xg"]) + float(item["predicted_away_xg"]) for item in predictions) / len(predictions)
    average_actual = sum(float(item["actual_home_score"]) + float(item["actual_away_score"]) for item in predictions) / len(predictions)
    metrics.update(
        {
            "favorite_calibration_gap": metrics["favorite_actual_win_rate"] - metrics["favorite_predicted_win_rate"],
            "average_predicted_goals": average_predicted,
            "average_actual_goals": average_actual,
            "predicted_vs_actual_goal_gap": average_predicted - average_actual,
        }
    )
    return metrics


def segment_metrics(
    predictions: list[dict[str, Any]], split: str, model_version: str, train_team_counts: Counter[str]
) -> dict[str, Any]:
    def grouped(key: Callable[[dict[str, Any]], str]) -> dict[str, Any]:
        groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for prediction in predictions:
            groups[key(prediction)].append(prediction)
        return {name: evaluate_metrics(items, split, model_version) for name, items in sorted(groups.items())}

    return {
        "performance_by_competition": grouped(lambda item: str(item["competition"])),
        "performance_by_competition_tier": grouped(lambda item: str(item.get("competition_tier"))),
        "performance_by_season": grouped(lambda item: str(item["season"])),
        "performance_by_low_sample_teams": grouped(
            lambda item: "low_sample"
            if train_team_counts[str(item["home_team"])] < 8 or train_team_counts[str(item["away_team"])] < 8
            else "non_low_sample"
        ),
    }


def metric_deltas(challenger: dict[str, Any], baseline: dict[str, Any]) -> dict[str, float | int]:
    direct = (
        "accuracy_1x2",
        "log_loss_1x2",
        "brier_score_1x2",
        "exact_score_accuracy",
        "top_3_score_hit_rate",
        "modal_1_1_rate",
        "high_confidence_wrong_predictions",
    )
    delta = {metric: challenger[metric] - baseline[metric] for metric in direct}
    for metric in ("draw_calibration_gap", "favorite_calibration_gap", "predicted_vs_actual_goal_gap"):
        delta[metric] = abs(challenger[metric]) - abs(baseline[metric])
    return delta


def guardrails(
    validation: dict[str, Any],
    test: dict[str, Any],
    baseline_validation: dict[str, Any],
    baseline_test: dict[str, Any],
    segments: dict[str, Any],
    baseline_segments: dict[str, Any],
    temporal_leakage_risk: bool = False,
) -> dict[str, bool]:
    low = segments["test"]["performance_by_low_sample_teams"].get("low_sample")
    base_low = baseline_segments["test"]["performance_by_low_sample_teams"].get("low_sample")
    major = segments["test"]["performance_by_competition_tier"].get("major_tournament")
    base_major = baseline_segments["test"]["performance_by_competition_tier"].get("major_tournament")
    return {
        "test_log_loss_improves_by_0_01": test["log_loss_1x2"] <= baseline_test["log_loss_1x2"] - 0.01,
        "test_brier_improves_by_0_01": test["brier_score_1x2"] <= baseline_test["brier_score_1x2"] - 0.01,
        "validation_log_loss_improved": validation["log_loss_1x2"] < baseline_validation["log_loss_1x2"],
        "validation_brier_improved": validation["brier_score_1x2"] < baseline_validation["brier_score_1x2"],
        "accuracy_not_materially_worse": test["accuracy_1x2"] >= baseline_test["accuracy_1x2"] - 0.01,
        "top_3_not_materially_worse": test["top_3_score_hit_rate"] >= baseline_test["top_3_score_hit_rate"] - 0.01,
        "draw_calibration_not_severely_worse": abs(test["draw_calibration_gap"]) <= abs(baseline_test["draw_calibration_gap"]) + 0.01,
        "high_confidence_wrong_not_increased": test["high_confidence_wrong_predictions"] <= baseline_test["high_confidence_wrong_predictions"],
        "modal_1_1_not_increased": test["modal_1_1_rate"] <= baseline_test["modal_1_1_rate"],
        "no_temporal_leakage": not temporal_leakage_risk,
        "low_sample_segment_not_severely_harmed": bool(not low or not base_low or low["log_loss_1x2"] <= base_low["log_loss_1x2"] + 0.02),
        "major_competition_segment_not_severely_harmed": bool(
            not major or not base_major or major["log_loss_1x2"] <= base_major["log_loss_1x2"] + 0.02
        ),
    }


def train_team_counts(train: list[dict[str, Any]]) -> Counter[str]:
    return Counter(team for match in train for team in (str(match["home_team"]), str(match["away_team"])))


def recent_coverage_by_team(train: list[dict[str, Any]], reference_date: datetime, months: int = 24) -> dict[str, Any]:
    cutoff_seconds = months * 30.4375 * 24 * 60 * 60
    counts = Counter()
    teams = {team for match in train for team in (str(match["home_team"]), str(match["away_team"]))}
    for match in train:
        if (reference_date - parse_date(str(match["kickoff_at"]))).total_seconds() <= cutoff_seconds:
            counts.update((str(match["home_team"]), str(match["away_team"])))
    return {
        "window_months": months,
        "reference_date": reference_date.isoformat(),
        "team_counts": {team: counts[team] for team in sorted(teams)},
        "low_coverage_teams": sorted(team for team in teams if counts[team] < 5),
    }
