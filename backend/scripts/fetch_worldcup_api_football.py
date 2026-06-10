"""Fetch active World Cup API-Football data without persisting credentials."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.config.settings import API_FOOTBALL_KEY
from backend.data_acquisition.api_football_client import ApiFootballClient, ApiFootballError

RAW_DIR = PROJECT_ROOT / "backend" / "data" / "raw" / "api_football" / "worldcup_2026"
ENDPOINTS = {
    "fixtures": "fixtures",
    "teams": "teams",
    "standings": "standings",
    "rounds": "fixtures/rounds",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--season", type=int, default=2026)
    parser.add_argument("--league-id", type=int, default=1)
    parser.add_argument("--force-refresh", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not API_FOOTBALL_KEY:
        raise SystemExit("API_FOOTBALL_KEY is not configured in .env")
    summary: dict[str, Any] = {
        "fetched_at": utc_now(),
        "league_id": args.league_id,
        "season": args.season,
        "dry_run": args.dry_run,
        "endpoints": {},
    }
    if args.dry_run:
        for name, endpoint in ENDPOINTS.items():
            summary["endpoints"][name] = {
                "endpoint": endpoint,
                "params": {"league": args.league_id, "season": args.season},
                "status": "dry_run",
            }
        write_json(RAW_DIR / "fetch_summary.json", summary)
        print("Dry run complete; no API calls made.")
        return

    client = ApiFootballClient(max_calls=len(ENDPOINTS))
    for name, endpoint in ENDPOINTS.items():
        path = RAW_DIR / f"{name}.json"
        if path.exists() and not args.force_refresh:
            payload = json.loads(path.read_text(encoding="utf-8"))
            response = payload.get("response", []) if isinstance(payload, dict) else []
            errors = payload.get("errors") or [] if isinstance(payload, dict) else ["invalid cached payload"]
            items = len(response) if isinstance(response, list) else 0
            summary["endpoints"][name] = {
                "status": "cached_api_error" if errors else "cached_empty" if items == 0 else "cached",
                "items": items,
                "errors": errors,
                "path": str(path.relative_to(PROJECT_ROOT)),
            }
            continue
        try:
            payload = client.get(endpoint, {"league": args.league_id, "season": args.season})
            write_json(path, payload)
            response = payload.get("response", [])
            errors = payload.get("errors") or []
            items = len(response) if isinstance(response, list) else 0
            summary["endpoints"][name] = {
                "status": "api_error" if errors else "empty" if items == 0 else "fetched",
                "items": items,
                "errors": errors,
                "path": str(path.relative_to(PROJECT_ROOT)),
            }
        except (ApiFootballError, OSError, json.JSONDecodeError) as exc:
            summary["endpoints"][name] = {"status": "error", "items": 0, "error": str(exc)}

    statuses = {item["status"] for item in summary["endpoints"].values()}
    summary["status"] = "PASS" if statuses <= {"fetched", "cached"} else "PASS_WITH_ENDPOINT_ERRORS"
    summary["api_calls"] = client.call_count
    write_json(RAW_DIR / "fetch_summary.json", summary)
    print(f"World Cup fetch status: {summary['status']}; API calls: {client.call_count}")


if __name__ == "__main__":
    main()
