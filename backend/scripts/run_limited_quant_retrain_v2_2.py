"""Run the V2.2 limited quant retrain on the refreshed V2.1 historical splits."""

from __future__ import annotations

import argparse
from datetime import datetime
import importlib.metadata
import shutil
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import backend.calibration.active_engine_adapter_v2 as active_adapter
from backend.calibration.feature_builder_v2_2 import build_chronological_features
from backend.calibration.historical_replay_v2_2 import build_predictions, coherence_audit, evaluate_predictions, segment_metrics
from backend.calibration.markets_v2_2 import evaluate_secondary_markets
from backend.calibration.monte_carlo_simulation_v2_2 import stability_audit
from backend.calibration.optuna_optimizer_v2_2 import optimize, rating_config, xgb_params, xg_params
from backend.calibration.xgboost_market_models_v2_2 import (
    feature_importance, predict_binary_models, predict_multiclass, train_binary_models, train_multiclass,
)
from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, utc_now, write_json

VERSION = "v2.2"


def publish(payload: Any, name: str, frontend: bool = True, snapshot: bool = True) -> None:
    target = DATA_DIR / "generated" / name
    write_json(payload, target)
    if snapshot:
        shutil.copy2(target, DATA_DIR / "snapshots" / name)
    if frontend:
        shutil.copy2(target, FRONTEND_DATA_DIR / name)


def assert_inputs(splits: dict[str, list[dict[str, Any]]]) -> None:
    audit = load_json(DATA_DIR / "generated" / "temporal_leakage_audit_v2_1.json")
    if not audit["passed"] or audit["temporal_leakage_detected"]:
        raise ValueError("V2.1 temporal leakage audit did not pass")
    seen: set[str] = set()
    for split in ("train", "validation", "test"):
        rows = splits[split]
        if rows != sorted(rows, key=lambda row: row["kickoff_at"]):
            raise ValueError(f"{split} is not chronological")
        for row in rows:
            if row.get("is_future_fixture") or row.get("home_score") is None or row.get("away_score") is None:
                raise ValueError(f"Invalid historical row in {split}")
            if row["match_id"] in seen:
                raise ValueError(f"Duplicate match across splits: {row['match_id']}")
            seen.add(row["match_id"])


def deltas(current: dict[str, Any], reference: dict[str, Any]) -> dict[str, float]:
    return {k: float(v) - float(reference[k]) for k, v in current.items() if isinstance(v, (int, float)) and isinstance(reference.get(k), (int, float))}


def usable_markets(report: dict[str, Any]) -> int:
    return sum(
        item["0.60"]["selections"] >= 20
        and item["0.60"]["coverage_if_thresholded"] >= .10
        and (item["0.60"]["win_rate"] or 0) >= .65
        for item in report["all_markets"].values()
    )


def assess(metrics, coherence, secondary, feature_audit, v20):
    dnb = secondary["test"]["draw_no_bet"]["0.60"]
    gap = metrics["validation"]["log_loss_1x2"] - metrics["train"]["log_loss_1x2"]
    usable = usable_markets(secondary["test"])
    gates = {
        "test_log_loss_improves_v2_0_and_v0_9": metrics["test"]["log_loss_1x2"] < min(v20["test"]["log_loss_1x2"], 1.0412190253172982),
        "test_brier_improves_v2_0_and_v0_9": metrics["test"]["brier_score_1x2"] < min(v20["test"]["brier_score_1x2"], .6277293494283444),
        "validation_and_test_directionally_coherent": metrics["validation"]["log_loss_1x2"] < v20["validation"]["log_loss_1x2"] and metrics["test"]["log_loss_1x2"] < v20["test"]["log_loss_1x2"],
        "train_validation_gap_strongly_reduced": gap < .15 and gap < .2122,
        "modal_1_1_rate_strongly_reduced": metrics["test"]["modal_1_1_rate"] < .425,
        "clear_favorite_alignment_at_least_55_percent": (coherence["test"]["clear_favorite_score_alignment_rate"] or 0) >= .55,
        "dnb_0_60_progress_useful": dnb["coverage"] >= .30 and (dnb["win_rate_excluding_pushes"] or 0) > .7804878048780488,
        "secondary_markets_exploitable": usable >= 4,
        "no_temporal_leakage": not feature_audit["leakage_detected"],
        "no_obvious_overfit": gap < .15 and metrics["test"]["log_loss_1x2"] - metrics["validation"]["log_loss_1x2"] < .12,
    }
    return {
        "deployment_decision": "deploy_active_engine" if all(gates.values()) else "do_not_deploy",
        "gates": gates, "failed_gates": [k for k, v in gates.items() if not v],
        "train_validation_log_loss_gap": gap, "usable_secondary_markets_at_0_60": usable,
        "dnb_0_60": dnb, "product_satisfactory": gates["modal_1_1_rate_strongly_reduced"] and gates["clear_favorite_alignment_at_least_55_percent"],
    }


def docs(results, feature_audit, xgb_results):
    v, t = results["validation"], results["test"]
    dnb = results["secondary_markets"]["draw_no_bet_test"]["0.60"]
    common = ("V2.2 uses only the refreshed V2.1 chronological splits. Every feature is built before the current result "
              "is observed; test is evaluated once after validation-only selection. Sparse provider statistics, events, "
              "lineups, provider xG, exploratory xG proxy and odds are excluded.")
    return {
        "QUANT_ENGINE_V2_2_RESULTS.md": f"""# Quant Engine V2.2 Results

V2.2 is a limited retrain of the V2 quant architecture on 3,062 refreshed completed senior-international matches. {common}

- Validation log loss / Brier: `{v['log_loss_1x2']:.4f}` / `{v['brier_score_1x2']:.4f}`
- Test log loss / Brier: `{t['log_loss_1x2']:.4f}` / `{t['brier_score_1x2']:.4f}`
- Test accuracy / exact / top-3 / top-5: `{t['accuracy_1x2']:.1%}` / `{t['exact_score_accuracy']:.1%}` / `{t['top_3_score_hit_rate']:.1%}` / `{t['top_5_score_hit_rate']:.1%}`
- Test modal 1-1: `{t['modal_1_1_rate']:.1%}`
- Decision: `{results['deployment_decision']}`

The comparison with V2.0 and V0.9 is directional because those versions used older test periods. The strict active-deployment decision nevertheless requires every listed gate to pass. Failed gates remain visible in the result JSON.
""",
        "ACTIVE_ENGINE_DEPLOYMENT_V2_2.md": f"""# Active Engine Deployment V2.2

Decision: `{results['deployment_decision']}`. Active engine replacement: `{str(results['active_engine_replacement']).lower()}`.

V2.2 may deploy only when both final-test calibration metrics improve V2.0 and V0.9, validation and test agree directionally, the train-validation gap is strongly reduced, modal 1-1 concentration falls, clear-favorite score alignment reaches 55%, DNB improves at useful coverage, secondary markets are exploitable, and leakage/overfit checks pass.

Failed gates: `{results['deployment_reason']}`. When any gate fails, active World Cup 2026 prediction files are intentionally untouched. Future fixtures are never used for training, validation, selection or the deployment decision.
""",
        "FEATURE_AUDIT_V2_2.md": f"""# Feature Audit V2.2

The V2.2 builder retains `{feature_audit['feature_count']}` conservative numeric pre-match features reconstructed from prior results. {common}

Advanced provider feature families were available on a six-match probe but their broad historical coverage was not established. They are therefore excluded rather than imputed into a misleading signal. Features retained and excluded are enumerated in `feature_audit_v2_2.json`.

- Advanced features used: none
- Current-match post-match data used: false
- Provider xG used: false
- Leakage detected: `{str(feature_audit['leakage_detected']).lower()}`
""",
        "XGBOOST_MARKET_ENGINE_V2_2.md": f"""# XGBoost Market Engine V2.2

V2.2 trains one multiclass 1X2 model and thirteen binary secondary-market models. Tree depth is capped at three, regularization is mandatory, and validation early stopping is used during Optuna selection. The frozen round count and parameters are then fitted on train only before the single final-test evaluation.

The measured train-validation log-loss gap is `{xgb_results['train_validation_log_loss_gap']:.4f}`. Test never selects parameters. Gain importance for all fourteen models is retained in `xgboost_market_results_v2_2.json`; permutation importance was excluded to keep the limited retrain focused.
""",
        "HISTORICAL_REPLAY_V2_2.md": f"""# Historical Replay V2.2

Replay follows `predict -> observe -> update` across train, validation and test. Validation contains `{v['matches']}` matches and test contains `{t['matches']}` matches from the V2.1 refreshed chronological splits. Test is evaluated once after selection and cannot trigger retuning.

The rating and team-history states advance only after each completed match result is observed. Future World Cup 2026 fixtures are excluded from every historical state and selection decision.

Split boundaries remain explicit in every artifact. Earlier observed results may update state for a later chronological match, but final-test evidence never changes the selected configuration or triggers retuning.
""",
        "SECONDARY_MARKET_EVALUATION_V2_2.md": f"""# Secondary Market Evaluation V2.2

The report evaluates DNB, double chance, over/under, BTTS, clean sheets and team goals at all, 0.55, 0.60, 0.65 and 0.70 thresholds. DNB separates wins, losses and pushes.

At confidence 0.60, DNB test coverage is `{dnb['coverage']:.1%}`, win rate excluding pushes is `{dnb['win_rate_excluding_pushes']:.1%}`, and non-loss including pushes is `{dnb['non_loss_rate_including_pushes']:.1%}`. Coverage and selection counts remain visible to prevent low-volume claims.

All threshold tables retain wins, losses, pushes, confidence and coverage so that a high headline rate cannot hide a trivial number of selections.
""",
        "MONTE_CARLO_STABILITY_V2_2.md": f"""# Monte Carlo Stability V2.2

Each validation and test match receives exactly 1,500 deterministic Poisson simulations with seed 2026. The analytical score matrix remains the model output; Monte Carlo measures sampling stability only.

The test analytical-versus-simulated average absolute gap is `{results['monte_carlo']['stability_summary']['analytic_vs_simulated_average_gap']:.4f}` and the maximum match gap is `{results['monte_carlo']['stability_summary']['max_average_gap']:.4f}`. This validates simulation stability, not predictive promotion.

The same seed and simulation count make reruns directly comparable. Promotion still depends on historical calibration, market utility, coherence, leakage and overfit gates.
""",
        "ENGINE_V2_2_COHERENCE_AUDIT.md": f"""# Engine V2.2 Coherence Audit

The product audit compares the hybrid 1X2 favorite with the outcome implied by the modal Poisson score. A clear favorite has an outcome-probability lead of at least 0.08.

- Modal 1-1 test rate: `{t['modal_1_1_rate']:.1%}`
- Clear-favorite alignment: `{results['coherence']['clear_favorite_score_alignment_rate']:.1%}`
- Favorites with modal 1-1: `{results['coherence']['share_favorites_with_1_1_modal_score']:.1%}`
- Product satisfactory: `{str(results['product_satisfactory']).lower()}`

The guardrails require a marked reduction from V2.0's 47.5% modal 1-1 rate and at least 55% clear-favorite alignment.

Misaligned clear-favorite examples remain in the JSON artifact for manual review; aggregate success does not remove the need to inspect product-facing contradictions.
""",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--quick", action="store_true")
    mode.add_argument("--full", action="store_true")
    args = parser.parse_args(argv)
    n_trials = 150 if args.quick else 1500 if args.full else 500
    generated_at = utc_now()
    splits = {s: load_json(DATA_DIR / "normalized" / f"historical_{s}_matches_v2_1.json") for s in ("train", "validation", "test")}
    assert_inputs(splits)
    selected, optuna_summary = optimize(splits, n_trials)
    rows, timeline, feature_audit, rating, history = build_chronological_features(splits, rating_config(selected))
    params = xgb_params(selected)
    multiclass = train_multiclass(rows["train"], params)
    binaries = train_binary_models(rows["train"], params)
    predictions, metrics, segments, coherence, secondary, monte = {}, {}, {}, {}, {}, {}
    for split in ("train", "validation", "test"):
        predictions[split] = build_predictions(rows[split], predict_multiclass(multiclass, rows[split]), selected, xg_params(selected))
        for item in predictions[split]:
            item["model_version"] = item["engine_version"] = "quant_hybrid_v2.2"
        metrics[split] = evaluate_predictions(predictions[split])
        segments[split] = segment_metrics(predictions[split])
        coherence[split] = coherence_audit(predictions[split]) | {"modal_score_distribution": metrics[split]["modal_score_distribution"], "modal_1_1_rate": metrics[split]["modal_1_1_rate"]}
        secondary[split] = evaluate_secondary_markets(predict_binary_models(binaries, rows[split]), rows[split], [x["markets"] for x in predictions[split]])
        if split != "train":
            monte[split] = stability_audit(predictions[split], 1500, 2026)
    v20 = load_json(DATA_DIR / "generated" / "quant_engine_v2_0_results.json")
    v09 = load_json(DATA_DIR / "generated" / "upstream_xg_challenger_results_v1_4.json")["v0_9_reference"]
    assessment = assess(metrics, coherence, secondary, feature_audit, v20)
    active = False
    active_details = {}
    if assessment["deployment_decision"] == "deploy_active_engine":
        fixtures = load_json(DATA_DIR / "normalized" / "matches.json")
        final_model = train_multiclass(rows["train"] + rows["validation"] + rows["test"], params)
        from backend.calibration.xg_engine_v2_2 import expected_goals
        active_adapter.expected_goals = expected_goals
        active_rows = active_adapter.active_predictions(fixtures, final_model, selected, xg_params(selected), rating, history, generated_at)
        for item in active_rows:
            for key in ("prediction_id", "model_version", "prediction_version", "engine_version"):
                item[key] = str(item[key]).replace("v2.0", "v2.2")
        archive = DATA_DIR / "archived" / f"pre_v2_2_deployment_{datetime.now().strftime('%Y%m%dT%H%M%S')}"
        archive.mkdir(parents=True, exist_ok=True)
        active_names = ("predictions.json", "predictions_baseline.json", "predictions_elo.json", "model_comparison.json")
        for folder in (DATA_DIR / "generated", DATA_DIR / "snapshots", FRONTEND_DATA_DIR):
            for name in active_names:
                source = folder / name
                if source.exists():
                    shutil.copy2(source, archive / f"{folder.name}_{name}")
        for target in (DATA_DIR / "generated" / "predictions.json", DATA_DIR / "snapshots" / "predictions.json", FRONTEND_DATA_DIR / "predictions.json"):
            write_json(active_rows, target)
        active_details = {"active_engine_replacement": True, "archive_path": str(archive.relative_to(ROOT))}
        comparison = {"generated_at": generated_at, "active_engine": "quant_hybrid_v2.2", "deployment_source": "quant_engine_v2_2_results.json"}
        for folder in (DATA_DIR / "generated", DATA_DIR / "snapshots", FRONTEND_DATA_DIR):
            write_json(comparison, folder / "model_comparison.json")
        active = True
    xgb_results = {
        "version": VERSION, "selected_params": params, "model_count": 1 + len(binaries),
        "train_1x2": metrics["train"], "validation_1x2": metrics["validation"], "test_1x2": metrics["test"],
        "train_validation_log_loss_gap": assessment["train_validation_log_loss_gap"],
        "feature_importance": {"outcome_1x2": multiclass.get_score(importance_type="gain")} | feature_importance(binaries),
        "permutation_importance": {"performed": False, "reason": "Excluded from limited retrain scope."},
        "overfit_risk": not assessment["gates"]["no_obvious_overfit"],
    }
    results = {
        "generated_at": generated_at, "version": VERSION, "status": "active" if active else "experimental",
        "engine_type": "limited_quant_retrain_refreshed_dataset", "training_dataset": "historical_splits_v2_1",
        "dependencies": {"xgboost": importlib.metadata.version("xgboost"), "optuna": importlib.metadata.version("optuna")},
        "deployment_decision": assessment["deployment_decision"], "active_engine_replacement": active,
        "deployment_reason": assessment["failed_gates"] or ["All strict gates passed."], "deployment_gates": assessment["gates"],
        "selected_params": selected, "validation": metrics["validation"], "test": metrics["test"],
        "delta_vs_v2_0": {"validation": deltas(metrics["validation"], v20["validation"]), "test": deltas(metrics["test"], v20["test"])},
        "delta_vs_v0_9": {"validation": deltas(metrics["validation"], v09["validation"]), "test": deltas(metrics["test"], v09["test"])},
        "score_exact": {s: {k: metrics[s][k] for k in ("exact_score_accuracy", "top_3_score_hit_rate", "top_5_score_hit_rate")} for s in ("validation", "test")},
        "secondary_markets": {"test_usable_market_count_at_0_60": assessment["usable_secondary_markets_at_0_60"], "draw_no_bet_test": secondary["test"]["draw_no_bet"]},
        "coherence": coherence["test"], "monte_carlo": {"simulations_per_match": 1500, "seed": 2026, "stability_summary": monte["test"]},
        "overfit_audit": {"train_validation_log_loss_gap": assessment["train_validation_log_loss_gap"], "overfit_risk": xgb_results["overfit_risk"]},
        "temporal_leakage_detected": feature_audit["leakage_detected"], "product_satisfactory": assessment["product_satisfactory"],
        "optuna": {k: optuna_summary[k] for k in ("mode", "n_trials", "best_trial", "best_value")},
        "historical_replay": {"validation_matches_replayed": len(rows["validation"]), "test_matches_replayed": len(rows["test"]), "test_evaluated_once_after_selection": True},
        "segments": {"validation": segments["validation"], "test": segments["test"]}, "active_deployment_details": active_details,
        "notes": ["V2.2 uses V2.1 splits exclusively.", "Provider xG, xG proxy, current-match post-match features and odds are excluded.", "V2.0/V0.9 comparisons use different historical test periods and are directional."],
    }
    optuna_summary["validation_metrics"] = metrics["validation"]
    replay = {"version": VERSION, "predict_observe_update_confirmed": True, "test_used_for_parameter_selection": False, "test_evaluated_once": True, "validation": metrics["validation"], "test": metrics["test"], "segments": results["segments"]}
    for payload, name in (
        (results, "quant_engine_v2_2_results.json"), (timeline, "internal_rating_timeline_v2_2.json"),
        (feature_audit, "feature_audit_v2_2.json"), (xgb_results, "xgboost_market_results_v2_2.json"),
        (optuna_summary, "optuna_study_summary_v2_2.json"), (replay, "historical_replay_metrics_v2_2.json"),
        (secondary, "secondary_market_metrics_v2_2.json"), (monte, "monte_carlo_stability_v2_2.json"),
        (coherence, "engine_v2_2_coherence_audit.json"),
    ):
        publish(payload, name)
    publish(predictions["validation"], "historical_validation_predictions_quant_engine_v2_2.json", False, False)
    publish(predictions["test"], "historical_test_predictions_quant_engine_v2_2.json", False, False)
    publish(predictions["validation"], "historical_replay_validation_v2_2.json", False, False)
    publish(predictions["test"], "historical_replay_test_v2_2.json", False, False)
    for name, text in docs(results, feature_audit, xgb_results).items():
        (ROOT / "docs" / name).write_text(text, encoding="utf-8")
    print(f"V2.2 complete: {results['deployment_decision']}; test log loss={metrics['test']['log_loss_1x2']:.4f}")


if __name__ == "__main__":
    main()
