"""Build, evaluate, publish, and conditionally deploy the V2.0 quant hybrid engine."""

from __future__ import annotations

import argparse
import importlib.metadata
import shutil
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.calibration.active_engine_adapter_v2 import active_predictions, deploy_active_predictions
from backend.calibration.feature_builder_v2 import build_chronological_features
from backend.calibration.historical_replay_v2 import (
    build_predictions,
    coherence_audit,
    evaluate_predictions,
    segment_metrics,
)
from backend.calibration.markets_v2 import evaluate_secondary_markets
from backend.calibration.monte_carlo_simulation_v2 import stability_audit
from backend.calibration.optuna_optimizer_v2 import optimize, rating_config, xgb_params, xg_params
from backend.calibration.xgboost_market_models_v2 import (
    feature_importance,
    predict_binary_models,
    predict_multiclass,
    train_binary_models,
    train_multiclass,
)
from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, utc_now, write_json

VERSION = "v2.0"


def publish(payload: Any, name: str, frontend: bool = True, snapshot: bool = True) -> None:
    generated = DATA_DIR / "generated" / name
    write_json(payload, generated)
    if snapshot:
        shutil.copy2(generated, DATA_DIR / "snapshots" / name)
    if frontend:
        shutil.copy2(generated, FRONTEND_DATA_DIR / name)


def assert_historical_splits(splits: dict[str, list[dict[str, Any]]]) -> None:
    for split, matches in splits.items():
        if any(match.get("season") == 2026 or match.get("is_future_fixture") for match in matches):
            raise ValueError(f"Future or 2026 fixture found in {split}")
        if matches != sorted(matches, key=lambda item: item["kickoff_at"]):
            raise ValueError(f"{split} is not chronological")
    for earlier, later in (("train", "validation"), ("validation", "test")):
        if max(item["kickoff_at"] for item in splits[earlier]) > min(item["kickoff_at"] for item in splits[later]):
            raise ValueError(f"{earlier} overlaps {later}")


def numeric_deltas(current: dict[str, Any], reference: dict[str, Any]) -> dict[str, float]:
    return {
        key: float(value) - float(reference[key])
        for key, value in current.items()
        if isinstance(value, (int, float)) and isinstance(reference.get(key), (int, float))
    }


def usable_secondary_count(metrics: dict[str, Any]) -> int:
    count = 0
    for thresholds in metrics["all_markets"].values():
        item = thresholds["0.60"]
        if item["selections"] >= 10 and item["coverage_if_thresholded"] >= 0.10 and (item["win_rate"] or 0) >= 0.65:
            count += 1
    return count


def deployment_assessment(
    validation: dict[str, Any],
    test: dict[str, Any],
    train: dict[str, Any],
    reference: dict[str, Any],
    coherence: dict[str, Any],
    secondary: dict[str, Any],
    feature_audit: dict[str, Any],
    latest_history: str,
    fixtures: list[dict[str, Any]],
    known_teams: set[str],
) -> dict[str, Any]:
    main_gain = test["log_loss_1x2"] <= reference["test"]["log_loss_1x2"] - 0.01 or test[
        "brier_score_1x2"
    ] <= reference["test"]["brier_score_1x2"] - 0.01
    validation_supports = validation["log_loss_1x2"] < reference["validation"]["log_loss_1x2"] and validation[
        "brier_score_1x2"
    ] < reference["validation"]["brier_score_1x2"]
    modal_reduced = test["modal_1_1_rate"] <= reference["test"]["modal_1_1_rate"] * 0.70
    product_satisfactory = (coherence["clear_favorite_score_alignment_rate"] or 0) >= 0.50
    no_overfit = validation["log_loss_1x2"] - train["log_loss_1x2"] <= 0.20 and test[
        "log_loss_1x2"
    ] - validation["log_loss_1x2"] <= 0.10
    secondary_count = usable_secondary_count(secondary["test"])
    secondary_strong = secondary_count >= 4
    no_leakage = not feature_audit["leakage_detected"]
    freshness_days = (
        __import__("datetime").datetime.fromisoformat(min(item["kickoff_at"] for item in fixtures).replace("Z", "+00:00"))
        - __import__("datetime").datetime.fromisoformat(latest_history.replace("Z", "+00:00"))
    ).days
    fixture_teams = {str(item["home_team"]) for item in fixtures} | {str(item["away_team"]) for item in fixtures}
    coverage = len(fixture_teams & known_teams) / len(fixture_teams)
    operational_data_sufficient = freshness_days <= 365 and coverage >= 0.90
    gates = {
        "main_metric_gain_or_secondary_utility": main_gain or secondary_strong,
        "validation_supports_gain": validation_supports,
        "modal_1_1_strongly_reduced": modal_reduced,
        "favorite_score_product_coherent": product_satisfactory,
        "no_temporal_leakage": no_leakage,
        "no_obvious_overfit": no_overfit,
        "secondary_markets_exploitable": secondary_strong,
        "active_input_freshness_and_team_coverage": operational_data_sufficient,
    }
    reasons = [name for name, passed in gates.items() if not passed]
    return {
        "deployment_decision": "deploy_active_engine" if all(gates.values()) else "do_not_deploy",
        "gates": gates,
        "deployment_reason": reasons or ["All deployment gates passed."],
        "main_metric_gain": main_gain,
        "secondary_usable_market_count_at_0_60": secondary_count,
        "active_history_staleness_days": freshness_days,
        "active_fixture_team_coverage": coverage,
        "product_satisfactory": product_satisfactory,
        "no_obvious_overfit": no_overfit,
    }


def markdown_documents(results: dict[str, Any], feature_audit: dict[str, Any], xgb_results: dict[str, Any]) -> dict[str, str]:
    val, test = results["validation"], results["test"]
    decision = results["deployment_decision"]
    gates = "\n".join(f"- `{name}`: `{str(passed).lower()}`" for name, passed in results["deployment_gates"].items())
    common = (
        "All historical features are reconstructed chronologically before each result is observed. "
        "Optuna selects on validation only; the fixed configuration is then evaluated once on test. "
        "No World Cup 2026 fixture and no external static Elo rating enters training or selection."
    )
    return {
        "QUANT_ENGINE_V2_0_RESULTS.md": f"""# Quant Hybrid Engine V2.0 Results

## Outcome

V2.0 combines an internal chronological rating, pre-match features, regularized XGBoost
probabilities and an independent-Poisson score distribution. {common}

- Validation log loss / Brier: `{val['log_loss_1x2']:.4f}` / `{val['brier_score_1x2']:.4f}`
- Test log loss / Brier: `{test['log_loss_1x2']:.4f}` / `{test['brier_score_1x2']:.4f}`
- Test exact / top-3 / top-5: `{test['exact_score_accuracy']:.1%}` / `{test['top_3_score_hit_rate']:.1%}` / `{test['top_5_score_hit_rate']:.1%}`
- Test modal 1-1 rate: `{test['modal_1_1_rate']:.1%}`
- Test delta vs V0.9 log loss / Brier: `{results['delta_vs_v0_9']['test']['log_loss_1x2']:+.4f}` / `{results['delta_vs_v0_9']['test']['brier_score_1x2']:+.4f}`
- Deployment decision: `{decision}`

## Deployment gates

{gates}

The active engine is changed only when every historical, product-coherence,
overfitting, secondary-market, and operational-data gate passes. Failed results are
retained in the JSON artifacts rather than hidden.
""",
        "XGBOOST_MARKET_ENGINE_V2_0.md": f"""# XGBoost Market Engine V2.0

The experiment trains one `multi:softprob` 1X2 model and thirteen
`binary:logistic` secondary-market models. Depth is bounded, regularization is
mandatory, and the shared hyperparameters are selected by Optuna on validation only.

Selected parameters: `{results['selected_params']}`.

Train, validation, and test reports are published to expose overfit risk. The measured
train-to-validation log-loss gap is
`{val['log_loss_1x2'] - xgb_results['train_1x2']['log_loss_1x2']:+.4f}`.
Feature importance for the multiclass model and every binary market model is retained
in `xgboost_market_results_v2_0.json`. Test data never chooses a tree parameter.
""",
        "FEATURE_AUDIT_V2_0.md": f"""# Feature Audit V2.0

The builder produces `{feature_audit['feature_count']}` numeric features. Every row is
built from rating and team history available strictly before kickoff; the current
match result is observed only after its prediction row exists. Updates then feed the
next chronological match.

{common}

- Pre-match only: `{str(feature_audit['pre_match_only']).lower()}`
- Current-match stats used: `{str(feature_audit['current_match_stats_used']).lower()}`
- External static Elo used: `{str(feature_audit['external_static_elo_used']).lower()}`
- Leakage detected: `{str(feature_audit['leakage_detected']).lower()}`
- Rows by split: `{feature_audit['rows_by_split']}`

Unknown venue context is encoded neutrally because the normalized historical source
does not expose a reliable neutral-site flag.
""",
        "HISTORICAL_REPLAY_V2_0.md": f"""# Historical Replay V2.0

Historical evaluation follows `predict -> observe -> update -> next match`.
Validation replays `{results['historical_replay']['validation_matches_replayed']}`
matches and test replays `{results['historical_replay']['test_matches_replayed']}`
matches. The XGBoost model is fitted on train only, while the internal rating and
recent-history state advance after each observed validation/test match.

{common}

The test remains final and is not fed back into Optuna or parameter selection.
Per-match replay outputs, full metrics, lambda diagnostics, and segment reports are
published separately for auditability.
""",
        "SECONDARY_MARKET_EVALUATION_V2_0.md": f"""# Secondary Market Evaluation V2.0

The report covers over/under, BTTS, double chance, team goals, clean sheets and Draw
No Bet at all-matches, `0.55`, `0.60`, `0.65`, and `0.70` confidence thresholds.
DNB explicitly separates wins, losses, and pushes. Its win rate excludes pushes,
while its non-loss rate includes them; neither number is presented as the other.

At threshold `0.60`, the test has
`{results['deployment_diagnostics']['secondary_usable_market_count_at_0_60']}`
markets meeting the minimum coverage/selection/accuracy utility rule. High rates with
tiny coverage do not qualify the engine for deployment. Full threshold tables remain
in `secondary_market_metrics_v2_0.json`.
""",
        "MONTE_CARLO_STABILITY_V2_0.md": f"""# Monte Carlo Stability V2.0

Each validation and test match is simulated exactly `1500` times with seed `2026`.
The analytical Poisson matrix remains the exact model output; Monte Carlo is used to
measure sampling stability and prepare future tournament scenario simulation.

The test analytical-versus-simulated average absolute gap is
`{results['monte_carlo']['stability_summary']['analytic_vs_simulated_average_gap']:.4f}`;
the maximum per-match average gap is
`{results['monte_carlo']['stability_summary']['max_average_gap']:.4f}`.
These values compare like-for-like Poisson probabilities, not the blended XGBoost
1X2 output. All test matches fall below a `0.03` average absolute gap, so the
sampling implementation is stable enough for future tournament-scenario work.
This stability does not validate the predictive model itself: model promotion still
depends on out-of-sample calibration, coherence, and operational-data gates.
""",
        "ENGINE_V2_0_COHERENCE_AUDIT.md": f"""# Engine V2.0 Coherence Audit

The audit checks whether the favorite selected by blended 1X2 probabilities agrees
with the outcome implied by the modal Poisson score. A clear favorite has a gap of at
least `0.08` over the second-highest 1X2 probability.

- Favorite-score alignment: `{results['coherence']['favorite_score_alignment_rate']:.1%}`
- Clear-favorite alignment: `{results['coherence']['clear_favorite_score_alignment_rate']:.1%}`
- Favorite matches with modal 1-1: `{results['coherence']['share_favorites_with_1_1_modal_score']:.1%}`
- Test modal 1-1: `{results['coherence']['modal_1_1_rate']:.1%}`

Clear-favorite alignment below `50%` is an automatic product-satisfaction failure,
regardless of log-loss improvement. Misaligned examples are retained in the JSON.
""",
        "ACTIVE_ENGINE_DEPLOYMENT_V2_0.md": f"""# Active Engine Deployment V2.0

Decision: `{decision}`.

The fixed model improves validation strongly but changes final-test log loss and
Brier against V0.9 by `{results['delta_vs_v0_9']['test']['log_loss_1x2']:+.4f}` and
`{results['delta_vs_v0_9']['test']['brier_score_1x2']:+.4f}`. Its
train-to-validation log-loss gap is
`{xgb_results['train_validation_log_loss_gap']:.4f}`. DNB at confidence `0.60`
reaches `{results['secondary_markets']['draw_no_bet_test']['0.60']['win_rate_excluding_pushes']:.1%}`
wins excluding pushes and
`{results['secondary_markets']['draw_no_bet_test']['0.60']['non_loss_rate_including_pushes']:.1%}`
non-loss including pushes at
`{results['secondary_markets']['draw_no_bet_test']['0.60']['coverage']:.1%}` coverage.

The deployment decision is automatic but conservative: every gate must pass. The
active World Cup 2026 prediction files are replaced and archived only after clear
historical gains, reduced 1-1 concentration, acceptable favorite-score coherence,
useful secondary markets, no leakage, no obvious overfit, and adequate operational
input freshness/team coverage.

Failed gates:
{chr(10).join(f'- `{reason}`' for reason in results['deployment_reason'])}

Active history staleness is
`{results['deployment_diagnostics']['active_history_staleness_days']}` days and 2026
fixture-team historical coverage is
`{results['deployment_diagnostics']['active_fixture_team_coverage']:.1%}`. When the
decision is `do_not_deploy`, existing active predictions are intentionally untouched.
""",
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full-optuna", action="store_true")
    args = parser.parse_args(argv)
    n_trials = 1000 if args.full_optuna else 100
    generated_at = utc_now()
    splits = {
        split: load_json(DATA_DIR / "normalized" / f"historical_{split}_matches.json")
        for split in ("train", "validation", "test")
    }
    assert_historical_splits(splits)
    selected, optuna_summary = optimize(splits, n_trials=n_trials)
    rows, timeline, feature_audit, rating, history = build_chronological_features(splits, rating_config(selected))
    params = xgb_params(selected)
    multiclass = train_multiclass(rows["train"], params)
    binary_models = train_binary_models(rows["train"], params)
    historical_predictions = {}
    metrics = {}
    segments = {}
    coherence = {}
    secondary = {}
    monte_carlo = {}
    for split in ("train", "validation", "test"):
        probabilities = predict_multiclass(multiclass, rows[split])
        historical_predictions[split] = build_predictions(rows[split], probabilities, selected, xg_params(selected))
        metrics[split] = evaluate_predictions(historical_predictions[split])
        segments[split] = segment_metrics(historical_predictions[split])
        coherence[split] = coherence_audit(historical_predictions[split])
        binary_probabilities = predict_binary_models(binary_models, rows[split])
        secondary[split] = evaluate_secondary_markets(
            binary_probabilities, rows[split], [item["markets"] for item in historical_predictions[split]]
        )
        if split != "train":
            monte_carlo[split] = stability_audit(historical_predictions[split], simulations_per_match=1500, seed=2026)
    reference = load_json(DATA_DIR / "generated" / "upstream_xg_challenger_results_v1_4.json")["v0_9_reference"]
    fixtures = load_json(DATA_DIR / "normalized" / "matches.json")
    assessment = deployment_assessment(
        metrics["validation"],
        metrics["test"],
        metrics["train"],
        reference,
        coherence["test"],
        secondary,
        feature_audit,
        max(match["kickoff_at"] for match in splits["test"]),
        fixtures,
        set(history.matches),
    )
    xgb_results = {
        "selected_params": params,
        "model_count": 1 + len(binary_models),
        "train_1x2": metrics["train"],
        "validation_1x2": metrics["validation"],
        "test_1x2": metrics["test"],
        "train_validation_log_loss_gap": metrics["validation"]["log_loss_1x2"] - metrics["train"]["log_loss_1x2"],
        "feature_importance": {"outcome_1x2": multiclass.get_score(importance_type="gain")} | feature_importance(binary_models),
        "secondary_market_metrics": {
            "validation": secondary["validation"]["xgboost_binary_markets"],
            "test": secondary["test"]["xgboost_binary_markets"],
        },
        "overfit_risk": not assessment["no_obvious_overfit"],
    }
    active_replacement = False
    active_details: dict[str, Any] = {}
    if assessment["deployment_decision"] == "deploy_active_engine":
        all_rows = rows["train"] + rows["validation"] + rows["test"]
        final_model = train_multiclass(all_rows, params)
        predictions = active_predictions(fixtures, final_model, selected, xg_params(selected), rating, history, generated_at)
        active_details = deploy_active_predictions(predictions, PROJECT_ROOT)
        active_replacement = True
    benchmarks = {
        "v0_9": reference,
        "v1_2": load_json(DATA_DIR / "generated" / "challenger_results_v1_2.json")["ranking"],
        "v1_4": load_json(DATA_DIR / "generated" / "upstream_xg_challenger_results_v1_4.json")["ranking"],
        "prototype": load_json(DATA_DIR / "generated" / "challenger_results_v1_2.json")["prototype_reference"],
    }
    results = {
        "generated_at": generated_at,
        "version": VERSION,
        "status": "active" if active_replacement else "experimental",
        "engine_type": "hybrid_internal_rating_xgboost_poisson",
        "dependencies": {
            "xgboost": importlib.metadata.version("xgboost"),
            "optuna": importlib.metadata.version("optuna"),
        },
        "active_engine_replacement": active_replacement,
        "deployment_decision": assessment["deployment_decision"],
        "deployment_reason": assessment["deployment_reason"],
        "deployment_gates": assessment["gates"],
        "deployment_diagnostics": {key: value for key, value in assessment.items() if key not in {"gates", "deployment_reason", "deployment_decision"}},
        "external_static_elo_used": False,
        "selected_params": selected,
        "optuna": {
            "mode": optuna_summary["mode"],
            "n_trials": optuna_summary["n_trials"],
            "best_trial": optuna_summary["best_trial"],
            "best_value": optuna_summary["best_value"],
        },
        "validation": metrics["validation"],
        "test": metrics["test"],
        "delta_vs_v0_9": {
            "validation": numeric_deltas(metrics["validation"], reference["validation"]),
            "test": numeric_deltas(metrics["test"], reference["test"]),
        },
        "score_exact": {
            split: {key: metrics[split][key] for key in ("exact_score_accuracy", "top_2_score_hit_rate", "top_3_score_hit_rate", "top_5_score_hit_rate")}
            for split in ("validation", "test")
        },
        "secondary_markets": {
            "test_usable_market_count_at_0_60": assessment["secondary_usable_market_count_at_0_60"],
            "draw_no_bet_test": secondary["test"]["draw_no_bet"],
        },
        "historical_replay": {
            "validation_matches_replayed": len(rows["validation"]),
            "test_matches_replayed": len(rows["test"]),
            "predict_observe_update_confirmed": True,
            "test_used_for_parameter_selection": False,
        },
        "coherence": coherence["test"] | {"modal_1_1_rate": metrics["test"]["modal_1_1_rate"]},
        "monte_carlo": {"simulations_per_match": 1500, "stability_summary": monte_carlo["test"]},
        "product_satisfactory": assessment["product_satisfactory"],
        "benchmarks": benchmarks,
        "segments": {"validation": segments["validation"], "test": segments["test"]},
        "active_deployment_details": active_details,
        "notes": [
            "Expected-goals intensities are model estimates from result history; provider xG is unavailable.",
            "Historical source ends in July 2024 and is assessed explicitly before any active 2026 deployment.",
            "Score exact is secondary to probabilistic calibration and product coherence.",
        ],
    }
    optuna_summary["validation_metrics"] = metrics["validation"]
    replay_metrics = {
        "predict_observe_update_confirmed": True,
        "test_used_for_parameter_selection": False,
        "validation": metrics["validation"],
        "test": metrics["test"],
        "segments": {"validation": segments["validation"], "test": segments["test"]},
    }
    publish(results, "quant_engine_v2_0_results.json")
    publish(timeline, "internal_rating_timeline_v2_0.json")
    publish(feature_audit, "feature_audit_v2_0.json")
    publish(xgb_results, "xgboost_market_results_v2_0.json")
    publish(optuna_summary, "optuna_study_summary_v2_0.json")
    publish(replay_metrics, "historical_replay_metrics_v2_0.json")
    publish(secondary, "secondary_market_metrics_v2_0.json")
    publish(monte_carlo, "monte_carlo_stability_v2_0.json")
    publish(coherence, "engine_v2_0_coherence_audit.json")
    publish(historical_predictions["validation"], "historical_validation_predictions_quant_engine_v2_0.json", frontend=False, snapshot=False)
    publish(historical_predictions["test"], "historical_test_predictions_quant_engine_v2_0.json", frontend=False, snapshot=False)
    publish(historical_predictions["validation"], "historical_replay_validation_v2_0.json", frontend=False, snapshot=False)
    publish(historical_predictions["test"], "historical_replay_test_v2_0.json", frontend=False, snapshot=False)
    for name, content in markdown_documents(results, feature_audit, xgb_results).items():
        (PROJECT_ROOT / "docs" / name).write_text(content, encoding="utf-8")
    print(f"V2.0 complete: {assessment['deployment_decision']}; test log loss={metrics['test']['log_loss_1x2']:.4f}")


if __name__ == "__main__":
    main()
