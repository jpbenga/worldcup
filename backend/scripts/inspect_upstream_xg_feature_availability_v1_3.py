"""Inspect upstream xG feature availability without training or changing predictions."""

from __future__ import annotations

import shutil
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, utc_now, write_json

VERSION = "v1.3"
RECENT_WINDOW_MONTHS = 24


def parse_date(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def date_range(matches: list[dict[str, Any]]) -> dict[str, Any]:
    dates = [parse_date(str(match["kickoff_at"])) for match in matches]
    return {
        "matches": len(matches),
        "date_min": min(dates).isoformat() if dates else None,
        "date_max": max(dates).isoformat() if dates else None,
    }


def publish(filename: str, payload: dict[str, Any]) -> None:
    generated = DATA_DIR / "generated" / filename
    snapshot = DATA_DIR / "snapshots" / filename
    frontend = FRONTEND_DATA_DIR / filename
    write_json(payload, generated)
    snapshot.parent.mkdir(parents=True, exist_ok=True)
    frontend.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(generated, snapshot)
    shutil.copy2(generated, frontend)


def build_design() -> dict[str, Any]:
    return {
        "version": VERSION,
        "status": "design_only",
        "base_model": "calibrated_simple_poisson_v0.9",
        "previous_challenger_result": "v1.2_no_isolated_post_probability_challenger_passed",
        "promotion_recommendation": "do_not_promote_yet",
        "implementation_phase": "v1.4",
        "challengers": [
            {
                "id": "competition_weighted_xg",
                "priority": 1,
                "target": "competition-specific scoring distributions",
                "implementation_phase": "v1.4",
                "candidate_params": {
                    "major_tournament_weight": 1.0,
                    "continental_championship_weight": 0.9,
                    "qualifier_weight": 0.75,
                    "friendly_weight": 0.4,
                },
                "risk": "arbitrary weighting",
            },
            {
                "id": "time_decay_xg",
                "priority": 2,
                "target": "recent team-strength changes",
                "implementation_phase": "v1.4",
                "candidate_params": {"half_life_months": [12, 24, 36, 48]},
                "risk": "low effective sample size and recent-tournament overfitting",
            },
            {
                "id": "elo_prior_xg",
                "priority": 3,
                "target": "strength prior and low-sample stabilization",
                "implementation_phase": "v1.4_limited_unless_historical_elo_is_available",
                "candidate_params": {"elo_prior_weight": 0.15, "elo_diff_scale": 400, "elo_factor_cap": 0.25},
                "risk": "temporal leakage from current static Elo",
            },
            {
                "id": "low_sample_fallback_xg",
                "priority": 4,
                "target": "stable xG for teams with sparse historical evidence",
                "implementation_phase": "v1.4",
                "candidate_params": {"low_sample_threshold": 8, "extra_smoothing_weight": 12},
                "risk": "oversmoothing real differences",
            },
            {
                "id": "upstream_combined_candidate",
                "priority": 5,
                "target": "combine only independently successful upstream features",
                "implementation_phase": "deferred",
                "risk": "confounded gains before isolated evidence exists",
            },
        ],
        "guardrails": [
            "Select parameters on validation only and use test only for final evaluation.",
            "Improve V0.9 test log loss and Brier by at least 0.01 each.",
            "Do not materially worsen draw calibration, modal 1-1 concentration, or high-confidence errors.",
            "Do not use current static Elo as historical pre-match Elo without labeling temporal leakage.",
            "Do not promote automatically or implement the combined candidate before isolated successes.",
        ],
        "do_not_modify": [
            "World Cup 2026 predictions",
            "current prototype engine",
            "main Angular app predictions",
        ],
    }


def render_availability(availability: dict[str, Any]) -> str:
    low_sample = availability["low_sample_teams"]
    coverage = availability["elo_availability"]
    split_rows = "\n".join(
        f"| {name.title()} | {values['matches']} | {values['date_min']} | {values['date_max']} |"
        for name, values in availability["split_date_ranges"].items()
    )
    competition_rows = "\n".join(
        f"| {name} | {count} |" for name, count in availability["matches_by_competition"].items()
    )
    return f"""# Upstream xG Feature Availability V1.3

## Scope

This read-only inspection measures whether the current historical dataset can
support future upstream xG challengers. It does not train a model, select a
parameter, evaluate a challenger, or modify World Cup 2026 predictions.

## Dataset coverage

- Total historical matches: `{availability['total_matches']}`
- Historical teams: `{availability['teams_count']}`
- Competitions: `{len(availability['matches_by_competition'])}`
- Competition tiers: `{availability['matches_by_competition_tier']}`
- Competition families: `{availability['matches_by_competition_family']}`
- Seasons: `{availability['matches_by_season']}`

| Competition | Matches |
|---|---:|
{competition_rows}

| Split | Matches | Date min | Date max |
|---|---:|---|---|
{split_rows}

## Low-sample and recent coverage

- Teams below 5 matches: `{low_sample['below_5']['teams_count']}`
- Teams below 8 matches: `{low_sample['below_8']['teams_count']}`
- Teams below 10 matches: `{low_sample['below_10']['teams_count']}`
- Recent window: `{availability['recent_coverage']['window_months']}` months before
  `{availability['recent_coverage']['reference_date']}`
- Teams with no match in that recent window: `{availability['recent_coverage']['teams_with_zero_recent_matches']}`
- Teams below 5 recent matches: `{availability['recent_coverage']['teams_below_5_recent_matches']}`

The full team lists and counts are retained in the JSON artifact.

## Elo and identity availability

- Elo ratings rows: `{coverage['ratings_rows']}`
- Elo retrieval timestamps: `{coverage['retrieved_at_values']}`
- Historical teams with an exact Elo-name match: `{coverage['historical_teams_with_exact_elo_name']}`
- Historical teams covered by exact Elo name or identity mapping: `{coverage['historical_teams_covered']}`
- Historical teams without Elo coverage: `{coverage['historical_teams_without_elo_coverage_count']}`
- Identity-map rows: `{coverage['identity_mapping_rows']}`
- Historical teams without an identity-map entry: `{coverage['historical_teams_without_identity_mapping_count']}`

## Temporal leakage risks

{chr(10).join(f"- {risk}" for risk in availability['temporal_leakage_risks'])}

## Recommendations for V1.4

{chr(10).join(f"- {item}" for item in availability['recommendations'])}

## Decision

Competition, date and low-sample signals are available for isolated V1.4
experiments. Elo is current/static rather than historical pre-match evidence,
so an Elo-prior challenger must remain limited or wait for temporally aligned
ratings. Promotion remains `do_not_promote_yet`.
"""


def main() -> None:
    normalized = DATA_DIR / "normalized"
    expanded: list[dict[str, Any]] = load_json(normalized / "historical_matches_expanded.json")
    splits = {
        split: load_json(normalized / f"historical_{split}_matches.json") for split in ("train", "validation", "test")
    }
    ratings: list[dict[str, Any]] = load_json(normalized / "team_ratings.json")
    identity_map: list[dict[str, Any]] = load_json(DATA_DIR / "mappings" / "team_identity_map.json")

    if any(match.get("season") == 2026 or match.get("is_future_fixture") for match in expanded):
        raise ValueError("Future or 2026 fixtures must not enter V1.3 feature inspection")
    split_ids = [str(match["match_id"]) for split in splits.values() for match in split]
    if len(split_ids) != len(expanded) or set(split_ids) != {str(match["match_id"]) for match in expanded}:
        raise ValueError("Chronological splits do not align with the expanded historical dataset")

    team_counts = Counter(team for match in expanded for team in (str(match["home_team"]), str(match["away_team"])))
    historical_teams = set(team_counts)
    elo_names = {str(item["team_name"]) for item in ratings}
    identity_names: dict[str, str | None] = {}
    for item in identity_map:
        api_name = item.get("api_football", {}).get("name")
        display_name = item.get("display_name")
        elo_name = item.get("elo", {}).get("team_name")
        for name in (api_name, display_name):
            if name:
                identity_names[str(name)] = str(elo_name) if elo_name else None
    exact_elo = historical_teams & elo_names
    mapped_elo = {team for team in historical_teams if identity_names.get(team) in elo_names}
    covered_elo = exact_elo | mapped_elo

    reference_date = max(parse_date(str(match["kickoff_at"])) for match in expanded)
    recent_cutoff = reference_date.timestamp() - RECENT_WINDOW_MONTHS * 30.4375 * 24 * 60 * 60
    recent_counts = Counter()
    for match in expanded:
        if parse_date(str(match["kickoff_at"])).timestamp() >= recent_cutoff:
            recent_counts.update((str(match["home_team"]), str(match["away_team"])))

    low_sample = {}
    for threshold in (5, 8, 10):
        teams = sorted(team for team, count in team_counts.items() if count < threshold)
        low_sample[f"below_{threshold}"] = {"threshold": threshold, "teams_count": len(teams), "teams": teams}

    retrieved_at_values = sorted({str(item.get("retrieved_at")) for item in ratings if item.get("retrieved_at")})
    temporal_risks = [
        "team_ratings.json contains current/static Elo snapshots, not ratings known before each historical kickoff.",
        "The Elo snapshot was retrieved after every historical split; using it directly would leak future information.",
        "team_identity_map.json covers only a subset of historical teams and cannot by itself create historical Elo provenance.",
        "Time decay must calculate age relative to each predicted match and must never include later matches.",
    ]
    recommendations = [
        "Implement competition weighting and time decay first because their required fields already exist with historical dates.",
        "Evaluate low-sample fallback independently and report results for sparse teams versus adequately sampled teams.",
        "Use Elo in V1.4 only with reconstructed or sourced pre-match ratings; otherwise label it a limited leakage-risk experiment.",
        "Select every parameter on validation only, reserve test for final evaluation, and keep the combined candidate deferred.",
    ]
    availability = {
        "generated_at": utc_now(),
        "version": VERSION,
        "status": "read_only_feature_inspection",
        "total_matches": len(expanded),
        "teams_count": len(historical_teams),
        "matches_by_competition": dict(Counter(str(match["competition"]) for match in expanded).most_common()),
        "matches_by_competition_tier": dict(Counter(str(match["competition_tier"]) for match in expanded).most_common()),
        "matches_by_competition_family": dict(
            Counter(str(match["competition_family"]) for match in expanded).most_common()
        ),
        "matches_by_season": dict(Counter(str(match["season"]) for match in expanded).most_common()),
        "split_date_ranges": {split: date_range(matches) for split, matches in splits.items()},
        "team_match_counts": dict(team_counts.most_common()),
        "low_sample_teams": low_sample,
        "recent_coverage": {
            "window_months": RECENT_WINDOW_MONTHS,
            "reference_date": reference_date.isoformat(),
            "teams_with_zero_recent_matches": sum(recent_counts[team] == 0 for team in historical_teams),
            "teams_below_5_recent_matches": sum(recent_counts[team] < 5 for team in historical_teams),
            "team_recent_match_counts": {team: recent_counts[team] for team in sorted(historical_teams)},
        },
        "elo_availability": {
            "ratings_rows": len(ratings),
            "retrieved_at_values": retrieved_at_values,
            "rating_type": "current_static_snapshot",
            "historical_pre_match_elo_available": False,
            "historical_teams_with_exact_elo_name": len(exact_elo),
            "historical_teams_covered": len(covered_elo),
            "historical_teams_without_elo_coverage_count": len(historical_teams - covered_elo),
            "historical_teams_without_elo_coverage": sorted(historical_teams - covered_elo),
            "identity_mapping_rows": len(identity_map),
            "historical_teams_without_identity_mapping_count": len(historical_teams - set(identity_names)),
            "historical_teams_without_identity_mapping": sorted(historical_teams - set(identity_names)),
        },
        "temporal_leakage_risks": temporal_risks,
        "recommendations": recommendations,
        "model_trained": False,
        "predictions_modified": False,
        "promotion_recommendation": "do_not_promote_yet",
    }
    publish("upstream_xg_feature_availability_v1_3.json", availability)
    publish("upstream_xg_challenger_design_v1_3.json", build_design())
    (PROJECT_ROOT / "docs" / "UPSTREAM_XG_FEATURE_AVAILABILITY_V1_3.md").write_text(
        render_availability(availability), encoding="utf-8"
    )
    print(
        f"Inspected {len(expanded)} historical matches and {len(historical_teams)} teams; "
        f"Elo coverage={len(covered_elo)}/{len(historical_teams)}, model trained=no."
    )


if __name__ == "__main__":
    main()
