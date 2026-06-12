"""Build the per-match active versus non-active candidate comparison."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, load_json
from backend.scripts.v2_9_dual_matrix_utils import (
    CANDIDATE_VERSION, ENGINE, VERSION, expected_goals, markets, matrix_entries, publish, top_scores, utc_now,
)


def label(modal_changed: bool, total_delta: float, margin_delta: float, draw_delta: float) -> str:
    if margin_delta >= 0.02:
        return "favorite_margin_increased"
    if total_delta >= 0.04:
        return "more_goal_pressure"
    if draw_delta <= -0.02:
        return "draw_mass_reduced"
    if modal_changed:
        return "less_conservative"
    return "no_material_change" if abs(total_delta) + abs(margin_delta) < 0.02 else "unchanged"


def main() -> None:
    active_payload = load_json(DATA_DIR / "generated" / "worldcup_2026_predictions_release_candidate_v2_4.json")
    candidate_payload = load_json(DATA_DIR / "generated" / "worldcup_2026_predictions_score_matrix_candidate_v2_8.json")
    states = {row["match_id"]: row for row in load_json(DATA_DIR / "generated" / "worldcup_match_state_view_model_v2_7.json")["matches"]}
    candidates = {row["match_id"]: row for row in candidate_payload["matches"]}
    matches = []
    for active in active_payload["matches"]:
        candidate = candidates[active["match_id"]]
        state = states[active["match_id"]]
        favorite_side = "home" if active["probabilities"]["home_win"] >= active["probabilities"]["away_win"] else "away"
        favorite_probability = active["probabilities"][f"{favorite_side}_win"]
        active_entries = matrix_entries(active["score_matrix"])
        candidate_entries = matrix_entries(candidate["score_matrix"])
        active_markets, candidate_markets = markets(active_entries, favorite_side), markets(candidate_entries, favorite_side)
        active_xg, candidate_xg = expected_goals(active_entries), expected_goals(candidate_entries)
        active_top, candidate_top = top_scores(active_entries), top_scores(candidate_entries)
        total_delta = candidate_xg["total"] - active_xg["total"]
        margin_delta = candidate_markets["favorite_win_by_2_plus"] - active_markets["favorite_win_by_2_plus"]
        over_delta = candidate_markets["over_2_5"] - active_markets["over_2_5"]
        draw_delta = candidate_markets["draw"] - active_markets["draw"]
        modal_changed = active_top[0]["score"] != candidate_top[0]["score"]
        matches.append({
            "fixture_id": active.get("fixture_id"),
            "match_id": active["match_id"],
            "home_team": active["home_team"],
            "away_team": active["away_team"],
            "group": active["group"],
            "status": state["status"],
            "favorite": active[f"{favorite_side}_team"],
            "favorite_side": favorite_side,
            "favorite_probability": favorite_probability,
            "active": {"score_modal": active_top[0]["score"], "score_modal_probability": active_top[0]["probability"], "top_scores": active_top[:5], "top_10_scores": active_top, "expected_goals": active_xg, "markets": active_markets},
            "candidate": {"score_modal": candidate_top[0]["score"], "score_modal_probability": candidate_top[0]["probability"], "top_scores": candidate_top[:5], "top_10_scores": candidate_top, "expected_goals": candidate_xg, "markets": candidate_markets},
            "comparison": {
                "modal_changed": modal_changed,
                "modal_change": f"{active_top[0]['score']} -> {candidate_top[0]['score']}",
                "total_xg_delta": total_delta,
                "favorite_margin_delta": margin_delta,
                "over_2_5_delta": over_delta,
                "draw_mass_delta": draw_delta,
                "label": label(modal_changed, total_delta, margin_delta, draw_delta),
            },
            "product_labels": {"active": "Prédiction active", "candidate": "Projection alternative", "candidate_status": "Non active", "candidate_character": "Moins conservatrice"},
        })
    labels = Counter(row["comparison"]["label"] for row in matches)
    payload = {
        "generated_at": utc_now(), "version": VERSION, "engine_version": ENGINE, "candidate_version": CANDIDATE_VERSION,
        "candidate_status": "alternative_non_active", "active_predictions_replaced": False, "match_count": len(matches),
        "modal_changed_count": sum(row["comparison"]["modal_changed"] for row in matches),
        "label_distribution": dict(labels), "matches": matches,
    }
    publish(payload, "dual_matrix_comparison_v2_9.json")
    spain = next(row for row in matches if row["home_team"] == "Spain" and "Cape Verde" in row["away_team"])
    (ROOT / "docs" / "DUAL_MATRIX_COMPARISON_V2_9.md").write_text(f"""# Dual Matrix Comparison V2.9

V2.9 compares `{len(matches)}` active score matrices with the V2.8 alternative candidate. `{payload['modal_changed_count']}` modal scores change. The active forecast remains official; the candidate is labelled **Projection alternative**, **Non active**, and **Moins conservatrice**.

## Spain vs Cape Verde Islands

- Active modal: `{spain['active']['score_modal']}` at `{spain['active']['score_modal_probability']:.1%}`
- Candidate modal: `{spain['candidate']['score_modal']}` at `{spain['candidate']['score_modal_probability']:.1%}`
- Active top 10: `{spain['active']['top_10_scores']}`
- Candidate top 10: `{spain['candidate']['top_10_scores']}`
- Over 2.5 delta: `{spain['comparison']['over_2_5_delta']:+.1%}`
- Spain 2+ goals delta: `{spain['candidate']['markets']['home_scores_2_plus'] - spain['active']['markets']['home_scores_2_plus']:+.1%}`
- Spain by 2+ delta: `{spain['comparison']['favorite_margin_delta']:+.1%}`

La prédiction active reste la référence officielle. La projection candidate montre une lecture moins conservatrice du même rapport de force.

The candidate primarily increases favorite margin and goal pressure. It does not rewrite the frozen hybrid 1X2 forecast or claim that Spain is now officially predicted 2-0.
""", encoding="utf-8")
    print(json.dumps({"matches": len(matches), "modal_changes": payload["modal_changed_count"], "labels": dict(labels)}))


if __name__ == "__main__":
    main()
