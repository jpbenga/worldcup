"""Validate the V2.21 tournament simulation and living scenario contract."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, load_json


def main() -> None:
    simulation = load_json(DATA_DIR / "generated" / "tournament_simulation_engine_v4_results_v2_21.json")
    evolution = load_json(DATA_DIR / "generated" / "road_to_the_trophy_scenario_evolution_v2_21.json")
    validation = load_json(DATA_DIR / "generated" / "road_to_the_trophy_v4_validation_v2_21.json")
    view = load_json(DATA_DIR / "generated" / "road_to_the_trophy_coherent_view_model_v2_21.json")

    checks = {
        "50000_current_tournaments": simulation["simulation_count"] == 50_000,
        "50000_counterfactual_tournaments": validation["counterfactual_simulation_count"] == 50_000,
        "known_results_locked": simulation["real_results_locked"] == evolution["known_results_count"] > 0,
        "result_sensitive_scenario": evolution["scenario_changed"],
        "uniform_candidate_reservoir": validation["reservoir_size"] >= 1_000,
        "champion_not_forced": not validation["scenario_selection"]["champion_forced"],
        "explicit_knockout_resolution": sum(simulation["knockout_resolution_counts"].values()) == 50_000 * 31,
        "extra_time_observed": simulation["knockout_resolution_counts"].get("extra_time", 0) > 0,
        "penalties_observed": simulation["knockout_resolution_counts"].get("penalties", 0) > 0,
        "living_scenario_exposed": view["scenario_evolution"]["scenario_changed"],
        "limitations_exposed": len(view["limitations"]) >= 3,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise SystemExit(f"V2.21 validation FAIL: {', '.join(failed)}")
    print(f"V2.21 validation PASS: {len(checks)} checks")


if __name__ == "__main__":
    main()
