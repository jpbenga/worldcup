"""Normalize mock fixtures into the application's internal match contract."""

from __future__ import annotations

import sys

from pipeline_utils import DATA_DIR, PROJECT_ROOT, load_json, write_json

sys.path.insert(0, str(PROJECT_ROOT))


def normalize_match(match: dict[str, object]) -> dict[str, object]:
    return {
        "match_id": match["match_id"],
        "competition": match["competition"],
        "stage": match["stage"],
        "group": match.get("group"),
        "home_team": match["home_team"],
        "away_team": match["away_team"],
        "kickoff_at": match["kickoff_at"],
        "status": match.get("status", "scheduled"),
        "home_score": match.get("home_score"),
        "away_score": match.get("away_score"),
        "source_type": "mock",
        "source_name": "sample_matches",
        "is_real_fixture": False,
        "model_inputs": {
            "home_elo": match["home_elo"],
            "away_elo": match["away_elo"],
            "home_recent_goals_for": match["home_recent_goals_for"],
            "home_recent_goals_against": match["home_recent_goals_against"],
            "away_recent_goals_for": match["away_recent_goals_for"],
            "away_recent_goals_against": match["away_recent_goals_against"],
        },
    }


def main() -> None:
    input_path = DATA_DIR / "mock" / "sample_matches.json"
    output_path = DATA_DIR / "normalized" / "matches.json"
    matches = load_json(input_path)
    normalized = [normalize_match(match) for match in matches]
    write_json(normalized, output_path)
    print(f"Normalized {len(normalized)} matches in {output_path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
