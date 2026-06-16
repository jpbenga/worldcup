"""Audit API-Football historical fixture coverage with a strict call budget."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.config.settings import API_FOOTBALL_KEY
from backend.data_acquisition.api_football_client import ApiFootballClient, ApiFootballError
from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, utc_now, write_json

OUTPUT = "api_football_historical_stats_coverage_v2_27_1.json"
SAMPLE = DATA_DIR / "generated" / "historical_api_sample_fixtures_v2_27_1.json"
RAW = DATA_DIR / "raw" / "api_football" / "v2_27_1"
ENDPOINTS = {
    "statistics": "fixtures/statistics",
    "events": "fixtures/events",
    "lineups": "fixtures/lineups",
    "players": "fixtures/players",
}


def publish(payload: dict[str, Any]) -> None:
    target = DATA_DIR / "generated" / OUTPUT
    write_json(payload, target)
    shutil.copy2(target, DATA_DIR / "snapshots" / OUTPUT)
    shutil.copy2(target, FRONTEND_DATA_DIR / OUTPUT)


def response(payload: dict[str, Any]) -> list[Any]:
    value = payload.get("response", [])
    return value if isinstance(value, list) else []


def cached_call(client: ApiFootballClient | None, endpoint: str, fixture_id: int, allow_live: bool) -> tuple[dict[str, Any], bool]:
    path = RAW / f"{endpoint.replace('/', '_')}_{fixture_id}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8")), True
    if not allow_live or client is None:
        return {"response": [], "errors": ["cache_miss_live_disabled"]}, False
    payload = client.get(endpoint, {"fixture": fixture_id})
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload, False


def stat_fields(items: list[Any]) -> tuple[list[str], list[str]]:
    fields, nulls = set(), set()
    for team in items:
        for stat in team.get("statistics", []) if isinstance(team, dict) else []:
            name = str(stat.get("type"))
            fields.add(name)
            if stat.get("value") is None:
                nulls.add(name)
    return sorted(fields), sorted(nulls)


def player_fields(items: list[Any]) -> tuple[list[str], list[str]]:
    fields, present, nulls = set(), set(), set()
    for team in items:
        for player in team.get("players", []) if isinstance(team, dict) else []:
            for stats in player.get("statistics", []) if isinstance(player, dict) else []:
                for family, values in stats.items():
                    if not isinstance(values, dict):
                        continue
                    for key, value in values.items():
                        name = f"{family}.{key}"
                        fields.add(name)
                        if value is None:
                            nulls.add(name)
                        else:
                            present.add(name)
    return sorted(present or fields), sorted(nulls)


def rate(rows: list[dict[str, Any]], family: str, key: str = "available") -> float | None:
    return round(sum(bool(row[family][key]) for row in rows) / len(rows), 4) if rows else None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--use-cache", action="store_true")
    parser.add_argument("--max-live-calls", type=int, default=500)
    parser.add_argument("--cache-only", action="store_true")
    args = parser.parse_args()
    sample = load_json(SAMPLE)["selected_fixtures"]
    allow_live = not args.cache_only
    client = ApiFootballClient(max_calls=args.max_live_calls) if allow_live and API_FOOTBALL_KEY else None
    rows, warnings = [], []
    cache_hits = 0
    for fixture in sample:
        fixture_id = int(fixture["api_football_fixture_id"])
        payloads = {}
        for family, endpoint in ENDPOINTS.items():
            try:
                payloads[family], cached = cached_call(client, endpoint, fixture_id, allow_live)
                cache_hits += int(cached)
            except (ApiFootballError, OSError, json.JSONDecodeError) as exc:
                payloads[family] = {"response": [], "errors": [str(exc)]}
                warnings.append(f"{fixture_id} {family}: {exc}")
        stats, events = response(payloads["statistics"]), response(payloads["events"])
        lineups, players = response(payloads["lineups"]), response(payloads["players"])
        fields, null_fields = stat_fields(stats)
        pfields, pnulls = player_fields(players)
        event_types = sorted({str(item.get("type")) for item in events if isinstance(item, dict) and item.get("type")})
        event_details = sorted({str(item.get("detail")) for item in events if isinstance(item, dict) and item.get("detail")})
        goals_detected = sum(str(item.get("type")).lower() == "goal" for item in events if isinstance(item, dict))
        expected_goals = int(fixture["home_score"]) + int(fixture["away_score"])
        rows.append(
            {
                "competition": fixture["competition"],
                "season_or_year": fixture["season_or_year"],
                "fixture_id": fixture_id,
                "match": f"{fixture['home_team']} - {fixture['away_team']}",
                "date": fixture["date"],
                "score": f"{fixture['home_score']}-{fixture['away_score']}",
                "statistics": {
                    "available": bool(stats), "fields_detected": fields,
                    "xg_available": "expected_goals" in fields,
                    "shots_available": "Total Shots" in fields or "Shots on Goal" in fields,
                    "possession_available": "Ball Possession" in fields,
                    "corners_available": "Corner Kicks" in fields,
                    "passes_available": "Total passes" in fields or "Passes accurate" in fields,
                    "saves_available": "Goalkeeper Saves" in fields,
                    "null_fields": null_fields, "warnings": payloads["statistics"].get("errors") or [],
                },
                "events": {
                    "available": bool(events), "event_types": event_types, "event_details": event_details,
                    "goals_detected": goals_detected, "score_goals": expected_goals,
                    "score_consistent": goals_detected == expected_goals if events else None,
                    "cards_detected": "Card" in event_types, "substitutions_detected": "subst" in event_types,
                    "warnings": payloads["events"].get("errors") or [],
                },
                "lineups": {
                    "available": bool(lineups),
                    "formations_available": bool(lineups) and all(bool(item.get("formation")) for item in lineups if isinstance(item, dict)),
                    "starting_xi_available": bool(lineups) and all(len(item.get("startXI", [])) >= 11 for item in lineups if isinstance(item, dict)),
                    "warnings": payloads["lineups"].get("errors") or [],
                },
                "players": {
                    "available": bool(players), "fields_detected": pfields,
                    "ratings_available": "games.rating" in pfields, "shots_available": any(name.startswith("shots.") for name in pfields),
                    "passes_available": any(name.startswith("passes.") for name in pfields),
                    "duels_available": any(name.startswith("duels.") for name in pfields),
                    "null_fields": pnulls, "warnings": payloads["players"].get("errors") or [],
                },
            }
        )
    summary = {
        "fixtures_checked": len(rows),
        "statistics_available_rate": rate(rows, "statistics"),
        "xg_available_rate": rate(rows, "statistics", "xg_available"),
        "shots_available_rate": rate(rows, "statistics", "shots_available"),
        "possession_available_rate": rate(rows, "statistics", "possession_available"),
        "passes_available_rate": rate(rows, "statistics", "passes_available"),
        "events_available_rate": rate(rows, "events"),
        "lineups_available_rate": rate(rows, "lineups"),
        "players_available_rate": rate(rows, "players"),
    }
    payload = {
        "version": "v2.27.1", "source": "api-football", "fetched_at": utc_now(),
        "api_key_present": bool(API_FOOTBALL_KEY), "cache_used": cache_hits > 0, "cache_hits": cache_hits,
        "live_calls_used": client.call_count if client else 0, "max_live_calls": args.max_live_calls,
        "coverage_by_fixture": rows, "coverage_summary": summary, "warnings": warnings,
        "verdict": "PASS" if rows and not warnings else "WARNING",
    }
    publish(payload)
    print(f"V2.27.1 historical API audit: {payload['verdict']}; fixtures={len(rows)}; live_calls={payload['live_calls_used']}; cache_hits={cache_hits}")


if __name__ == "__main__":
    main()
