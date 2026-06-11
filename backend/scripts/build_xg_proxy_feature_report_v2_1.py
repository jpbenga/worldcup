"""Assess whether sampled API-Football statistics support an exploratory xG proxy."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.scripts.pipeline_utils import DATA_DIR
from backend.scripts.v2_1_data_utils import base_report, load, publish, write_doc

ALIASES = {
    "shots_total": ("Total Shots",),
    "shots_on_goal": ("Shots on Goal",),
    "corners": ("Corner Kicks",),
}


def number(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.replace("%", ""))
        except ValueError:
            return None
    return None


def main() -> None:
    features = load(DATA_DIR / "normalized" / "historical_match_features_v2_1.json")
    rows = []
    complete_matches = 0
    team_stat_rows = 0
    true_xg_rows = 0
    competitions = set()
    seasons = set()
    matches = {item["match_id"]: item for item in load(DATA_DIR / "normalized" / "historical_matches_refreshed_v2_1.json")}
    for item in features:
        match_complete = True
        teams = []
        for team in item.get("statistics", []):
            team_stat_rows += 1
            values = team.get("values", {})
            true_xg = number(values.get("expected_goals"))
            true_xg_rows += int(true_xg is not None)
            extracted = {
                name: next((number(values.get(alias)) for alias in aliases if number(values.get(alias)) is not None), None)
                for name, aliases in ALIASES.items()
            }
            if any(value is None for value in extracted.values()):
                match_complete = False
            proxy = (
                0.05 * extracted["shots_total"] + 0.18 * extracted["shots_on_goal"] + 0.03 * extracted["corners"]
                if all(value is not None for value in extracted.values())
                else None
            )
            teams.append({"team": team.get("team"), **extracted, "provider_expected_goals": true_xg, "xg_proxy_exploratory": proxy})
        if match_complete and len(teams) == 2:
            complete_matches += 1
        match = matches.get(item["match_id"], {})
        competitions.add(str(item["competition"]))
        if isinstance(match.get("season"), int):
            seasons.add(match["season"])
        rows.append({"match_id": item["match_id"], "competition": item["competition"], "post_match_only": True, "teams": teams})
    sample = len(features)
    coverage = complete_matches / sample if sample else 0
    possible = complete_matches >= 3 and coverage >= 0.50
    broad_coverage_sufficient = sample >= 100 and coverage >= 0.80
    report = base_report() | {
        "status": "feasibility_analysis",
        "true_xg_available": true_xg_rows > 0,
        "true_xg_team_rows": true_xg_rows,
        "team_stat_rows": team_stat_rows,
        "true_xg_team_row_coverage": true_xg_rows / team_stat_rows if team_stat_rows else 0,
        "true_xg_coverage_sufficient": team_stat_rows >= 200 and true_xg_rows / team_stat_rows >= 0.80,
        "xg_proxy_possible": possible,
        "statistical_coverage_sufficient": broad_coverage_sufficient,
        "sample_matches": sample,
        "complete_proxy_matches": complete_matches,
        "complete_proxy_coverage": coverage,
        "competitions_covered": sorted(competitions),
        "seasons_covered": sorted(seasons),
        "formula": "0.05 * shots_total + 0.18 * shots_on_goal + 0.03 * corners",
        "proxy_rows": rows,
        "risk_of_bias": [
            "The coefficients are heuristic and not calibrated to shot location or chance quality.",
            "The sampled post-match statistics cannot be used for the same-match prediction.",
            "Coverage measured on a bounded sample may not generalize across eras and competitions.",
        ],
        "recommendation_for_v2_2": (
            "Technically feasible, but use only after broad coverage validation as an exploratory lagged team-form aggregate."
            if possible
            else "Do not use an xG proxy in V2.2 until broader stable statistics coverage is established."
        ),
    }
    publish("xg_proxy_feasibility_v2_1.json", report)
    write_doc(
        "XG_PROXY_FEASIBILITY_V2_1.md",
        f"""# xG Proxy Feasibility V2.1

API-Football exposes a provider `expected_goals` field on only
`{true_xg_rows}/{team_stat_rows}` sampled team-stat rows. This is real provider
xG evidence, but its `{(true_xg_rows / team_stat_rows if team_stat_rows else 0):.1%}`
sample coverage is far too sparse to support V2.2.

- True provider xG available: `{str(true_xg_rows > 0).lower()}` (sparse)
- True provider xG coverage sufficient: `false`
- Exploratory xG proxy possible: `{str(possible).lower()}`
- Statistical coverage sufficient at scale: `{str(broad_coverage_sufficient).lower()}`
- Complete sample coverage: `{complete_matches}/{sample}` (`{coverage:.1%}`)
- Formula: `0.05 * shots_total + 0.18 * shots_on_goal + 0.03 * corners`

The exploratory proxy is fragile: its coefficients are heuristic, it omits shot location
and chance quality, and its source statistics are post-match. The six-match
sample does not establish large-scale coverage. It must never be described as
true xG or used for the same match. The JSON report records
competition/season scope, per-team exploratory values, bias risks and the V2.2
recommendation.
""",
    )
    print(f"V2.1 xG proxy feasibility: possible={possible}, complete={complete_matches}/{sample}.")


if __name__ == "__main__":
    main()
