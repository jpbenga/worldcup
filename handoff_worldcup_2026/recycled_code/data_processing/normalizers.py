"""Pure normalizers adapted from the API-Football ingestion/audit scripts."""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Mapping


def normalize_team_name(name: str) -> str:
    ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]", "", ascii_name.lower())


def normalize_api_football_fixture(raw: Mapping[str, object]) -> dict[str, object]:
    fixture = raw["fixture"]
    league = raw["league"]
    teams = raw["teams"]
    if not isinstance(fixture, Mapping) or not isinstance(league, Mapping) or not isinstance(teams, Mapping):
        raise ValueError("Malformed API-Football fixture")
    home = teams["home"]
    away = teams["away"]
    if not isinstance(home, Mapping) or not isinstance(away, Mapping):
        raise ValueError("Malformed team data")
    return {
        "match_id": str(fixture["id"]),
        "home_team": str(home["name"]),
        "away_team": str(away["name"]),
        "kickoff_at": fixture["date"],
        "competition": league["name"],
        "stage": league.get("round"),
        "group": None,
    }


def normalize_api_football_result(raw: Mapping[str, object]) -> dict[str, object]:
    fixture = raw["fixture"]
    goals = raw["goals"]
    if not isinstance(fixture, Mapping) or not isinstance(goals, Mapping):
        raise ValueError("Malformed API-Football result")
    status = fixture.get("status", {})
    status_short = status.get("short") if isinstance(status, Mapping) else None
    return {
        "match_id": str(fixture["id"]),
        "home_score": goals.get("home"),
        "away_score": goals.get("away"),
        "status": "finished" if status_short in {"FT", "AET", "PEN"} else "scheduled",
    }
