"""Validate V2.27 API statistics exploration and scenario catalog."""

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

OUTPUT = "api_stats_and_scenario_catalog_validation_v2_27.json"
ACTIVE = [
    "backend/data/generated/predictions.json", "backend/data/snapshots/predictions.json",
    "frontend/src/assets/data/predictions.json", "backend/data/generated/quant_engine_v2_2_results.json",
    "backend/data/generated/optuna_study_summary_v2_2.json",
]
PUBLIC_ENGINE = ["backend/scripts/run_tournament_simulation_engine_v4_v2_21.py", "backend/simulation/tournament_engine_v3.py", "backend/simulation/tournament_engine_v4.py"]


def publish(payload: dict[str, Any]) -> None:
    target = DATA_DIR / "generated" / OUTPUT
    write_json(payload, target)
    shutil.copy2(target, DATA_DIR / "snapshots" / OUTPUT)
    shutil.copy2(target, FRONTEND_DATA_DIR / OUTPUT)


def unchanged(paths: list[str]) -> bool:
    return subprocess.run(["git", "diff", "--quiet", "--", *paths], cwd=ROOT).returncode == 0


def main() -> None:
    api = load_json(DATA_DIR / "generated" / "api_football_statistics_exploration_v2_27.json")
    catalog = load_json(DATA_DIR / "generated" / "germany_curacao_scenario_catalog_v2_27.json")
    answer = load_json(DATA_DIR / "generated" / "api_stats_and_scenario_exploration_answer_v2_27.json")
    families = catalog.get("scenario_catalog", {})
    required_families = ["result_1n2", "exact_scores", "victory_margins", "team_goal_totals", "match_goal_totals", "btts_clean_sheet", "football_reading_scenarios"]
    docs = list((ROOT / "docs").glob("*V2_27*.md"))
    report = ROOT / "docs" / "API_STATS_AND_MATCH_SCENARIOS_EXPLORATION_V2_27.md"
    secret_pattern = re.compile(r"AKIA[0-9A-Z]{16}|-----BEGIN (?:RSA|OPENSSH|EC|DSA) PRIVATE KEY-----|x-apisports-key\s*:")
    secret_found = any(secret_pattern.search(path.read_text(errors="ignore")) for path in [*ROOT.glob("backend/scripts/*v2_27.py"), *docs])
    endpoint = api.get("endpoint_availability", {})
    checks = {
        "api_statistics_explored": api.get("api_key_present") is True and bool(api.get("fixtures_checked")),
        "xg_availability_checked": endpoint.get("xg", {}).get("available") is not None,
        "match_statistics_checked": endpoint.get("fixture_statistics", {}).get("available") is not None,
        "events_checked": endpoint.get("events", {}).get("available") is not None,
        "germany_curacao_catalog_generated": catalog.get("fixture", {}).get("actual_score") == "7-1",
        "scenario_families_generated": all(families.get(key) for key in required_families),
        "answer_generated": bool(answer.get("answers", {}).get("api_football_stats", {}).get("short_answer")) and bool(answer.get("answers", {}).get("germany_curacao_scenarios", {}).get("short_answer")),
        "public_engine_unchanged": unchanged(PUBLIC_ENGINE),
        "active_predictions_unchanged": unchanged(ACTIVE),
        "no_optuna": unchanged(["backend/data/generated/optuna_study_summary_v2_2.json"]),
        "no_secret": not secret_found,
        "single_v2_27_report": docs == [report],
    }
    blocking = [key for key, passed in checks.items() if not passed]
    payload = {
        "version": "v2.27", "generated_at": utc_now(), "passed": not blocking,
        "api_statistics_explored": checks["api_statistics_explored"],
        "xg_availability_checked": checks["xg_availability_checked"],
        "match_statistics_checked": checks["match_statistics_checked"],
        "events_checked": checks["events_checked"],
        "germany_curacao_catalog_generated": checks["germany_curacao_catalog_generated"],
        "scenario_families_generated": checks["scenario_families_generated"],
        "answer_generated": checks["answer_generated"],
        "public_engine_changed": not checks["public_engine_unchanged"],
        "active_predictions_unchanged": checks["active_predictions_unchanged"],
        "checks": checks, "blocking_issues": blocking,
        "warnings": api.get("warnings", []) + ["Raw API exploration responses remain local and outside the commit."],
    }
    publish(payload)
    if blocking:
        raise SystemExit(f"V2.27 validation failed: {blocking}")
    print("V2.27 API stats and scenario catalog validation: PASS")


if __name__ == "__main__":
    main()
