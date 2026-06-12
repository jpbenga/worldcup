"""Shared operational refresh helpers for V2.10."""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, write_json

ROOT = Path(__file__).resolve().parents[2]
VERSION = "v2.10"
ENGINE = "quant_hybrid_v2.2"
CANDIDATE = "score_matrix_candidate_v2.8"
PROTECTED_FILES = (
    "backend/data/generated/predictions.json",
    "backend/data/snapshots/predictions.json",
    "frontend/src/assets/data/predictions.json",
    "backend/data/generated/quant_engine_v2_2_results.json",
    "backend/data/generated/optuna_study_summary_v2_2.json",
)
EXPECTED_REFRESH_PREFIXES = (
    "backend/data/generated/worldcup_2026_",
    "backend/data/generated/worldcup_projected_campaign_v2_6.json",
    "backend/data/generated/worldcup_tournament_simulation_conditioned_v2_6.json",
    "backend/data/generated/worldcup_tournament_simulation_candidate_v2_9.json",
    "backend/data/generated/worldcup_projected_campaign_candidate_v2_9.json",
    "backend/data/generated/worldcup_live_group_standings_v2_7.json",
    "backend/data/generated/worldcup_match_state_view_model_v2_7.json",
    "backend/data/generated/result_consistency_validation_v2_7.json",
    "backend/data/generated/active_vs_candidate_simulation_comparison_v2_9.json",
    "backend/data/generated/dual_matrix_validation_v2_9.json",
    "backend/data/snapshots/worldcup_2026_",
    "backend/data/snapshots/worldcup_projected_campaign_v2_6.json",
    "backend/data/snapshots/worldcup_tournament_simulation_conditioned_v2_6.json",
    "backend/data/snapshots/worldcup_tournament_simulation_candidate_v2_9.json",
    "backend/data/snapshots/worldcup_projected_campaign_candidate_v2_9.json",
    "backend/data/snapshots/worldcup_live_group_standings_v2_7.json",
    "backend/data/snapshots/worldcup_match_state_view_model_v2_7.json",
    "backend/data/snapshots/result_consistency_validation_v2_7.json",
    "backend/data/snapshots/active_vs_candidate_simulation_comparison_v2_9.json",
    "backend/data/snapshots/dual_matrix_validation_v2_9.json",
    "frontend/src/assets/data/worldcup_2026_",
    "frontend/src/assets/data/worldcup_projected_campaign_v2_6.json",
    "frontend/src/assets/data/worldcup_tournament_simulation_conditioned_v2_6.json",
    "frontend/src/assets/data/worldcup_tournament_simulation_candidate_v2_9.json",
    "frontend/src/assets/data/worldcup_projected_campaign_candidate_v2_9.json",
    "frontend/src/assets/data/worldcup_live_group_standings_v2_7.json",
    "frontend/src/assets/data/worldcup_match_state_view_model_v2_7.json",
    "frontend/src/assets/data/result_consistency_validation_v2_7.json",
    "frontend/src/assets/data/active_vs_candidate_simulation_comparison_v2_9.json",
    "frontend/src/assets/data/dual_matrix_validation_v2_9.json",
    "docs/WORLDCUP_2026_",
    "docs/WORLDCUP_TOURNAMENT_SIMULATION_CONDITIONED_V2_6.md",
    "docs/WORLDCUP_LIVE_GROUP_STANDINGS_V2_7.md",
    "docs/WORLDCUP_MATCH_STATE_VIEW_MODEL_V2_7.md",
    "docs/RESULT_CONSISTENCY_VALIDATION_V2_7.md",
    "docs/ACTIVE_VS_CANDIDATE_SIMULATION_COMPARISON_V2_9.md",
    "docs/DUAL_MATRIX_VALIDATION_V2_9.md",
)


def publish(payload: Any, name: str, skip_frontend: bool = False) -> None:
    generated = DATA_DIR / "generated" / name
    write_json(payload, generated)
    shutil.copy2(generated, DATA_DIR / "snapshots" / name)
    if not skip_frontend:
        shutil.copy2(generated, FRONTEND_DATA_DIR / name)


def sha256(path: str) -> str | None:
    target = ROOT / path
    if not target.exists():
        return None
    digest = hashlib.sha256()
    with target.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def protected_hashes() -> dict[str, str | None]:
    return {path: sha256(path) for path in PROTECTED_FILES}


def git_changes() -> list[str]:
    result = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, check=True, text=True, capture_output=True)
    return sorted({line[3:] for line in result.stdout.splitlines() if len(line) >= 4})


def is_expected_refresh(path: str) -> bool:
    return any(path.startswith(prefix) for prefix in EXPECTED_REFRESH_PREFIXES)


def child_environment(skip_frontend: bool) -> dict[str, str]:
    environment = os.environ.copy()
    if skip_frontend:
        environment["MATCHDAY_SKIP_FRONTEND_COPY"] = "1"
    else:
        environment.pop("MATCHDAY_SKIP_FRONTEND_COPY", None)
    return environment
