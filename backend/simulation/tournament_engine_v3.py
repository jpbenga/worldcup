"""Auditable V2.14 candidate match and tournament helpers."""

from __future__ import annotations

import math
import random
import shutil
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, write_json

ROOT = Path(__file__).resolve().parents[2]
BASE_GOALS = 1.28
MAX_GOALS = 7


def publish(name: str, payload: Any) -> None:
    target = DATA_DIR / "generated" / name
    write_json(payload, target)
    shutil.copy2(target, DATA_DIR / "snapshots" / name)
    shutil.copy2(target, FRONTEND_DATA_DIR / name)


def historical_matches() -> list[dict[str, Any]]:
    return load_json(DATA_DIR / "normalized" / "historical_matches_expanded.json")


def current_elos() -> dict[str, float]:
    return {row["team_name"]: float(row["elo_rating"]) for row in load_json(DATA_DIR / "normalized" / "team_ratings.json")}


def poisson(k: int, lam: float) -> float:
    return math.exp(-lam) * lam**k / math.factorial(k)


def profiles(matches: list[dict[str, Any]], as_of: datetime | None = None) -> dict[str, dict[str, float]]:
    as_of = as_of or datetime.now(timezone.utc)
    rows: dict[str, dict[str, float]] = defaultdict(lambda: {"gf": 0.0, "ga": 0.0, "weight": 0.0, "matches": 0.0})
    for match in matches:
        date = datetime.fromisoformat(match["kickoff_at"].replace("Z", "+00:00"))
        if date >= as_of:
            continue
        age_days = max(0, (as_of - date).days)
        weight = math.exp(-age_days / 730)
        for team, gf, ga in (
            (match["home_team"], match["home_score"], match["away_score"]),
            (match["away_team"], match["away_score"], match["home_score"]),
        ):
            rows[team]["gf"] += float(gf) * weight
            rows[team]["ga"] += float(ga) * weight
            rows[team]["weight"] += weight
            rows[team]["matches"] += 1
    result = {}
    for team, row in rows.items():
        weight = row["weight"]
        result[team] = {
            "attack_goals": row["gf"] / weight if weight else BASE_GOALS,
            "defense_conceded": row["ga"] / weight if weight else BASE_GOALS,
            "weighted_matches": weight,
            "matches": int(row["matches"]),
        }
    return result


def match_prediction(
    team_a: str,
    team_b: str,
    elos: dict[str, float],
    team_profiles: dict[str, dict[str, float]],
    stage: str = "knockout",
) -> dict[str, Any]:
    elo_a, elo_b = elos.get(team_a, 1500.0), elos.get(team_b, 1500.0)
    pa = team_profiles.get(team_a, {"attack_goals": BASE_GOALS, "defense_conceded": BASE_GOALS, "matches": 0})
    pb = team_profiles.get(team_b, {"attack_goals": BASE_GOALS, "defense_conceded": BASE_GOALS, "matches": 0})
    elo_factor_a = math.exp((elo_a - elo_b) / 900)
    elo_factor_b = math.exp((elo_b - elo_a) / 900)
    lambda_a = min(3.8, max(0.25, BASE_GOALS * (pa["attack_goals"] / BASE_GOALS) ** 0.28 * (pb["defense_conceded"] / BASE_GOALS) ** 0.20 * elo_factor_a))
    lambda_b = min(3.8, max(0.25, BASE_GOALS * (pb["attack_goals"] / BASE_GOALS) ** 0.28 * (pa["defense_conceded"] / BASE_GOALS) ** 0.20 * elo_factor_b))
    matrix, home, draw, away = [], 0.0, 0.0, 0.0
    for a in range(MAX_GOALS + 1):
        for b in range(MAX_GOALS + 1):
            probability = poisson(a, lambda_a) * poisson(b, lambda_b)
            matrix.append({"score": f"{a}-{b}", "home_goals": a, "away_goals": b, "probability": probability})
            home += probability if a > b else 0
            draw += probability if a == b else 0
            away += probability if a < b else 0
    total = home + draw + away
    for row in matrix:
        row["probability"] /= total
    home, draw, away = home / total, draw / total, away / total
    elo_expected_a = 1 / (1 + 10 ** ((elo_b - elo_a) / 400))
    advance_a = home + draw * elo_expected_a
    missing = ["injuries", "future_lineups", "squad_value", "betting_odds", "fifa_ranking"]
    factors = [
        {"factor": "Elo", "team_a": elo_a, "team_b": elo_b, "advantage": team_a if elo_a >= elo_b else team_b},
        {"factor": "Attaque récente pondérée", "team_a": pa["attack_goals"], "team_b": pb["attack_goals"], "advantage": team_a if pa["attack_goals"] >= pb["attack_goals"] else team_b},
        {"factor": "Défense récente pondérée", "team_a": pa["defense_conceded"], "team_b": pb["defense_conceded"], "advantage": team_a if pa["defense_conceded"] <= pb["defense_conceded"] else team_b},
    ]
    favorite = team_a if advance_a >= 0.5 else team_b
    strong_inversion = (favorite == team_a and elo_a + 100 < elo_b) or (favorite == team_b and elo_b + 100 < elo_a)
    return {
        "version": "v2.14",
        "engine_name": "match_probability_engine_v3",
        "team_a": team_a,
        "team_b": team_b,
        "stage": stage,
        "neutral_site": True,
        "inputs": {"rating": {team_a: elo_a, team_b: elo_b}, "elo": {team_a: elo_a, team_b: elo_b}, "attack_strength": {team_a: pa["attack_goals"], team_b: pb["attack_goals"]}, "defense_strength": {team_a: pa["defense_conceded"], team_b: pb["defense_conceded"]}, "recent_form": "exponential_time_decay_730_days", "competition_context": stage, "rest_days": None, "host_context": "neutral", "data_missing": missing},
        "probabilities_90": {"team_a_win": home, "draw": draw, "team_b_win": away},
        "advance_probabilities": {"team_a": advance_a, "team_b": 1 - advance_a},
        "expected_goals": {"team_a": lambda_a, "team_b": lambda_b},
        "score_matrix": matrix,
        "top_scores": sorted(matrix, key=lambda row: row["probability"], reverse=True)[:5],
        "favorite": favorite,
        "confidence": "low" if abs(advance_a - 0.5) < 0.08 else "medium" if abs(advance_a - 0.5) < 0.18 else "high",
        "explanation": {"headline": f"{favorite} favori selon les forces tête-à-tête mesurables", "key_factors": factors, "upset_context": ["Un match à élimination directe reste fortement aléatoire."], "missing_context": missing, "warning": "credibility_warning" if strong_inversion else ""},
    }


def sample_score(prediction: dict[str, Any], rng: random.Random) -> tuple[int, int]:
    value, cumulative = rng.random(), 0.0
    for row in prediction["score_matrix"]:
        cumulative += row["probability"]
        if value <= cumulative:
            return row["home_goals"], row["away_goals"]
    return MAX_GOALS, MAX_GOALS


def knockout_winner(prediction: dict[str, Any], rng: random.Random) -> str:
    return prediction["team_a"] if rng.random() < prediction["advance_probabilities"]["team_a"] else prediction["team_b"]
