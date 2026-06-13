"""Extract the representative tournament path from the V2.13 living scenario."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, utc_now, write_json

OUTPUT = "representative_tournament_paths_v2_13.json"


def publish(payload: dict[str, Any]) -> None:
    generated = DATA_DIR / "generated" / OUTPUT
    write_json(payload, generated)
    shutil.copy2(generated, DATA_DIR / "snapshots" / OUTPUT)
    shutil.copy2(generated, FRONTEND_DATA_DIR / OUTPUT)


def main() -> None:
    scenario = load_json(DATA_DIR / "generated" / "living_worldcup_scenario_v2_13.json")
    rounds = scenario["knockout_path"]["rounds"]
    leader = scenario["tournament_winner_projected"]["team"]
    leader_path = []
    for round_name, matches in rounds.items():
        match = next((item for item in matches if leader in (item["team_a"], item["team_b"])), None)
        if match:
            opponent = match["team_b"] if match["team_a"] == leader else match["team_a"]
            leader_probability = (
                match["team_a_win_probability"] if match["team_a"] == leader else match["team_b_win_probability"]
            )
            leader_path.append(
                {
                    "round": round_name,
                    "opponent": opponent,
                    "advance_probability": leader_probability,
                    "status": "projected",
                }
            )
    evidence = scenario["simulation_evidence"]
    payload = {
        "version": "v2.13",
        "generated_at": utc_now(),
        "scenario_type": scenario["scenario_type"],
        "representative_path": {
            "leader": leader,
            "rounds": leader_path,
            "description": "Chemin le plus probable du vainqueur projeté dans le tableau dérivé des simulations.",
        },
        "most_common_final": {
            "teams": scenario["final_projected"]["most_common_pairing"],
            "probability": scenario["final_projected"]["most_common_pairing_probability"],
        },
        "most_common_champion": scenario["tournament_winner_projected"],
        "most_common_semi_finalists": evidence["most_common_semi_final_set"],
        "most_common_quarter_finalists": evidence["most_common_quarter_final_set"],
        "path_stability": {
            "label": scenario["scenario_confidence"]["label"],
            "representative_semi_final_set_probability": evidence["most_common_semi_final_set_probability"],
            "representative_quarter_final_set_probability": evidence["most_common_quarter_final_set_probability"],
            "winner_probability": scenario["scenario_confidence"]["winner_probability"],
        },
        "result_impact": scenario["result_impact"],
        "limitations": scenario["limitations"],
    }
    publish(payload)
    print(f"V2.13 representative path: leader={leader}, rounds={len(leader_path)}")


if __name__ == "__main__":
    main()
