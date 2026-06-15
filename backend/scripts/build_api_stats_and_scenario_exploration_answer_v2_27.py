"""Build the consolidated French V2.27 exploration answer."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, utc_now, write_json

OUTPUT = "api_stats_and_scenario_exploration_answer_v2_27.json"


def publish(payload: dict[str, Any]) -> None:
    target = DATA_DIR / "generated" / OUTPUT
    write_json(payload, target)
    shutil.copy2(target, DATA_DIR / "snapshots" / OUTPUT)
    shutil.copy2(target, FRONTEND_DATA_DIR / OUTPUT)


def main() -> None:
    api = load_json(DATA_DIR / "generated" / "api_football_statistics_exploration_v2_27.json")
    catalog = load_json(DATA_DIR / "generated" / "germany_curacao_scenario_catalog_v2_27.json")
    readings = catalog["scenario_catalog"]["football_reading_scenarios"]
    payload = {
        "version": "v2.27",
        "generated_at": utc_now(),
        "answers": {
            "api_football_stats": {
                "short_answer": (
                    "API-Football fournit des statistiques post-match, événements, compositions et statistiques joueurs selon la couverture du match. "
                    "Ces données peuvent enrichir l'explication et, après audit historique, créer des features retardées; elles ne doivent jamais être injectées rétroactivement dans une prédiction pré-match."
                ),
                "usable_data": api["data_classification"],
                "not_usable_or_missing_data": api["not_usable_now"],
                "algorithm_opportunities": api["model_enrichment_opportunities"],
                "product_opportunities": ["Afficher une lecture de performance réelle après match.", "Préparer plus tard un mode live séparé."],
            },
            "germany_curacao_scenarios": {
                "short_answer": catalog["answer_for_user"],
                "scenario_summary": [{"label": row["label"], "probability": row["probability"], "definition": row["definition"]} for row in readings],
                "why_ui_was_insufficient": "Les top scores classent des cellules exactes individuellement et masquent la masse cumulée de familles footballistiques importantes.",
                "product_opportunity": "Ajouter une section Scénarios SimuAI combinant résultat probable, score recommandé, victoire large, buts, over/under, BTTS et clean sheet.",
            },
        },
        "recommended_next_steps": [
            "V2.28 — Unified Match Outcome Distribution & Scenario Families.",
            "Créer d'abord une couche d'explication post-match à partir des statistiques API disponibles.",
            "Mesurer ensuite la couverture historique et backtester des features retardées avant toute promotion modèle.",
            "Afficher les familles de scénarios sans modifier les prédictions actives.",
        ],
        "requires_engine_change": False,
        "requires_ui_change": True,
        "requires_data_pipeline_change": True,
    }
    publish(payload)
    print("V2.27 API stats and scenario answer: PASS")


if __name__ == "__main__":
    main()
