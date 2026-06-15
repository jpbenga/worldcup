"""Explore API-Football match statistics with a strict quota-safe call budget."""

from __future__ import annotations

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

OUTPUT = "api_football_statistics_exploration_v2_27.json"
RAW_DIR = DATA_DIR / "raw" / "api_football" / "v2_27"
FIXTURES = [
    ("germany_curacao", 1489374),
    ("spain_cape_verde", 1489380),
    ("sweden_tunisia", 1539002),
]
ENDPOINTS = {
    "fixture_statistics": "fixtures/statistics",
    "events": "fixtures/events",
    "lineups": "fixtures/lineups",
    "player_statistics": "fixtures/players",
}


def publish(payload: dict[str, Any]) -> None:
    target = DATA_DIR / "generated" / OUTPUT
    write_json(payload, target)
    shutil.copy2(target, DATA_DIR / "snapshots" / OUTPUT)
    shutil.copy2(target, FRONTEND_DATA_DIR / OUTPUT)


def cached_call(client: ApiFootballClient, endpoint: str, fixture_id: int) -> tuple[dict[str, Any], bool]:
    path = RAW_DIR / f"{endpoint.replace('/', '_')}_{fixture_id}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8")), True
    payload = client.get(endpoint, {"fixture": fixture_id})
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload, False


def response(payload: dict[str, Any]) -> list[Any]:
    value = payload.get("response", [])
    return value if isinstance(value, list) else []


def statistic_fields(items: list[Any]) -> list[str]:
    return sorted({
        str(stat.get("type"))
        for team in items if isinstance(team, dict)
        for stat in team.get("statistics", []) if isinstance(stat, dict) and stat.get("type")
    })


def generic_fields(items: list[Any]) -> list[str]:
    return sorted({str(key) for item in items if isinstance(item, dict) for key in item})


def statistic_values(items: list[Any]) -> dict[str, dict[str, Any]]:
    return {
        str(team.get("team", {}).get("name")): {
            str(stat.get("type")): stat.get("value")
            for stat in team.get("statistics", []) if isinstance(stat, dict) and stat.get("type")
        }
        for team in items if isinstance(team, dict) and team.get("team", {}).get("name")
    }


def fixture_summary(fixture_id: int, payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    stats = response(payloads["fixture_statistics"])
    fields = statistic_fields(stats)
    events = response(payloads["events"])
    lineups = response(payloads["lineups"])
    players = response(payloads["player_statistics"])
    return {
        "fixture_id": fixture_id,
        "stats_available": bool(stats),
        "xg_available": "expected_goals" in fields,
        "events_available": bool(response(payloads["events"])),
        "lineups_available": bool(response(payloads["lineups"])),
        "player_statistics_available": bool(response(payloads["player_statistics"])),
        "fields": {
            "statistics": fields,
            "statistics_by_team": statistic_values(stats),
            "events": generic_fields(events),
            "event_types": sorted({str(row.get("type")) for row in events if isinstance(row, dict) and row.get("type")}),
            "event_details": sorted({str(row.get("detail")) for row in events if isinstance(row, dict) and row.get("detail")}),
            "event_count": len(events),
            "lineups": generic_fields(lineups),
            "formations": {str(row.get("team", {}).get("name")): row.get("formation") for row in lineups if isinstance(row, dict)},
            "player_statistics": generic_fields(players),
            "players_with_statistics": sum(len(row.get("players", [])) for row in players if isinstance(row, dict)),
        },
    }


def coverage(fixtures: list[dict[str, Any]], key: str) -> dict[str, Any]:
    count = sum(bool(row[key]) for row in fixtures)
    return {"fixtures_with_data": count, "fixtures_checked": len(fixtures), "rate": count / len(fixtures)}


def main() -> None:
    if not API_FOOTBALL_KEY:
        raise SystemExit("API_FOOTBALL_KEY is not configured")
    client = ApiFootballClient(max_calls=14)
    fixture_payloads: dict[str, dict[str, dict[str, Any]]] = {}
    warnings = []
    cache_hits = 0
    for key, fixture_id in FIXTURES:
        fixture_payloads[key] = {}
        for family, endpoint in ENDPOINTS.items():
            try:
                payload, cached = cached_call(client, endpoint, fixture_id)
                fixture_payloads[key][family] = payload
                cache_hits += int(cached)
            except ApiFootballError as exc:
                fixture_payloads[key][family] = {"response": [], "errors": [str(exc)]}
                warnings.append(f"{family} fixture {fixture_id}: {exc}")
    # Probe subscription availability for two useful adjacent families on the main case.
    adjacent = {}
    for family, endpoint in (("predictions", "predictions"), ("odds", "odds")):
        try:
            payload, cached = cached_call(client, endpoint, FIXTURES[0][1])
            adjacent[family] = {"available": bool(response(payload)), "errors": payload.get("errors") or []}
            cache_hits += int(cached)
        except ApiFootballError as exc:
            adjacent[family] = {"available": False, "errors": [str(exc)]}
            warnings.append(f"{family}: {exc}")

    fixtures = [
        {"case": key, **fixture_summary(fixture_id, fixture_payloads[key])}
        for key, fixture_id in FIXTURES
    ]
    families = {}
    for family in ENDPOINTS:
        items_by_fixture = [response(fixture_payloads[key][family]) for key, _ in FIXTURES]
        fields = statistic_fields([item for rows in items_by_fixture for item in rows]) if family == "fixture_statistics" else generic_fields([item for rows in items_by_fixture for item in rows])
        flag = {
            "fixture_statistics": "stats_available",
            "events": "events_available",
            "lineups": "lineups_available",
            "player_statistics": "player_statistics_available",
        }[family]
        family_coverage = coverage(fixtures, flag)
        families[family] = {
            "available": family_coverage["fixtures_with_data"] > 0,
            "fields_detected": fields,
            "coverage": family_coverage,
            "limitations": [] if family_coverage["rate"] == 1 else ["Coverage is incomplete across the checked finished fixtures."],
        }
    xg_coverage = coverage(fixtures, "xg_available")
    families["xg"] = {
        "available": xg_coverage["fixtures_with_data"] > 0,
        "field_names_detected": ["expected_goals"] if xg_coverage["fixtures_with_data"] else [],
        "coverage": xg_coverage,
        "limitations": [] if xg_coverage["rate"] == 1 else ["xG is missing for at least one checked fixture and must be treated as fragile."],
    }
    stats_fields = set(families["fixture_statistics"]["fields_detected"])
    payload = {
        "version": "v2.27",
        "source": "api-football",
        "fetched_at": utc_now(),
        "api_key_present": True,
        "quota_safe_mode": True,
        "quota": {"max_live_calls": 14, "live_calls_used": client.call_count, "cache_hits": cache_hits},
        "fixtures_checked": fixtures,
        "endpoint_availability": families | {
            "fixture_details": {"available": True, "source": "existing cached World Cup fixtures/results"},
            "team_statistics": {"available": None, "limitations": ["Not probed: league/team/season endpoint is not a fixture-level post-match source."]},
            "odds": adjacent["odds"],
            "predictions": adjacent["predictions"],
        },
        "germany_curacao": next(row for row in fixtures if row["case"] == "germany_curacao"),
        "spain_cape_verde": next(row for row in fixtures if row["case"] == "spain_cape_verde"),
        "data_classification": {
            "pre_match": ["fixture identity and schedule", "teams", "odds when available", "lineups only if published before kickoff"],
            "live": ["events", "score", "cards", "substitutions", "statistics snapshots when refreshed during play"],
            "post_match": ["shots", "shots on target", "possession", "corners", "fouls", "cards", "passes", "goalkeeper saves", "events", "player statistics", "expected_goals when covered"],
        },
        "model_enrichment_opportunities": [
            "Build a post-match performance explanation layer from shots, possession, xG and events.",
            "Measure historical coverage before using any statistic as a future model feature.",
            "Create lagged team-performance features only from statistics known before the future target match.",
            "Keep live probability updates separate from frozen pre-match predictions.",
        ],
        "not_usable_now": [
            "Post-match statistics as retroactive pre-match features.",
            "Attacks or dangerous attacks when absent from detected fixture-statistics fields.",
            "Any field with incomplete historical coverage before a chronological backtest.",
            "Attacks and dangerous attacks: absent from the checked fixture-statistics payloads.",
        ],
        "field_presence": {
            name: name in stats_fields for name in (
                "Shots on Goal", "Total Shots", "Ball Possession", "Corner Kicks", "Fouls",
                "Yellow Cards", "Red Cards", "Total passes", "Goalkeeper Saves", "expected_goals",
            )
        },
        "warnings": warnings,
        "coverage_warning": "Three finished fixtures showed complete endpoint coverage, but this is not proof of complete historical coverage.",
        "verdict": "PASS" if not warnings else "WARNING",
    }
    publish(payload)
    print(f"V2.27 API-Football statistics exploration: {payload['verdict']}; live_calls={client.call_count}")


if __name__ == "__main__":
    main()
