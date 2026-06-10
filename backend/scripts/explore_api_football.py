"""Explore API-Football with a deliberately small number of calls."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.config.settings import API_FOOTBALL_KEY, mask_secret
from backend.data_acquisition.api_football_client import ApiFootballClient, ApiFootballError
from backend.data_acquisition.status import update_source

RAW_ROOT = PROJECT_ROOT / "backend" / "data" / "raw" / "api_football"
CANDIDATES_PATH = RAW_ROOT / "discovery" / "worldcup_candidates.json"


def response_items(payload: dict[str, Any]) -> list[dict[str, Any]]:
    response = payload.get("response", [])
    return response if isinstance(response, list) else []


def save(client: ApiFootballClient, name: str, payload: dict[str, Any]) -> dict[str, Any]:
    path = client.save_raw_response(name, payload)
    print(f"Saved {path.relative_to(PROJECT_ROOT)}")
    return payload


def find_worldcup_candidates(leagues: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidates = []
    for item in leagues:
        league = item.get("league", {})
        country = item.get("country", {})
        name = str(league.get("name", ""))
        searchable = f"{name} {country.get('name', '')}".lower()
        if "world cup" not in searchable and "coupe du monde" not in searchable:
            continue
        candidates.append(
            {
                "league_id": league.get("id"),
                "name": name,
                "type": league.get("type"),
                "country": country.get("name"),
                "seasons": [season.get("year") for season in item.get("seasons", [])],
            }
        )
    return candidates


def ping(client: ApiFootballClient) -> None:
    payload = client.get("status")
    response = payload.get("response")
    if isinstance(response, dict):
        response.pop("account", None)
    save(client, "discovery/status.json", payload)


def discovery(client: ApiFootballClient) -> None:
    leagues = save(client, "discovery/leagues.json", client.get("leagues"))
    save(client, "discovery/countries.json", client.get("countries"))
    save(client, "discovery/team_countries.json", client.get("teams/countries"))
    candidates = find_worldcup_candidates(response_items(leagues))
    CANDIDATES_PATH.parent.mkdir(parents=True, exist_ok=True)
    CANDIDATES_PATH.write_text(json.dumps(candidates, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"World Cup candidates: {len(candidates)}")


def load_best_candidate() -> tuple[dict[str, Any], int]:
    if not CANDIDATES_PATH.exists():
        raise ApiFootballError("Run --mode discovery before --mode worldcup")
    candidates = json.loads(CANDIDATES_PATH.read_text(encoding="utf-8"))
    if not candidates:
        raise ApiFootballError("No World Cup candidate found")
    ranked = sorted(
        candidates,
        key=lambda item: (
            "world cup" in str(item.get("name", "")).lower(),
            2026 in item.get("seasons", []),
            2022 in item.get("seasons", []),
        ),
        reverse=True,
    )
    candidate = ranked[0]
    seasons = candidate.get("seasons", [])
    season = 2026 if 2026 in seasons else 2022 if 2022 in seasons else max(seasons)
    return candidate, season


def worldcup(client: ApiFootballClient) -> None:
    candidate, season = load_best_candidate()
    league_id = candidate["league_id"]
    print(f"Exploring league={league_id} ({candidate['name']}), season={season}")
    for endpoint, name in (
        ("fixtures", f"worldcup_fixtures_{season}.json"),
        ("teams", f"worldcup_teams_{season}.json"),
        ("standings", f"worldcup_standings_{season}.json"),
        ("fixtures/rounds", f"worldcup_rounds_{season}.json"),
    ):
        save(client, f"samples/{name}", client.get(endpoint, {"league": league_id, "season": season}))


def first_fixture() -> dict[str, Any]:
    paths = sorted((RAW_ROOT / "samples").glob("worldcup_fixtures_*.json"), reverse=True)
    for path in paths:
        items = response_items(json.loads(path.read_text(encoding="utf-8")))
        if items:
            return items[0]
    raise ApiFootballError("No fixture sample available; run --mode worldcup first")


def samples(client: ApiFootballClient) -> None:
    fixture = first_fixture()
    fixture_id = fixture.get("fixture", {}).get("id")
    league = fixture.get("league", {})
    calls = (
        ("fixtures/statistics", {"fixture": fixture_id}, "fixture_statistics_sample.json"),
        ("predictions", {"fixture": fixture_id}, "predictions_sample.json"),
        ("odds", {"fixture": fixture_id}, "odds_sample.json"),
    )
    for endpoint, params, name in calls:
        save(client, f"samples/{name}", client.get(endpoint, params))
    print(f"Sample fixture={fixture_id}, league={league.get('id')}, season={league.get('season')}")


def status_summary(reachable: bool, usable: bool, notes: str) -> None:
    candidates = []
    if CANDIDATES_PATH.exists():
        candidates = json.loads(CANDIDATES_PATH.read_text(encoding="utf-8"))
    update_source(
        {
            "id": "api_football",
            "label": "API-Football",
            "configured": bool(API_FOOTBALL_KEY),
            "reachable": reachable,
            "usable": usable,
            "worldcup_2026_found": any(2026 in item.get("seasons", []) for item in candidates),
            "notes": notes,
        }
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("ping", "discovery", "worldcup", "samples"), required=True)
    args = parser.parse_args()
    print(f"API-Football key: {mask_secret(API_FOOTBALL_KEY)}")
    try:
        client = ApiFootballClient(max_calls={"ping": 1, "discovery": 3, "worldcup": 4, "samples": 3}[args.mode])
        {"ping": ping, "discovery": discovery, "worldcup": worldcup, "samples": samples}[args.mode](client)
        status_summary(True, True, f"Mode {args.mode} completed with {client.call_count} controlled call(s).")
    except (ApiFootballError, ValueError, OSError, json.JSONDecodeError) as exc:
        status_summary(False, False, f"Mode {args.mode} failed: {exc}")
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    main()
