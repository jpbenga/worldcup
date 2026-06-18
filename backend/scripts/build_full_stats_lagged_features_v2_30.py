"""Build full strict chronological lagged API-Football statistics features."""

from __future__ import annotations

import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.full_stats_engine_v2_30_utils import avg, number, parse_date, publish
from backend.scripts.pipeline_utils import DATA_DIR, load_json

OUTPUT = "full_stats_lagged_features_v2_30.json"
CACHE_ROOT = DATA_DIR / "cache" / "api_football" / "historical_stats"
MATCH_FILES = [
    DATA_DIR / "normalized" / "historical_train_matches_v2_1.json",
    DATA_DIR / "normalized" / "historical_validation_matches_v2_1.json",
    DATA_DIR / "normalized" / "historical_test_matches_v2_1.json",
]
FUTURE_PREDICTIONS = DATA_DIR / "generated" / "predictions.json"
SUMMARY = DATA_DIR / "generated" / "api_football_full_collection_summary_v2_29.json"
MANIFEST = DATA_DIR / "generated" / "api_football_historical_stats_collection_manifest_v2_29.json"
WINDOWS = (3, 5, 10)

STAT_NAMES = {
    "expected_goals": "xg",
    "Total Shots": "shots",
    "Shots on Goal": "shots_on_goal",
    "Shots off Goal": "shots_off_goal",
    "Blocked Shots": "blocked_shots",
    "Shots insidebox": "shots_inside_box",
    "Shots outsidebox": "shots_outside_box",
    "Ball Possession": "possession",
    "Corner Kicks": "corners",
    "Fouls": "fouls",
    "Offsides": "offsides",
    "Yellow Cards": "yellow_cards",
    "Red Cards": "red_cards",
    "Goalkeeper Saves": "goalkeeper_saves",
    "Total passes": "passes_total",
    "Passes accurate": "passes_accurate",
    "Passes %": "passes_pct",
    "goals_prevented": "goals_prevented",
}


def response(fixture_id: int, endpoint: str) -> list[Any]:
    path = CACHE_ROOT / str(fixture_id) / f"{endpoint}.json"
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    value = payload.get("response", [])
    return value if isinstance(value, list) else []


def rows_by_team_id(items: list[Any]) -> dict[int, dict[str, float]]:
    result: dict[int, dict[str, float]] = {}
    for row in items:
        if not isinstance(row, dict):
            continue
        team = row.get("team") or {}
        team_id = team.get("id")
        if team_id is None:
            continue
        values: dict[str, float] = {}
        for stat in row.get("statistics", []):
            if not isinstance(stat, dict):
                continue
            key = STAT_NAMES.get(str(stat.get("type")))
            value = number(stat.get("value"))
            if key and value is not None:
                values[key] = value
        result[int(team_id)] = values
    return result


def event_rows_by_team_id(items: list[Any]) -> dict[int, dict[str, float]]:
    result: dict[int, dict[str, float]] = defaultdict(lambda: {
        "event_goals": 0.0, "event_penalties": 0.0, "event_yellow_cards": 0.0,
        "event_red_cards": 0.0, "event_substitutions": 0.0,
    })
    for event in items:
        if not isinstance(event, dict):
            continue
        team_id = (event.get("team") or {}).get("id")
        if team_id is None:
            continue
        row = result[int(team_id)]
        typ, detail = str(event.get("type") or ""), str(event.get("detail") or "")
        row["event_goals"] += float(typ == "Goal")
        row["event_penalties"] += float("Penalty" in detail)
        row["event_yellow_cards"] += float(typ == "Card" and "Yellow" in detail)
        row["event_red_cards"] += float(typ == "Card" and "Red" in detail)
        row["event_substitutions"] += float(typ == "subst")
    return dict(result)


def player_rows_by_team_id(items: list[Any]) -> dict[int, dict[str, float]]:
    result: dict[int, dict[str, float]] = {}
    for team_row in items:
        if not isinstance(team_row, dict):
            continue
        team_id = (team_row.get("team") or {}).get("id")
        if team_id is None:
            continue
        ratings: list[float] = []
        minutes = shots = shots_on = saves = tackles = duels = duels_won = 0.0
        players_count = 0
        for player in team_row.get("players", []):
            if not isinstance(player, dict):
                continue
            for stats in player.get("statistics", []):
                if not isinstance(stats, dict):
                    continue
                players_count += 1
                games = stats.get("games") or {}
                rating = number(games.get("rating"))
                if rating is not None:
                    ratings.append(rating)
                minutes += number(games.get("minutes")) or 0.0
                shots += number((stats.get("shots") or {}).get("total")) or 0.0
                shots_on += number((stats.get("shots") or {}).get("on")) or 0.0
                saves += number((stats.get("goals") or {}).get("saves")) or 0.0
                tackles += number((stats.get("tackles") or {}).get("total")) or 0.0
                duels += number((stats.get("duels") or {}).get("total")) or 0.0
                duels_won += number((stats.get("duels") or {}).get("won")) or 0.0
        result[int(team_id)] = {
            "player_rating_avg": avg(ratings),
            "player_minutes_total": minutes,
            "player_shots_total": shots,
            "player_shots_on_total": shots_on,
            "player_saves_total": saves,
            "player_tackles_total": tackles,
            "player_duels_total": duels,
            "player_duels_won_total": duels_won,
            "player_rows": float(players_count),
        }
    return result


def source_record(match: dict[str, Any]) -> dict[str, dict[str, Any]]:
    fixture_id = int(match["api_football_fixture_id"])
    stats = rows_by_team_id(response(fixture_id, "statistics"))
    events = event_rows_by_team_id(response(fixture_id, "events"))
    players = player_rows_by_team_id(response(fixture_id, "players"))
    lineups = response(fixture_id, "lineups")
    out: dict[str, dict[str, Any]] = {}
    for side in ("home", "away"):
        team = str(match[f"{side}_team"])
        opponent_side = "away" if side == "home" else "home"
        team_id = int(match[f"{side}_team_id"])
        opponent_id = int(match[f"{opponent_side}_team_id"])
        goals_for = int(match[f"{side}_score"])
        goals_against = int(match[f"{opponent_side}_score"])
        values = stats.get(team_id, {})
        opp_values = stats.get(opponent_id, {})
        event_values = events.get(team_id, {})
        player_values = players.get(team_id, {})
        row = {
            "fixture_id": fixture_id,
            "match_id": match["match_id"],
            "date": match["kickoff_at"],
            "team": team,
            "opponent": str(match[f"{opponent_side}_team"]),
            "goals_for": goals_for,
            "goals_against": goals_against,
            "clean_sheet": float(goals_against == 0),
            "large_win": float(goals_for - goals_against >= 3),
            "stats_available": bool(values),
            "xg_available": values.get("xg") is not None and opp_values.get("xg") is not None,
            "events_available": bool(events),
            "players_available": bool(player_values and player_values.get("player_rows")),
            "lineups_available": bool(lineups),
            "lineups_used_as_predictive_feature": False,
            "xg_for": values.get("xg"),
            "xg_against": opp_values.get("xg"),
            "xg_diff": values.get("xg") - opp_values.get("xg") if values.get("xg") is not None and opp_values.get("xg") is not None else None,
            "goals_minus_xg": goals_for - values.get("xg") if values.get("xg") is not None else None,
            "goals_against_minus_xg_against": goals_against - opp_values.get("xg") if opp_values.get("xg") is not None else None,
        }
        for key, value in values.items():
            row[f"{key}_for" if key not in {"possession", "passes_total", "passes_accurate", "passes_pct", "goalkeeper_saves", "goals_prevented", "fouls", "yellow_cards", "red_cards", "offsides"} else key] = value
        for key in ("shots", "shots_on_goal", "corners", "fouls", "yellow_cards", "red_cards", "goalkeeper_saves", "goals_prevented"):
            row[f"{key}_against"] = opp_values.get(key)
        row.update(event_values)
        row["event_goal_diff"] = event_values.get("event_goals", 0.0) - events.get(opponent_id, {}).get("event_goals", 0.0)
        row.update(player_values)
        out[team] = row
    return out


def window_features(history: list[dict[str, Any]], target_date: str, window: int) -> dict[str, Any]:
    rows = history[-window:]
    stat_rows = [row for row in rows if row["stats_available"]]
    xg_rows = [row for row in rows if row["xg_available"]]
    event_rows = [row for row in rows if row["events_available"]]
    player_rows = [row for row in rows if row["players_available"]]
    target = parse_date(target_date)
    latest = rows[-1] if rows else None
    age = (target - parse_date(latest["date"])).days if latest else None
    out: dict[str, Any] = {
        f"matches_last{window}": len(rows),
        f"stats_matches_last{window}": len(stat_rows),
        f"xg_matches_last{window}": len(xg_rows),
        f"events_matches_last{window}": len(event_rows),
        f"players_matches_last{window}": len(player_rows),
        f"stats_missing_last{window}": int(not stat_rows),
        f"xg_missing_last{window}": int(not xg_rows),
        f"events_missing_last{window}": int(not event_rows),
        f"players_missing_last{window}": int(not player_rows),
        f"recency_age_days_last{window}": age,
        f"goals_for_avg_last{window}": avg([row["goals_for"] for row in rows]),
        f"goals_against_avg_last{window}": avg([row["goals_against"] for row in rows]),
        f"clean_sheet_rate_last{window}": avg([row["clean_sheet"] for row in rows]),
        f"large_win_rate_last{window}": avg([row["large_win"] for row in rows]),
    }
    for field, source in (
        ("xg_for", xg_rows), ("xg_against", xg_rows), ("xg_diff", xg_rows),
        ("goals_minus_xg", xg_rows), ("goals_against_minus_xg_against", xg_rows),
        ("shots_for", stat_rows), ("shots_against", stat_rows),
        ("shots_on_goal_for", stat_rows), ("shots_on_goal_against", stat_rows),
        ("possession", stat_rows), ("corners_for", stat_rows), ("corners_against", stat_rows),
        ("passes_total", stat_rows), ("passes_accurate", stat_rows),
        ("passes_pct", stat_rows), ("goalkeeper_saves", stat_rows),
        ("goalkeeper_saves_against", stat_rows), ("goals_prevented", stat_rows),
        ("goals_prevented_against", stat_rows), ("fouls", stat_rows),
        ("yellow_cards", stat_rows), ("red_cards", stat_rows),
        ("event_goals", event_rows), ("event_goal_diff", event_rows),
        ("event_penalties", event_rows), ("event_yellow_cards", event_rows),
        ("event_red_cards", event_rows), ("event_substitutions", event_rows),
        ("player_rating_avg", player_rows), ("player_minutes_total", player_rows),
        ("player_shots_total", player_rows), ("player_shots_on_total", player_rows),
        ("player_saves_total", player_rows), ("player_tackles_total", player_rows),
        ("player_duels_won_total", player_rows),
    ):
        out[f"{field}_avg_last{window}"] = avg([row.get(field) for row in source])
    shots, sog = out.get(f"shots_for_avg_last{window}"), out.get(f"shots_on_goal_for_avg_last{window}")
    out[f"shot_on_target_ratio_last{window}"] = round(sog / shots, 6) if shots and sog is not None else None
    return {key: value for key, value in out.items() if value is not None and not (isinstance(value, float) and math.isnan(value))}


def build_match_feature(match: dict[str, Any], histories: dict[str, list[dict[str, Any]]], split: str) -> dict[str, Any]:
    home, away, date = str(match["home_team"]), str(match["away_team"]), str(match["kickoff_at"])
    home_history = [row for row in histories[home] if row["date"] < date]
    away_history = [row for row in histories[away] if row["date"] < date]
    home_features: dict[str, Any] = {}
    away_features: dict[str, Any] = {}
    for window in WINDOWS:
        home_features.update(window_features(home_history, date, window))
        away_features.update(window_features(away_history, date, window))
    diff = {}
    for key, value in home_features.items():
        other = away_features.get(key)
        if isinstance(value, (int, float)) and isinstance(other, (int, float)):
            diff[f"home_minus_away_{key}"] = round(float(value) - float(other), 6)
    source_dates = [row["date"] for history in (home_history, away_history) for row in history[-10:]]
    coverage = {
        "home_stats_matches_last5": home_features.get("stats_matches_last5", 0),
        "away_stats_matches_last5": away_features.get("stats_matches_last5", 0),
        "home_xg_matches_last5": home_features.get("xg_matches_last5", 0),
        "away_xg_matches_last5": away_features.get("xg_matches_last5", 0),
        "home_events_matches_last5": home_features.get("events_matches_last5", 0),
        "away_events_matches_last5": away_features.get("events_matches_last5", 0),
        "home_players_matches_last5": home_features.get("players_matches_last5", 0),
        "away_players_matches_last5": away_features.get("players_matches_last5", 0),
    }
    return {
        "match_id": match["match_id"],
        "fixture_id": match.get("api_football_fixture_id") or match.get("fixture_id"),
        "date": date,
        "split": split,
        "home_team": home,
        "away_team": away,
        "home_features": home_features,
        "away_features": away_features,
        "diff_features": diff,
        "coverage": coverage,
        "source_dates": source_dates,
        "source_date_count": len(source_dates),
        "max_source_date": max(source_dates) if source_dates else None,
        "leakage_safe": all(source < date for source in source_dates),
    }


def main() -> None:
    matches: list[dict[str, Any]] = []
    for path in MATCH_FILES:
        split = path.name.removeprefix("historical_").removesuffix("_matches_v2_1.json")
        matches.extend(item | {"split": split} for item in load_json(path))
    matches.sort(key=lambda item: (item["kickoff_at"], item["api_football_fixture_id"]))
    histories: dict[str, list[dict[str, Any]]] = defaultdict(list)
    features: list[dict[str, Any]] = []
    stats_sources = xg_sources = events_sources = players_sources = 0
    for match in matches:
        features.append(build_match_feature(match, histories, str(match["split"])))
        records = source_record(match)
        for team in (str(match["home_team"]), str(match["away_team"])):
            row = records[team]
            histories[team].append(row)
        stats_sources += int(records[str(match["home_team"])]["stats_available"] and records[str(match["away_team"])]["stats_available"])
        xg_sources += int(records[str(match["home_team"])]["xg_available"] and records[str(match["away_team"])]["xg_available"])
        events_sources += int(records[str(match["home_team"])]["events_available"] or records[str(match["away_team"])]["events_available"])
        players_sources += int(records[str(match["home_team"])]["players_available"] or records[str(match["away_team"])]["players_available"])
    for prediction in load_json(FUTURE_PREDICTIONS):
        features.append(build_match_feature({
            "match_id": prediction["match_id"],
            "fixture_id": prediction.get("fixture_id"),
            "kickoff_at": prediction.get("kickoff_at") or prediction.get("date") or prediction["generated_at"],
            "home_team": prediction["home_team"],
            "away_team": prediction["away_team"],
        }, histories, "future_2026"))
    collection = load_json(SUMMARY)
    manifest = load_json(MANIFEST)
    payload = {
        "version": "v2.30",
        "source_collection": {
            "version": collection["version"],
            "units_total": collection["units_total"],
            "units_completed": collection["units_completed"],
            "units_remaining": collection["units_remaining"],
            "fixtures_with_any_stats": collection["fixtures_with_any_stats"],
            "ready_for_model_retest": collection["ready_for_model_retest"],
            "failed_units": manifest["failed_units"],
            "rate_limited_units": manifest["rate_limited_units"],
        },
        "feature_policy": {
            "strict_chronology": True,
            "uses_only_prior_matches": True,
            "xg_missing_not_invented": True,
            "missingness_indicators": True,
            "lineups_excluded_until_prematch_timestamp_proven": True,
            "lineups_used_as_predictive_feature": False,
            "no_team_specific_patch": True,
        },
        "features": features,
        "coverage_summary": {
            "historical_matches": len(matches),
            "future_matches": len(features) - len(matches),
            "features_total": len(features),
            "post_match_stat_source_matches": stats_sources,
            "post_match_xg_source_matches": xg_sources,
            "post_match_event_source_matches": events_sources,
            "post_match_player_source_matches": players_sources,
            "features_with_any_stats_last5": sum(row["coverage"]["home_stats_matches_last5"] + row["coverage"]["away_stats_matches_last5"] > 0 for row in features),
            "features_with_both_xg_last5": sum(row["coverage"]["home_xg_matches_last5"] > 0 and row["coverage"]["away_xg_matches_last5"] > 0 for row in features),
            "leakage_safe_rows": sum(bool(row["leakage_safe"]) for row in features),
        },
        "warnings": [
            "Lineups are counted for coverage only and excluded from predictive features because no pre-match publication timestamp is proven.",
            "xG remains null when unavailable; no synthetic xG is imputed.",
        ],
    }
    publish(payload, OUTPUT)
    print(
        "V2.30 full stats lagged features: "
        f"rows={len(features)}, stats_sources={stats_sources}, xg_sources={xg_sources}"
    )


if __name__ == "__main__":
    main()
