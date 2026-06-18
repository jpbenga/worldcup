"""Validate V2.7 unified match state and official-result standings."""

from __future__ import annotations

import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, load_json, utc_now
from backend.scripts.v2_7_consistency_utils import VERSION, publish


def blank(team: str) -> dict[str, Any]:
    return {
        "team": team,
        "played": 0,
        "wins": 0,
        "draws": 0,
        "losses": 0,
        "goals_for": 0,
        "goals_against": 0,
        "goal_difference": 0,
        "points": 0,
        "rank": 0,
    }


def non_finite(value: Any) -> bool:
    if isinstance(value, float):
        return not math.isfinite(value)
    if isinstance(value, dict):
        return any(non_finite(item) for item in value.values())
    if isinstance(value, list):
        return any(non_finite(item) for item in value)
    return False


def expected_standings(matches: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    tables: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for item in matches:
        group = item["standings_impact"]["group"]
        for team in (item["home_team"], item["away_team"]):
            tables[group].setdefault(team, blank(team))
    for item in matches:
        result = item.get("result", {})
        if item.get("status") != "finished" or not result.get("available"):
            continue
        group = item["standings_impact"]["group"]
        home, away = tables[group][item["home_team"]], tables[group][item["away_team"]]
        hg, ag = int(result["home_goals"]), int(result["away_goals"])
        home["played"] += 1
        away["played"] += 1
        home["goals_for"] += hg
        home["goals_against"] += ag
        away["goals_for"] += ag
        away["goals_against"] += hg
        if hg > ag:
            home["wins"] += 1
            home["points"] += 3
            away["losses"] += 1
        elif ag > hg:
            away["wins"] += 1
            away["points"] += 3
            home["losses"] += 1
        else:
            home["draws"] += 1
            away["draws"] += 1
            home["points"] += 1
            away["points"] += 1
    expected = {}
    for group, rows in tables.items():
        for row in rows.values():
            row["goal_difference"] = row["goals_for"] - row["goals_against"]
        ordered = sorted(rows.values(), key=lambda row: (-row["points"], -row["goal_difference"], -row["goals_for"], row["team"]))
        for rank, row in enumerate(ordered, 1):
            row["rank"] = rank
        expected[group] = ordered
    return expected


def main() -> None:
    view = load_json(DATA_DIR / "generated" / "worldcup_match_state_view_model_v2_7.json")
    standings = load_json(DATA_DIR / "generated" / "worldcup_live_group_standings_v2_7.json")
    issues = []
    matches = view.get("matches", [])
    if len(matches) != 72:
        issues.append(f"Expected 72 matches, found {len(matches)}")
    for item in matches:
        prediction, result, evaluation, display = item.get("prediction", {}), item.get("result", {}), item.get("evaluation", {}), item.get("display", {})
        for field in ("status", "prediction", "result", "evaluation", "display", "matchday_label"):
            if field not in item:
                issues.append(f"{item.get('match_id')} missing {field}")
        if item.get("status") == "finished" and not result.get("available"):
            issues.append(f"{item.get('match_id')} finished without result")
        if item.get("status") == "finished" and not evaluation.get("available"):
            issues.append(f"{item.get('match_id')} finished without evaluation")
        if item.get("status") != "finished" and evaluation.get("available"):
            issues.append(f"{item.get('match_id')} non-finished with final evaluation")
        if item.get("status") == "finished" and display.get("modal_status_label") == "À venir":
            issues.append(f"{item.get('match_id')} finished but displayed upcoming")
        if not prediction.get("score_consistent_with_favorite"):
            issues.append(f"{item.get('match_id')} missing favorite-consistent score")
        if prediction.get("coherence_status") == "modal_differs_from_1x2_favorite" and not prediction.get("coherence_explanation"):
            issues.append(f"{item.get('match_id')} missing coherence explanation")
        if non_finite(item):
            issues.append(f"{item.get('match_id')} contains non-finite value")
    expected_groups = expected_standings(matches)
    standing_mismatches = []
    for group, expected_rows in sorted(expected_groups.items()):
        actual_rows = standings["groups"].get(group, {}).get("standings", [])
        actual_by_team = {row["team"]: row for row in actual_rows}
        for expected in expected_rows:
            actual = actual_by_team.get(expected["team"])
            comparable = {key: actual.get(key) for key in expected} if actual else None
            if comparable != expected:
                standing_mismatches.append({
                    "group": group,
                    "team": expected["team"],
                    "expected": expected,
                    "actual": comparable,
                })
    if standing_mismatches:
        issues.append(f"Live standings mismatch for {len(standing_mismatches)} team(s)")
    report = {
        "version": VERSION, "generated_at": utc_now(), "passed": not issues, "issues": issues,
        "checks": {
            "match_count": len(matches), "finished_with_results": sum(item["status"] == "finished" and item["result"]["available"] for item in matches),
            "finished_with_evaluations": sum(item["status"] == "finished" and item["evaluation"]["available"] for item in matches),
            "modal_favorite_divergences_explained": sum(item["prediction"]["coherence_status"] == "modal_differs_from_1x2_favorite" and bool(item["prediction"]["coherence_explanation"]) for item in matches),
            "live_standings_match_recomputed_results": not standing_mismatches,
            "standing_mismatches": standing_mismatches[:20],
            "groups": len(standings["groups"]),
        },
    }
    publish(report, "result_consistency_validation_v2_7.json")
    (ROOT / "docs" / "RESULT_CONSISTENCY_VALIDATION_V2_7.md").write_text(
        f"""# Result Consistency Validation V2.7

Status: `{"PASS" if report["passed"] else "FAIL"}`.

The validator checked `{len(matches)}` unified match records, all finished-result and evaluation invariants, card/modal display fields, normalized matchdays, favorite-consistent scores, divergence explanations and non-finite values. It also rebuilt all live group standings from finished official results and compared them against the published standings artifact.

Live standings match recomputed results: `{not standing_mismatches}`. Standing mismatches: `{standing_mismatches[:5]}`. Explained modal/favorite divergences: `{report["checks"]["modal_favorite_divergences_explained"]}`.

No pre-match prediction, matrix or probability is modified by this validation.
""", encoding="utf-8")
    if issues:
        raise SystemExit("V2.7 result consistency failed: " + "; ".join(issues[:10]))
    print("V2.7 result consistency validation: PASS")


if __name__ == "__main__":
    main()
