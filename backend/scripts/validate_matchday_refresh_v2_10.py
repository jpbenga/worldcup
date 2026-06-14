"""Validate the complete V2.10 operational matchday refresh."""

from __future__ import annotations

import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, utc_now
from backend.scripts.v2_10_refresh_utils import ENGINE, VERSION, PROTECTED_FILES, publish


def load(name: str) -> Any:
    return json.loads((DATA_DIR / "generated" / name).read_text())


def finite(value: Any) -> bool:
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, dict):
        return all(finite(item) for item in value.values())
    if isinstance(value, list):
        return all(finite(item) for item in value)
    return True


def secret_scan_lines() -> list[str]:
    pattern = re.compile(r"AKIA[0-9A-Z]{16}|-----BEGIN (RSA|OPENSSH|EC|DSA) PRIVATE KEY-----")
    if shutil.which("rg"):
        scan = subprocess.run(
            ["rg", "-n", "--hidden", "--glob", "!.git/**", "--glob", "!node_modules/**", pattern.pattern],
            cwd=ROOT, text=True, capture_output=True,
        )
        return scan.stdout.splitlines()

    lines = []
    excluded = {".git", "node_modules", "dist", "__pycache__", ".angular"}
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in excluded for part in path.parts) or path.stat().st_size > 2 * 1024 * 1024:
            continue
        try:
            for number, line in enumerate(path.read_text(errors="ignore").splitlines(), 1):
                if pattern.search(line):
                    lines.append(f"{path.relative_to(ROOT)}:{number}:{line.strip()}")
        except OSError:
            continue
    return lines


def main() -> None:
    required = {
        "manifest": "matchday_refresh_manifest_v2_10.json",
        "results": "worldcup_2026_results_v2_6.json",
        "evaluation": "worldcup_2026_prediction_evaluation_v2_6.json",
        "standings": "worldcup_live_group_standings_v2_7.json",
        "match_state": "worldcup_match_state_view_model_v2_7.json",
        "active_simulation": "worldcup_tournament_simulation_conditioned_v2_6.json",
        "candidate_simulation": "worldcup_tournament_simulation_candidate_v2_9.json",
        "simulation_comparison": "active_vs_candidate_simulation_comparison_v2_9.json",
        "active_campaign": "worldcup_projected_campaign_v2_6.json",
        "candidate_campaign": "worldcup_projected_campaign_candidate_v2_9.json",
        "result_validation": "result_consistency_validation_v2_7.json",
        "dual_validation": "dual_matrix_validation_v2_9.json",
        "hygiene": "generated_artifact_hygiene_v2_10.json",
    }
    exists = {key: (DATA_DIR / "generated" / name).exists() for key, name in required.items()}
    artifacts = {key: load(name) for key, name in required.items() if exists[key]}
    manifest = artifacts.get("manifest", {})
    protected_unchanged = manifest.get("model_integrity", {}).get("protected_hashes_before") == manifest.get("model_integrity", {}).get("protected_hashes_after")
    large_files = [str(path.relative_to(ROOT)) for path in DATA_DIR.rglob("*") if path.is_file() and path.stat().st_size > 10 * 1024 * 1024]
    secret_lines = secret_scan_lines()
    checks = {
        **{f"{key}_exists": value for key, value in exists.items()},
        "manifest_pass": manifest.get("status") == "pass",
        "result_consistency_pass": artifacts.get("result_validation", {}).get("passed") is True,
        "dual_matrix_validation_pass": artifacts.get("dual_validation", {}).get("passed") is True,
        "candidate_simulation_count_matches_manifest": artifacts.get("candidate_simulation", {}).get("simulation_count") == manifest.get("simulation_count"),
        "active_simulation_count_matches_manifest": artifacts.get("active_simulation", {}).get("simulation_count") == manifest.get("simulation_count"),
        "active_predictions_unchanged": protected_unchanged and not manifest.get("model_integrity", {}).get("pre_match_predictions_modified", True),
        "active_prediction_files_protected_by_hygiene": artifacts.get("hygiene", {}).get("active_prediction_files_protected") is True,
        "model_unchanged": protected_unchanged,
        "optuna_not_run": manifest.get("model_integrity", {}).get("optuna_run") is False,
        "retrain_not_run": manifest.get("model_integrity", {}).get("retrain_run") is False,
        "all_artifacts_finite": all(finite(value) for value in artifacts.values()),
        "no_unjustified_large_files": not large_files,
        "no_secret_literal_detected": not secret_lines,
    }
    payload = {
        "generated_at": utc_now(), "version": VERSION, "engine_version": ENGINE, "passed": all(checks.values()),
        "checks": checks, "large_files": large_files, "secret_scan_unexpected_lines": secret_lines,
        "protected_files": list(PROTECTED_FILES), "model_retrained": False, "optuna_rerun": False,
    }
    publish(payload, "matchday_refresh_validation_v2_10.json")
    (ROOT / "docs" / "MATCHDAY_REFRESH_VALIDATION_V2_10.md").write_text(f"""# Matchday Refresh Validation V2.10

Validation status: **{'PASS' if payload['passed'] else 'FAIL'}**.

The validator checks the refresh manifest, result/evaluation/standings/match-state layers, active and candidate conditioned simulations, their comparison, both projected-campaign proxies, V2.7 result consistency and V2.9 dual-matrix validation.

Protected active predictions and model artifacts unchanged: `{protected_unchanged}`. Retraining and Optuna were not run. Unjustified files above 10 MB: `{large_files}`. Unexpected secret scan lines: `{secret_lines}`.

The validation confirms operational coherence only. It never promotes the candidate or changes frozen pre-match probabilities.
""", encoding="utf-8")
    if not payload["passed"]:
        raise SystemExit(f"V2.10 validation failed: {[key for key, value in checks.items() if not value]}")
    print("V2.10 matchday refresh validation: PASS")


if __name__ == "__main__":
    main()
