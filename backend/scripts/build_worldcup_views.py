"""Build team, group, standings, and strength snapshots for the World Cup UX."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, write_json

RAW_STANDINGS = DATA_DIR / "raw" / "api_football" / "worldcup_2026" / "standings.json"


def standings_by_group() -> dict[str, list[dict[str, Any]]]:
    if not RAW_STANDINGS.exists():
        return {}
    payload = json.loads(RAW_STANDINGS.read_text(encoding="utf-8"))
    result: dict[str, list[dict[str, Any]]] = {}
    for response in payload.get("response", []):
        for table in response.get("league", {}).get("standings", []):
            for row in table:
                group = row.get("group")
                if not isinstance(group, str) or not group.startswith("Group "):
                    continue
                result.setdefault(group, []).append(
                    {
                        "rank": row.get("rank"),
                        "team_id": row.get("team", {}).get("id"),
                        "team_name": row.get("team", {}).get("name"),
                        "logo_url": row.get("team", {}).get("logo"),
                        "points": row.get("points"),
                        "played": row.get("all", {}).get("played"),
                        "won": row.get("all", {}).get("win"),
                        "drawn": row.get("all", {}).get("draw"),
                        "lost": row.get("all", {}).get("lose"),
                        "goals_for": row.get("all", {}).get("goals", {}).get("for"),
                        "goals_against": row.get("all", {}).get("goals", {}).get("against"),
                        "goal_difference": row.get("goalsDiff"),
                    }
                )
    return result


def publish(name: str, payload: Any) -> None:
    snapshot = DATA_DIR / "snapshots" / name
    frontend = FRONTEND_DATA_DIR / name
    write_json(payload, snapshot)
    FRONTEND_DATA_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(snapshot, frontend)


def main() -> None:
    teams = load_json(DATA_DIR / "normalized" / "api_football_teams.json")
    matches = load_json(DATA_DIR / "normalized" / "matches.json")
    tables = standings_by_group()
    teams_by_api_id = {team["api_football_team_id"]: team for team in teams}
    groups = []
    strengths = []

    for group in sorted(tables):
        standings = sorted(tables[group], key=lambda row: row["rank"])
        group_teams = [teams_by_api_id[row["team_id"]] for row in standings if row["team_id"] in teams_by_api_id]
        group_matches = [match for match in matches if match.get("group") == group]
        ratings = [team["elo_rating"] for team in group_teams if isinstance(team.get("elo_rating"), int)]
        strongest = max(group_teams, key=lambda team: team.get("elo_rating") or -1) if ratings else None
        weakest = min(group_teams, key=lambda team: team.get("elo_rating") or 10_000) if ratings else None
        groups.append(
            {
                "group": group.removeprefix("Group "),
                "group_label": group,
                "teams": group_teams,
                "matches": group_matches,
                "standings_available": bool(standings),
                "standings": standings,
            }
        )
        strengths.append(
            {
                "group": group.removeprefix("Group "),
                "group_label": group,
                "group_data_available": True,
                "team_count": len(group_teams),
                "match_count": len(group_matches),
                "average_elo": round(sum(ratings) / len(ratings), 2) if ratings else None,
                "max_elo": max(ratings) if ratings else None,
                "min_elo": min(ratings) if ratings else None,
                "strongest_team": strongest["name"] if strongest else None,
                "weakest_team": weakest["name"] if weakest else None,
            }
        )

    publish("teams.json", teams)
    publish("worldcup_groups.json", groups)
    publish("group_strengths.json", strengths)
    print(f"Published {len(groups)} World Cup groups and {len(teams)} enriched teams.")


if __name__ == "__main__":
    main()
