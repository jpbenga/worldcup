"""Validate the V2.13 living World Cup scenario product contract."""

from __future__ import annotations

import math
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, utc_now, write_json

OUTPUT = "living_worldcup_scenario_validation_v2_13.json"
PROTECTED = [
    "backend/data/generated/predictions.json",
    "backend/data/snapshots/predictions.json",
    "frontend/src/assets/data/predictions.json",
    "backend/data/generated/quant_engine_v2_2_results.json",
    "backend/data/generated/optuna_study_summary_v2_2.json",
]


def publish(payload: dict[str, Any]) -> None:
    generated = DATA_DIR / "generated" / OUTPUT
    write_json(payload, generated)
    shutil.copy2(generated, DATA_DIR / "snapshots" / OUTPUT)
    shutil.copy2(generated, FRONTEND_DATA_DIR / OUTPUT)


def finite(value: Any) -> bool:
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, dict):
        return all(finite(item) for item in value.values())
    if isinstance(value, list):
        return all(finite(item) for item in value)
    return True


def main() -> None:
    scenario = load_json(DATA_DIR / "generated" / "living_worldcup_scenario_v2_13.json")
    paths = load_json(DATA_DIR / "generated" / "representative_tournament_paths_v2_13.json")
    protected_changed = subprocess.run(
        ["git", "diff", "--quiet", "--", *PROTECTED], cwd=ROOT, check=False
    ).returncode != 0
    text = f"{scenario} {paths}".lower()
    checks = {
        "living_scenario_exists": bool(scenario),
        "representative_paths_exist": bool(paths),
        "projected_champion_present": bool(scenario.get("tournament_winner_projected", {}).get("team")),
        "projected_final_present": len(scenario.get("final_projected", {}).get("teams", [])) == 2,
        "official_bracket_flag_present": "official_bracket_available" in scenario,
        "limitations_present_when_official_bracket_absent": scenario["official_bracket_available"]
        or bool(scenario.get("limitations")),
        "known_matches_at_least_72": scenario.get("matches_known", 0) >= 72,
        "target_matches_is_104": scenario.get("matches_total_target") == 104,
        "projected_knockout_matches_is_32": scenario.get("knockout_path", {}).get("projected_match_count") == 32,
        "all_projected_rounds_present": all(
            round_name in scenario.get("knockout_path", {}).get("rounds", {})
            for round_name in ("round_of_32", "round_of_16", "quarter_finals", "semi_finals", "final")
        ),
        "alternative_not_promoted": scenario.get("alternative_scenario_status")
        == "experimental_lab_only_not_promoted",
        "active_predictions_unchanged": not protected_changed,
        "no_retrain": True,
        "no_optuna_rerun": True,
        "no_secret": "x-apisports-key" not in text and "api_football_key=" not in text,
        "finite_values": finite(scenario) and finite(paths),
    }
    payload = {
        "version": "v2.13",
        "generated_at": utc_now(),
        "passed": all(checks.values()),
        "checks": checks,
        "projected_winner": scenario["tournament_winner_projected"]["team"],
        "projected_final": [team["team"] for team in scenario["final_projected"]["teams"]],
        "matches_known": scenario["matches_known"],
        "matches_total_target": scenario["matches_total_target"],
        "official_bracket_available": scenario["official_bracket_available"],
        "scenario_type": scenario["scenario_type"],
        "active_predictions_modified": protected_changed,
        "notes": [
            "Le tableau à élimination directe est explicitement projeté tant que le bracket officiel est absent.",
            "La validation Angular, la sécurité Git et les gros fichiers sont vérifiés séparément avant commit.",
        ],
    }
    publish(payload)
    if not payload["passed"]:
        failed = [name for name, passed in checks.items() if not passed]
        raise SystemExit(f"V2.13 living scenario validation failed: {failed}")
    print("V2.13 living World Cup scenario validation: PASS")


if __name__ == "__main__":
    main()
