"""Audit readiness for a result-by-result Road to the Trophy timeline."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, utc_now, write_json


def publish(name: str, payload: dict[str, Any]) -> None:
    target = DATA_DIR / "generated" / name
    write_json(payload, target)
    shutil.copy2(target, DATA_DIR / "snapshots" / name)
    shutil.copy2(target, FRONTEND_DATA_DIR / name)


def main() -> None:
    results = load_json(DATA_DIR / "generated/worldcup_2026_results_v2_6.json")
    evolution = load_json(DATA_DIR / "generated/road_to_the_trophy_scenario_evolution_v2_21.json")
    view = load_json(DATA_DIR / "generated/road_to_the_trophy_coherent_view_model_v2_21.json")
    groups = view.get("groups", [])
    rounds = view.get("rounds", [])
    stable_groups = all(group.get("group") for group in groups)
    stable_matches = all(match.get("match_id") for group in groups for match in group.get("matches", [])) and all(
        match.get("match_id") for round_row in rounds for match in round_row.get("matches", [])
    )
    timeline_exists = (DATA_DIR / "generated/road_to_the_trophy_scenario_timeline_v2_22.json").exists()
    payload = {
        "version": "v2.22",
        "generated_at": utc_now(),
        "real_results_locked": results.get("finished_count", 0),
        "current_scenario_available": bool(view.get("projected_winner")),
        "counterfactual_scenario_available": bool(evolution.get("before")),
        "per_result_snapshots_available": timeline_exists,
        "common_random_streams_available": evolution.get("comparison") == "same_engine_common_random_numbers_with_known_results_vs_without_known_results",
        "atlas_nodes_have_stable_ids": stable_groups and stable_matches,
        "bracket_nodes_can_be_diffed": stable_matches,
        "frontend_can_compare_states": (ROOT / "frontend/src/app/pages/simulation/simulation.component.ts").exists(),
        "can_build_timeline": bool(view.get("projected_winner")) and stable_groups and stable_matches,
        "missing_requirements": [] if stable_groups and stable_matches else ["Stable Atlas identifiers"],
        "warnings": [] if timeline_exists else ["Per-result snapshots must be generated progressively."],
    }
    publish("road_to_the_trophy_timeline_readiness_v2_22.json", payload)
    print(f"V2.22 timeline readiness: {'PASS' if payload['can_build_timeline'] else 'FAIL'}")
    if not payload["can_build_timeline"]:
        raise SystemExit("Timeline readiness failed")


if __name__ == "__main__":
    main()
