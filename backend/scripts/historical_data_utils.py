"""Shared configuration and helpers for the isolated historical-data spike."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, PROJECT_ROOT, utc_now, write_json

RAW_DIR = DATA_DIR / "raw" / "api_football" / "historical"
LEAGUES_CACHE = DATA_DIR / "raw" / "api_football" / "discovery" / "leagues.json"

COMPETITIONS = {
    "world_cup": {"league_id": 1, "name": "World Cup"},
    "world_cup_qualification_europe": {"league_id": 32, "name": "World Cup - Qualification Europe"},
    "world_cup_qualification_africa": {"league_id": 29, "name": "World Cup - Qualification Africa"},
    "world_cup_qualification_asia": {"league_id": 30, "name": "World Cup - Qualification Asia"},
    "world_cup_qualification_concacaf": {"league_id": 31, "name": "World Cup - Qualification CONCACAF"},
    "world_cup_qualification_oceania": {"league_id": 33, "name": "World Cup - Qualification Oceania"},
    "world_cup_qualification_south_america": {"league_id": 34, "name": "World Cup - Qualification South America"},
    "friendlies": {"league_id": 10, "name": "Friendlies"},
    "euro": {"league_id": 4, "name": "Euro Championship"},
    "copa_america": {"league_id": 9, "name": "Copa America"},
    "africa_cup_of_nations": {"league_id": 6, "name": "Africa Cup of Nations"},
    "asian_cup": {"league_id": 7, "name": "Asian Cup"},
    "gold_cup": {"league_id": 22, "name": "CONCACAF Gold Cup"},
    "uefa_nations_league": {"league_id": 5, "name": "UEFA Nations League"},
}

EXPANDED_COMPETITIONS = {
    "world_cup": {**COMPETITIONS["world_cup"], "family": "world_championship", "tier": "major_tournament", "weight": "normal"},
    "euro": {**COMPETITIONS["euro"], "family": "continental_championship", "tier": "major_tournament", "weight": "normal"},
    "copa_america": {**COMPETITIONS["copa_america"], "family": "continental_championship", "tier": "major_tournament", "weight": "normal"},
    "afcon": {**COMPETITIONS["africa_cup_of_nations"], "family": "continental_championship", "tier": "major_tournament", "weight": "normal"},
    "asian_cup": {**COMPETITIONS["asian_cup"], "family": "continental_championship", "tier": "major_tournament", "weight": "normal"},
    "gold_cup": {**COMPETITIONS["gold_cup"], "family": "continental_championship", "tier": "major_tournament", "weight": "normal"},
    "uefa_nations_league": {**COMPETITIONS["uefa_nations_league"], "family": "nations_league", "tier": "competitive", "weight": "normal"},
    "friendlies": {**COMPETITIONS["friendlies"], "family": "friendly", "tier": "friendly", "weight": "low"},
    "world_cup_qualification_europe": {**COMPETITIONS["world_cup_qualification_europe"], "family": "world_cup_qualification", "tier": "qualification", "weight": "normal"},
    "world_cup_qualification_africa": {**COMPETITIONS["world_cup_qualification_africa"], "family": "world_cup_qualification", "tier": "qualification", "weight": "normal"},
    "world_cup_qualification_asia": {**COMPETITIONS["world_cup_qualification_asia"], "family": "world_cup_qualification", "tier": "qualification", "weight": "normal"},
    "world_cup_qualification_concacaf": {**COMPETITIONS["world_cup_qualification_concacaf"], "family": "world_cup_qualification", "tier": "qualification", "weight": "normal"},
    "world_cup_qualification_oceania": {**COMPETITIONS["world_cup_qualification_oceania"], "family": "world_cup_qualification", "tier": "qualification", "weight": "normal"},
    "world_cup_qualification_south_america": {**COMPETITIONS["world_cup_qualification_south_america"], "family": "world_cup_qualification", "tier": "qualification", "weight": "normal"},
}

EXPANDED_PRESETS = {
    "conservative": {
        "world_cup": [2014, 2018, 2022],
        "euro": [2016, 2020, 2024],
        "copa_america": [2016, 2019, 2021, 2024],
        "afcon": [2017, 2019, 2021, 2023],
        "asian_cup": [2015, 2019, 2023],
        "gold_cup": [2017, 2019, 2021, 2023],
    },
}

EXPANDED_PRESETS["broad"] = {
    **EXPANDED_PRESETS["conservative"],
    "uefa_nations_league": [2018, 2020, 2022, 2024],
    "friendlies": [2022, 2023, 2024, 2025],
    "world_cup_qualification_europe": [2018, 2020, 2024],
    "world_cup_qualification_africa": [2018, 2022, 2023],
    "world_cup_qualification_asia": [2018, 2022],
    "world_cup_qualification_concacaf": [2018, 2022],
    "world_cup_qualification_oceania": [2018, 2022],
    "world_cup_qualification_south_america": [2018, 2022],
}

FINISHED_STATUSES = {"FT", "AET", "PEN"}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def response_items(payload: dict[str, Any]) -> list[dict[str, Any]]:
    response = payload.get("response", [])
    return response if isinstance(response, list) else []


def safe_errors(payload: dict[str, Any]) -> Any:
    return payload.get("errors") or []


def publish(filename: str, payload: Any) -> None:
    snapshot = DATA_DIR / "snapshots" / filename
    frontend = FRONTEND_DATA_DIR / filename
    write_json(payload, snapshot)
    frontend.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(snapshot, frontend)


def league_inventory() -> dict[int, dict[str, Any]]:
    if not LEAGUES_CACHE.exists():
        return {}
    result = {}
    for item in response_items(load_json(LEAGUES_CACHE)):
        league = item.get("league", {})
        league_id = league.get("id")
        if isinstance(league_id, int):
            result[league_id] = item
    return result


def available_seasons(league_id: int, include_2026: bool = False) -> list[int]:
    item = league_inventory().get(league_id, {})
    seasons = [
        season.get("year")
        for season in item.get("seasons", [])
        if isinstance(season.get("year"), int) and season.get("year") <= (2026 if include_2026 else 2025)
    ]
    return sorted(set(seasons), reverse=True)


def selected_competitions(competition: str | None, all_competitions: bool) -> list[tuple[str, dict[str, Any]]]:
    if competition:
        return [(competition, COMPETITIONS[competition])]
    if all_competitions:
        return list(COMPETITIONS.items())
    return list(COMPETITIONS.items())


def fixture_status(item: dict[str, Any]) -> str | None:
    return item.get("fixture", {}).get("status", {}).get("short")


def finished_items(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return [item for item in response_items(payload) if fixture_status(item) in FINISHED_STATUSES]


def filename_for(key: str, season: int) -> str:
    return f"fixtures_{key}_{season}.json"


def relative(path: Path) -> str:
    return path.relative_to(PROJECT_ROOT).as_posix()


def base_summary() -> dict[str, Any]:
    return {
        "generated_at": utc_now(),
        "api_provider": "api_football",
        "scope": "historical_international_matches",
    }
