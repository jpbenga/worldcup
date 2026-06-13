"""Shared helpers for the V2.17 local operator workflow."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, utc_now, write_json

VERSION = "v2.17"
CRITICAL_SCRIPTS = [
    "backend/scripts/run_matchday_refresh_v2_10.py",
    "backend/scripts/validate_matchday_refresh_v2_10.py",
]
CRITICAL_DATA = [
    "backend/data/generated/predictions.json",
    "backend/data/generated/quant_engine_v2_2_results.json",
    "backend/data/generated/road_to_the_trophy_engine.json",
]
CRITICAL_ASSETS = [
    "frontend/src/assets/data/predictions.json",
    "frontend/src/assets/data/road_to_the_trophy_engine.json",
]


def publish(name: str, payload: dict[str, Any], frontend: bool = False) -> None:
    generated = DATA_DIR / "generated" / name
    write_json(payload, generated)
    shutil.copy2(generated, DATA_DIR / "snapshots" / name)
    if frontend:
        shutil.copy2(generated, FRONTEND_DATA_DIR / name)


def command_version(command: str, argument: str = "--version") -> dict[str, Any]:
    executable = shutil.which(command)
    if not executable:
        return {"available": False, "version": None}
    result = subprocess.run([executable, argument], text=True, capture_output=True)
    return {"available": result.returncode == 0, "version": (result.stdout or result.stderr).strip().splitlines()[0]}


def git_status() -> dict[str, Any]:
    result = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, text=True, capture_output=True)
    lines = result.stdout.splitlines()
    return {
        "dirty": bool(lines),
        "modified_count": sum(not line.startswith("??") for line in lines),
        "untracked_count": sum(line.startswith("??") for line in lines),
        "files": [line[3:] for line in lines],
        "notes": ["Pre-existing Matchday refresh files are intentionally outside V2.17 scope."] if lines else [],
    }


def api_key_status() -> dict[str, bool]:
    env_file = ROOT / ".env"
    present = bool(os.getenv("API_FOOTBALL_KEY"))
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8", errors="ignore").splitlines():
            if line.strip().startswith("API_FOOTBALL_KEY=") and line.partition("=")[2].strip():
                present = True
                break
    return {"env_file_present": env_file.exists(), "api_key_present": present, "value_printed": False}


def last_refresh() -> dict[str, Any]:
    path = DATA_DIR / "generated" / "matchday_refresh_manifest_v2_10.json"
    if not path.exists():
        return {"available": False, "generated_at": None, "status": "unknown"}
    manifest = load_json(path)
    return {
        "available": True,
        "generated_at": manifest.get("generated_at"),
        "status": manifest.get("status", "unknown"),
        "simulation_count": manifest.get("simulation_count"),
        "result_summary": manifest.get("result_summary", {}),
    }


def freshness_status() -> dict[str, Any]:
    refresh = last_refresh()
    results_path = DATA_DIR / "generated" / "worldcup_2026_results_v2_6.json"
    results = load_json(results_path) if results_path.exists() else {}
    generated_at = refresh.get("generated_at")
    age_hours = None
    if generated_at:
        date = datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
        age_hours = round((datetime.now(timezone.utc) - date).total_seconds() / 3600, 1)
    status = "unknown" if age_hours is None else "fresh" if age_hours <= 12 else "stale"
    finished = results.get("finished_count", refresh.get("result_summary", {}).get("finished_matches", 0))
    live = results.get("live_count", refresh.get("result_summary", {}).get("live_matches", 0))
    upcoming = results.get("not_started_count", refresh.get("result_summary", {}).get("not_started_matches", 0))
    return {
        "version": VERSION,
        "generated_at": utc_now(),
        "last_matchday_refresh_at": generated_at,
        "refresh_age_hours": age_hours,
        "real_results_locked": finished,
        "live_matches": live,
        "upcoming_matches": upcoming,
        "finished_matches": finished,
        "road_to_the_trophy_engine": "SimuAI Tournament Engine V3",
        "pre_match_engine": "quant_hybrid_v2.2",
        "data_status": status,
        "operator_message": "Run the operator refresh before publishing." if status != "fresh" else "Data refresh is recent.",
        "public_message": f"Données mises à jour : {generated_at or 'date inconnue'}. Résultats officiels intégrés : {finished}.",
    }


def operator_audit() -> dict[str, Any]:
    python = {"available": True, "version": sys.version.split()[0]}
    node, npm = command_version("node"), command_version("npm")
    scripts = {path: (ROOT / path).exists() for path in CRITICAL_SCRIPTS}
    data = {path: (ROOT / path).exists() for path in CRITICAL_DATA}
    assets = {path: (ROOT / path).exists() for path in CRITICAL_ASSETS}
    git = git_status()
    blockers = [path for path, exists in {**scripts, **data, **assets}.items() if not exists]
    if not node["available"] or not npm["available"]:
        blockers.append("Node/npm unavailable")
    warnings = ["Git worktree is dirty; review scope before commit."] if git["dirty"] else []
    return {
        "version": VERSION,
        "generated_at": utc_now(),
        "environment": {
            "python_available": python["available"], "python_version": python["version"],
            "node_available": node["available"], "node_version": node["version"],
            "npm_available": npm["available"], "npm_version": npm["version"],
            "frontend_package_json": (ROOT / "frontend/package.json").exists(),
        },
        "critical_scripts": scripts, "critical_data": data, "frontend_assets": assets,
        "documentation": {"operations_runbook": (ROOT / "docs/OPERATIONS_RUNBOOK.md").exists()},
        "api_key": api_key_status(), "last_refresh": last_refresh(), "git_status": git,
        "operator_readiness": "fail" if blockers else "warning" if warnings else "pass",
        "blocking_issues": blockers, "warnings": warnings,
    }
