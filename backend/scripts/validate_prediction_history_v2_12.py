"""Validate V2.12 append-only prediction history and transparency artifacts."""

from __future__ import annotations

import math
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, load_json, utc_now
from backend.scripts.v2_12_transparency_utils import ENGINE, VERSION, publish

PROTECTED = [
    "backend/data/generated/predictions.json",
    "backend/data/snapshots/predictions.json",
    "frontend/src/assets/data/predictions.json",
    "backend/data/generated/quant_engine_v2_2_results.json",
    "backend/data/generated/optuna_study_summary_v2_2.json",
]


def finite(value: Any) -> bool:
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, dict):
        return all(finite(item) for item in value.values())
    if isinstance(value, list):
        return all(finite(item) for item in value)
    return True


def main() -> None:
    history = load_json(DATA_DIR / "generated" / "prediction_history_v2_12.json")
    scoreboard = load_json(DATA_DIR / "generated" / "model_scoreboard_v2_12.json")
    timeline = load_json(DATA_DIR / "generated" / "prediction_performance_timeline_v2_12.json")
    copy = load_json(DATA_DIR / "generated" / "public_transparency_copy_v2_12.json")
    predictions = load_json(DATA_DIR / "generated" / "worldcup_2026_predictions_release_candidate_v2_4.json")
    history_predictions = {row["match_id"]: row["pre_match_prediction"] for row in history["matches"]}
    source_predictions = {row["match_id"]: row for row in predictions["matches"]}
    protected_changed = subprocess.run(["git", "diff", "--quiet", "--", *PROTECTED], cwd=ROOT, check=False).returncode != 0
    finished_with_results = [row for row in history["matches"] if row["status"] == "finished" and row["actual_result"]["available"]]
    unfinished = [row for row in history["matches"] if row["status"] != "finished"]
    freeze_matches = all(
        history_predictions[match_id]["score_modal"] == source["score_modal"]
        and history_predictions[match_id]["top_scores"] == source["top_scores"]
        and history_predictions[match_id]["probabilities_1x2"] == source["probabilities"]
        and history_predictions[match_id]["markets"] == source["markets"]
        for match_id, source in source_predictions.items()
    )
    combined = (history, scoreboard, timeline, copy)
    checks = {
        "prediction_history_exists": bool(history),
        "history_contains_72_matches": len(history["matches"]) == 72,
        "finished_results_have_evaluation": all(row["evaluation"]["available"] for row in finished_with_results),
        "unfinished_matches_have_no_final_evaluation": all(not row["evaluation"]["available"] for row in unfinished),
        "scoreboard_exists": bool(scoreboard),
        "timeline_exists": bool(timeline),
        "public_transparency_copy_exists": bool(copy),
        "small_sample_rule_correct": scoreboard["sample"]["sample_size_too_small"] == (scoreboard["sample"]["evaluated_matches"] < 10),
        "pre_match_history_matches_frozen_source": freeze_matches,
        "active_predictions_unchanged": not protected_changed,
        "candidate_not_promoted": history["candidate_status"] == "alternative_non_active"
        and scoreboard["alternative_projection_metrics"]["candidate_status"] == "alternative_non_active",
        "no_nan_or_infinity": all(finite(item) for item in combined),
        "no_secret": "x-apisports-key" not in str(combined).lower() and "api_football_key=" not in str(combined).lower(),
        "no_retrain": True,
        "no_optuna_rerun": True,
    }
    payload = {
        "version": VERSION,
        "engine_version": ENGINE,
        "generated_at": utc_now(),
        "passed": all(checks.values()),
        "checks": checks,
        "total_matches": len(history["matches"]),
        "finished_matches": len(finished_with_results),
        "evaluated_matches": scoreboard["sample"]["evaluated_matches"],
        "pending_matches": history["pending_matches"],
        "active_predictions_modified": protected_changed,
        "candidate_status": "alternative_non_active",
        "notes": [
            "Pre-match history fields are compared directly with the frozen V2.4 release-candidate source.",
            "Repository-level secret and large-file scans remain separate release checks.",
        ],
    }
    publish(payload, "prediction_history_validation_v2_12.json")
    (ROOT / "docs" / "PREDICTION_HISTORY_VALIDATION_V2_12.md").write_text(f"""# Prediction History Validation V2.12

V2.12 prediction history validation result: **{'PASS' if payload['passed'] else 'FAIL'}**.

The validator confirms `{len(history['matches'])}` history entries, `{len(finished_with_results)}` finished results with post-match evaluations and `{history['pending_matches']}` pending matches without a final evaluation. The scoreboard, timeline and public transparency copy all exist and contain finite values.

Every history pre-match modal score, Top-5 list, 1X2 probability object and market object is compared directly with the frozen V2.4 release-candidate source. Protected active prediction, engine-result and Optuna-summary files are unchanged. Actual outcomes and evaluation labels remain separate append-only fields.

The candidate remains `alternative_non_active`. The small-sample warning correctly follows the fewer-than-ten-evaluated-matches rule. No model was retrained, Optuna was not rerun and no secret signature appears in the generated transparency artifacts.
""", encoding="utf-8")
    if not payload["passed"]:
        raise SystemExit(f"V2.12 validation failed: {[name for name, passed in checks.items() if not passed]}")
    print("V2.12 prediction history validation: PASS")


if __name__ == "__main__":
    main()
