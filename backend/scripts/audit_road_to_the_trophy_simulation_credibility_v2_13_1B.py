"""Audit whether Road to the Trophy simulation outputs support their product claims."""

from __future__ import annotations

import math
import random
import shutil
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, utc_now, write_json
from backend.scripts.build_living_worldcup_scenario_v2_13 import (
    RNG_SEED,
    ROUND_NAMES,
    next_pairings,
    pair_entrants,
    play_round,
    projected_qualifiers,
    strength,
    team_assets,
)

OUTPUT = "road_to_the_trophy_simulation_credibility_audit_v2_13_1B.json"
SIMULATIONS = 50_000


def publish(payload: dict[str, Any]) -> None:
    generated = DATA_DIR / "generated" / OUTPUT
    write_json(payload, generated)
    shutil.copy2(generated, DATA_DIR / "snapshots" / OUTPUT)
    shutil.copy2(generated, FRONTEND_DATA_DIR / OUTPUT)


def elo_probability(team_a_elo: float, team_b_elo: float) -> float:
    return 1 / (1 + 10 ** ((team_b_elo - team_a_elo) / 400))


def main() -> None:
    scenario = load_json(DATA_DIR / "generated" / "living_worldcup_scenario_v2_13.json")
    groups = load_json(FRONTEND_DATA_DIR / "worldcup_groups.json")
    group_simulation = load_json(DATA_DIR / "generated" / "worldcup_tournament_simulation_conditioned_v2_6.json")
    assets = {team["name"]: team for group in groups for team in group["teams"]}

    group_probabilities = [
        value
        for row in group_simulation["teams"].values()
        for key, value in row.items()
        if key.endswith("_probability")
    ]
    exact_group_count_evidence = all(abs(round(value * SIMULATIONS) - value * SIMULATIONS) < 1e-8 for value in group_probabilities)
    champion_probabilities = [row["probability"] for row in scenario["simulation_evidence"]["champion_frequencies"]]
    exact_knockout_count_evidence = all(
        abs(round(value * SIMULATIONS) - value * SIMULATIONS) < 1e-8 for value in champion_probabilities
    )
    knockout_assets = team_assets()
    qualifiers = projected_qualifiers(group_simulation)
    strengths = {row["team"]: strength(row["team"], group_simulation, knockout_assets) for row in qualifiers}
    opening_pairings = pair_entrants(qualifiers, strengths)
    rng = random.Random(RNG_SEED)
    champions: Counter[str] = Counter()
    matchup_counts: Counter[tuple[str, str]] = Counter()
    for _ in range(SIMULATIONS):
        pairings = opening_pairings
        for _round_name in ROUND_NAMES:
            winners, _ = play_round(pairings, strengths, rng, matchup_counts)
            pairings = next_pairings(winners)
        champions[winners[0]] += 1
    published_top_counts = {
        row["team"]: round(row["probability"] * SIMULATIONS)
        for row in scenario["simulation_evidence"]["champion_frequencies"]
    }

    inversions = []
    france_switzerland = None
    for round_name, matches in scenario["knockout_path"]["rounds"].items():
        for match in matches:
            winner = match["projected_winner"]
            loser = match["team_b"] if winner == match["team_a"] else match["team_a"]
            winner_elo = assets[winner]["elo_rating"]
            loser_elo = assets[loser]["elo_rating"]
            if winner_elo < loser_elo:
                inversions.append(
                    {
                        "round": round_name,
                        "projected_winner": winner,
                        "projected_winner_elo": winner_elo,
                        "higher_elo_opponent": loser,
                        "higher_elo_opponent_elo": loser_elo,
                        "elo_gap": loser_elo - winner_elo,
                    }
                )
            if {match["team_a"], match["team_b"]} == {"France", "Switzerland"}:
                france_probability = (
                    match["team_a_win_probability"] if match["team_a"] == "France" else match["team_b_win_probability"]
                )
                france_switzerland = {
                    "round": round_name,
                    "scenario_france_advance_probability": france_probability,
                    "scenario_switzerland_advance_probability": 1 - france_probability,
                    "france_elo": assets["France"]["elo_rating"],
                    "switzerland_elo": assets["Switzerland"]["elo_rating"],
                    "standard_elo_france_expected_score": elo_probability(
                        assets["France"]["elo_rating"], assets["Switzerland"]["elo_rating"]
                    ),
                    "diagnosis": "Group qualification and first-place probabilities overwhelm the Elo advantage.",
                }

    payload = {
        "version": "v2.13.1B",
        "generated_at": utc_now(),
        "verdict": "FAIL_CALIBRATION_REVIEW_REQUIRED",
        "execution_evidence": {
            "group_stage_declared_simulations": group_simulation["simulation_count"],
            "knockout_declared_simulations": scenario["simulations"],
            "group_probabilities_are_exact_empirical_count_multiples": exact_group_count_evidence,
            "knockout_probabilities_are_exact_empirical_count_multiples": exact_knockout_count_evidence,
            "independent_knockout_rerun_matches_published_top_counts": all(
                champions[team] == count for team, count in published_top_counts.items()
            ),
            "independent_knockout_rerun_champion_count": sum(champions.values()),
            "full_end_to_end_world_cup_paths_simulated": False,
            "run_manifest_with_input_hashes_available": False,
            "interpretation": "Two real 50,000-draw blocks exist: group stage, then knockout on one fixed projected bracket.",
        },
        "reproducibility": {
            "seeded": True,
            "cross_process_reproducibility_bug_found": True,
            "cause": "Unsorted Python set iteration affected seeded tie-break allocation.",
            "fix": "Group table construction is now sorted before tie-break draws.",
            "existing_artifacts_generated_before_fix": True,
        },
        "calibration": {
            "knockout_formula": "50% group qualification + 25% group first place + 25% logistic Elo signal",
            "problem": "Group difficulty is incorrectly treated as head-to-head strength.",
            "lower_elo_projected_winner_count": len(inversions),
            "projected_match_count": sum(len(matches) for matches in scenario["knockout_path"]["rounds"].values()),
            "lower_elo_projected_winners": inversions,
            "france_vs_switzerland": france_switzerland,
            "fifa_ranking_used": False,
            "squad_quality_used": False,
            "offensive_strength_directly_used_in_knockout": False,
        },
        "recommendations": [
            "Do not present current knockout probabilities as calibrated.",
            "Build and backtest a dedicated neutral-site knockout advancement model.",
            "Use Elo and active engine team-strength signals directly; do not use group difficulty as matchup strength.",
            "Persist complete end-to-end paths and simulation run manifests before claiming full World Cup simulations.",
        ],
    }
    publish(payload)
    print(
        f"Road to the Trophy credibility audit: {payload['verdict']} "
        f"({len(inversions)} lower-Elo projected winners)"
    )


if __name__ == "__main__":
    main()
