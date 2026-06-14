"""Audit the V2.23 SVG and odds UX regression."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, utc_now, write_json


def publish(name: str, payload: dict) -> None:
    target = DATA_DIR / "generated" / name
    write_json(payload, target)
    shutil.copy2(target, DATA_DIR / "snapshots" / name)
    shutil.copy2(target, FRONTEND_DATA_DIR / name)


def main() -> None:
    template = (ROOT / "frontend/src/app/pages/simulation/simulation.component.html").read_text()
    styles = (ROOT / "frontend/src/app/pages/simulation/simulation.component.css").read_text()
    modal = (ROOT / "frontend/src/app/components/match-modal/match-modal.component.html").read_text()
    odds = load_json(DATA_DIR / "generated/api_football_odds_snapshot_v2_23.json")
    reference_path = DATA_DIR / "generated/reference_bookmaker_v2_23_1.json"
    reference = load_json(reference_path) if reference_path.exists() else {}
    selected = reference.get("selected_bookmaker")
    issues = []
    if "<marker" in template or "marker-end" in template: issues.append("Decorative SVG arrow markers remain.")
    if "rgb(251 191 36" in styles or "rgb(250 204 21" in styles: issues.append("Gold visual states remain unexplained.")
    if "(click)=\"selectTeam(" not in template: issues.append("SVG paths do not select a team journey.")
    payload = {
        "version": "v2.23.1", "generated_at": utc_now(),
        "svg": {
            "arrow_markers_detected": "<marker" in template or "marker-end" in template,
            "gold_borders_detected": "rgb(251 191 36" in styles or "rgb(250 204 21" in styles,
            "unexplained_colors_detected": "atlas-changed-gradient" in template,
            "clickable_paths_detected": "atlas-path--interactive" in template and "(click)=\"selectTeam(" in template,
            "team_path_mapping_detected": "teamPathSegments" in template,
            "legend_detected": "atlas-semantic-legend" in template,
        },
        "odds": {
            "odds_snapshot_available": odds.get("available", False), "selected_bookmaker": selected,
            "single_bookmaker_mode": bool(selected), "markets_available": selected.get("coverage_markets", []) if selected else [],
            "markets_displayed": ["1X2", "Double chance", "Draw no bet", "Over/Under 2.5", "Both teams to score"] if "referenceOdds" in modal else [],
            "odds_visible_in_match_ui": "Cotes du marché" in modal, "value_signals_visible": "Cote intéressante" in modal,
        },
        "blocking_ux_issues": issues,
        "recommendations": ["Remove arrows and gold.", "Make team path overlays clickable.", "Always show the selected bookmaker odds."],
        "verdict": "PASS" if not issues else "FAIL",
    }
    publish("svg_and_odds_ux_audit_v2_23_1.json", payload)
    print(f"V2.23.1 SVG and odds UX audit: {payload['verdict']}")


if __name__ == "__main__":
    main()
