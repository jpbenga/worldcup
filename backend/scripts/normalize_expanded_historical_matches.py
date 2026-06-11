"""Normalize the expanded senior-international raw dataset without altering V0.7."""

from __future__ import annotations

import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from historical_data_utils import EXPANDED_COMPETITIONS, RAW_DIR, load_json, publish, response_items
from normalize_historical_matches import normalize
from pipeline_utils import DATA_DIR, write_json

EXPANDED_RAW = RAW_DIR / "expanded"
CONFIG_BY_LEAGUE = {config["league_id"]: config for config in EXPANDED_COMPETITIONS.values()}


def expanded_match(item: dict[str, Any], mixed_scope_possible: bool) -> dict[str, Any] | None:
    match = normalize(item)
    league_id = item.get("league", {}).get("id")
    config = CONFIG_BY_LEAGUE.get(league_id)
    if match is None or config is None:
        return None
    round_name = str(match.get("round") or "").lower()
    explicit_qualification = "qualif" in round_name or "preliminary" in round_name
    family = "continental_qualification" if explicit_qualification else config["family"]
    tier = "qualification" if explicit_qualification else config["tier"]
    source_scope = "mixed_scope_possible" if mixed_scope_possible and not explicit_qualification else "clear"
    match.update(
        {
            "competition_family": family,
            "competition_tier": tier,
            "training_weight_hint": config["weight"],
            "source_name": "api_football_historical_expanded",
            "source_scope": source_scope,
            "source_classification_confidence": "low" if source_scope == "mixed_scope_possible" else "high",
        }
    )
    return match


def main() -> None:
    by_id = {}
    rejected = 0
    files = sorted(EXPANDED_RAW.glob("fixtures_*.json"))
    for path in files:
        items = response_items(load_json(path))
        mixed_scope_possible = len(items) > 100
        for item in items:
            match = expanded_match(item, mixed_scope_possible)
            if match is None:
                rejected += 1
                continue
            by_id[match["api_football_fixture_id"]] = match
    matches = sorted(by_id.values(), key=lambda item: (item["kickoff_at"], item["api_football_fixture_id"]))
    write_json(matches, DATA_DIR / "normalized" / "historical_matches_expanded.json")

    competitions: defaultdict[str, dict[str, Any]] = defaultdict(lambda: {"seasons": set(), "matches": 0})
    teams = set()
    for match in matches:
        competitions[match["competition"]]["seasons"].add(match["season"])
        competitions[match["competition"]]["matches"] += 1
        teams.update((match["home_team_id"], match["away_team_id"]))
    summary = {
        "total_matches": len(matches),
        "source_files": [path.relative_to(PROJECT_ROOT).as_posix() for path in files],
        "rejected_future_club_or_incomplete_fixtures": rejected,
        "competitions": {
            name: {"seasons": sorted(values["seasons"]), "matches": values["matches"]}
            for name, values in sorted(competitions.items())
        },
        "competition_families": dict(Counter(match["competition_family"] for match in matches)),
        "training_weight_hints": dict(Counter(match["training_weight_hint"] for match in matches)),
        "source_scopes": dict(Counter(match["source_scope"] for match in matches)),
        "teams_count": len({team for team in teams if team is not None}),
        "date_min": matches[0]["kickoff_at"] if matches else None,
        "date_max": matches[-1]["kickoff_at"] if matches else None,
        "future_2026_fixtures_excluded": all(match["season"] != 2026 for match in matches),
        "club_competitions_excluded": all(match["competition_id"] in CONFIG_BY_LEAGUE for match in matches),
        "usable_for_calibration_experiment": len(matches) > 192 and len(competitions) >= 2,
        "limitations": [
            "Competition families and friendlies may have materially different score distributions.",
            "Some API-Football league/season responses mix final-tournament and qualification scope; uncertain rows are tagged.",
            "AET/PEN score semantics must be resolved before fitting.",
            "Pre-match Elo history and neutral-site validation are not included.",
        ],
    }
    publish("historical_matches_expanded_summary.json", summary)
    print(f"Normalized {len(matches)} expanded historical matches from {len(files)} files; rejected={rejected}.")


if __name__ == "__main__":
    main()
