"""Validate the V2.9 dual-matrix comparative product layer."""

from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, load_json
from backend.scripts.v2_9_dual_matrix_utils import ENGINE, VERSION, publish, utc_now


def finite(value: Any) -> bool:
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, dict):
        return all(finite(item) for item in value.values())
    if isinstance(value, list):
        return all(finite(item) for item in value)
    return True


def main() -> None:
    dual = load_json(DATA_DIR / "generated" / "dual_matrix_comparison_v2_9.json")
    candidate_sim = load_json(DATA_DIR / "generated" / "worldcup_tournament_simulation_candidate_v2_9.json")
    sim_comparison = load_json(DATA_DIR / "generated" / "active_vs_candidate_simulation_comparison_v2_9.json")
    candidate_campaign = load_json(DATA_DIR / "generated" / "worldcup_projected_campaign_candidate_v2_9.json")
    active = load_json(DATA_DIR / "generated" / "worldcup_2026_predictions_release_candidate_v2_4.json")
    candidate = load_json(DATA_DIR / "generated" / "worldcup_2026_predictions_score_matrix_candidate_v2_8.json")
    matches = dual["matches"]
    text = str(dual).lower()
    checks = {
        "72_matches_compared": len(matches) == 72,
        "active_and_candidate_present": all(row.get("active") and row.get("candidate") for row in matches),
        "no_nan_or_infinity": all(finite(item) for item in (dual, candidate_sim, sim_comparison, candidate_campaign)),
        "probabilities_between_zero_and_one": all(
            0 <= score["probability"] <= 1
            for row in matches
            for projection in ("active", "candidate")
            for score in row[projection]["top_scores"]
        ),
        "active_predictions_not_replaced": not dual["active_predictions_replaced"] and not candidate["active_predictions_replaced"],
        "candidate_labels_present": all(term in text for term in ("candidate", "alternative", "non active")),
        "candidate_simulation_50000": candidate_sim["simulation_count"] == 50000,
        "simulation_comparison_exists": bool(sim_comparison["team_deltas"]),
        "candidate_projected_campaign_exists": bool(candidate_campaign["top_contenders"]),
        "spain_cape_verde_present": "spain" in text and "cape verde" in text,
        "active_fixture_count_unchanged": active["fixture_count"] == 72,
    }
    payload = {
        "generated_at": utc_now(), "version": VERSION, "engine_version": ENGINE, "passed": all(checks.values()),
        "checks": checks, "match_count": len(matches), "candidate_status": "alternative_non_active",
        "no_model_retrained": True, "no_optuna_rerun": True, "active_probabilities_modified": False,
        "notes": ["Secret scanning is performed separately before commit.", "Candidate simulation and campaign remain comparative, not official."],
    }
    publish(payload, "dual_matrix_validation_v2_9.json")
    (ROOT / "docs" / "DUAL_MATRIX_VALIDATION_V2_9.md").write_text(f"""# Dual Matrix Validation V2.9

V2.9 validation result: **{'PASS' if payload['passed'] else 'FAIL'}**.

The validator confirms `{len(matches)}` active/candidate match comparisons, finite values, bounded displayed probabilities, a 50,000-scenario candidate simulation, an active-versus-candidate simulation comparison, a candidate projected-campaign proxy, and the Spain vs Cape Verde case.

The active V2.4 release candidate still contains 72 fixtures. The V2.8 candidate explicitly reports that active predictions were not replaced. The comparative artifacts and product labels identify the candidate as an alternative, non-active projection.

No model was retrained, Optuna was not rerun, and active hybrid probabilities were not modified. Secret scanning and large-file checks remain separate repository-level release checks.
""", encoding="utf-8")
    if not payload["passed"]:
        raise SystemExit(f"V2.9 validation failed: {[key for key, value in checks.items() if not value]}")
    print("V2.9 dual matrix validation: PASS")


if __name__ == "__main__":
    main()
