"""Audit the isolated historical match dataset without training or backtesting a model."""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from historical_data_utils import publish
from pipeline_utils import DATA_DIR, load_json, utc_now, write_json


def percent(count: int, total: int) -> float:
    return count / total if total else 0.0


def render(audit: dict[str, Any]) -> str:
    return f"""# Historical Dataset Audit

## Result

- Total matches: `{audit['total_matches']}`
- Competitions: `{audit['competition_count']}`
- Seasons: `{audit['seasons']}`
- Teams: `{audit['teams_count']}`
- Date range: `{audit['date_min']}` to `{audit['date_max']}`
- Average goals per match: `{audit['average_goals_per_match']}`
- Home win: `{audit['home_win_rate']:.1%}`
- Draw: `{audit['draw_rate']:.1%}`
- Away win: `{audit['away_win_rate']:.1%}`
- Usable for training experiments: `{str(audit['usable_for_training']).lower()}`
- Dataset sufficiency: `{audit['dataset_sufficiency']}`

## Score distribution

`{audit['score_distribution']}`

## Most represented teams

`{audit['top_teams_by_matches']}`

## Limitations

{chr(10).join(f"- {item}" for item in audit['limitations'])}

## Decision

This dataset may support a controlled baseline-calibration experiment, but it
is not sufficient by itself for a full advanced engine. No model was trained
and no backtest was performed in V0.7.
"""


def main() -> None:
    path = DATA_DIR / "normalized" / "historical_matches.json"
    matches: list[dict[str, Any]] = load_json(path) if path.exists() else []
    total = len(matches)
    score_distribution = Counter(f"{item['home_score']}-{item['away_score']}" for item in matches)
    team_counts = Counter(team for item in matches for team in (item["home_team"], item["away_team"]))
    seasons = sorted({item["season"] for item in matches})
    competitions = sorted({item["competition"] for item in matches})
    total_goals = sum(item["home_score"] + item["away_score"] for item in matches)
    home_wins = sum(item["winner"] == "home" for item in matches)
    draws = sum(item["winner"] == "draw" for item in matches)
    away_wins = sum(item["winner"] == "away" for item in matches)
    sufficiency = "medium" if total >= 150 else "low"
    limitations = [
        "The conservative spike covers World Cups only; qualifiers, continental tournaments and friendlies are absent.",
        "Three tournaments can support a baseline experiment but are insufficient for a full advanced engine.",
        "Knockout scores may include extra time; regulation-time score fields must be defined before model fitting.",
        "Neutral-site quality, pre-match Elo history and advanced statistics are not yet joined.",
    ]
    if not matches:
        limitations.insert(0, "No usable historical match was normalized.")
    audit = {
        "generated_at": utc_now(),
        "total_matches": total,
        "competition_count": len(competitions),
        "competitions": competitions,
        "seasons": seasons,
        "teams_count": len(team_counts),
        "score_distribution": dict(score_distribution.most_common()),
        "average_goals_per_match": round(total_goals / total, 3) if total else 0.0,
        "home_win_rate": percent(home_wins, total),
        "draw_rate": percent(draws, total),
        "away_win_rate": percent(away_wins, total),
        "top_teams_by_matches": [{"team": team, "matches": count} for team, count in team_counts.most_common(15)],
        "date_min": min((item["kickoff_at"] for item in matches), default=None),
        "date_max": max((item["kickoff_at"] for item in matches), default=None),
        "gaps_or_limitations": limitations,
        "limitations": limitations,
        "usable_for_training": total > 0,
        "dataset_sufficiency": sufficiency,
    }
    generated = DATA_DIR / "generated" / "historical_dataset_audit.json"
    write_json(audit, generated)
    publish("historical_dataset_audit.json", audit)
    (PROJECT_ROOT / "docs" / "HISTORICAL_DATASET_AUDIT.md").write_text(render(audit), encoding="utf-8")
    print(f"Audited {total} historical matches; sufficiency={sufficiency}.")


if __name__ == "__main__":
    main()
