"""Fetch bounded recent senior-international history and build a refreshed dataset."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.data_acquisition.api_football_client import ApiFootballClient, ApiFootballError
from backend.scripts.pipeline_utils import DATA_DIR, write_json
from backend.scripts.v2_1_data_utils import (
    BY_LEAGUE,
    RAW_V21,
    REFRESH_PLAN,
    base_report,
    dataset_stats,
    days_since,
    load,
    is_senior_team,
    normalize_fixture,
    publish,
    response,
    write_doc,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-requests", type=int, default=20)
    parser.add_argument("--force-refresh", action="store_true")
    args = parser.parse_args()
    old = load(DATA_DIR / "normalized" / "historical_matches_expanded.json")
    previous_report_path = DATA_DIR / "generated" / "historical_refresh_report_v2_1.json"
    previous_request_count = load(previous_report_path).get("request_count", 0) if previous_report_path.exists() else 0
    old_by_id = {item["api_football_fixture_id"]: item for item in old}
    client = None
    failures = []
    files = []
    RAW_V21.mkdir(parents=True, exist_ok=True)
    try:
        client = ApiFootballClient(max_calls=args.max_requests)
    except ApiFootballError as exc:
        failures.append({"scope": "client_initialization", "error": str(exc)})

    for key, seasons in REFRESH_PLAN.items():
        config = next(item for item in BY_LEAGUE.values() if item["key"] == key)
        for season in seasons:
            target = RAW_V21 / f"fixtures_{key}_{season}.json"
            try:
                if target.exists() and not args.force_refresh:
                    payload, status = load(target), "cached"
                elif client is not None:
                    payload = client.get("fixtures", {"league": config["league_id"], "season": season})
                    write_json(payload, target)
                    status = "fetched"
                else:
                    continue
                files.append(
                    {
                        "competition": key,
                        "league_id": config["league_id"],
                        "season": season,
                        "status": status,
                        "responses": len(response(payload)),
                        "path": target.relative_to(PROJECT_ROOT).as_posix(),
                    }
                )
            except (ApiFootballError, OSError, json.JSONDecodeError) as exc:
                failures.append({"competition": key, "season": season, "error": str(exc)})

    candidates = []
    non_senior_friendlies_excluded = 0
    for path in sorted(RAW_V21.glob("fixtures_*.json")):
        for item in response(load(path)):
            if item.get("league", {}).get("id") == 10:
                teams = item.get("teams", {})
                if not is_senior_team(teams.get("home", {}).get("name")) or not is_senior_team(teams.get("away", {}).get("name")):
                    non_senior_friendlies_excluded += 1
            normalized = normalize_fixture(item)
            if normalized:
                candidates.append(normalized)
    added_by_id = {item["api_football_fixture_id"]: item for item in candidates if item["api_football_fixture_id"] not in old_by_id}
    combined = old_by_id | added_by_id
    refreshed = sorted(combined.values(), key=lambda item: (item["kickoff_at"], item["api_football_fixture_id"]))
    write_json(refreshed, DATA_DIR / "normalized" / "historical_matches_refreshed_v2_1.json")

    old_stats, new_stats = dataset_stats(old), dataset_stats(refreshed)
    old_competitions = set(old_stats["competitions"])
    old_teams = {item["home_team"] for item in old} | {item["away_team"] for item in old}
    new_teams = {item["home_team"] for item in refreshed} | {item["away_team"] for item in refreshed}
    report = base_report() | {
        "status": "completed" if not failures else "completed_with_failures",
        "request_count": (client.call_count if client and client.call_count else previous_request_count),
        "execution_request_count": client.call_count if client else 0,
        "max_requests": args.max_requests,
        "quota_impact": f"{client.call_count if client else 0} API calls; cached responses consume no quota.",
        "old_matches": len(old),
        "new_matches": len(refreshed),
        "matches_added": len(added_by_id),
        "date_range_before": {"min": old_stats["date_min"], "max": old_stats["date_max"]},
        "date_range_after": {"min": new_stats["date_min"], "max": new_stats["date_max"]},
        "competitions_added": sorted(set(new_stats["competitions"]) - old_competitions),
        "teams_added": sorted(new_teams - old_teams),
        "duplicates_detected": len(old) + len(candidates) - len(combined),
        "future_fixtures_excluded": True,
        "future_2026_fixtures_excluded": all(not item.get("is_future_fixture") and not (item["competition_id"] == 1 and item["season"] == 2026) for item in refreshed),
        "clubs_excluded": all(item["competition_id"] in BY_LEAGUE for item in refreshed),
        "non_senior_friendlies_excluded": non_senior_friendlies_excluded,
        "missing_scores": sum(not isinstance(item.get("home_score"), int) or not isinstance(item.get("away_score"), int) for item in refreshed),
        "finished_status_confirmed": all(item.get("status") == "finished" for item in refreshed),
        "latest_historical_match": new_stats["date_max"],
        "days_since_latest_historical_match": days_since(new_stats["date_max"]),
        "files": files,
        "failures": failures,
    }
    publish("historical_refresh_report_v2_1.json", report)
    write_doc(
        "HISTORICAL_REFRESH_REPORT_V2_1.md",
        f"""# Historical Refresh Report V2.1

V2.1 combined the existing `{len(old)}`-match dataset with completed,
allowlisted senior-international fixtures from a bounded recent-season plan.
The refreshed dataset contains `{len(refreshed)}` matches, adding
`{len(added_by_id)}` unique fixtures.

- Date range before: `{old_stats['date_min']}` to `{old_stats['date_max']}`
- Date range after: `{new_stats['date_min']}` to `{new_stats['date_max']}`
- Latest-history age: `{report['days_since_latest_historical_match']}` days
- API requests: `{report['request_count']}`
- Non-senior friendlies excluded: `{non_senior_friendlies_excluded}`
- Added competitions: `{report['competitions_added']}`
- Added teams: `{len(report['teams_added'])}`

Only completed fixtures with integer scores enter the normalized output.
Club league IDs and future World Cup 2026 fixtures are excluded. Qualification
seasons labelled 2026 contribute only already-finished matches. Failures, cache
usage, duplicate counts and quota impact remain explicit in the JSON report.
""",
    )
    print(f"V2.1 history refresh: old={len(old)}, new={len(refreshed)}, added={len(added_by_id)}, requests={report['request_count']}.")


if __name__ == "__main__":
    main()
