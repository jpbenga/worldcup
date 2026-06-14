"""Build visible single-bookmaker odds cards and responsible value badges."""

from __future__ import annotations

import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.build_match_odds_value_signals_v2_23 import MIN_EDGE, MIN_EV, canonical_market, selection_key
from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, utc_now, write_json


def publish(name: str, payload: dict) -> None:
    target = DATA_DIR / "generated" / name
    write_json(payload, target)
    shutil.copy2(target, DATA_DIR / "snapshots" / name)
    shutil.copy2(target, FRONTEND_DATA_DIR / name)


def freshness(updated: str) -> str:
    try:
        stamp = datetime.fromisoformat(updated.replace("Z", "+00:00"))
        return "fresh" if (datetime.now(timezone.utc) - stamp).total_seconds() <= 48 * 3600 else "stale"
    except (ValueError, TypeError):
        return "unknown"


def display_label(key: str, prediction: dict) -> str:
    return {
        "home_win": prediction["home_team"], "draw": "Nul", "away_win": prediction["away_team"],
        "double_chance_1X": f"{prediction['home_team']} ou nul", "double_chance_X2": f"Nul ou {prediction['away_team']}",
        "double_chance_12": f"{prediction['home_team']} ou {prediction['away_team']}",
        "draw_no_bet_home": prediction["home_team"], "draw_no_bet_away": prediction["away_team"],
        "over_2_5": "Plus de 2,5 buts", "under_2_5": "Moins de 2,5 buts",
        "btts_yes": "Les deux marquent", "btts_no": "Au moins une équipe ne marque pas",
    }.get(key, key)


def main() -> None:
    odds = load_json(DATA_DIR / "generated/api_football_odds_snapshot_v2_23.json")
    reference = load_json(DATA_DIR / "generated/reference_bookmaker_v2_23_1.json").get("selected_bookmaker")
    predictions = {str(row["fixture_id"]): row for row in load_json(DATA_DIR / "generated/predictions.json")}
    statuses = {str(row["fixture_id"]): row["status"] for row in load_json(DATA_DIR / "generated/worldcup_2026_results_v2_6.json")["fixtures"]}
    fixtures = []
    for fixture in odds.get("fixtures", []):
        prediction = predictions.get(str(fixture["fixture_id"]))
        bookmaker = next((row for row in fixture["bookmakers"] if reference and row["bookmaker_id"] == reference["id"]), None)
        if not prediction or not bookmaker:
            continue
        fresh = freshness(fixture.get("odds_updated_at", ""))
        markets, interesting = [], []
        for raw_market in bookmaker["markets"]:
            market = canonical_market(raw_market["name"])
            mapped = [(row, selection_key(market, row["name"], prediction)) for row in raw_market["outcomes"]] if market else []
            mapped = [(row, key) for row, key in mapped if key and key in prediction["markets"]]
            if not market or len(mapped) < 2:
                continue
            implied_sum = sum(1 / row["decimal_odds"] for row, _ in mapped)
            outcomes = []
            for row, key in mapped:
                model_probability = prediction["markets"][key]
                market_probability = (1 / row["decimal_odds"]) / implied_sum
                edge = model_probability - market_probability
                expected_value = model_probability * row["decimal_odds"] - 1
                is_interesting = (
                    expected_value >= MIN_EV and edge >= MIN_EDGE and prediction.get("confidence") != "low"
                    and fresh == "fresh" and statuses.get(str(fixture["fixture_id"])) == "not_started"
                )
                outcome = {
                    "label": display_label(key, prediction), "odds": row["decimal_odds"], "simuai_probability": model_probability,
                    "market_probability": market_probability, "edge": edge, "expected_value": expected_value,
                    "is_interesting": is_interesting,
                }
                outcomes.append(outcome)
                if is_interesting:
                    interesting.append({"market": market, **outcome})
            markets.append({"market_key": market.lower().replace(" ", "_"), "market_label": market, "outcomes": outcomes})
        interesting.sort(key=lambda row: (row["expected_value"], row["edge"]), reverse=True)
        fixtures.append({
            "fixture_id": fixture["fixture_id"], "match_id": fixture["match_id"],
            "match_label": f"{fixture['home_team']} vs {fixture['away_team']}", "status": statuses.get(str(fixture["fixture_id"]), "unknown"),
            "odds_freshness": fresh, "odds_updated_at": fixture.get("odds_updated_at", ""), "markets": markets,
            "best_value_signal": interesting[0] if interesting else None,
        })
    payload = {
        "version": "v2.23.1", "generated_at": utc_now(), "bookmaker": reference, "fixtures": fixtures,
        "responsible_display": {"disclaimer": "Signal statistique, sans garantie de résultat."},
        "warnings": [] if reference else ["Cotes indisponibles : aucun bookmaker de référence sélectionné."],
    }
    publish("match_reference_odds_view_model_v2_23_1.json", payload)
    print(f"V2.23.1 reference odds: bookmaker={reference['name'] if reference else 'none'}, fixtures={len(fixtures)}")


if __name__ == "__main__":
    main()
