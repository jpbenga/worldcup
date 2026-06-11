"""Shared helpers for the V2.1 data-only refresh and feature-coverage audit."""

from __future__ import annotations

import json
import re
import shutil
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, PROJECT_ROOT, utc_now, write_json

RAW_V21 = DATA_DIR / "raw" / "api_football" / "v2_1"
LEAGUES_CACHE = DATA_DIR / "raw" / "api_football" / "discovery" / "leagues.json"
FINISHED = {"FT", "AET", "PEN"}
INTERNATIONAL_COMPETITIONS = {
    "world_cup": {"league_id": 1, "name": "World Cup", "family": "world_championship", "tier": "major_tournament"},
    "euro": {"league_id": 4, "name": "Euro Championship", "family": "continental_championship", "tier": "major_tournament"},
    "uefa_nations_league": {"league_id": 5, "name": "UEFA Nations League", "family": "nations_league", "tier": "competitive"},
    "afcon": {"league_id": 6, "name": "Africa Cup of Nations", "family": "continental_championship", "tier": "major_tournament"},
    "asian_cup": {"league_id": 7, "name": "Asian Cup", "family": "continental_championship", "tier": "major_tournament"},
    "copa_america": {"league_id": 9, "name": "Copa America", "family": "continental_championship", "tier": "major_tournament"},
    "friendlies": {"league_id": 10, "name": "Friendlies", "family": "friendly", "tier": "friendly"},
    "gold_cup": {"league_id": 22, "name": "CONCACAF Gold Cup", "family": "continental_championship", "tier": "major_tournament"},
    "wcq_africa": {"league_id": 29, "name": "World Cup - Qualification Africa", "family": "world_cup_qualification", "tier": "qualification"},
    "wcq_asia": {"league_id": 30, "name": "World Cup - Qualification Asia", "family": "world_cup_qualification", "tier": "qualification"},
    "wcq_concacaf": {"league_id": 31, "name": "World Cup - Qualification CONCACAF", "family": "world_cup_qualification", "tier": "qualification"},
    "wcq_europe": {"league_id": 32, "name": "World Cup - Qualification Europe", "family": "world_cup_qualification", "tier": "qualification"},
    "wcq_oceania": {"league_id": 33, "name": "World Cup - Qualification Oceania", "family": "world_cup_qualification", "tier": "qualification"},
    "wcq_south_america": {"league_id": 34, "name": "World Cup - Qualification South America", "family": "world_cup_qualification", "tier": "qualification"},
}
BY_LEAGUE = {item["league_id"]: item | {"key": key} for key, item in INTERNATIONAL_COMPETITIONS.items()}
REFRESH_PLAN = {
    "afcon": [2025],
    "gold_cup": [2025],
    "uefa_nations_league": [2024],
    "friendlies": [2024, 2025],
    "wcq_africa": [2023],
    "wcq_asia": [2026],
    "wcq_concacaf": [2026],
    "wcq_europe": [2024],
    "wcq_oceania": [2026],
    "wcq_south_america": [2026],
}
NON_SENIOR_PATTERN = re.compile(r"(^|[\s-])(U\d{2}|U-\d{2}|W|Women|Olympic|Youth|B Team)($|[\s-])", re.IGNORECASE)


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def response(payload: dict[str, Any]) -> list[dict[str, Any]]:
    value = payload.get("response", [])
    return value if isinstance(value, list) else []


def publish(name: str, payload: Any) -> None:
    generated = DATA_DIR / "generated" / name
    write_json(payload, generated)
    shutil.copy2(generated, DATA_DIR / "snapshots" / name)
    shutil.copy2(generated, FRONTEND_DATA_DIR / name)


def league_inventory() -> dict[int, dict[str, Any]]:
    if not LEAGUES_CACHE.exists():
        return {}
    return {
        item["league"]["id"]: item
        for item in response(load(LEAGUES_CACHE))
        if isinstance(item.get("league", {}).get("id"), int)
    }


def normalize_fixture(item: dict[str, Any]) -> dict[str, Any] | None:
    fixture, league, teams, goals = (item.get(key, {}) for key in ("fixture", "league", "teams", "goals"))
    fixture_id, league_id = fixture.get("id"), league.get("id")
    status = fixture.get("status", {}).get("short")
    home, away = goals.get("home"), goals.get("away")
    config = BY_LEAGUE.get(league_id)
    home_name, away_name = teams.get("home", {}).get("name"), teams.get("away", {}).get("name")
    if (
        not config
        or not isinstance(fixture_id, int)
        or status not in FINISHED
        or not isinstance(home, int)
        or not isinstance(away, int)
        or (league_id == 1 and league.get("season") == 2026)
        or (league_id == 10 and (not is_senior_team(home_name) or not is_senior_team(away_name)))
    ):
        return None
    kickoff = fixture.get("date")
    if not kickoff or datetime.fromisoformat(kickoff.replace("Z", "+00:00")) > datetime.now(timezone.utc):
        return None
    return {
        "match_id": f"api_football_{fixture_id}",
        "api_football_fixture_id": fixture_id,
        "competition": league.get("name"),
        "competition_id": league_id,
        "season": league.get("season"),
        "stage": league.get("round"),
        "round": league.get("round"),
        "home_team": home_name,
        "away_team": away_name,
        "home_team_id": teams.get("home", {}).get("id"),
        "away_team_id": teams.get("away", {}).get("id"),
        "kickoff_at": kickoff,
        "venue": fixture.get("venue", {}).get("name"),
        "city": fixture.get("venue", {}).get("city"),
        "status": "finished",
        "source_status": status,
        "home_score": home,
        "away_score": away,
        "winner": "home" if home > away else "away" if away > home else "draw",
        "source_type": "api_football",
        "source_name": "api_football_historical_refreshed_v2_1",
        "is_real_data": True,
        "is_future_fixture": False,
        "usable_for_training": True,
        "competition_family": config["family"],
        "competition_tier": config["tier"],
        "training_weight_hint": "low" if config["tier"] == "friendly" else "normal",
        "source_scope": "clear",
        "source_classification_confidence": "high",
    }


def is_senior_team(name: Any) -> bool:
    return isinstance(name, str) and not NON_SENIOR_PATTERN.search(name)


def dataset_stats(items: list[dict[str, Any]]) -> dict[str, Any]:
    teams = {str(item["home_team"]) for item in items} | {str(item["away_team"]) for item in items}
    return {
        "matches": len(items),
        "date_min": min((item["kickoff_at"] for item in items), default=None),
        "date_max": max((item["kickoff_at"] for item in items), default=None),
        "competitions": dict(Counter(str(item["competition"]) for item in items)),
        "seasons": sorted({int(item["season"]) for item in items if isinstance(item.get("season"), int)}),
        "teams": len(teams),
    }


def days_since(value: str | None) -> int | None:
    if not value:
        return None
    return (datetime.now(timezone.utc) - datetime.fromisoformat(value.replace("Z", "+00:00"))).days


def write_doc(name: str, content: str) -> None:
    (PROJECT_ROOT / "docs" / name).write_text(content, encoding="utf-8")


def base_report() -> dict[str, Any]:
    return {"generated_at": utc_now(), "version": "v2.1", "model_retrained": False, "optuna_rerun": False}
