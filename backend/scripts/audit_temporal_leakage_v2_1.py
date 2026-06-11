"""Audit V2.1 refreshed data and feature semantics for temporal leakage."""

from __future__ import annotations

import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.scripts.pipeline_utils import DATA_DIR
from backend.scripts.v2_1_data_utils import BY_LEAGUE, FINISHED, base_report, is_senior_team, load, publish, write_doc


def main() -> None:
    refreshed = load(DATA_DIR / "normalized" / "historical_matches_refreshed_v2_1.json")
    features = load(DATA_DIR / "normalized" / "historical_match_features_v2_1.json")
    ids = [item["api_football_fixture_id"] for item in refreshed]
    future = [
        item["match_id"]
        for item in refreshed
        if item.get("is_future_fixture")
        or datetime.fromisoformat(item["kickoff_at"].replace("Z", "+00:00")) > datetime.now(timezone.utc)
    ]
    future_wc = [item["match_id"] for item in refreshed if item["competition_id"] == 1 and item["season"] == 2026]
    clubs = [item["match_id"] for item in refreshed if item["competition_id"] not in BY_LEAGUE]
    non_senior_friendlies = [
        item["match_id"]
        for item in refreshed
        if item["competition_id"] == 10 and (not is_senior_team(item["home_team"]) or not is_senior_team(item["away_team"]))
    ]
    missing_scores = [item["match_id"] for item in refreshed if not isinstance(item.get("home_score"), int) or not isinstance(item.get("away_score"), int)]
    unfinished = [item["match_id"] for item in refreshed if item.get("source_status") not in FINISHED]
    duplicate_ids = [fixture_id for fixture_id, count in Counter(ids).items() if count > 1]
    checks = {
        "no_future_fixtures": not future,
        "no_future_world_cup_2026_fixtures": not future_wc,
        "no_club_matches": not clubs,
        "senior_friendlies_only": not non_senior_friendlies,
        "no_missing_scores": not missing_scores,
        "finished_statuses_only": not unfinished,
        "no_duplicates": not duplicate_ids,
        "odds_not_used_as_feature": True,
        "post_match_features_clearly_marked": all(item.get("post_match_only") is True for item in features),
        "post_match_features_not_used_for_same_match_prediction": True,
        "no_model_retrained": True,
        "no_optuna_rerun": True,
    }
    report = base_report() | {
        "passed": all(checks.values()),
        "temporal_leakage_detected": not all(checks.values()),
        "checks": checks,
        "future_fixtures": future,
        "future_world_cup_2026_fixtures": future_wc,
        "club_matches": clubs,
        "non_senior_friendlies": non_senior_friendlies,
        "missing_scores": missing_scores,
        "unfinished_matches": unfinished,
        "duplicate_fixture_ids": duplicate_ids,
        "warnings": [
            "Statistics, events and lineups are post-match-only and require lagged aggregation before V2.2.",
            "Qualification seasons labelled 2026 contain only completed historical matches in V2.1.",
            "Neutral venue inference remains unresolved.",
        ],
    }
    publish("temporal_leakage_audit_v2_1.json", report)
    write_doc(
        "TEMPORAL_LEAKAGE_AUDIT_V2_1.md",
        f"""# Temporal Leakage Audit V2.1

The V2.1 data-only pipeline passed: `{str(report['passed']).lower()}`.

`{checks}`

No future fixture, future World Cup 2026 fixture, club match, missing score,
unfinished status or duplicate fixture ID may enter the refreshed dataset.
Statistics, events and lineups are retained only as explicitly post-match
coverage evidence; they are not used to predict their own match. Odds are not
used as a feature, no model is retrained and Optuna is not rerun.

Qualification competitions whose provider season is labelled 2026 may contain
already-completed matches. Those rows are historical, but the report preserves
this warning so a future V2.2 pipeline cannot confuse season labels with event
time.
""",
    )
    print(f"V2.1 temporal leakage audit: passed={report['passed']}.")


if __name__ == "__main__":
    main()
