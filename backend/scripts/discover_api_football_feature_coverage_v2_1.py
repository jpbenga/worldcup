"""Discover cached API-Football international feature coverage without spending quota."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.scripts.v2_1_data_utils import (
    INTERNATIONAL_COMPETITIONS,
    base_report,
    league_inventory,
    publish,
    write_doc,
)


def main() -> None:
    inventory = league_inventory()
    checked = []
    seasons_checked = []
    feature_claims: dict[str, list[bool]] = {name: [] for name in ("statistics", "events", "lineups", "standings", "odds")}
    for key, config in INTERNATIONAL_COMPETITIONS.items():
        source = inventory.get(config["league_id"], {})
        seasons = []
        for season in source.get("seasons", []):
            year = season.get("year")
            if not isinstance(year, int) or year > 2026:
                continue
            coverage = season.get("coverage", {})
            fixture_coverage = coverage.get("fixtures", {})
            record = {
                "competition": key,
                "league_id": config["league_id"],
                "season": year,
                "start": season.get("start"),
                "end": season.get("end"),
                "current": season.get("current"),
                "features": {
                    "fixtures": True,
                    "statistics": fixture_coverage.get("statistics_fixtures"),
                    "events": fixture_coverage.get("events"),
                    "lineups": fixture_coverage.get("lineups"),
                    "standings": coverage.get("standings"),
                    "odds": coverage.get("odds"),
                },
            }
            seasons.append(record)
            seasons_checked.append({"competition": key, "season": year})
            for feature in feature_claims:
                if isinstance(record["features"][feature], bool):
                    feature_claims[feature].append(record["features"][feature])
        checked.append(
            {
                "key": key,
                "league_id": config["league_id"],
                "name": config["name"],
                "type": source.get("league", {}).get("type"),
                "country": source.get("country", {}).get("name"),
                "is_club_competition": source.get("country", {}).get("name") != "World",
                "seasons": seasons,
            }
        )
    available = {"fixtures": True}
    for feature, values in feature_claims.items():
        available[feature] = any(values) if values else None
    report: dict[str, Any] = base_report() | {
        "status": "coverage_discovery",
        "source": "cached_api_football_leagues_inventory",
        "request_count": 0,
        "competitions_checked": checked,
        "seasons_checked": seasons_checked,
        "coverage": {
            item["key"]: {
                "seasons": len(item["seasons"]),
                "statistics_seasons": sum(s["features"]["statistics"] is True for s in item["seasons"]),
                "events_seasons": sum(s["features"]["events"] is True for s in item["seasons"]),
                "lineups_seasons": sum(s["features"]["lineups"] is True for s in item["seasons"]),
            }
            for item in checked
        },
        "available_features": available,
        "limitations": [
            "Coverage flags are provider metadata and must be verified on actual finished fixtures.",
            "Odds coverage does not establish pre-match timestamp provenance.",
            "Neutral-site is not exposed as a reliable league coverage field.",
        ],
        "recommendations": [
            "Probe statistics, events and lineups on a bounded sample of finished fixtures.",
            "Keep odds separate from V2.2 features unless pre-match provenance is proven.",
        ],
    }
    publish("api_football_feature_coverage_v2_1.json", report)
    write_doc(
        "API_FOOTBALL_FEATURE_COVERAGE_V2_1.md",
        f"""# API-Football Feature Coverage V2.1

## Scope

V2.1 inspected the cached API-Football `/leagues` inventory for
`{len(checked)}` explicitly allowlisted senior-international competitions and
`{len(seasons_checked)}` competition-season records. No API request was needed,
so request count is `0`.

Provider metadata claims that finished-fixture statistics, events and lineups
exist for many major competitions and qualifiers. Standings are competition
dependent; odds coverage is sparse and remains benchmark-only. These metadata
flags are not treated as proof of row-level availability.

## Available Features

`{available}`

## Safety And Limitations

All checked competitions are World/international entries from an explicit
allowlist; club competitions are excluded. Future World Cup 2026 fixtures are
not acquired by this discovery step. The next script probes row-level
statistics, events and lineups on a bounded sample of completed matches.
""",
    )
    print(f"V2.1 coverage discovery: competitions={len(checked)}, seasons={len(seasons_checked)}, requests=0.")


if __name__ == "__main__":
    main()
