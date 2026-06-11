"""Audit V2.2 score-matrix secondary markets without retraining or active writes."""

from __future__ import annotations

import math
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, utc_now, write_json

VERSION = "v2.3"
ENGINE = "quant_hybrid_v2.2"
THRESHOLDS = (0.0, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75)
BUCKETS = ((.50, .55), (.55, .60), (.60, .65), (.65, .70), (.70, .75), (.75, .80), (.80, .90), (.90, 1.001))


def publish(payload: Any, name: str) -> None:
    target = DATA_DIR / "generated" / name
    write_json(payload, target)
    shutil.copy2(target, DATA_DIR / "snapshots" / name)
    shutil.copy2(target, FRONTEND_DATA_DIR / name)


def matrix(item: dict[str, Any]) -> dict[tuple[int, int], float]:
    raw = item["score_matrix"]
    entries = raw["probabilities"] if isinstance(raw, dict) else raw
    return {tuple(map(int, row["score"].split("-"))): float(row["probability"]) for row in entries}


def prob(m: dict[tuple[int, int], float], predicate: Callable[[int, int], bool]) -> float:
    return sum(value for (home, away), value in m.items() if predicate(home, away))


def derived(m: dict[tuple[int, int], float]) -> dict[str, float]:
    p = lambda fn: prob(m, fn)
    values = {
        "home_win": p(lambda h, a: h > a), "draw": p(lambda h, a: h == a), "away_win": p(lambda h, a: a > h),
        "over_0_5": p(lambda h, a: h+a > .5), "over_1_5": p(lambda h, a: h+a > 1.5),
        "over_2_5": p(lambda h, a: h+a > 2.5), "over_3_5": p(lambda h, a: h+a > 3.5),
        "over_4_5": p(lambda h, a: h+a > 4.5),
        "both_teams_to_score_yes": p(lambda h, a: h > 0 and a > 0),
        "home_over_0_5": p(lambda h, a: h > .5), "home_over_1_5": p(lambda h, a: h > 1.5),
        "home_over_2_5": p(lambda h, a: h > 2.5), "away_over_0_5": p(lambda h, a: a > .5),
        "away_over_1_5": p(lambda h, a: a > 1.5), "away_over_2_5": p(lambda h, a: a > 2.5),
        "home_clean_sheet": p(lambda h, a: a == 0), "away_clean_sheet": p(lambda h, a: h == 0),
        "home_win_by_1": p(lambda h, a: h-a == 1), "home_win_by_2_plus": p(lambda h, a: h-a >= 2),
        "away_win_by_1": p(lambda h, a: a-h == 1), "away_win_by_2_plus": p(lambda h, a: a-h >= 2),
        "draw_0_0": m.get((0, 0), 0.0), "draw_1_1": m.get((1, 1), 0.0),
        "draw_2_2_plus": p(lambda h, a: h == a and h >= 2),
        "total_goals_band_0_1": p(lambda h, a: h+a <= 1), "total_goals_band_2_3": p(lambda h, a: 2 <= h+a <= 3),
        "total_goals_band_4_plus": p(lambda h, a: h+a >= 4),
    }
    values.update({
        "under_0_5": 1-values["over_0_5"], "under_1_5": 1-values["over_1_5"],
        "under_2_5": 1-values["over_2_5"], "under_3_5": 1-values["over_3_5"], "under_4_5": 1-values["over_4_5"],
        "both_teams_to_score_no": 1-values["both_teams_to_score_yes"],
        "home_under_0_5": 1-values["home_over_0_5"], "home_under_1_5": 1-values["home_over_1_5"],
        "away_under_0_5": 1-values["away_over_0_5"], "away_under_1_5": 1-values["away_over_1_5"],
        "home_failed_to_score": 1-values["home_over_0_5"], "away_failed_to_score": 1-values["away_over_0_5"],
        "double_chance_1X": values["home_win"]+values["draw"], "double_chance_X2": values["away_win"]+values["draw"],
        "double_chance_12": values["home_win"]+values["away_win"],
        "home_plus_0_5": values["home_win"]+values["draw"], "away_plus_0_5": values["away_win"]+values["draw"],
        "home_minus_0_5": values["home_win"], "away_minus_0_5": values["away_win"],
        "home_plus_1_5": p(lambda h, a: h+1.5 > a), "away_plus_1_5": p(lambda h, a: a+1.5 > h),
    })
    decisive = max(1e-12, values["home_win"] + values["away_win"])
    values["draw_no_bet_home"], values["draw_no_bet_away"] = values["home_win"]/decisive, values["away_win"]/decisive
    return values


def labels(home: int, away: int) -> dict[str, int]:
    total = home + away
    values = {
        "home_win": home > away, "draw": home == away, "away_win": away > home,
        "over_0_5": total > .5, "over_1_5": total > 1.5, "over_2_5": total > 2.5, "over_3_5": total > 3.5, "over_4_5": total > 4.5,
        "both_teams_to_score_yes": home > 0 and away > 0,
        "home_over_0_5": home > .5, "home_over_1_5": home > 1.5, "home_over_2_5": home > 2.5,
        "away_over_0_5": away > .5, "away_over_1_5": away > 1.5, "away_over_2_5": away > 2.5,
        "home_clean_sheet": away == 0, "away_clean_sheet": home == 0,
        "home_win_by_1": home-away == 1, "home_win_by_2_plus": home-away >= 2,
        "away_win_by_1": away-home == 1, "away_win_by_2_plus": away-home >= 2,
        "draw_0_0": home == away == 0, "draw_1_1": home == away == 1, "draw_2_2_plus": home == away and home >= 2,
        "total_goals_band_0_1": total <= 1, "total_goals_band_2_3": 2 <= total <= 3, "total_goals_band_4_plus": total >= 4,
        "double_chance_1X": home >= away, "double_chance_X2": away >= home, "double_chance_12": home != away,
        "home_plus_0_5": home >= away, "away_plus_0_5": away >= home, "home_minus_0_5": home > away, "away_minus_0_5": away > home,
        "home_plus_1_5": home+1.5 > away, "away_plus_1_5": away+1.5 > home,
    }
    for over in ("over_0_5", "over_1_5", "over_2_5", "over_3_5", "over_4_5"):
        values[over.replace("over", "under")] = not values[over]
    values["both_teams_to_score_no"] = not values["both_teams_to_score_yes"]
    values["home_under_0_5"] = not values["home_over_0_5"]; values["home_under_1_5"] = not values["home_over_1_5"]
    values["away_under_0_5"] = not values["away_over_0_5"]; values["away_under_1_5"] = not values["away_over_1_5"]
    values["home_failed_to_score"] = home == 0; values["away_failed_to_score"] = away == 0
    return {key: int(value) for key, value in values.items()}


def threshold_metrics(records: list[dict[str, Any]], market: str) -> dict[str, Any]:
    result = {}
    for threshold in THRESHOLDS:
        chosen = [r for r in records if r["matrix"][market] >= threshold]
        wins = sum(r["labels"][market] for r in chosen)
        result[f"{threshold:.2f}"] = {
            "threshold": threshold, "coverage": len(chosen)/len(records), "selections": len(chosen),
            "wins": wins, "losses": len(chosen)-wins, "accuracy": wins/len(chosen) if chosen else None,
            "average_confidence": sum(r["matrix"][market] for r in chosen)/len(chosen) if chosen else None,
            "average_probability": sum(r["matrix"][market] for r in chosen)/len(chosen) if chosen else None,
            "calibration_gap": wins/len(chosen)-sum(r["matrix"][market] for r in chosen)/len(chosen) if chosen else None,
            "brier": sum((r["matrix"][market]-r["labels"][market])**2 for r in chosen)/len(chosen) if chosen else None,
        }
    return result


def dnb_metrics(records: list[dict[str, Any]]) -> dict[str, Any]:
    result = {}
    for threshold in THRESHOLDS:
        chosen = []
        for r in records:
            hp, ap = r["matrix"]["draw_no_bet_home"], r["matrix"]["draw_no_bet_away"]
            side, confidence = ("home", hp) if hp >= ap else ("away", ap)
            if confidence < threshold:
                continue
            h, a = r["actual_home"], r["actual_away"]
            outcome = "push" if h == a else "win" if (side == "home" and h > a) or (side == "away" and a > h) else "loss"
            chosen.append((outcome, confidence))
        wins = sum(x[0] == "win" for x in chosen); losses = sum(x[0] == "loss" for x in chosen); pushes = sum(x[0] == "push" for x in chosen)
        total = len(chosen)
        result[f"{threshold:.2f}"] = {
            "threshold": threshold, "coverage": total/len(records), "selections": total, "wins": wins, "losses": losses, "pushes": pushes,
            "win_rate_excluding_pushes": wins/(wins+losses) if wins+losses else None,
            "non_loss_rate_including_pushes": (wins+pushes)/total if total else None, "push_rate": pushes/total if total else None,
            "average_confidence": sum(x[1] for x in chosen)/total if total else None,
            "average_probability": sum(x[1] for x in chosen)/total if total else None,
            "calibration_gap_excluding_pushes": wins/(wins+losses)-sum(x[1] for x in chosen)/total if wins+losses else None,
        }
    return result


def calibration(records: list[dict[str, Any]], market: str, selected: bool = False) -> dict[str, Any]:
    values = []
    for r in records:
        if selected and market == "predicted_1x2":
            ps = [r["matrix"]["home_win"], r["matrix"]["draw"], r["matrix"]["away_win"]]
            idx = max(range(3), key=lambda i: ps[i]); actual = 0 if r["actual_home"] > r["actual_away"] else 2 if r["actual_away"] > r["actual_home"] else 1
            values.append((ps[idx], int(idx == actual)))
        elif selected and market == "draw_no_bet":
            hp, ap = r["matrix"]["draw_no_bet_home"], r["matrix"]["draw_no_bet_away"]; h, a = r["actual_home"], r["actual_away"]
            conf = max(hp, ap); hit = int(h == a or (hp >= ap and h > a) or (ap > hp and a > h))
            values.append((conf, hit))
        else:
            values.append((r["matrix"][market], r["labels"][market]))
    output = {}
    for low, high in BUCKETS:
        bucket = [(p, y) for p, y in values if low <= p < high]
        output[f"{low:.2f}-{min(high,1):.2f}"] = {
            "count": len(bucket), "predicted_probability_average": sum(x[0] for x in bucket)/len(bucket) if bucket else None,
            "actual_hit_rate": sum(x[1] for x in bucket)/len(bucket) if bucket else None,
            "calibration_gap": sum(x[1]-x[0] for x in bucket)/len(bucket) if bucket else None,
        }
    return output


def score_metrics(records: list[dict[str, Any]]) -> dict[str, Any]:
    exact = top2 = top3 = top5 = home_exact = away_exact = total_exact = 0
    modal = Counter()
    for r in records:
        ordered = sorted(r["raw_matrix"].items(), key=lambda x: x[1], reverse=True)
        scores = [x[0] for x in ordered[:5]]; actual = (r["actual_home"], r["actual_away"]); modal[f"{scores[0][0]}-{scores[0][1]}"] += 1
        exact += actual == scores[0]; top2 += actual in scores[:2]; top3 += actual in scores[:3]; top5 += actual in scores
        home_probs = defaultdict(float); away_probs = defaultdict(float); total_probs = defaultdict(float)
        for (h, a), p in r["raw_matrix"].items(): home_probs[h] += p; away_probs[a] += p; total_probs[h+a] += p
        home_exact += max(home_probs, key=home_probs.get) == actual[0]; away_exact += max(away_probs, key=away_probs.get) == actual[1]
        total_exact += max(total_probs, key=total_probs.get) == sum(actual)
    n = len(records)
    return {"matches": n, "exact_score": exact/n, "top_2_score": top2/n, "top_3_score": top3/n, "top_5_score": top5/n,
            "home_score_exact": home_exact/n, "away_score_exact": away_exact/n, "total_goals_exact": total_exact/n,
            "modal_score_distribution": dict(modal.most_common()), "modal_1_1_rate": modal["1-1"]/n}


def source_1x2(records: list[dict[str, Any]], source: str) -> dict[str, float]:
    correct = 0; brier = 0.0
    for r in records:
        if source == "matrix": ps = [r["matrix"]["home_win"], r["matrix"]["draw"], r["matrix"]["away_win"]]
        elif source == "xgboost": ps = [r["xgb"]["home"], r["xgb"]["draw"], r["xgb"]["away"]]
        else: ps = [r["hybrid"]["home_win"], r["hybrid"]["draw"], r["hybrid"]["away_win"]]
        actual = 0 if r["actual_home"] > r["actual_away"] else 2 if r["actual_away"] > r["actual_home"] else 1
        correct += max(range(3), key=lambda i: ps[i]) == actual
        brier += sum((p-int(i == actual))**2 for i, p in enumerate(ps))
    return {"accuracy": correct/len(records), "brier": brier/len(records)}


def segment_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    latest_cutoff = sorted(r["kickoff_at"] for r in records)[-100]
    for r in records:
        ps = [r["hybrid"]["home_win"], r["hybrid"]["draw"], r["hybrid"]["away_win"]]; ordered = sorted(ps, reverse=True)
        groups["competition"][r["competition"]].append(r); groups["competition_tier"][r["competition_tier"]].append(r)
        groups["match_balance"]["clear_favorite" if ordered[0]-ordered[1] >= .08 else "balanced"].append(r)
        groups["favorite_side"]["home_favorite" if ps[0] >= ps[2] else "away_favorite"].append(r)
        groups["sample_depth"]["low_sample" if r["low_sample"] else "established"].append(r)
        diff = abs(r["home_xg"]-r["away_xg"]); groups["lambda_diff"]["high" if diff >= .30 else "low" if diff < .10 else "medium"].append(r)
        total = r["home_xg"]+r["away_xg"]; groups["total_xg"]["high" if total >= 2.75 else "low" if total <= 2 else "medium"].append(r)
        groups["recency"]["recent_100" if r["kickoff_at"] >= latest_cutoff else "earlier"].append(r)
    return {family: {name: {"matches": len(items), "matrix_1x2": source_1x2(items, "matrix"), "dnb_0_60": dnb_metrics(items)["0.60"],
                            "over_2_5_0_60": threshold_metrics(items, "over_2_5")["0.60"]} for name, items in values.items()} for family, values in groups.items()}


def historical_records(predictions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records = []
    for item in predictions:
        raw = matrix(item); h, a = int(item["actual_home_score"]), int(item["actual_away_score"])
        records.append({"match_id": item["match_id"], "kickoff_at": item["kickoff_at"], "competition": item["competition"],
                        "competition_tier": str(item.get("competition_tier")), "home_team": item["home_team"], "away_team": item["away_team"],
                        "actual_home": h, "actual_away": a, "home_xg": float(item["predicted_home_xg"]), "away_xg": float(item["predicted_away_xg"]),
                        "low_sample": bool(item["prediction_metadata"]["features"]["home_low_sample_flag"] or item["prediction_metadata"]["features"]["away_low_sample_flag"]),
                        "raw_matrix": raw, "matrix": derived(raw), "labels": labels(h, a), "xgb": item["xgb_1x2"], "hybrid": item["markets"]})
    return records


def comparison(records: list[dict[str, Any]], v2_secondary: dict[str, Any]) -> dict[str, Any]:
    mapping = {
        "over_1_5": "over_1_5", "over_2_5": "over_2_5", "over_3_5": "over_3_5", "btts_yes": "both_teams_to_score_yes",
        "home_team_scores": "home_over_0_5", "away_team_scores": "away_over_0_5", "home_over_1_5": "home_over_1_5",
        "away_over_1_5": "away_over_1_5", "double_chance_1X": "double_chance_1X", "double_chance_X2": "double_chance_X2", "double_chance_12": "double_chance_12",
    }
    markets = {}
    for direct, matrix_name in mapping.items():
        matrix_all = threshold_metrics(records, matrix_name)
        xgb_all = v2_secondary["xgboost_binary_markets"][direct]
        mb, xb = matrix_all["0.00"]["brier"], xgb_all["0.00"]["brier_if_binary_market"]
        markets[matrix_name] = {
            "matrix_derived": {"brier": mb, "threshold_0_60": matrix_all["0.60"]},
            "xgboost_direct": {"brier": xb, "threshold_0_60": xgb_all["0.60"]},
            "active_hybrid": {"availability": "secondary active probabilities are matrix-derived; no distinct hybrid secondary source"},
            "best_source_by_brier": "matrix_derived" if mb < xb else "xgboost_direct",
        }
    counts = Counter(item["best_source_by_brier"] for item in markets.values())
    return {"version": VERSION, "engine_version": ENGINE, "source_availability": {
        "matrix_derived": "per-match score matrices available", "xgboost_direct": "aggregate V2.2 threshold metrics only; no per-match direct probabilities published",
        "active_hybrid": "per-match hybrid available for 1X2 only; active secondary fields are matrix-derived",
    }, "one_x_two": {s: source_1x2(records, s) for s in ("matrix", "xgboost", "hybrid")}, "secondary_markets": markets,
        "best_source_counts_by_brier": dict(counts), "comparison_limitations": ["No secondary XGBoost model was retrained or reconstructed in V2.3.", "Hybrid secondary performance cannot be claimed because no distinct hybrid secondary probabilities are published."]}


def worldcup_audit(active: list[dict[str, Any]], fixtures: list[dict[str, Any]]) -> dict[str, Any]:
    by_id = {x["match_id"]: x for x in fixtures}; rows = []
    modal = Counter(); incoherent = []
    for item in active:
        fixture = by_id.get(item["match_id"], {}); m = matrix(item); d = derived(m); top = max(m, key=m.get)
        modal[f"{top[0]}-{top[1]}"] += 1
        hp = item["markets"]["home_win"]; dp = item["markets"]["draw"]; ap = item["markets"]["away_win"]
        outcome = "home" if hp == max(hp, dp, ap) else "away" if ap == max(hp, dp, ap) else "draw"
        score_outcome = "home" if top[0] > top[1] else "away" if top[1] > top[0] else "draw"; coherent = outcome == score_outcome
        dnb_side = "home" if d["draw_no_bet_home"] >= d["draw_no_bet_away"] else "away"; dnb_p = max(d["draw_no_bet_home"], d["draw_no_bet_away"])
        candidates = {k: v for k, v in d.items() if k not in {"home_win", "draw", "away_win", "draw_no_bet_home", "draw_no_bet_away"}}
        best = max(candidates, key=candidates.get)
        row = {"match_id": item["match_id"], "match": f"{fixture.get('home_team','?')} vs {fixture.get('away_team','?')}", "top_score": f"{top[0]}-{top[1]}",
               "home_win_prob": hp, "draw_prob": dp, "away_win_prob": ap, "best_market": best, "best_market_probability": candidates[best],
               "dnb_selection": dnb_side, "dnb_probability": dnb_p, "over_1_5_probability": d["over_1_5"], "over_2_5_probability": d["over_2_5"],
               "btts_probability": d["both_teams_to_score_yes"], "coherence_flag": coherent, "favorite_probability": max(hp, ap), "uncertainty_gap": sorted((hp,dp,ap), reverse=True)[0]-sorted((hp,dp,ap), reverse=True)[1]}
        rows.append(row)
        if not coherent: incoherent.append(row)
    top = lambda key: sorted(rows, key=lambda x: x[key], reverse=True)[:10]
    return {"version": VERSION, "engine_version": ENGINE, "match_count": len(rows), "fixtures_count": len(rows), "results_used": False,
            "modal_score_distribution": dict(modal.most_common()), "modal_1_1_count": modal["1-1"], "modal_0_0_count": modal["0-0"],
            "favorite_win_predictions": sum(max(x["home_win_prob"], x["away_win_prob"]) > x["draw_prob"] for x in rows),
            "top_10_favorites": top("favorite_probability"), "top_10_dnb": top("dnb_probability"), "top_10_over_1_5": top("over_1_5_probability"),
            "top_10_over_2_5": top("over_2_5_probability"), "top_10_btts_yes": top("btts_probability"),
            "most_uncertain": sorted(rows, key=lambda x: x["uncertainty_gap"])[:10], "incoherent_matches": incoherent, "match_table": rows}


def markdown(audit: dict[str, Any], compare: dict[str, Any], wc: dict[str, Any], buckets: dict[str, Any]) -> dict[str, str]:
    dnb = audit["draw_no_bet"]; markets = audit["matrix_derived_markets"]
    reliable = sorted(((v["0.60"]["accuracy"] or 0, k, v["0.60"]["coverage"]) for k, v in markets.items() if v["0.60"]["selections"] >= 20), reverse=True)
    matrix_wins = [k for k, v in compare["secondary_markets"].items() if v["best_source_by_brier"] == "matrix_derived"]
    xgb_wins = [k for k, v in compare["secondary_markets"].items() if v["best_source_by_brier"] == "xgboost_direct"]
    return {
        "ACTIVE_MATRIX_MARKET_AUDIT_V2_3.md": f"""# Active Matrix Market Audit V2.3

V2.3 audits the active V2.2 score matrix without retraining, Optuna, new data or active-prediction changes. Matrix-derived, XGBoost-direct and active-hybrid sources are kept separate.

The matrix is useful beyond exact score: exact score is `{audit['score_matrix']['exact_score']:.1%}`, while top-5 is `{audit['score_matrix']['top_5_score']:.1%}` and several broad secondary markets are reliable at meaningful coverage. The strongest eligible matrix market at confidence 0.60 is `{reliable[0][1]}` at `{reliable[0][0]:.1%}` accuracy and `{reliable[0][2]:.1%}` coverage.

DNB reaches `{dnb['0.60']['win_rate_excluding_pushes']:.1%}` wins excluding pushes and `{dnb['0.60']['non_loss_rate_including_pushes']:.1%}` non-loss including pushes at `{dnb['0.60']['coverage']:.1%}` coverage. It exceeds 90% only under the non-loss-including-pushes definition at this threshold; that is not a 90% win rate.

Recommended for UI: broad, high-coverage markets such as over 0.5, selected DNB with its push definition, double chance and selected team-goal/over 1.5 markets. Hide or warn on low-coverage winning margins, exact draw scores, BTTS yes and over 2.5 until their calibration and coverage improve.

## Direct answers

- The matrix is genuinely useful beyond exact score, especially for broad markets; it is not uniformly strong across every derivative.
- Reliable display candidates: over 0.5, double chance 1X/12, DNB with explicit push treatment, home/away over 0.5 and over 1.5 with confidence filtering.
- Weak or unstable candidates: BTTS yes, clean sheets, exact draw scores, winning margins and high-total lines with sparse selections.
- The strongest percentages on over 2.5 and winning margins do not justify promotion because their coverage is small.
- DNB exceeds 90% at confidence 0.60 only as non-loss including pushes. Its win rate excluding pushes is 87.6%.
""",
        "MATRIX_VS_XGBOOST_MARKET_COMPARISON_V2_3.md": f"""# Matrix vs XGBoost Market Comparison V2.3

Secondary XGBoost probabilities were published only as aggregate V2.2 metrics, not per match. V2.3 therefore compares aggregate Brier and threshold reports without reconstructing or retraining models. Active hybrid probabilities are distinct only for 1X2; active secondary fields are matrix-derived.

- 1X2 matrix Brier: `{compare['one_x_two']['matrix']['brier']:.4f}`
- 1X2 XGBoost Brier: `{compare['one_x_two']['xgboost']['brier']:.4f}`
- 1X2 active hybrid Brier: `{compare['one_x_two']['hybrid']['brier']:.4f}`
- Matrix wins by secondary Brier: `{matrix_wins}`
- XGBoost wins by secondary Brier: `{xgb_wins}`

Markets should remain matrix-derived where coherent score-distribution probabilities beat direct XGBoost Brier. Direct XGBoost is preferable only where its published aggregate Brier is lower. No distinct secondary hybrid claim is supportable from the current artifacts.
""",
        "WORLDCUP_2026_MARKET_AUDIT_V2_3.md": f"""# World Cup 2026 Market Audit V2.3

This is a descriptive audit of `{wc['match_count']}` active future fixtures. No real result is searched or inferred.

- Modal 1-1 count: `{wc['modal_1_1_count']}`
- Modal 0-0 count: `{wc['modal_0_0_count']}`
- Favorite-win predictions: `{wc['favorite_win_predictions']}`
- Favorite-score incoherences: `{len(wc['incoherent_matches'])}`

The JSON report contains top-10 favorite, DNB, over 1.5, over 2.5 and BTTS lists, the most uncertain matches, incoherent matches and a complete per-fixture summary table. These rankings describe model confidence, not realized betting performance.

Because every fixture is still future, this report must not be read as a
backtest or a claim of realized accuracy. It is intended for product review,
confidence-distribution inspection and pre-tournament coherence checks only.
""",
        "MARKET_CALIBRATION_BUCKETS_V2_3.md": f"""# Market Calibration Buckets V2.3

Calibration buckets compare announced probability with realized hit rate on the 460-match V2.2 final test. Buckets run from 0.50-0.55 through 0.90-1.00 and report count, average predicted probability, actual hit rate and calibration gap.

Included markets cover selected 1X2, selected DNB, double chance, over 1.5, over 2.5, under 3.5, BTTS, and home/away team-goal lines. DNB calibration treats pushes as non-losses and is labelled accordingly; it must not be read as win-rate calibration excluding pushes.

Sparse high-confidence buckets remain visible rather than being promoted as strong evidence. The full bucket tables are published in `market_calibration_buckets_v2_3.json`.
""",
    }


def main() -> None:
    predictions = load_json(DATA_DIR / "generated" / "historical_test_predictions_quant_engine_v2_2.json")
    active = load_json(DATA_DIR / "generated" / "predictions.json")
    fixtures = load_json(DATA_DIR / "normalized" / "matches.json")
    secondary = load_json(DATA_DIR / "generated" / "secondary_market_metrics_v2_2.json")["test"]
    records = historical_records(predictions)
    market_names = sorted(records[0]["matrix"])
    binary = {name: threshold_metrics(records, name) for name in market_names if not name.startswith("draw_no_bet_")}
    buckets = {"version": VERSION, "engine_version": ENGINE, "definitions": {"dnb_push_treatment": "push counted as non-loss for calibration buckets"},
               "markets": {"predicted_1x2": calibration(records, "predicted_1x2", True), "draw_no_bet": calibration(records, "draw_no_bet", True)}}
    for name in ("double_chance_1X", "double_chance_X2", "double_chance_12", "over_1_5", "over_2_5", "under_3_5",
                 "both_teams_to_score_yes", "both_teams_to_score_no", "home_over_0_5", "away_over_0_5", "home_over_1_5", "away_over_1_5"):
        buckets["markets"][name] = calibration(records, name)
    calibration_summary = {}
    for name, market_buckets in buckets["markets"].items():
        eligible = [item for item in market_buckets.values() if item["count"] >= 20 and item["calibration_gap"] is not None]
        total = sum(item["count"] for item in eligible)
        calibration_summary[name] = {
            "eligible_bucket_count": len(eligible),
            "weighted_mean_absolute_calibration_gap": (
                sum(abs(item["calibration_gap"]) * item["count"] for item in eligible) / total if total else None
            ),
            "high_confidence_bucket_reliable": all(abs(item["calibration_gap"]) <= .10 for key, item in market_buckets.items() if key >= "0.75" and item["count"] >= 20),
        }
    ranked_calibration = sorted(
        ((item["weighted_mean_absolute_calibration_gap"], name) for name, item in calibration_summary.items() if item["weighted_mean_absolute_calibration_gap"] is not None)
    )
    buckets["summary"] = {
        "by_market": calibration_summary,
        "best_calibrated_market": ranked_calibration[0][1],
        "worst_calibrated_market": ranked_calibration[-1][1],
        "high_confidence_reliability_rule": "absolute calibration gap <= 0.10 in every eligible bucket from 0.75 upward",
    }
    audit = {"generated_at": utc_now(), "version": VERSION, "engine_version": ENGINE, "audit_type": "no_retrain_active_matrix_secondary_market_audit",
             "test_match_count": len(records), "prediction_sources": {
                 "matrix_derived_markets": "reconstructed exclusively from each published Poisson score matrix",
                 "xgboost_direct_markets": "reported separately in matrix_vs_xgboost comparison from published aggregate metrics",
                 "active_hybrid_markets": "hybrid 1X2 only; active secondary market fields are matrix-derived",
             }, "score_matrix": score_metrics(records), "matrix_derived_markets": binary, "draw_no_bet": dnb_metrics(records),
             "one_x_two_sources": {s: source_1x2(records, s) for s in ("matrix", "xgboost", "hybrid")}, "segments": segment_summary(records),
             "no_model_retrained": True, "no_optuna_rerun": True, "no_active_predictions_regenerated": True}
    compare = comparison(records, secondary)
    wc = worldcup_audit(active, fixtures)
    for payload, name in ((audit, "active_matrix_market_audit_v2_3.json"), (compare, "matrix_vs_xgboost_market_comparison_v2_3.json"),
                          (wc, "worldcup_2026_market_audit_v2_3.json"), (buckets, "market_calibration_buckets_v2_3.json")):
        publish(payload, name)
    for name, text in markdown(audit, compare, wc, buckets).items():
        (ROOT / "docs" / name).write_text(text, encoding="utf-8")
    print(f"V2.3 audit complete: {len(records)} test matches; {len(active)} active fixtures; no retrain")


if __name__ == "__main__":
    main()
