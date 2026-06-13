"""Build an append-only public history from frozen predictions and actual results."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, load_json, utc_now
from backend.scripts.v2_12_transparency_utils import CANDIDATE, ENGINE, VERSION, public_headline, publish


def main() -> None:
    predictions = load_json(DATA_DIR / "generated" / "worldcup_2026_predictions_release_candidate_v2_4.json")
    states = load_json(DATA_DIR / "generated" / "worldcup_match_state_view_model_v2_7.json")
    evaluations = load_json(DATA_DIR / "generated" / "worldcup_2026_prediction_evaluation_v2_6.json")
    dual = load_json(DATA_DIR / "generated" / "dual_matrix_comparison_v2_9.json")
    states_by_id = {row["match_id"]: row for row in states["matches"]}
    evaluations_by_id = {row["match_id"]: row for row in evaluations["matches"]}
    dual_by_id = {row["match_id"]: row for row in dual["matches"]}
    matches = []
    for prediction in predictions["matches"]:
        match_id = prediction["match_id"]
        state = states_by_id[match_id]
        source_evaluation = evaluations_by_id.get(match_id)
        alternative = dual_by_id.get(match_id)
        evaluation_available = state["status"] == "finished" and state["result"]["available"] and source_evaluation is not None
        evaluation = {
            "available": evaluation_available,
            "exact_score_hit": source_evaluation["exact_score_hit"] if evaluation_available else None,
            "top_3_hit": source_evaluation["top_3_score_hit"] if evaluation_available else None,
            "top_5_hit": source_evaluation["top_5_score_hit"] if evaluation_available else None,
            "one_x_two_hit": source_evaluation["one_x_two_hit"] if evaluation_available else None,
            "favorite_hit": source_evaluation["favorite_hit"] if evaluation_available else None,
            "dnb_outcome": source_evaluation["draw_no_bet"]["outcome"] if evaluation_available else None,
            "over_under_hits": source_evaluation["over_under"] if evaluation_available else {},
            "btts_hit": source_evaluation["btts_hit"] if evaluation_available else None,
            "team_goals_hits": source_evaluation["team_goals_hit"] if evaluation_available else {},
            "summary_label": source_evaluation["post_match_summary"] if evaluation_available else "",
        }
        actual = {
            "available": state["result"]["available"],
            "home_goals": state["result"]["home_goals"],
            "away_goals": state["result"]["away_goals"],
            "winner": state["result"]["winner"],
            "source": state["result"]["source"],
        }
        matches.append({
            "fixture_id": prediction["fixture_id"],
            "match_id": match_id,
            "group": state["group"],
            "matchday": state["matchday_label"],
            "kickoff_at": prediction["kickoff_at"],
            "home_team": prediction["home_team"],
            "away_team": prediction["away_team"],
            "status": state["status"],
            "pre_match_prediction": {
                "engine_version": prediction["engine_version"],
                "prediction_generated_at": prediction["generated_at"],
                "score_modal": prediction["score_modal"],
                "score_modal_probability": prediction["top_scores"][0]["probability"],
                "top_scores": prediction["top_scores"],
                "probabilities_1x2": prediction["probabilities"],
                "favorite_1x2": state["prediction"]["favorite_1x2"],
                "favorite_probability": state["prediction"]["favorite_probability"],
                "markets": prediction["markets"],
            },
            "actual_result": actual,
            "evaluation": evaluation,
            "alternative_projection": {
                "available": alternative is not None,
                "candidate_version": CANDIDATE,
                "candidate_status": "alternative_non_active",
                "score_modal": alternative["candidate"]["score_modal"] if alternative else "",
                "top_scores": alternative["candidate"]["top_scores"] if alternative else [],
                "comparison_label": alternative["comparison"]["label"] if alternative else "",
            },
            "public_summary": {
                "headline": public_headline(evaluation),
                "short_explanation": evaluation["summary_label"] if evaluation_available else "Le résultat final n’est pas encore disponible.",
                "result_badge": "Évalué" if evaluation_available else "À venir",
                "confidence_context": f"Confiance pré-match : {prediction['confidence']['level']}.",
            },
        })
    matches.sort(key=lambda row: row["kickoff_at"])
    finished = sum(row["status"] == "finished" for row in matches)
    evaluated = sum(row["evaluation"]["available"] for row in matches)
    payload = {
        "version": VERSION,
        "engine_version": ENGINE,
        "candidate_version": CANDIDATE,
        "generated_at": utc_now(),
        "history_policy": "append_actuals_never_rewrite_pre_match",
        "total_matches": len(matches),
        "finished_matches": finished,
        "evaluated_matches": evaluated,
        "pending_matches": len(matches) - evaluated,
        "active_predictions_frozen": True,
        "candidate_status": "alternative_non_active",
        "matches": matches,
    }
    publish(payload, "prediction_history_v2_12.json")
    (ROOT / "docs" / "PREDICTION_HISTORY_V2_12.md").write_text(f"""# Prediction History V2.12

V2.12 publishes an append-only history for all `{len(matches)}` World Cup fixtures. It contains `{finished}` finished matches, `{evaluated}` evaluated predictions and `{len(matches) - evaluated}` pending predictions.

Every entry keeps the active `quant_hybrid_v2.2` pre-match score matrix summary, probabilities, favorite and markets separate from the actual-result and post-match evaluation layers. A result can be appended after full time, but the pre-match forecast is never recomputed or rewritten. Matches without a final result keep `evaluation.available=false`.

The alternative `score_matrix_candidate_v2.8` projection is included only as a clearly labelled, non-active comparison. It does not replace the active forecast. Public summaries expose exact hits, partial hits and misses instead of hiding poor outcomes.

A prediction history never rewrites pre-match forecasts. It appends actual outcomes and evaluation labels after the match is known.
""", encoding="utf-8")
    print(f"V2.12 prediction history built: {len(matches)} matches, {evaluated} evaluated")


if __name__ == "__main__":
    main()
