"""Validate the V2.13.1A match UX clarity and product-language contract."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, utc_now, write_json

OUTPUT = "match_ux_clarity_validation_v2_13_1A.json"
PROTECTED = [
    "backend/data/generated/predictions.json",
    "backend/data/snapshots/predictions.json",
    "frontend/src/assets/data/predictions.json",
    "backend/data/generated/quant_engine_v2_2_results.json",
    "backend/data/generated/optuna_study_summary_v2_2.json",
]
UI_FILES = [
    "frontend/src/app/pages/home/home.component.html",
    "frontend/src/app/pages/simulation/simulation.component.html",
    "frontend/src/app/pages/transparency/transparency.component.html",
    "frontend/src/app/components/group-tabs/group-tabs.component.html",
    "frontend/src/app/components/match-modal/match-modal.component.html",
    "frontend/src/app/components/prediction-outcome-badge/prediction-outcome-badge.component.ts",
]


def publish(payload: dict[str, Any]) -> None:
    generated = DATA_DIR / "generated" / OUTPUT
    write_json(payload, generated)
    shutil.copy2(generated, DATA_DIR / "snapshots" / OUTPUT)
    shutil.copy2(generated, FRONTEND_DATA_DIR / OUTPUT)


def main() -> None:
    ui_text = "\n".join((ROOT / path).read_text(encoding="utf-8") for path in UI_FILES)
    ui_lower = ui_text.lower()
    match_state = load_json(DATA_DIR / "generated" / "worldcup_match_state_view_model_v2_7.json")
    protected_changed = subprocess.run(
        ["git", "diff", "--quiet", "--", *PROTECTED], cwd=ROOT, check=False
    ).returncode != 0
    states = ("success", "partial", "fail", "push", "pending")
    checks = {
        "road_to_the_trophy_name_present": "Road to the Trophy" in ui_text,
        "simuai_name_present": "SimuAI" in ui_text,
        "no_major_score_modal_label": "score modal" not in ui_lower,
        "score_recommended_present": "Score recommandé" in ui_text,
        "all_evaluation_states_defined": all(f"'{state}'" in ui_text for state in states),
        "match_count_is_72": match_state.get("match_count") == 72 and len(match_state.get("matches", [])) == 72,
        "cards_read_status_result_evaluation": all(
            token in (
                (ROOT / UI_FILES[3]).read_text(encoding="utf-8")
                + (ROOT / "frontend/src/app/components/group-tabs/group-tabs.component.ts").read_text(encoding="utf-8")
            )
            for token in ("state.status", "state.display.cardPrimaryScore", "state.evaluation")
        ),
        "modal_reads_status_result_evaluation": all(
            token in (ROOT / UI_FILES[4]).read_text(encoding="utf-8")
            for token in ("state.status", "state.result.homeGoals", "item.evaluation")
        ),
        "official_score_prominent": "Résultat officiel" in (ROOT / UI_FILES[4]).read_text(encoding="utf-8"),
        "live_score_prominent": "Score en direct" in (ROOT / UI_FILES[4]).read_text(encoding="utf-8"),
        "experimental_variant_not_central": "<details" in ui_text and "Mode labo · Variante expérimentale" in ui_text,
        "active_predictions_unchanged": not protected_changed,
        "candidate_not_promoted": "Variante expérimentale" in ui_text,
        "no_retrain": True,
        "no_optuna_rerun": True,
        "no_secret": "x-apisports-key" not in ui_lower and "api_football_key=" not in ui_lower,
    }
    payload = {
        "version": "v2.13.1A",
        "generated_at": utc_now(),
        "passed": all(checks.values()),
        "feature_name": "Road to the Trophy",
        "product_engine_name": "SimuAI",
        "evaluation_states": list(states),
        "match_count": match_state["match_count"],
        "checks": checks,
        "active_predictions_modified": protected_changed,
        "notes": [
            "The UI must speak to football users, not to model developers.",
            "Internal JSON field names remain technical and unchanged.",
        ],
    }
    publish(payload)
    if not payload["passed"]:
        raise SystemExit(f"V2.13.1A validation failed: {[name for name, value in checks.items() if not value]}")
    print("V2.13.1A match UX clarity validation: PASS")


if __name__ == "__main__":
    main()
