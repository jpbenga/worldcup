"""Pure error-analysis helpers for historical calibration predictions."""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from typing import Any, Callable

EPSILON = 1e-15
OUTCOMES = ("home", "draw", "away")


def _probabilities(record: dict[str, Any]) -> dict[str, float]:
    markets = record["markets"]
    return {
        "home": float(markets["home_win"]),
        "draw": float(markets["draw"]),
        "away": float(markets["away_win"]),
    }


def _actual_probability(record: dict[str, Any]) -> float:
    return _probabilities(record)[str(record["actual_1x2"])]


def _log_loss(record: dict[str, Any]) -> float:
    return -math.log(max(EPSILON, min(1.0 - EPSILON, _actual_probability(record))))


def _brier(record: dict[str, Any]) -> float:
    probabilities = _probabilities(record)
    actual = str(record["actual_1x2"])
    return sum((probabilities[outcome] - float(outcome == actual)) ** 2 for outcome in OUTCOMES)


def _actual_score(record: dict[str, Any]) -> str:
    return f"{record['actual_home_score']}-{record['actual_away_score']}"


def _top_3_hit(record: dict[str, Any]) -> bool:
    return _actual_score(record) in {item["score"] for item in record["top_scores"][:3]}


def _rate(count: int | float, total: int) -> float:
    return float(count) / total if total else 0.0


def _average(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def enrich_predictions(
    predictions: list[dict[str, Any]], matches: list[dict[str, Any]], split: str
) -> list[dict[str, Any]]:
    """Join immutable match metadata to prediction records."""
    matches_by_id = {match["match_id"]: match for match in matches}
    if len(matches_by_id) != len(matches):
        raise ValueError(f"Duplicate match IDs in {split} matches")
    if {prediction["match_id"] for prediction in predictions} != set(matches_by_id):
        raise ValueError(f"Prediction and match IDs differ for {split}")
    return [
        {
            **prediction,
            "split": split,
            "season": matches_by_id[prediction["match_id"]]["season"],
            "competition_family": matches_by_id[prediction["match_id"]]["competition_family"],
            "competition_tier": matches_by_id[prediction["match_id"]]["competition_tier"],
            "source_scope": matches_by_id[prediction["match_id"]]["source_scope"],
            "source_status": matches_by_id[prediction["match_id"]]["source_status"],
        }
        for prediction in predictions
    ]


def summarize_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Return common probabilistic and score metrics for one segment."""
    total = len(records)
    actual_results = Counter(record["actual_1x2"] for record in records)
    predicted_results = Counter(record["predicted_1x2"] for record in records)
    exact_hits = sum(record["top_scores"][0]["score"] == _actual_score(record) for record in records)
    return {
        "matches": total,
        "accuracy_1x2": _rate(sum(bool(record["is_correct_1x2"]) for record in records), total),
        "log_loss_1x2": _average([_log_loss(record) for record in records]),
        "brier_score_1x2": _average([_brier(record) for record in records]),
        "exact_score_accuracy": _rate(exact_hits, total),
        "top_3_score_hit_rate": _rate(sum(_top_3_hit(record) for record in records), total),
        "actual_result_distribution": {
            outcome: {"count": actual_results[outcome], "rate": _rate(actual_results[outcome], total)}
            for outcome in OUTCOMES
        },
        "predicted_result_distribution": {
            outcome: {"count": predicted_results[outcome], "rate": _rate(predicted_results[outcome], total)}
            for outcome in OUTCOMES
        },
        "average_predicted_home_goals": _average([float(record["predicted_home_xg"]) for record in records]),
        "average_actual_home_goals": _average([float(record["actual_home_score"]) for record in records]),
        "average_predicted_away_goals": _average([float(record["predicted_away_xg"]) for record in records]),
        "average_actual_away_goals": _average([float(record["actual_away_score"]) for record in records]),
    }


def _segment(records: list[dict[str, Any]], key: Callable[[dict[str, Any]], str]) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        groups[key(record)].append(record)
    return {name: summarize_records(groups[name]) for name in sorted(groups)}


def segment_by_competition(records: list[dict[str, Any]]) -> dict[str, Any]:
    return _segment(records, lambda record: str(record["competition"]))


def segment_by_season(records: list[dict[str, Any]]) -> dict[str, Any]:
    return _segment(records, lambda record: str(record["season"]))


def segment_by_result_type(records: list[dict[str, Any]]) -> dict[str, Any]:
    return _segment(records, lambda record: str(record["actual_1x2"]))


def confidence_bucket(confidence: float) -> str:
    if confidence < 0.40:
        return "0.33-0.40"
    if confidence < 0.50:
        return "0.40-0.50"
    if confidence < 0.60:
        return "0.50-0.60"
    if confidence < 0.70:
        return "0.60-0.70"
    return "0.70+"


def segment_by_confidence_bucket(records: list[dict[str, Any]]) -> dict[str, Any]:
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        probabilities = _probabilities(record)
        buckets[confidence_bucket(max(probabilities.values()))].append(record)
    result = {}
    for name in ("0.33-0.40", "0.40-0.50", "0.50-0.60", "0.60-0.70", "0.70+"):
        items = buckets.get(name, [])
        confidences = [max(_probabilities(record).values()) for record in items]
        accuracy = _rate(sum(bool(record["is_correct_1x2"]) for record in items), len(items))
        average_confidence = _average(confidences)
        result[name] = {
            "matches": len(items),
            "average_confidence": average_confidence,
            "accuracy": accuracy,
            "calibration_gap": accuracy - average_confidence if average_confidence is not None else None,
        }
    return result


def goal_total_segment(record: dict[str, Any]) -> str:
    total = int(record["actual_home_score"]) + int(record["actual_away_score"])
    if total <= 1:
        return "0-1 total goals"
    if total == 2:
        return "2 goals"
    if total == 3:
        return "3 goals"
    return "4+ goals"


def segment_by_goal_total(records: list[dict[str, Any]]) -> dict[str, Any]:
    return _segment(records, goal_total_segment)


def _favorite(record: dict[str, Any]) -> tuple[str, float, str]:
    probabilities = _probabilities(record)
    side = max(("home", "away"), key=lambda outcome: probabilities[outcome])
    team = str(record["home_team"] if side == "home" else record["away_team"])
    return side, probabilities[side], team


def segment_favorite_vs_underdog(records: list[dict[str, Any]]) -> dict[str, Any]:
    favorite_wins = upsets = draws = predicted_favorite = 0
    favorite_probabilities: list[float] = []
    upset_losses: list[float] = []
    high_confidence_wrong = 0
    for record in records:
        side, probability, _ = _favorite(record)
        favorite_probabilities.append(probability)
        predicted_favorite += int(record["predicted_1x2"] == side)
        favorite_wins += int(record["actual_1x2"] == side)
        draws += int(record["actual_1x2"] == "draw")
        is_upset = record["actual_1x2"] not in {side, "draw"}
        upsets += int(is_upset)
        if is_upset:
            upset_losses.append(_log_loss(record))
        high_confidence_wrong += int(probability >= 0.60 and record["actual_1x2"] != side)
    total = len(records)
    return {
        "matches": total,
        "favorite_win_predicted_rate": _rate(predicted_favorite, total),
        "favorite_win_actual_rate": _rate(favorite_wins, total),
        "upset_rate": _rate(upsets, total),
        "draw_rate": _rate(draws, total),
        "average_favorite_probability": _average(favorite_probabilities),
        "average_log_loss_on_upsets": _average(upset_losses),
        "high_confidence_wrong_favorite_picks": high_confidence_wrong,
    }


def analyze_draw_bias(records: list[dict[str, Any]]) -> dict[str, Any]:
    draws = [record for record in records if record["actual_1x2"] == "draw"]
    return {
        "matches": len(records),
        "actual_draw_rate": _rate(len(draws), len(records)),
        "predicted_draw_class_rate": _rate(
            sum(record["predicted_1x2"] == "draw" for record in records), len(records)
        ),
        "average_draw_probability": _average([float(record["markets"]["draw"]) for record in records]),
        "true_draws": len(draws),
        "missed_true_draws": sum(record["predicted_1x2"] != "draw" for record in draws),
        "draw_recall": _rate(sum(record["predicted_1x2"] == "draw" for record in draws), len(draws)),
        "average_log_loss_on_true_draws": _average([_log_loss(record) for record in draws]),
    }


def analyze_favorite_bias(records: list[dict[str, Any]]) -> dict[str, Any]:
    return segment_favorite_vs_underdog(records)


def analyze_modal_score_distribution(records: list[dict[str, Any]]) -> dict[str, Any]:
    modal = Counter(record["top_scores"][0]["score"] for record in records)
    actual = Counter(_actual_score(record) for record in records)
    top_score_hits: dict[str, dict[str, int | float]] = {}
    for score, occurrences in actual.items():
        hits = sum(record["top_scores"][0]["score"] == score and _actual_score(record) == score for record in records)
        top_score_hits[score] = {"actual_occurrences": occurrences, "hits": hits, "hit_rate": hits / occurrences}
    return {
        "modal_score_distribution": dict(modal.most_common()),
        "actual_score_distribution": dict(actual.most_common()),
        "top_score_hit_by_score": dict(sorted(top_score_hits.items())),
        "modal_1_1_rate": _rate(modal["1-1"], len(records)),
        "actual_1_1_rate": _rate(actual["1-1"], len(records)),
        "modal_0_0_rate": _rate(modal["0-0"], len(records)),
        "actual_0_0_rate": _rate(actual["0-0"], len(records)),
    }


def match_diagnostic(record: dict[str, Any], reason: str) -> dict[str, Any]:
    probabilities = _probabilities(record)
    return {
        "split": record["split"],
        "match_id": record["match_id"],
        "competition": record["competition"],
        "season": record["season"],
        "home_team": record["home_team"],
        "away_team": record["away_team"],
        "actual_score": _actual_score(record),
        "predicted_top_score": record["top_scores"][0]["score"],
        "predicted_1x2": record["predicted_1x2"],
        "actual_1x2": record["actual_1x2"],
        "home_win_prob": probabilities["home"],
        "draw_prob": probabilities["draw"],
        "away_win_prob": probabilities["away"],
        "actual_result_probability": _actual_probability(record),
        "prediction_confidence": max(probabilities.values()),
        "predicted_home_xg": record["predicted_home_xg"],
        "predicted_away_xg": record["predicted_away_xg"],
        "log_loss": _log_loss(record),
        "reason": reason,
    }


def identify_worst_log_loss_matches(records: list[dict[str, Any]], top_n: int = 20) -> list[dict[str, Any]]:
    return [
        match_diagnostic(record, "worst_log_loss")
        for record in sorted(records, key=_log_loss, reverse=True)[:top_n]
    ]


def identify_high_confidence_wrong_predictions(
    records: list[dict[str, Any]], top_n: int = 20, threshold: float = 0.60
) -> list[dict[str, Any]]:
    wrong = [
        record
        for record in records
        if not record["is_correct_1x2"] and max(_probabilities(record).values()) >= threshold
    ]
    return [
        match_diagnostic(record, "high_confidence_wrong_prediction")
        for record in sorted(wrong, key=lambda item: max(_probabilities(item).values()), reverse=True)[:top_n]
    ]


def identify_largest_xg_mismatch_matches(records: list[dict[str, Any]], top_n: int = 20) -> list[dict[str, Any]]:
    def mismatch(record: dict[str, Any]) -> float:
        return abs(float(record["predicted_home_xg"]) - float(record["actual_home_score"])) + abs(
            float(record["predicted_away_xg"]) - float(record["actual_away_score"])
        )

    result = []
    for record in sorted(records, key=mismatch, reverse=True)[:top_n]:
        item = match_diagnostic(record, "largest_xg_mismatch")
        item["absolute_xg_score_mismatch"] = mismatch(record)
        result.append(item)
    return result


def identify_unexpected_draws(records: list[dict[str, Any]], top_n: int = 20) -> list[dict[str, Any]]:
    draws = [record for record in records if record["actual_1x2"] == "draw"]
    return [
        match_diagnostic(record, "unexpected_draw")
        for record in sorted(draws, key=lambda item: float(item["markets"]["draw"]))[:top_n]
    ]


def identify_unexpected_upsets(records: list[dict[str, Any]], top_n: int = 20) -> list[dict[str, Any]]:
    upsets = [record for record in records if record["actual_1x2"] not in {_favorite(record)[0], "draw"}]
    return [
        match_diagnostic(record, "unexpected_upset")
        for record in sorted(upsets, key=_actual_probability)[:top_n]
    ]


def segment_by_team(records: list[dict[str, Any]], ranking_limit: int = 20) -> dict[str, Any]:
    teams: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "matches": 0,
            "log_loss_total": 0.0,
            "correct": 0,
            "predicted_points": 0.0,
            "actual_points": 0,
            "goals_for_predicted": 0.0,
            "goals_for_actual": 0,
            "goals_against_predicted": 0.0,
            "goals_against_actual": 0,
        }
    )
    for record in records:
        probabilities = _probabilities(record)
        for side, team in (("home", record["home_team"]), ("away", record["away_team"])):
            values = teams[str(team)]
            values["matches"] += 1
            values["log_loss_total"] += _log_loss(record)
            values["correct"] += int(record["is_correct_1x2"])
            values["predicted_points"] += 3 * probabilities[side] + probabilities["draw"]
            values["actual_points"] += 3 * int(record["actual_1x2"] == side) + int(record["actual_1x2"] == "draw")
            if side == "home":
                values["goals_for_predicted"] += float(record["predicted_home_xg"])
                values["goals_for_actual"] += int(record["actual_home_score"])
                values["goals_against_predicted"] += float(record["predicted_away_xg"])
                values["goals_against_actual"] += int(record["actual_away_score"])
            else:
                values["goals_for_predicted"] += float(record["predicted_away_xg"])
                values["goals_for_actual"] += int(record["actual_away_score"])
                values["goals_against_predicted"] += float(record["predicted_home_xg"])
                values["goals_against_actual"] += int(record["actual_home_score"])

    summaries = []
    for team, values in teams.items():
        matches = int(values["matches"])
        summaries.append(
            {
                "team": team,
                "matches": matches,
                "avg_log_loss": values["log_loss_total"] / matches,
                "accuracy_1x2": values["correct"] / matches,
                "predicted_points": values["predicted_points"],
                "actual_points": values["actual_points"],
                "points_delta": values["predicted_points"] - values["actual_points"],
                "goals_for_predicted": values["goals_for_predicted"],
                "goals_for_actual": values["goals_for_actual"],
                "goals_against_predicted": values["goals_against_predicted"],
                "goals_against_actual": values["goals_against_actual"],
                "sample_warning": matches < 5,
            }
        )
    eligible = [summary for summary in summaries if not summary["sample_warning"]]
    return {
        "teams_count": len(summaries),
        "low_sample_teams_count": sum(summary["sample_warning"] for summary in summaries),
        "worst_teams_by_log_loss": sorted(eligible, key=lambda item: item["avg_log_loss"], reverse=True)[:ranking_limit],
        "best_teams_by_log_loss": sorted(eligible, key=lambda item: item["avg_log_loss"])[:ranking_limit],
        "most_overestimated_teams": sorted(eligible, key=lambda item: item["points_delta"], reverse=True)[:ranking_limit],
        "most_underestimated_teams": sorted(eligible, key=lambda item: item["points_delta"])[:ranking_limit],
        "teams_with_low_sample_warning": sorted(
            (summary for summary in summaries if summary["sample_warning"]), key=lambda item: (item["matches"], item["team"])
        ),
    }


def analyze_split(records: list[dict[str, Any]], top_n: int = 20) -> dict[str, Any]:
    return {
        "summary": summarize_records(records),
        "by_competition": segment_by_competition(records),
        "by_season": segment_by_season(records),
        "by_team": segment_by_team(records, top_n),
        "by_result_type": segment_by_result_type(records),
        "draw_bias": analyze_draw_bias(records),
        "favorite_bias": analyze_favorite_bias(records),
        "confidence_buckets": segment_by_confidence_bucket(records),
        "score_distribution": analyze_modal_score_distribution(records),
        "goal_total_segments": segment_by_goal_total(records),
        "worst_log_loss_matches": identify_worst_log_loss_matches(records, top_n),
        "high_confidence_wrong_predictions": identify_high_confidence_wrong_predictions(records, top_n),
        "largest_xg_mismatch_matches": identify_largest_xg_mismatch_matches(records, top_n),
        "unexpected_draws": identify_unexpected_draws(records, top_n),
        "unexpected_upsets": identify_unexpected_upsets(records, top_n),
    }
