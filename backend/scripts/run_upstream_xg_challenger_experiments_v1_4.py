"""Run isolated upstream xG challengers with validation-only parameter selection."""

from __future__ import annotations

import copy
import shutil
import sys
from collections import Counter
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.calibration.upstream_xg_challengers import (
    BASE_MODEL_VERSION,
    COMPETITION_MODEL_VERSION,
    COMPETITION_WEIGHT_GRID,
    ELO_DIAGNOSTIC_MODEL_VERSION,
    ELO_DIAGNOSTIC_PARAMS,
    LOW_SAMPLE_GRID,
    LOW_SAMPLE_MODEL_VERSION,
    TIME_DECAY_HALF_LIVES,
    TIME_DECAY_MODEL_VERSION,
    WeightedSimplePoisson,
    apply_elo_prior,
    competition_weight,
    evaluate_metrics,
    guardrails,
    metric_deltas,
    parse_date,
    predict_time_decay,
    predict_with_model,
    recent_coverage_by_team,
    segment_metrics,
    train_team_counts,
)
from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, utc_now, write_json

VERSION = "v1.4"
PROMOTION_RECOMMENDATION = "do_not_promote_yet"


def publish(payload: dict[str, Any]) -> None:
    generated = DATA_DIR / "generated" / "upstream_xg_challenger_results_v1_4.json"
    snapshot = DATA_DIR / "snapshots" / "upstream_xg_challenger_results_v1_4.json"
    frontend = FRONTEND_DATA_DIR / "upstream_xg_challenger_results_v1_4.json"
    write_json(payload, generated)
    snapshot.parent.mkdir(parents=True, exist_ok=True)
    frontend.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(generated, snapshot)
    shutil.copy2(generated, frontend)


def assert_historical_splits(splits: dict[str, list[dict[str, Any]]]) -> None:
    if any(match.get("season") == 2026 or match.get("is_future_fixture") for matches in splits.values() for match in matches):
        raise ValueError("Future or 2026 fixtures must not enter V1.4")
    for earlier, later in (("train", "validation"), ("validation", "test")):
        if max(match["kickoff_at"] for match in splits[earlier]) > min(match["kickoff_at"] for match in splits[later]):
            raise ValueError(f"{earlier} and {later} are not chronological")


def enrich_baseline(
    predictions: list[dict[str, Any]], matches: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    by_id = {str(match["match_id"]): match for match in matches}
    enriched = []
    for source in predictions:
        prediction = copy.deepcopy(source)
        match = by_id[str(prediction["match_id"])]
        prediction.update(
            {
                "competition_tier": match.get("competition_tier"),
                "competition_family": match.get("competition_family"),
                "season": match["season"],
            }
        )
        enriched.append(prediction)
    return enriched


def trial(
    params: dict[str, Any],
    predictions: list[dict[str, Any]],
    model_version: str,
    baseline_validation: dict[str, Any],
    selection_guardrails: dict[str, bool] | None = None,
    diagnostics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    metrics = evaluate_metrics(predictions, "validation", model_version)
    guards = selection_guardrails or {
        "brier_not_materially_worse": metrics["brier_score_1x2"] <= baseline_validation["brier_score_1x2"] + 0.01,
    }
    return {"params": params, "metrics": metrics, "selection_guardrails": guards, "diagnostics": diagnostics or {}}


def select_trial(trials: list[dict[str, Any]]) -> dict[str, Any]:
    eligible = [item for item in trials if all(item["selection_guardrails"].values())]
    return min(eligible or trials, key=lambda item: item["metrics"]["log_loss_1x2"])


def challenger_result(
    model_version: str,
    selected_params: dict[str, Any],
    trials: list[dict[str, Any]],
    predictions: dict[str, list[dict[str, Any]]],
    baseline: dict[str, dict[str, Any]],
    counts: Counter[str],
    baseline_segments: dict[str, Any],
    notes: list[str],
    temporal_leakage_risk: bool = False,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    metrics = {split: evaluate_metrics(items, split, model_version) for split, items in predictions.items()}
    segments = {
        split: segment_metrics(items, split, model_version, counts) for split, items in predictions.items()
    }
    gates = guardrails(
        metrics["validation"],
        metrics["test"],
        baseline["validation"],
        baseline["test"],
        segments,
        baseline_segments,
        temporal_leakage_risk,
    )
    passed = all(gates.values())
    result = {
        "model_version": model_version,
        "selected_params": selected_params,
        "selection_basis": "minimum validation log loss among candidates passing validation-only selection guardrails",
        "validation_trials": trials,
        "validation": metrics["validation"],
        "test": metrics["test"],
        "delta_vs_v0_9": {
            split: metric_deltas(metrics[split], baseline[split]) for split in ("validation", "test")
        },
        "segments": segments,
        "guardrails": gates,
        "passed_guardrails": passed,
        "promotion_eligible": False,
        "candidate_for_future_combination": passed and not temporal_leakage_risk,
        "temporal_leakage_risk": temporal_leakage_risk,
        "notes": notes,
    }
    result.update(extra or {})
    return result


def build_elo_ratings(ratings: list[dict[str, Any]], identity_map: list[dict[str, Any]]) -> dict[str, float]:
    by_name = {str(item["team_name"]): float(item["elo_rating"]) for item in ratings}
    resolved = dict(by_name)
    for item in identity_map:
        elo_name = item.get("elo", {}).get("team_name")
        rating = by_name.get(str(elo_name)) if elo_name else None
        for name in (item.get("display_name"), item.get("api_football", {}).get("name")):
            if name and rating is not None:
                resolved[str(name)] = rating
    return resolved


def render_report(results: dict[str, Any]) -> str:
    def section(key: str, title: str) -> str:
        item = results["challengers"][key]
        validation, test, delta = item["validation"], item["test"], item["delta_vs_v0_9"]["test"]
        failed = ", ".join(name for name, passed in item["guardrails"].items() if not passed) or "none"
        return f"""## {title}

- Selected parameters: `{item['selected_params']}`
- Validation log loss / Brier: `{validation['log_loss_1x2']:.4f}` / `{validation['brier_score_1x2']:.4f}`
- Test log loss / Brier: `{test['log_loss_1x2']:.4f}` / `{test['brier_score_1x2']:.4f}`
- Test draw / favorite calibration gaps: `{test['draw_calibration_gap']:+.4f}` / `{test['favorite_calibration_gap']:+.4f}`
- Test modal 1-1 / high-confidence wrong: `{test['modal_1_1_rate']:.1%}` / `{test['high_confidence_wrong_predictions']}`
- Test delta vs V0.9 log loss / Brier: `{delta['log_loss_1x2']:+.4f}` / `{delta['brier_score_1x2']:+.4f}`
- Passed all guardrails: `{str(item['passed_guardrails']).lower()}`
- Candidate for future combination: `{str(item['candidate_for_future_combination']).lower()}`
- Failed guardrails: {failed}

The JSON artifact retains every validation trial and the required competition,
tier, season and low-sample segment reports.
"""

    ranking = "\n".join(
        f"{index}. `{item['challenger']}`: test log loss `{item['test_log_loss_1x2']:.4f}`, "
        f"Brier `{item['test_brier_score_1x2']:.4f}`, combination candidate "
        f"`{str(item['candidate_for_future_combination']).lower()}`"
        for index, item in enumerate(results["ranking"], start=1)
    )
    elo = results["challengers"]["elo_prior_xg_diagnostic"]
    return f"""# Upstream xG Isolated Challenger Results V1.4

## Objective and boundaries

V1.4 implements isolated upstream xG challengers after V1.2 showed that
post-probability corrections were insufficient and V1.3 validated the upstream
direction. Parameters are selected on validation only and test is used only
after selection. The active engine and World Cup 2026 predictions are
unchanged; no combined challenger is implemented and no model is promoted.

## Methods and tested parameters

- Competition-Weighted xG fits weighted V0.9-form team strengths on train only
  using the three documented competition-weight grids. No friendly rows exist,
  so `friendly_weight` is not evaluable.
- Time-Decay xG fits train-only weights relative to every predicted match and
  tests half-lives `12`, `24`, `36`, and `48` months.
- Low-Sample Fallback xG tests thresholds/smoothing `(5, 8)`, `(8, 12)`, and
  `(10, 16)`.
- Elo-Prior xG uses the current/static Elo snapshot only as a non-promotable
  diagnostic with explicit temporal leakage risk.

{section('competition_weighted_xg', 'Competition-Weighted xG')}
{section('time_decay_xg', 'Time-Decay xG')}
{section('low_sample_fallback_xg', 'Low-Sample Fallback xG')}
## Elo-Prior xG diagnostic

- Executed: `true`
- Temporal leakage risk: `{str(elo['temporal_leakage_risk']).lower()}`
- Promotion eligible: `{str(elo['promotion_eligible']).lower()}`
- Candidate for future combination: `{str(elo['candidate_for_future_combination']).lower()}`
- Test log loss / Brier: `{elo['test']['log_loss_1x2']:.4f}` / `{elo['test']['brier_score_1x2']:.4f}`

Current/static Elo snapshot used on historical matches. This is temporal
leakage risk evidence and cannot support promotion.

## Ranking and conclusion

{ranking}

{chr(10).join(f"- {item}" for item in results['recommendations'])}

## Decision

- Promotion recommendation: `{results['promotion_recommendation']}`
- Combined challenger implemented: `false`
- Active engine replaced: `false`
- World Cup 2026 predictions modified: `false`

The full JSON retains validation trials, V0.9 deltas, segment metrics,
effective-weight diagnostics and guardrails. Human review is required before
any later experiment.
"""


def main() -> None:
    normalized, generated = DATA_DIR / "normalized", DATA_DIR / "generated"
    splits = {split: load_json(normalized / f"historical_{split}_matches.json") for split in ("train", "validation", "test")}
    assert_historical_splits(splits)
    train, validation, test = splits["train"], splits["validation"], splits["test"]
    counts = train_team_counts(train)

    baseline_predictions = {
        split: enrich_baseline(
            load_json(generated / f"historical_{split}_predictions_calibrated_v0_9.json"), splits[split]
        )
        for split in ("validation", "test")
    }
    baseline = {
        split: evaluate_metrics(predictions, split, BASE_MODEL_VERSION)
        for split, predictions in baseline_predictions.items()
    }
    source_v0_9_reports = {
        split: load_json(generated / f"calibration_{split}_report_v0_9.json") for split in ("validation", "test")
    }
    baseline_segments = {
        split: segment_metrics(predictions, split, BASE_MODEL_VERSION, counts)
        for split, predictions in baseline_predictions.items()
    }

    competition_trials = []
    for params in COMPETITION_WEIGHT_GRID:
        weights = [competition_weight(match, params) for match in train]
        model = WeightedSimplePoisson().fit(train, weights)
        predictions = predict_with_model(validation, model, COMPETITION_MODEL_VERSION, params)
        competition_trials.append(
            trial(
                params,
                predictions,
                COMPETITION_MODEL_VERSION,
                baseline["validation"],
                diagnostics={
                    "effective_sample_weight": model.effective_sample_weight,
                    "effective_sample_size": model.effective_sample_size,
                },
            )
        )
    competition_selected = select_trial(competition_trials)
    competition_params = competition_selected["params"]
    competition_weights = [competition_weight(match, competition_params) for match in train]
    competition_model = WeightedSimplePoisson().fit(train, competition_weights)
    competition_predictions = {
        split: predict_with_model(matches, competition_model, COMPETITION_MODEL_VERSION, competition_params)
        for split, matches in (("validation", validation), ("test", test))
    }

    time_trials = []
    time_validation_predictions: dict[int, list[dict[str, Any]]] = {}
    for half_life in TIME_DECAY_HALF_LIVES:
        predictions, diagnostics = predict_time_decay(train, validation, half_life)
        time_validation_predictions[half_life] = predictions
        time_trials.append(
            trial({"half_life_months": half_life}, predictions, TIME_DECAY_MODEL_VERSION, baseline["validation"], diagnostics=diagnostics)
        )
    time_selected = select_trial(time_trials)
    half_life = int(time_selected["params"]["half_life_months"])
    time_test_predictions, time_test_diagnostics = predict_time_decay(train, test, half_life)
    time_predictions = {"validation": time_validation_predictions[half_life], "test": time_test_predictions}

    low_trials = []
    for params in LOW_SAMPLE_GRID:
        model = WeightedSimplePoisson(
            int(params["low_sample_threshold"]), float(params["extra_smoothing_weight"])
        ).fit(train)
        predictions = predict_with_model(validation, model, LOW_SAMPLE_MODEL_VERSION, params)
        metrics = evaluate_metrics(predictions, "validation", LOW_SAMPLE_MODEL_VERSION)
        low_trials.append(
            trial(
                params,
                predictions,
                LOW_SAMPLE_MODEL_VERSION,
                baseline["validation"],
                {
                    "brier_not_materially_worse": metrics["brier_score_1x2"] <= baseline["validation"]["brier_score_1x2"] + 0.01,
                    "high_confidence_wrong_not_increased": metrics["high_confidence_wrong_predictions"]
                    <= baseline["validation"]["high_confidence_wrong_predictions"],
                },
                {"low_sample_teams_count": sum(count < int(params["low_sample_threshold"]) for count in counts.values())},
            )
        )
    low_selected = select_trial(low_trials)
    low_params = low_selected["params"]
    low_model = WeightedSimplePoisson(
        int(low_params["low_sample_threshold"]), float(low_params["extra_smoothing_weight"])
    ).fit(train)
    low_predictions = {
        split: predict_with_model(matches, low_model, LOW_SAMPLE_MODEL_VERSION, low_params)
        for split, matches in (("validation", validation), ("test", test))
    }

    ratings = load_json(normalized / "team_ratings.json")
    identity_map = load_json(DATA_DIR / "mappings" / "team_identity_map.json")
    elo_ratings = build_elo_ratings(ratings, identity_map)
    elo_model = WeightedSimplePoisson().fit(train)
    elo_predictions = {
        split: apply_elo_prior(matches, elo_model, elo_ratings)
        for split, matches in (("validation", validation), ("test", test))
    }

    prediction_sets = {
        "competition_weighted_xg": competition_predictions,
        "time_decay_xg": time_predictions,
        "low_sample_fallback_xg": low_predictions,
        "elo_prior_xg_diagnostic": elo_predictions,
    }
    filenames = {
        "competition_weighted_xg": "competition_weighted_xg_v1_4",
        "time_decay_xg": "time_decay_xg_v1_4",
        "low_sample_fallback_xg": "low_sample_fallback_xg_v1_4",
        "elo_prior_xg_diagnostic": "elo_prior_xg_v1_4_diagnostic",
    }
    for key, predictions_by_split in prediction_sets.items():
        for split, predictions in predictions_by_split.items():
            write_json(predictions, generated / f"historical_{split}_predictions_{filenames[key]}.json")

    challengers = {
        "competition_weighted_xg": challenger_result(
            COMPETITION_MODEL_VERSION,
            competition_params,
            competition_trials,
            competition_predictions,
            baseline,
            counts,
            baseline_segments,
            ["Friendly weight is not evaluable because no friendly rows are present."],
            extra={
                "effective_sample_weights": {
                    "total": competition_model.effective_sample_weight,
                    "effective_sample_size": competition_model.effective_sample_size,
                    "by_competition": dict(
                        Counter(
                            {
                                competition: sum(
                                    competition_weight(match, competition_params)
                                    for match in train
                                    if match["competition"] == competition
                                )
                                for competition in {match["competition"] for match in train}
                            }
                        )
                    ),
                }
            },
        ),
        "time_decay_xg": challenger_result(
            TIME_DECAY_MODEL_VERSION,
            {"half_life_months": half_life},
            time_trials,
            time_predictions,
            baseline,
            counts,
            baseline_segments,
            ["Weights use train only and are calculated relative to each predicted match date."],
            extra={
                "effective_sample_size": {
                    "validation": time_selected["diagnostics"],
                    "test": time_test_diagnostics,
                },
                "recent_coverage_by_team": recent_coverage_by_team(
                    train, max(parse_date(str(match["kickoff_at"])) for match in validation)
                ),
            },
        ),
        "low_sample_fallback_xg": challenger_result(
            LOW_SAMPLE_MODEL_VERSION,
            low_params,
            low_trials,
            low_predictions,
            baseline,
            counts,
            baseline_segments,
            ["Extra smoothing is applied only to teams below the selected train-match threshold."],
            extra={
                "low_sample_teams": sorted(team for team, count in counts.items() if count < int(low_params["low_sample_threshold"])),
                "low_sample_teams_count": sum(count < int(low_params["low_sample_threshold"]) for count in counts.values()),
            },
        ),
        "elo_prior_xg_diagnostic": challenger_result(
            ELO_DIAGNOSTIC_MODEL_VERSION,
            ELO_DIAGNOSTIC_PARAMS,
            [],
            elo_predictions,
            baseline,
            counts,
            baseline_segments,
            [
                "Current/static Elo snapshot used on historical matches.",
                "This is temporal leakage risk evidence and cannot support promotion.",
            ],
            temporal_leakage_risk=True,
            extra={
                "elo_coverage": {
                    split: sum(
                        item["prediction_metadata"]["elo_available_for_both_teams"] for item in predictions
                    )
                    / len(predictions)
                    for split, predictions in elo_predictions.items()
                }
            },
        ),
    }
    ranking = sorted(
        (
            {
                "challenger": name,
                "test_log_loss_1x2": item["test"]["log_loss_1x2"],
                "test_brier_score_1x2": item["test"]["brier_score_1x2"],
                "passed_guardrails": item["passed_guardrails"],
                "candidate_for_future_combination": item["candidate_for_future_combination"],
                "temporal_leakage_risk": item["temporal_leakage_risk"],
            }
            for name, item in challengers.items()
        ),
        key=lambda item: item["test_log_loss_1x2"],
    )
    candidates = [item["challenger"] for item in ranking if item["candidate_for_future_combination"]]
    results = {
        "generated_at": utc_now(),
        "version": VERSION,
        "status": "experimental",
        "promotion_recommendation": PROMOTION_RECOMMENDATION,
        "base_model": BASE_MODEL_VERSION,
        "previous_result": "v1.3_upstream_xg_design_validated",
        "selection_policy": "validation_only",
        "test_used_for_parameter_selection": False,
        "v0_9_reference": baseline,
        "source_v0_9_reports": source_v0_9_reports,
        "challengers": challengers,
        "ranking": ranking,
        "recommendations": [
            "Do not promote any V1.4 challenger; promotion_recommendation remains do_not_promote_yet.",
            (
                f"Candidates for a future combination review: {', '.join(candidates)}."
                if candidates
                else "No isolated upstream challenger passes every future-combination guardrail."
            ),
            "Treat Elo results as non-promotable temporal-leakage-risk diagnostics only.",
        ],
        "next_steps": [
            "Complete human review of V1.4 validation-only selection and segment evidence.",
            "Keep the combined upstream challenger deferred pending explicit human approval.",
        ],
        "combined_challenger_implemented": False,
        "active_engine_replaced": False,
        "world_cup_2026_predictions_modified": False,
    }
    publish(results)
    (PROJECT_ROOT / "docs" / "UPSTREAM_XG_CHALLENGER_RESULTS_V1_4.md").write_text(
        render_report(results), encoding="utf-8"
    )
    print(
        "Selected upstream xG parameters on validation only; "
        f"competition={competition_params}, half_life={half_life}, low_sample={low_params}."
    )


if __name__ == "__main__":
    main()
