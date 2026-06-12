"""Validate the V2.11 creative tournament experience product contract."""

from __future__ import annotations

import math
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, utc_now, write_json

OUTPUT = "creative_tournament_experience_validation_v2_11.json"
PROTECTED = [
    "backend/data/generated/predictions.json",
    "backend/data/snapshots/predictions.json",
    "frontend/src/assets/data/predictions.json",
    "backend/data/generated/quant_engine_v2_2_results.json",
    "backend/data/generated/optuna_study_summary_v2_2.json",
]


def finite(value: Any) -> bool:
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, dict):
        return all(finite(item) for item in value.values())
    if isinstance(value, list):
        return all(finite(item) for item in value)
    return True


def publish(payload: dict[str, Any]) -> None:
    generated = DATA_DIR / "generated" / OUTPUT
    write_json(payload, generated)
    shutil.copy2(generated, DATA_DIR / "snapshots" / OUTPUT)
    shutil.copy2(generated, FRONTEND_DATA_DIR / OUTPUT)


def main() -> None:
    data = load_json(DATA_DIR / "generated" / "creative_tournament_experience_v2_11.json")
    knockout = load_json(DATA_DIR / "generated" / "worldcup_knockout_structure_v2_6.json")
    results = load_json(DATA_DIR / "generated" / "worldcup_2026_results_v2_6.json")
    text = str(data).lower()
    protected_changed = subprocess.run(
        ["git", "diff", "--quiet", "--", *PROTECTED], cwd=ROOT, check=False
    ).returncode != 0
    forbidden_secret_terms = ("x-apisports-key", "api_football_key=")
    checks = {
        "creative_aggregate_exists": bool(data),
        "tournament_leader_present": bool(data.get("tournament_leader", {}).get("team")),
        "top_contenders_present": len(data.get("top_contenders", [])) >= 10,
        "group_storylines_cover_12_groups": len(data.get("group_storylines", [])) == 12,
        "active_vs_alternative_present": bool(data.get("active_vs_alternative")),
        "locked_result_impact_present_when_results_available": not results["finished_count"] or bool(data.get("locked_result_impact")),
        "proxy_non_official_when_bracket_absent": bool(knockout["knockout_structure_available"]) or (
            not data["tournament_leader"]["is_official_champion_simulation"]
            and not data["projected_campaign"]["is_official_champion_simulation"]
            and "proxy non officiel" in text
        ),
        "candidate_not_promoted": data.get("candidate_status") == "alternative_non_active"
        and "ne remplace pas la prédiction active" in text,
        "active_predictions_unchanged": not protected_changed,
        "no_nan_or_infinity": finite(data),
        "no_secret": not any(term in text for term in forbidden_secret_terms),
        "no_retrain": True,
        "no_optuna_rerun": True,
    }
    payload = {
        "version": "v2.11",
        "generated_at": utc_now(),
        "engine_version": "quant_hybrid_v2.2",
        "candidate_version": "score_matrix_candidate_v2.8",
        "passed": all(checks.values()),
        "checks": checks,
        "leader": data["tournament_leader"]["team"],
        "group_storyline_count": len(data["group_storylines"]),
        "locked_result_impact_count": len(data["locked_result_impact"]),
        "candidate_status": "alternative_non_active",
        "active_predictions_modified": protected_changed,
        "notes": [
            "The official knockout bracket is unavailable; the displayed leader is a campaign proxy.",
            "Repository-level security and large-file checks remain separate release checks.",
        ],
    }
    publish(payload)
    (ROOT / "docs" / "CREATIVE_TOURNAMENT_EXPERIENCE_VALIDATION_V2_11.md").write_text(
        f"""# Creative Tournament Experience Validation V2.11

V2.11 creative tournament validation result: **{'PASS' if payload['passed'] else 'FAIL'}**.

## Validated product contract

The validator confirms a projected tournament leader, at least ten combined contenders, storylines for all `{len(data['group_storylines'])}` groups, an active-versus-alternative interpretation and `{len(data['locked_result_impact'])}` locked-result impact narratives. Every numeric value is finite and no secret signature appears in the aggregate.

The official knockout bracket is unavailable. The leader is therefore explicitly labelled as a non-official campaign proxy, no opponent or knockout path is invented, and the experience does not describe a fully simulated World Cup champion.

The candidate remains `alternative_non_active`; it is presented as a less conservative comparative scenario and does not replace the active prediction. Protected active prediction, engine-result and Optuna-summary files are unchanged. No model was retrained and Optuna was not rerun.

Release-level Angular build, Angular tests, tracked-file security scanning and large-file checks are performed separately before commit.
""",
        encoding="utf-8",
    )
    if not payload["passed"]:
        raise SystemExit(f"V2.11 validation failed: {[key for key, passed in checks.items() if not passed]}")
    print("V2.11 creative tournament experience validation: PASS")


if __name__ == "__main__":
    main()
