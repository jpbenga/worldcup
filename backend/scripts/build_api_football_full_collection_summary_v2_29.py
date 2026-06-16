"""Build V2.29 full historical API-Football collection summary from cache and manifest."""

from __future__ import annotations

import json
import shutil
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, write_json

VERSION = "v2.29"
OUTPUT = "api_football_full_collection_summary_v2_29.json"
MANIFEST = DATA_DIR / "generated" / "api_football_historical_stats_collection_manifest_v2_29.json"
CACHE_ROOT = DATA_DIR / "cache" / "api_football" / "historical_stats"
MATCHES = DATA_DIR / "normalized" / "historical_matches_refreshed_v2_1.json"
ENDPOINTS = ["statistics", "events", "lineups", "players"]


def publish(payload: dict[str, Any]) -> None:
    target = DATA_DIR / "generated" / OUTPUT
    write_json(payload, target)
    shutil.copy2(target, DATA_DIR / "snapshots" / OUTPUT)
    shutil.copy2(target, FRONTEND_DATA_DIR / OUTPUT)


def response(path: Path) -> list[Any]:
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    value = payload.get("response", [])
    return value if isinstance(value, list) else []


def stat_fields(items: list[Any]) -> set[str]:
    fields = set()
    for row in items:
        if isinstance(row, dict):
            for stat in row.get("statistics", []):
                if isinstance(stat, dict) and stat.get("type"):
                    fields.add(str(stat["type"]))
    return fields


def main() -> None:
    matches = load_json(MATCHES)
    manifest = load_json(MANIFEST) if MANIFEST.exists() else {}
    by_fixture = {int(match["api_football_fixture_id"]): match for match in matches}
    coverage = defaultdict(lambda: {"fixtures": 0, "statistics": 0, "xg": 0, "events": 0, "lineups": 0, "players": 0})
    season_cov = defaultdict(lambda: {"fixtures": 0, "statistics": 0, "xg": 0, "events": 0, "lineups": 0, "players": 0})
    totals = {"statistics": 0, "xg": 0, "events": 0, "lineups": 0, "players": 0}
    fixtures_with_any = 0
    for fixture_id, match in by_fixture.items():
        comp, season = str(match["competition"]), str(match["season"])
        coverage[comp]["fixtures"] += 1
        season_cov[season]["fixtures"] += 1
        any_data = False
        stats = response(CACHE_ROOT / str(fixture_id) / "statistics.json")
        fields = stat_fields(stats)
        if stats:
            totals["statistics"] += 1
            coverage[comp]["statistics"] += 1
            season_cov[season]["statistics"] += 1
            any_data = True
        if "expected_goals" in fields:
            totals["xg"] += 1
            coverage[comp]["xg"] += 1
            season_cov[season]["xg"] += 1
        for endpoint in ("events", "lineups", "players"):
            if response(CACHE_ROOT / str(fixture_id) / f"{endpoint}.json"):
                totals[endpoint] += 1
                coverage[comp][endpoint] += 1
                season_cov[season][endpoint] += 1
                any_data = True
        fixtures_with_any += int(any_data)
    units_total = len(matches) * len(ENDPOINTS)
    units_completed = int(manifest.get("completed_units", 0))
    def rate(count: int) -> float | None:
        return round(count / len(matches), 6) if matches else None
    def rows(source: dict[str, dict[str, int]]) -> list[dict[str, Any]]:
        result = []
        for key, values in sorted(source.items()):
            fixtures = values["fixtures"]
            result.append({
                "key": key, "fixtures": fixtures,
                "statistics_available_rate": round(values["statistics"] / fixtures, 6) if fixtures else None,
                "xg_available_rate": round(values["xg"] / fixtures, 6) if fixtures else None,
                "events_available_rate": round(values["events"] / fixtures, 6) if fixtures else None,
                "lineups_available_rate": round(values["lineups"] / fixtures, 6) if fixtures else None,
                "players_available_rate": round(values["players"] / fixtures, 6) if fixtures else None,
            })
        return result
    ready = units_completed >= int(units_total * 0.8) and totals["statistics"] >= int(len(matches) * 0.5)
    payload = {
        "version": VERSION,
        "fixtures_total": len(matches),
        "endpoints": ENDPOINTS,
        "units_total": units_total,
        "units_completed": units_completed,
        "units_remaining": max(0, units_total - units_completed),
        "fixtures_with_any_stats": fixtures_with_any,
        "statistics_available_rate": rate(totals["statistics"]),
        "xg_available_rate": rate(totals["xg"]),
        "events_available_rate": rate(totals["events"]),
        "lineups_available_rate": rate(totals["lineups"]),
        "players_available_rate": rate(totals["players"]),
        "coverage_by_competition": rows(coverage),
        "coverage_by_season": rows(season_cov),
        "ready_for_model_retest": ready,
        "reason": "Ready only after broad cache coverage is collected." if not ready else "Sufficient collection coverage for a model retest gate.",
        "manifest_stop_reason": manifest.get("last_stop_reason"),
        "live_calls_last_run": manifest.get("live_calls_this_run", 0),
    }
    publish(payload)
    print(f"V2.29 full collection summary: completed={units_completed}/{units_total}, ready_for_model_retest={ready}")


if __name__ == "__main__":
    main()
