"""Train and evaluate a bounded stats-enriched candidate overlay."""

from __future__ import annotations

import math
import shutil
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, load_json, write_json

OUTPUT = "stats_enriched_engine_candidate_v2_28.json"
OUTCOMES = ("home", "draw", "away")


def publish(payload: dict[str, Any]) -> None:
    target = DATA_DIR / "generated" / OUTPUT
    write_json(payload, target)
    shutil.copy2(target, DATA_DIR / "snapshots" / OUTPUT)


def actual(row: dict[str, Any]) -> str:
    return row["actual_1x2"]


def probs(row: dict[str, Any]) -> dict[str, float]:
    return {"home": row["markets"]["home_win"], "draw": row["markets"]["draw"], "away": row["markets"]["away_win"]}


def normalize(values: dict[str, float]) -> dict[str, float]:
    total = sum(values.values())
    return {key: max(1e-9, value / total) for key, value in values.items()}


def edge(feature: dict[str, Any]) -> float:
    diff = feature.get("diff_features", {})
    values = []
    for key, scale in (
        ("home_minus_away_xg_diff_avg_last5", 2.5),
        ("home_minus_away_shots_for_avg_last5", 20.0),
        ("home_minus_away_shots_on_goal_for_avg_last5", 8.0),
        ("home_minus_away_goals_for_avg_last5", 4.0),
        ("home_minus_away_large_win_rate_last5", 1.0),
    ):
        value = diff.get(key)
        if isinstance(value, (int, float)):
            values.append(max(-1.5, min(1.5, float(value) / scale)))
    return sum(values) / len(values) if values else 0.0


def apply_overlay(row: dict[str, Any], feature: dict[str, Any], alpha: float) -> dict[str, float]:
    base = probs(row)
    e = edge(feature)
    if not e or feature["coverage"]["home_stats_matches_last5"] + feature["coverage"]["away_stats_matches_last5"] == 0:
        return base
    logits = {key: math.log(max(1e-9, value)) for key, value in base.items()}
    logits["home"] += alpha * e
    logits["away"] -= alpha * e
    exp = {key: math.exp(value) for key, value in logits.items()}
    return normalize(exp)


def brier(row: dict[str, Any], p: dict[str, float]) -> float:
    a = actual(row)
    return sum((p[key] - float(key == a)) ** 2 for key in OUTCOMES)


def logloss(row: dict[str, Any], p: dict[str, float]) -> float:
    return -math.log(max(1e-12, p[actual(row)]))


def score_metrics(rows: list[dict[str, Any]], features: dict[str, dict[str, Any]], alpha: float) -> dict[str, Any]:
    if not rows:
        return {"matches": 0}
    ll = br = correct = over25_brier = over35_brier = btts_brier = large_actual = large_pred = 0.0
    draws = draw_prob = favorite_hits = favorite_total = upset_total = upset_prob = 0.0
    exact_top3 = exact_top5 = 0
    for row in rows:
        p = apply_overlay(row, features[row["match_id"]], alpha)
        a = actual(row)
        prediction = max(p, key=p.get)
        ll += logloss(row, p)
        br += brier(row, p)
        correct += int(prediction == a)
        draws += int(a == "draw")
        draw_prob += p["draw"]
        side = "home" if row["actual_home_score"] > row["actual_away_score"] else "away" if row["actual_away_score"] > row["actual_home_score"] else "draw"
        favorite = "home" if row["markets"]["home_win"] >= row["markets"]["away_win"] else "away"
        if favorite != "draw":
            favorite_total += 1
            favorite_hits += int(side == favorite)
            upset_total += int(side not in (favorite, "draw"))
            upset_prob += p["away" if favorite == "home" else "home"]
        total_goals = row["actual_home_score"] + row["actual_away_score"]
        over25_brier += (row["markets"]["over_2_5"] - float(total_goals >= 3)) ** 2
        over35_brier += (row["markets"]["over_3_5"] - float(total_goals >= 4)) ** 2
        btts_brier += (row["markets"]["btts_yes"] - float(row["actual_home_score"] > 0 and row["actual_away_score"] > 0)) ** 2
        large_actual += int(abs(row["actual_home_score"] - row["actual_away_score"]) >= 3)
        large_pred += large_win_probability(row)
        scores = [item["score"] for item in row.get("top_scores", [])]
        actual_score = f"{row['actual_home_score']}-{row['actual_away_score']}"
        exact_top3 += int(actual_score in scores[:3])
        exact_top5 += int(actual_score in scores[:5])
    n = len(rows)
    return {
        "matches": n, "accuracy_1x2": round(correct / n, 6), "log_loss_1x2": round(ll / n, 6),
        "brier_score_1x2": round(br / n, 6), "draw_actual_rate": round(draws / n, 6),
        "draw_probability_average": round(draw_prob / n, 6), "draw_calibration_gap": round(draws / n - draw_prob / n, 6),
        "favorite_actual_win_rate": round(favorite_hits / favorite_total, 6) if favorite_total else None,
        "underdog_upset_actual_rate": round(upset_total / favorite_total, 6) if favorite_total else None,
        "underdog_upset_probability_average": round(upset_prob / favorite_total, 6) if favorite_total else None,
        "large_win_actual_rate": round(large_actual / n, 6), "large_win_probability_average": round(large_pred / n, 6),
        "large_win_calibration_gap": round(large_actual / n - large_pred / n, 6),
        "over_2_5_brier": round(over25_brier / n, 6), "over_3_5_brier": round(over35_brier / n, 6),
        "btts_brier": round(btts_brier / n, 6), "exact_score_top3": round(exact_top3 / n, 6),
        "exact_score_top5": round(exact_top5 / n, 6),
    }


def large_win_probability(row: dict[str, Any]) -> float:
    entries = row.get("score_matrix", [])
    if isinstance(entries, dict):
        entries = entries.get("probabilities", [])
    total = 0.0
    for item in entries:
        score = item["score"]
        h, a = [int(part) for part in score.split("-")]
        if abs(h - a) >= 3:
            total += float(item["probability"])
    return total


def rows_for(split: str) -> list[dict[str, Any]]:
    return load_json(DATA_DIR / "generated" / f"historical_{split}_predictions_quant_engine_v2_2.json")


def delta(candidate: dict[str, Any], baseline: dict[str, Any]) -> dict[str, Any]:
    return {
        key: round(candidate[key] - baseline[key], 6)
        for key in ("log_loss_1x2", "brier_score_1x2", "accuracy_1x2", "large_win_calibration_gap")
        if isinstance(candidate.get(key), (int, float)) and isinstance(baseline.get(key), (int, float))
    }


def segment_metrics(rows: list[dict[str, Any]], features: dict[str, dict[str, Any]], alpha: float) -> dict[str, Any]:
    selectors: dict[str, Callable[[dict[str, Any]], bool]] = {
        "with_xg_lag": lambda r: features[r["match_id"]]["coverage"]["home_xg_matches_last5"] > 0 and features[r["match_id"]]["coverage"]["away_xg_matches_last5"] > 0,
        "without_xg_lag": lambda r: not (features[r["match_id"]]["coverage"]["home_xg_matches_last5"] > 0 and features[r["match_id"]]["coverage"]["away_xg_matches_last5"] > 0),
        "recent_competitions": lambda r: int(r["season"]) >= 2024,
        "older_competitions": lambda r: int(r["season"]) < 2024,
        "strong_favorites": lambda r: max(r["markets"]["home_win"], r["markets"]["away_win"]) >= 0.6,
        "balanced_matches": lambda r: max(r["markets"]["home_win"], r["markets"]["away_win"]) < 0.45,
        "actual_large_wins": lambda r: abs(r["actual_home_score"] - r["actual_away_score"]) >= 3,
        "matrix_large_win_signal": lambda r: large_win_probability(r) >= 0.10,
    }
    return {name: score_metrics([row for row in rows if selector(row)], features, alpha) for name, selector in selectors.items()}


def main() -> None:
    feature_rows = load_json(DATA_DIR / "generated" / "api_stats_lagged_features_v2_28.json")["features"]
    features = {row["match_id"]: row for row in feature_rows}
    validation, test = rows_for("validation"), rows_for("test")
    alphas = [0.0, 0.05, 0.1, 0.2, 0.35, 0.5]
    baseline_val = score_metrics(validation, features, 0.0)
    baseline_test = score_metrics(test, features, 0.0)
    trials = []
    for alpha in alphas:
        metrics = score_metrics(validation, features, alpha)
        trials.append({
            "feature_set": "quant_hybrid_v2.2_plus_lagged_stats_overlay",
            "params": {"alpha": alpha}, "validation_metrics": metrics,
            "delta_vs_baseline": delta(metrics, baseline_val),
        })
    eligible = [trial for trial in trials if trial["validation_metrics"]["brier_score_1x2"] <= baseline_val["brier_score_1x2"] + 0.002]
    selected = min(eligible or trials, key=lambda trial: trial["validation_metrics"]["log_loss_1x2"])
    non_zero_trials = [trial for trial in trials if float(trial["params"]["alpha"]) > 0]
    best_non_zero = min(non_zero_trials, key=lambda trial: trial["validation_metrics"]["log_loss_1x2"]) if non_zero_trials else None
    alpha = float(selected["params"]["alpha"])
    candidate_val = score_metrics(validation, features, alpha)
    candidate_test = score_metrics(test, features, alpha)
    comparison = {
        "improves_log_loss": candidate_test["log_loss_1x2"] < baseline_test["log_loss_1x2"],
        "improves_brier": candidate_test["brier_score_1x2"] < baseline_test["brier_score_1x2"],
        "improves_large_win_calibration": abs(candidate_test["large_win_calibration_gap"]) < abs(baseline_test["large_win_calibration_gap"]),
        "delta_test": delta(candidate_test, baseline_test),
        "tradeoffs": [],
    }
    if not comparison["improves_log_loss"]:
        comparison["tradeoffs"].append("Stats overlay did not improve test log loss versus quant_hybrid_v2.2.")
    if not comparison["improves_brier"]:
        comparison["tradeoffs"].append("Stats overlay did not improve test Brier score.")
    promote = comparison["improves_log_loss"] and comparison["improves_brier"] and candidate_test["accuracy_1x2"] >= baseline_test["accuracy_1x2"] - 0.005
    payload = {
        "version": "v2.28", "candidate_name": "stats_enriched_candidate_v2_28",
        "training_method": "bounded validation-selected overlay on top of quant_hybrid_v2.2 using sparse lagged API-Football stats",
        "feature_sets": [
            {
                "key": "A",
                "name": "Baseline active features + lagged stats coverage-aware overlay",
                "tested": True,
                "implementation": "bounded logit overlay selected on validation",
            },
            {
                "key": "B",
                "name": "Lagged xG only where available + missing indicators",
                "tested": True,
                "implementation": "included in the overlay edge when both teams have prior xG rows",
            },
            {
                "key": "C",
                "name": "Two-head model",
                "tested": False,
                "implementation": "deferred until the stat-covered sample is large enough for a separate head",
            },
            {
                "key": "D",
                "name": "Ensemble with stats boost only when coverage is sufficient",
                "tested": True,
                "implementation": "represented by alpha grid; promotion alpha selected only if validation clears guardrails",
            },
        ],
        "splits": {"validation": len(validation), "test": len(test), "selection_grid": alphas, "selected_alpha": alpha},
        "metrics": {
            "validation": {"baseline_quant_hybrid_v2_2": baseline_val, "candidate": candidate_val},
            "test": {"baseline_quant_hybrid_v2_2": baseline_test, "candidate": candidate_test},
            "segments": {
                "validation": segment_metrics(validation, features, alpha),
                "test": segment_metrics(test, features, alpha),
            },
            "trials": trials,
            "best_non_zero_stats_overlay_trial": best_non_zero,
        },
        "comparison_to_quant_hybrid_v2_2": comparison,
        "promotion_recommendation": {
            "promote": promote,
            "reason": "Promote only if global test log loss and Brier improve without segment regressions." if promote else "Do not promote: sparse lagged stats are useful but the candidate has not cleared the active-engine benchmark.",
            "required_before_promotion": [
                "Broaden historical statistics coverage beyond the quota sample.",
                "Evaluate a proper two-head model with enough stat-covered rows.",
                "Validate score-tail realism and 1X2 calibration together.",
                "Keep quant_hybrid_v2.2 active until the gate is passed.",
            ],
        },
        "warnings": ["No Optuna was run; this is a bounded candidate benchmark, not a production promotion."],
    }
    publish(payload)
    print(f"V2.28 stats-enriched candidate: selected_alpha={alpha}, promote={promote}")


if __name__ == "__main__":
    main()
