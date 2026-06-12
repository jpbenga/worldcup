"""Build the unified frontend match-state source for V2.7."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, load_json, utc_now
from backend.scripts.v2_7_consistency_utils import ENGINE_VERSION, VERSION, group_code, publish

COHERENCE_EXPLANATION = "Le score modal est la case individuelle la plus probable. La tendance 1X2 additionne toutes les victoires possibles."


def matchday(round_name: str | None) -> str:
    value = str(round_name or "")
    found = re.search(r"(\d+)$", value)
    return f"Group Stage - Matchday {found.group(1)}" if found else value or "Group Stage"


def score_outcome(row: dict[str, Any]) -> str:
    home, away = int(row["home_goals"]), int(row["away_goals"])
    return "home" if home > away else "away" if away > home else "draw"


def favorite_label(favorite: str, match: dict[str, Any]) -> str:
    return match["home_team"] if favorite == "home" else match["away_team"] if favorite == "away" else "Nul"


def main() -> None:
    predictions = load_json(DATA_DIR / "generated" / "worldcup_2026_predictions_release_candidate_v2_4.json")["matches"]
    results = {item["match_id"]: item for item in load_json(DATA_DIR / "generated" / "worldcup_2026_results_v2_6.json")["fixtures"]}
    evaluations = {item["match_id"]: item for item in load_json(DATA_DIR / "generated" / "worldcup_2026_prediction_evaluation_v2_6.json")["matches"]}
    fixtures = {item["match_id"]: item for item in load_json(DATA_DIR / "normalized" / "matches.json")}
    simulation = load_json(DATA_DIR / "generated" / "worldcup_tournament_simulation_conditioned_v2_6.json")
    campaign = load_json(DATA_DIR / "generated" / "worldcup_projected_campaign_v2_6.json")
    matches = []
    divergent = 0
    for prediction in predictions:
        match_id = prediction["match_id"]
        result = results[match_id]
        evaluation = evaluations.get(match_id)
        fixture = fixtures[match_id]
        probabilities = prediction["probabilities"]
        favorite_key = max(probabilities, key=probabilities.get)
        favorite = favorite_key.replace("_win", "")
        entries = prediction["score_matrix"]["probabilities"]
        consistent = max((row for row in entries if score_outcome(row) == favorite), key=lambda row: row["probability"])
        modal_outcome = score_outcome(entries_by_score(entries)[prediction["score_modal"]])
        differs = modal_outcome != favorite
        divergent += differs
        status = result["status"]
        result_available = status in {"finished", "live"} and result["actual_score"]["home"] is not None
        card_score = f'{result["actual_score"]["home"]}-{result["actual_score"]["away"]}' if result_available else prediction["score_modal"]
        card_label = evaluation["post_match_summary"] if evaluation else "En direct" if status == "live" else f'Tendance {favorite_label(favorite, prediction)} {probabilities[favorite_key]:.0%}'
        matches.append({
            "fixture_id": prediction["fixture_id"], "match_id": match_id, "group": group_code(prediction["group"]),
            "matchday": matchday(fixture.get("round")), "matchday_label": matchday(fixture.get("round")),
            "home_team": prediction["home_team"], "away_team": prediction["away_team"], "kickoff_at": prediction["kickoff_at"],
            "venue": fixture.get("venue"), "city": fixture.get("city"), "home_team_logo_url": fixture.get("home_team_logo_url"),
            "away_team_logo_url": fixture.get("away_team_logo_url"), "status": status,
            "result": {"available": result_available, "home_goals": result["actual_score"]["home"], "away_goals": result["actual_score"]["away"], "winner": result["winner"], "source": result["confidence"]},
            "prediction": {
                "engine_version": ENGINE_VERSION, "score_modal": prediction["score_modal"],
                "score_modal_probability": prediction["top_scores"][0]["probability"], "top_scores": prediction["top_scores"],
                "score_matrix": prediction["score_matrix"], "probabilities_1x2": probabilities,
                "favorite_1x2": favorite, "favorite_label": favorite_label(favorite, prediction),
                "favorite_probability": probabilities[favorite_key], "score_consistent_with_favorite": consistent["score"],
                "score_consistent_with_favorite_probability": consistent["probability"],
                "coherence_status": "modal_differs_from_1x2_favorite" if differs else "modal_aligned_with_1x2_favorite",
                "coherence_explanation": COHERENCE_EXPLANATION if differs else "Le score modal et la tendance 1X2 pointent vers le même résultat.",
                "confidence": prediction["confidence"], "markets": prediction["markets"],
            },
            "evaluation": {
                "available": evaluation is not None, "summary_label": evaluation["post_match_summary"] if evaluation else "",
                "exact_score_hit": evaluation["exact_score_hit"] if evaluation else None,
                "top_3_hit": evaluation["top_3_score_hit"] if evaluation else None,
                "top_5_hit": evaluation["top_5_score_hit"] if evaluation else None,
                "one_x_two_hit": evaluation["one_x_two_hit"] if evaluation else None,
                "dnb_outcome": evaluation["draw_no_bet"]["outcome"] if evaluation else None,
                "market_hits": {"over_under": evaluation["over_under"], "btts": evaluation["btts_hit"], "team_goals": evaluation["team_goals_hit"]} if evaluation else {},
            },
            "standings_impact": {"group": group_code(prediction["group"]), "locked_in_conditioned_simulation": status == "finished"},
            "display": {
                "card_primary_score": card_score, "card_secondary_label": card_label,
                "modal_status_label": "Résultat officiel" if status == "finished" else "En direct" if status == "live" else "À venir",
                "result_vs_prediction_label": evaluation["post_match_summary"] if evaluation else "",
                "show_result_block": status == "finished" and evaluation is not None, "show_coherence_warning": differs,
            },
        })
    payload = {
        "version": VERSION, "engine_version": ENGINE_VERSION, "generated_at": utc_now(), "match_count": len(matches),
        "divergent_modal_favorite_count": divergent, "conditioned_simulation_version": simulation["version"],
        "projected_campaign_path_type": campaign["path_type"], "matches": matches,
    }
    publish(payload, "worldcup_match_state_view_model_v2_7.json")
    (ROOT / "docs" / "WORLDCUP_MATCH_STATE_VIEW_MODEL_V2_7.md").write_text(
        f"""# World Cup Match State View Model V2.7

The V2.7 match-state view model is the single frontend source for all `{len(matches)}` fixtures. Each record joins the frozen V2.4 prediction, current V2.6 result status, finished-match evaluation, normalized matchday, standings impact and display labels used by both cards and the existing modal.

`{divergent}` matches have a modal-score outcome that differs from the active 1X2 favorite. Those matches include a score compatible with the favorite and a concise explanation rather than being labelled contradictory.

Finished results remain a separate layer and never rewrite pre-match matrices or probabilities. Non-finished matches never receive a final evaluation.
""", encoding="utf-8")
    print(f"V2.7 match state: {len(matches)} matches, {divergent} modal/favorite divergences")


def entries_by_score(entries: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {row["score"]: row for row in entries}


if __name__ == "__main__":
    main()
