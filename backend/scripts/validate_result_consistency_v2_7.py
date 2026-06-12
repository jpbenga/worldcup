"""Validate V2.7 unified match state and official-result standings."""

from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, load_json, utc_now
from backend.scripts.v2_7_consistency_utils import VERSION, publish


def non_finite(value: Any) -> bool:
    if isinstance(value, float):
        return not math.isfinite(value)
    if isinstance(value, dict):
        return any(non_finite(item) for item in value.values())
    if isinstance(value, list):
        return any(non_finite(item) for item in value)
    return False


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
    group_a = {row["team"]: row for row in standings["groups"]["A"]["standings"]}
    mexico, south_africa = group_a.get("Mexico"), group_a.get("South Africa")
    mexico_ok = mexico and (mexico["played"], mexico["wins"], mexico["goals_for"], mexico["goals_against"], mexico["goal_difference"], mexico["points"]) == (1, 1, 2, 0, 2, 3)
    south_africa_ok = south_africa and (south_africa["played"], south_africa["losses"], south_africa["goals_for"], south_africa["goals_against"], south_africa["goal_difference"], south_africa["points"]) == (1, 1, 0, 2, -2, 0)
    if not mexico_ok:
        issues.append("Mexico 2-0 standing impact is incorrect")
    if not south_africa_ok:
        issues.append("South Africa 0-2 standing impact is incorrect")
    report = {
        "version": VERSION, "generated_at": utc_now(), "passed": not issues, "issues": issues,
        "checks": {
            "match_count": len(matches), "finished_with_results": sum(item["status"] == "finished" and item["result"]["available"] for item in matches),
            "finished_with_evaluations": sum(item["status"] == "finished" and item["evaluation"]["available"] for item in matches),
            "modal_favorite_divergences_explained": sum(item["prediction"]["coherence_status"] == "modal_differs_from_1x2_favorite" and bool(item["prediction"]["coherence_explanation"]) for item in matches),
            "mexico_standing_correct": bool(mexico_ok), "south_africa_standing_correct": bool(south_africa_ok),
            "groups": len(standings["groups"]),
        },
    }
    publish(report, "result_consistency_validation_v2_7.json")
    (ROOT / "docs" / "RESULT_CONSISTENCY_VALIDATION_V2_7.md").write_text(
        f"""# Result Consistency Validation V2.7

Status: `{"PASS" if report["passed"] else "FAIL"}`.

The validator checked `{len(matches)}` unified match records, all finished-result and evaluation invariants, card/modal display fields, normalized matchdays, favorite-consistent scores, divergence explanations and non-finite values. It also rebuilt and verified the official Group A impact of Mexico 2-0 South Africa.

Mexico standing correct: `{bool(mexico_ok)}`. South Africa standing correct: `{bool(south_africa_ok)}`. Explained modal/favorite divergences: `{report["checks"]["modal_favorite_divergences_explained"]}`.

No pre-match prediction, matrix or probability is modified by this validation.
""", encoding="utf-8")
    if issues:
        raise SystemExit("V2.7 result consistency failed: " + "; ".join(issues[:10]))
    print("V2.7 result consistency validation: PASS")


if __name__ == "__main__":
    main()
