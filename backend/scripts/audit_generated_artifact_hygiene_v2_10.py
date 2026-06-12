"""Classify modified repository artifacts after a matchday refresh."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR
from backend.scripts.v2_10_refresh_utils import ENGINE, PROTECTED_FILES, VERSION, git_changes, is_expected_refresh, publish
from backend.scripts.pipeline_utils import utc_now

MODEL_ARTIFACTS = {
    "backend/data/generated/quant_engine_v2_2_results.json",
    "backend/data/generated/optuna_study_summary_v2_2.json",
}
MANUAL_SOURCES = {"backend/data/data_sources.json", "backend/data/snapshots/data_sources.json"}
LEGACY_TOKENS = ("prediction_diversity_audit", "predictions_baseline", "predictions_elo", "worldcup_knockout_structure_v2_6")
EXPECTED_IMPLEMENTATION = {
    "README.md",
    "docs/FUTURE_ENGINE_BLUEPRINT.md",
    "docs/MANUAL_VALIDATION_CHECKLISTS.md",
    "docs/VALIDATION_LOG.md",
    "backend/scripts/v2_6_live_utils.py",
    "backend/scripts/fetch_worldcup_2026_results_v2_6.py",
    "backend/scripts/v2_7_consistency_utils.py",
    "backend/scripts/v2_9_dual_matrix_utils.py",
}


def category(path: str) -> str:
    if path in PROTECTED_FILES:
        return "active_prediction_file"
    if path in MODEL_ARTIFACTS:
        return "model_training_artifact"
    if path in MANUAL_SOURCES:
        return "manual_source_file"
    if is_expected_refresh(path) or "v2_10" in path or "_V2_10" in path or path in EXPECTED_IMPLEMENTATION:
        return "expected_refresh_artifact"
    if any(token in path for token in LEGACY_TOKENS):
        return "legacy_artifact"
    return "unexpected_change"


def main() -> None:
    manifest_path = DATA_DIR / "generated" / "matchday_refresh_manifest_v2_10.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    files = [{"path": path, "category": category(path), "preexisting_before_refresh": path in manifest.get("git_hygiene", {}).get("preexisting_modified_files", [])} for path in git_changes()]
    counts = Counter(row["category"] for row in files)
    monitored = [{
        "path": path,
        "exists": (ROOT / path).exists(),
        "modified": path in {row["path"] for row in files},
        "category": category(path),
    } for path in (
        *PROTECTED_FILES,
        "backend/data/generated/quant_engine_v2_2_results.json",
        "backend/data/generated/optuna_study_summary_v2_2.json",
        "backend/data/generated/worldcup_2026_results_v2_6.json",
        "backend/data/generated/worldcup_match_state_view_model_v2_7.json",
        "backend/data/generated/worldcup_tournament_simulation_conditioned_v2_6.json",
        "backend/data/generated/worldcup_tournament_simulation_candidate_v2_9.json",
    )]
    payload = {
        "generated_at": utc_now(), "version": VERSION, "engine_version": ENGINE,
        "files": files, "category_counts": dict(counts), "monitored_files": monitored,
        "active_prediction_files_protected": not any(row["modified"] for row in monitored if row["category"] == "active_prediction_file"),
        "unexpected_changes": [row for row in files if row["category"] == "unexpected_change"],
        "notes": ["Preexisting workspace changes are reported explicitly and are not automatically staged.", "Legacy artifacts are visible but are not matchday refresh outputs."],
    }
    publish(payload, "generated_artifact_hygiene_v2_10.json")
    (ROOT / "docs" / "GENERATED_ARTIFACT_HYGIENE_V2_10.md").write_text(f"""# Generated Artifact Hygiene V2.10

The hygiene audit classifies every currently modified or untracked repository file. Category counts: `{dict(counts)}`.

Active prediction files protected: `{payload['active_prediction_files_protected']}`. Unexpected changes: `{payload['unexpected_changes']}`.

Expected refresh artifacts include result overlays, evaluations, live standings, unified match state, conditioned active/candidate simulations, comparisons, projected campaigns and validations. Legacy baseline/Elo/diversity artifacts, manual source files, active prediction files and model-training artifacts are classified separately.

Preexisting workspace changes remain visible through `preexisting_before_refresh`; they are never silently described as new refresh output or automatically staged. Before commit, stage explicit V2.10 files only and investigate any active-prediction or model-training artifact marked modified.
""", encoding="utf-8")
    print(json.dumps({"category_counts": dict(counts), "active_prediction_files_protected": payload["active_prediction_files_protected"], "unexpected": len(payload["unexpected_changes"])}))


if __name__ == "__main__":
    main()
