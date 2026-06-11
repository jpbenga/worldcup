"""Deterministic Monte Carlo stability audit for analytical Poisson probabilities."""

from __future__ import annotations

import random
from typing import Any


def poisson_sample(lam: float, rng: random.Random) -> int:
    limit, product, count = __import__("math").exp(-lam), 1.0, 0
    while product > limit:
        count += 1
        product *= rng.random()
    return count - 1


def stability_audit(predictions: list[dict[str, Any]], simulations_per_match: int = 1500, seed: int = 2026) -> dict[str, Any]:
    rng = random.Random(seed)
    gaps = []
    examples = []
    for item in predictions:
        counts = [0, 0, 0]
        for _ in range(simulations_per_match):
            home = poisson_sample(item["predicted_home_xg"], rng)
            away = poisson_sample(item["predicted_away_xg"], rng)
            counts[0 if home > away else 2 if away > home else 1] += 1
        simulated = [count / simulations_per_match for count in counts]
        analytical = [item["poisson_1x2"]["home"], item["poisson_1x2"]["draw"], item["poisson_1x2"]["away"]]
        gap = sum(abs(simulated[i] - analytical[i]) for i in range(3)) / 3
        gaps.append(gap)
        if len(examples) < 10:
            examples.append({"match_id": item["match_id"], "analytical": analytical, "simulated": simulated, "average_abs_gap": gap})
    return {
        "simulations_per_match": simulations_per_match,
        "random_seed": seed,
        "matches": len(predictions),
        "analytic_vs_simulated_average_gap": sum(gaps) / len(gaps),
        "max_average_gap": max(gaps),
        "stable_below_0_03_share": sum(gap < .03 for gap in gaps) / len(gaps),
        "examples": examples,
        "useful_for_tournament_simulation": True,
    }
