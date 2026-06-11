"""Probe and cache post-match statistics, events and lineups for a bounded sample."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.data_acquisition.api_football_client import ApiFootballClient, ApiFootballError
from backend.scripts.pipeline_utils import DATA_DIR, write_json
from backend.scripts.v2_1_data_utils import RAW_V21, base_report, load, publish, response, write_doc


def stat_map(items: list[dict[str, Any]]) -> dict[str, Any]:
    return {str(item.get("type")): item.get("value") for item in items}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample-size", type=int, default=6)
    parser.add_argument("--max-requests", type=int, default=18)
    parser.add_argument("--force-refresh", action="store_true")
    args = parser.parse_args()
    matches = load(DATA_DIR / "normalized" / "historical_matches_refreshed_v2_1.json")
    selected = []
    seen_competitions = set()
    for match in reversed(matches):
        if match["competition"] not in seen_competitions:
            selected.append(match)
            seen_competitions.add(match["competition"])
        if len(selected) >= args.sample_size:
            break
    feature_raw = RAW_V21 / "features"
    feature_raw.mkdir(parents=True, exist_ok=True)
    client = None
    failures = []
    try:
        client = ApiFootballClient(max_calls=args.max_requests)
    except ApiFootballError as exc:
        failures.append({"scope": "client_initialization", "error": str(exc)})
    records = []
    endpoints = {"statistics": "fixtures/statistics", "events": "fixtures/events", "lineups": "fixtures/lineups"}
    for match in selected:
        fixture_id = match["api_football_fixture_id"]
        payloads = {}
        for feature, endpoint in endpoints.items():
            path = feature_raw / f"{feature}_{fixture_id}.json"
            try:
                if path.exists() and not args.force_refresh:
                    payloads[feature] = load(path)
                elif client is not None:
                    payloads[feature] = client.get(endpoint, {"fixture": fixture_id})
                    write_json(payloads[feature], path)
                else:
                    payloads[feature] = {"response": [], "errors": ["API client unavailable"]}
            except (ApiFootballError, OSError, json.JSONDecodeError) as exc:
                failures.append({"fixture_id": fixture_id, "feature": feature, "error": str(exc)})
                payloads[feature] = {"response": [], "errors": [str(exc)]}
        statistics = response(payloads["statistics"])
        events = response(payloads["events"])
        lineups = response(payloads["lineups"])
        records.append(
            {
                "match_id": match["match_id"],
                "api_football_fixture_id": fixture_id,
                "kickoff_at": match["kickoff_at"],
                "competition": match["competition"],
                "post_match_only": True,
                "statistics_available": bool(statistics),
                "events_available": bool(events),
                "lineups_available": bool(lineups),
                "statistics": [
                    {"team": item.get("team", {}).get("name"), "values": stat_map(item.get("statistics", []))}
                    for item in statistics
                ],
                "events_count": len(events),
                "event_types": dict(Counter(str(item.get("type")) for item in events)),
                "lineups": [
                    {
                        "team": item.get("team", {}).get("name"),
                        "formation": item.get("formation"),
                        "starting_xi_count": len(item.get("startXI", [])),
                        "substitutes_count": len(item.get("substitutes", [])),
                        "coach": item.get("coach", {}).get("name"),
                    }
                    for item in lineups
                ],
                "venue": match.get("venue"),
                "city": match.get("city"),
                "neutral_flag_available": False,
            }
        )
    write_json(records, DATA_DIR / "normalized" / "historical_match_features_v2_1.json")
    total = len(records)
    report = base_report() | {
        "status": "feature_probe",
        "request_count": client.call_count if client else 0,
        "sample_matches": total,
        "statistics_available_matches": sum(item["statistics_available"] for item in records),
        "events_available_matches": sum(item["events_available"] for item in records),
        "lineups_available_matches": sum(item["lineups_available"] for item in records),
        "venue_available_matches": sum(bool(item["venue"]) for item in records),
        "neutral_flag_available_matches": 0,
        "coverage": {
            feature: (sum(item[f"{feature}_available"] for item in records) / total if total else 0)
            for feature in ("statistics", "events", "lineups")
        },
        "post_match_features_not_valid_for_same_match_prediction": True,
        "odds_used_as_feature": False,
        "failures": failures,
        "limitations": [
            "The bounded sample measures feasibility, not whole-dataset coverage.",
            "Statistics, events and lineups are post-match evidence and require lagged aggregation for V2.2.",
            "No reliable neutral flag was found in normalized fixture records.",
        ],
    }
    publish("match_feature_availability_v2_1.json", report)
    write_doc(
        "MATCH_FEATURE_AVAILABILITY_V2_1.md",
        f"""# Match Feature Availability V2.1

V2.1 probed `{total}` recent completed matches across distinct competitions,
using at most `{args.max_requests}` API calls. Statistics were available for
`{report['statistics_available_matches']}/{total}` matches, events for
`{report['events_available_matches']}/{total}`, and lineups for
`{report['lineups_available_matches']}/{total}`. Venue names were present for
`{report['venue_available_matches']}/{total}`, while a reliable neutral flag
was unavailable.

These payloads are explicitly post-match-only. They may support future lagged
team aggregates, but using a match's own shots, events or lineup outcomes to
predict that same match would be temporal leakage. Odds were not fetched or
used as a feature. Sparse or unavailable fields remain documented rather than
invented.
""",
    )
    print(f"V2.1 feature probe: sample={total}, requests={report['request_count']}, coverage={report['coverage']}.")


if __name__ == "__main__":
    main()
