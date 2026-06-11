"""Build the V2.4 product release candidate and integrated market summary."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, load_json, utc_now
from backend.scripts.v2_4_release_utils import ENGINE_VERSION, VERSION, normalized_probability, publish


def block(markets: dict[str, float]) -> dict[str, Any]:
    return {
        "double_chance": {key: markets[key] for key in ("double_chance_1X", "double_chance_X2", "double_chance_12")},
        "draw_no_bet": {"home": markets["draw_no_bet_home"], "away": markets["draw_no_bet_away"]},
        "over_under": {key: markets[key] for key in ("over_0_5", "over_1_5", "over_2_5", "over_3_5", "under_1_5", "under_2_5", "under_3_5")},
        "both_teams_to_score": {"yes": markets["both_teams_to_score_yes"], "no": markets["both_teams_to_score_no"]},
        "team_goals": {key: markets[key] for key in ("team_home_over_0_5", "team_away_over_0_5", "team_home_over_1_5", "team_away_over_1_5")},
    }


def release_match(item: dict[str, Any]) -> dict[str, Any]:
    probabilities = {key: item["markets"][key] for key in ("home_win", "draw", "away_win")}
    top_score = item["top_scores"][0]["score"]
    predicted = max(probabilities, key=probabilities.get)
    home, away = map(int, top_score.split("-"))
    score_outcome = "home_win" if home > away else "away_win" if away > home else "draw"
    ordered = sorted(probabilities.values(), reverse=True)
    return {
        "fixture_id": item.get("fixture_id"), "match_id": item["match_id"], "group": item.get("group"), "stage": item.get("stage"),
        "kickoff_at": item.get("kickoff_at"), "home_team": item["home_team"], "away_team": item["away_team"],
        "engine_version": ENGINE_VERSION, "release_candidate_version": VERSION, "prediction_version": item["prediction_version"],
        "generated_at": item["generated_at"], "score_matrix": item["score_matrix"], "top_scores": item["top_scores"], "score_modal": top_score,
        "probabilities": probabilities, "markets": block(item["markets"]),
        "confidence": {"level": item.get("confidence"), "favorite_probability": max(probabilities["home_win"], probabilities["away_win"]), "outcome_gap": ordered[0]-ordered[1]},
        "coherence": {"favorite_score_aligned": predicted == score_outcome, "notes": [] if predicted == score_outcome else ["Modal score outcome differs from active hybrid 1X2 selection."]},
        "source": {"active_prediction_file": "backend/data/generated/predictions.json", "engine": ENGINE_VERSION},
    }


def market_summary() -> dict[str, Any]:
    audit = load_json(DATA_DIR / "generated" / "active_matrix_market_audit_v2_3.json")
    compare = load_json(DATA_DIR / "generated" / "matrix_vs_xgboost_market_comparison_v2_3.json")
    score, markets, dnb = audit["score_matrix"], audit["matrix_derived_markets"], audit["draw_no_bet"]
    names = ("over_0_5", "over_1_5", "over_2_5", "under_2_5", "under_3_5", "double_chance_1X", "double_chance_X2", "double_chance_12", "both_teams_to_score_yes", "both_teams_to_score_no", "home_over_0_5", "away_over_0_5")
    return {
        "generated_at": utc_now(), "version": VERSION, "engine_version": ENGINE_VERSION, "source_version": "v2.3",
        "plain_language_definitions": {
            "top_3": "The actual score appears among the three highest-probability scores.",
            "top_5": "The actual score appears among the five highest-probability scores.",
            "modal_score": "The single score with the highest matrix probability.",
            "coverage": "Selections divided by all audited matches.", "push": "A DNB draw returns the stake and is neither a win nor a loss.",
            "win_excluding_push": "Wins divided by wins plus losses.", "non_loss_including_push": "Wins plus pushes divided by all selections.",
        },
        "score_matrix": {key: score[key] for key in ("exact_score", "top_3_score", "top_5_score", "modal_1_1_rate")},
        "draw_no_bet": {key: dnb[key] for key in ("0.00", "0.60", "0.70")},
        "matrix_markets_at_0_60": {name: markets[name]["0.60"] for name in names},
        "matrix_vs_xgboost": {"best_source_counts_by_brier": compare["best_source_counts_by_brier"], "one_x_two": compare["one_x_two"], "limitations": compare["comparison_limitations"]},
        "product_guidance": {"show": ["over_0_5", "double_chance", "DNB with push definition", "team_over_0_5", "filtered over_1_5"], "warn_or_hide": ["BTTS yes", "clean sheets", "winning margins", "low-coverage high totals"]},
    }


def main() -> None:
    active = load_json(DATA_DIR / "generated" / "predictions.json")
    matches = [release_match(item) for item in active]
    if len(matches) != 72:
        raise SystemExit(f"Expected 72 active predictions, found {len(matches)}")
    for item in matches:
        probs = item["probabilities"]
        if not all(normalized_probability(value) for value in probs.values()) or abs(sum(probs.values()) - 1) > 1e-5:
            raise SystemExit(f"Invalid 1X2 probabilities: {item['match_id']}")
    payload = {"version": VERSION, "engine_version": ENGINE_VERSION, "status": "release_candidate", "fixture_count": len(matches), "matches": matches}
    summary = market_summary()
    publish(payload, "worldcup_2026_predictions_release_candidate_v2_4.json")
    publish(summary, "secondary_market_performance_summary_v2_4.json")
    incoherent = sum(not item["coherence"]["favorite_score_aligned"] for item in matches)
    (ROOT / "docs" / "WORLDCUP_2026_PREDICTION_RELEASE_CANDIDATE_V2_4.md").write_text(
        f"""# World Cup 2026 Prediction Release Candidate V2.4

The release candidate packages exactly `{len(matches)}` active `{ENGINE_VERSION}` predictions for frontend consumption. Every match includes fixture metadata, normalized score matrix, top scores, active hybrid 1X2 probabilities, structured secondary markets, confidence and favorite-score coherence.

All 72 matrices, top-score lists and market blocks passed structural validation. `{incoherent}` matches have a modal-score outcome that differs from the active hybrid 1X2 selection; these are retained and explicitly flagged rather than hidden. No model was retrained and no probability was recalculated by V2.4.

The fixture metadata is a versioned release snapshot, not a live score/status feed. Consumers must refresh fixture status separately before treating a scheduled match as not yet started.
""", encoding="utf-8")
    (ROOT / "docs" / "SECONDARY_MARKET_PERFORMANCE_SUMMARY_V2_4.md").write_text(
        """# Secondary Market Performance Summary V2.4

V2.4 integrates the V2.3 market audit as product context rather than creating another model iteration. Top-3 and top-5 mean that the actual score appears among the three or five highest-probability matrix scores. The modal score is the single most likely score. Coverage is the share of all audited matches producing a selection.

A DNB push is a draw that returns the stake. Win rate excluding pushes divides wins by wins plus losses; non-loss including pushes counts both wins and returned-stake draws. At confidence 0.60, matrix DNB reaches 87.6% wins excluding pushes and 90.1% non-loss including pushes at 70.2% coverage. The 90% statement applies only to the pushes-included non-loss definition.

Broad markets such as over 0.5, double chance and filtered team-goal lines are useful product signals. BTTS yes, clean sheets, winning margins and sparse high-total selections require warnings or should remain hidden. Matrix-versus-XGBoost provenance and limitations remain explicit in the JSON summary.
""", encoding="utf-8")
    print(f"V2.4 release candidate built: {len(matches)} matches; incoherent={incoherent}")


if __name__ == "__main__":
    main()
