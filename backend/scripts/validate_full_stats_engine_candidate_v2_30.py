"""Validate the V2.30 full stats-enriched engine candidate bundle."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.full_stats_engine_v2_30_utils import publish
from backend.scripts.pipeline_utils import DATA_DIR, load_json, utc_now

OUTPUT = "full_stats_engine_candidate_validation_v2_30.json"
PROTECTED = [
    "backend/data/generated/predictions.json",
    "backend/data/snapshots/predictions.json",
    "frontend/src/assets/data/predictions.json",
    "backend/data/generated/quant_engine_v2_2_results.json",
    "backend/data/generated/optuna_study_summary_v2_2.json",
]
REQUIRED_GENERATED = [
    "full_stats_lagged_features_v2_30.json",
    "full_stats_feature_leakage_audit_v2_30.json",
    "full_stats_enriched_engine_v2_30_results.json",
    "full_stats_engine_promotion_decision_v2_30.json",
    "predictions_full_stats_candidate_v2_30.json",
    "full_stats_scenario_aware_matrix_v2_30.json",
    "full_stats_engine_road_to_trophy_impact_v2_30.json",
]


def git_output(args: list[str]) -> str:
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=False).stdout


def main() -> None:
    features = load_json(DATA_DIR / "generated" / "full_stats_lagged_features_v2_30.json")
    leakage = load_json(DATA_DIR / "generated" / "full_stats_feature_leakage_audit_v2_30.json")
    results = load_json(DATA_DIR / "generated" / "full_stats_enriched_engine_v2_30_results.json")
    decision = load_json(DATA_DIR / "generated" / "full_stats_engine_promotion_decision_v2_30.json")
    scenario = load_json(DATA_DIR / "generated" / "full_stats_scenario_aware_matrix_v2_30.json")
    road = load_json(DATA_DIR / "generated" / "full_stats_engine_road_to_trophy_impact_v2_30.json")
    collection = load_json(DATA_DIR / "generated" / "api_football_full_collection_summary_v2_29.json")
    protected_diff = git_output(["git", "diff", "--", *PROTECTED])
    raw_cache_status = git_output(["git", "status", "--short", "backend/data/cache/api_football/historical_stats"])
    large_files = git_output(["find", ".", "-type", "f", "-size", "+10M", "-not", "-path", "./.git/*", "-not", "-path", "./frontend/node_modules/*", "-print"])
    grep = git_output(["git", "grep", "-n", r"API_FOOTBALL_KEY\|x-apisports-key", "--", ".", ":!.env.example"])
    scripts = "\n".join(path.read_text(encoding="utf-8") for path in ROOT.glob("backend/scripts/*v2_30.py"))
    literal_secret = bool(re.search(r"x-apisports-key\s*:\s*['\"][^'\"]+|API_FOOTBALL_KEY\s*=\s*['\"][^'\"]+", scripts, re.I))
    generated_exist = {name: (DATA_DIR / "generated" / name).exists() for name in REQUIRED_GENERATED}
    snapshot_exist = {name: (DATA_DIR / "snapshots" / name).exists() for name in REQUIRED_GENERATED if name != "full_stats_enriched_engine_v2_30_results.json"}
    frontend_exist = {name: (ROOT / "frontend" / "src" / "assets" / "data" / name).exists() for name in REQUIRED_GENERATED if name != "full_stats_enriched_engine_v2_30_results.json"}
    checks: dict[str, bool] = {
        "collection_complete": collection.get("units_remaining") == 0 and collection.get("ready_for_model_retest") is True,
        "features_created": bool(features.get("features")),
        "features_use_full_collection": (
            features["source_collection"].get("units_total") == collection.get("units_total")
            and features["source_collection"].get("units_completed") == collection.get("units_completed")
            and features["source_collection"].get("units_remaining") == 0
            and features["source_collection"].get("ready_for_model_retest") is True
        ),
        "leakage_audit_passed": leakage.get("passed") is True,
        "xg_missing_not_invented": features["feature_policy"].get("xg_missing_not_invented") is True,
        "lineups_excluded_from_predictive_features": features["feature_policy"].get("lineups_used_as_predictive_feature") is False,
        "candidate_evaluated": bool(results["metrics"]["test"]["full_stats_candidate"]),
        "models_compared": all(key in results["models_compared"] for key in ("A_quant_hybrid_v2_2_active", "B_stats_enriched_full_v2_30", "C_ensemble_quant_plus_stats", "D_coverage_aware_full_stats")),
        "promotion_decision_documented": decision["decision"] in {"recommend_promotion", "promote_with_reservations", "do_not_promote"},
        "active_predictions_not_overwritten": decision["active_predictions_overwritten"] is False,
        "candidate_predictions_generated": (DATA_DIR / "generated" / "predictions_full_stats_candidate_v2_30.json").exists(),
        "scenario_matrix_generated": bool(scenario["matches"]),
        "road_to_trophy_unchanged": road["road_to_the_trophy_changed"] is False,
        "protected_files_unchanged": protected_diff == "",
        "raw_cache_not_staged": raw_cache_status == "",
        "no_literal_secret_in_v2_30_scripts": not literal_secret,
        "required_generated_files_exist": all(generated_exist.values()),
        "required_snapshot_files_exist": all(snapshot_exist.values()),
        "required_frontend_files_exist": all(frontend_exist.values()),
    }
    warnings = []
    if grep.strip():
        warnings.append("Secret-name references exist in code checks or env loading; no literal key was detected in V2.30 scripts.")
    if large_files.strip():
        warnings.append("Repository contains files larger than 10MB; inspect before committing.")
    if decision["decision"] == "promote_with_reservations":
        warnings.append("Candidate is promotable under the user rule but did not strictly beat every baseline metric.")
    blocking = [key for key, value in checks.items() if not value]
    flat_expected = {
        "full_collection_consumed": checks["collection_complete"] and checks["features_use_full_collection"],
        "features_generated": checks["features_created"],
        "leakage_audit_passed": checks["leakage_audit_passed"],
        "candidate_trained": checks["candidate_evaluated"],
        "compared_to_quant_hybrid_v2_2": checks["models_compared"],
        "promotion_decision_documented": checks["promotion_decision_documented"],
        "user_rule_applied": decision.get("user_rule") == "Promote the richer-data engine unless a serious technical blocker is present.",
        "production_candidate_generated": checks["candidate_predictions_generated"],
        "scenario_aware_matrix_generated": checks["scenario_matrix_generated"],
        "road_to_trophy_impact_audited": checks["road_to_trophy_unchanged"],
        "public_engine_changed": not checks["protected_files_unchanged"],
        "active_predictions_changed": not checks["protected_files_unchanged"],
    }
    payload: dict[str, Any] = {
        "version": "v2.30",
        "generated_at": utc_now(),
        "passed": not blocking,
        **flat_expected,
        "checks": checks,
        "blocking_issues": blocking,
        "warnings": warnings,
        "promotion_decision": decision["decision"],
        "protected_files_checked": PROTECTED,
        "raw_cache_status": raw_cache_status.strip(),
        "large_files": [line for line in large_files.splitlines() if line.strip()],
    }
    publish(payload, OUTPUT)
    print(f"V2.30 validation: {'PASS' if payload['passed'] else 'FAIL'}")
    if blocking:
        raise SystemExit(blocking)


if __name__ == "__main__":
    main()
