"""Aggregate the historical API-Football fixture audit by competition-season."""

from __future__ import annotations

import shutil
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, write_json

OUTPUT = "api_football_historical_coverage_matrix_v2_27_1.json"
SOURCE = DATA_DIR / "generated" / "api_football_historical_stats_coverage_v2_27_1.json"


def publish(payload: dict[str, Any]) -> None:
    target = DATA_DIR / "generated" / OUTPUT
    write_json(payload, target)
    shutil.copy2(target, DATA_DIR / "snapshots" / OUTPUT)
    shutil.copy2(target, FRONTEND_DATA_DIR / OUTPUT)


def rate(rows: list[dict[str, Any]], family: str, key: str = "available") -> float:
    return round(sum(bool(row[family][key]) for row in rows) / len(rows), 4)


def readiness(stats: float, xg: float, events: float, lineups: float, players: float, size: int) -> tuple[str, str]:
    minimum = min(stats, events, lineups, players)
    if size < 3 or minimum < 0.5:
        return "not_ready", "Sample or endpoint coverage is too weak for historical model features."
    if xg < 0.5 or minimum < 0.8:
        return "fragile", "Coverage is partial and would create substantial missingness or selection bias."
    if xg < 0.9 or minimum < 0.95:
        return "promising", "Coverage is encouraging but still requires a larger chronological audit."
    return "promising", "The bounded sample is strong, but five fixtures per competition cannot establish production readiness."


def main() -> None:
    audit = load_json(SOURCE)
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in audit["coverage_by_fixture"]:
        grouped[(row["competition"], row["season_or_year"])].append(row)
    matrix = []
    for (competition, season), rows in sorted(grouped.items()):
        values = {
            "statistics_available_rate": rate(rows, "statistics"),
            "xg_available_rate": rate(rows, "statistics", "xg_available"),
            "shots_available_rate": rate(rows, "statistics", "shots_available"),
            "possession_available_rate": rate(rows, "statistics", "possession_available"),
            "passes_available_rate": rate(rows, "statistics", "passes_available"),
            "events_available_rate": rate(rows, "events"),
            "lineups_available_rate": rate(rows, "lineups"),
            "players_available_rate": rate(rows, "players"),
        }
        status, reason = readiness(values["statistics_available_rate"], values["xg_available_rate"], values["events_available_rate"], values["lineups_available_rate"], values["players_available_rate"], len(rows))
        matrix.append({"competition": competition, "season_or_year": season, "sample_size": len(rows), **values, "algorithm_feature_readiness": status, "reason": reason})
    summary = audit["coverage_summary"]
    competitions = sorted({row["competition"] for row in audit["coverage_by_fixture"]})
    payload = {
        "version": "v2.27.1", "matrix": matrix,
        "global_summary": {
            "competitions_checked": len(competitions), "competition_seasons_checked": len(matrix),
            "fixtures_checked": summary["fixtures_checked"], "xg_global_rate": summary["xg_available_rate"],
            "statistics_global_rate": summary["statistics_available_rate"], "events_global_rate": summary["events_available_rate"],
            "lineups_global_rate": summary["lineups_available_rate"], "players_global_rate": summary["players_available_rate"],
        },
        "conclusion": "The stratified sample measures historical feasibility, but incomplete fields and sparse per-season samples require a broader chronological coverage audit before model use.",
    }
    publish(payload)
    print(f"V2.27.1 historical coverage matrix: rows={len(matrix)}, fixtures={summary['fixtures_checked']}")


if __name__ == "__main__":
    main()
