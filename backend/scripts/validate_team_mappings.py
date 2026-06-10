"""Validate structural and identity-safety rules for generated team mappings."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MAPPINGS_DIR = PROJECT_ROOT / "backend" / "data" / "mappings"


def read_json(filename: str) -> Any:
    return json.loads((MAPPINGS_DIR / filename).read_text(encoding="utf-8"))


def main() -> None:
    teams: list[dict[str, Any]] = read_json("team_identity_map.json")
    unmapped = read_json("unmapped_teams.json")
    report = read_json("team_mapping_report.json")
    errors: list[str] = []

    for field in ("team_id", "display_name", "country_code", "api_football", "elo", "mapping"):
        if any(field not in team for team in teams):
            errors.append(f"Missing required mapped-team field: {field}")
    for values, label in (
        ([team["team_id"] for team in teams], "team_id"),
        ([team["api_football"]["team_id"] for team in teams], "api_football.team_id"),
        ([team["elo"]["team_name"] for team in teams], "elo.team_name"),
    ):
        if len(values) != len(set(values)):
            errors.append(f"Duplicate mapped identity: {label}")
    if any(not 0 <= team["mapping"]["confidence"] <= 1 for team in teams):
        errors.append("Mapping confidence must be between 0 and 1")
    if any(team["mapping"]["status"] == "auto_validated" and team["mapping"]["confidence"] < 0.9 for team in teams):
        errors.append("Low-confidence mappings must not be auto-validated")
    if any(team["mapping"]["method"].startswith("fuzzy") and team["mapping"]["status"] == "auto_validated" for team in teams):
        errors.append("Fuzzy mappings must not be auto-validated")
    if any(team["mapping"]["needs_human_review"] and team["mapping"]["status"] == "auto_validated" for team in teams):
        errors.append("Mappings needing human review must not be auto-validated")
    if any(team["status"] not in {"needs_review", "unmapped_api_team", "rejected"} for team in unmapped["unmapped_api_teams"]):
        errors.append("Invalid unmapped API-team status")

    if report["mapped_count"] != len(teams):
        errors.append("Report mapped count does not match team_identity_map.json")
    if report["needs_review_count"] != sum(item["status"] == "needs_review" for item in unmapped["unmapped_api_teams"]):
        errors.append("Report needs-review count does not match unmapped_teams.json")
    if report["unmapped_api_count"] != sum(
        item["status"] in {"unmapped_api_team", "rejected"} for item in unmapped["unmapped_api_teams"]
    ):
        errors.append("Report unmapped API count does not match unmapped_teams.json")
    if report["api_football_teams_count"] != len(teams) + len(unmapped["unmapped_api_teams"]):
        errors.append("API-Football total is inconsistent")

    print("Team mapping validation")
    print(f"API teams: {report['api_football_teams_count']}")
    print(f"Mapped: {report['mapped_count']}")
    print(f"Auto validated: {report['auto_validated_count']}")
    print(f"Needs review: {report['needs_review_count']}")
    print(f"Unmapped API teams: {report['unmapped_api_count']}")
    print(f"Coverage: {report['coverage_percent']:.2f}%")
    if errors:
        print("Status: FAIL")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)
    print(f"Status: {report['status']}")


if __name__ == "__main__":
    main()
