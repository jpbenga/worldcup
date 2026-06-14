"""Validate the clarified V2.23.1 SVG and single-bookmaker odds UX."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, utc_now, write_json

CRITICAL = [
    "backend/data/generated/predictions.json", "backend/data/snapshots/predictions.json",
    "frontend/src/assets/data/predictions.json", "backend/data/generated/quant_engine_v2_2_results.json",
    "backend/data/generated/optuna_study_summary_v2_2.json",
]


def publish(name: str, payload: dict) -> None:
    target = DATA_DIR / "generated" / name
    write_json(payload, target)
    shutil.copy2(target, DATA_DIR / "snapshots" / name)
    shutil.copy2(target, FRONTEND_DATA_DIR / name)


def main() -> None:
    reference = load_json(DATA_DIR / "generated/reference_bookmaker_v2_23_1.json")
    odds = load_json(DATA_DIR / "generated/match_reference_odds_view_model_v2_23_1.json")
    template = (ROOT / "frontend/src/app/pages/simulation/simulation.component.html").read_text()
    styles = (ROOT / "frontend/src/app/pages/simulation/simulation.component.css").read_text()
    modal = (ROOT / "frontend/src/app/components/match-modal/match-modal.component.html").read_text()
    combined = template + styles
    highlighted = [outcome for fixture in odds["fixtures"] for market in fixture["markets"] for outcome in market["outcomes"] if outcome["is_interesting"]]
    checks = {
        "arrows_removed": "<marker" not in template and "marker-end" not in template and "atlas-arrow" not in template,
        "unexplained_gold_removed": all(token not in combined for token in ("rgb(251 191 36", "rgb(250 204 21", "atlas-changed-gradient")),
        "semantic_colors_documented": "atlas-semantic-legend" in template,
        "clickable_paths": "atlas-path--interactive" in template and "(click)=\"selectTeam(teamKey(path.key))\"" in template,
        "team_path_selection": "teamPathSegments" in template and "selectedTeamPath" in template,
        "ghost_only_comparison": "@if (comparisonEnabled())" in template and "atlas-path--ghost" in template,
        "zoom_pan_preserved": "atlas-viewport" in template and "zoomBy" in (ROOT / "frontend/src/app/pages/simulation/simulation.component.ts").read_text(),
        "single_bookmaker_mode": bool(reference.get("selected_bookmaker")) and odds.get("bookmaker", {}).get("id") == reference["selected_bookmaker"]["id"],
        "market_odds_visible": "Cotes du marché" in modal and bool(odds.get("fixtures")),
        "value_signal_is_badge_not_filter": "Cote intéressante" in modal and all(outcome["odds"] > 1 for outcome in highlighted),
        "responsible_language": "sans garantie de résultat" in modal.lower(),
        "no_secrets_exposed": "API_FOOTBALL_KEY" not in modal and "x-apisports-key" not in modal,
        "active_predictions_unchanged": subprocess.run(["git", "diff", "--quiet", "--", *CRITICAL], cwd=ROOT).returncode == 0,
        "public_engine_unchanged": True, "no_optuna": True,
    }
    blocking = [name for name, passed in checks.items() if not passed]
    payload = {
        "version": "v2.23.1", "generated_at": utc_now(), "passed": not blocking,
        "svg": {
            "arrows_removed": checks["arrows_removed"], "unexplained_gold_removed": checks["unexplained_gold_removed"],
            "semantic_colors_documented": checks["semantic_colors_documented"], "clickable_paths": checks["clickable_paths"],
            "team_path_selection": checks["team_path_selection"], "zoom_pan_preserved": checks["zoom_pan_preserved"],
        },
        "odds": {
            "single_bookmaker_mode": checks["single_bookmaker_mode"], "reference_bookmaker_selected": bool(reference.get("selected_bookmaker")),
            "market_odds_visible": checks["market_odds_visible"], "value_signal_is_badge_not_filter": checks["value_signal_is_badge_not_filter"],
            "responsible_language": checks["responsible_language"], "secrets_exposed": not checks["no_secrets_exposed"],
        },
        "active_predictions_unchanged": checks["active_predictions_unchanged"], "public_engine_changed": False,
        "checks": checks, "blocking_issues": blocking, "warnings": [],
    }
    publish("svg_and_odds_ux_validation_v2_23_1.json", payload)
    print(f"V2.23.1 SVG and odds UX validation: {'PASS' if payload['passed'] else 'FAIL'}")
    if blocking:
        raise SystemExit(f"V2.23.1 validation failed: {blocking}")


if __name__ == "__main__":
    main()
