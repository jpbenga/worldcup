"""Fetch and normalize API-Football pre-match odds without exposing credentials."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.config.settings import API_FOOTBALL_KEY
from backend.data_acquisition.api_football_client import ApiFootballClient, ApiFootballError
from backend.scripts.pipeline_utils import DATA_DIR, load_json, utc_now, write_json

RAW_PATH = DATA_DIR / "raw/api_football/v2_23/odds.json"
SUPPORTED_MARKETS = {"match winner", "double chance", "home/away", "draw no bet", "goals over/under", "both teams score", "both teams to score"}


def publish(name: str, payload: dict) -> None:
    target = DATA_DIR / "generated" / name
    write_json(payload, target)
    shutil.copy2(target, DATA_DIR / "snapshots" / name)


def decimal(value: Any) -> float | None:
    try:
        result = float(value)
        return result if result > 1 else None
    except (TypeError, ValueError):
        return None


def normalize(payload: dict, request_count: int, source: str, warnings: list[str]) -> dict:
    known = {str(row["fixture_id"]): row for row in load_json(DATA_DIR / "generated/worldcup_2026_results_v2_6.json")["fixtures"]}
    fixtures = []
    for item in payload.get("response", []):
        fixture = item.get("fixture", {})
        fixture_id = str(fixture.get("id", ""))
        if fixture_id not in known:
            continue
        bookmakers = []
        for bookmaker in item.get("bookmakers", []):
            markets = []
            for bet in bookmaker.get("bets", []):
                if bet.get("name", "").strip().lower() not in SUPPORTED_MARKETS:
                    continue
                outcomes = [{"name": row.get("value", ""), "decimal_odds": decimal(row.get("odd"))} for row in bet.get("values", [])]
                outcomes = [row for row in outcomes if row["decimal_odds"]]
                if outcomes:
                    markets.append({"market_id": bet.get("id"), "name": bet.get("name", ""), "outcomes": outcomes})
            if markets:
                bookmakers.append({"bookmaker_id": bookmaker.get("id"), "name": bookmaker.get("name", ""), "markets": markets})
        if bookmakers:
            row = known[fixture_id]
            fixtures.append({
                "fixture_id": row["fixture_id"], "match_id": row["match_id"], "home_team": row["home_team"], "away_team": row["away_team"],
                "kickoff_at": row["kickoff_at"], "odds_updated_at": item.get("update", ""), "bookmakers": bookmakers,
            })
    available = bool(fixtures)
    return {
        "version": "v2.23", "source": "api-football", "fetched_at": utc_now(), "available": available,
        "reason": None if available else "no odds returned for known 2026 fixtures",
        "request_count": request_count, "fetch_mode": source, "fixtures": fixtures, "warnings": warnings,
        "limitations": ["Availability depends on API-Football subscription and bookmaker coverage.", "Odds are analysis data and never modify active predictions."],
    }


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch", action="store_true", help="Explicitly call API-Football. Default uses the cached response.")
    args = parser.parse_args(argv)
    warnings, payload, request_count, source = [], None, 0, "cached"
    if args.fetch:
        if not API_FOOTBALL_KEY:
            warnings.append("API_FOOTBALL_KEY is not configured; odds fetch skipped.")
        else:
            try:
                client = ApiFootballClient(max_calls=1)
                payload = client.get("odds", {"league": 1, "season": 2026, "page": 1})
                request_count = client.call_count
                write_json(payload, RAW_PATH)
                source = "api"
            except ApiFootballError as exc:
                warnings.append(f"Odds endpoint unavailable; cached data used when available: {exc}")
    if payload is None and RAW_PATH.exists():
        payload = load_json(RAW_PATH)
    if payload is None:
        existing_path = DATA_DIR / "generated/api_football_odds_snapshot_v2_23.json"
        if existing_path.exists():
            existing = load_json(existing_path)
            note = "Network fetch disabled; existing normalized odds snapshot preserved."
            if note not in existing.setdefault("warnings", []):
                existing["warnings"].append(note)
            publish("api_football_odds_snapshot_v2_23.json", existing)
            print(f"V2.23 odds snapshot preserved: available={existing.get('available', False)}, fixtures={len(existing.get('fixtures', []))}")
            return
        payload = {"response": []}
        warnings.append("No cached odds snapshot is available.")
    result = normalize(payload, request_count, source, warnings)
    publish("api_football_odds_snapshot_v2_23.json", result)
    print(f"V2.23 odds snapshot: available={result['available']}, fixtures={len(result['fixtures'])}, requests={request_count}")


if __name__ == "__main__":
    main()
