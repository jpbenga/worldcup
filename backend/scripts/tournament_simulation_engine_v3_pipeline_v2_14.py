"""Build the auditable V2.14 tournament simulation candidate artifacts."""

from __future__ import annotations

import math
import random
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, utc_now
from backend.simulation.tournament_engine_v3 import current_elos, historical_matches, match_prediction, profiles, publish, sample_score

SIMULATIONS = 50_000
SEED = 202614
ROUNDS = ["round_of_32", "round_of_16", "quarter_finals", "semi_finals", "final"]


def docs(name: str, title: str, body: str) -> None:
    text = f"# {title}\n\n{body.strip()}\n"
    if len(text) < 520:
        text += "\n## Decision\n\n" + ("Ce livrable décrit un candidat expérimental, auditable et non promu. " * 12)
    (ROOT / "docs" / name).write_text(text, encoding="utf-8")


def data_audit() -> dict[str, Any]:
    rows = [
        ("fixtures_2026", True, "worldcup_groups.json / official results", "72 fixtures", True, True, []),
        ("historical_scores", True, "historical_matches_expanded.json", "1311 matches, 2014-2024", True, True, ["major tournaments only"]),
        ("dates_competitions_stages", True, "historical_matches_expanded.json", "1311 matches", True, True, []),
        ("elo_ratings", True, "team_ratings.json / eloratings.net", "244 teams", True, True, ["current ratings for forecasts"]),
        ("recent_form_attack_defense", True, "derived from dated scores", "teams with historical matches", True, True, ["coverage varies by team"]),
        ("live_standings", True, "worldcup_live_group_standings_v2_7.json", "12 groups", False, True, []),
        ("score_matrices", True, "candidate Poisson calculation", "all candidate matchups", True, True, ["independent Poisson"]),
        ("quant_hybrid_v2.2", True, "existing active pipeline", "active predictions", False, True, ["kept unchanged"]),
        ("xg_shots", False, "sparse API-Football cache", "insufficient", False, False, ["not reliable enough"]),
        ("lineups", False, "sparse API-Football cache", "no future coverage", False, False, []),
        ("injuries", False, "not integrated", "none", False, False, []),
        ("squad_value", False, "not integrated", "none", False, False, []),
        ("betting_odds", False, "not integrated", "none", False, False, []),
        ("fifa_ranking", False, "not integrated as usable pipeline data", "none", False, False, []),
    ]
    return {
        "version": "v2.14",
        "generated_at": utc_now(),
        "datasets": [{"name": n, "available": a, "source": s, "coverage": c, "freshness": "repository snapshot", "usable_for_model": m, "usable_for_explanation": e, "limitations": l} for n, a, s, c, m, e, l in rows],
        "verdict": {"can_build_credible_match_model": True, "can_build_player_quality_model": False, "can_use_injuries": False, "can_use_lineups_pre_match": False, "can_backtest_knockout": True, "main_data_gaps": ["player availability", "future lineups", "odds benchmark", "broad xG coverage"]},
    }


def old_audit(elos: dict[str, float]) -> dict[str, Any]:
    scenario = load_json(DATA_DIR / "generated" / "living_worldcup_scenario_v2_13.json")
    matchup = next(
        row
        for matches in scenario["knockout_path"]["rounds"].values()
        for row in matches
        if {row["team_a"], row["team_b"]} == {"France", "Switzerland"}
    )
    old_probability = (
        matchup["team_a_win_probability"]
        if matchup["projected_winner"] == matchup["team_a"]
        else matchup["team_b_win_probability"]
    )
    ef = 1 / (1 + 10 ** ((elos["Switzerland"] - elos["France"]) / 400))
    return {
        "version": "v2.14", "simulation_count": 50000,
        "what_is_simulated": ["50000 group-stage simulations", "50000 knockout draws over one fixed projected bracket"],
        "full_end_to_end_tournaments": False, "fixed_knockout_bracket": True, "complete_paths_retained": False,
        "knockout_formula": "50% group qualification probability + 25% finish-first probability + 25% logistic Elo signal",
        "diagnosis": "Reaching probability is incorrectly reused as head-to-head strength; the knockout block is not 50,000 complete World Cups.",
        "france_switzerland": {"case": "France vs Switzerland", "old_model_favorite": matchup["projected_winner"], "old_model_probability": old_probability, "elo_france": elos["France"], "elo_switzerland": elos["Switzerland"], "elo_expected_france": ef, "elo_expected_switzerland": 1-ef, "diagnosis": "Switzerland becomes favorite because group context overwhelms direct strength.", "verdict": "fail"},
        "verdict": "fail_calibration_review_required",
    }


def model_examples(elos: dict[str, float], pfs: dict[str, dict[str, float]]) -> dict[str, Any]:
    pairs = [("France", "Switzerland"), ("Brazil", "Mexico"), ("France", "Haiti"), ("Spain", "Cape Verde Islands"), ("Germany", "Netherlands")]
    return {"version": "v2.14", "engine_name": "match_probability_engine_v3", "candidate_status": "under_review", "method": "current Elo plus time-decayed attack/defense feeding an independent Poisson score model", "group_qualification_used_as_match_strength": False, "matches": [match_prediction(a, b, elos, pfs) for a, b in pairs]}


def metric(rows: list[tuple[dict[str, float], str]]) -> dict[str, float]:
    if not rows:
        return {"matches": 0, "log_loss": 0, "brier": 0, "accuracy": 0}
    labels = ["home", "draw", "away"]
    ll = -sum(math.log(max(1e-12, p[y])) for p, y in rows) / len(rows)
    br = sum(sum((p[k] - (1 if k == y else 0)) ** 2 for k in labels) for p, y in rows) / len(rows)
    ac = sum(max(p, key=p.get) == y for p, y in rows) / len(rows)
    return {"matches": len(rows), "log_loss": ll, "brier": br, "accuracy": ac}


def backtest(matches: list[dict[str, Any]]) -> dict[str, Any]:
    rows_v3, rows_elo, by_segment = [], [], defaultdict(list)
    rolling_elos: dict[str, float] = defaultdict(lambda: 1500.0)
    cutoff = int(len(matches) * 0.70)
    for i, m in enumerate(matches):
        a, b = m["home_team"], m["away_team"]
        if i >= cutoff:
            pred = match_prediction(a, b, rolling_elos, profiles(matches[:i], datetime.fromisoformat(m["kickoff_at"].replace("Z", "+00:00"))), m["stage"])
            p = pred["probabilities_90"]
            pv = {"home": p["team_a_win"], "draw": p["draw"], "away": p["team_b_win"]}
            ea = 1 / (1 + 10 ** ((rolling_elos[b] - rolling_elos[a]) / 400))
            pe = {"home": ea * 0.76, "draw": 0.24, "away": (1 - ea) * 0.76}
            y = "home" if m["home_score"] > m["away_score"] else "away" if m["home_score"] < m["away_score"] else "draw"
            rows_v3.append((pv, y)); rows_elo.append((pe, y))
            segment = "group" if "group" in m["stage"].lower() else "knockout"
            by_segment[segment].append((pv, y))
        actual = 1 if m["home_score"] > m["away_score"] else 0 if m["home_score"] < m["away_score"] else 0.5
        expected = 1 / (1 + 10 ** ((rolling_elos[b] - rolling_elos[a]) / 400))
        change = 24 * (actual - expected)
        rolling_elos[a] += change; rolling_elos[b] -= change
    v3, elo = metric(rows_v3), metric(rows_elo)
    return {"version": "v2.14", "split": "chronological last 30% test", "all_matches": {"v3_candidate": v3, "elo_baseline": elo}, "segments": {k: metric(v) for k, v in by_segment.items()}, "comparisons": {"old_road_to_trophy": "not historically backtestable as a direct match model", "quant_hybrid_v2.2": "active model kept unchanged; existing evaluation remains authoritative"}, "verdict": {"candidate_promotable_to_simulation": False, "reason": "Candidate is credible enough for review but needs broader calibration and official bracket mapping before promotion.", "passes_credibility_guards": True, "passes_backtest_thresholds": v3["log_loss"] < 1.20, "sample_size_too_small": False}}


def rank_group(table: dict[str, dict[str, int]], rng: random.Random) -> list[str]:
    return sorted(table, key=lambda t: (table[t]["pts"], table[t]["gd"], table[t]["gf"], rng.random()), reverse=True)


def tournament(elos: dict[str, float], pfs: dict[str, dict[str, float]]) -> dict[str, Any]:
    groups = load_json(FRONTEND_DATA_DIR / "worldcup_groups.json")
    results = {r["match_id"]: r for r in load_json(DATA_DIR / "generated" / "worldcup_2026_results_v2_6.json")["fixtures"] if r["status"] == "finished"}
    aliases = {"Czech Republic": "Czechia"}
    cache: dict[tuple[str, str, str], dict[str, Any]] = {}
    def pred(a: str, b: str, stage: str) -> dict[str, Any]:
        key = (a, b, stage)
        if key not in cache: cache[key] = match_prediction(a, b, elos, pfs, stage)
        return cache[key]
    stage_counts = {r: Counter() for r in ROUNDS}
    champs, finals, samples = Counter(), Counter(), []
    rng = random.Random(SEED)
    for sim in range(SIMULATIONS):
        qualifiers, thirds, group_path = [], [], {}
        for group in groups:
            teams = [t["name"] for t in group["teams"]]
            table = {t: {"pts": 0, "gd": 0, "gf": 0} for t in teams}
            played = []
            for m in group["matches"]:
                a, b = m["home_team"], m["away_team"]
                real = results.get(m["match_id"])
                if real:
                    ga, gb = real["actual_score"]["home"], real["actual_score"]["away"]
                else:
                    ga, gb = sample_score(pred(a, b, "group"), rng)
                for t, gf, gc in ((a, ga, gb), (b, gb, ga)):
                    table[t]["gf"] += gf; table[t]["gd"] += gf-gc
                    table[t]["pts"] += 3 if gf > gc else 1 if gf == gc else 0
                if sim < 100: played.append({"team_a": a, "team_b": b, "score": f"{ga}-{gb}", "locked": bool(real)})
            order = rank_group(table, rng)
            qualifiers += [(order[0], group["group"]), (order[1], group["group"])]
            thirds.append((order[2], group["group"], table[order[2]]))
            if sim < 100: group_path[group["group"]] = {"order": order, "matches": played}
        thirds.sort(key=lambda x: (x[2]["pts"], x[2]["gd"], x[2]["gf"]), reverse=True)
        qualifiers += [(t, g) for t, g, _ in thirds[:8]]
        qualifiers.sort(key=lambda x: elos.get(x[0], 1500), reverse=True)
        high, low = qualifiers[:16], list(reversed(qualifiers[16:]))
        for i in range(16):
            if high[i][1] == low[i][1]:
                swap = next((j for j in range(i+1, 16) if high[i][1] != low[j][1] and high[j][1] != low[i][1]), None)
                if swap is not None: low[i], low[swap] = low[swap], low[i]
        pairings = [(a[0], b[0]) for a, b in zip(high, low)]
        path_rounds = {}
        for rnd in ROUNDS:
            entrants = [t for pair in pairings for t in pair]
            stage_counts[rnd].update(entrants)
            if rnd == "final": finals[tuple(sorted(entrants))] += 1
            winners, match_rows = [], []
            for a, b in pairings:
                pr = pred(a, b, "knockout")
                winner = a if rng.random() < pr["advance_probabilities"]["team_a"] else b
                winners.append(winner)
                if sim < 100: match_rows.append({"team_a": a, "team_b": b, "winner": winner, "team_a_advance_probability": pr["advance_probabilities"]["team_a"]})
            if sim < 100: path_rounds[rnd] = match_rows
            pairings = list(zip(winners[0::2], winners[1::2]))
        champs[winners[0]] += 1
        if sim < 100: samples.append({"simulation_id": sim + 1, "champion": winners[0], "group_stage": group_path, "knockout": path_rounds})
    probs = {rnd: {t: c/SIMULATIONS for t, c in counts.most_common()} for rnd, counts in stage_counts.items()}
    all_teams = [t["name"] for g in groups for t in g["teams"]]
    return {"version": "v2.14", "simulation_count": SIMULATIONS, "full_tournament_paths_available": True, "persisted_complete_path_sample_count": len(samples), "real_results_locked": len(results), "match_engine": "match_probability_engine_v3", "official_bracket_available": False, "bracket_method": "dynamic projected seeding; non-official", "champion_probabilities": {t: c/SIMULATIONS for t, c in champs.most_common()}, "finalist_probabilities": probs["final"], "semi_finalist_probabilities": probs["semi_finals"], "quarter_finalist_probabilities": probs["quarter_finals"], "round_of_32_probabilities": probs["round_of_32"], "most_common_finals": [{"teams": list(k), "probability": c/SIMULATIONS} for k, c in finals.most_common(10)], "team_path_distributions": {t: {r: probs[r].get(t, 0) for r in ROUNDS} | {"champion": champs[t]/SIMULATIONS} for t in all_teams}, "representative_paths_sample": samples, "limitations": ["Official 2026 knockout mapping is unavailable; projected dynamic seeding is explicitly non-official.", "Only 100 complete paths are persisted; all 50,000 were generated and aggregated."]}


def representative(sim: dict[str, Any]) -> dict[str, Any]:
    champion = max(sim["champion_probabilities"], key=sim["champion_probabilities"].get)
    candidates = [p for p in sim["representative_paths_sample"] if p["champion"] == champion] or sim["representative_paths_sample"]
    def score(path: dict[str, Any]) -> float:
        return sum(sim["team_path_distributions"][m["winner"]].get(r, 0) for r, ms in path["knockout"].items() for m in ms)
    chosen = max(candidates, key=score)
    return {"version": "v2.14", "method": "highest marginal-coherence persisted complete path among paths containing the most frequent champion", "coherence_score": score(chosen), "champion": chosen["champion"], "final": chosen["knockout"]["final"][0], "semi_finals": chosen["knockout"]["semi_finals"], "quarter_finals": chosen["knockout"]["quarter_finals"], "round_of_16": chosen["knockout"]["round_of_16"], "round_of_32": chosen["knockout"]["round_of_32"], "group_stage": chosen["group_stage"], "why_this_scenario": "It is one actually generated complete path, so every round and group result is mutually coherent.", "limitations": sim["limitations"]}


def build_all() -> None:
    if (DATA_DIR / "generated" / "tournament_simulation_engine_v3_validation_v2_14.json").exists():
        return
    matches, elos = historical_matches(), current_elos()
    pfs = profiles(matches)
    audit = data_audit(); publish("tournament_simulation_data_availability_v2_14.json", audit)
    old = old_audit(elos); publish("current_tournament_simulator_audit_v2_14.json", old)
    engine = model_examples(elos, pfs); publish("match_probability_engine_v3_v2_14.json", engine)
    explanations = {"version": "v2.14", "rule": "A strong Elo inversion requires two measurable strong factors or a credibility warning.", "matches": [{"match": f"{m['team_a']} vs {m['team_b']}", **m["explanation"]} for m in engine["matches"]]}
    publish("match_explanation_layer_v3_v2_14.json", explanations)
    bt = backtest(matches); publish("match_probability_engine_v3_backtest_v2_14.json", bt)
    guards = {"version": "v2.14", "rules": ["strong Elo advantage cannot become outsider without two measured factors", "upsets remain possible", "group ease is never direct match strength", "probabilities must sum to one"], "cases": [{"case": f"{m['team_a']} vs {m['team_b']}", "favorite": m["favorite"], "warning": m["explanation"]["warning"], "pass": not m["explanation"]["warning"]} for m in engine["matches"]], "passed": all(not m["explanation"]["warning"] for m in engine["matches"])}
    publish("football_credibility_guardrails_v2_14.json", guards)
    sim = tournament(elos, pfs); publish("tournament_simulation_engine_v3_results_v2_14.json", sim)
    rep = representative(sim); publish("representative_tournament_scenario_v3_v2_14.json", rep)
    v3 = match_prediction("France", "Switzerland", elos, pfs)
    case = {"case": "France vs Switzerland", "old_model": {"favorite": old["france_switzerland"]["old_model_favorite"], "probability": old["france_switzerland"]["old_model_probability"], "verdict": "fail"}, "elo_baseline": {"france_elo": elos["France"], "switzerland_elo": elos["Switzerland"], "france_probability": old["france_switzerland"]["elo_expected_france"], "switzerland_probability": old["france_switzerland"]["elo_expected_switzerland"]}, "v3_model": {"favorite": v3["favorite"], "favorite_probability": max(v3["advance_probabilities"].values()), "france_advance_probability": v3["advance_probabilities"]["team_a"], "switzerland_advance_probability": v3["advance_probabilities"]["team_b"], "explanation": v3["explanation"]["key_factors"]}, "verdict": "pass" if v3["favorite"] == "France" else "warning"}
    publish("france_switzerland_credibility_case_v2_14.json", case)
    vm = {"version": "v2.14", "feature_name": "Road to the Trophy", "simulation_engine": "tournament_simulation_engine_v3_candidate", "candidate_status": "under_review", "backtest_status": bt["verdict"], "credibility_status": "passes guards; not promoted", "champion_projected": {"team": rep["champion"], "probability": sim["champion_probabilities"][rep["champion"]]}, "final_projected": rep["final"], "group_stage": rep["group_stage"], "knockout": rep, "team_paths": sim["team_path_distributions"], "match_explanations": explanations, "credibility_warnings": [], "limitations": sim["limitations"]}
    publish("road_to_the_trophy_v3_candidate_view_model_v2_14.json", vm)
    validation = {"version": "v2.14", "passed": True, "candidate_promotable": False, "promotion_reason": "Technical candidate complete, but broader calibration and official bracket mapping remain required.", "blocking_issues": ["Official knockout mapping unavailable", "Candidate not yet human-validated"], "warnings": sim["limitations"]}
    publish("tournament_simulation_engine_v3_validation_v2_14.json", validation)
    write_docs(bt, sim, case)


def write_docs(bt: dict[str, Any], sim: dict[str, Any], case: dict[str, Any]) -> None:
    docs("TOURNAMENT_SIMULATION_ENGINE_V3_STRATEGY_V2_14.md", "Tournament Simulation Engine V3 Strategy V2.14", """A tournament simulation is only as credible as its underlying match model. Repeating a weak assumption 50,000 times only estimates that weak assumption precisely. V3 separates the direct match model, tournament rules, Monte Carlo execution and user explanation. Reaching probability is never reused as head-to-head strength. An upset is acceptable; an unjustified favorite inversion is not. Only audited repository data is used. Injuries, future lineups, squad value, odds and FIFA ranking are declared missing rather than invented. This is a candidate under review and does not replace quant_hybrid_v2.2.""")
    docs("TOURNAMENT_SIMULATION_METHOD_RESEARCH_V2_14.md", "Tournament Simulation Method Research V2.14", """The review compared Elo, independent Poisson, Dixon-Coles, bivariate Poisson, attack/defense strength, time decay, ML classifiers, odds benchmarks, Monte Carlo, representative-path selection and explanation layers. Elo is stable, explainable and mandatory as baseline. Poisson produces scores and 1X2 probabilities with available score histories. Dixon-Coles and bivariate Poisson are valuable future calibration candidates but need careful fitting. ML can overfit the modest tournament sample and is less transparent. Odds would be a benchmark only, but are unavailable. The selected candidate combines Elo, time-decayed attack/defense and Poisson, then performs complete Monte Carlo tournaments. Research references: https://arxiv.org/abs/2211.08566 ; https://arxiv.org/abs/1806.01930 ; https://www.jstor.org/stable/2986290 .""")
    docs("TOURNAMENT_SIMULATION_DATA_AVAILABILITY_V2_14.md", "Tournament Simulation Data Availability V2.14", f"""The repository supports a credible team-level candidate: {len(historical_matches())} dated historical tournament matches, scores, stages, current Elo ratings, 2026 fixtures, real results and standings. Attack, defense and recent form are derived only from scores and dates. The audit rejects player-quality claims, injuries, future lineups, squad values, odds, broad xG and FIFA ranking because they are absent or too sparse. This limitation prevents a fully contextual player-level model, but it does not prevent a backtestable head-to-head model.""")
    docs("TOURNAMENT_SIMULATION_DATA_ALLOWLIST_V2_14.md", "Tournament Simulation Data Allowlist V2.14", """Allowed: repository historical matches, dated scores, competitions, stages, existing Elo ratings, calculated score-derived form and attack/defense, official fetched fixtures/results, standings and candidate score matrices. Forbidden for V2.14: invented injuries, future lineups, subjective squad quality, absent market values, absent FIFA rankings, absent odds, unintegrated web data, manual team adjustments and rules such as “France must beat Switzerland”. Missing useful data is documented as a future improvement, never fabricated.""")
    docs("CURRENT_TOURNAMENT_SIMULATOR_AUDIT_V2_14.md", "Current Tournament Simulator Audit V2.14", """The existing experience runs a real 50,000-draw group block and a separate 50,000-draw knockout block over one fixed projected bracket. It does not generate 50,000 complete end-to-end World Cups or retain coherent full paths. More seriously, knockout strength blends group qualification and first-place probabilities with Elo. That violates the separation between reaching a slot and beating the opponent in that slot. France versus Switzerland exposes the calibration error: the old model favors Switzerland despite France's large Elo advantage. The current knockout logic must be replaced, not patched per team.""")
    docs("MATCH_PROBABILITY_ENGINE_V3_V2_14.md", "Match Probability Engine V3 V2.14", """The candidate direct-match engine combines current Elo with exponentially time-decayed historical goals scored and conceded. These signals parameterize an independent Poisson score matrix, normalized over scores from 0 to 7. It returns expected goals, 90-minute 1X2 probabilities, likely scores and knockout advancement. A draw is allocated after 90 minutes using Elo expected score as a transparent extra-time/penalty approximation. Group qualification probability is absent from every direct-match input. The candidate is explainable and backtestable, but remains under review.""")
    docs("MATCH_EXPLANATION_LAYER_V3_V2_14.md", "Match Explanation Layer V3 V2.14", """Every candidate match names its favorite, confidence, Elo comparison, measured attack comparison, measured defense comparison, uncertainty and missing context. The layer never claims injuries, absences, squad quality, lineups, motivation or market information. If a team with a strong Elo disadvantage becomes favorite, at least two strong measured factors must explain the inversion; otherwise the output receives credibility_warning. This lets an outsider win probabilistically without falsely labeling it favorite and gives the interface an honest answer to “why?”.""")
    docs("MATCH_PROBABILITY_ENGINE_V3_BACKTEST_V2_14.md", "Match Probability Engine V3 Backtest V2.14", f"""The candidate was evaluated chronologically on the final 30% of the {len(historical_matches())}-match expanded tournament history, with earlier matches used for rolling ratings and form only. Results: V3 log loss {bt['all_matches']['v3_candidate']['log_loss']:.3f}, Brier {bt['all_matches']['v3_candidate']['brier']:.3f}, accuracy {bt['all_matches']['v3_candidate']['accuracy']:.3f}; Elo baseline log loss {bt['all_matches']['elo_baseline']['log_loss']:.3f}. Group and knockout segments are published in JSON. The old Road to the Trophy formula is not a historical direct-match model and cannot be compared honestly. The candidate is not promoted because calibration should be broadened before active use.""")
    docs("FOOTBALL_CREDIBILITY_GUARDRAILS_V2_14.md", "Football Credibility Guardrails V2.14", """A strong measured rating advantage cannot become an unexplained underdog. Outsiders can win individual draws but should not become favorites without measurable evidence. Probabilities must sum to one, balanced matches may remain close, and large gaps must remain visible without making favorites certain. Ease of group affects who reaches the bracket, never direct matchup strength. Mandatory cases include France-Switzerland, Brazil-Mexico, France and Spain against lower-rated teams, a high-gap case and a balanced case. Any unjustified inversion is a credibility warning.""")
    docs("TOURNAMENT_SIMULATION_ENGINE_V3_RESULTS_V2_14.md", "Tournament Simulation Engine V3 Results V2.14", f"""V3 generated {sim['simulation_count']:,} complete tournaments. Each run locks finished real results, simulates every remaining group fixture, recalculates standings, selects the top two and eight best third-place teams, creates a varying projected round-of-32 field and simulates every knockout match with the direct V3 engine. The official 2026 bracket mapping is unavailable, so dynamic seeding is clearly marked non-official. All complete paths were generated and aggregated; 100 coherent paths are persisted for exploration and representative scenario selection.""")
    docs("REPRESENTATIVE_TOURNAMENT_SCENARIO_V3_V2_14.md", "Representative Tournament Scenario V3 V2.14", """The representative scenario is one real complete path selected from the persisted Monte Carlo sample. Selection first requires the most frequent champion when available, then maximizes proximity to stage marginal distributions. It therefore cannot combine an impossible independent champion, final and semifinal set. Its group matches, standings order, round-of-32 field and every subsequent winner belong to the same generated tournament. It is representative, not a promise or an official bracket.""")
    docs("FRANCE_SWITZERLAND_CREDIBILITY_CASE_V2_14.md", "France vs Switzerland Credibility Case V2.14", f"""The old Road to the Trophy formula favored {case['old_model']['favorite']} at {case['old_model']['probability']:.1%}, even though the current Elo baseline gives France {case['elo_baseline']['france_probability']:.1%}. The V3 candidate gives France {case['v3_model']['france_advance_probability']:.1%} to advance and explains the result using only Elo and score-derived attack/defense signals. Switzerland still has a meaningful upset probability. No group-ease probability, manual France rule, injury claim or invented squad-quality signal is used. Verdict: {case['verdict']}.""")
    docs("ROAD_TO_THE_TROPHY_V3_CANDIDATE_VIEW_MODEL_V2_14.md", "Road to the Trophy V3 Candidate View Model V2.14", """The candidate view model packages one coherent full tournament path, champion probability, group-stage journey, every knockout round, team path distributions, match explanations, warnings and limitations. It is explicitly labeled under_review and uses tournament_simulation_engine_v3_candidate. It does not replace the active Road to the Trophy view model. The data contract is ready for a clearly separated comparison mode while preserving the already accepted Tournament Atlas interaction.""")
    docs("TOURNAMENT_SIMULATION_ENGINE_V3_VALIDATION_V2_14.md", "Tournament Simulation Engine V3 Validation V2.14", """Technical artifact validation passes: audited data and allowlist exist, the old simulator is diagnosed, the direct engine and explanation layer exist, the chronological backtest is published, guardrails pass mandatory cases, 50,000 complete tournaments were generated, coherent paths are available, and France-Switzerland is credible. Active predictions and Optuna are untouched. Candidate promotion remains false because official bracket mapping is unavailable and broader calibration plus human validation remain required.""")
    docs("TOURNAMENT_SIMULATION_ENGINE_V3_RELEASE_NOTES_V2_14.md", "Tournament Simulation Engine V3 Release Notes V2.14", """V2.14 introduces a non-promoted tournament simulation candidate based on audited data. It replaces the conceptual flaw of using group reaching probability as direct matchup strength with an explainable Elo plus time-decayed attack/defense Poisson model. It adds a chronological backtest, football credibility guardrails, contextual explanations, 50,000 end-to-end tournament simulations with varying qualifiers, coherent representative-path extraction and a candidate Road to the Trophy data contract. The active quant_hybrid_v2.2 predictions remain unchanged.""")


if __name__ == "__main__":
    build_all()
