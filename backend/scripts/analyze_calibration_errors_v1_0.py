"""Analyze V0.9 calibration errors without retraining or changing predictions."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.calibration.error_analysis import analyze_split, enrich_predictions
from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, utc_now, write_json

MODEL_VERSION = "calibrated_simple_poisson_v0.9"
ANALYSIS_VERSION = "v1.0"
PROMOTION_RECOMMENDATION = "do_not_promote_yet"


def publish(payload: dict[str, Any]) -> None:
    generated = DATA_DIR / "generated" / "calibration_error_analysis_v1_0.json"
    snapshot = DATA_DIR / "snapshots" / "calibration_error_analysis_v1_0.json"
    frontend = FRONTEND_DATA_DIR / "calibration_error_analysis_v1_0.json"
    write_json(payload, generated)
    snapshot.parent.mkdir(parents=True, exist_ok=True)
    frontend.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(generated, snapshot)
    shutil.copy2(generated, frontend)


def weakest_segment(splits: dict[str, Any], segment_name: str) -> tuple[str, str, dict[str, Any]]:
    candidates = [
        (split_name, name, metrics)
        for split_name, split in splits.items()
        for name, metrics in split[segment_name].items()
        if metrics["matches"] >= 5
    ]
    return max(candidates, key=lambda item: item[2]["log_loss_1x2"])


def derive_findings(splits: dict[str, Any], comparison: dict[str, Any]) -> tuple[list[str], list[str], list[str]]:
    findings: list[str] = []
    recommendations: list[str] = []
    hypotheses: list[str] = []
    for split_name, split in splits.items():
        draw = split["draw_bias"]
        findings.append(
            f"{split_name.title()}: actual draws are {draw['actual_draw_rate']:.1%}, while draw is the predicted "
            f"class in {draw['predicted_draw_class_rate']:.1%} of matches."
        )
        if draw["predicted_draw_class_rate"] + 0.05 < draw["actual_draw_rate"]:
            recommendations.append(
                f"Measure a draw-probability adjustment on {split_name}: draw-class predictions trail actual draws "
                f"by {(draw['actual_draw_rate'] - draw['predicted_draw_class_rate']):.1%}."
            )
            hypotheses.append("Test a fitted Dixon-Coles rho or explicit draw-calibration layer.")

        favorite = split["favorite_bias"]
        favorite_gap = favorite["favorite_win_actual_rate"] - favorite["average_favorite_probability"]
        findings.append(
            f"{split_name.title()}: favorites win {favorite['favorite_win_actual_rate']:.1%} of matches against "
            f"an average favorite probability of {favorite['average_favorite_probability']:.1%}; "
            f"upset rate is {favorite['upset_rate']:.1%}."
        )
        if abs(favorite_gap) >= 0.05:
            recommendations.append(
                f"Recalibrate favorite strength on {split_name}; realized favorite wins differ from average "
                f"favorite probability by {favorite_gap:+.1%}."
            )
            hypotheses.append("Test an Elo prior to distinguish team strength before applying Poisson rates.")

        high_goals = split["goal_total_segments"].get("4+ goals")
        if high_goals and high_goals["matches"]:
            predicted_total = high_goals["average_predicted_home_goals"] + high_goals["average_predicted_away_goals"]
            actual_total = high_goals["average_actual_home_goals"] + high_goals["average_actual_away_goals"]
            findings.append(
                f"{split_name.title()}: in {high_goals['matches']} matches with 4+ goals, the model predicts "
                f"{predicted_total:.2f} goals on average versus {actual_total:.2f} actual."
            )
            if actual_total - predicted_total >= 1:
                recommendations.append(
                    f"Investigate high-score underestimation on {split_name}; 4+ goal matches are underpredicted "
                    f"by {actual_total - predicted_total:.2f} goals on average."
                )
                hypotheses.append("Test recent-form attack features or a heavier-tailed score model for high-total matches.")

        populated_buckets = [
            (name, values)
            for name, values in split["confidence_buckets"].items()
            if values["matches"] >= 5 and values["calibration_gap"] is not None
        ]
        bucket_name, bucket = max(populated_buckets, key=lambda item: abs(item[1]["calibration_gap"]))
        findings.append(
            f"{split_name.title()}: largest eligible confidence calibration gap is {bucket['calibration_gap']:+.1%} "
            f"in bucket {bucket_name} (n={bucket['matches']})."
        )
        if abs(bucket["calibration_gap"]) >= 0.10:
            recommendations.append(
                f"Calibrate confidence bucket {bucket_name} on {split_name}; observed accuracy differs from "
                f"average confidence by {bucket['calibration_gap']:+.1%}."
            )
            hypotheses.append("Test a post-model probability calibration layer using validation data only.")

        teams = split["by_team"]
        findings.append(
            f"{split_name.title()}: {teams['low_sample_teams_count']} of {teams['teams_count']} teams have fewer "
            "than five matches in the split."
        )
        if teams["low_sample_teams_count"] > teams["teams_count"] / 2:
            recommendations.append(
                f"Treat team rankings on {split_name} cautiously and expand coverage: "
                f"{teams['low_sample_teams_count']}/{teams['teams_count']} teams have low split samples."
            )
        overestimated = teams["most_overestimated_teams"][0]
        underestimated = teams["most_underestimated_teams"][0]
        findings.append(
            f"{split_name.title()}: largest eligible team points overestimate is {overestimated['team']} "
            f"({overestimated['points_delta']:+.2f}); largest underestimate is {underestimated['team']} "
            f"({underestimated['points_delta']:+.2f})."
        )

    split_name, competition, metrics = weakest_segment(splits, "by_competition")
    findings.append(
        f"Worst competition segment with at least five matches is {competition} on {split_name} "
        f"(log loss {metrics['log_loss_1x2']:.4f}, accuracy {metrics['accuracy_1x2']:.1%}, n={metrics['matches']})."
    )
    recommendations.append(
        f"Audit competition effects beginning with {competition} on {split_name}; it has the highest eligible "
        f"competition log loss ({metrics['log_loss_1x2']:.4f})."
    )
    hypotheses.append("Test competition-aware intercepts or weighting because segment performance differs by competition.")

    split_name, season, metrics = weakest_segment(splits, "by_season")
    findings.append(
        f"Worst season segment with at least five matches is {season} on {split_name} "
        f"(log loss {metrics['log_loss_1x2']:.4f}, n={metrics['matches']})."
    )
    recommendations.append(
        f"Review temporal drift around season {season}; it has the highest eligible season log loss "
        f"({metrics['log_loss_1x2']:.4f})."
    )
    hypotheses.append("Test a chronological recent-form window or time decay to address observed season drift.")

    for split_name, split in splits.items():
        one_one = split["score_distribution"]
        findings.append(
            f"{split_name.title()}: 1-1 is modal in {one_one['modal_1_1_rate']:.1%} of predictions versus "
            f"{one_one['actual_1_1_rate']:.1%} of actual scores."
        )
        if one_one["modal_1_1_rate"] - one_one["actual_1_1_rate"] >= 0.10:
            recommendations.append(
                f"Reduce modal 1-1 concentration on {split_name}; predicted modal rate exceeds actual rate by "
                f"{one_one['modal_1_1_rate'] - one_one['actual_1_1_rate']:.1%}."
            )

    findings.append(
        f"V0.9 still improves test log loss by {comparison['test']['delta']['log_loss_1x2']:.4f} and test "
        f"Brier by {comparison['test']['delta']['brier_score_1x2']:.4f} versus the neutral prototype."
    )
    recommendations.append("Keep promotion recommendation do_not_promote_yet until a second challenger passes the same splits.")
    hypotheses.append("Expand history for teams repeatedly flagged with low split sample sizes before tuning team parameters.")
    return list(dict.fromkeys(findings)), list(dict.fromkeys(recommendations)), list(dict.fromkeys(hypotheses))


def table_rows(segments: dict[str, Any]) -> str:
    return "\n".join(
        f"| {name} | {metrics['matches']} | {metrics['accuracy_1x2']:.1%} | "
        f"{metrics['log_loss_1x2']:.4f} | {metrics['brier_score_1x2']:.4f} |"
        for name, metrics in segments.items()
    )


def render_report(analysis: dict[str, Any]) -> str:
    sections = []
    for split_name, split in analysis["splits"].items():
        worst = split["worst_log_loss_matches"][0]
        worst_three = ", ".join(
            f"`{item['home_team']}–{item['away_team']}` ({item['actual_score']}, {item['log_loss']:.3f})"
            for item in split["worst_log_loss_matches"][:3]
        )
        high_confidence_three = ", ".join(
            f"`{item['home_team']}–{item['away_team']}` ({item['prediction_confidence']:.1%})"
            for item in split["high_confidence_wrong_predictions"][:3]
        ) or "none"
        confidence = split["confidence_buckets"]
        confidence_lines = ", ".join(
            f"{name}: n={values['matches']}, gap={values['calibration_gap']:+.3f}"
            for name, values in confidence.items()
            if values["matches"]
        )
        sections.append(
            f"""## {split_name.title()} results

- Matches: `{split['summary']['matches']}`
- Accuracy 1X2: `{split['summary']['accuracy_1x2']:.1%}`
- Log loss: `{split['summary']['log_loss_1x2']:.4f}`
- Brier: `{split['summary']['brier_score_1x2']:.4f}`
- Draw actual / predicted class: `{split['draw_bias']['actual_draw_rate']:.1%}` / `{split['draw_bias']['predicted_draw_class_rate']:.1%}`
- Favorite actual win / average probability: `{split['favorite_bias']['favorite_win_actual_rate']:.1%}` / `{split['favorite_bias']['average_favorite_probability']:.1%}`
- Worst log-loss match: `{worst['home_team']}–{worst['away_team']}` (`{worst['actual_score']}`, log loss `{worst['log_loss']:.4f}`)
- Confidence buckets: {confidence_lines}

### Competition segments

| Competition | Matches | Accuracy | Log loss | Brier |
|---|---:|---:|---:|---:|
{table_rows(split['by_competition'])}

### Season segments

| Season | Matches | Accuracy | Log loss | Brier |
|---|---:|---:|---:|---:|
{table_rows(split['by_season'])}

### Team and score diagnostics

- Worst eligible team by log loss: `{split['by_team']['worst_teams_by_log_loss'][0]['team']}` (`{split['by_team']['worst_teams_by_log_loss'][0]['avg_log_loss']:.4f}`)
- Low-sample teams: `{split['by_team']['low_sample_teams_count']}`
- Modal 1-1 / actual 1-1: `{split['score_distribution']['modal_1_1_rate']:.1%}` / `{split['score_distribution']['actual_1_1_rate']:.1%}`
- High-confidence wrong predictions: `{len(split['high_confidence_wrong_predictions'])}`
- Unexpected upsets retained: `{len(split['unexpected_upsets'])}`
- Unexpected draws retained: `{len(split['unexpected_draws'])}`

### Problematic matches

- Three worst log-loss matches: {worst_three}
- Highest-confidence wrong predictions: {high_confidence_three}
"""
        )
    return f"""# Calibration Error Analysis V1.0

## Objective and sources

V1.0 diagnoses the fixed `calibrated_simple_poisson_v0.9` predictions on the
chronological validation and test splits. It reads existing historical
predictions, matches and the prototype comparison only. No model is retrained,
no World Cup 2026 prediction is regenerated, and promotion remains blocked.

{chr(10).join(sections)}

## Overall findings

{chr(10).join(f"- {item}" for item in analysis['overall_findings'])}

## Priority recommendations

{chr(10).join(f"- {item}" for item in analysis['priority_recommendations'])}

## V1.1 challenger hypotheses

{chr(10).join(f"- {item}" for item in analysis['next_challenger_hypotheses'])}

## Decision

- Promotion recommendation: `{analysis['promotion_recommendation']}`
- Model retrained: `false`
- Active engine changed: `false`
- World Cup 2026 predictions changed: `false`

The next step is **V1.1 — Second Calibration Challenger Design**, after human
review of the full JSON rankings and problematic matches.
"""


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", choices=("validation", "test"))
    parser.add_argument("--top-n", type=int, default=20)
    args = parser.parse_args(argv)
    if args.top_n <= 0:
        raise ValueError("--top-n must be positive")

    split_names = (args.split,) if args.split else ("validation", "test")
    splits = {}
    for split_name in split_names:
        predictions = load_json(DATA_DIR / "generated" / f"historical_{split_name}_predictions_calibrated_v0_9.json")
        matches = load_json(DATA_DIR / "normalized" / f"historical_{split_name}_matches.json")
        records = enrich_predictions(predictions, matches, split_name)
        splits[split_name] = analyze_split(records, args.top_n)

    comparison = load_json(DATA_DIR / "generated" / "calibrated_vs_prototype_comparison_v0_9.json")
    findings, recommendations, hypotheses = derive_findings(splits, comparison)
    analysis = {
        "generated_at": utc_now(),
        "model_version": MODEL_VERSION,
        "analysis_version": ANALYSIS_VERSION,
        "promotion_recommendation": PROMOTION_RECOMMENDATION,
        "model_retrained": False,
        "active_engine_changed": False,
        "world_cup_2026_predictions_changed": False,
        "sources": [
            "historical_validation_predictions_calibrated_v0_9.json",
            "historical_test_predictions_calibrated_v0_9.json",
            "historical_validation_matches.json",
            "historical_test_matches.json",
            "calibrated_vs_prototype_comparison_v0_9.json",
        ],
        "splits": splits,
        "overall_findings": findings,
        "priority_recommendations": recommendations,
        "next_challenger_hypotheses": hypotheses,
    }
    publish(analysis)
    (PROJECT_ROOT / "docs" / "CALIBRATION_ERROR_ANALYSIS_V1_0.md").write_text(render_report(analysis), encoding="utf-8")
    print(f"Analyzed calibration errors for {', '.join(split_names)}; promotion={PROMOTION_RECOMMENDATION}.")


if __name__ == "__main__":
    main()
