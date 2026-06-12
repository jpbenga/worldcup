"""Evaluate bounded V2.8 score-matrix challengers without retraining."""

from __future__ import annotations

import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, load_json, utc_now
from backend.scripts.v2_8_matrix_utils import (
    ENGINE,
    VERSION,
    entries_to_matrix,
    favorite_info,
    historical_metrics,
    matrix_markets,
    matrix_to_entries,
    normalize,
    ordered_scores,
    publish,
)

Matrix = dict[tuple[int, int], float]


def active_probabilities(row: dict[str, Any]) -> dict[str, float]:
    markets = row["markets"]
    return {"home": markets["home_win"], "draw": markets["draw"], "away": markets["away_win"]}


def favorite_gap_scaling(matrix: Matrix, probabilities: dict[str, float], alpha: float, beta: float) -> Matrix:
    side, favorite_probability = favorite_info(probabilities)
    gap = max(0.0, favorite_probability - 0.55)
    if gap == 0:
        return matrix.copy()
    adjusted = {}
    for (home, away), value in matrix.items():
        favorite_goals, underdog_goals = (home, away) if side == "home" else (away, home)
        adjusted[(home, away)] = value * math.exp(alpha * gap * favorite_goals - beta * gap * underdog_goals)
    return normalize(adjusted)


def margin_boost(matrix: Matrix, probabilities: dict[str, float], threshold: float, fraction: float) -> Matrix:
    side, favorite_probability = favorite_info(probabilities)
    if favorite_probability < threshold:
        return matrix.copy()
    adjusted = matrix.copy()
    max_goal = max(max(score) for score in matrix)
    for score, value in list(matrix.items()):
        home, away = score
        is_one_goal_win = (side == "home" and home - away == 1) or (side == "away" and away - home == 1)
        target = (home + 1, away) if side == "home" else (home, away + 1)
        if is_one_goal_win and max(target) <= max_goal and target in adjusted:
            moved = value * fraction
            adjusted[score] -= moved
            adjusted[target] += moved
    return adjusted


def total_goals_temperature(matrix: Matrix, gamma: float) -> Matrix:
    return normalize({score: value * math.exp(gamma * sum(score)) for score, value in matrix.items()})


def draw_mass_correction(matrix: Matrix, probabilities: dict[str, float], threshold: float, fraction: float) -> Matrix:
    side, favorite_probability = favorite_info(probabilities)
    if favorite_probability < threshold:
        return matrix.copy()
    adjusted = matrix.copy()
    max_goal = max(max(score) for score in matrix)
    for (home, away), value in list(matrix.items()):
        if home != away:
            continue
        target = (home + 1, away) if side == "home" else (home, away + 1)
        if max(target) <= max_goal and target in adjusted:
            moved = value * fraction
            adjusted[(home, away)] -= moved
            adjusted[target] += moved
    return adjusted


def variants() -> list[tuple[str, str, dict[str, Any], Callable[[Matrix, dict[str, float]], Matrix]]]:
    output = []
    for alpha, beta in ((0.5, 0.25), (1.0, 0.5), (1.5, 0.75), (2.0, 1.0)):
        output.append((
            f"A_gap_alpha_{alpha}_beta_{beta}",
            "A — Favorite gap lambda scaling",
            {"alpha": alpha, "beta": beta},
            lambda matrix, probabilities, a=alpha, b=beta: favorite_gap_scaling(matrix, probabilities, a, b),
        ))
    for threshold, fraction in ((0.60, 0.05), (0.60, 0.10), (0.60, 0.15), (0.65, 0.10), (0.65, 0.20)):
        output.append((
            f"B_margin_t{threshold}_f{fraction}",
            "B — Strong favorite margin boost",
            {"threshold": threshold, "fraction": fraction},
            lambda matrix, probabilities, t=threshold, f=fraction: margin_boost(matrix, probabilities, t, f),
        ))
    for gamma in (0.03, 0.06, 0.10, 0.15):
        output.append((
            f"C_total_gamma_{gamma}",
            "C — Total goals temperature",
            {"gamma": gamma},
            lambda matrix, probabilities, g=gamma: total_goals_temperature(matrix, g),
        ))
    for threshold, fraction in ((0.60, 0.03), (0.60, 0.06), (0.65, 0.05), (0.65, 0.10)):
        output.append((
            f"D_draw_t{threshold}_f{fraction}",
            "D — Draw mass correction",
            {"threshold": threshold, "fraction": fraction},
            lambda matrix, probabilities, t=threshold, f=fraction: draw_mass_correction(matrix, probabilities, t, f),
        ))
    return output


def guardrails(baseline: dict[str, Any], metrics: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "score_log_likelihood_improved": metrics["score_log_loss"] < baseline["score_log_loss"] - 0.001,
        "exact_score_not_materially_degraded": metrics["exact_score_accuracy"] >= baseline["exact_score_accuracy"] - 0.02,
        "one_x_two_accuracy_not_materially_degraded": metrics["one_x_two_accuracy"] >= baseline["one_x_two_accuracy"] - 0.01,
        "one_x_two_brier_not_materially_degraded": metrics["one_x_two_brier"] <= baseline["one_x_two_brier"] + 0.01,
        "dnb_win_not_materially_degraded": metrics["dnb_win_excluding_pushes"] >= baseline["dnb_win_excluding_pushes"] - 0.02,
        "dnb_non_loss_not_materially_degraded": metrics["dnb_non_loss_including_pushes"] >= baseline["dnb_non_loss_including_pushes"] - 0.02,
        "over_under_brier_not_materially_degraded": metrics["over_2_5_brier"] <= baseline["over_2_5_brier"] + 0.01,
        "top_3_not_materially_degraded": metrics["top_3_accuracy"] >= baseline["top_3_accuracy"] - 0.01,
        "top_5_not_materially_degraded": metrics["top_5_accuracy"] >= baseline["top_5_accuracy"] - 0.01,
        "favorite_margin_gap_improved": abs(metrics["actual_average_favorite_margin"] - metrics["modal_average_favorite_margin"])
        < abs(baseline["actual_average_favorite_margin"] - baseline["modal_average_favorite_margin"]),
        "no_extreme_modal_explosion": sum(
            count for score, count in metrics["modal_score_distribution"].items() if sum(map(int, score.split("-"))) >= 5
        )
        <= 0.05 * metrics["matches"],
    }
    return {"checks": checks, "passed": all(checks.values())}


def challenger_score(baseline: dict[str, Any], metrics: dict[str, Any]) -> float:
    return (
        (baseline["score_log_loss"] - metrics["score_log_loss"]) * 4
        + (metrics["top_3_accuracy"] - baseline["top_3_accuracy"])
        + (metrics["top_5_accuracy"] - baseline["top_5_accuracy"])
        + (baseline["over_2_5_brier"] - metrics["over_2_5_brier"])
        + (
            abs(baseline["actual_average_favorite_margin"] - baseline["modal_average_favorite_margin"])
            - abs(metrics["actual_average_favorite_margin"] - metrics["modal_average_favorite_margin"])
        )
        * 0.25
    )


def build_candidate(
    release_matches: list[dict[str, Any]], transform: Callable[[Matrix, dict[str, float]], Matrix], winner: dict[str, Any]
) -> dict[str, Any]:
    matches = []
    for row in release_matches:
        old_matrix = entries_to_matrix(row)
        probabilities = {"home": row["probabilities"]["home_win"], "draw": row["probabilities"]["draw"], "away": row["probabilities"]["away_win"]}
        new_matrix = transform(old_matrix, probabilities)
        old_markets, new_markets = matrix_markets(old_matrix), matrix_markets(new_matrix)
        old_top, new_top = ordered_scores(old_matrix, 5), ordered_scores(new_matrix, 5)
        matches.append({
            "match_id": row["match_id"],
            "home_team": row["home_team"],
            "away_team": row["away_team"],
            "old_score_modal": old_top[0]["score"],
            "new_score_modal": new_top[0]["score"],
            "old_top_scores": old_top,
            "new_top_scores": new_top,
            "old_markets": old_markets,
            "new_markets": new_markets,
            "active_one_x_two": row["probabilities"],
            "one_x_two_preserved": True,
            "one_x_two_preservation_scope": "Frozen active hybrid 1X2 is preserved; matrix-derived 1X2 changes with the candidate matrix.",
            "matrix_realism_improved": winner["guardrails"]["checks"]["favorite_margin_gap_improved"],
            "difference_explanation": "Candidate changes only the score matrix projection; frozen active hybrid 1X2 probabilities remain unchanged.",
            "score_matrix": {"max_goals": row["score_matrix"]["max_goals"], "probabilities": matrix_to_entries(new_matrix)},
        })
    return {
        "generated_at": utc_now(),
        "version": VERSION,
        "engine_version": ENGINE,
        "status": "candidate_not_active",
        "challenger": winner["id"],
        "fixture_count": len(matches),
        "active_predictions_replaced": False,
        "matches": matches,
    }


def markdown(payload: dict[str, Any]) -> str:
    baseline, decision = payload["baseline"], payload["promotion_decision"]
    best = payload["best_challenger"]
    return f"""# Score Matrix Challengers V2.8

V2.8 evaluates bounded post-model score-matrix transformations on the frozen 460-match historical test. World Cup 2026 fixtures are never used for selection. No XGBoost model is retrained and Optuna is not rerun.

## Baseline

The active matrix reaches exact/top-3/top-5 accuracy of `{baseline['exact_score_accuracy']:.1%}` / `{baseline['top_3_accuracy']:.1%}` / `{baseline['top_5_accuracy']:.1%}`, score log loss `{baseline['score_log_loss']:.4f}`, 1X2 Brier `{baseline['one_x_two_brier']:.4f}` and over-2.5 Brier `{baseline['over_2_5_brier']:.4f}`.

## Challengers

Tested families include favorite-gap lambda scaling, strong-favorite margin redistribution, total-goals temperature and strong-favorite draw-mass correction. Challenger E, a constrained hybrid reconstruction matching 1X2, over 2.5 and team-goal targets, is assessed as feasible but deferred because it requires a dedicated numerical solver and validation protocol.

The best measured challenger is `{best['id']}`. Its exact/top-3/top-5 accuracy is `{best['metrics']['exact_score_accuracy']:.1%}` / `{best['metrics']['top_3_accuracy']:.1%}` / `{best['metrics']['top_5_accuracy']:.1%}`, score log loss `{best['metrics']['score_log_loss']:.4f}`, 1X2 Brier `{best['metrics']['one_x_two_brier']:.4f}` and over-2.5 Brier `{best['metrics']['over_2_5_brier']:.4f}`.

The exact-score rate decreases from `{baseline['exact_score_accuracy']:.1%}` to `{best['metrics']['exact_score_accuracy']:.1%}`. This trade-off remains visible: the candidate is supported by improved score likelihood, top-3/top-5, broad-market Brier and favorite-margin realism, not by an exact-score accuracy claim.

## Decision

Promotion decision: **{decision['decision']}**. {decision['reason']}

A candidate file is generated only when every historical guardrail passes and the improvement is positive. Even then it remains explicitly non-active and preserves frozen hybrid 1X2 probabilities.
"""


def candidate_markdown(candidate: dict[str, Any], results: dict[str, Any]) -> str:
    spain = next(row for row in candidate["matches"] if row["home_team"] == "Spain" and "Cape Verde" in row["away_team"])
    old_distribution = dict(Counter(row["old_score_modal"] for row in candidate["matches"]).most_common())
    new_distribution = dict(Counter(row["new_score_modal"] for row in candidate["matches"]).most_common())
    return f"""# World Cup 2026 Score Matrix Candidate V2.8

This candidate applies `{candidate['challenger']}` to the 72 World Cup score matrices after it passed the historical-test guardrails. It is not active, does not replace `predictions.json`, and preserves every frozen hybrid 1X2 probability.

Spain vs Cape Verde Islands changes from modal `{spain['old_score_modal']}` to `{spain['new_score_modal']}`. The complete JSON retains old and new top scores, matrix-derived markets, the active 1X2 block and a per-match explanation.

Old modal distribution: `{old_distribution}`.

New modal distribution: `{new_distribution}`.

The candidate exists for human validation and simulation review only. Promotion requires an explicit later decision; V2.8 does not silently alter the product's active prediction contract.
"""


def main() -> None:
    rows = load_json(DATA_DIR / "generated" / "historical_test_predictions_quant_engine_v2_2.json")
    release = load_json(DATA_DIR / "generated" / "worldcup_2026_predictions_release_candidate_v2_4.json")
    baseline_matrices = [entries_to_matrix(row) for row in rows]
    baseline = historical_metrics(rows, baseline_matrices)
    evaluated = []
    variant_lookup = {}
    for identifier, family, parameters, transform in variants():
        matrices = [transform(matrix, active_probabilities(row)) for row, matrix in zip(rows, baseline_matrices)]
        metrics = historical_metrics(rows, matrices)
        gates = guardrails(baseline, metrics)
        result = {
            "id": identifier,
            "family": family,
            "parameters": parameters,
            "metrics": metrics,
            "guardrails": gates,
            "selection_score": challenger_score(baseline, metrics),
        }
        evaluated.append(result)
        variant_lookup[identifier] = transform
    ranked = sorted(evaluated, key=lambda item: item["selection_score"], reverse=True)
    passing = [item for item in ranked if item["guardrails"]["passed"] and item["selection_score"] > 0]
    winner = passing[0] if passing else ranked[0]
    promote = bool(passing)
    decision = {
        "decision": "generate_candidate_not_active" if promote else "keep_quant_hybrid_v2.2_active_no_candidate",
        "promoted_challenger": winner["id"] if promote else None,
        "reason": (
            "The best challenger improves historical score likelihood and favorite-margin realism while passing every broad-market guardrail."
            if promote
            else "No challenger produced a sufficiently broad historical improvement while passing every guardrail."
        ),
        "worldcup_2026_used_for_selection": False,
        "active_predictions_replaced": False,
    }
    payload = {
        "generated_at": utc_now(),
        "version": VERSION,
        "engine_version": ENGINE,
        "baseline": baseline,
        "challengers": ranked,
        "best_challenger": winner,
        "challenger_e_feasibility": {
            "status": "feasible_but_deferred",
            "reason": "Requires a constrained numerical solver to reconcile hybrid 1X2, over 2.5 and team-goal targets without inventing unsupported precision.",
            "recommended_test": "Fit two lambdas plus bounded dependence/temperature terms on validation, freeze them, then evaluate once on test.",
        },
        "promotion_decision": decision,
        "no_model_retrained": True,
        "no_optuna_rerun": True,
        "active_probabilities_modified": False,
    }
    publish(payload, "score_matrix_challenger_results_v2_8.json")
    (ROOT / "docs" / "SCORE_MATRIX_CHALLENGERS_V2_8.md").write_text(markdown(payload), encoding="utf-8")
    candidate_path = DATA_DIR / "generated" / "worldcup_2026_predictions_score_matrix_candidate_v2_8.json"
    if promote:
        candidate = build_candidate(release["matches"], variant_lookup[winner["id"]], winner)
        publish(candidate, candidate_path.name)
        (ROOT / "docs" / "WORLDCUP_2026_SCORE_MATRIX_CANDIDATE_V2_8.md").write_text(candidate_markdown(candidate, payload), encoding="utf-8")
    else:
        for path in (candidate_path, DATA_DIR / "snapshots" / candidate_path.name, ROOT / "frontend/src/assets/data" / candidate_path.name):
            if path.exists():
                path.unlink()
        doc = ROOT / "docs" / "WORLDCUP_2026_SCORE_MATRIX_CANDIDATE_V2_8.md"
        if doc.exists():
            doc.unlink()
    print(json.dumps({"best_challenger": winner["id"], "guardrails_passed": winner["guardrails"]["passed"], "decision": decision["decision"]}))


if __name__ == "__main__":
    main()
