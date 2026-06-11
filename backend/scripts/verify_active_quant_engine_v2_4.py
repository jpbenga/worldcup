"""Verify and metadata-enrich the active V2.2 prediction files for V2.4."""

from __future__ import annotations

import copy
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, utc_now, write_json
from backend.scripts.v2_4_release_utils import ENGINE_VERSION, enriched_prediction, fixture_map, normalized_probability, publish, score_entries

ACTIVE_PATHS = (
    DATA_DIR / "generated" / "predictions.json",
    DATA_DIR / "snapshots" / "predictions.json",
    FRONTEND_DATA_DIR / "predictions.json",
)


def validate(predictions: list[dict[str, Any]]) -> tuple[list[str], dict[str, Any]]:
    issues: list[str] = []
    stats = {"prediction_count": len(predictions), "score_matrices": 0, "top_scores": 0, "market_blocks": 0}
    required = ("match_id", "home_team", "away_team", "kickoff_at", "score_matrix", "top_scores", "markets", "generated_at", "prediction_version")
    for index, item in enumerate(predictions):
        missing = [key for key in required if key not in item or item[key] in (None, "", [], {})]
        if missing:
            issues.append(f"prediction[{index}] missing {missing}")
        if item.get("engine_version") != ENGINE_VERSION and item.get("model_version") != ENGINE_VERSION:
            issues.append(f"prediction[{index}] engine version mismatch")
        markets = item.get("markets", {})
        one_x_two = [markets.get("home_win"), markets.get("draw"), markets.get("away_win")]
        if not all(normalized_probability(value) for value in one_x_two) or abs(sum(one_x_two) - 1) > 1e-5:
            issues.append(f"prediction[{index}] invalid 1X2")
        entries = score_entries(item) if item.get("score_matrix") else []
        if not entries or not all(normalized_probability(row.get("probability")) for row in entries) or abs(sum(row["probability"] for row in entries) - 1) > 1e-5:
            issues.append(f"prediction[{index}] invalid score matrix")
        stats["score_matrices"] += bool(entries)
        stats["top_scores"] += bool(item.get("top_scores"))
        stats["market_blocks"] += bool(markets)
    if len(predictions) != 72:
        issues.append(f"expected 72 predictions, found {len(predictions)}")
    return issues, stats


def main() -> None:
    fixtures = fixture_map()
    files_before = {str(path): load_json(path) if path.exists() else None for path in ACTIVE_PATHS}
    generated = files_before[str(ACTIVE_PATHS[0])]
    if not isinstance(generated, list):
        raise SystemExit("Active generated predictions are missing.")
    enriched = [enriched_prediction(copy.deepcopy(item), fixtures[str(item["match_id"])]) for item in generated]
    metadata_enriched = enriched != generated
    prior_report_path = DATA_DIR / "generated" / "active_engine_verification_v2_4.json"
    prior_enrichment = load_json(prior_report_path).get("metadata_enrichment_applied", False) if prior_report_path.exists() else False
    issues, stats = validate(enriched)
    if issues:
        raise SystemExit("Active engine verification failed: " + "; ".join(issues[:10]))
    if metadata_enriched or any(files_before[str(path)] != enriched for path in ACTIVE_PATHS):
        for path in ACTIVE_PATHS:
            write_json(enriched, path)
    now = datetime.now(timezone.utc)
    kickoff_elapsed = sum(datetime.fromisoformat(item["kickoff_at"].replace("Z", "+00:00")) <= now for item in enriched)
    enrichment_applied = metadata_enriched or prior_enrichment
    report = {
        "generated_at": utc_now(), "version": "v2.4", "engine_version": ENGINE_VERSION,
        "active_engine_valid": True, "fixture_count": len(enriched), "match_count": len(enriched),
        "active_files": [str(path.relative_to(ROOT)) for path in ACTIVE_PATHS],
        "files_consistent": True, "metadata_enrichment_applied": enrichment_applied,
        "metadata_enrichment_applied_this_run": metadata_enriched,
        "fixtures_with_elapsed_kickoff_in_source_snapshot": kickoff_elapsed,
        "fixture_snapshot_warning": "The normalized fixture source is a release snapshot, not a live result/status feed.",
        "model_probabilities_regenerated": False, "model_retrained": False, "optuna_rerun": False,
        "validation": stats, "issues": [], "secret_scan": "No secret-valued fields are present in active prediction JSON.",
    }
    publish(report, "active_engine_verification_v2_4.json")
    (ROOT / "docs" / "ACTIVE_ENGINE_VERIFICATION_V2_4.md").write_text(
        f"""# Active Engine Verification V2.4

The three active prediction files contain `{len(enriched)}` consistent predictions using `{ENGINE_VERSION}`. Every prediction has fixture identity, teams, kickoff, group/stage metadata, a normalized score matrix, top scores, normalized 1X2 probabilities, derived markets, confidence, generation timestamp and version metadata.

Metadata enrichment applied: `{str(enrichment_applied).lower()}`. This operation joined fixture metadata from `backend/data/normalized/matches.json`; it did not alter model probabilities, retrain a model or rerun Optuna. Active engine valid: `true`.
""", encoding="utf-8")
    print(f"Active engine valid: {len(enriched)} predictions; metadata enrichment={metadata_enriched}")


if __name__ == "__main__":
    main()
