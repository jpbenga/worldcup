"""Normalize available acquisition samples without changing the main pipeline."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = PROJECT_ROOT / "backend" / "data"
API_SAMPLES = DATA_ROOT / "raw" / "api_football" / "samples"
ELO_SAMPLE = DATA_ROOT / "raw" / "elo" / "samples" / "elo_ratings_sample.json"
NORMALIZED = DATA_ROOT / "normalized"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def items(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    response = payload.get("response", []) if isinstance(payload, dict) else payload
    return response if isinstance(response, list) else []


def write(name: str, payload: Any) -> None:
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    path = NORMALIZED / name
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {path.relative_to(PROJECT_ROOT)} ({len(payload)} item(s))")


def normalize_matches() -> list[dict[str, Any]]:
    paths = sorted(API_SAMPLES.glob("worldcup_fixtures_*.json"), reverse=True)
    fixtures = items(paths[0]) if paths else []
    return [
        {
            "match_id": f"api_football_{fixture.get('fixture', {}).get('id')}",
            "external_fixture_id": fixture.get("fixture", {}).get("id"),
            "competition": fixture.get("league", {}).get("name"),
            "season": fixture.get("league", {}).get("season"),
            "round": fixture.get("league", {}).get("round"),
            "home_team": fixture.get("teams", {}).get("home", {}).get("name"),
            "away_team": fixture.get("teams", {}).get("away", {}).get("name"),
            "kickoff_at": fixture.get("fixture", {}).get("date"),
            "status": fixture.get("fixture", {}).get("status", {}).get("short"),
            "home_score": fixture.get("goals", {}).get("home"),
            "away_score": fixture.get("goals", {}).get("away"),
            "source_type": "api",
            "source_name": "api_football",
            "is_real_fixture": True,
        }
        for fixture in fixtures[:20]
    ]


def normalize_teams() -> list[dict[str, Any]]:
    paths = sorted(API_SAMPLES.glob("worldcup_teams_*.json"), reverse=True)
    teams = items(paths[0]) if paths else []
    return [
        {
            "external_team_id": item.get("team", {}).get("id"),
            "team_name": item.get("team", {}).get("name"),
            "country": item.get("team", {}).get("country"),
            "code": item.get("team", {}).get("code"),
            "source_type": "api",
            "source_name": "api_football",
        }
        for item in teams[:50]
    ]


def normalize_ratings() -> list[dict[str, Any]]:
    retrieved_at = utc_now()
    return [
        {
            "team_name": item.get("team_name"),
            "country_code": None,
            "elo_rating": item.get("elo_rating"),
            "rank": item.get("rank"),
            "source_type": "elo",
            "source_name": "eloratings.net",
            "source_url": "https://eloratings.net/",
            "retrieved_at": retrieved_at,
        }
        for item in items(ELO_SAMPLE)
    ]


def main() -> None:
    write("external_matches_sample.json", normalize_matches())
    write("external_teams_sample.json", normalize_teams())
    write("team_ratings.json", normalize_ratings())


if __name__ == "__main__":
    main()
