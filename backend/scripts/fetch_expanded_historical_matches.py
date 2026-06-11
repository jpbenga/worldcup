"""Fetch a bounded expanded senior-international historical dataset."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.data_acquisition.api_football_client import ApiFootballClient, ApiFootballError
from historical_data_utils import (
    EXPANDED_COMPETITIONS,
    EXPANDED_PRESETS,
    RAW_DIR,
    available_seasons,
    finished_items,
    load_json,
    response_items,
    safe_errors,
)
from pipeline_utils import utc_now, write_json

EXPANDED_RAW = RAW_DIR / "expanded"


def plan(preset: str, competitions: list[str] | None) -> dict[str, list[int]]:
    source = EXPANDED_PRESETS[preset]
    keys = competitions or list(source)
    return {key: source.get(key, available_seasons(EXPANDED_COMPETITIONS[key]["league_id"])) for key in keys}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preset", choices=("conservative", "broad"), default="conservative")
    parser.add_argument("--max-requests", type=int, default=100)
    parser.add_argument("--competitions", nargs="+", choices=tuple(EXPANDED_COMPETITIONS))
    parser.add_argument("--force-refresh", action="store_true")
    args = parser.parse_args()
    requested = plan(args.preset, args.competitions)
    client = ApiFootballClient(max_calls=max(1, args.max_requests))
    files = []
    failures = []
    skipped = []
    total_fixtures = total_finished = 0
    EXPANDED_RAW.mkdir(parents=True, exist_ok=True)

    for key, seasons in requested.items():
        config = EXPANDED_COMPETITIONS[key]
        available = available_seasons(config["league_id"])
        for season in seasons:
            if season not in available:
                skipped.append({"competition": key, "season": season, "reason": "season unavailable"})
                continue
            target = EXPANDED_RAW / f"fixtures_{key}_{season}.json"
            legacy = RAW_DIR / f"fixtures_{key}_{season}.json"
            try:
                if target.exists() and not args.force_refresh:
                    payload, status = load_json(target), "cached"
                elif legacy.exists() and not args.force_refresh:
                    shutil.copy2(legacy, target)
                    payload, status = load_json(target), "copied_v0_7_cache"
                elif client.call_count < args.max_requests:
                    payload = client.get("fixtures", {"league": config["league_id"], "season": season})
                    write_json(payload, target)
                    status = "fetched"
                else:
                    skipped.append({"competition": key, "season": season, "reason": "request budget reached"})
                    continue
                fixture_count = len(response_items(payload))
                finished_count = len(finished_items(payload))
                total_fixtures += fixture_count
                total_finished += finished_count
                files.append(
                    {
                        "competition": key,
                        "competition_name": config["name"],
                        "league_id": config["league_id"],
                        "season": season,
                        "status": "api_error" if safe_errors(payload) else status,
                        "fixtures_downloaded": fixture_count,
                        "finished_fixtures": finished_count,
                        "errors": safe_errors(payload),
                        "path": target.relative_to(PROJECT_ROOT).as_posix(),
                    }
                )
            except (ApiFootballError, OSError, json.JSONDecodeError) as exc:
                failures.append({"competition": key, "season": season, "error": str(exc)})

    summary = {
        "generated_at": utc_now(),
        "scope": "expanded_international_historical_matches",
        "preset": args.preset,
        "requested_competitions": list(requested),
        "requested_seasons": requested,
        "requests_executed": client.call_count,
        "max_requests": args.max_requests,
        "fixtures_downloaded": total_fixtures,
        "finished_fixtures": total_finished,
        "files": files,
        "failed_requests": failures,
        "skipped_competitions": skipped,
        "quota_notes": ["Cached files consume no API quota.", f"Execution capped at {args.max_requests} API calls."],
        "usable_for_training_experiment": total_finished > 192,
    }
    write_json(summary, EXPANDED_RAW / "fetch_expanded_historical_summary.json")
    print(f"Expanded fetch: calls={client.call_count}, fixtures={total_fixtures}, finished={total_finished}.")


if __name__ == "__main__":
    main()
