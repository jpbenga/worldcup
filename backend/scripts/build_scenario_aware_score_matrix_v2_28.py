"""Build scenario-aware score-matrix view models from active predictions."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, write_json

OUTPUT = "scenario_aware_score_matrix_v2_28.json"
THRESHOLDS = {"large_favorite_win": 0.10, "favorite_scores_4_plus": 0.08, "over_3_5": 0.20, "blowout": 0.01}


def publish(payload: dict[str, Any]) -> None:
    target = DATA_DIR / "generated" / OUTPUT
    write_json(payload, target)
    shutil.copy2(target, DATA_DIR / "snapshots" / OUTPUT)
    shutil.copy2(target, FRONTEND_DATA_DIR / OUTPUT)


def entries(prediction: dict[str, Any]) -> list[dict[str, Any]]:
    matrix = prediction["score_matrix"]
    return matrix["probabilities"] if isinstance(matrix, dict) else matrix


def parse(item: dict[str, Any]) -> tuple[int, int, float]:
    if "home_goals" in item:
        return int(item["home_goals"]), int(item["away_goals"]), float(item["probability"])
    h, a = [int(part) for part in item["score"].split("-")]
    return h, a, float(item["probability"])


def family(items: list[dict[str, Any]], key: str, label: str, rule: Callable[[int, int], bool]) -> dict[str, Any]:
    cells = [(f"{h}-{a}", p) for h, a, p in (parse(item) for item in items) if rule(h, a)]
    probability = sum(p for _, p in cells)
    representatives = [score for score, _ in sorted(cells, key=lambda item: item[1], reverse=True)[:3]]
    return {"key": key, "label": label, "probability": round(probability, 6), "representative_scores": representatives}


def build(prediction: dict[str, Any]) -> dict[str, Any]:
    items = entries(prediction)
    markets = prediction["markets"]
    home, away = prediction["home_team"], prediction["away_team"]
    favorite = "home" if markets["home_win"] >= markets["away_win"] else "away"
    favorite_name = home if favorite == "home" else away
    def fav_margin(h: int, a: int) -> int:
        return h - a if favorite == "home" else a - h
    def fav_goals(h: int, a: int) -> int:
        return h if favorite == "home" else a
    scenario_families = [
        family(items, "short_favorite_win", "Victoire courte", lambda h, a: fav_margin(h, a) == 1),
        family(items, "controlled_favorite_win", "Victoire contrôlée", lambda h, a: fav_margin(h, a) == 2),
        family(items, "large_favorite_win", "Victoire large", lambda h, a: fav_margin(h, a) >= 3),
        family(items, "blowout", "Carton possible", lambda h, a: fav_margin(h, a) >= 5),
        family(items, "favorite_4_plus_goals", f"{favorite_name} marque 4+ buts", lambda h, a: fav_goals(h, a) >= 4),
        family(items, "open_match", "Match ouvert", lambda h, a: h + a >= 4),
        family(items, "closed_match", "Match fermé", lambda h, a: h + a <= 2),
        family(items, "btts", "Les deux équipes marquent", lambda h, a: h > 0 and a > 0),
        family(items, "favorite_clean_sheet", "Favori sans encaisser", lambda h, a: fav_margin(h, a) > 0 and (a == 0 if favorite == "home" else h == 0)),
    ]
    signals = {row["key"]: row["probability"] for row in scenario_families}
    representative = []
    mode = max(items, key=lambda item: float(item["probability"]))
    mode_score = mode["score"]
    representative.append({"score": mode_score, "reason": "score repère exact le plus probable", "show_probability": False})
    for key in ("large_favorite_win", "favorite_4_plus_goals", "open_match", "blowout"):
        row = next(item for item in scenario_families if item["key"] == key)
        for score in row["representative_scores"]:
            if score not in {item["score"] for item in representative}:
                representative.append({"score": score, "reason": f"représente le scénario {row['label'].lower()}", "show_probability": False})
                break
        if len(representative) >= 5:
            break
    main_label = f"{favorite_name} favori, avec lecture par scénarios plutôt que par score exact isolé"
    confidence = "high" if max(markets["home_win"], markets["away_win"]) >= 0.60 else "medium" if max(markets["home_win"], markets["away_win"]) >= 0.45 else "low"
    return {
        "fixture_id": prediction.get("fixture_id"), "match_id": prediction["match_id"],
        "match_label": f"{home} - {away}",
        "main_reading": {"label": main_label, "confidence": confidence},
        "outcome_probabilities": {"home_win": markets["home_win"], "draw": markets["draw"], "away_win": markets["away_win"]},
        "scenario_families": scenario_families,
        "scenario_signals": {
            "large_win_visible": signals["large_favorite_win"] >= THRESHOLDS["large_favorite_win"],
            "favorite_4_plus_goals_visible": signals["favorite_4_plus_goals"] >= THRESHOLDS["favorite_scores_4_plus"],
            "over_3_5_visible": markets["over_3_5"] >= THRESHOLDS["over_3_5"],
            "blowout_visible": signals["blowout"] >= THRESHOLDS["blowout"],
        },
        "display_scores": {"mode_score": mode_score, "representative_scores": representative},
        "ui_policy": {
            "do_not_center_exact_score_percentages": True,
            "show_scenario_probabilities_first": True,
            "force_large_win_signal_if_threshold_met": True,
            "exact_score_percentages_location": "advanced_detail",
        },
    }


def main() -> None:
    predictions = load_json(DATA_DIR / "generated" / "predictions.json")
    payload = {
        "version": "v2.28",
        "thresholds": THRESHOLDS,
        "matrix_policy": {
            "score_repere_first_level": True,
            "exact_score_percentages_decentered": True,
            "scenario_probabilities_first": True,
        },
        "matches": [build(prediction) for prediction in predictions],
    }
    publish(payload)
    print(f"V2.28 scenario-aware score matrix: matches={len(payload['matches'])}")


if __name__ == "__main__":
    main()
