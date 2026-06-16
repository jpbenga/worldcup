"""Respectful resumable full historical API-Football stats collector."""

from __future__ import annotations

import argparse
import json
import random
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.config.settings import API_FOOTBALL_BASE_URL, API_FOOTBALL_KEY
from backend.scripts.pipeline_utils import DATA_DIR, load_json, write_json

VERSION = "v2.29"
MATCHES_PATH = DATA_DIR / "normalized" / "historical_matches_refreshed_v2_1.json"
MANIFEST_NAME = "api_football_historical_stats_collection_manifest_v2_29.json"
MANIFEST_PATH = DATA_DIR / "generated" / MANIFEST_NAME
SNAPSHOT_PATH = DATA_DIR / "snapshots" / MANIFEST_NAME
CACHE_ROOT = DATA_DIR / "cache" / "api_football" / "historical_stats"
LEGACY_CACHE_ROOTS = [
    DATA_DIR / "raw" / "api_football" / "v2_27_1",
    DATA_DIR / "raw" / "api_football" / "v2_27",
]
ENDPOINT_MAP = {
    "statistics": "fixtures/statistics",
    "events": "fixtures/events",
    "lineups": "fixtures/lineups",
    "players": "fixtures/players",
}
LEGACY_PREFIX = {
    "statistics": "fixtures_statistics",
    "events": "fixtures_events",
    "lineups": "fixtures_lineups",
    "players": "fixtures_players",
}
STATUSES = ("pending", "cached", "fetched", "empty", "failed", "skipped", "rate_limited")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def endpoint_list(value: str) -> list[str]:
    items = [item.strip() for item in value.split(",") if item.strip()]
    invalid = [item for item in items if item not in ENDPOINT_MAP]
    if invalid:
        raise SystemExit(f"Invalid endpoint(s): {invalid}; choices={sorted(ENDPOINT_MAP)}")
    return items


def cache_path(fixture_id: int, endpoint: str) -> Path:
    return CACHE_ROOT / str(fixture_id) / f"{endpoint}.json"


def legacy_path(fixture_id: int, endpoint: str) -> Path | None:
    filename = f"{LEGACY_PREFIX[endpoint]}_{fixture_id}.json"
    for root in LEGACY_CACHE_ROOTS:
        path = root / filename
        if path.exists() and valid_json(path):
            return path
    return None


def valid_json(path: Path) -> bool:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return isinstance(payload, dict)


def response_items(payload: dict[str, Any]) -> list[Any]:
    value = payload.get("response", [])
    return value if isinstance(value, list) else []


def load_matches(args: argparse.Namespace) -> list[dict[str, Any]]:
    matches = load_json(MATCHES_PATH)
    rows = []
    for match in matches:
        if args.competition and str(match.get("competition")) != args.competition:
            continue
        if args.season and str(match.get("season")) != str(args.season):
            continue
        if args.fixture_id and int(match.get("api_football_fixture_id")) != int(args.fixture_id):
            continue
        rows.append(match)
    return sorted(rows, key=lambda item: (item["kickoff_at"], item["api_football_fixture_id"]))


def work_units(matches: list[dict[str, Any]], endpoints: list[str]) -> list[dict[str, Any]]:
    rows = []
    for match in matches:
        fixture_id = int(match["api_football_fixture_id"])
        for endpoint in endpoints:
            rows.append(
                {
                    "work_id": f"{fixture_id}:{endpoint}",
                    "fixture_id": fixture_id,
                    "endpoint": endpoint,
                    "status": "pending",
                    "cache_path": rel(cache_path(fixture_id, endpoint)),
                    "attempts": 0,
                    "last_error": None,
                    "http_status": None,
                    "last_response_at": None,
                    "duration_seconds": None,
                    "response_count": None,
                    "rate_limit_headers": {},
                }
            )
    return rows


def new_manifest(args: argparse.Namespace, matches: list[dict[str, Any]], endpoints: list[str]) -> dict[str, Any]:
    return {
        "version": VERSION,
        "created_at": utc_now(),
        "last_run_at": None,
        "resume_enabled": bool(args.resume),
        "dry_run": bool(args.dry_run),
        "total_historical_matches": len(load_json(MATCHES_PATH)),
        "selected_historical_matches": len(matches),
        "endpoints": endpoints,
        "planned_calls_total": len(matches) * len(endpoints),
        "completed_units": 0,
        "cached_units": 0,
        "fetched_units": 0,
        "empty_units": 0,
        "failed_units": 0,
        "skipped_units": 0,
        "rate_limited_units": 0,
        "remaining_units": len(matches) * len(endpoints),
        "live_calls_this_run": 0,
        "max_live_calls_this_run": args.max_live_calls,
        "rate_limit": {
            "strategy": "single_worker_sleep_backoff_retry_after",
            "concurrency": 1,
            "sleep_seconds": args.sleep_seconds,
            "respect_retry_after": bool(args.respect_retry_after),
            "circuit_breaker_open": False,
            "last_rate_limit_event": None,
            "consecutive_rate_limit_or_server_errors": 0,
        },
        "rate_limit_headers_detected": {
            "retry_after": False,
            "x_ratelimit_limit": False,
            "x_ratelimit_remaining": False,
        },
        "filters": {
            "competition": args.competition,
            "season": args.season,
            "fixture_id": args.fixture_id,
        },
        "fixtures": work_units(matches, endpoints),
        "last_stop_reason": None,
        "recommended_continue_command": None,
    }


def load_or_create_manifest(args: argparse.Namespace, matches: list[dict[str, Any]], endpoints: list[str]) -> dict[str, Any]:
    if args.resume and MANIFEST_PATH.exists():
        manifest = load_json(MANIFEST_PATH)
        existing = {(unit["fixture_id"], unit["endpoint"]) for unit in manifest.get("fixtures", [])}
        wanted = {(int(match["api_football_fixture_id"]), endpoint) for match in matches for endpoint in endpoints}
        if existing == wanted:
            manifest["dry_run"] = bool(args.dry_run)
            manifest["resume_enabled"] = True
            manifest["max_live_calls_this_run"] = args.max_live_calls
            manifest["live_calls_this_run"] = 0
            manifest["rate_limit"]["sleep_seconds"] = args.sleep_seconds
            manifest["rate_limit"]["respect_retry_after"] = bool(args.respect_retry_after)
            manifest["rate_limit"]["circuit_breaker_open"] = False
            manifest["rate_limit"]["consecutive_rate_limit_or_server_errors"] = 0
            return manifest
    return new_manifest(args, matches, endpoints)


def save_manifest(manifest: dict[str, Any]) -> None:
    summarize(manifest)
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(MANIFEST_PATH, SNAPSHOT_PATH)


def summarize(manifest: dict[str, Any]) -> None:
    counts = {status: 0 for status in STATUSES}
    for unit in manifest.get("fixtures", []):
        counts[unit.get("status", "pending")] = counts.get(unit.get("status", "pending"), 0) + 1
    completed = sum(counts[status] for status in ("cached", "fetched", "empty", "failed", "skipped", "rate_limited"))
    manifest.update(
        {
            "completed_units": completed,
            "cached_units": counts["cached"],
            "fetched_units": counts["fetched"],
            "empty_units": counts["empty"],
            "failed_units": counts["failed"],
            "skipped_units": counts["skipped"],
            "rate_limited_units": counts["rate_limited"],
            "remaining_units": counts["pending"],
            "last_run_at": utc_now(),
        }
    )
    manifest["recommended_continue_command"] = (
        "python3 backend/scripts/collect_api_football_historical_stats_full_v2_29.py "
        "--use-cache --resume --max-live-calls 1000 --sleep-seconds 1.5 "
        f"--endpoints {','.join(manifest['endpoints'])}"
    )


def copy_legacy_cache(unit: dict[str, Any]) -> bool:
    path = legacy_path(int(unit["fixture_id"]), str(unit["endpoint"]))
    if not path:
        return False
    target = cache_path(int(unit["fixture_id"]), str(unit["endpoint"]))
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, target)
    return True


def mark_from_cache(unit: dict[str, Any]) -> bool:
    path = cache_path(int(unit["fixture_id"]), str(unit["endpoint"]))
    if not path.exists() and not copy_legacy_cache(unit):
        return False
    if not valid_json(path):
        unit["status"] = "failed"
        unit["last_error"] = "cache_file_invalid_json"
        return True
    payload = json.loads(path.read_text(encoding="utf-8"))
    unit["status"] = "cached"
    unit["response_count"] = len(response_items(payload))
    unit["last_error"] = None
    print(f"[cache-hit] fixture={unit['fixture_id']} endpoint={unit['endpoint']}")
    return True


def retry_wait(attempt: int, retry_after: str | None, respect_retry_after: bool) -> float:
    if respect_retry_after and retry_after:
        try:
            return max(0.0, float(retry_after))
        except ValueError:
            pass
    return (2 ** attempt) + random.uniform(0.0, 0.75)


def fetch_unit(unit: dict[str, Any], args: argparse.Namespace, manifest: dict[str, Any]) -> str:
    if not API_FOOTBALL_KEY:
        unit["status"] = "failed"
        unit["last_error"] = "API_FOOTBALL_KEY is not configured"
        return "failed"
    endpoint = str(unit["endpoint"])
    fixture_id = int(unit["fixture_id"])
    clean_endpoint = ENDPOINT_MAP[endpoint]
    url = f"{API_FOOTBALL_BASE_URL}/{clean_endpoint}"
    headers = {"x-apisports-key": API_FOOTBALL_KEY}
    params = {"fixture": fixture_id}
    for attempt in range(1, args.max_retries + 1):
        unit["attempts"] = int(unit.get("attempts") or 0) + 1
        start = time.monotonic()
        try:
            response = requests.get(url, headers=headers, params=params, timeout=args.timeout_seconds)
            duration = round(time.monotonic() - start, 3)
            unit["duration_seconds"] = duration
            unit["http_status"] = response.status_code
            unit["last_response_at"] = utc_now()
            retry_after = response.headers.get("Retry-After")
            rate_headers = {
                "retry_after": retry_after,
                "x_ratelimit_limit": response.headers.get("x-ratelimit-limit") or response.headers.get("X-RateLimit-Limit"),
                "x_ratelimit_remaining": response.headers.get("x-ratelimit-remaining") or response.headers.get("X-RateLimit-Remaining"),
            }
            unit["rate_limit_headers"] = {key: value for key, value in rate_headers.items() if value is not None}
            for key, value in rate_headers.items():
                if value is not None:
                    manifest["rate_limit_headers_detected"][key] = True
            if response.status_code == 429:
                manifest["rate_limit"]["last_rate_limit_event"] = {"fixture_id": fixture_id, "endpoint": endpoint, "at": utc_now(), "retry_after": retry_after}
                print(f"[retry] status=429 retry_after={retry_after}")
                if args.stop_on_rate_limit:
                    unit["status"] = "rate_limited"
                    unit["last_error"] = "HTTP 429 rate limit"
                    return "rate_limited"
                wait = retry_wait(attempt, retry_after, args.respect_retry_after)
                print(f"[backoff] attempt={attempt} wait={wait:.2f}")
                time.sleep(wait)
                continue
            if 500 <= response.status_code < 600:
                print(f"[retry] status={response.status_code} retry_after={retry_after}")
                wait = retry_wait(attempt, retry_after, args.respect_retry_after)
                print(f"[backoff] attempt={attempt} wait={wait:.2f}")
                time.sleep(wait)
                continue
            if 400 <= response.status_code < 500:
                unit["status"] = "failed"
                unit["last_error"] = f"non_recoverable_http_{response.status_code}"
                return "failed"
            payload = response.json()
            if not isinstance(payload, dict):
                unit["status"] = "failed"
                unit["last_error"] = "unexpected_non_dict_payload"
                return "failed"
            target = cache_path(fixture_id, endpoint)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            count = len(response_items(payload))
            unit["response_count"] = count
            unit["last_error"] = None
            unit["status"] = "fetched" if count else "empty"
            print(f"[{'empty' if count == 0 else 'fetch'}] fixture={fixture_id} endpoint={endpoint} live_call={manifest['live_calls_this_run']}/{args.max_live_calls}")
            return str(unit["status"])
        except (requests.Timeout, requests.ConnectionError) as exc:
            unit["last_error"] = type(exc).__name__
            wait = retry_wait(attempt, None, args.respect_retry_after)
            print(f"[backoff] attempt={attempt} wait={wait:.2f}")
            time.sleep(wait)
        except (requests.RequestException, json.JSONDecodeError) as exc:
            unit["last_error"] = str(exc)
            wait = retry_wait(attempt, None, args.respect_retry_after)
            print(f"[backoff] attempt={attempt} wait={wait:.2f}")
            time.sleep(wait)
    unit["status"] = "failed"
    unit["last_error"] = unit.get("last_error") or "retries_exhausted"
    return "failed"


def print_summary(manifest: dict[str, Any]) -> None:
    summarize(manifest)
    print(
        "[summary] "
        f"cached={manifest['cached_units']} fetched={manifest['fetched_units']} empty={manifest['empty_units']} "
        f"failed={manifest['failed_units']} rate_limited={manifest['rate_limited_units']} "
        f"remaining={manifest['remaining_units']} live_calls={manifest['live_calls_this_run']}/{manifest['max_live_calls_this_run']}"
    )
    print(f"[continue] {manifest['recommended_continue_command']}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--use-cache", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--max-live-calls", type=int, default=1000)
    parser.add_argument("--endpoints", default="statistics,events,lineups,players")
    parser.add_argument("--competition")
    parser.add_argument("--season")
    parser.add_argument("--fixture-id", type=int)
    parser.add_argument("--sleep-seconds", type=float, default=1.5)
    parser.add_argument("--max-retries", type=int, default=5)
    parser.add_argument("--timeout-seconds", type=float, default=30)
    parser.add_argument("--save-every", type=int, default=1)
    parser.add_argument("--stop-on-rate-limit", action="store_true", default=True)
    parser.add_argument("--respect-retry-after", action="store_true", default=True)
    args = parser.parse_args()
    endpoints = endpoint_list(args.endpoints)
    matches = load_matches(args)
    manifest = load_or_create_manifest(args, matches, endpoints)
    print(f"[plan] fixtures={len(matches)} endpoints={endpoints} units={len(matches) * len(endpoints)} max_live_calls={args.max_live_calls} dry_run={args.dry_run}")
    consecutive_errors = 0
    touched = 0
    for unit in manifest["fixtures"]:
        if unit["endpoint"] not in endpoints:
            unit["status"] = "skipped"
            continue
        if unit["status"] in {"cached", "fetched", "empty", "failed", "skipped"} and args.resume:
            continue
        if args.use_cache and mark_from_cache(unit):
            touched += 1
            if touched % max(1, args.save_every) == 0:
                save_manifest(manifest)
            continue
        if args.dry_run:
            continue
        if manifest["live_calls_this_run"] >= args.max_live_calls:
            manifest["last_stop_reason"] = "max_live_calls reached"
            print("[stop] max_live_calls reached")
            break
        manifest["live_calls_this_run"] += 1
        print(f"[fetch] fixture={unit['fixture_id']} endpoint={unit['endpoint']} live_call={manifest['live_calls_this_run']}/{args.max_live_calls}")
        status = fetch_unit(unit, args, manifest)
        touched += 1
        if status in {"rate_limited", "failed"} and (unit.get("http_status") == 429 or (unit.get("http_status") and int(unit["http_status"]) >= 500)):
            consecutive_errors += 1
        else:
            consecutive_errors = 0
        manifest["rate_limit"]["consecutive_rate_limit_or_server_errors"] = consecutive_errors
        if touched % max(1, args.save_every) == 0:
            save_manifest(manifest)
        if status == "rate_limited":
            manifest["last_stop_reason"] = "rate_limit reached"
            save_manifest(manifest)
            break
        if consecutive_errors >= 5:
            manifest["rate_limit"]["circuit_breaker_open"] = True
            manifest["last_stop_reason"] = "circuit_breaker open"
            print("[stop] circuit_breaker open")
            save_manifest(manifest)
            break
        time.sleep(max(0.0, args.sleep_seconds))
    save_manifest(manifest)
    print_summary(manifest)


if __name__ == "__main__":
    main()
