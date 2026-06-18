"""Promote the V2.30 full-stats candidate for individual match predictions."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, utc_now, write_json

VERSION = "v2.30.1"
CANDIDATE = DATA_DIR / "generated" / "predictions_full_stats_candidate_v2_30.json"
DECISION = DATA_DIR / "generated" / "full_stats_engine_promotion_decision_v2_30.json"
VALIDATION = DATA_DIR / "generated" / "full_stats_engine_candidate_validation_v2_30.json"
RESULTS = DATA_DIR / "generated" / "full_stats_enriched_engine_v2_30_results.json"
ARCHIVE_DIR = DATA_DIR / "archives" / "v2_30_1_pre_full_stats_promotion"
MANIFEST_NAME = "full_stats_engine_promotion_manifest_v2_30_1.json"
ENGINE_MANIFEST_NAME = "active_prediction_engine_manifest.json"

ACTIVE_PATHS = {
    "generated": DATA_DIR / "generated" / "predictions.json",
    "snapshot": DATA_DIR / "snapshots" / "predictions.json",
    "frontend": FRONTEND_DATA_DIR / "predictions.json",
}
ARCHIVE_PATHS = {
    "generated": ARCHIVE_DIR / "predictions.generated.json",
    "snapshot": ARCHIVE_DIR / "predictions.snapshot.json",
    "frontend": ARCHIVE_DIR / "predictions.frontend.json",
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def assert_ready() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    decision = load_json(DECISION)
    validation = load_json(VALIDATION)
    results = load_json(RESULTS)
    blockers = []
    if decision.get("decision") != "recommend_promotion":
        blockers.append("decision_not_recommend_promotion")
    if decision.get("serious_blockers"):
        blockers.append("serious_blockers_present")
    if validation.get("passed") is not True:
        blockers.append("v2_30_validation_failed")
    if validation.get("blocking_issues"):
        blockers.append("v2_30_blocking_issues_present")
    if validation.get("active_predictions_changed") is not False:
        blockers.append("v2_30_active_predictions_already_changed")
    if validation.get("public_engine_changed") is not False:
        blockers.append("v2_30_public_engine_already_changed")
    if not CANDIDATE.exists():
        blockers.append("candidate_predictions_missing")
    manifest_exists = (DATA_DIR / "generated" / MANIFEST_NAME).exists()
    if ARCHIVE_DIR.exists() and not manifest_exists:
        blockers.append("archive_dir_already_exists_refuse_to_overwrite")
    if blockers:
        raise SystemExit(f"Promotion refused: {blockers}")
    return decision, validation, results


def copy_to_public(name: str, payload: dict[str, Any]) -> None:
    for base in (DATA_DIR / "generated", DATA_DIR / "snapshots", FRONTEND_DATA_DIR):
        write_json(payload, base / name)


def activate_predictions(candidate: list[dict[str, Any]]) -> list[dict[str, Any]]:
    active = []
    for row in candidate:
        item = dict(row)
        item["engine_version"] = "stats_enriched_full_v2.30"
        item["engine_status"] = "active"
        item["active_engine_replaced"] = True
        item["activated_in"] = VERSION
        overlay = dict(item.get("full_stats_overlay", {}))
        overlay["status"] = "active_match_prediction_engine"
        item["full_stats_overlay"] = overlay
        active.append(item)
    return active


def main() -> None:
    decision, validation, results = assert_ready()
    candidate = activate_predictions(load_json(CANDIDATE))
    existing_manifest = (DATA_DIR / "generated" / MANIFEST_NAME).exists()
    if not ARCHIVE_DIR.exists():
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=False)
    archive_entries = []
    for key, source in ACTIVE_PATHS.items():
        archive = ARCHIVE_PATHS[key]
        if not archive.exists():
            shutil.copy2(source, archive)
        archive_entries.append({"role": key, "active_path": rel(source), "archive_path": rel(archive)})
    for target in ACTIVE_PATHS.values():
        write_json(candidate, target)
    comparison = results["comparison_to_quant_hybrid_v2_2"]
    metrics = results["metrics"]["test"]
    manifest = {
        "version": VERSION,
        "promoted_engine": "stats_enriched_full_v2_30",
        "previous_engine": "quant_hybrid_v2.2",
        "promotion_reason": "Full stats candidate improves test log loss, Brier and accuracy and follows user production rule favoring richer-data engine.",
        "promotion_decision_source": rel(DECISION),
        "promoted_at": load_json(DATA_DIR / "generated" / MANIFEST_NAME).get("promoted_at") if existing_manifest else utc_now(),
        "active_predictions_changed": True,
        "road_to_trophy_changed": False,
        "optuna_rerun": False,
        "rollback_available": True,
        "rollback_script": "backend/scripts/rollback_full_stats_engine_v2_30_1.py",
        "archive_paths": archive_entries,
        "metrics": {
            "previous": {
                "test_accuracy": metrics["quant_hybrid_v2_2"]["accuracy_1x2"],
                "test_log_loss": metrics["quant_hybrid_v2_2"]["log_loss_1x2"],
                "test_brier": metrics["quant_hybrid_v2_2"]["brier_score_1x2"],
            },
            "promoted": {
                "test_accuracy": metrics["full_stats_candidate"]["accuracy_1x2"],
                "test_log_loss": metrics["full_stats_candidate"]["log_loss_1x2"],
                "test_brier": metrics["full_stats_candidate"]["brier_score_1x2"],
            },
            "delta": comparison["delta_test"],
        },
        "blocking_issues": [],
        "source_validation": {
            "v2_30_validation_passed": validation["passed"],
            "promotion_decision": decision["decision"],
        },
    }
    engine_manifest = {
        "version": VERSION,
        "active_prediction_engine": "stats_enriched_full_v2_30",
        "previous_prediction_engine": "quant_hybrid_v2.2",
        "activated_in": VERSION,
        "public_label": "SimuAI",
        "technical_label": "Full Stats Engine",
        "uses_api_football_lagged_stats": True,
        "uses_xg_when_available": True,
        "uses_missingness_indicators": True,
        "road_to_trophy_engine_changed": False,
        "promotion_manifest": f"backend/data/generated/{MANIFEST_NAME}",
    }
    copy_to_public(MANIFEST_NAME, manifest)
    copy_to_public(ENGINE_MANIFEST_NAME, engine_manifest)
    print(f"{VERSION} promoted full stats engine for {len(candidate)} match predictions")


if __name__ == "__main__":
    main()
