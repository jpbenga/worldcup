"""Secondary market evaluation, including explicit DNB win/loss/push metrics."""

from __future__ import annotations

from typing import Any

THRESHOLDS = (0.0, 0.55, 0.60, 0.65, 0.70)


def binary_market_metrics(probabilities: list[float], labels: list[int]) -> dict[str, Any]:
    result = {}
    for threshold in THRESHOLDS:
        indexes = [i for i, probability in enumerate(probabilities) if probability >= threshold]
        wins = sum(labels[i] for i in indexes)
        result[f"{threshold:.2f}"] = {
            "threshold": threshold,
            "total_predictions": len(labels),
            "coverage_if_thresholded": len(indexes) / len(labels),
            "selections": len(indexes),
            "wins": wins,
            "losses": len(indexes) - wins,
            "accuracy": wins / len(indexes) if indexes else None,
            "win_rate": wins / len(indexes) if indexes else None,
            "brier_if_binary_market": sum((probabilities[i] - labels[i]) ** 2 for i in indexes) / len(indexes) if indexes else None,
            "average_confidence": sum(probabilities[i] for i in indexes) / len(indexes) if indexes else None,
        }
    return result


def dnb_metrics(home_prob: list[float], away_prob: list[float], rows: list[dict[str, Any]]) -> dict[str, Any]:
    result = {}
    for threshold in THRESHOLDS:
        records = []
        for hp, ap, row in zip(home_prob, away_prob, rows):
            side, confidence = ("home", hp) if hp >= ap else ("away", ap)
            if confidence < threshold:
                continue
            home, away = int(row["actual_home_score"]), int(row["actual_away_score"])
            outcome = "push" if home == away else "win" if (side == "home" and home > away) or (side == "away" and away > home) else "loss"
            records.append((outcome, confidence))
        wins = sum(outcome == "win" for outcome, _ in records)
        losses = sum(outcome == "loss" for outcome, _ in records)
        pushes = sum(outcome == "push" for outcome, _ in records)
        total = len(records)
        result[f"{threshold:.2f}"] = {
            "threshold": threshold,
            "number_of_bets": total,
            "coverage": total / len(rows),
            "wins": wins,
            "losses": losses,
            "pushes": pushes,
            "win_rate_excluding_pushes": wins / (wins + losses) if wins + losses else None,
            "non_loss_rate_including_pushes": (wins + pushes) / total if total else None,
            "push_rate": pushes / total if total else None,
            "loss_rate": losses / total if total else None,
            "average_confidence": sum(conf for _, conf in records) / total if total else None,
        }
    return result


def evaluate_secondary_markets(
    binary_probabilities: dict[str, list[float]], rows: list[dict[str, Any]], analytical: list[dict[str, float]]
) -> dict[str, Any]:
    binary = {
        target: binary_market_metrics(probabilities, [row["labels"][target] for row in rows])
        for target, probabilities in binary_probabilities.items()
    }
    market_sources = {
        "over_0_5": [market["over_0_5"] for market in analytical],
        "over_1_5": binary_probabilities["over_1_5"],
        "over_2_5": binary_probabilities["over_2_5"],
        "over_3_5": binary_probabilities["over_3_5"],
        "under_1_5": [1 - value for value in binary_probabilities["over_1_5"]],
        "under_2_5": [1 - value for value in binary_probabilities["over_2_5"]],
        "under_3_5": [1 - value for value in binary_probabilities["over_3_5"]],
        "btts_yes": binary_probabilities["btts_yes"],
        "btts_no": [1 - value for value in binary_probabilities["btts_yes"]],
        "clean_sheet_home": [market["clean_sheet_home"] for market in analytical],
        "clean_sheet_away": [market["clean_sheet_away"] for market in analytical],
        "team_home_over_0_5": binary_probabilities["home_team_scores"],
        "team_away_over_0_5": binary_probabilities["away_team_scores"],
        "team_home_over_1_5": binary_probabilities["home_over_1_5"],
        "team_away_over_1_5": binary_probabilities["away_over_1_5"],
        "double_chance_1X": binary_probabilities["double_chance_1X"],
        "double_chance_X2": binary_probabilities["double_chance_X2"],
        "double_chance_12": binary_probabilities["double_chance_12"],
    }
    label_names = {
        "over_0_5": "over_0_5",
        "team_home_over_0_5": "home_team_scores",
        "team_away_over_0_5": "away_team_scores",
        "team_home_over_1_5": "home_over_1_5",
        "team_away_over_1_5": "away_over_1_5",
    }
    complete = {
        name: binary_market_metrics(probabilities, [row["labels"][label_names.get(name, name)] for row in rows])
        for name, probabilities in market_sources.items()
    }
    dnb = dnb_metrics(
        [market["draw_no_bet_home"] for market in analytical],
        [market["draw_no_bet_away"] for market in analytical],
        rows,
    )
    return {
        "draw_no_bet": dnb,
        "over_under": {key: value for key, value in complete.items() if key.startswith(("over_", "under_"))},
        "btts": {key: value for key, value in complete.items() if key.startswith("btts_")},
        "double_chance": {key: value for key, value in complete.items() if key.startswith("double_chance_")},
        "team_goals": {key: value for key, value in complete.items() if key.startswith("team_")},
        "clean_sheet": {key: value for key, value in complete.items() if key.startswith("clean_sheet_")},
        "all_markets": complete,
        "xgboost_binary_markets": binary,
        "performance_by_confidence_bucket": "Threshold tables 0.00/0.55/0.60/0.65/0.70 are embedded per market.",
    }
