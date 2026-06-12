"""Discover whether an official World Cup 2026 knockout bracket exists locally."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, load_json, utc_now
from backend.scripts.v2_6_live_utils import VERSION, publish

KNOCKOUT_WORDS = ("round of 32", "round of 16", "quarter", "semi", "final")


def main() -> None:
    candidates = [
        DATA_DIR / "raw" / "api_football" / "v2_6" / "worldcup_results" / "fixtures.json",
        DATA_DIR / "raw" / "api_football" / "worldcup_2026" / "fixtures.json",
    ]
    fixtures = []
    sources = []
    for path in candidates:
        if path.exists():
            payload = load_json(path)
            fixtures.extend(payload.get("response", []))
            sources.append(str(path.relative_to(ROOT)))
    knockout = []
    for item in fixtures:
        round_name = str(item.get("league", {}).get("round", ""))
        if any(word in round_name.lower() for word in KNOCKOUT_WORDS):
            knockout.append({"fixture_id": item.get("fixture", {}).get("id"), "round": round_name})
    rounds = sorted({item["round"] for item in knockout})
    report = {
        "version": VERSION, "generated_at": utc_now(), "knockout_structure_available": False,
        "source": sources, "rounds": rounds, "mapping": {}, "discovered_knockout_fixtures": knockout,
        "limitations": [
            "Available API-Football fixture files contain only the 72 group-stage fixtures.",
            "No official mapping from qualified group positions to knockout slots is available.",
            "An official champion path cannot be simulated without inventing a bracket.",
        ],
    }
    publish(report, "worldcup_knockout_structure_v2_6.json")
    (ROOT / "docs" / "WORLDCUP_KNOCKOUT_STRUCTURE_V2_6.md").write_text(
        """# World Cup Knockout Structure V2.6

The available local and V2.6 API-Football fixture files contain only the 72
group-stage fixtures. No Round of 32, Round of 16, quarter-final, semi-final or
final fixture mapping is available.

`knockout_structure_available` is therefore `false`. V2.6 does not invent an
official bracket or claim an official champion simulation. The product uses a
clearly labelled Projected Campaign proxy instead.

The discovery inspected both the dedicated V2.6 cached result response and the
previous World Cup fixture cache. Re-running discovery is safe: it reads
fixture metadata only, makes no prediction changes and will continue to block
official-path simulation until both knockout fixtures and an authoritative
slot mapping are available.
""", encoding="utf-8")
    print("V2.6 knockout discovery: unavailable; projected campaign required")


if __name__ == "__main__":
    main()
