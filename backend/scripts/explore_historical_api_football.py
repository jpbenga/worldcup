"""Explore historical international API-Football coverage with a strict call budget."""

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
    finished_items,
    publish,
    relative,
    response_items,
    safe_errors,
    selected_competitions,
)
from pipeline_utils import DATA_DIR, write_json


def planned_checks(competition: str | None, all_competitions: bool, limit: int) -> list[dict[str, Any]]:
    competitions = selected_competitions(competition, all_competitions)
    if competition or all_competitions:
        checks = [
            {"key": key, "league_id": config["league_id"], "name": config["name"], "season": season}
            for key, config in competitions
            for season in available_seasons(config["league_id"])
        ]
        return checks if all_competitions else checks[:limit]
    checks = []
    depth = 0
    while len(checks) < limit:
        added = False
        for key, config in competitions:
            seasons = available_seasons(config["league_id"])
            if depth < len(seasons):
                checks.append(
                    {"key": key, "league_id": config["league_id"], "name": config["name"], "season": seasons[depth]}
                )
                added = True
                if len(checks) == limit:
                    break
        if not added:
            break
        depth += 1
    return checks


def render_doc(summary: dict[str, Any], inventory: list[dict[str, Any]]) -> str:
    lines = [
        "# Historical API-Football Exploration",
        "",
        "## Result",
        "",
        f"- Generated at: `{summary['generated_at']}`",
        f"- Requests planned: `{summary['requests_planned']}`",
        f"- Requests executed: `{summary['requests_executed']}`",
        f"- Seasons checked: `{len(summary['seasons_checked'])}`",
        f"- Finished fixtures found in checked seasons: `{summary['total_finished_fixtures_found']}`",
        f"- Usable for training: `{str(summary['usable_for_training']).lower()}`",
        "",
        "## Competition inventory",
        "",
        "| Key | League ID | Competition | Available seasons | Checked seasons | Finished fixtures found |",
        "|---|---:|---|---|---|---:|",
    ]
    for item in inventory:
        lines.append(
            f"| `{item['key']}` | {item['league_id']} | {item['name']} | "
            f"{', '.join(map(str, item['available_seasons'])) or 'none'} | "
            f"{', '.join(map(str, item['checked_seasons'])) or 'none'} | {item['finished_fixtures_found']} |"
        )
    lines.extend(
        [
            "",
            "## Limitations",
            "",
            *[f"- {item}" for item in summary["limitations"]],
            "",
            "## Next steps",
            "",
            *[f"- {item}" for item in summary["next_steps"]],
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit-seasons", type=int, default=5)
    parser.add_argument("--competition", choices=tuple(COMPETITIONS))
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()

    checks = planned_checks(args.competition, args.all, max(1, args.limit_seasons))
    planned = len(checks)
    results = []
    errors = []
    client = None if args.dry_run else ApiFootballClient(max_calls=max(1, planned))
    for check in checks:
        if args.dry_run:
            results.append({**check, "status": "dry_run", "fixtures": 0, "finished_fixtures": 0, "errors": []})
            continue
        try:
            payload = client.get("fixtures", {"league": check["league_id"], "season": check["season"]})
            results.append(
                {
                    **check,
                    "status": "api_error" if safe_errors(payload) else "checked",
                    "fixtures": len(response_items(payload)),
                    "finished_fixtures": len(finished_items(payload)),
                    "errors": safe_errors(payload),
                }
            )
        except (ApiFootballError, OSError, json.JSONDecodeError) as exc:
            errors.append({**check, "error": str(exc)})
            results.append({**check, "status": "error", "fixtures": 0, "finished_fixtures": 0, "errors": [str(exc)]})

    inventory = []
    result_by_key: dict[str, list[dict[str, Any]]] = {}
    for result in results:
        result_by_key.setdefault(result["key"], []).append(result)
    for key, config in COMPETITIONS.items():
        checked = result_by_key.get(key, [])
        inventory.append(
            {
                "key": key,
                "league_id": config["league_id"],
                "name": config["name"],
                "available_seasons": available_seasons(config["league_id"]),
                "checked_seasons": [item["season"] for item in checked],
                "finished_fixtures_found": sum(item["finished_fixtures"] for item in checked),
                "checks": checked,
            }
        )

    total_finished = sum(item["finished_fixtures"] for item in results)
    summary = {
        **base_summary(),
        "dry_run": args.dry_run,
        "competitions_checked": sorted({item["key"] for item in results}),
        "seasons_checked": [{"competition": item["key"], "league_id": item["league_id"], "season": item["season"]} for item in results],
        "requests_planned": planned,
        "requests_executed": 0 if args.dry_run else client.call_count,
        "total_finished_fixtures_found": total_finished,
        "failed_requests": errors,
        "usable_for_training": total_finished > 0,
        "limitations": [
            "Fixture counts cover only explicitly checked league/season pairs, not every available international competition.",
            "Advanced statistics and neutral-site quality were not evaluated in this controlled spike.",
        ],
        "next_steps": [
            "Fetch the conservative World Cup 2014, 2018 and 2022 dataset.",
            "Normalize only finished fixtures with real scores and audit chronology before any training.",
        ],
    }
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    write_json(summary, RAW_DIR / "exploration_summary.json")
    write_json(inventory, DATA_DIR / "generated" / "historical_competition_inventory.json")
    publish("historical_data_status.json", summary)
    (PROJECT_ROOT / "docs" / "HISTORICAL_API_FOOTBALL_EXPLORATION.md").write_text(
        render_doc(summary, inventory), encoding="utf-8"
    )
    print(
        f"Historical exploration complete: calls={summary['requests_executed']}, "
        f"finished fixtures={total_finished}, summary={relative(RAW_DIR / 'exploration_summary.json')}"
    )


if __name__ == "__main__":
    main()
