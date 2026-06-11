"""Fetch a bounded real historical international fixture dataset from API-Football."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

PROJECT_ROOT = __import__("pathlib").Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.data_acquisition.api_football_client import ApiFootballClient, ApiFootballError
from historical_data_utils import (
    COMPETITIONS,
    RAW_DIR,
    available_seasons,
    base_summary,
    filename_for,
    finished_items,
    load_json,
    relative,
    response_items,
    safe_errors,
)
from pipeline_utils import write_json


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preset", choices=("conservative",))
    parser.add_argument("--competition", choices=tuple(COMPETITIONS))
    parser.add_argument("--seasons", type=int, nargs="+")
    parser.add_argument("--max-requests", type=int, default=50)
    parser.add_argument("--force-refresh", action="store_true")
    args = parser.parse_args()

    competition = args.competition or "world_cup"
    requested = args.seasons or ([2014, 2018, 2022] if args.preset == "conservative" or not args.competition else [])
    available = available_seasons(COMPETITIONS[competition]["league_id"])
    selected = [season for season in requested if season in available]
    unavailable = [season for season in requested if season not in available]
    client = ApiFootballClient(max_calls=max(1, args.max_requests))
    entries = []
    failures = []
    fixtures_downloaded = 0
    finished_count = 0

    for season in selected:
        if client.call_count >= args.max_requests:
            failures.append({"competition": competition, "season": season, "error": "max request budget reached"})
            continue
        path = RAW_DIR / filename_for(competition, season)
        try:
            if path.exists() and not args.force_refresh:
                payload = load_json(path)
                status = "cached"
            else:
                payload = client.get(
                    "fixtures",
                    {"league": COMPETITIONS[competition]["league_id"], "season": season},
                )
                write_json(payload, path)
                status = "fetched"
            fixtures = len(response_items(payload))
            finished = len(finished_items(payload))
            fixtures_downloaded += fixtures
            finished_count += finished
            entries.append(
                {
                    "competition": competition,
                    "competition_name": COMPETITIONS[competition]["name"],
                    "league_id": COMPETITIONS[competition]["league_id"],
                    "season": season,
                    "status": "api_error" if safe_errors(payload) else status,
                    "fixtures_downloaded": fixtures,
                    "finished_fixtures": finished,
                    "errors": safe_errors(payload),
                    "path": relative(path),
                }
            )
        except (ApiFootballError, OSError, json.JSONDecodeError) as exc:
            failures.append({"competition": competition, "season": season, "error": str(exc)})

    summary: dict[str, Any] = {
        **base_summary(),
        "requested_competitions": [competition],
        "requested_seasons": requested,
        "available_seasons": available,
        "unavailable_requested_seasons": unavailable,
        "requests_executed": client.call_count,
        "max_requests": args.max_requests,
        "fixtures_downloaded": fixtures_downloaded,
        "finished_fixtures": finished_count,
        "files": entries,
        "failed_requests": failures,
        "quota_notes": [
            f"Execution capped at {args.max_requests} API calls.",
            "Cached raw fixture files do not consume API quota.",
        ],
        "usable_for_training": finished_count > 0,
    }
    write_json(summary, RAW_DIR / "fetch_historical_summary.json")
    print(
        f"Historical fetch complete: calls={client.call_count}, fixtures={fixtures_downloaded}, "
        f"finished={finished_count}, summary={relative(RAW_DIR / 'fetch_historical_summary.json')}"
    )


if __name__ == "__main__":
    main()
