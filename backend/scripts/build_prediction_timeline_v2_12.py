"""Build chronological performance summaries from the V2.12 history."""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, load_json, utc_now
from backend.scripts.v2_12_transparency_utils import ENGINE, VERSION, dnb_metric, hit_metric, publish


def summarize(rows: list[dict], date: str, matchday: str) -> dict:
    evaluations = [row["evaluation"] for row in rows]
    exact = sum(row["exact_score_hit"] for row in evaluations)
    top3 = sum(row["top_3_hit"] for row in evaluations)
    top5 = sum(row["top_5_hit"] for row in evaluations)
    one_x_two = sum(row["one_x_two_hit"] for row in evaluations)
    return {
        "date": date,
        "matchday": matchday,
        "groups": sorted({row["group"] for row in rows}),
        "matches_played": len(rows),
        "exact_hits": exact,
        "top_3_hits": top3,
        "top_5_hits": top5,
        "one_x_two_hits": one_x_two,
        "dnb_summary": dnb_metric([row["dnb_outcome"] for row in evaluations]),
        "market_summary": {
            "btts": hit_metric([row["btts_hit"] for row in evaluations]),
            "team_goals": hit_metric([value for row in evaluations for value in row["team_goals_hits"].values()]),
        },
        "headline": f"{one_x_two}/{len(rows)} tendances 1X2 et {top5}/{len(rows)} scores dans le Top-5.",
    }


def main() -> None:
    history = load_json(DATA_DIR / "generated" / "prediction_history_v2_12.json")
    evaluated = [row for row in history["matches"] if row["evaluation"]["available"]]
    dates: dict[str, list[dict]] = defaultdict(list)
    matchdays: dict[str, list[dict]] = defaultdict(list)
    groups: dict[str, list[dict]] = defaultdict(list)
    for row in evaluated:
        dates[row["kickoff_at"][:10]].append(row)
        matchdays[row["matchday"]].append(row)
        groups[row["group"]].append(row)
    payload = {
        "version": VERSION,
        "engine_version": ENGINE,
        "generated_at": utc_now(),
        "evaluated_matches": len(evaluated),
        "by_date": [summarize(rows, date, rows[0]["matchday"]) for date, rows in sorted(dates.items())],
        "by_matchday": [summarize(rows, rows[0]["kickoff_at"][:10], matchday) for matchday, rows in sorted(matchdays.items())],
        "by_group": [summarize(rows, rows[0]["kickoff_at"][:10], group) for group, rows in sorted(groups.items())],
        "chronological_matches": [{
            "kickoff_at": row["kickoff_at"],
            "matchday": row["matchday"],
            "group": row["group"],
            "match": f"{row['home_team']} {row['actual_result']['home_goals']}-{row['actual_result']['away_goals']} {row['away_team']}",
            "headline": row["public_summary"]["headline"],
            "evaluation": row["evaluation"],
        } for row in evaluated],
    }
    publish(payload, "prediction_performance_timeline_v2_12.json")
    (ROOT / "docs" / "PREDICTION_PERFORMANCE_TIMELINE_V2_12.md").write_text(f"""# Prediction Performance Timeline V2.12

The timeline organizes `{len(evaluated)}` evaluated predictions into `{len(payload['by_date'])}` dates, `{len(payload['by_matchday'])}` matchdays and `{len(payload['by_group'])}` groups. Every entry derives from the append-only V2.12 prediction history and preserves chronological order.

Date and matchday summaries report exact, Top-3, Top-5 and 1X2 hits alongside Draw No Bet outcomes and concise market summaries. The UI can therefore show good and difficult days without presenting a dense spreadsheet or hiding individual misses.

The current evidence is still a small sample. Timeline movement is descriptive and should not be interpreted as proof of sustained improvement or decline. Pre-match predictions remain frozen while actual outcomes and evaluation labels are appended after full time.
""", encoding="utf-8")
    print(f"V2.12 timeline built: {len(payload['by_date'])} dates, {len(evaluated)} matches")


if __name__ == "__main__":
    main()
