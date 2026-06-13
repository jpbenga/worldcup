"""Publish simple public-language explanations for V2.12 metrics."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import utc_now
from backend.scripts.v2_12_transparency_utils import VERSION, publish


def main() -> None:
    payload = {
        "version": VERSION,
        "generated_at": utc_now(),
        "glossary": {
            "score_exact": "Le score final correspond exactement au score le plus probable calculé avant le match.",
            "top_3": "Top-3 : le vrai score est dans les trois scores les plus probables calculés avant le match.",
            "top_5": "Top-5 : le vrai score est dans les cinq scores les plus probables calculés avant le match.",
            "score_modal": "Le score modal est le score individuel auquel le modèle attribue la probabilité la plus élevée.",
            "draw_no_bet": "Draw No Bet : pari sur une équipe où un match nul produit un remboursement.",
            "push": "Push : résultat remboursé, ni victoire ni défaite, utilisé notamment en Draw No Bet.",
            "coverage": "La couverture indique combien de matchs ou de sélections ont réellement pu être évalués.",
            "sample_size": "La taille d’échantillon est le nombre de matchs terminés utilisés pour lire les métriques.",
            "projection_alternative": "Projection alternative : scénario non actif qui aide à comparer une matrice moins conservatrice.",
        },
        "model_disclaimer": "Les probabilités sont des estimations pré-match figées, pas des certitudes ni des conseils.",
        "small_sample_warning": "Moins de dix matchs évalués : les taux peuvent bouger fortement après chaque résultat.",
        "active_vs_alternative_explanation": "La prédiction active reste la référence. La projection alternative non active sert uniquement à comparer un scénario moins conservateur.",
        "pre_match_freeze_explanation": "Une prédiction pré-match n’est jamais réécrite après le résultat. Le résultat réel et son évaluation sont ajoutés dans une couche séparée.",
    }
    publish(payload, "public_transparency_copy_v2_12.json")
    (ROOT / "docs" / "PUBLIC_TRANSPARENCY_COPY_V2_12.md").write_text("""# Public Transparency Copy V2.12

V2.12 uses short, plain-language explanations so public accountability remains readable. Exact score means the final result matches the single pre-match modal score. Top-3 and Top-5 mean the final score appears among the three or five highest-probability scores calculated before kickoff.

Draw No Bet is explained with pushes kept separate: a push is a refunded result, neither a win nor a loss. Coverage describes how many selections were evaluable, while sample size describes how many finished matches support the displayed rates.

The active forecast remains the reference. The alternative projection is a non-active scenario used only to compare a less conservative matrix. Every page warns that fewer than ten evaluated matches is a small sample and that frozen pre-match forecasts are never rewritten after results arrive.
""", encoding="utf-8")
    print("V2.12 public transparency copy built")


if __name__ == "__main__":
    main()
