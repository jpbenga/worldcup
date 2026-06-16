"""Select a deterministic quota-safe historical API-Football fixture sample."""

from __future__ import annotations

import argparse
import shutil
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, write_json

OUTPUT = "historical_api_sample_fixtures_v2_27_1.json"
SOURCE = DATA_DIR / "normalized" / "historical_matches_refreshed_v2_1.json"
ENDPOINTS = ("fixture_statistics", "events", "lineups", "player_statistics")


def publish(payload: dict[str, Any]) -> None:
    target = DATA_DIR / "generated" / OUTPUT
    write_json(payload, target)
    shutil.copy2(target, DATA_DIR / "snapshots" / OUTPUT)
    shutil.copy2(target, FRONTEND_DATA_DIR / OUTPUT)


def evenly_spaced(items: list[dict[str, Any]], count: int) -> list[dict[str, Any]]:
    if len(items) <= count:
        return items
    indexes = [round(index * (len(items) - 1) / (count - 1)) for index in range(count)]
    return [items[index] for index in indexes]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--max-fixtures-per-competition-season", type=int, default=5)
    parser.add_argument("--max-live-calls", type=int, default=500)
    parser.add_argument("--use-cache", action="store_true")
    args = parser.parse_args()
    matches: list[dict[str, Any]] = load_json(SOURCE)
    by_pair: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    by_competition: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for match in sorted(matches, key=lambda item: (item["kickoff_at"], item["api_football_fixture_id"])):
        by_pair[(str(match["competition"]), str(match["season"]))].append(match)
        by_competition[str(match["competition"])].append(match)
    ideal_count = sum(min(args.max_fixtures_per_competition_season, len(items)) for items in by_pair.values())
    ideal_calls = ideal_count * len(ENDPOINTS)
    fallback = ideal_calls > args.max_live_calls
    selected: list[dict[str, Any]] = []
    if fallback:
        for competition, items in sorted(by_competition.items()):
            for item in evenly_spaced(items, args.max_fixtures_per_competition_season):
                selected.append(item | {"selection_reason": "Quota fallback: stratified old/middle/recent fixture across the competition history."})
    else:
        for _, items in sorted(by_pair.items()):
            for item in evenly_spaced(items, args.max_fixtures_per_competition_season):
                selected.append(item | {"selection_reason": "Stratified fixture within competition-season."})
    rows = [
        {
            "competition": item["competition"],
            "season_or_year": str(item["season"]),
            "local_match_id": item["match_id"],
            "api_football_fixture_id": item["api_football_fixture_id"],
            "date": item["kickoff_at"],
            "home_team": item["home_team"],
            "away_team": item["away_team"],
            "home_score": item["home_score"],
            "away_score": item["away_score"],
            "selection_reason": item["selection_reason"],
        }
        for item in selected
    ]
    calls = {endpoint: len(rows) for endpoint in ENDPOINTS}
    payload = {
        "version": "v2.27.1",
        "sampling_policy": {
            "max_fixtures_per_competition_season": args.max_fixtures_per_competition_season,
            "cache_first": True,
            "quota_safe": len(rows) * len(ENDPOINTS) <= args.max_live_calls,
            "dry_run": args.dry_run or not args.live,
            "fallback_if_too_many": (
                f"Ideal competition-season sample would require {ideal_calls} calls; selected five stratified fixtures per competition instead."
                if fallback else "No fallback required."
            ),
            "ideal_fixture_count": ideal_count,
            "ideal_api_calls": ideal_calls,
        },
        "selected_fixtures": rows,
        "estimated_api_calls": calls | {"total": sum(calls.values()), "max_live_calls": args.max_live_calls},
        "warnings": [] if rows else ["No eligible historical fixture was selected."],
    }
    publish(payload)
    print(f"V2.27.1 historical sample: fixtures={len(rows)}, estimated_calls={sum(calls.values())}, fallback={fallback}")


if __name__ == "__main__":
    main()
