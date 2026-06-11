"""Confirm expanded senior international competition coverage with bounded API calls."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.data_acquisition.api_football_client import ApiFootballClient, ApiFootballError
from historical_data_utils import (
    EXPANDED_COMPETITIONS,
    EXPANDED_PRESETS,
    RAW_DIR,
    available_seasons,
    finished_items,
    publish,
    response_items,
    safe_errors,
)
from pipeline_utils import DATA_DIR, utc_now, write_json

EXPANDED_RAW = RAW_DIR / "expanded"


def checks(all_seasons: bool) -> list[tuple[str, dict[str, Any], int]]:
    result = []
    for key, config in EXPANDED_COMPETITIONS.items():
        requested = available_seasons(config["league_id"]) if all_seasons else EXPANDED_PRESETS["broad"].get(key, [])
        for season in requested:
            if season in available_seasons(config["league_id"]):
                result.append((key, config, season))
    return result


def render(summary: dict[str, Any], inventory: list[dict[str, Any]]) -> str:
    rows = "\n".join(
        f"| `{item['key']}` | {item['league_id']} | {item['name']} | {item['family']} | "
        f"{', '.join(map(str, item['available_seasons']))} | {item['finished_fixtures_found']} | "
        f"{str(item['usable_for_dataset']).lower()} |"
        for item in inventory
    )
    return f"""# Expanded Historical Competition Exploration

## Result

- Requests executed: `{summary['requests_executed']}`
- Competitions checked: `{len(summary['competitions_checked'])}`
- Usable competitions: `{len(summary['usable_competitions'])}`
- Finished fixtures found: `{summary['finished_fixtures_found']}`

| Key | League ID | API-Football name | Family | Available historical seasons | Finished found | Usable |
|---|---:|---|---|---|---:|---|
{rows}

## Limitations

{chr(10).join(f"- {item}" for item in summary['limitations'])}
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--max-requests", type=int, default=60)
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()
    planned = checks(args.all)[: args.max_requests]
    client = None if args.dry_run else ApiFootballClient(max_calls=max(1, args.max_requests))
    results = []
    failures = []
    for key, config, season in planned:
        if args.dry_run:
            results.append({"key": key, "season": season, "finished_fixtures": 0, "status": "dry_run"})
            continue
        try:
            payload = client.get("fixtures", {"league": config["league_id"], "season": season})
            results.append(
                {
                    "key": key,
                    "season": season,
                    "fixtures": len(response_items(payload)),
                    "finished_fixtures": len(finished_items(payload)),
                    "status": "api_error" if safe_errors(payload) else "checked",
                    "errors": safe_errors(payload),
                }
            )
        except (ApiFootballError, OSError, json.JSONDecodeError) as exc:
            failures.append({"key": key, "season": season, "error": str(exc)})

    inventory = []
    for key, config in EXPANDED_COMPETITIONS.items():
        selected = [item for item in results if item["key"] == key]
        finished = sum(item.get("finished_fixtures", 0) for item in selected)
        inventory.append(
            {
                "key": key,
                "league_id": config["league_id"],
                "name": config["name"],
                "type": "Cup",
                "country_or_confederation": "World",
                "family": config["family"],
                "tier": config["tier"],
                "available_seasons": available_seasons(config["league_id"]),
                "checked_seasons": [item["season"] for item in selected],
                "finished_fixtures_found": finished,
                "usable_for_dataset": bool(available_seasons(config["league_id"])) and (args.dry_run or finished > 0),
                "reason_if_unusable": None if available_seasons(config["league_id"]) else "No historical season in cached league inventory.",
                "checks": selected,
            }
        )
    usable = [item["key"] for item in inventory if item["usable_for_dataset"]]
    summary = {
        "generated_at": utc_now(),
        "scope": "expanded_international_historical_matches",
        "dry_run": args.dry_run,
        "competitions_checked": sorted({item["key"] for item in results}),
        "usable_competitions": usable,
        "unusable_competitions": [item["key"] for item in inventory if not item["usable_for_dataset"]],
        "seasons_checked": [{"competition": item["key"], "season": item["season"]} for item in results],
        "requests_planned": len(planned),
        "requests_executed": 0 if args.dry_run else client.call_count,
        "finished_fixtures_found": sum(item.get("finished_fixtures", 0) for item in results),
        "failed_requests": failures,
        "limitations": [
            "Counts describe only checked senior international league/season pairs.",
            "Competition families have different score distributions and must remain tagged.",
            "No club competition is included.",
        ],
        "quota_notes": [f"Execution capped at {args.max_requests} calls."],
    }
    write_json(inventory, DATA_DIR / "generated" / "expanded_historical_competition_inventory.json")
    write_json(summary, RAW_DIR / "expanded_exploration_summary.json")
    publish("expanded_historical_data_status.json", summary)
    (PROJECT_ROOT / "docs" / "EXPANDED_HISTORICAL_COMPETITION_EXPLORATION.md").write_text(
        render(summary, inventory), encoding="utf-8"
    )
    print(f"Expanded exploration: calls={summary['requests_executed']}, finished={summary['finished_fixtures_found']}.")


if __name__ == "__main__":
    main()
