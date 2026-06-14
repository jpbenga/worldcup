"""Audit the data contract consumed by the Road to the Trophy frontend."""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, utc_now, write_json

VERSION = "v2.21.1"
CONSUMED = "road_to_the_trophy_coherent_view_model_v2_21.json"


def publish(name: str, payload: dict[str, Any]) -> None:
    generated = DATA_DIR / "generated" / name
    write_json(payload, generated)
    shutil.copy2(generated, DATA_DIR / "snapshots" / name)
    shutil.copy2(generated, FRONTEND_DATA_DIR / name)


def main() -> None:
    service = (ROOT / "frontend/src/app/services/worldcup.service.ts").read_text()
    consumed_files = re.findall(r"assets/data/(road_to_the_trophy[^']+\.json)", service)
    available = sorted(path.name for path in FRONTEND_DATA_DIR.glob("*road_to_the_trophy*.json"))
    missing = [name for name in consumed_files if not (FRONTEND_DATA_DIR / name).exists()]
    view = load_json(FRONTEND_DATA_DIR / CONSUMED) if (FRONTEND_DATA_DIR / CONSUMED).exists() else {}
    groups = view.get("groups", [])
    mismatches = []
    for group in groups:
        if len(group.get("teams", [])) != 4:
            mismatches.append({"group": group.get("group"), "field": "teams", "actual": len(group.get("teams", [])), "expected": 4})
        if not group.get("matches"):
            mismatches.append({"group": group.get("group"), "field": "matches", "actual": 0, "expected": ">0"})
        for team in group.get("teams", []):
            absent = [
                field for field in ("current_rank", "played", "points", "goal_difference", "goals_for", "central_status", "simulation_probabilities")
                if team.get(field) is None
            ]
            if absent:
                mismatches.append({"group": group.get("group"), "team": team.get("name"), "missing_fields": absent})
    template = (ROOT / "frontend/src/app/pages/simulation/simulation.component.html").read_text()
    css = (ROOT / "frontend/src/app/pages/simulation/simulation.component.css").read_text()
    empty_groups = any(not group.get("teams") for group in groups)
    empty_tables = any(not (group.get("central_table") or group.get("standings")) for group in groups)
    layout_risk = "group.teams.length && group.matches.length" not in template or ".group-node { width: 400px; height: 470px;" not in css
    payload = {
        "version": VERSION,
        "generated_at": utc_now(),
        "frontend_consumed_files": consumed_files,
        "available_road_to_trophy_files": available,
        "missing_files": missing,
        "schema_mismatches": mismatches,
        "empty_groups_detected": empty_groups,
        "empty_tables_detected": empty_tables,
        "layout_risk_detected": layout_risk,
        "adapter_present": (ROOT / "frontend/src/app/services/road-to-the-trophy.adapter.ts").exists(),
        "probable_root_causes": [
            "V4 initially omitted fields consumed directly by the Angular group-card template.",
            "The frontend previously had no normalization layer or compact invalid-contract fallback.",
        ],
        "verdict": "PASS" if not missing and not mismatches and not empty_groups and not empty_tables and not layout_risk else "FAIL",
    }
    publish("road_to_the_trophy_ui_contract_audit_v2_21_1.json", payload)
    print(f"V2.21.1 UI contract audit: {payload['verdict']}")
    if payload["verdict"] != "PASS":
        raise SystemExit("Road to the Trophy UI contract audit failed")


if __name__ == "__main__":
    main()
