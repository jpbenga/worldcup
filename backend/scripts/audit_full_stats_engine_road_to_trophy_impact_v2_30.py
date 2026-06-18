"""Audit whether the V2.30 candidate can safely feed Road to the Trophy."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.full_stats_engine_v2_30_utils import publish
from backend.scripts.pipeline_utils import DATA_DIR, load_json, utc_now

OUTPUT = "full_stats_engine_road_to_trophy_impact_v2_30.json"


def main() -> None:
    decision = load_json(DATA_DIR / "generated" / "full_stats_engine_promotion_decision_v2_30.json")
    results = load_json(DATA_DIR / "generated" / "full_stats_enriched_engine_v2_30_results.json")
    candidate_predictions = load_json(DATA_DIR / "generated" / "predictions_full_stats_candidate_v2_30.json")
    payload: dict[str, Any] = {
        "version": "v2.30",
        "generated_at": utc_now(),
        "candidate": {
            "name": results["candidate_name"],
            "decision": decision["decision"],
            "promote_candidate_for_match_predictions": decision["promote_candidate"],
            "active_predictions_overwritten": False,
        },
        "road_to_the_trophy_changed": False,
        "road_to_the_trophy_can_consume_now": False,
        "reason": (
            "V2.30 generates a candidate predictions file for the known fixture set, but it does not yet "
            "persist an arbitrary-pair inference contract for every possible future knockout or group matchup."
        ),
        "required_before_road_to_trophy_integration": [
            "Persist a reusable Unified Match Outcome Distribution for arbitrary team pairs.",
            "Benchmark that contract chronologically against the current tournament engine.",
            "Run a full tournament replay and compare bracket, group and knockout calibration.",
            "Keep official-result locking behavior unchanged.",
        ],
        "impact_scope": {
            "candidate_prediction_matches": len(candidate_predictions),
            "active_match_predictions_changed": False,
            "simulation_group_engine_changed": False,
            "simulation_knockout_engine_changed": False,
            "scenario_matrix_candidate_available": True,
        },
        "safe_next_step": "Use V2.30 for match-level candidate validation first; Road to the Trophy remains on its current engine.",
    }
    publish(payload, OUTPUT)
    print("V2.30 Road to the Trophy impact audit: no active simulation change")


if __name__ == "__main__":
    main()
