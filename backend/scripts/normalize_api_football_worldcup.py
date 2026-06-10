"""Normalize active API-Football World Cup fixtures and teams."""

from __future__ import annotations

import json
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

RAW_DIR = PROJECT_ROOT / "backend" / "data" / "raw" / "api_football" / "worldcup_2026"
NORMALIZED_DIR = PROJECT_ROOT / "backend" / "data" / "normalized"
MAPPING_PATH = PROJECT_ROOT / "backend" / "data" / "mappings" / "team_identity_map.json"
SCHEDULED_STATUSES = {"NS", "TBD", "PST", "SUSP", "INT"}
LIVE_STATUSES = {"1H", "HT", "2H", "ET", "BT", "P", "LIVE"}
FINISHED_STATUSES = {"FT", "AET", "PEN"}
NEUTRAL_PROTOTYPE_XG = 1.35


def read_response(name: str, required: bool = True) -> list[Any]:
    path = RAW_DIR / f"{name}.json"
    if not path.exists():
        if not required:
            return []
        raise FileNotFoundError(f"Missing {path.relative_to(PROJECT_ROOT)}; run fetch_worldcup_api_football.py")
    payload = json.loads(path.read_text(encoding="utf-8"))
    response = payload.get("response", []) if isinstance(payload, dict) else []
    return response if isinstance(response, list) else []


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def slugify(name: str) -> str:
    folded = unicodedata.normalize("NFKD", name.casefold())
    ascii_name = "".join(character for character in folded if not unicodedata.combining(character))
    return "_".join(re.sub(r"[^a-z0-9]+", " ", ascii_name).split())


def normalized_status(short: str | None) -> str:
    if short in FINISHED_STATUSES:
        return "finished"
    if short in LIVE_STATUSES:
        return "live"
    return "scheduled"


def stage_from_round(round_name: str | None) -> str:
    if not round_name:
        return "unknown"
    lowered = round_name.lower()
    if "group" in lowered:
        return "group"
    if "final" in lowered:
        return "final"
    return "knockout"


def parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def group_by_team_id() -> dict[int, str]:
    groups: dict[int, str] = {}
    for response in read_response("standings", required=False):
        for standing_group in response.get("league", {}).get("standings", []):
            for standing in standing_group:
                team_id = standing.get("team", {}).get("id")
                group = standing.get("group")
                if isinstance(team_id, int) and isinstance(group, str):
                    groups[team_id] = group
    return groups


def country_codes() -> dict[str, str]:
    mappings = json.loads(MAPPING_PATH.read_text(encoding="utf-8"))
    return {item["display_name"]: item["country_code"] for item in mappings}


def normalize_teams() -> list[dict[str, Any]]:
    codes = country_codes()
    return [
        {
            "team_id": slugify(item.get("team", {}).get("name", "")),
            "api_football_team_id": item.get("team", {}).get("id"),
            "name": item.get("team", {}).get("name"),
            "country": item.get("team", {}).get("country"),
            "country_code": item.get("team", {}).get("code") or codes.get(item.get("team", {}).get("name")),
            "source_type": "api_football",
            "source_name": "api_football_worldcup_2026",
            "is_real_data": True,
        }
        for item in read_response("teams")
        if item.get("team", {}).get("name")
    ]


def normalize_matches() -> list[dict[str, Any]]:
    groups = group_by_team_id()
    now = datetime.now(timezone.utc)
    matches = []
    for item in read_response("fixtures"):
        fixture = item.get("fixture", {})
        league = item.get("league", {})
        teams = item.get("teams", {})
        home = teams.get("home", {})
        away = teams.get("away", {})
        goals = item.get("goals", {})
        status_short = fixture.get("status", {}).get("short")
        kickoff = parse_date(fixture.get("date"))
        home_id = home.get("id")
        away_id = away.get("id")
        matches.append(
            {
                "match_id": f"api_football_{fixture.get('id')}",
                "api_football_fixture_id": fixture.get("id"),
                "competition": league.get("name") or "FIFA World Cup",
                "season": league.get("season"),
                "stage": stage_from_round(league.get("round")),
                "round": league.get("round"),
                "group": groups.get(home_id) if groups.get(home_id) == groups.get(away_id) else None,
                "home_team": home.get("name"),
                "away_team": away.get("name"),
                "home_team_id": home_id,
                "away_team_id": away_id,
                "kickoff_at": fixture.get("date"),
                "venue": fixture.get("venue", {}).get("name"),
                "city": fixture.get("venue", {}).get("city"),
                "status": normalized_status(status_short),
                "source_status": status_short,
                "home_score": goals.get("home"),
                "away_score": goals.get("away"),
                "source_type": "api_football",
                "source_name": "api_football_worldcup_2026",
                "is_real_data": True,
                "is_real_fixture": True,
                "is_future_fixture": bool(kickoff and kickoff > now and status_short in SCHEDULED_STATUSES),
                "model_inputs": {
                    "home_elo": 1500,
                    "away_elo": 1500,
                    "home_recent_goals_for": NEUTRAL_PROTOTYPE_XG,
                    "home_recent_goals_against": NEUTRAL_PROTOTYPE_XG,
                    "away_recent_goals_for": NEUTRAL_PROTOTYPE_XG,
                    "away_recent_goals_against": NEUTRAL_PROTOTYPE_XG,
                    "input_basis": "neutral_prototype_defaults_not_historically_calibrated",
                },
            }
        )
    return matches


def main() -> None:
    teams = normalize_teams()
    matches = normalize_matches()
    write_json(NORMALIZED_DIR / "api_football_teams.json", teams)
    write_json(NORMALIZED_DIR / "api_football_matches.json", matches)
    print(f"Normalized {len(matches)} API-Football fixtures and {len(teams)} teams.")


if __name__ == "__main__":
    main()
