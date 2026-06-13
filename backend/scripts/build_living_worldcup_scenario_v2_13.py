"""Build the V2.13 living World Cup scenario and projected knockout path."""

from __future__ import annotations

import math
import random
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, utc_now, write_json

VERSION = "v2.13"
ENGINE = "quant_hybrid_v2.2"
OUTPUT = "living_worldcup_scenario_v2_13.json"
SIMULATIONS = 50_000
RNG_SEED = 202613
ROUND_NAMES = ["round_of_32", "round_of_16", "quarter_finals", "semi_finals", "final"]


def publish(payload: dict[str, Any]) -> None:
    generated = DATA_DIR / "generated" / OUTPUT
    write_json(payload, generated)
    shutil.copy2(generated, DATA_DIR / "snapshots" / OUTPUT)
    shutil.copy2(generated, FRONTEND_DATA_DIR / OUTPUT)


def team_assets() -> dict[str, dict[str, Any]]:
    groups = load_json(FRONTEND_DATA_DIR / "worldcup_groups.json")
    return {
        team["name"]: {
            "logo_url": team.get("logo_url"),
            "country_code": team.get("country_code"),
            "elo_rating": team.get("elo_rating") or 1500,
        }
        for group in groups
        for team in group["teams"]
    }


def projected_qualifiers(simulation: dict[str, Any]) -> list[dict[str, Any]]:
    qualifiers: list[dict[str, Any]] = []
    third_candidates: list[dict[str, Any]] = []
    for group, team_names in sorted(simulation["groups"].items()):
        rows = [{"team": team, **simulation["teams"][team]} for team in team_names]
        first = max(rows, key=lambda row: row["finish_first_probability"])
        remaining = [row for row in rows if row["team"] != first["team"]]
        second = max(remaining, key=lambda row: row["finish_second_probability"])
        remaining = [row for row in remaining if row["team"] != second["team"]]
        third = max(remaining, key=lambda row: row["finish_third_probability"])
        qualifiers.extend(
            [
                {**first, "projected_slot": f"1er {group}", "projected_finish": 1},
                {**second, "projected_slot": f"2e {group}", "projected_finish": 2},
            ]
        )
        third_candidates.append(
            {
                **third,
                "projected_slot": f"Meilleur 3e {group}",
                "projected_finish": 3,
                "third_selection_score": third["best_third_qualification_probability"],
            }
        )
    qualifiers.extend(
        sorted(third_candidates, key=lambda row: row["third_selection_score"], reverse=True)[:8]
    )
    return qualifiers


def strength(team: str, simulation: dict[str, Any], assets: dict[str, dict[str, Any]]) -> float:
    row = simulation["teams"][team]
    elo = float(assets[team]["elo_rating"])
    elo_signal = 1 / (1 + math.exp(-(elo - 1750) / 180))
    return 0.50 * row["qualification_probability"] + 0.25 * row["finish_first_probability"] + 0.25 * elo_signal


def win_probability(team_a: str, team_b: str, strengths: dict[str, float]) -> float:
    return 1 / (1 + math.exp(-(strengths[team_a] - strengths[team_b]) * 5.2))


def pair_entrants(qualifiers: list[dict[str, Any]], strengths: dict[str, float]) -> list[tuple[str, str]]:
    seeded = sorted(qualifiers, key=lambda row: strengths[row["team"]], reverse=True)
    high = seeded[:16]
    low = list(reversed(seeded[16:]))
    for index, favorite in enumerate(high):
        if favorite["group"] == low[index]["group"]:
            swap = next(
                (
                    candidate
                    for candidate in range(index + 1, len(low))
                    if favorite["group"] != low[candidate]["group"]
                    and high[candidate]["group"] != low[index]["group"]
                ),
                None,
            )
            if swap is not None:
                low[index], low[swap] = low[swap], low[index]
    return [(favorite["team"], opponent["team"]) for favorite, opponent in zip(high, low)]


def play_round(
    pairings: list[tuple[str, str]],
    strengths: dict[str, float],
    rng: random.Random,
    matchup_counts: Counter[tuple[str, str]],
) -> tuple[list[str], list[str]]:
    winners: list[str] = []
    losers: list[str] = []
    for team_a, team_b in pairings:
        key = tuple(sorted((team_a, team_b)))
        matchup_counts[key] += 1
        winner = team_a if rng.random() < win_probability(team_a, team_b, strengths) else team_b
        winners.append(winner)
        losers.append(team_b if winner == team_a else team_a)
    return winners, losers


def next_pairings(teams: list[str]) -> list[tuple[str, str]]:
    return list(zip(teams[0::2], teams[1::2]))


def representative_bracket(
    opening_pairings: list[tuple[str, str]], strengths: dict[str, float], assets: dict[str, dict[str, Any]]
) -> dict[str, list[dict[str, Any]]]:
    rounds: dict[str, list[dict[str, Any]]] = {}
    pairings = opening_pairings
    for round_name in ROUND_NAMES:
        matches = []
        winners = []
        for index, (team_a, team_b) in enumerate(pairings, 1):
            probability_a = win_probability(team_a, team_b, strengths)
            winner = team_a if probability_a >= 0.5 else team_b
            winners.append(winner)
            matches.append(
                {
                    "match_id": f"projected_{round_name}_{index}",
                    "status": "projected",
                    "official": False,
                    "team_a": team_a,
                    "team_b": team_b,
                    "team_a_logo_url": assets[team_a]["logo_url"],
                    "team_b_logo_url": assets[team_b]["logo_url"],
                    "team_a_win_probability": probability_a,
                    "team_b_win_probability": 1 - probability_a,
                    "projected_winner": winner,
                }
            )
        rounds[round_name] = matches
        pairings = next_pairings(winners)
    return rounds


def team_summary(team: str, probability: float, simulation: dict[str, Any], assets: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        "team": team,
        "probability": probability,
        "group": simulation["teams"][team]["group"],
        "qualification_probability": simulation["teams"][team]["qualification_probability"],
        "logo_url": assets[team]["logo_url"],
        "country_code": assets[team]["country_code"],
    }


def main() -> None:
    simulation = load_json(DATA_DIR / "generated" / "worldcup_tournament_simulation_conditioned_v2_6.json")
    prior = load_json(DATA_DIR / "generated" / "worldcup_tournament_simulation_v2_4.json")
    knockout = load_json(DATA_DIR / "generated" / "worldcup_knockout_structure_v2_6.json")
    results = load_json(DATA_DIR / "generated" / "worldcup_2026_results_v2_6.json")
    assets = team_assets()
    qualifiers = projected_qualifiers(simulation)
    strengths = {row["team"]: strength(row["team"], simulation, assets) for row in qualifiers}
    opening_pairings = pair_entrants(qualifiers, strengths)

    rng = random.Random(RNG_SEED)
    round_appearances = {round_name: Counter() for round_name in ROUND_NAMES}
    champions: Counter[str] = Counter()
    finals: Counter[tuple[str, str]] = Counter()
    semi_sets: Counter[tuple[str, ...]] = Counter()
    quarter_sets: Counter[tuple[str, ...]] = Counter()
    matchup_counts: Counter[tuple[str, str]] = Counter()

    for _ in range(SIMULATIONS):
        current_pairings = opening_pairings
        semi_teams: list[str] = []
        quarter_teams: list[str] = []
        for round_name in ROUND_NAMES:
            entrants = [team for pairing in current_pairings for team in pairing]
            for team in entrants:
                round_appearances[round_name][team] += 1
            if round_name == "quarter_finals":
                quarter_teams = entrants
            if round_name == "semi_finals":
                semi_teams = entrants
            if round_name == "final":
                finals[tuple(sorted(entrants))] += 1
            winners, _ = play_round(current_pairings, strengths, rng, matchup_counts)
            current_pairings = next_pairings(winners)
        champions[winners[0]] += 1
        semi_sets[tuple(sorted(semi_teams))] += 1
        quarter_sets[tuple(sorted(quarter_teams))] += 1

    bracket = representative_bracket(opening_pairings, strengths, assets)
    projected_winner = bracket["final"][0]["projected_winner"]
    projected_final_teams = [bracket["final"][0]["team_a"], bracket["final"][0]["team_b"]]
    projected_semis = [team for match in bracket["semi_finals"] for team in (match["team_a"], match["team_b"])]
    projected_quarters = [team for match in bracket["quarter_finals"] for team in (match["team_a"], match["team_b"])]
    projected_r16 = [team for match in bracket["round_of_16"] for team in (match["team_a"], match["team_b"])]
    projected_r32 = [team for match in bracket["round_of_32"] for team in (match["team_a"], match["team_b"])]
    most_common_final, most_common_final_count = finals.most_common(1)[0]

    result_impact = [
        {
            "team": team,
            "qualification_delta": delta,
            "direction": "up" if delta > 0 else "down",
            "label": f"{delta * 100:+.1f} pts de qualification",
        }
        for team, delta in sorted(simulation["changes_vs_v2_4"].items(), key=lambda item: abs(item[1]), reverse=True)[:8]
    ]
    qualifier_rows = [
        {
            "team": row["team"],
            "group": row["group"],
            "slot": row["projected_slot"],
            "status": "projected",
            "qualification_probability": row["qualification_probability"],
            "logo_url": assets[row["team"]]["logo_url"],
        }
        for row in qualifiers
    ]
    payload = {
        "version": VERSION,
        "engine_version": ENGINE,
        "generated_at": utc_now(),
        "simulations": SIMULATIONS,
        "matches_total_target": 104,
        "matches_known": simulation["fixture_count"],
        "matches_projected": 32,
        "official_bracket_available": bool(knockout["knockout_structure_available"]),
        "scenario_type": "simulation_derived_bracket_projection",
        "scenario_status_label": "Scénario projeté à partir des simulations",
        "tournament_winner_projected": team_summary(
            projected_winner, champions[projected_winner] / SIMULATIONS, simulation, assets
        ),
        "final_projected": {
            "teams": [
                team_summary(team, round_appearances["final"][team] / SIMULATIONS, simulation, assets)
                for team in projected_final_teams
            ],
            "most_common_pairing": list(most_common_final),
            "most_common_pairing_probability": most_common_final_count / SIMULATIONS,
            "status": "projected",
        },
        "semi_finalists_projected": [
            team_summary(team, round_appearances["semi_finals"][team] / SIMULATIONS, simulation, assets)
            for team in projected_semis
        ],
        "quarter_finalists_projected": [
            team_summary(team, round_appearances["quarter_finals"][team] / SIMULATIONS, simulation, assets)
            for team in projected_quarters
        ],
        "round_of_16_projected": [
            team_summary(team, round_appearances["round_of_16"][team] / SIMULATIONS, simulation, assets)
            for team in projected_r16
        ],
        "round_of_32_projected": [
            team_summary(team, round_appearances["round_of_32"][team] / SIMULATIONS, simulation, assets)
            for team in projected_r32
        ],
        "group_stage": {
            "matches_known": 72,
            "finished_matches_locked": simulation["finished_matches_locked"],
            "future_matches_simulated": simulation["future_matches_simulated"],
            "projected_qualifiers": qualifier_rows,
            "qualification_rule": simulation["qualification_rule"],
        },
        "knockout_path": {
            "status": "projected",
            "rounds": bracket,
            "third_place_match": {
                "match_id": "projected_third_place",
                "status": "projected",
                "official": False,
                "slots": ["Perdant demi-finale 1", "Perdant demi-finale 2"],
            },
            "projected_match_count": 32,
        },
        "scenario_confidence": {
            "label": "open" if champions[projected_winner] / SIMULATIONS < 0.25 else "leading",
            "winner_probability": champions[projected_winner] / SIMULATIONS,
            "most_common_final_probability": most_common_final_count / SIMULATIONS,
            "path_stability": semi_sets.most_common(1)[0][1] / SIMULATIONS,
            "interpretation": "Le scénario montre le parcours dominant, pas une certitude ni un bracket officiel.",
        },
        "simulation_evidence": {
            "champion_frequencies": [
                team_summary(team, count / SIMULATIONS, simulation, assets) for team, count in champions.most_common(12)
            ],
            "most_common_semi_final_set": list(semi_sets.most_common(1)[0][0]),
            "most_common_semi_final_set_probability": semi_sets.most_common(1)[0][1] / SIMULATIONS,
            "most_common_quarter_final_set": list(quarter_sets.most_common(1)[0][0]),
            "most_common_quarter_final_set_probability": quarter_sets.most_common(1)[0][1] / SIMULATIONS,
            "rng_seed": RNG_SEED,
        },
        "result_impact": result_impact,
        "result_summary": {
            "finished_matches": results["finished_count"],
            "live_matches": results["live_count"],
            "not_started_matches": results["not_started_count"],
        },
        "alternative_scenario_status": "experimental_lab_only_not_promoted",
        "limitations": [
            "Le bracket officiel à élimination directe est absent des données disponibles.",
            "Les appariements sont un scénario projeté dérivé des probabilités de groupes et ne sont jamais présentés comme officiels.",
            "Les 50 000 parcours à élimination directe utilisent un tableau projeté fixe; ils ne remplacent pas une simulation FIFA officielle.",
            "La petite finale est comptée dans la cible de 104 matchs mais reste un slot projeté.",
            "Les probabilités du Prono IA restent inchangées et aucun modèle n'est réentraîné.",
        ],
        "prior_context": {
            "pre_result_simulations": prior["simulation_count"],
            "current_result_locks": simulation["finished_matches_locked"],
        },
    }
    publish(payload)
    print(
        f"V2.13 living scenario: winner={projected_winner}, final={' vs '.join(projected_final_teams)}, "
        f"known=72, target=104"
    )


if __name__ == "__main__":
    main()
