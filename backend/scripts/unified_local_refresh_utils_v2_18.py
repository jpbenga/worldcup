"""Shared helpers for the unified local refresh."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, utc_now, write_json

VERSION = "v2.18"
PROTECTED_PREDICTIONS = [
    "backend/data/generated/predictions.json", "backend/data/snapshots/predictions.json",
    "frontend/src/assets/data/predictions.json", "backend/data/generated/quant_engine_v2_2_results.json",
    "backend/data/generated/optuna_study_summary_v2_2.json",
]


def publish(name: str, payload: dict[str, Any], frontend: bool = False) -> None:
    generated = DATA_DIR / "generated" / name
    write_json(payload, generated)
    shutil.copy2(generated, DATA_DIR / "snapshots" / name)
    if frontend:
        shutil.copy2(generated, FRONTEND_DATA_DIR / name)


def file_hash(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def protected_hashes() -> dict[str, str | None]:
    return {path: file_hash(ROOT / path) for path in PROTECTED_PREDICTIONS}


def run(script: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, f"backend/scripts/{script}", *args], cwd=ROOT, text=True, capture_output=True)


def refresh_decision(simulations: int = 50000, force: bool = False) -> dict[str, Any]:
    results_path = DATA_DIR / "generated/worldcup_2026_results_v2_6.json"
    matchday_path = DATA_DIR / "generated/matchday_refresh_manifest_v2_10.json"
    sim_path = DATA_DIR / "generated/tournament_simulation_engine_v4_results_v2_21.json"
    engine_path = DATA_DIR / "generated/road_to_the_trophy_engine.json"
    freshness_path = DATA_DIR / "generated/data_freshness_status_v2_17.json"
    validation_path = DATA_DIR / "generated/unified_local_refresh_validation_v2_18.json"
    coherence_path = DATA_DIR / "generated/road_to_the_trophy_coherent_view_model_v2_21.json"
    results = load_json(results_path) if results_path.exists() else {}
    matchday = load_json(matchday_path) if matchday_path.exists() else {}
    simulation = load_json(sim_path) if sim_path.exists() else {}
    engine = load_json(engine_path) if engine_path.exists() else {}
    freshness = load_json(freshness_path) if freshness_path.exists() else {}
    finished = results.get("finished_count", 0)
    locked = simulation.get("real_results_locked", 0)
    reasons = []
    if force: reasons.append("force_requested")
    if not matchday_path.exists(): reasons.append("matchday_manifest_missing")
    if freshness.get("data_status") in ("stale", "unknown"): reasons.append(f"data_{freshness.get('data_status')}")
    if matchday.get("simulation_count") != simulations: reasons.append("simulation_count_changed")
    if finished != locked: reasons.append(f"official_results_locked_mismatch:{locked}->{finished}")
    if engine.get("source_engine") != "tournament_simulation_engine_v4": reasons.append("road_to_the_trophy_engine_version_mismatch")
    if not coherence_path.exists(): reasons.append("coherent_road_to_the_trophy_view_model_missing")
    if not validation_path.exists(): reasons.append("unified_validation_missing")
    frontend_missing = [name for name in ("worldcup_2026_results_v2_6.json", "road_to_the_trophy_engine.json", "data_freshness_status_v2_17.json") if not (FRONTEND_DATA_DIR / name).exists()]
    return {
        "version": VERSION, "generated_at": utc_now(), "refresh_needed": bool(reasons), "reasons": reasons,
        "transparency_rebuild_needed": force or finished != locked or not matchday_path.exists(),
        "road_to_the_trophy_rebuild_needed": force or finished != locked or engine.get("source_engine") != "tournament_simulation_engine_v4" or not coherence_path.exists(),
        "frontend_copy_needed": force or bool(frontend_missing),
        "safe_to_skip_heavy_simulation": not (force or finished != locked or matchday.get("simulation_count") != simulations),
        "finished_results": finished, "v3_locked_results": locked, "requested_simulations": simulations,
        "frontend_assets_missing": frontend_missing,
    }


def rebuild_v4() -> None:
    from backend.scripts.run_tournament_simulation_engine_v4_v2_21 import main
    from backend.scripts.build_road_to_the_trophy_scenario_timeline_v2_22 import main as build_timeline

    main()
    build_timeline()
