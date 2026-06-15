"""Validate the V2.26 match-matrix and tournament-simulation coherence audit."""

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

OUTPUT = "match_matrix_and_simulation_coherence_validation_v2_26.json"
ACTIVE = [
    "backend/data/generated/predictions.json",
    "backend/data/snapshots/predictions.json",
    "frontend/src/assets/data/predictions.json",
    "backend/data/generated/quant_engine_v2_2_results.json",
    "backend/data/generated/optuna_study_summary_v2_2.json",
]
PUBLIC_ENGINE_CODE = [
    "backend/scripts/run_tournament_simulation_engine_v4_v2_21.py",
    "backend/simulation/tournament_engine_v3.py",
    "backend/simulation/tournament_engine_v4.py",
]


def publish(payload: dict[str, Any]) -> None:
    target = DATA_DIR / "generated" / OUTPUT
    write_json(payload, target)
    shutil.copy2(target, DATA_DIR / "snapshots" / OUTPUT)
    shutil.copy2(target, FRONTEND_DATA_DIR / OUTPUT)


def git_unchanged(paths: list[str]) -> bool:
    return subprocess.run(["git", "diff", "--quiet", "--", *paths], cwd=ROOT).returncode == 0


def main() -> None:
    names = {
        "spain": "real_result_impact_audit_v2_26.json",
        "germany": "score_matrix_tail_risk_audit_v2_26.json",
        "architecture": "match_matrix_vs_tournament_simulation_audit_v2_26.json",
        "answers": "match_matrix_and_simulation_coherence_answer_v2_26.json",
    }
    exists = {key: (DATA_DIR / "generated" / name).exists() for key, name in names.items()}
    artifacts = {key: load_json(DATA_DIR / "generated" / name) for key, name in names.items() if exists[key]}
    answer_rows = artifacts.get("answers", {}).get("answers", {})
    three_answers = all(
        all(str(answer_rows.get(key, {}).get(field, "")).strip() for field in ("short_answer", "technical_answer", "product_conclusion"))
        for key in ("spain_0_0_cape_verde", "germany_7_1_large_score", "score_matrix_not_used_by_simulation")
    )
    report = ROOT / "docs" / "MATCH_MATRIX_AND_SIMULATION_COHERENCE_AUDIT_V2_26.md"
    v226_docs = list((ROOT / "docs").glob("*V2_26*.md"))
    secret_pattern = re.compile(r"AKIA[0-9A-Z]{16}|-----BEGIN (?:RSA|OPENSSH|EC|DSA) PRIVATE KEY-----")
    secret_found = any(
        secret_pattern.search(path.read_text(errors="ignore"))
        for path in [*ROOT.glob("backend/scripts/*v2_26.py"), *v226_docs]
    )
    checks = {
        "spain_case_answered": exists["spain"] and bool(artifacts["spain"].get("answer_for_user")),
        "germany_case_answered": exists["germany"] and bool(artifacts["germany"].get("answer_for_user")),
        "matrix_vs_simulation_answered": exists["architecture"] and bool(artifacts["architecture"].get("answer_for_user")),
        "three_explicit_answers": exists["answers"] and three_answers,
        "large_score_tail_audited": exists["germany"] and artifacts["germany"].get("tail_mass", {}).get("favorite_win_by_3_plus") is not None,
        "real_result_impact_audited": exists["spain"] and artifacts["spain"].get("result_locked") is True,
        "unified_distribution_recommendation_evaluated": exists["architecture"] and artifacts["architecture"].get("recommended_architecture", {}).get("priority") == "high",
        "public_engine_unchanged": git_unchanged(PUBLIC_ENGINE_CODE),
        "active_predictions_unchanged": git_unchanged(ACTIVE),
        "no_optuna": git_unchanged(["backend/data/generated/optuna_study_summary_v2_2.json"]),
        "no_secret": not secret_found,
        "single_v2_26_report": report.exists() and v226_docs == [report],
    }
    blocking = [key for key, passed in checks.items() if not passed]
    payload = {
        "version": "v2.26",
        "generated_at": utc_now(),
        "passed": not blocking,
        "spain_case_answered": checks["spain_case_answered"],
        "germany_case_answered": checks["germany_case_answered"],
        "matrix_vs_simulation_answered": checks["matrix_vs_simulation_answered"],
        "large_score_tail_audited": checks["large_score_tail_audited"],
        "real_result_impact_audited": checks["real_result_impact_audited"],
        "unified_distribution_recommendation_evaluated": checks["unified_distribution_recommendation_evaluated"],
        "public_engine_changed": not checks["public_engine_unchanged"],
        "active_predictions_unchanged": checks["active_predictions_unchanged"],
        "checks": checks,
        "blocking_issues": blocking,
        "warnings": [
            "Final and semi-final before/after marginals are absent from the compact V2.22 intermediate states.",
            "Existing refresh artifacts and large timeline files remain outside the V2.26 audit scope.",
        ],
    }
    publish(payload)
    if blocking:
        raise SystemExit(f"V2.26 coherence audit validation failed: {blocking}")
    print("V2.26 coherence audit validation: PASS")


if __name__ == "__main__":
    main()
