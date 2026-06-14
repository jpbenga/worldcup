"""Compare SimuAI model probabilities with complete bookmaker markets."""

from __future__ import annotations

import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, utc_now, write_json

MIN_EV, MIN_EDGE = 0.05, 0.04


def publish(name: str, payload: dict) -> None:
    target = DATA_DIR / "generated" / name
    write_json(payload, target)
    shutil.copy2(target, DATA_DIR / "snapshots" / name)
    shutil.copy2(target, FRONTEND_DATA_DIR / name)


def canonical_market(name: str) -> str | None:
    return {
        "match winner": "1X2",
        "double chance": "Double chance",
        "home/away": "Draw no bet",
        "draw no bet": "Draw no bet",
        "goals over/under": "Over/Under 2.5",
        "both teams score": "Both teams to score",
        "both teams to score": "Both teams to score",
    }.get(name.strip().lower())


def selection_key(market: str, name: str, prediction: dict) -> str | None:
    value = name.strip().lower()
    home, away = prediction["home_team"].lower(), prediction["away_team"].lower()
    if market == "1X2":
        return "home_win" if value in {"home", "1"} or value == home else "draw" if value in {"draw", "x"} else "away_win" if value in {"away", "2"} or value == away else None
    if market == "Double chance":
        return {"home/draw": "double_chance_1X", "1x": "double_chance_1X", "draw/away": "double_chance_X2", "x2": "double_chance_X2", "home/away": "double_chance_12", "12": "double_chance_12"}.get(value)
    if market == "Draw no bet":
        return "draw_no_bet_home" if value in {"home", "1"} or value == home else "draw_no_bet_away" if value in {"away", "2"} or value == away else None
    if market == "Over/Under 2.5":
        return "over_2_5" if value in {"over 2.5", "over 2,5"} else "under_2_5" if value in {"under 2.5", "under 2,5"} else None
    if market == "Both teams to score":
        return "btts_yes" if value in {"yes", "oui"} else "btts_no" if value in {"no", "non"} else None
    return None


def fresh(updated: str) -> str:
    if not updated:
        return "unknown"
    try:
        stamp = datetime.fromisoformat(updated.replace("Z", "+00:00"))
        return "fresh" if (datetime.now(timezone.utc) - stamp).total_seconds() <= 48 * 3600 else "stale"
    except ValueError:
        return "unknown"


def main() -> None:
    odds = load_json(DATA_DIR / "generated/api_football_odds_snapshot_v2_23.json")
    predictions = {str(row["fixture_id"]): row for row in load_json(DATA_DIR / "generated/predictions.json")}
    statuses = {str(row["fixture_id"]): row["status"] for row in load_json(DATA_DIR / "generated/worldcup_2026_results_v2_6.json")["fixtures"]}
    fixtures = []
    for fixture in odds.get("fixtures", []):
        prediction = predictions.get(str(fixture["fixture_id"]))
        if not prediction or statuses.get(str(fixture["fixture_id"])) != "not_started":
            continue
        candidates, non_comparable = {}, []
        freshness = fresh(fixture.get("odds_updated_at", ""))
        for bookmaker in fixture["bookmakers"]:
            for raw_market in bookmaker["markets"]:
                market = canonical_market(raw_market["name"])
                mapped = [(row, selection_key(market, row["name"], prediction)) for row in raw_market["outcomes"]] if market else []
                mapped = [(row, key) for row, key in mapped if key and key in prediction["markets"]]
                if not market or len(mapped) != len(raw_market["outcomes"]) or len(mapped) < 2:
                    non_comparable.append({"bookmaker": bookmaker["name"], "market": raw_market["name"], "reason": "No complete matching SimuAI market."})
                    continue
                implied_sum = sum(1 / row["decimal_odds"] for row, _ in mapped)
                for row, key in mapped:
                    model_probability = prediction["markets"][key]
                    market_probability = (1 / row["decimal_odds"]) / implied_sum
                    candidates.setdefault((market, key), []).append({
                        "selection": row["name"], "decimal_odds": row["decimal_odds"], "market_probability": market_probability,
                        "model_probability": model_probability, "bookmaker": bookmaker["name"],
                    })
        all_signals = []
        for (market, _), rows in candidates.items():
            coverage = len(rows)
            model_probability = rows[0]["model_probability"]
            decimal_odds = median(row["decimal_odds"] for row in rows)
            market_probability = median(row["market_probability"] for row in rows)
            edge = model_probability - market_probability
            ev = model_probability * decimal_odds - 1
            eligible = ev >= MIN_EV and edge >= MIN_EDGE and prediction.get("confidence") != "low" and freshness == "fresh" and coverage >= 3
            all_signals.append({
                "label": "Cote intéressante" if eligible else "Écart modèle / marché",
                "market": market, "selection": rows[0]["selection"], "decimal_odds": decimal_odds,
                "model_probability": model_probability, "market_probability": market_probability,
                "edge": edge, "expected_value": ev, "confidence": prediction.get("confidence"),
                "freshness": freshness, "bookmaker": f"Consensus de {coverage} bookmakers", "bookmaker_count": coverage,
                "odds_updated_at": fixture.get("odds_updated_at", ""),
                "market_has_enough_outcomes": coverage >= 3, "eligible": eligible,
                "reason": "SimuAI estime cette issue plus probable que le consensus marché après normalisation." if eligible else "Signal sous les seuils responsables.",
            })
        eligible = sorted((row for row in all_signals if row["eligible"]), key=lambda row: (row["expected_value"], row["edge"]), reverse=True)
        fixtures.append({
            "fixture_id": fixture["fixture_id"], "match_id": fixture["match_id"], "match_label": f"{fixture['home_team']} vs {fixture['away_team']}",
            "best_value_signal": eligible[0] if eligible else None, "all_signals": all_signals, "non_comparable_markets": non_comparable,
            "warnings": [] if eligible else ["Aucune cote intéressante détectée : marché aligné, cote stale, confiance faible ou données insuffisantes."],
        })
    payload = {
        "version": "v2.23", "generated_at": utc_now(), "odds_available": odds.get("available", False),
        "thresholds": {"expected_value": MIN_EV, "edge": MIN_EDGE, "model_confidence_excluded": "low", "freshness_required": "fresh"},
        "fixtures": fixtures,
        "responsible_display": {"is_betting_advice": False, "uses_guaranteed_language": False, "disclaimer": "Signal statistique, sans garantie de résultat."},
        "limitations": ["Only complete API-Football markets with an existing SimuAI probability are comparable."],
    }
    publish("match_odds_value_signals_v2_23.json", payload)
    print(f"V2.23 odds value signals: fixtures={len(fixtures)}, highlighted={sum(bool(row['best_value_signal']) for row in fixtures)}")


if __name__ == "__main__":
    main()
