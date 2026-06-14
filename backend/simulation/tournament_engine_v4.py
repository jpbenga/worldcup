"""Rules-aware tournament simulation helpers for Road to the Trophy V4."""

from __future__ import annotations

import math
import random
from collections import defaultdict
from typing import Any

from backend.simulation.tournament_engine_v3 import match_prediction


def cumulative_score_matrix(prediction: dict[str, Any]) -> list[tuple[float, int, int]]:
    total = 0.0
    rows = []
    for row in prediction["score_matrix"]:
        total += row["probability"]
        rows.append((total, row["home_goals"], row["away_goals"]))
    rows[-1] = (1.0, rows[-1][1], rows[-1][2])
    return rows


def sample_score(cumulative: list[tuple[float, int, int]], rng: random.Random) -> tuple[int, int]:
    value = rng.random()
    for threshold, home, away in cumulative:
        if value <= threshold:
            return home, away
    return cumulative[-1][1], cumulative[-1][2]


def poisson_sample(lam: float, rng: random.Random) -> int:
    limit = math.exp(-lam)
    product = 1.0
    value = 0
    while product > limit:
        value += 1
        product *= rng.random()
    return value - 1


def knockout_result(prediction: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    """Simulate regulation, extra time, then a conservative penalty shootout."""
    regulation = sample_score(prediction["_cumulative"], rng)
    if regulation[0] != regulation[1]:
        winner = prediction["team_a"] if regulation[0] > regulation[1] else prediction["team_b"]
        return {"winner": winner, "resolution": "90m", "score_90": f"{regulation[0]}-{regulation[1]}", "score_et": None}

    expected = prediction["expected_goals"]
    extra_a = poisson_sample(expected["team_a"] / 3, rng)
    extra_b = poisson_sample(expected["team_b"] / 3, rng)
    if extra_a != extra_b:
        winner = prediction["team_a"] if extra_a > extra_b else prediction["team_b"]
        return {
            "winner": winner,
            "resolution": "extra_time",
            "score_90": f"{regulation[0]}-{regulation[1]}",
            "score_et": f"{regulation[0] + extra_a}-{regulation[1] + extra_b}",
        }

    # Available shootout data is too sparse for a strong model. Shrink Elo heavily
    # toward a coin flip instead of pretending to know penalty specialists.
    elo_a = prediction["inputs"]["elo"][prediction["team_a"]]
    elo_b = prediction["inputs"]["elo"][prediction["team_b"]]
    elo_probability = 1 / (1 + 10 ** ((elo_b - elo_a) / 400))
    penalty_probability_a = 0.5 + 0.15 * (elo_probability - 0.5)
    winner = prediction["team_a"] if rng.random() < penalty_probability_a else prediction["team_b"]
    return {
        "winner": winner,
        "resolution": "penalties",
        "score_90": f"{regulation[0]}-{regulation[1]}",
        "score_et": f"{regulation[0] + extra_a}-{regulation[1] + extra_b}",
        "penalty_probability_a": penalty_probability_a,
    }


def _mini_table(teams: list[str], matches: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    table = {team: {"pts": 0, "gd": 0, "gf": 0} for team in teams}
    selected = set(teams)
    for match in matches:
        if match["team_a"] not in selected or match["team_b"] not in selected:
            continue
        a, b = match["team_a"], match["team_b"]
        ga, gb = map(int, match["score"].split("-"))
        for team, gf, gc in ((a, ga, gb), (b, gb, ga)):
            table[team]["gf"] += gf
            table[team]["gd"] += gf - gc
            table[team]["pts"] += 3 if gf > gc else 1 if gf == gc else 0
    return table


def rank_group(
    table: dict[str, dict[str, int]],
    matches: list[dict[str, Any]],
    elos: dict[str, float],
) -> tuple[list[str], list[dict[str, Any]]]:
    """Apply available FIFA-style criteria and expose unresolved proxy decisions."""
    base = sorted(table, key=lambda team: (table[team]["pts"], table[team]["gd"], table[team]["gf"]), reverse=True)
    result: list[str] = []
    decisions: list[dict[str, Any]] = []
    index = 0
    while index < len(base):
        key = (table[base[index]]["pts"], table[base[index]]["gd"], table[base[index]]["gf"])
        tied = []
        while index < len(base) and (table[base[index]]["pts"], table[base[index]]["gd"], table[base[index]]["gf"]) == key:
            tied.append(base[index])
            index += 1
        if len(tied) == 1:
            result.extend(tied)
            continue
        mini = _mini_table(tied, matches)
        ordered = sorted(tied, key=lambda team: (mini[team]["pts"], mini[team]["gd"], mini[team]["gf"], elos.get(team, 1500)), reverse=True)
        result.extend(ordered)
        decisions.append({
            "teams": tied,
            "criteria": "head_to_head_then_elo_proxy",
            "order": ordered,
            "limitation": "Elo is used only as a deterministic proxy where fair-play/drawing-lots data is unavailable.",
        })
    return result, decisions


def prediction_cache(
    elos: dict[str, float],
    profiles: dict[str, dict[str, float]],
) -> Any:
    cache: dict[tuple[str, str, str], dict[str, Any]] = {}

    def prediction(team_a: str, team_b: str, stage: str) -> dict[str, Any]:
        key = (team_a, team_b, stage)
        if key not in cache:
            row = match_prediction(team_a, team_b, elos, profiles, stage)
            row["_cumulative"] = cumulative_score_matrix(row)
            cache[key] = row
        return cache[key]

    return prediction


def table_from_path(group: dict[str, Any]) -> dict[str, dict[str, int]]:
    table = defaultdict(lambda: {"pts": 0, "gd": 0, "gf": 0})
    for match in group["matches"]:
        a, b = match["team_a"], match["team_b"]
        ga, gb = map(int, match["score"].split("-"))
        for team, gf, gc in ((a, ga, gb), (b, gb, ga)):
            table[team]["gf"] += gf
            table[team]["gd"] += gf - gc
            table[team]["pts"] += 3 if gf > gc else 1 if gf == gc else 0
    return dict(table)
