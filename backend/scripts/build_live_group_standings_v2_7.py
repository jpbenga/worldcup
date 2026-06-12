"""Build live group standings exclusively from finished official results."""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, load_json, utc_now
from backend.scripts.v2_7_consistency_utils import VERSION, group_code, publish


def blank(team: str) -> dict[str, Any]:
    return {"team": team, "played": 0, "wins": 0, "draws": 0, "losses": 0, "goals_for": 0, "goals_against": 0, "goal_difference": 0, "points": 0, "rank": 0}


def main() -> None:
    predictions = load_json(DATA_DIR / "generated" / "worldcup_2026_predictions_release_candidate_v2_4.json")["matches"]
    results = load_json(DATA_DIR / "generated" / "worldcup_2026_results_v2_6.json")["fixtures"]
    result_map = {item["match_id"]: item for item in results}
    tables: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for match in predictions:
        group = group_code(match["group"])
        for team in (match["home_team"], match["away_team"]):
            tables[group].setdefault(team, blank(team))
    finished = 0
    for match in predictions:
        result = result_map.get(match["match_id"], {})
        score = result.get("actual_score", {})
        if result.get("status") != "finished" or score.get("home") is None or score.get("away") is None:
            continue
        finished += 1
        group = group_code(match["group"])
        home, away = tables[group][match["home_team"]], tables[group][match["away_team"]]
        hg, ag = int(score["home"]), int(score["away"])
        for row in (home, away):
            row["played"] += 1
        home["goals_for"] += hg; home["goals_against"] += ag
        away["goals_for"] += ag; away["goals_against"] += hg
        if hg > ag:
            home["wins"] += 1; home["points"] += 3; away["losses"] += 1
        elif ag > hg:
            away["wins"] += 1; away["points"] += 3; home["losses"] += 1
        else:
            home["draws"] += 1; away["draws"] += 1; home["points"] += 1; away["points"] += 1
    groups = {}
    for group, rows in sorted(tables.items()):
        for row in rows.values():
            row["goal_difference"] = row["goals_for"] - row["goals_against"]
        ordered = sorted(rows.values(), key=lambda row: (-row["points"], -row["goal_difference"], -row["goals_for"], row["team"]))
        for rank, row in enumerate(ordered, 1):
            row["rank"] = rank
        groups[group] = {"standings": ordered}
    payload = {
        "version": VERSION, "source": "official_results_layer", "generated_at": utc_now(),
        "finished_matches_count": finished, "groups": groups,
        "tiebreak_limitations": ["Ranks use points, goal difference, goals scored, then team name. Complete FIFA head-to-head and disciplinary tiebreakers are not yet applied."],
    }
    publish(payload, "worldcup_live_group_standings_v2_7.json")
    group_a = groups.get("A", {}).get("standings", [])
    (ROOT / "docs" / "WORLDCUP_LIVE_GROUP_STANDINGS_V2_7.md").write_text(
        f"""# World Cup Live Group Standings V2.7

V2.7 builds all 12 group tables exclusively from `{finished}` finished official result(s). Unplayed and live matches do not award points. Each row exposes played, wins, draws, losses, goals for, goals against, goal difference, points and rank.

Current Group A: `{group_a}`.

The current ordering uses points, goal difference, goals scored and team name as a deterministic fallback. Full FIFA head-to-head, fair-play and drawing-of-lots tiebreakers are documented as unavailable until they are necessary and supported by complete data. Pre-match predictions are not used to build standings.
""", encoding="utf-8")
    print(f"V2.7 live standings: {finished} finished result(s), {len(groups)} groups")


if __name__ == "__main__":
    main()
