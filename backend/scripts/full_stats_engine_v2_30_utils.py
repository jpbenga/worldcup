"""Shared helpers for V2.30 full stats-enriched engine candidate."""

from __future__ import annotations

import math
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, write_json

OUTCOMES = ("home", "draw", "away")


def publish(payload: dict[str, Any], name: str, frontend: bool = True) -> None:
    target = DATA_DIR / "generated" / name
    write_json(payload, target)
    shutil.copy2(target, DATA_DIR / "snapshots" / name)
    if frontend:
        shutil.copy2(target, FRONTEND_DATA_DIR / name)


def parse_date(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def number(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace("%", "")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def avg(values: list[float | int | None]) -> float | None:
    valid = [float(value) for value in values if value is not None]
    return round(sum(valid) / len(valid), 6) if valid else None


def normalize(values: dict[str, float]) -> dict[str, float]:
    total = sum(max(0.0, value) for value in values.values())
    if total <= 0:
        return {key: 1.0 / len(values) for key in values}
    return {key: max(1e-9, value / total) for key, value in values.items()}


def actual(row: dict[str, Any]) -> str:
    return row["actual_1x2"]


def base_probs(row: dict[str, Any]) -> dict[str, float]:
    markets = row["markets"]
    return {"home": float(markets["home_win"]), "draw": float(markets["draw"]), "away": float(markets["away_win"])}


def feature_edge(feature: dict[str, Any]) -> float:
    diff = feature.get("diff_features", {})
    weighted: list[tuple[float, float]] = []
    for key, scale, weight in (
        ("home_minus_away_xg_diff_avg_last5", 2.0, 1.40),
        ("home_minus_away_xg_diff_avg_last10", 2.0, 0.80),
        ("home_minus_away_shots_for_avg_last5", 18.0, 0.75),
        ("home_minus_away_shots_on_goal_for_avg_last5", 7.0, 0.80),
        ("home_minus_away_possession_avg_last5", 30.0, 0.35),
        ("home_minus_away_corners_for_avg_last5", 7.0, 0.35),
        ("home_minus_away_passes_accurate_avg_last5", 350.0, 0.25),
        ("home_minus_away_goals_for_avg_last5", 4.0, 0.85),
        ("home_minus_away_goals_against_avg_last5", -4.0, 0.65),
        ("home_minus_away_clean_sheet_rate_last5", 1.0, 0.45),
        ("home_minus_away_large_win_rate_last5", 1.0, 0.50),
        ("home_minus_away_event_goal_diff_avg_last5", 4.0, 0.35),
        ("home_minus_away_player_rating_avg_last5", 2.0, 0.30),
    ):
        value = diff.get(key)
        if isinstance(value, (int, float)) and scale:
            signed = float(value) / scale
            weighted.append((max(-1.75, min(1.75, signed)), weight))
    if not weighted:
        return 0.0
    score = sum(value * weight for value, weight in weighted) / sum(weight for _, weight in weighted)
    return max(-1.5, min(1.5, score))


def coverage_factor(feature: dict[str, Any]) -> float:
    coverage = feature.get("coverage", {})
    stat = min(1.0, (coverage.get("home_stats_matches_last5", 0) + coverage.get("away_stats_matches_last5", 0)) / 6.0)
    xg = min(1.0, (coverage.get("home_xg_matches_last5", 0) + coverage.get("away_xg_matches_last5", 0)) / 4.0)
    events = min(1.0, (coverage.get("home_events_matches_last5", 0) + coverage.get("away_events_matches_last5", 0)) / 6.0)
    return round(0.25 + 0.45 * stat + 0.20 * xg + 0.10 * events, 6)


def adjusted_probs(row: dict[str, Any], feature: dict[str, Any], alpha: float, coverage_aware: bool = True) -> dict[str, float]:
    base = base_probs(row)
    edge = feature_edge(feature)
    if not edge:
        return base
    strength = alpha * (coverage_factor(feature) if coverage_aware else 1.0)
    logits = {key: math.log(max(1e-9, value)) for key, value in base.items()}
    logits["home"] += strength * edge
    logits["away"] -= strength * edge
    logits["draw"] -= abs(strength * edge) * 0.10
    exp = {key: math.exp(value) for key, value in logits.items()}
    return normalize(exp)


def matrix_entries(row: dict[str, Any]) -> list[dict[str, Any]]:
    matrix = row.get("score_matrix", [])
    return matrix.get("probabilities", []) if isinstance(matrix, dict) else matrix


def parse_score(item: dict[str, Any]) -> tuple[int, int, float]:
    if "home_goals" in item and "away_goals" in item:
        return int(item["home_goals"]), int(item["away_goals"]), float(item["probability"])
    h, a = [int(part) for part in str(item["score"]).split("-")]
    return h, a, float(item["probability"])


def adjusted_matrix(row: dict[str, Any], feature: dict[str, Any], alpha: float) -> list[dict[str, Any]]:
    edge = feature_edge(feature) * coverage_factor(feature)
    items = []
    raw_total = 0.0
    for item in matrix_entries(row):
        h, a, probability = parse_score(item)
        margin = h - a
        total = h + a
        wide_bonus = 1.0 + min(0.30, abs(edge) * alpha * max(0, abs(margin) - 1) * 0.10)
        pace_bonus = 1.0 + min(0.18, abs(edge) * alpha * max(0, total - 2) * 0.06)
        weight = math.exp(alpha * 0.45 * edge * margin) * wide_bonus * pace_bonus
        adjusted = max(0.0, probability * weight)
        raw_total += adjusted
        items.append({"score": f"{h}-{a}", "home_goals": h, "away_goals": a, "probability": adjusted})
    if raw_total <= 0:
        return matrix_entries(row)
    return [{**item, "probability": item["probability"] / raw_total} for item in items]


def markets_from_matrix(items: list[dict[str, Any]]) -> dict[str, float]:
    home = draw = away = over25 = over35 = btts = clean_home = clean_away = 0.0
    for item in items:
        h, a, p = parse_score(item)
        home += p if h > a else 0.0
        draw += p if h == a else 0.0
        away += p if a > h else 0.0
        over25 += p if h + a >= 3 else 0.0
        over35 += p if h + a >= 4 else 0.0
        btts += p if h > 0 and a > 0 else 0.0
        clean_home += p if a == 0 else 0.0
        clean_away += p if h == 0 else 0.0
    return {
        "home_win": home, "draw": draw, "away_win": away,
        "over_2_5": over25, "under_2_5": 1 - over25,
        "over_3_5": over35, "under_3_5": 1 - over35,
        "btts_yes": btts, "btts_no": 1 - btts,
        "both_teams_to_score_yes": btts, "both_teams_to_score_no": 1 - btts,
        "clean_sheet_home": clean_home, "clean_sheet_away": clean_away,
    }


def large_win_probability(row: dict[str, Any], matrix: list[dict[str, Any]] | None = None) -> float:
    total = 0.0
    for item in matrix or matrix_entries(row):
        h, a, p = parse_score(item)
        if abs(h - a) >= 3:
            total += p
    return total


def top_scores_from_matrix(items: list[dict[str, Any]], n: int = 5) -> list[dict[str, Any]]:
    return [
        {"score": item["score"], "probability": item["probability"]}
        for item in sorted(items, key=lambda value: value["probability"], reverse=True)[:n]
    ]


def logloss(row: dict[str, Any], p: dict[str, float]) -> float:
    return -math.log(max(1e-12, p[actual(row)]))


def brier(row: dict[str, Any], p: dict[str, float]) -> float:
    return sum((p[key] - float(key == actual(row))) ** 2 for key in OUTCOMES)


def score_rows(rows: list[dict[str, Any]], features: dict[str, dict[str, Any]], alpha: float, coverage_aware: bool = True) -> dict[str, Any]:
    if not rows:
        return {"matches": 0}
    ll = br = correct = draw_actual = draw_prob = 0.0
    favorite_actual = favorite_prob = strong_count = strong_correct = 0.0
    upset_actual = upset_prob = large_actual = large_prob = 0.0
    over25_brier = over35_brier = btts_brier = exact_top3 = exact_top5 = 0.0
    for row in rows:
        feature = features[row["match_id"]]
        p = adjusted_probs(row, feature, alpha, coverage_aware)
        matrix = adjusted_matrix(row, feature, alpha)
        market_matrix = markets_from_matrix(matrix)
        prediction = max(p, key=p.get)
        a = actual(row)
        ll += logloss(row, p)
        br += brier(row, p)
        correct += int(prediction == a)
        draw_actual += int(a == "draw")
        draw_prob += p["draw"]
        favorite = "home" if row["markets"]["home_win"] >= row["markets"]["away_win"] else "away"
        actual_side = "home" if row["actual_home_score"] > row["actual_away_score"] else "away" if row["actual_away_score"] > row["actual_home_score"] else "draw"
        favorite_actual += int(actual_side == favorite)
        favorite_prob += p[favorite]
        upset_side = "away" if favorite == "home" else "home"
        upset_actual += int(actual_side == upset_side)
        upset_prob += p[upset_side]
        if max(row["markets"]["home_win"], row["markets"]["away_win"]) >= 0.60:
            strong_count += 1
            strong_correct += int(actual_side == favorite)
        total_goals = row["actual_home_score"] + row["actual_away_score"]
        over25_brier += (market_matrix["over_2_5"] - float(total_goals >= 3)) ** 2
        over35_brier += (market_matrix["over_3_5"] - float(total_goals >= 4)) ** 2
        btts_brier += (market_matrix["btts_yes"] - float(row["actual_home_score"] > 0 and row["actual_away_score"] > 0)) ** 2
        large_actual += int(abs(row["actual_home_score"] - row["actual_away_score"]) >= 3)
        large_prob += large_win_probability(row, matrix)
        scores = [item["score"] for item in top_scores_from_matrix(matrix, 5)]
        actual_score = f"{row['actual_home_score']}-{row['actual_away_score']}"
        exact_top3 += int(actual_score in scores[:3])
        exact_top5 += int(actual_score in scores[:5])
    n = len(rows)
    return {
        "matches": n,
        "accuracy_1x2": round(correct / n, 6),
        "log_loss_1x2": round(ll / n, 6),
        "brier_score_1x2": round(br / n, 6),
        "draw_actual_rate": round(draw_actual / n, 6),
        "draw_probability_average": round(draw_prob / n, 6),
        "draw_calibration_gap": round(draw_actual / n - draw_prob / n, 6),
        "favorite_actual_win_rate": round(favorite_actual / n, 6),
        "favorite_probability_average": round(favorite_prob / n, 6),
        "favorite_calibration_gap": round(favorite_actual / n - favorite_prob / n, 6),
        "underdog_upset_actual_rate": round(upset_actual / n, 6),
        "underdog_upset_probability_average": round(upset_prob / n, 6),
        "strong_favorite_accuracy": round(strong_correct / strong_count, 6) if strong_count else None,
        "large_win_actual_rate": round(large_actual / n, 6),
        "large_win_probability_average": round(large_prob / n, 6),
        "large_win_calibration_gap": round(large_actual / n - large_prob / n, 6),
        "over_2_5_brier": round(over25_brier / n, 6),
        "over_3_5_brier": round(over35_brier / n, 6),
        "btts_brier": round(btts_brier / n, 6),
        "exact_score_top3": round(exact_top3 / n, 6),
        "exact_score_top5": round(exact_top5 / n, 6),
    }


def metric_delta(candidate: dict[str, Any], baseline: dict[str, Any]) -> dict[str, Any]:
    return {
        key: round(candidate[key] - baseline[key], 6)
        for key in ("log_loss_1x2", "brier_score_1x2", "accuracy_1x2", "large_win_calibration_gap")
        if isinstance(candidate.get(key), (int, float)) and isinstance(baseline.get(key), (int, float))
    }


def rows_for(split: str) -> list[dict[str, Any]]:
    return load_json(DATA_DIR / "generated" / f"historical_{split}_predictions_quant_engine_v2_2.json")


def load_feature_index() -> dict[str, dict[str, Any]]:
    rows = load_json(DATA_DIR / "generated" / "full_stats_lagged_features_v2_30.json")["features"]
    return {row["match_id"]: row for row in rows}
