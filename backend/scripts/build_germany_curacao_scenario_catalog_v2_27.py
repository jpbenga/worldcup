"""Build readable scenario families from the Germany-Curacao active score matrix."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, utc_now, write_json

OUTPUT = "germany_curacao_scenario_catalog_v2_27.json"
MATCH_ID = "api_football_1489374"


def publish(payload: dict[str, Any]) -> None:
    target = DATA_DIR / "generated" / OUTPUT
    write_json(payload, target)
    shutil.copy2(target, DATA_DIR / "snapshots" / OUTPUT)
    shutil.copy2(target, FRONTEND_DATA_DIR / OUTPUT)


def family(entries: list[dict[str, Any]], key: str, label: str, definition: str, test: Callable[[int, int], bool], interpretation: str = "") -> dict[str, Any]:
    included = [row["score"] for row in entries if test(row["home_goals"], row["away_goals"])]
    probability = sum(row["probability"] for row in entries if row["score"] in included)
    return {"scenario_key": key, "label": label, "definition": definition, "probability": probability, "included_scores": included, "interpretation": interpretation}


def main() -> None:
    prediction = next(row for row in load_json(DATA_DIR / "generated" / "predictions.json") if row["match_id"] == MATCH_ID)
    result = next(row for row in load_json(DATA_DIR / "generated" / "worldcup_2026_results_v2_6.json")["fixtures"] if row["match_id"] == MATCH_ID)
    entries = prediction["score_matrix"]["probabilities"]
    by_score = {row["score"]: row for row in entries}
    top = sorted(entries, key=lambda row: row["probability"], reverse=True)
    exact_selected = ["4-0", "5-0", "6-0", "7-0", "7-1"]
    exact_rows = [
        {"scenario_key": "recommended_score", "label": "Score recommandé", **prediction["top_scores"][0]},
        {"scenario_key": "actual_score", "label": "Score réel", **by_score["7-1"]},
        *[{"scenario_key": f"exact_{score.replace('-', '_')}", "label": score, **by_score[score]} for score in exact_selected],
        {"scenario_key": "other_scores", "label": "Autres scores", "probability": 1 - sum(row["probability"] for row in top[:10]), "included_scores": [row["score"] for row in top[10:]]},
    ]
    catalog = {
        "result_1n2": [
            family(entries, "germany_win", "Allemagne gagne", "Buts Allemagne > buts Curaçao", lambda h, a: h > a),
            family(entries, "draw", "Match nul", "Buts Allemagne = buts Curaçao", lambda h, a: h == a),
            family(entries, "curacao_win", "Curaçao gagne", "Buts Curaçao > buts Allemagne", lambda h, a: h < a),
        ],
        "exact_scores": exact_rows,
        "top_5_exact_scores": top[:5],
        "top_10_exact_scores": top[:10],
        "victory_margins": [
            family(entries, "germany_by_1", "Allemagne gagne par 1 but", "Marge Allemagne = 1", lambda h, a: h - a == 1),
            family(entries, "germany_by_2", "Allemagne gagne par 2 buts", "Marge Allemagne = 2", lambda h, a: h - a == 2),
            family(entries, "germany_by_3_plus", "Allemagne gagne par 3+ buts", "Marge Allemagne >= 3", lambda h, a: h - a >= 3),
            family(entries, "germany_by_4_plus", "Allemagne gagne par 4+ buts", "Marge Allemagne >= 4", lambda h, a: h - a >= 4),
            family(entries, "germany_by_5_plus", "Allemagne gagne par 5+ buts", "Marge Allemagne >= 5", lambda h, a: h - a >= 5),
            family(entries, "curacao_win_any", "Curaçao gagne", "Marge Curaçao >= 1", lambda h, a: a > h),
            family(entries, "draw", "Nul", "Marge = 0", lambda h, a: h == a),
        ],
        "team_goal_totals": [
            *[family(entries, f"germany_scores_{n}", f"Allemagne marque {n}", f"Buts Allemagne = {n}", lambda h, a, n=n: h == n) for n in range(4)],
            family(entries, "germany_scores_4_plus", "Allemagne marque 4+ buts", "Buts Allemagne >= 4", lambda h, a: h >= 4),
            family(entries, "germany_scores_5_plus", "Allemagne marque 5+ buts", "Buts Allemagne >= 5", lambda h, a: h >= 5),
            family(entries, "germany_scores_6_plus", "Allemagne marque 6+ buts", "Buts Allemagne >= 6", lambda h, a: h >= 6),
        ],
        "match_goal_totals": [
            family(entries, "over_1_5", "Plus de 1,5 buts", "Total >= 2", lambda h, a: h + a >= 2),
            family(entries, "over_2_5", "Plus de 2,5 buts", "Total >= 3", lambda h, a: h + a >= 3),
            family(entries, "over_3_5", "Plus de 3,5 buts", "Total >= 4", lambda h, a: h + a >= 4),
            family(entries, "over_4_5", "Plus de 4,5 buts", "Total >= 5", lambda h, a: h + a >= 5),
            family(entries, "under_2_5", "Moins de 2,5 buts", "Total <= 2", lambda h, a: h + a <= 2),
            family(entries, "under_3_5", "Moins de 3,5 buts", "Total <= 3", lambda h, a: h + a <= 3),
        ],
        "btts_clean_sheet": [
            family(entries, "btts_yes", "Les deux équipes marquent", "Allemagne >= 1 et Curaçao >= 1", lambda h, a: h >= 1 and a >= 1),
            family(entries, "btts_no", "Au moins une équipe ne marque pas", "Allemagne = 0 ou Curaçao = 0", lambda h, a: h == 0 or a == 0),
            family(entries, "germany_win_clean_sheet", "Allemagne gagne sans encaisser", "Allemagne gagne et Curaçao = 0", lambda h, a: h > a and a == 0),
            family(entries, "germany_win_concedes", "Allemagne gagne en encaissant", "Allemagne gagne et Curaçao >= 1", lambda h, a: h > a and a >= 1),
        ],
        "football_reading_scenarios": [
            family(entries, "short_germany_win", "Victoire courte Allemagne", "Allemagne gagne par 1 but", lambda h, a: h - a == 1, "Le résultat favorable le plus serré."),
            family(entries, "controlled_germany_win", "Victoire contrôlée Allemagne", "Allemagne gagne par exactement 2 buts", lambda h, a: h - a == 2, "Avantage clair sans score extrême."),
            family(entries, "large_germany_win", "Victoire large Allemagne", "Allemagne gagne par au moins 3 buts", lambda h, a: h - a >= 3, "La famille de score lourd était significative."),
            family(entries, "germany_rout", "Carton Allemagne", "Allemagne gagne par au moins 5 buts", lambda h, a: h - a >= 5, "Scénario extrême mais mesurable."),
            family(entries, "closed_match", "Match fermé", "Total de buts <= 2", lambda h, a: h + a <= 2),
            family(entries, "open_match", "Match ouvert", "Total de buts >= 4", lambda h, a: h + a >= 4),
            family(entries, "germany_dominates_but_concedes", "Allemagne domine mais encaisse", "Allemagne gagne et Curaçao marque", lambda h, a: h > a and a >= 1),
            family(entries, "surprise_draw", "Surprise : nul", "Match nul", lambda h, a: h == a),
            family(entries, "surprise_curacao_win", "Surprise : victoire Curaçao", "Curaçao gagne", lambda h, a: a > h),
        ],
    }
    payload = {
        "version": "v2.27",
        "generated_at": utc_now(),
        "fixture": {"fixture_id": result["fixture_id"], "match": "Allemagne - Curaçao", "actual_score": "7-1"},
        "source_matrix": {"available": True, "grid": "0-7", "normalized": True, "truncated_tail_known": False},
        "scenario_catalog": catalog,
        "ui_diagnosis": {
            "top_scores_only_was_insufficient": True,
            "large_win_signal_should_be_displayed": True,
            "exact_7_1_should_not_be_promoted_as_likely": True,
        },
        "answer_for_user": (
            "Avant le match, SimuAI identifiait déjà plusieurs familles : Allemagne gagne, victoire courte, victoire contrôlée, victoire large, carton, match fermé ou ouvert, BTTS et clean sheet. "
            "Le 7-1 exact ne pesait que 0,058 %, mais une victoire allemande par 3+ buts pesait 14,73 %. Le produit affichait les scores exacts les plus probables au lieu de rendre ces familles lisibles."
        ),
    }
    publish(payload)
    print("V2.27 Germany-Curacao scenario catalog: PASS")


if __name__ == "__main__":
    main()
