"""Build scenario-aware score matrix payloads from the V2.30 candidate predictions."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.full_stats_engine_v2_30_utils import large_win_probability, matrix_entries, parse_score, publish
from backend.scripts.pipeline_utils import DATA_DIR, load_json, utc_now

OUTPUT = "full_stats_scenario_aware_matrix_v2_30.json"
PREDICTIONS = "predictions_full_stats_candidate_v2_30.json"
THRESHOLDS = {
    "large_favorite_win": 0.10,
    "favorite_scores_4_plus": 0.08,
    "over_3_5": 0.20,
    "blowout": 0.01,
}


def family(items: list[dict[str, Any]], key: str, label: str, rule: Callable[[int, int], bool]) -> dict[str, Any]:
    parsed = [(item["score"], *parse_score(item)) for item in items]
    cells = [(score, probability) for score, h, a, probability in parsed if rule(h, a)]
    probability = sum(probability for _, probability in cells)
    representatives = [score for score, _ in sorted(cells, key=lambda row: row[1], reverse=True)[:3]]
    return {
        "key": key,
        "label": label,
        "probability": round(probability, 6),
        "representative_scores": representatives,
    }


def build_match(prediction: dict[str, Any]) -> dict[str, Any]:
    items = matrix_entries(prediction)
    markets = prediction["markets"]
    home, away = prediction["home_team"], prediction["away_team"]
    favorite_side = "home" if markets["home_win"] >= markets["away_win"] else "away"
    favorite_name = home if favorite_side == "home" else away

    def fav_margin(h: int, a: int) -> int:
        return h - a if favorite_side == "home" else a - h

    def fav_goals(h: int, a: int) -> int:
        return h if favorite_side == "home" else a

    families = [
        family(items, "short_favorite_win", "Victoire courte", lambda h, a: fav_margin(h, a) == 1),
        family(items, "controlled_favorite_win", "Victoire contrôlée", lambda h, a: fav_margin(h, a) == 2),
        family(items, "large_favorite_win", "Victoire large", lambda h, a: fav_margin(h, a) >= 3),
        family(items, "blowout", "Carton possible", lambda h, a: fav_margin(h, a) >= 5),
        family(items, "favorite_4_plus_goals", f"{favorite_name} marque 4+ buts", lambda h, a: fav_goals(h, a) >= 4),
        family(items, "over_2_5", "Over 2,5", lambda h, a: h + a >= 3),
        family(items, "over_3_5", "Over 3,5", lambda h, a: h + a >= 4),
        family(items, "open_match", "Match ouvert / Over 3,5", lambda h, a: h + a >= 4),
        family(items, "closed_match", "Match fermé / Under 2,5", lambda h, a: h + a <= 2),
        family(items, "btts", "Les deux équipes marquent", lambda h, a: h > 0 and a > 0),
        family(items, "favorite_clean_sheet", "Favori sans encaisser", lambda h, a: fav_margin(h, a) > 0 and (a == 0 if favorite_side == "home" else h == 0)),
    ]
    signals = {row["key"]: row["probability"] for row in families}
    mode = max(items, key=lambda row: float(row["probability"]))
    representatives = [{"score": mode["score"], "reason": "score repère exact le plus probable", "show_probability": False}]
    seen = {mode["score"]}
    for key in ("large_favorite_win", "favorite_4_plus_goals", "open_match", "blowout"):
        row = next(item for item in families if item["key"] == key)
        for score in row["representative_scores"]:
            if score not in seen:
                representatives.append({"score": score, "reason": f"représente le scénario {row['label'].lower()}", "show_probability": False})
                seen.add(score)
                break
        if len(representatives) >= 5:
            break
    favorite_probability = max(markets["home_win"], markets["away_win"])
    confidence = "high" if favorite_probability >= 0.60 else "medium" if favorite_probability >= 0.45 else "low"
    return {
        "fixture_id": prediction.get("fixture_id"),
        "match_id": prediction["match_id"],
        "match_label": f"{home} - {away}",
        "candidate_model_version": prediction.get("model_version"),
        "main_reading": {
            "label": f"{favorite_name} favori, lecture par familles de scénarios",
            "confidence": confidence,
            "favorite_probability": round(favorite_probability, 6),
        },
        "outcome_probabilities": {
            "home_win": markets["home_win"],
            "draw": markets["draw"],
            "away_win": markets["away_win"],
        },
        "scenario_families": families,
        "scenario_signals": {
            "large_win_visible": signals["large_favorite_win"] >= THRESHOLDS["large_favorite_win"],
            "favorite_4_plus_goals_visible": signals["favorite_4_plus_goals"] >= THRESHOLDS["favorite_scores_4_plus"],
            "over_3_5_visible": signals["over_3_5"] >= THRESHOLDS["over_3_5"],
            "blowout_visible": signals["blowout"] >= THRESHOLDS["blowout"],
        },
        "display_scores": {"mode_score": mode["score"], "representative_scores": representatives},
        "advanced_exact_scores": sorted(items, key=lambda row: float(row["probability"]), reverse=True)[:10],
        "ui_policy": {
            "do_not_center_exact_score_percentages": True,
            "show_scenario_probabilities_first": True,
            "exact_score_percentages_location": "advanced_detail",
        },
    }


def main() -> None:
    predictions = load_json(DATA_DIR / "generated" / PREDICTIONS)
    matches = [build_match(prediction) for prediction in predictions]
    germany_curacao = [
        row for row in matches
        if "germany" in row["match_label"].lower() and ("cura" in row["match_label"].lower() or "curacao" in row["match_label"].lower())
    ]
    high_imbalance = sorted(
        matches,
        key=lambda row: (row["main_reading"]["favorite_probability"], large_win_probability(row)),
        reverse=True,
    )[:8]
    payload = {
        "version": "v2.30",
        "generated_at": utc_now(),
        "source_predictions": PREDICTIONS,
        "thresholds": THRESHOLDS,
        "matrix_policy": {
            "score_repere_first_level": True,
            "exact_score_percentages_decentered": True,
            "scenario_probabilities_first": True,
            "candidate_only_not_active": True,
        },
        "matches": matches,
        "focus_checks": {
            "germany_curacao_in_candidate_predictions": bool(germany_curacao),
            "germany_curacao": germany_curacao[:1],
            "high_imbalance_matches": [
                {
                    "match_id": row["match_id"],
                    "match_label": row["match_label"],
                    "favorite_probability": row["main_reading"]["favorite_probability"],
                    "large_favorite_win_probability": next(f["probability"] for f in row["scenario_families"] if f["key"] == "large_favorite_win"),
                    "mode_score": row["display_scores"]["mode_score"],
                }
                for row in high_imbalance
            ],
        },
    }
    publish(payload, OUTPUT)
    print(f"V2.30 scenario-aware matrix: matches={len(matches)}")


if __name__ == "__main__":
    main()
