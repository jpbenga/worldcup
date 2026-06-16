"""Discover the historical competition/season scope used by SimuMondial."""

from __future__ import annotations

import shutil
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, write_json

OUTPUT = "historical_competition_coverage_v2_27_1.json"
PRIMARY = DATA_DIR / "normalized" / "historical_matches_refreshed_v2_1.json"
RELATED = [
    DATA_DIR / "normalized" / "historical_matches.json",
    DATA_DIR / "normalized" / "historical_matches_expanded.json",
    PRIMARY,
]


def publish(payload: dict[str, Any]) -> None:
    target = DATA_DIR / "generated" / OUTPUT
    write_json(payload, target)
    shutil.copy2(target, DATA_DIR / "snapshots" / OUTPUT)
    shutil.copy2(target, FRONTEND_DATA_DIR / OUTPUT)


def main() -> None:
    matches: list[dict[str, Any]] = load_json(PRIMARY)
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for match in matches:
        grouped[(str(match.get("competition")), str(match.get("season")))].append(match)
    rows = []
    for (competition, season), items in sorted(grouped.items()):
        dates = sorted(str(item.get("kickoff_at") or "") for item in items)
        fixture_ids = [item.get("api_football_fixture_id") for item in items]
        league_ids = sorted({item.get("competition_id") for item in items if isinstance(item.get("competition_id"), int)})
        rows.append(
            {
                "competition": competition,
                "season_or_year": season,
                "matches_count": len(items),
                "date_range": {"min": dates[0], "max": dates[-1]},
                "teams_count": len({str(item.get("home_team")) for item in items} | {str(item.get("away_team")) for item in items}),
                "api_football_mapping_available": all(isinstance(value, int) for value in fixture_ids),
                "mapped_fixture_ids": sum(isinstance(value, int) for value in fixture_ids),
                "candidate_api_football_league_id": league_ids[0] if len(league_ids) == 1 else None,
                "sample_strategy": "Eligible for up to five fixtures; global quota fallback may stratify five fixtures per competition.",
            }
        )
    dates = sorted(str(item.get("kickoff_at") or "") for item in matches)
    competitions = sorted({str(item.get("competition")) for item in matches})
    warnings = []
    if not all(row["api_football_mapping_available"] for row in rows):
        warnings.append("Some local historical matches lack an API-Football fixture identifier.")
    payload = {
        "version": "v2.27.1",
        "local_historical_dataset": {
            "primary_file": PRIMARY.relative_to(ROOT).as_posix(),
            "files_scanned": [path.relative_to(ROOT).as_posix() for path in RELATED if path.exists()],
            "matches_count": len(matches),
            "competitions": competitions,
            "competitions_count": len(competitions),
            "competition_seasons_count": len(rows),
            "years": sorted({str(item.get("season")) for item in matches}),
            "date_range": {"min": dates[0], "max": dates[-1]},
            "teams_count": len({str(item.get("home_team")) for item in matches} | {str(item.get("away_team")) for item in matches}),
            "matches_with_api_football_fixture_id": sum(isinstance(item.get("api_football_fixture_id"), int) for item in matches),
        },
        "competition_seasons": rows,
        "warnings": warnings,
    }
    publish(payload)
    print(f"V2.27.1 historical discovery: competitions={len(competitions)}, competition_seasons={len(rows)}, matches={len(matches)}")


if __name__ == "__main__":
    main()
