"""Validate V2.28 stats-enriched engine candidate and scenario-aware matrix."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, utc_now, write_json

OUTPUT = "stats_enriched_engine_and_scenario_matrix_validation_v2_28.json"
PROTECTED = [
    "backend/data/generated/predictions.json", "backend/data/snapshots/predictions.json",
    "frontend/src/assets/data/predictions.json", "backend/data/generated/quant_engine_v2_2_results.json",
    "backend/data/generated/optuna_study_summary_v2_2.json", "backend/scripts/run_tournament_simulation_engine_v4_v2_21.py",
    "backend/simulation/tournament_engine_v3.py", "backend/simulation/tournament_engine_v4.py",
]


def publish(payload: dict[str, Any]) -> None:
    target = DATA_DIR / "generated" / OUTPUT
    write_json(payload, target)
    shutil.copy2(target, DATA_DIR / "snapshots" / OUTPUT)
    shutil.copy2(target, FRONTEND_DATA_DIR / OUTPUT)


def main() -> None:
    features = load_json(DATA_DIR / "generated" / "api_stats_lagged_features_v2_28.json")
    leakage = load_json(DATA_DIR / "generated" / "api_stats_feature_leakage_audit_v2_28.json")
    candidate = load_json(DATA_DIR / "generated" / "stats_enriched_engine_candidate_v2_28.json")
    scenario = load_json(DATA_DIR / "generated" / "scenario_aware_score_matrix_v2_28.json")
    germany = load_json(DATA_DIR / "generated" / "germany_curacao_scenario_matrix_audit_v2_28.json")
    contract = load_json(DATA_DIR / "generated" / "unified_match_outcome_distribution_contract_v2_28.json")
    diff = subprocess.run(["git", "diff", "--", *PROTECTED], cwd=ROOT, text=True, capture_output=True).stdout
    scripts = "\n".join(path.read_text(encoding="utf-8") for path in ROOT.glob("backend/scripts/*v2_28.py"))
    secret = bool(re.search(r"x-apisports-key\s*:\s*['\"][^'\"]+|API_FOOTBALL_KEY\s*=\s*['\"][^'\"]+", scripts, re.I))
    checks = {
        "stats_features_created": bool(features["features"]),
        "leakage_audit_passed": leakage["passed"] is True,
        "partial_coverage_handled": features["feature_policy"]["missingness_indicators"] and features["feature_policy"]["xg_missing_not_invented"],
        "candidate_evaluated": bool(candidate["metrics"]["test"]),
        "compared_to_quant_hybrid_v2_2": "comparison_to_quant_hybrid_v2_2" in candidate,
        "promotion_decision_documented": "promotion_recommendation" in candidate,
        "scenario_aware_matrix_created": bool(scenario["matches"]),
        "large_score_scenarios_visible": germany["new_scenario_view"]["large_win_visible"],
        "exact_score_percentages_decentered": scenario["matrix_policy"]["exact_score_percentages_decentered"],
        "unified_contract_designed": contract["status"] == "target_contract_designed_not_promoted",
        "public_engine_changed": bool(diff),
        "active_predictions_changed": bool(diff),
        "no_secret": not secret,
    }
    blocking = [key for key, value in checks.items() if key not in {"public_engine_changed", "active_predictions_changed"} and not value]
    if diff:
        blocking.append("protected_files_changed")
    payload = {
        "version": "v2.28", "generated_at": utc_now(),
        "passed": not blocking, **checks, "blocking_issues": blocking,
        "warnings": candidate.get("warnings", []) + ["Optuna was not run; candidate selection used a bounded validation grid."],
    }
    publish(payload)
    print(f"V2.28 stats-enriched engine and scenario matrix validation: {'PASS' if payload['passed'] else 'FAIL'}")
    if blocking:
        raise SystemExit(blocking)


if __name__ == "__main__":
    main()
