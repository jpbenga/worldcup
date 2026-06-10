"""Build an explicit, reviewable API-Football to Elo team identity map."""

from __future__ import annotations

import json
import re
import unicodedata
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "backend" / "data"
MAPPINGS_DIR = DATA_DIR / "mappings"
API_TEAMS_PATH = DATA_DIR / "normalized" / "external_teams_sample.json"
ELO_RATINGS_PATH = DATA_DIR / "normalized" / "team_ratings.json"
ALIASES_PATH = MAPPINGS_DIR / "team_aliases.json"
MAP_PATH = MAPPINGS_DIR / "team_identity_map.json"
UNMAPPED_PATH = MAPPINGS_DIR / "unmapped_teams.json"
REPORT_PATH = MAPPINGS_DIR / "team_mapping_report.json"
STATUS_PATH = DATA_DIR / "snapshots" / "team_mapping_status.json"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(data: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def normalize_name(name: str) -> str:
    folded = unicodedata.normalize("NFKD", name.casefold())
    without_accents = "".join(character for character in folded if not unicodedata.combining(character))
    return " ".join(re.sub(r"[^a-z0-9]+", " ", without_accents).split())


def internal_team_id(name: str) -> str:
    return normalize_name(name).replace(" ", "_")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def possible_elo_matches(api_name: str, elo_teams: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized_api = normalize_name(api_name)
    candidates = []
    for team in elo_teams:
        similarity = SequenceMatcher(None, normalized_api, normalize_name(team["team_name"])).ratio()
        candidates.append(
            {
                "team_name": team["team_name"],
                "rank": team["rank"],
                "elo_rating": team["elo_rating"],
                "similarity": round(similarity, 4),
            }
        )
    return sorted(candidates, key=lambda candidate: candidate["similarity"], reverse=True)[:3]


def main() -> None:
    api_teams: list[dict[str, Any]] = read_json(API_TEAMS_PATH)
    elo_teams: list[dict[str, Any]] = read_json(ELO_RATINGS_PATH)
    aliases: dict[str, list[str]] = read_json(ALIASES_PATH)
    elo_by_name = {team["team_name"]: team for team in elo_teams}
    elo_by_casefold: dict[str, list[dict[str, Any]]] = {}
    elo_by_normalized: dict[str, list[dict[str, Any]]] = {}
    for team in elo_teams:
        elo_by_casefold.setdefault(team["team_name"].casefold(), []).append(team)
        elo_by_normalized.setdefault(normalize_name(team["team_name"]), []).append(team)

    mapped: list[dict[str, Any]] = []
    unmapped_api: list[dict[str, Any]] = []
    used_elo_names: set[str] = set()

    for api_team in api_teams:
        api_name = api_team["team_name"]
        method = ""
        confidence = 0.0
        matches: list[dict[str, Any]] = []

        if api_name in elo_by_name:
            matches, method, confidence = [elo_by_name[api_name]], "exact", 1.0
        elif len(elo_by_casefold.get(api_name.casefold(), [])) == 1:
            matches, method, confidence = elo_by_casefold[api_name.casefold()], "normalized_exact", 0.99
        elif len(elo_by_normalized.get(normalize_name(api_name), [])) == 1:
            matches, method, confidence = elo_by_normalized[normalize_name(api_name)], "normalized_exact", 0.99
        else:
            alias_matches = [elo_by_name[alias] for alias in aliases.get(api_name, []) if alias in elo_by_name]
            if len(alias_matches) == 1:
                matches, method, confidence = alias_matches, "alias", 0.98

        if len(matches) == 1 and matches[0]["team_name"] not in used_elo_names:
            elo_team = matches[0]
            used_elo_names.add(elo_team["team_name"])
            mapped.append(
                {
                    "team_id": internal_team_id(api_name),
                    "display_name": api_name,
                    "country_code": api_team["code"],
                    "api_football": {
                        "team_id": api_team["external_team_id"],
                        "name": api_name,
                        "country": api_team["country"],
                    },
                    "elo": {
                        "team_name": elo_team["team_name"],
                        "rank": elo_team["rank"],
                        "elo_rating": elo_team["elo_rating"],
                    },
                    "mapping": {
                        "status": "auto_validated",
                        "confidence": confidence,
                        "method": method,
                        "needs_human_review": False,
                        "notes": f"{api_name} matched to {elo_team['team_name']} via {method}.",
                    },
                }
            )
            continue

        candidates = possible_elo_matches(api_name, elo_teams)
        best = candidates[0]["similarity"]
        gap = best - candidates[1]["similarity"]
        unmapped_api.append(
            {
                "team_id": api_team["external_team_id"],
                "name": api_name,
                "country": api_team["country"],
                "status": "needs_review" if best >= 0.8 and gap >= 0.05 else "unmapped_api_team",
                "possible_elo_matches": candidates,
            }
        )

    unmatched_elo = [
        {
            "team_name": team["team_name"],
            "rank": team["rank"],
            "elo_rating": team["elo_rating"],
            "status": "unmapped_elo_team",
            "possible_api_matches": [],
        }
        for team in elo_teams
        if team["team_name"] not in used_elo_names
    ]
    updated_at = utc_now()
    needs_review_count = sum(team["status"] == "needs_review" for team in unmapped_api)
    unmapped_api_count = sum(team["status"] == "unmapped_api_team" for team in unmapped_api)
    auto_validated_count = sum(team["mapping"]["status"] == "auto_validated" for team in mapped)
    coverage = round(len(mapped) / len(api_teams) * 100, 2) if api_teams else 0
    status = "PASS" if not unmapped_api else "PASS_WITH_REVIEW_REQUIRED"

    report = {
        "updated_at": updated_at,
        "api_football_teams_count": len(api_teams),
        "elo_teams_count": len(elo_teams),
        "mapped_count": len(mapped),
        "auto_validated_count": auto_validated_count,
        "needs_review_count": needs_review_count,
        "unmapped_api_count": unmapped_api_count,
        "unmapped_elo_count": len(unmatched_elo),
        "coverage_percent": coverage,
        "status": status,
        "methods": {
            method: sum(team["mapping"]["method"] == method for team in mapped)
            for method in sorted({team["mapping"]["method"] for team in mapped})
        },
        "warnings": [
            "Some teams require human validation before using Elo ratings in the model.",
            "Elo ratings remain excluded from the prediction engine.",
        ],
    }
    status_snapshot = {
        key: report[key]
        for key in (
            "updated_at",
            "api_football_teams_count",
            "elo_teams_count",
            "mapped_count",
            "auto_validated_count",
            "needs_review_count",
            "unmapped_api_count",
            "coverage_percent",
            "status",
        )
    }
    status_snapshot["elo_connected_to_prediction_engine"] = False

    write_json(mapped, MAP_PATH)
    write_json(
        {"updated_at": updated_at, "unmapped_api_teams": unmapped_api, "unmapped_elo_teams": unmatched_elo},
        UNMAPPED_PATH,
    )
    write_json(report, REPORT_PATH)
    write_json(status_snapshot, STATUS_PATH)
    print(f"Mapped {len(mapped)}/{len(api_teams)} API-Football teams ({coverage:.2f}%).")
    print(f"Status: {status}; review required: {needs_review_count}; unmapped API teams: {unmapped_api_count}.")


if __name__ == "__main__":
    main()
