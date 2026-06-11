"""Audit the expanded international historical dataset without fitting a model."""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from historical_data_utils import publish
from pipeline_utils import DATA_DIR, load_json, utc_now, write_json


def render(audit: dict[str, Any]) -> str:
    return f"""# Expanded Historical Dataset Audit

## Result

- Total matches: `{audit['total_matches']}`
- Teams: `{audit['teams_count']}`
- Competitions: `{audit['competition_count']}`
- Date range: `{audit['date_min']}` to `{audit['date_max']}`
- Average goals: `{audit['average_goals_per_match']}`
- Home win: `{audit['home_win_rate']:.1%}`
- Draw: `{audit['draw_rate']:.1%}`
- Away win: `{audit['away_win_rate']:.1%}`
- Normal weight: `{audit['training_weight_hints'].get('normal', 0)}`
- Low weight: `{audit['training_weight_hints'].get('low', 0)}`
- Sufficiency: `{audit['dataset_sufficiency']}`
- Usable for experimental calibration: `{str(audit['usable_for_calibration_experiment']).lower()}`

## Matches by competition

`{audit['matches_by_competition']}`

## Limitations

{chr(10).join(f"- {item}" for item in audit['limitations'])}
"""


def main() -> None:
    matches: list[dict[str, Any]] = load_json(DATA_DIR / "normalized" / "historical_matches_expanded.json")
    total = len(matches)
    winners = Counter(match["winner"] for match in matches)
    teams = Counter(team for match in matches for team in (match["home_team"], match["away_team"]))
    competitions = Counter(match["competition"] for match in matches)
    seasons = Counter(str(match["season"]) for match in matches)
    scores = Counter(f"{match['home_score']}-{match['away_score']}" for match in matches)
    families = Counter(match["competition_family"] for match in matches)
    weights = Counter(match["training_weight_hint"] for match in matches)
    scopes = Counter(match["source_scope"] for match in matches)
    total_goals = sum(match["home_score"] + match["away_score"] for match in matches)
    limitations = [
        "Competition families have different selection processes and score distributions.",
        "Qualifications and friendlies, when included, require explicit weighting and segmented evaluation.",
        "AET/PEN score semantics, pre-match Elo and neutral-site quality remain unresolved.",
        "Rows tagged mixed_scope_possible require review before calibration.",
        "The expanded dataset is an experimental calibration input, not a final training corpus.",
    ]
    audit = {
        "generated_at": utc_now(),
        "total_matches": total,
        "teams_count": len(teams),
        "competition_count": len(competitions),
        "competitions_covered": sorted(competitions),
        "seasons_covered": sorted({match["season"] for match in matches}),
        "matches_by_competition": dict(competitions),
        "matches_by_season": dict(seasons),
        "date_min": matches[0]["kickoff_at"] if matches else None,
        "date_max": matches[-1]["kickoff_at"] if matches else None,
        "average_goals_per_match": round(total_goals / total, 3) if total else 0.0,
        "home_win_rate": winners["home"] / total if total else 0.0,
        "draw_rate": winners["draw"] / total if total else 0.0,
        "away_win_rate": winners["away"] / total if total else 0.0,
        "score_distribution": dict(scores.most_common()),
        "top_teams_by_matches": [{"team": team, "matches": count} for team, count in teams.most_common(20)],
        "competition_families": dict(families),
        "major_vs_friendlies": {
            "major_or_competitive": total - families["friendly"],
            "friendlies": families["friendly"],
        },
        "training_weight_hints": dict(weights),
        "source_scopes": dict(scopes),
        "gaps_or_limitations": limitations,
        "limitations": limitations,
        "dataset_sufficiency": "medium" if total > 192 and len(competitions) >= 2 else "low",
        "usable_for_calibration_experiment": total > 192 and len(competitions) >= 2,
    }
    write_json(audit, DATA_DIR / "generated" / "expanded_historical_dataset_audit.json")
    publish("expanded_historical_dataset_audit.json", audit)
    (PROJECT_ROOT / "docs" / "EXPANDED_HISTORICAL_DATASET_AUDIT.md").write_text(render(audit), encoding="utf-8")
    print(f"Audited {total} expanded historical matches; sufficiency={audit['dataset_sufficiency']}.")


if __name__ == "__main__":
    main()
