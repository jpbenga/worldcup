"""Select one deterministic reference bookmaker for the match odds UI."""

from __future__ import annotations

import shutil
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, utc_now, write_json

USEFUL = {"Match Winner", "Double Chance", "Home/Away", "Draw No Bet", "Goals Over/Under", "Both Teams Score", "Both Teams To Score"}


def publish(name: str, payload: dict) -> None:
    target = DATA_DIR / "generated" / name
    write_json(payload, target)
    shutil.copy2(target, DATA_DIR / "snapshots" / name)
    shutil.copy2(target, FRONTEND_DATA_DIR / name)


def main() -> None:
    odds = load_json(DATA_DIR / "generated/api_football_odds_snapshot_v2_23.json")
    coverage: dict[tuple[int, str], dict] = defaultdict(lambda: {"matches": set(), "markets": set(), "fresh_updates": 0})
    for fixture in odds.get("fixtures", []):
        for bookmaker in fixture["bookmakers"]:
            key = (bookmaker["bookmaker_id"], bookmaker["name"])
            useful = {market["name"] for market in bookmaker["markets"] if market["name"] in USEFUL}
            if useful:
                coverage[key]["matches"].add(fixture["fixture_id"])
                coverage[key]["markets"].update(useful)
                coverage[key]["fresh_updates"] += bool(fixture.get("odds_updated_at"))
    ranked = sorted(
        coverage.items(),
        key=lambda row: (-len(row[1]["matches"]), -len(row[1]["markets"]), -row[1]["fresh_updates"], row[0][1].lower()),
    )
    selected = None
    if ranked:
        (bookmaker_id, name), stats = ranked[0]
        selected = {
            "id": bookmaker_id, "name": name, "coverage_matches": len(stats["matches"]),
            "coverage_markets": sorted(stats["markets"]),
            "selection_reason": "Plus grande couverture de matchs, puis de marchés utiles, avec un nom API-Football stable.",
        }
    payload = {
        "version": "v2.23.1", "generated_at": utc_now(), "selected_bookmaker": selected,
        "fallbacks": [{"id": key[0], "name": key[1], "coverage_matches": len(stats["matches"])} for key, stats in ranked[1:4]],
        "warnings": [] if selected else ["Aucun bookmaker ne couvre les marchés utiles disponibles."],
    }
    publish("reference_bookmaker_v2_23_1.json", payload)
    print(f"V2.23.1 reference bookmaker: {selected['name'] if selected else 'unavailable'}")


if __name__ == "__main__":
    main()
