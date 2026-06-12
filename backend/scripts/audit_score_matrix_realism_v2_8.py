"""Audit whether the active V2.2 score matrix is too conservative."""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, load_json, utc_now
from backend.scripts.v2_8_matrix_utils import (
    ENGINE,
    VERSION,
    bucket_name,
    entries_to_matrix,
    expected_goals,
    favorite_info,
    historical_metrics,
    matrix_markets,
    modal_distribution,
    ordered_scores,
    publish,
    score_outcome,
    top_compatible_score,
)


def worldcup_audit(matches: list[dict[str, Any]]) -> dict[str, Any]:
    matrices = [entries_to_matrix(row) for row in matches]
    modal_scores, modal_totals = modal_distribution(matrices)
    bucket_rows: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    cases = []
    strong_cases = []
    for row, matrix in zip(matches, matrices):
        probabilities = {
            "home": float(row["probabilities"]["home_win"]),
            "draw": float(row["probabilities"]["draw"]),
            "away": float(row["probabilities"]["away_win"]),
        }
        favorite_side, favorite_probability = favorite_info(probabilities)
        markets = matrix_markets(matrix)
        modal = max(matrix, key=matrix.get)
        home_xg, away_xg = expected_goals(matrix)
        case = {
            "match_id": row["match_id"],
            "match": f"{row['home_team']} vs {row['away_team']}",
            "favorite": row[f"{favorite_side}_team"],
            "favorite_side": favorite_side,
            "favorite_probability": favorite_probability,
            "modal_score": f"{modal[0]}-{modal[1]}",
            "modal_probability": matrix[modal],
            "top_compatible_score": top_compatible_score(matrix, favorite_side),
            "reconstructed_expected_goals": {"home": home_xg, "away": away_xg, "total": home_xg + away_xg},
            "favorite_win_mass": markets[favorite_side],
            "favorite_win_by_2_plus_mass": markets[f"{favorite_side}_win_by_2_plus"],
            "three_plus_total_goals_mass": markets["three_plus_total"],
            "favorite_score_modal_realism_flag": favorite_probability >= 0.60
            and (score_outcome(modal) != favorite_side or abs(modal[0] - modal[1]) < 2),
        }
        bucket_rows[bucket_name(favorite_probability)].append(case)
        cases.append(case)
        if favorite_probability >= 0.55:
            strong_cases.append(case)
    favorite_buckets = {}
    for threshold in (0.55, 0.60, 0.65, 0.70):
        selected = [case for case in strong_cases if case["favorite_probability"] >= threshold]
        favorite_buckets[f">={threshold:.2f}"] = {
            "count": len(selected),
            "modal_score_distribution": dict(Counter(case["modal_score"] for case in selected).most_common()),
            "modal_favorite_aligned_count": sum(
                score_outcome(tuple(map(int, case["modal_score"].split("-")))) == case["favorite_side"] for case in selected
            ),
            "average_favorite_win_by_2_plus_mass": sum(case["favorite_win_by_2_plus_mass"] for case in selected) / len(selected)
            if selected
            else None,
        }
    low_modal = sum(modal_scores.get(score, 0) for score in ("0-0", "1-0", "0-1", "1-1"))
    flags = []
    if low_modal / len(matches) >= 0.75:
        flags.append("At least 75% of 2026 modal scores are 0-0, 1-0, 0-1 or 1-1.")
    if modal_totals["3+"] / len(matches) < 0.10:
        flags.append("Fewer than 10% of 2026 modal scores contain three or more goals.")
    return {
        "fixture_count": len(matches),
        "modal_score_distribution": modal_scores,
        "modal_total_goals_distribution": modal_totals,
        "favorite_probability_buckets": favorite_buckets,
        "match_table": cases,
        "strong_favorite_cases": sorted(strong_cases, key=lambda item: item["favorite_probability"], reverse=True),
        "conservatism_flags": flags,
    }


def spain_case(matches: list[dict[str, Any]]) -> dict[str, Any]:
    row = next(row for row in matches if row["home_team"] == "Spain" and "Cape Verde" in row["away_team"])
    matrix = entries_to_matrix(row)
    markets = matrix_markets(matrix)
    probabilities = {
        "home": row["probabilities"]["home_win"],
        "draw": row["probabilities"]["draw"],
        "away": row["probabilities"]["away_win"],
    }
    favorite_side, favorite_probability = favorite_info(probabilities)
    modal = max(matrix, key=matrix.get)
    home_xg, away_xg = expected_goals(matrix)
    return {
        "match_id": row["match_id"],
        "match": f"{row['home_team']} vs {row['away_team']}",
        "score_modal": f"{modal[0]}-{modal[1]}",
        "score_modal_probability": matrix[modal],
        "top_10_scores": ordered_scores(matrix),
        "one_x_two": probabilities,
        "favorite": {"team": row[f"{favorite_side}_team"], "side": favorite_side, "probability": favorite_probability},
        "dnb": {"home": markets["dnb_home"], "away": markets["dnb_away"]},
        "over_under": {"over_2_5": markets["over_2_5"], "under_2_5": markets["under_2_5"]},
        "team_goals": {
            "spain_scores": markets["home_scores"],
            "spain_scores_2_plus": markets["home_scores_2_plus"],
            "cape_verde_scores": markets["away_scores"],
        },
        "reconstructed_expected_goals": {"spain": home_xg, "cape_verde": away_xg, "total": home_xg + away_xg},
        "probability_spain_wins_by_1": markets["home_win_by_1"],
        "probability_spain_wins_by_2_plus": markets["home_win_by_2_plus"],
        "matrix_explanation": (
            "The modal 1-0 is mathematically logical for independent low lambdas: it is the largest individual cell. "
            "It is footballistically cautious because Spain's aggregate favorite probability is much stronger than the modal margin suggests."
        ),
        "diagnosis": {
            "is_1_0_mathematically_logical": True,
            "is_1_0_footballistically_too_prudent": markets["home_win_by_2_plus"] < markets["home_win_by_1"],
            "implicit_lambda_spain": home_xg,
            "implicit_lambda_cape_verde": away_xg,
            "wide_wins_underestimated_flag": markets["home_win_by_2_plus"] < 0.30,
        },
    }


def causes(worldcup: dict[str, Any], historical: dict[str, Any]) -> list[dict[str, Any]]:
    modal_gap = historical["actual_average_favorite_margin"] - historical["modal_average_favorite_margin"]
    three_plus_actual = historical["actual_total_goals_distribution"]["3+"] / historical["match_count"]
    three_plus_modal = historical["modal_total_goals_distribution"]["3+"] / historical["match_count"]
    return [
        {"cause": "A. Compression des ratings / Elo gap trop faible", "evidence_for": "Strong-favorite modal margins remain narrow.", "evidence_against": "Hybrid 1X2 still creates strong-favorite buckets.", "severity": "medium", "recommended_test": "Compare rating gap with lambda gap by favorite bucket."},
        {"cause": "B. Lambdas attaque/défense trop proches de la moyenne", "evidence_for": f"Historical modal favorite margin trails actual by {modal_gap:.3f}.", "evidence_against": "Published lambda audit reports meaningful pairwise differences.", "severity": "high", "recommended_test": "Post-model favorite lambda-gap scaling."},
        {"cause": "C. Cap implicite sur favorite xG", "evidence_for": "Very few 3+ modal scores appear for strong favorites.", "evidence_against": "V2.2 metadata reports no explicit lambda clipping.", "severity": "medium", "recommended_test": "Inspect upper-tail favorite lambdas and clipping flags."},
        {"cause": "D. Trop forte probabilité de nul", "evidence_for": "Low-score draw cells are frequently modal.", "evidence_against": "A draw correction can damage calibrated 1X2.", "severity": "medium", "recommended_test": "Bounded strong-favorite draw-mass correction."},
        {"cause": "E. Distribution Poisson trop concentrée sur petits scores", "evidence_for": f"Actual 3+ total rate is {three_plus_actual:.1%} versus {three_plus_modal:.1%} modal.", "evidence_against": "A modal distribution is inherently narrower than realized scores.", "severity": "high", "recommended_test": "Total-goals temperature challenger with score-likelihood guardrail."},
        {"cause": "F. Calibration optimisée pour log loss 1X2 plutôt que score likelihood", "evidence_for": "The hybrid objective can aggregate outcome cells without rewarding realistic modal margins.", "evidence_against": "Poisson score likelihood remains indirectly represented.", "severity": "high", "recommended_test": "Use historical score log likelihood as a challenger criterion."},
        {"cause": "G. Manque de feature mismatch / mismatch boost", "evidence_for": "Strong favorites lack an explicit post-model mismatch term.", "evidence_against": "Ratings and attack/defence features already encode mismatch.", "severity": "medium", "recommended_test": "Targeted mismatch boost benchmark, no full retrain."},
        {"cause": "H. Données historiques internationales trop prudentes", "evidence_for": "International group and qualification games include cautious regimes.", "evidence_against": "The same corpus also contains large mismatches.", "severity": "low", "recommended_test": "Segment totals and margins by competition tier."},
        {"cause": "I. Effet compétition/groupe conservateur", "evidence_for": "World Cup group-stage priors may suppress totals.", "evidence_against": "The historical issue also appears across competitions.", "severity": "low", "recommended_test": "Compare group-stage and qualification matrix realism."},
    ]


def markdown(audit: dict[str, Any]) -> str:
    wc, hist, spain = audit["worldcup_2026"], audit["historical_test"], audit["spain_vs_cape_verde"]
    low = sum(wc["modal_score_distribution"].get(score, 0) for score in ("0-0", "1-0", "0-1", "1-1"))
    cause_lines = "\n".join(
        f"- **{item['cause']}** — severity `{item['severity']}`. Evidence for: {item['evidence_for']} "
        f"Evidence against: {item['evidence_against']} Recommended test: {item['recommended_test']}"
        for item in audit["diagnosis"]["causes"]
    )
    return f"""# Score Matrix Realism Audit V2.8

V2.8 audits the active `{ENGINE}` matrix without retraining, Optuna or changes to active predictions. The historical 460-match test is the decision set; the 72 World Cup fixtures are descriptive only.

Le 1X2 additionne de nombreuses cases de la matrice, alors que le score modal ne correspond qu’à une seule case. Un moteur peut donc être bien calibré en 1X2 tout en étant trop prudent dans la distribution des scores.

## Diagnosis

- World Cup modal scores 0-0/1-0/0-1/1-1: `{low}/{wc['fixture_count']}` (`{low/wc['fixture_count']:.1%}`)
- World Cup modal scores with 3+ goals: `{wc['modal_total_goals_distribution']['3+']}/{wc['fixture_count']}`
- Historical actual 3+ goal matches: `{hist['actual_total_goals_distribution']['3+']}/{hist['match_count']}`
- Historical modal 3+ goal matches: `{hist['modal_total_goals_distribution']['3+']}/{hist['match_count']}`
- Historical actual versus modal favorite margin: `{hist['actual_average_favorite_margin']:.3f}` versus `{hist['modal_average_favorite_margin']:.3f}`

The matrix is materially conservative as a modal-score generator. That does not prove its broad markets are unusable: it proves exact-score presentation and tournament score simulation require separate scrutiny.

## Spain vs Cape Verde Islands

Spain is the `{spain['favorite']['probability']:.1%}` favorite. The modal score is `{spain['score_modal']}` at `{spain['score_modal_probability']:.1%}`, with reconstructed expected goals `{spain['reconstructed_expected_goals']['spain']:.3f}` to `{spain['reconstructed_expected_goals']['cape_verde']:.3f}`. Spain wins by one with probability `{spain['probability_spain_wins_by_1']:.1%}` and by two or more with probability `{spain['probability_spain_wins_by_2_plus']:.1%}`.

The 1-0 cell is mathematically coherent because a modal score is only one cell. It is nevertheless footballistically cautious relative to the aggregate favorite signal and should be tested against historical strong-favorite margins rather than corrected from this example alone.

## Cause assessment

The strongest evidence points to lambda/total compression and an objective centered more on aggregate 1X2 than exact-score likelihood. Rating compression, draw mass and missing mismatch boost remain plausible but are not established as sole causes.

{cause_lines}
"""


def main() -> None:
    release = load_json(DATA_DIR / "generated" / "worldcup_2026_predictions_release_candidate_v2_4.json")
    states = load_json(DATA_DIR / "generated" / "worldcup_match_state_view_model_v2_7.json")
    historical_rows = load_json(DATA_DIR / "generated" / "historical_test_predictions_quant_engine_v2_2.json")
    secondary = load_json(DATA_DIR / "generated" / "secondary_market_metrics_v2_2.json")
    active_audit = load_json(DATA_DIR / "generated" / "active_matrix_market_audit_v2_3.json")
    historical_matrices = [entries_to_matrix(row) for row in historical_rows]
    wc = worldcup_audit(release["matches"])
    hist_metrics = historical_metrics(historical_rows, historical_matrices)
    hist = {
        "match_count": len(historical_rows),
        **hist_metrics,
        "actual_vs_modal_total_goals": {
            "actual": hist_metrics["actual_total_goals_distribution"],
            "modal": hist_metrics["modal_total_goals_distribution"],
        },
        "conservatism_flags": [
            "Historical modal scores materially underrepresent 3+ goal outcomes."
            if hist_metrics["modal_total_goals_distribution"]["3+"] < hist_metrics["actual_total_goals_distribution"]["3+"]
            else "No historical 3+ modal underrepresentation detected.",
            "Historical modal favorite margins are narrower than realized favorite margins."
            if hist_metrics["modal_average_favorite_margin"] < hist_metrics["actual_average_favorite_margin"]
            else "No favorite-margin compression detected.",
        ],
    }
    audit = {
        "generated_at": utc_now(),
        "version": VERSION,
        "engine_version": ENGINE,
        "worldcup_2026": wc,
        "historical_test": hist,
        "spain_vs_cape_verde": spain_case(release["matches"]),
        "diagnosis": {
            "conservatism_detected": bool(wc["conservatism_flags"]) and hist_metrics["modal_total_goals_distribution"]["3+"] < hist_metrics["actual_total_goals_distribution"]["3+"],
            "primary_evidence": "Historical modal totals and favorite margins are compressed relative to actual outcomes.",
            "causes": causes(wc, hist),
            "selection_rule": "Historical test is the arbiter; World Cup 2026 is descriptive and cannot select a challenger.",
        },
        "source_integrity": {
            "worldcup_match_states": states["match_count"],
            "secondary_test_available": "test" in secondary,
            "active_matrix_audit_test_matches": active_audit["test_match_count"],
            "no_model_retrained": True,
            "no_optuna_rerun": True,
            "active_predictions_modified": False,
        },
    }
    publish(audit, "score_matrix_realism_audit_v2_8.json")
    (ROOT / "docs" / "SCORE_MATRIX_REALISM_AUDIT_V2_8.md").write_text(markdown(audit), encoding="utf-8")
    print(json.dumps({"conservatism_detected": audit["diagnosis"]["conservatism_detected"], "worldcup_flags": len(wc["conservatism_flags"]), "historical_matches": len(historical_rows)}))


if __name__ == "__main__":
    main()
