"""Build the public V2.12 model scoreboard from prediction history."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, load_json, utc_now
from backend.scripts.v2_12_transparency_utils import ENGINE, VERSION, dnb_metric, hit_metric, publish


def main() -> None:
    history = load_json(DATA_DIR / "generated" / "prediction_history_v2_12.json")
    evaluated = [row for row in history["matches"] if row["evaluation"]["available"]]
    market_names = ["over_0_5_hit", "over_1_5_hit", "over_2_5_hit", "under_2_5_hit", "under_3_5_hit"]
    market_metrics = {
        name.replace("_hit", ""): hit_metric([row["evaluation"]["over_under_hits"][name] for row in evaluated])
        for name in market_names
    }
    team_goal_values = [
        value for row in evaluated for value in row["evaluation"]["team_goals_hits"].values()
    ]
    alternative = []
    for row in evaluated:
        actual = f"{row['actual_result']['home_goals']}-{row['actual_result']['away_goals']}"
        scores = [score["score"] for score in row["alternative_projection"]["top_scores"]]
        alternative.append({
            "match_id": row["match_id"],
            "active_exact": row["evaluation"]["exact_score_hit"],
            "alternative_exact": bool(scores and actual == scores[0]),
            "active_top_5": row["evaluation"]["top_5_hit"],
            "alternative_top_5": actual in scores[:5],
        })
    exact = hit_metric([row["evaluation"]["exact_score_hit"] for row in evaluated])
    top3 = hit_metric([row["evaluation"]["top_3_hit"] for row in evaluated])
    top5 = hit_metric([row["evaluation"]["top_5_hit"] for row in evaluated])
    one_x_two = hit_metric([row["evaluation"]["one_x_two_hit"] for row in evaluated])
    favorite = hit_metric([row["evaluation"]["favorite_hit"] for row in evaluated])
    dnb = dnb_metric([row["evaluation"]["dnb_outcome"] for row in evaluated])
    sample_small = len(evaluated) < 10
    payload = {
        "version": VERSION,
        "engine_version": ENGINE,
        "generated_at": utc_now(),
        "sample": {
            "total_matches": history["total_matches"],
            "finished_matches": history["finished_matches"],
            "evaluated_matches": len(evaluated),
            "pending_matches": history["pending_matches"],
            "sample_size_too_small": sample_small,
        },
        "score_metrics": {"exact_score": exact, "top_3": top3, "top_5": top5},
        "outcome_metrics": {"one_x_two": one_x_two, "favorite": favorite, "draw_no_bet": dnb},
        "market_metrics": {
            "over_under": market_metrics,
            "btts": hit_metric([row["evaluation"]["btts_hit"] for row in evaluated]),
            "team_goals": hit_metric(team_goal_values),
        },
        "alternative_projection_metrics": {
            "available": True,
            "candidate_status": "alternative_non_active",
            "compared_matches": len(alternative),
            "active_vs_alternative": {
                "active_exact_hits": sum(row["active_exact"] for row in alternative),
                "alternative_exact_hits": sum(row["alternative_exact"] for row in alternative),
                "active_top_5_hits": sum(row["active_top_5"] for row in alternative),
                "alternative_top_5_hits": sum(row["alternative_top_5"] for row in alternative),
                "interpretation": "La projection alternative reste un scénario comparatif non actif.",
            },
        },
        "streaks_and_highlights": {
            "best_hits": [row["public_summary"] | {"match": f"{row['home_team']} {row['actual_result']['home_goals']}-{row['actual_result']['away_goals']} {row['away_team']}"} for row in evaluated if row["evaluation"]["exact_score_hit"] or row["evaluation"]["top_5_hit"]],
            "misses_to_review": [row["public_summary"] | {"match": f"{row['home_team']} {row['actual_result']['home_goals']}-{row['actual_result']['away_goals']} {row['away_team']}"} for row in evaluated if not row["evaluation"]["one_x_two_hit"] and not row["evaluation"]["top_5_hit"]],
            "notable_partial_hits": [row["public_summary"] | {"match": f"{row['home_team']} {row['actual_result']['home_goals']}-{row['actual_result']['away_goals']} {row['away_team']}"} for row in evaluated if row["evaluation"]["one_x_two_hit"] and not row["evaluation"]["exact_score_hit"]],
        },
        "public_interpretation": {
            "headline": f"{len(evaluated)} matchs évalués : le moteur commence à rendre des comptes.",
            "summary": f"Le 1X2 est réussi sur {one_x_two['hits']}/{one_x_two['total']} matchs et le score réel apparaît dans le Top-5 sur {top5['hits']}/{top5['total']} matchs.",
            "caution": "Échantillon trop petit pour conclure sur la performance globale." if sample_small else "Les métriques deviennent plus informatives mais restent descriptives.",
        },
    }
    publish(payload, "model_scoreboard_v2_12.json")
    (ROOT / "docs" / "MODEL_SCOREBOARD_V2_12.md").write_text(f"""# Model Scoreboard V2.12

The public scoreboard currently covers `{len(evaluated)}` evaluated matches from `{history['total_matches']}` frozen forecasts. Exact score is `{exact['hits']}/{exact['total']}`, Top-3 is `{top3['hits']}/{top3['total']}`, Top-5 is `{top5['hits']}/{top5['total']}` and 1X2 is `{one_x_two['hits']}/{one_x_two['total']}`.

Draw No Bet is reported without hiding pushes: `{dnb['wins']}` wins, `{dnb['losses']}` losses and `{dnb['pushes']}` pushes. Win rate excluding pushes and non-loss including pushes are published separately. Over/under, BTTS and team-goal results are also preserved at market level.

Because fewer than ten matches are evaluated, `sample_size_too_small` is `{str(sample_small).lower()}`. These figures describe the current tournament evidence and must not be treated as a stable estimate of future quality. Misses remain visible. The alternative projection is compared on the same finished matches but remains non-active.
""", encoding="utf-8")
    print(f"V2.12 scoreboard built: {len(evaluated)} evaluated, small_sample={sample_small}")


if __name__ == "__main__":
    main()
