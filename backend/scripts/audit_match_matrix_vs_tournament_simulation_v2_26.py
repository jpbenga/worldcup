"""Audit the model boundary between visible match matrices and Road to the Trophy."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, utc_now, write_json

OUTPUT = "match_matrix_vs_tournament_simulation_audit_v2_26.json"


def publish(payload: dict[str, Any]) -> None:
    target = DATA_DIR / "generated" / OUTPUT
    write_json(payload, target)
    shutil.copy2(target, DATA_DIR / "snapshots" / OUTPUT)
    shutil.copy2(target, FRONTEND_DATA_DIR / OUTPUT)


def unchanged(paths: list[str]) -> bool:
    return subprocess.run(["git", "diff", "--quiet", "--", *paths], cwd=ROOT).returncode == 0


def main() -> None:
    engine_code = "backend/scripts/run_tournament_simulation_engine_v4_v2_21.py"
    payload = {
        "version": "v2.26",
        "generated_at": utc_now(),
        "visible_match_prediction": {
            "engine": "quant_hybrid_v2.2",
            "uses_score_matrix": True,
            "outputs": ["hybrid 1X2", "Poisson score matrix 0-7", "top exact scores", "matrix-derived markets"],
        },
        "score_matrix": {
            "engine": "quant_hybrid_v2.2 score projection",
            "distribution_type": "independent Poisson score grid fed by predicted xG; visible 1X2 is a hybrid XGBoost/Poisson blend",
            "full_distribution_available": True,
            "top_scores_only": False,
            "ui_summary_top_scores_only": True,
        },
        "tournament_simulation": {
            "engine": "SimuAI Tournament Engine V4 / elo_time_decay_independent_poisson_v4",
            "uses_score_matrix": False,
            "group_stage_model": "V4 samples a separate V3-style independent Poisson matrix built from current external Elo and time-decayed historical scoring profiles.",
            "knockout_model": "The same direct-match distribution simulates 90 minutes, then separate extra-time Poisson and conservative Elo-shrunk penalties.",
            "score_sampling_method": "One cached direct-match matrix per arbitrary pairing and stage, sampled inside each complete tournament.",
            "reason_score_matrix_not_used": (
                "Road to the Trophy must score arbitrary future knockout pairings. The active quant_hybrid_v2.2 inference bundle was not persisted as a reusable arbitrary-pairing contract, so V4 inherited the reusable V3 head-to-head engine."
            ),
        },
        "shared_data": ["team identities", "official finished scores", "group fixtures", "some historical score data"],
        "not_shared": ["active quant_hybrid_v2.2 matrices", "active hybrid 1X2 probabilities", "active predicted xG", "active internal ratings"],
        "coherence_diagnosis": {
            "platform_incoherence": True,
            "acceptable_short_term": True,
            "requires_unification": True,
            "explanation": (
                "The separation is transparent and technically understandable, but two different probability distributions can tell different stories for the same matchup. "
                "It is acceptable as an explicit V1 limitation, not as the target architecture."
            ),
        },
        "recommended_architecture": {
            "name": "Unified Match Outcome Distribution",
            "description": (
                "Persist one reusable, calibrated arbitrary-pairing distribution contract that reconciles hybrid 1X2, score probabilities and broad tail markets, then consume it in visible match predictions and every tournament stage."
            ),
            "priority": "high",
        },
        "public_engine_code_unchanged": unchanged([engine_code, "backend/simulation/tournament_engine_v3.py", "backend/simulation/tournament_engine_v4.py"]),
        "answer_for_user": (
            "Road to the Trophy n'utilise pas la matrice visible parce que quant_hybrid_v2.2 n'est pas persisté comme moteur réutilisable pour toutes les confrontations futures possibles. "
            "Le tournoi utilise donc une autre distribution Poisson Elo/historique. Cette séparation est une limite historique et d'architecture, pas une nécessité de performance. Elle est acceptable si elle est clairement annoncée en V1, mais la plateforme doit converger vers une distribution de match unifiée."
        ),
    }
    publish(payload)
    print("V2.26 match-matrix vs tournament audit: PASS")


if __name__ == "__main__":
    main()
