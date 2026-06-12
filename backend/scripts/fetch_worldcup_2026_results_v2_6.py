"""Fetch or read cached World Cup 2026 fixture results without touching predictions."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.config.settings import API_FOOTBALL_KEY
from backend.data_acquisition.api_football_client import ApiFootballClient, ApiFootballError
from backend.scripts.pipeline_utils import DATA_DIR, load_json, utc_now, write_json
from backend.scripts.v2_6_live_utils import VERSION, publish, release_matches

RAW_DIR = DATA_DIR / "raw" / "api_football" / "v2_6" / "worldcup_results"
STATUS_MAP = {
    "NS": "not_started", "TBD": "not_started",
    "1H": "live", "HT": "live", "2H": "live", "ET": "live", "BT": "live", "P": "live", "SUSP": "live", "INT": "live", "LIVE": "live",
    "FT": "finished", "AET": "finished", "PEN": "finished",
    "PST": "postponed", "CANC": "cancelled", "ABD": "cancelled", "AWD": "finished", "WO": "finished",
}


def normalized_fixture(item: dict[str, Any], match_id: str | None) -> dict[str, Any]:
    fixture = item.get("fixture", {})
    teams = item.get("teams", {})
    goals = item.get("goals", {})
    short = fixture.get("status", {}).get("short")
    status = STATUS_MAP.get(short, "unknown")
    home, away = goals.get("home"), goals.get("away")
    winner = "home" if home is not None and away is not None and home > away else "away" if home is not None and away is not None and away > home else "draw" if home is not None and away is not None else None
    return {
        "fixture_id": fixture.get("id"),
        "match_id": match_id,
        "home_team": teams.get("home", {}).get("name", ""),
        "away_team": teams.get("away", {}).get("name", ""),
        "kickoff_at": fixture.get("date", ""),
        "status": status,
        "elapsed": fixture.get("status", {}).get("elapsed"),
        "actual_score": {"home": home, "away": away},
        "winner": winner,
        "source_updated_at": fixture.get("date", ""),
        "confidence": "official" if status in {"live", "finished", "postponed", "cancelled"} else "cached",
        "source_status": short,
    }


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force-refresh", action="store_true")
    args = parser.parse_args(argv)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    raw_path = RAW_DIR / "fixtures.json"
    request_count, notes, source = 0, [], "cached"
    payload: dict[str, Any] | None = None
    if API_FOOTBALL_KEY and (args.force_refresh or not raw_path.exists()):
        try:
            client = ApiFootballClient(max_calls=1)
            payload = client.get("fixtures", {"league": 1, "season": 2026})
            request_count = client.call_count
            write_json(payload, raw_path)
            source = "api_football"
        except ApiFootballError as exc:
            notes.append(f"API fetch failed; cached fixture data used when available: {exc}")
    elif not API_FOOTBALL_KEY:
        notes.append("API_FOOTBALL_KEY is not configured; cached fixture data used when available.")
    if payload is None and raw_path.exists():
        payload = load_json(raw_path)
    if payload is None:
        fallback = DATA_DIR / "raw" / "api_football" / "worldcup_2026" / "fixtures.json"
        payload = load_json(fallback) if fallback.exists() else {"response": []}
        source = "api_football_or_cached"

    by_id = {str(match["fixture_id"]): match["match_id"] for match in release_matches()}
    fixtures = [normalized_fixture(item, by_id.get(str(item.get("fixture", {}).get("id")))) for item in payload.get("response", [])]
    existing = {str(item["fixture_id"]): item for item in fixtures}
    for match in release_matches():
        if str(match["fixture_id"]) not in existing:
            fixtures.append({
                "fixture_id": match["fixture_id"], "match_id": match["match_id"], "home_team": match["home_team"],
                "away_team": match["away_team"], "kickoff_at": match["kickoff_at"], "status": "unknown", "elapsed": None,
                "actual_score": {"home": None, "away": None}, "winner": None, "source_updated_at": "",
                "confidence": "unknown", "source_status": None,
            })
    fixtures.sort(key=lambda item: item["kickoff_at"])
    counts = {status: sum(item["status"] == status for item in fixtures) for status in ("finished", "live", "not_started", "postponed", "cancelled", "unknown")}
    report = {
        "version": VERSION, "source": source, "generated_at": utc_now(), "request_count": request_count,
        "fixture_count": len(fixtures), "finished_count": counts["finished"], "live_count": counts["live"],
        "not_started_count": counts["not_started"], "postponed_count": counts["postponed"],
        "cancelled_count": counts["cancelled"], "unknown_count": counts["unknown"],
        "result_available": counts["finished"] + counts["live"] > 0, "fixtures": fixtures, "notes": notes,
    }
    publish(report, "worldcup_2026_results_v2_6.json")
    (ROOT / "docs" / "WORLDCUP_2026_RESULTS_FETCH_V2_6.md").write_text(
        f"""# World Cup 2026 Results Fetch V2.6

V2.6 published a separate results overlay for all `{len(fixtures)}` release-candidate fixtures. The fetch used `{source}` and made `{request_count}` API request(s). It found `{counts["finished"]}` finished, `{counts["live"]}` live and `{counts["not_started"]}` not-started fixtures.

Pre-match predictions were not opened for writing or recalculated. Results remain a separate evaluation layer. When the API key or result data is unavailable, this script still publishes a complete status file and reports `result_available: false`.

Statuses are normalized into not-started, live, finished, postponed, cancelled
or unknown. Only the cached raw API response and the separate V2.6 result
artifacts are written. Credentials are loaded through the existing local
configuration and are never included in logs or published JSON.
""", encoding="utf-8")
    print(f"V2.6 results: requests={request_count}, finished={counts['finished']}, live={counts['live']}, available={report['result_available']}")


if __name__ == "__main__":
    main()
