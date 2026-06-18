"""Decide whether the V2.30 full stats candidate is promotable."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.full_stats_engine_v2_30_utils import publish
from backend.scripts.pipeline_utils import DATA_DIR, load_json, utc_now

OUTPUT = "full_stats_engine_promotion_decision_v2_30.json"
RESULTS = "full_stats_enriched_engine_v2_30_results.json"
LEAKAGE = "full_stats_feature_leakage_audit_v2_30.json"
COLLECTION = "api_football_full_collection_summary_v2_29.json"


def pct(value: float | int | None) -> float:
    return float(value or 0.0)


def blocker_checks(results: dict[str, Any], leakage: dict[str, Any], collection: dict[str, Any]) -> list[dict[str, Any]]:
    comparison = results["comparison_to_quant_hybrid_v2_2"]
    baseline = results["metrics"]["test"]["quant_hybrid_v2_2"]
    candidate = results["metrics"]["test"]["full_stats_candidate"]
    checks = [
        {
            "key": "temporal_leakage",
            "blocking": leakage.get("passed") is not True,
            "detail": "Feature source dates must be strictly before target matches.",
        },
        {
            "key": "xg_invented",
            "blocking": results["feature_policy"].get("xg_missing_not_invented") is not True,
            "detail": "Missing xG must stay missing and be represented by coverage flags.",
        },
        {
            "key": "collection_incomplete",
            "blocking": collection.get("units_remaining", 1) != 0 or collection.get("ready_for_model_retest") is not True,
            "detail": "Full historical stats collection must be complete before promotion decision.",
        },
        {
            "key": "log_loss_collapse",
            "blocking": pct(comparison.get("test_log_loss_degradation_pct")) > 3.0,
            "detail": f"Test log loss degradation: {comparison.get('test_log_loss_degradation_pct')}%",
        },
        {
            "key": "brier_collapse",
            "blocking": pct(comparison.get("test_brier_degradation_pct")) > 3.0,
            "detail": f"Test Brier degradation: {comparison.get('test_brier_degradation_pct')}%",
        },
        {
            "key": "accuracy_collapse",
            "blocking": pct(comparison.get("test_accuracy_delta_points")) < -3.0,
            "detail": f"Test accuracy delta: {comparison.get('test_accuracy_delta_points')} points.",
        },
        {
            "key": "dangerous_calibration_favorites",
            "blocking": abs(candidate.get("favorite_calibration_gap", 0.0)) > abs(baseline.get("favorite_calibration_gap", 0.0)) + 0.08
            and abs(candidate.get("favorite_calibration_gap", 0.0)) > 0.12,
            "detail": "Favorite calibration must not deteriorate sharply.",
        },
        {
            "key": "dangerous_calibration_large_wins",
            "blocking": abs(candidate.get("large_win_gap", 0.0)) > abs(baseline.get("large_win_gap", 0.0)) + 0.08
            and abs(candidate.get("large_win_gap", 0.0)) > 0.18,
            "detail": "Large-win calibration must not deteriorate sharply.",
        },
    ]
    return checks


def main() -> None:
    results = load_json(DATA_DIR / "generated" / RESULTS)
    leakage = load_json(DATA_DIR / "generated" / LEAKAGE)
    collection = load_json(DATA_DIR / "generated" / COLLECTION)
    checks = blocker_checks(results, leakage, collection)
    blockers = [row for row in checks if row["blocking"]]
    selected = results["comparison_to_quant_hybrid_v2_2"]
    candidate_beats_baseline = (
        selected["test_log_loss_degradation_pct"] <= 0
        and selected["test_brier_degradation_pct"] <= 0
        and selected["test_accuracy_delta_points"] >= 0
    )
    if blockers:
        decision = "do_not_promote"
        promote = False
    elif candidate_beats_baseline:
        decision = "recommend_promotion"
        promote = True
    else:
        decision = "promote_with_reservations"
        promote = True
    payload = {
        "version": "v2.30",
        "generated_at": utc_now(),
        "decision": decision,
        "promote_candidate": promote,
        "execute_promotion_now": False,
        "active_predictions_overwritten": False,
        "requires_explicit_user_confirmation_before_active_overwrite": True,
        "user_rule": "Promote the richer-data engine unless a serious technical blocker is present.",
        "selected_model": {
            "name": results["candidate_name"],
            "model_key": selected["selected_model_key"],
            "params": selected["selected_params"],
        },
        "metrics_vs_quant_hybrid_v2_2": selected,
        "serious_blocker_checks": checks,
        "serious_blockers": blockers,
        "rollback_plan": [
            "Do not overwrite active predictions until the promotion script is explicitly run.",
            "Keep backend/data/generated/predictions.json, snapshots and frontend copies as the rollback source.",
            "If promoted later, archive active predictions before replacement and restore those archives on rollback.",
        ],
        "promotion_script_prepared": "backend/scripts/promote_full_stats_engine_v2_30.py",
    }
    publish(payload, OUTPUT)
    print(f"V2.30 promotion decision: {decision}; blockers={len(blockers)}")
    if blockers:
        raise SystemExit("V2.30 candidate has serious blockers; active promotion refused.")


if __name__ == "__main__":
    main()
