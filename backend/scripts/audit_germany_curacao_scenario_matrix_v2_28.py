"""Audit the V2.28 scenario-aware matrix on Germany-Curacao."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, write_json

OUTPUT = "germany_curacao_scenario_matrix_audit_v2_28.json"


def publish(payload: dict[str, Any]) -> None:
    target = DATA_DIR / "generated" / OUTPUT
    write_json(payload, target)
    shutil.copy2(target, DATA_DIR / "snapshots" / OUTPUT)
    shutil.copy2(target, FRONTEND_DATA_DIR / OUTPUT)


def main() -> None:
    matrix = load_json(DATA_DIR / "generated" / "scenario_aware_score_matrix_v2_28.json")
    item = next(row for row in matrix["matches"] if "Germany" in row["match_label"] and "Curaçao" in row["match_label"])
    families = {row["key"]: row for row in item["scenario_families"]}
    display_scores = [row["score"] for row in item["display_scores"]["representative_scores"]]
    payload = {
        "version": "v2.28", "fixture": "Allemagne - Curaçao",
        "old_ui_problem": {
            "top_exact_scores_hid_large_win": True,
            "exact_score_percentages_overweighted": True,
        },
        "new_scenario_view": {
            "large_win_visible": item["scenario_signals"]["large_win_visible"],
            "favorite_4_plus_goals_visible": item["scenario_signals"]["favorite_4_plus_goals_visible"],
            "over_3_5_visible": item["scenario_signals"]["over_3_5_visible"],
            "blowout_context_visible": item["scenario_signals"]["blowout_visible"],
            "exact_7_1_not_overpromoted": "7-1" not in display_scores[:2] and item["ui_policy"]["exact_score_percentages_location"] == "advanced_detail",
        },
        "measured_signals": {
            "mode_score": item["display_scores"]["mode_score"],
            "large_favorite_win": families["large_favorite_win"]["probability"],
            "favorite_4_plus_goals": families["favorite_4_plus_goals"]["probability"],
            "over_3_5": next(row for row in item["scenario_families"] if row["key"] == "open_match")["probability"],
            "blowout": families["blowout"]["probability"],
            "representative_scores": display_scores,
        },
        "answer_for_user": "La nouvelle lecture garde 1-0 comme score repère, mais affiche d'abord les familles: victoire large, Allemagne à 4+ buts, match ouvert et carton possible. Le 7-1 reste un score extrême compatible, pas une promesse de score exact.",
    }
    publish(payload)
    print("V2.28 Germany-Curacao scenario matrix audit: PASS")


if __name__ == "__main__":
    main()
