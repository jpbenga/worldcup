"""Build the consolidated French answer for the V2.26 coherence audit."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, utc_now, write_json

OUTPUT = "match_matrix_and_simulation_coherence_answer_v2_26.json"


def publish(payload: dict[str, Any]) -> None:
    target = DATA_DIR / "generated" / OUTPUT
    write_json(payload, target)
    shutil.copy2(target, DATA_DIR / "snapshots" / OUTPUT)
    shutil.copy2(target, FRONTEND_DATA_DIR / OUTPUT)


def main() -> None:
    spain = load_json(DATA_DIR / "generated" / "real_result_impact_audit_v2_26.json")
    germany = load_json(DATA_DIR / "generated" / "score_matrix_tail_risk_audit_v2_26.json")
    architecture = load_json(DATA_DIR / "generated" / "match_matrix_vs_tournament_simulation_audit_v2_26.json")
    payload = {
        "version": "v2.26",
        "generated_at": utc_now(),
        "answers": {
            "spain_0_0_cape_verde": {
                "short_answer": spain["answer_for_user"],
                "technical_answer": spain["diagnosis"]["explanation"],
                "product_conclusion": "Séparer explicitement impact du score réel et impact de la performance; le second est actuellement indisponible.",
            },
            "germany_7_1_large_score": {
                "short_answer": germany["answer_for_user"],
                "technical_answer": germany["diagnosis"]["explanation"],
                "product_conclusion": "Afficher la masse de victoire large et de buts 4+ en complément du score recommandé et des top scores.",
            },
            "score_matrix_not_used_by_simulation": {
                "short_answer": architecture["answer_for_user"],
                "technical_answer": architecture["coherence_diagnosis"]["explanation"],
                "product_conclusion": "Planifier une distribution de match unifiée comme priorité haute, sans modifier le moteur dans cet audit.",
            },
        },
        "recommended_next_steps": [
            "Créer une distribution de match unifiée réutilisable pour les confrontations arbitraires.",
            "Ajouter un signal Risque de large victoire et les masses victoire par 3+/4+ et équipe à 4+ buts.",
            "Conserver score recommandé et top scores, mais rendre visible la queue de distribution.",
            "Ajouter ultérieurement un module de performance post-match si tirs, possession ou xG deviennent disponibles.",
        ],
        "requires_engine_change": True,
        "requires_ui_change": True,
        "requires_data_change": True,
        "changes_applied_in_v2_26": "Audit and documentation only; no public engine, active prediction or functional frontend change.",
    }
    publish(payload)
    print("V2.26 consolidated coherence answer: PASS")


if __name__ == "__main__":
    main()
