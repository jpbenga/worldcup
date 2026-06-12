"""Evaluate frozen pre-match predictions against available finished results."""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, load_json, utc_now
from backend.scripts.v2_6_live_utils import ENGINE_VERSION, VERSION, publish, release_matches


def outcome(home: int, away: int) -> str:
    return "home" if home > away else "away" if away > home else "draw"


def hit(actual: bool, probability: float) -> bool:
    return actual == (probability >= 0.5)


def summarize(item: dict[str, Any]) -> tuple[str, str]:
    if item["exact_score_hit"]:
        return "exact_score", "Score exact trouvé"
    if item["top_3_score_hit"]:
        return "top_3", "Le score réel était dans le Top-3"
    if item["one_x_two_hit"]:
        return "one_x_two", "Bon résultat 1X2, score différent"
    if item["draw_no_bet"]["outcome"] == "push":
        return "dnb_push", "Match nul remboursé en DNB"
    if item["draw_no_bet"]["outcome"] == "win":
        return "dnb_protected", "Prédiction principale ratée, mais DNB protégé"
    return "miss", "Prédiction principale ratée"


def ratio(items: list[dict[str, Any]], key: str) -> dict[str, Any]:
    hits = sum(bool(item[key]) for item in items)
    return {"hits": hits, "total": len(items), "rate": hits / len(items) if items else None}


def main() -> None:
    results = load_json(DATA_DIR / "generated" / "worldcup_2026_results_v2_6.json")
    predictions = {item["match_id"]: item for item in release_matches()}
    active = {item["match_id"]: item for item in load_json(DATA_DIR / "generated" / "predictions.json")}
    market_context = load_json(DATA_DIR / "generated" / "secondary_market_performance_summary_v2_4.json")
    evaluations = []
    for result in results["fixtures"]:
        if result["status"] != "finished" or result["actual_score"]["home"] is None or result["match_id"] not in predictions:
            continue
        prediction, raw = predictions[result["match_id"]], active[result["match_id"]]
        home, away = int(result["actual_score"]["home"]), int(result["actual_score"]["away"])
        score, actual_1x2 = f"{home}-{away}", outcome(home, away)
        predicted_1x2 = max(prediction["probabilities"], key=prediction["probabilities"].get).replace("_win", "")
        dnb_pick = "home" if prediction["markets"]["draw_no_bet"]["home"] >= prediction["markets"]["draw_no_bet"]["away"] else "away"
        dnb_outcome = "push" if actual_1x2 == "draw" else "win" if actual_1x2 == dnb_pick else "loss"
        total, btts = home + away, home > 0 and away > 0
        item = {
            "match_id": result["match_id"], "fixture_id": result["fixture_id"], "home_team": result["home_team"], "away_team": result["away_team"],
            "actual_score": score, "score_modal": prediction["score_modal"],
            "exact_score_hit": score == prediction["score_modal"],
            "top_3_score_hit": score in [row["score"] for row in prediction["top_scores"][:3]],
            "top_5_score_hit": score in [row["score"] for row in prediction["top_scores"][:5]],
            "predicted_1x2": predicted_1x2, "actual_1x2": actual_1x2, "one_x_two_hit": predicted_1x2 == actual_1x2,
            "favorite_hit": predicted_1x2 != "draw" and predicted_1x2 == actual_1x2,
            "draw_no_bet": {"selection": dnb_pick, "outcome": dnb_outcome},
            "over_under": {
                "over_0_5_hit": hit(total > 0.5, prediction["markets"]["over_under"]["over_0_5"]),
                "over_1_5_hit": hit(total > 1.5, prediction["markets"]["over_under"]["over_1_5"]),
                "over_2_5_hit": hit(total > 2.5, prediction["markets"]["over_under"]["over_2_5"]),
                "under_2_5_hit": hit(total < 2.5, prediction["markets"]["over_under"]["under_2_5"]),
                "under_3_5_hit": hit(total < 3.5, prediction["markets"]["over_under"]["under_3_5"]),
            },
            "btts_hit": hit(btts, prediction["markets"]["both_teams_to_score"]["yes"]),
            "team_goals_hit": {
                "home_over_0_5": hit(home > 0.5, prediction["markets"]["team_goals"]["team_home_over_0_5"]),
                "away_over_0_5": hit(away > 0.5, prediction["markets"]["team_goals"]["team_away_over_0_5"]),
            },
            "clean_sheet_hit": {
                "home": hit(away == 0, raw["markets"]["clean_sheet_home"]),
                "away": hit(home == 0, raw["markets"]["clean_sheet_away"]),
            },
            "confidence_bucket": prediction["confidence"]["level"],
        }
        item["prediction_evaluation_label"], item["post_match_summary"] = summarize(item)
        evaluations.append(item)
    dnb = Counter(item["draw_no_bet"]["outcome"] for item in evaluations)
    report = {
        "version": VERSION, "engine_version": ENGINE_VERSION, "generated_at": utc_now(),
        "evaluated_finished_matches": len(evaluations), "pending_matches": len(results["fixtures"]) - len(evaluations),
        "sample_size_too_small": len(evaluations) < 20,
        "exact_score": ratio(evaluations, "exact_score_hit"), "top_3": ratio(evaluations, "top_3_score_hit"),
        "top_5": ratio(evaluations, "top_5_score_hit"), "one_x_two": ratio(evaluations, "one_x_two_hit"),
        "draw_no_bet": {"wins": dnb["win"], "losses": dnb["loss"], "pushes": dnb["push"], "total": len(evaluations)},
        "over_under": {key: ratio([{"hit": item["over_under"][key]} for item in evaluations], "hit") for key in ("over_0_5_hit", "over_1_5_hit", "over_2_5_hit", "under_2_5_hit", "under_3_5_hit")},
        "btts": ratio(evaluations, "btts_hit"),
        "team_goals": {"evaluated_markets": len(evaluations) * 2, "hits": sum(sum(item["team_goals_hit"].values()) for item in evaluations)},
        "matches": evaluations,
        "secondary_market_context_version": market_context["version"],
        "notes": ["Sample is too small for a strong global conclusion."] if len(evaluations) < 20 else [],
    }
    publish(report, "worldcup_2026_prediction_evaluation_v2_6.json")
    (ROOT / "docs" / "WORLDCUP_2026_PREDICTION_EVALUATION_V2_6.md").write_text(
        f"""# World Cup 2026 Prediction Evaluation V2.6

V2.6 evaluated `{len(evaluations)}` finished match(es) against frozen pre-match `quant_hybrid_v2.2` predictions. It did not rewrite predictions after results became known.

Exact score: `{report["exact_score"]}`. Top-3: `{report["top_3"]}`. Top-5: `{report["top_5"]}`. 1X2: `{report["one_x_two"]}`. DNB outcomes: `{report["draw_no_bet"]}`.

`sample_size_too_small` is `{str(report["sample_size_too_small"]).lower()}`. No strong global performance conclusion should be drawn while this flag is true.
""", encoding="utf-8")
    print(f"V2.6 evaluation: finished={len(evaluations)}, sample_size_too_small={report['sample_size_too_small']}")


if __name__ == "__main__":
    main()
