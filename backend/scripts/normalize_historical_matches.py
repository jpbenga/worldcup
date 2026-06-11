"""Normalize isolated historical API-Football fixtures into a training-candidate dataset."""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from historical_data_utils import FINISHED_STATUSES, RAW_DIR, load_json, publish, response_items
from pipeline_utils import DATA_DIR, write_json


def winner(home: int, away: int) -> str:
    return "home" if home > away else "away" if away > home else "draw"


def normalize(item: dict[str, Any]) -> dict[str, Any] | None:
    fixture = item.get("fixture", {})
    league = item.get("league", {})
    teams = item.get("teams", {})
    goals = item.get("goals", {})
    fixture_id = fixture.get("id")
    season = league.get("season")
    home_score = goals.get("home")
    away_score = goals.get("away")
    status = fixture.get("status", {}).get("short")
    if (
        not isinstance(fixture_id, int)
        or season == 2026
        or status not in FINISHED_STATUSES
        or not isinstance(home_score, int)
        or not isinstance(away_score, int)
    ):
        return None
    return {
        "match_id": f"api_football_{fixture_id}",
        "api_football_fixture_id": fixture_id,
        "competition": league.get("name"),
        "competition_id": league.get("id"),
        "season": season,
        "stage": league.get("round"),
        "round": league.get("round"),
        "home_team": teams.get("home", {}).get("name"),
        "away_team": teams.get("away", {}).get("name"),
        "home_team_id": teams.get("home", {}).get("id"),
        "away_team_id": teams.get("away", {}).get("id"),
        "kickoff_at": fixture.get("date"),
        "venue": fixture.get("venue", {}).get("name"),
        "city": fixture.get("venue", {}).get("city"),
        "status": "finished",
        "source_status": status,
        "home_score": home_score,
        "away_score": away_score,
        "winner": winner(home_score, away_score),
        "source_type": "api_football",
        "source_name": "api_football_historical",
        "is_real_data": True,
        "is_future_fixture": False,
        "usable_for_training": True,
    }


def main() -> None:
    by_id = {}
    rejected = 0
    files = sorted(RAW_DIR.glob("fixtures_*.json"))
    for path in files:
        for item in response_items(load_json(path)):
            match = normalize(item)
            if match is None:
                rejected += 1
                continue
            by_id[match["api_football_fixture_id"]] = match
    matches = sorted(by_id.values(), key=lambda match: (match.get("kickoff_at") or "", match["api_football_fixture_id"]))
    write_json(matches, DATA_DIR / "normalized" / "historical_matches.json")

    competitions: defaultdict[str, dict[str, Any]] = defaultdict(lambda: {"seasons": set(), "matches": 0})
    teams = set()
    dates = []
    for match in matches:
        competitions[str(match["competition"])]["seasons"].add(match["season"])
        competitions[str(match["competition"])]["matches"] += 1
        teams.update((match["home_team_id"], match["away_team_id"]))
        dates.append(match["kickoff_at"])
    summary = {
        "total_matches": len(matches),
        "source_files": [path.relative_to(PROJECT_ROOT).as_posix() for path in files],
        "rejected_or_future_fixtures": rejected,
        "competitions": {
            name: {"seasons": sorted(values["seasons"]), "matches": values["matches"]}
            for name, values in sorted(competitions.items())
        },
        "teams_count": len({team for team in teams if team is not None}),
        "date_min": min(dates) if dates else None,
        "date_max": max(dates) if dates else None,
        "usable_for_training": bool(matches),
        "limitations": (
            [
                "The conservative dataset contains World Cup fixtures only.",
                "AET/PEN fixtures are retained; regulation-time score semantics must be defined before model fitting.",
                "Pre-match Elo history, neutral-site validation and advanced statistics are not included.",
            ]
            if matches
            else ["No finished historical fixture with complete scores was available."]
        ),
    }
    publish("historical_matches_summary.json", summary)
    print(f"Normalized {len(matches)} historical matches from {len(files)} raw files; rejected={rejected}.")


if __name__ == "__main__":
    main()
