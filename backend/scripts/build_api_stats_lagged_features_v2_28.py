"""Build strict chronological lagged API-Football statistics features."""

from __future__ import annotations

import json
import math
import shutil
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, write_json

OUTPUT = "api_stats_lagged_features_v2_28.json"
RAW_DIRS = [DATA_DIR / "raw" / "api_football" / "v2_27_1", DATA_DIR / "raw" / "api_football" / "v2_27"]
MATCH_FILES = [
    DATA_DIR / "normalized" / "historical_train_matches_v2_1.json",
    DATA_DIR / "normalized" / "historical_validation_matches_v2_1.json",
    DATA_DIR / "normalized" / "historical_test_matches_v2_1.json",
]
FUTURE_PREDICTIONS = DATA_DIR / "generated" / "predictions.json"
STAT_NAMES = {
    "expected_goals": "xg",
    "Total Shots": "shots",
    "Shots on Goal": "shots_on_goal",
    "Ball Possession": "possession",
    "Corner Kicks": "corners",
    "Passes accurate": "passes_accurate",
}
WINDOWS = (3, 5, 10)


def publish(payload: dict[str, Any]) -> None:
    target = DATA_DIR / "generated" / OUTPUT
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    shutil.copy2(target, DATA_DIR / "snapshots" / OUTPUT)
    shutil.copy2(target, FRONTEND_DATA_DIR / OUTPUT)


def parse_date(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def number(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace("%", "")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def raw_payload(prefix: str, fixture_id: int) -> dict[str, Any] | None:
    for directory in RAW_DIRS:
        path = directory / f"{prefix}_{fixture_id}.json"
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    return None


def response(payload: dict[str, Any] | None) -> list[Any]:
    if not payload:
        return []
    value = payload.get("response", [])
    return value if isinstance(value, list) else []


def stats_by_team(fixture_id: int) -> dict[str, dict[str, float]]:
    rows = response(raw_payload("fixtures_statistics", fixture_id))
    result: dict[str, dict[str, float]] = {}
    for row in rows:
        team = row.get("team", {}) if isinstance(row, dict) else {}
        name = team.get("name")
        if not name:
            continue
        values = {}
        for stat in row.get("statistics", []):
            key = STAT_NAMES.get(stat.get("type"))
            value = number(stat.get("value"))
            if key and value is not None:
                values[key] = value
        result[str(name)] = values
    return result


def source_record(match: dict[str, Any]) -> dict[str, Any] | None:
    fixture_id = int(match["api_football_fixture_id"])
    stats = stats_by_team(fixture_id)
    home, away = str(match["home_team"]), str(match["away_team"])
    home_stats, away_stats = stats.get(home), stats.get(away)
    if not home_stats or not away_stats:
        return None
    def row(team: str, opponent: str, values: dict[str, float], opp_values: dict[str, float], goals_for: int, goals_against: int) -> dict[str, Any]:
        return {
            "fixture_id": fixture_id, "match_id": match["match_id"], "date": match["kickoff_at"],
            "team": team, "opponent": opponent, "goals_for": goals_for, "goals_against": goals_against,
            "xg_for": values.get("xg"), "xg_against": opp_values.get("xg"),
            "shots_for": values.get("shots"), "shots_against": opp_values.get("shots"),
            "shots_on_goal_for": values.get("shots_on_goal"), "shots_on_goal_against": opp_values.get("shots_on_goal"),
            "possession": values.get("possession"), "corners_for": values.get("corners"),
            "corners_against": opp_values.get("corners"), "passes_accurate": values.get("passes_accurate"),
            "stats_quality": int(bool(values.get("shots") is not None and values.get("possession") is not None)),
            "xg_available": int(values.get("xg") is not None and opp_values.get("xg") is not None),
        }
    return {
        home: row(home, away, home_stats, away_stats, int(match["home_score"]), int(match["away_score"])),
        away: row(away, home, away_stats, home_stats, int(match["away_score"]), int(match["home_score"])),
    }


def avg(values: list[float | None]) -> float | None:
    valid = [value for value in values if value is not None]
    return round(sum(valid) / len(valid), 6) if valid else None


def team_features(history: list[dict[str, Any]], target_date: str, window: int) -> dict[str, Any]:
    rows = history[-window:]
    xg_rows = [row for row in rows if row["xg_available"]]
    stat_rows = [row for row in rows if row["stats_quality"]]
    latest = rows[-1] if rows else None
    target = parse_date(target_date)
    age = (target - parse_date(latest["date"])).days if latest else None
    out = {
        f"matches_last{window}": len(rows),
        f"stats_matches_last{window}": len(stat_rows),
        f"xg_matches_last{window}": len(xg_rows),
        f"xg_missing_last{window}": int(len(xg_rows) == 0),
        f"stats_missing_last{window}": int(len(stat_rows) == 0),
        f"recency_age_days_last{window}": age,
        f"goals_for_avg_last{window}": avg([row["goals_for"] for row in rows]),
        f"goals_against_avg_last{window}": avg([row["goals_against"] for row in rows]),
        f"xg_for_avg_last{window}": avg([row["xg_for"] for row in xg_rows]),
        f"xg_against_avg_last{window}": avg([row["xg_against"] for row in xg_rows]),
        f"shots_for_avg_last{window}": avg([row["shots_for"] for row in stat_rows]),
        f"shots_against_avg_last{window}": avg([row["shots_against"] for row in stat_rows]),
        f"shots_on_goal_for_avg_last{window}": avg([row["shots_on_goal_for"] for row in stat_rows]),
        f"possession_avg_last{window}": avg([row["possession"] for row in stat_rows]),
        f"corners_for_avg_last{window}": avg([row["corners_for"] for row in stat_rows]),
        f"passes_accurate_avg_last{window}": avg([row["passes_accurate"] for row in stat_rows]),
        f"clean_sheet_rate_last{window}": avg([float(row["goals_against"] == 0) for row in rows]),
        f"large_win_rate_last{window}": avg([float(row["goals_for"] - row["goals_against"] >= 3) for row in rows]),
    }
    if out[f"xg_for_avg_last{window}"] is not None and out[f"xg_against_avg_last{window}"] is not None:
        out[f"xg_diff_avg_last{window}"] = round(out[f"xg_for_avg_last{window}"] - out[f"xg_against_avg_last{window}"], 6)
    else:
        out[f"xg_diff_avg_last{window}"] = None
    shots, sog = out[f"shots_for_avg_last{window}"], out[f"shots_on_goal_for_avg_last{window}"]
    out[f"shot_on_target_ratio_last{window}"] = round(sog / shots, 6) if shots and sog is not None else None
    xg_for, goals_for = out[f"xg_for_avg_last{window}"], out[f"goals_for_avg_last{window}"]
    out[f"goals_minus_xg_avg_last{window}"] = round(goals_for - xg_for, 6) if xg_for is not None and goals_for is not None else None
    return {key: value for key, value in out.items() if value is not None}


def build_match_feature(match: dict[str, Any], histories: dict[str, list[dict[str, Any]]], future: bool = False) -> dict[str, Any]:
    home, away, date = str(match["home_team"]), str(match["away_team"]), str(match["kickoff_at"])
    home_features, away_features = {}, {}
    for window in WINDOWS:
        home_features |= team_features(histories[home], date, window)
        away_features |= team_features(histories[away], date, window)
    diff = {}
    for key, value in home_features.items():
        if not isinstance(value, (int, float)) or key.endswith("_missing_last3") or key.endswith("_missing_last5") or key.endswith("_missing_last10"):
            continue
        other = away_features.get(key)
        if isinstance(other, (int, float)) and not (math.isnan(value) or math.isnan(other)):
            diff[f"home_minus_away_{key}"] = round(value - other, 6)
    coverage = {
        "home_stats_matches_last5": home_features["stats_matches_last5"],
        "away_stats_matches_last5": away_features["stats_matches_last5"],
        "home_xg_matches_last5": home_features["xg_matches_last5"],
        "away_xg_matches_last5": away_features["xg_matches_last5"],
    }
    source_dates = [row["date"] for team in (home, away) for row in histories[team][-10:]]
    return {
        "match_id": match["match_id"], "fixture_id": match.get("api_football_fixture_id") or match.get("fixture_id"),
        "date": date, "split": match.get("split") or ("future_2026" if future else None),
        "home_team": home, "away_team": away, "home_features": home_features, "away_features": away_features,
        "diff_features": diff, "coverage": coverage,
        "source_date_count": len(source_dates), "max_source_date": max(source_dates) if source_dates else None,
        "leakage_safe": all(source < date for source in source_dates),
    }


def main() -> None:
    matches = []
    for path in MATCH_FILES:
        split = path.name.removeprefix("historical_").removesuffix("_matches_v2_1.json")
        for item in load_json(path):
            matches.append(item | {"split": split})
    matches.sort(key=lambda item: (item["kickoff_at"], item["api_football_fixture_id"]))
    histories: dict[str, list[dict[str, Any]]] = defaultdict(list)
    features, source_records = [], 0
    for match in matches:
        features.append(build_match_feature(match, histories))
        record = source_record(match)
        if record:
            source_records += 1
            histories[str(match["home_team"])].append(record[str(match["home_team"])])
            histories[str(match["away_team"])].append(record[str(match["away_team"])])
    predictions = load_json(FUTURE_PREDICTIONS)
    for prediction in predictions:
        features.append(build_match_feature({
            "match_id": prediction["match_id"], "fixture_id": prediction.get("fixture_id"),
            "kickoff_at": prediction.get("kickoff_at") or prediction.get("date") or prediction.get("generated_at"),
            "home_team": prediction["home_team"], "away_team": prediction["away_team"],
        }, histories, future=True))
    payload = {
        "version": "v2.28",
        "feature_policy": {
            "strict_chronology": True, "uses_only_prior_matches": True,
            "missingness_indicators": True, "xg_missing_not_invented": True,
            "lineups_excluded_until_prematch_timestamp_proven": True,
        },
        "features": features,
        "coverage_summary": {
            "historical_matches": len(matches), "future_matches": len(predictions),
            "features_total": len(features), "post_match_stat_source_matches": source_records,
            "features_with_any_stats_last5": sum(row["coverage"]["home_stats_matches_last5"] + row["coverage"]["away_stats_matches_last5"] > 0 for row in features),
            "features_with_both_xg_last5": sum(row["coverage"]["home_xg_matches_last5"] > 0 and row["coverage"]["away_xg_matches_last5"] > 0 for row in features),
            "leakage_safe_rows": sum(bool(row["leakage_safe"]) for row in features),
        },
        "warnings": [
            "The feature set is intentionally sparse because only cached historical API-Football statistics are used.",
            "xG remains null when unavailable; missingness indicators are part of the contract.",
        ],
    }
    publish(payload)
    print(f"V2.28 lagged API stats features: rows={len(features)}, stat_source_matches={source_records}")


if __name__ == "__main__":
    main()
