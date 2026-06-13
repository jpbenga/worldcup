"""Deterministic World Cup 2026 group-stage simulation from V2.4 score matrices."""

from __future__ import annotations

import random
from collections import Counter, defaultdict
from typing import Any


def sample_score(entries: list[dict[str, Any]], rng: random.Random) -> tuple[int, int]:
    value, cumulative = rng.random(), 0.0
    for row in entries:
        cumulative += float(row["probability"])
        if value <= cumulative:
            return int(row.get("home_goals", row["score"].split("-")[0])), int(row.get("away_goals", row["score"].split("-")[1]))
    last = entries[-1]
    return int(last.get("home_goals", last["score"].split("-")[0])), int(last.get("away_goals", last["score"].split("-")[1]))


def rank_group(table: dict[str, dict[str, int]], rng: random.Random) -> list[str]:
    return sorted(table, key=lambda team: (table[team]["points"], table[team]["gd"], table[team]["gf"], rng.random()), reverse=True)


def simulate_groups(matches: list[dict[str, Any]], simulations: int, seed: int = 2026) -> dict[str, Any]:
    rng = random.Random(seed)
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    group_teams: dict[str, set[str]] = defaultdict(set)
    for match in matches:
        groups[str(match["group"])].append(match)
        group_teams[str(match["group"])].update((match["home_team"], match["away_team"]))
    rank_counts: dict[str, Counter[int]] = defaultdict(Counter)
    qualified = Counter(); eliminated = Counter(); third_qualified = Counter()
    for _ in range(simulations):
        all_rankings: dict[str, list[str]] = {}
        tables: dict[str, dict[str, dict[str, int]]] = {}
        for group, fixtures in groups.items():
            # Set iteration varies across Python processes and used to change
            # which team received each seeded tie-break draw.
            table = {team: {"points": 0, "gf": 0, "ga": 0, "gd": 0} for team in sorted(group_teams[group])}
            for fixture in fixtures:
                entries = fixture["score_matrix"]["probabilities"] if isinstance(fixture["score_matrix"], dict) else fixture["score_matrix"]
                hg, ag = sample_score(entries, rng); home, away = fixture["home_team"], fixture["away_team"]
                table[home]["gf"] += hg; table[home]["ga"] += ag; table[away]["gf"] += ag; table[away]["ga"] += hg
                table[home]["points"] += 3 if hg > ag else 1 if hg == ag else 0
                table[away]["points"] += 3 if ag > hg else 1 if hg == ag else 0
            for values in table.values():
                values["gd"] = values["gf"] - values["ga"]
            all_rankings[group] = rank_group(table, rng); tables[group] = table
        thirds = [(tables[group][ranking[2]]["points"], tables[group][ranking[2]]["gd"], tables[group][ranking[2]]["gf"], rng.random(), ranking[2]) for group, ranking in all_rankings.items()]
        best_thirds = {item[-1] for item in sorted(thirds, reverse=True)[:8]}
        for ranking in all_rankings.values():
            for rank, team in enumerate(ranking, 1):
                rank_counts[team][rank] += 1
                is_qualified = rank <= 2 or team in best_thirds
                qualified[team] += is_qualified; eliminated[team] += not is_qualified
                third_qualified[team] += rank == 3 and team in best_thirds
    teams = {}
    for group, names in group_teams.items():
        for team in sorted(names):
            teams[team] = {
                "group": group,
                "finish_first_probability": rank_counts[team][1] / simulations,
                "finish_second_probability": rank_counts[team][2] / simulations,
                "finish_third_probability": rank_counts[team][3] / simulations,
                "finish_fourth_probability": rank_counts[team][4] / simulations,
                "qualification_probability": qualified[team] / simulations,
                "best_third_qualification_probability": third_qualified[team] / simulations,
                "group_elimination_probability": eliminated[team] / simulations,
            }
    return {"teams": teams, "groups": {group: sorted(names) for group, names in sorted(group_teams.items())}}
