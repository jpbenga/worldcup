"""Conditioned group-stage simulator that locks only finished official results."""

from __future__ import annotations

from typing import Any

from backend.simulation.worldcup_tournament_simulator_v2_4 import simulate_groups


def simulate_conditioned(matches: list[dict[str, Any]], finished: dict[str, tuple[int, int]], simulations: int) -> dict[str, Any]:
    conditioned = []
    for match in matches:
        item = dict(match)
        if match["match_id"] in finished:
            home, away = finished[match["match_id"]]
            item["score_matrix"] = {"probabilities": [{"score": f"{home}-{away}", "home_goals": home, "away_goals": away, "probability": 1.0}]}
        conditioned.append(item)
    return simulate_groups(conditioned, simulations, seed=202606)
