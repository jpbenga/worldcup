"""Shared publication and comparison helpers for V2.9."""

from __future__ import annotations

import math
import os
import shutil
from pathlib import Path
from typing import Any, Callable

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, utc_now, write_json

ROOT = Path(__file__).resolve().parents[2]
VERSION = "v2.9"
ENGINE = "quant_hybrid_v2.2"
CANDIDATE_VERSION = "score_matrix_candidate_v2.8"


def publish(payload: Any, name: str) -> None:
    target = DATA_DIR / "generated" / name
    write_json(payload, target)
    shutil.copy2(target, DATA_DIR / "snapshots" / name)
    if os.getenv("MATCHDAY_SKIP_FRONTEND_COPY") != "1":
        shutil.copy2(target, FRONTEND_DATA_DIR / name)


def matrix_entries(matrix: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    return matrix["probabilities"] if isinstance(matrix, dict) else matrix


def probability(entries: list[dict[str, Any]], predicate: Callable[[int, int], bool]) -> float:
    return sum(float(row["probability"]) for row in entries if predicate(int(row["home_goals"]), int(row["away_goals"])))


def expected_goals(entries: list[dict[str, Any]]) -> dict[str, float]:
    home = sum(int(row["home_goals"]) * float(row["probability"]) for row in entries)
    away = sum(int(row["away_goals"]) * float(row["probability"]) for row in entries)
    return {"home": home, "away": away, "total": home + away}


def markets(entries: list[dict[str, Any]], favorite_side: str) -> dict[str, Any]:
    values = {
        "home_win": probability(entries, lambda h, a: h > a),
        "draw": probability(entries, lambda h, a: h == a),
        "away_win": probability(entries, lambda h, a: a > h),
        "over_1_5": probability(entries, lambda h, a: h + a >= 2),
        "over_2_5": probability(entries, lambda h, a: h + a >= 3),
        "btts_yes": probability(entries, lambda h, a: h > 0 and a > 0),
        "home_scores": probability(entries, lambda h, a: h > 0),
        "away_scores": probability(entries, lambda h, a: a > 0),
        "home_scores_2_plus": probability(entries, lambda h, a: h >= 2),
        "away_scores_2_plus": probability(entries, lambda h, a: a >= 2),
        "home_win_by_2_plus": probability(entries, lambda h, a: h - a >= 2),
        "away_win_by_2_plus": probability(entries, lambda h, a: a - h >= 2),
    }
    values["favorite_win_by_2_plus"] = values[f"{favorite_side}_win_by_2_plus"]
    return values


def top_scores(entries: list[dict[str, Any]], limit: int = 10) -> list[dict[str, Any]]:
    return sorted(
        ({"score": row["score"], "probability": float(row["probability"])} for row in entries),
        key=lambda row: row["probability"],
        reverse=True,
    )[:limit]


def joined_candidate_matches() -> list[dict[str, Any]]:
    active = load_json(DATA_DIR / "generated" / "worldcup_2026_predictions_release_candidate_v2_4.json")["matches"]
    candidate = load_json(DATA_DIR / "generated" / "worldcup_2026_predictions_score_matrix_candidate_v2_8.json")["matches"]
    candidates = {row["match_id"]: row for row in candidate}
    return [
        {
            **row,
            "score_matrix": candidates[row["match_id"]]["score_matrix"],
            "candidate": candidates[row["match_id"]],
        }
        for row in active
    ]


def locked_results() -> dict[str, tuple[int, int]]:
    results = load_json(DATA_DIR / "generated" / "worldcup_2026_results_v2_6.json")
    return {
        row["match_id"]: (int(row["actual_score"]["home"]), int(row["actual_score"]["away"]))
        for row in results["fixtures"]
        if row["status"] == "finished" and row["actual_score"]["home"] is not None
    }


def build_campaign(simulation: dict[str, Any]) -> dict[str, Any]:
    ratings = {item["team_name"]: item for item in load_json(DATA_DIR / "normalized" / "team_ratings.json")}
    contenders = []
    for team, item in simulation["teams"].items():
        rating = ratings.get(team, {})
        elo = float(rating.get("elo_rating", 1500))
        elo_strength = 1 / (1 + math.exp(-(elo - 1750) / 180))
        proxy = 0.62 * item["qualification_probability"] + 0.23 * item["finish_first_probability"] + 0.15 * elo_strength
        probabilities = [item[f"finish_{name}_probability"] for name in ("first", "second", "third", "fourth")]
        likely_rank = probabilities.index(max(probabilities)) + 1
        contenders.append({
            "team": team,
            "group": item["group"],
            "qualification_probability": item["qualification_probability"],
            "group_winner_probability": item["finish_first_probability"],
            "elo_rating": rating.get("elo_rating"),
            "elo_rank": rating.get("rank"),
            "contender_proxy_score": proxy,
            "most_probable_group_finish": likely_rank,
            "campaign_steps": [
                {"label": "Phase de groupes", "detail": f"Rang alternatif le plus probable : {likely_rank}"},
                {"label": "Qualification alternative", "detail": f"Probabilité : {item['qualification_probability']:.1%}"},
                {"label": "Après les groupes", "detail": "Bracket officiel indisponible; aucun adversaire inventé."},
            ],
        })
    return {"contenders": sorted(contenders, key=lambda row: row["contender_proxy_score"], reverse=True)}


def group_effects(team_deltas: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in team_deltas:
        groups.setdefault(row["group"], []).append(row)
    return sorted(
        (
            {
                "group": group,
                "average_absolute_qualification_delta": sum(abs(row["qualification_delta"]) for row in rows) / len(rows),
                "maximum_absolute_qualification_delta": max(abs(row["qualification_delta"]) for row in rows),
            }
            for group, rows in groups.items()
        ),
        key=lambda row: row["average_absolute_qualification_delta"],
        reverse=True,
    )
