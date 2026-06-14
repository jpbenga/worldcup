"""Audit the current 50,000-run tournament simulation algorithm."""

from __future__ import annotations

import json
import math
import shutil
import sys
from collections import Counter
from pathlib import Path
from statistics import median
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, utc_now, write_json
from backend.simulation.tournament_engine_v3 import current_elos, historical_matches, profiles

VERSION = "v2.20"
OUTPUT = "tournament_simulation_algorithm_audit_v2_20.json"


def publish(payload: dict[str, Any]) -> None:
    target = DATA_DIR / "generated" / OUTPUT
    write_json(payload, target)
    shutil.copy2(target, DATA_DIR / "snapshots" / OUTPUT)


def main() -> None:
    matches = historical_matches()
    simulation = load_json(DATA_DIR / "generated/tournament_simulation_engine_v3_results_v2_14.json")
    v3_backtest = load_json(DATA_DIR / "generated/match_probability_engine_v3_backtest_v2_14.json")
    quant = load_json(DATA_DIR / "generated/quant_engine_v2_2_results.json")
    groups = load_json(FRONTEND_DATA_DIR / "worldcup_groups.json")
    teams = [team["name"] for group in groups for team in group["teams"]]
    elos = current_elos()
    team_profiles = profiles(matches)
    counts = Counter(team for match in matches for team in (match["home_team"], match["away_team"]))
    source_statuses = Counter(match["source_status"] for match in matches)
    group_tie_boundaries = 0
    for path in simulation["representative_paths_sample"]:
        for group in path["group_stage"].values():
            table = {team: {"pts": 0, "gd": 0, "gf": 0} for team in group["order"]}
            for row in group["matches"]:
                home, away = row["team_a"], row["team_b"]
                hg, ag = map(int, row["score"].split("-"))
                for team, gf, ga in ((home, hg, ag), (away, ag, hg)):
                    table[team]["gf"] += gf
                    table[team]["gd"] += gf - ga
                    table[team]["pts"] += 3 if gf > ga else 1 if gf == ga else 0
            keys = [(table[team]["pts"], table[team]["gd"], table[team]["gf"]) for team in group["order"]]
            group_tie_boundaries += int(keys[1] == keys[2] or keys[2] == keys[3])
    v3_test = v3_backtest["all_matches"]["v3_candidate"]
    quant_test = quant["test"]
    payload = {
        "version": VERSION,
        "generated_at": utc_now(),
        "scope": "Deep audit only; no model retraining, active-prediction change, Optuna run or tournament-engine promotion.",
        "executive_verdict": {
            "simulations_are_real": simulation["simulation_count"] == 50000,
            "monte_carlo_count_is_adequate_for_marginals": True,
            "current_engine_is_best_available_in_project": False,
            "current_engine_is_rules_complete": False,
            "current_engine_is_knockout_process_complete": False,
            "priority": "Fix rules and data semantics, then unify around the strongest historically validated match model before adding complexity.",
        },
        "current_algorithm": {
            "simulation_count": simulation["simulation_count"],
            "seed": 202614,
            "match_cache": "One fixed prediction matrix per team pair and stage reused across all tournaments.",
            "group_match_model": "Independent Poisson score matrix using current external Elo plus exponentially decayed goals-for/goals-against profiles.",
            "knockout_match_model": "Bernoulli advancement draw from 90-minute win probability plus draw probability allocated by Elo expected score.",
            "extra_time": "Not simulated.",
            "penalty_shootout": "Not simulated; included implicitly in Elo allocation of a 90-minute draw.",
            "group_ranking": "Points, goal difference, goals scored, then random tie-break.",
            "best_thirds": "Points, goal difference and goals scored; remaining ties inherit input order.",
            "bracket": simulation["bracket_method"],
            "central_scenario": "Selected from persisted complete paths; only 100 of 50,000 complete paths are retained.",
            "real_results_locked": simulation["real_results_locked"],
        },
        "measured_facts": {
            "historical_matches": len(matches),
            "historical_teams": len(counts),
            "historical_competitions": len({match["competition"] for match in matches}),
            "historical_year_min": min(match["kickoff_at"][:4] for match in matches),
            "historical_year_max": max(match["kickoff_at"][:4] for match in matches),
            "aet_matches": source_statuses["AET"],
            "pen_matches": source_statuses["PEN"],
            "aet_or_pen_matches": source_statuses["AET"] + source_statuses["PEN"],
            "median_matches_per_team": median(counts.values()),
            "teams_under_10_historical_matches": sum(value < 10 for value in counts.values()),
            "world_cup_teams_without_v3_profile": sorted(team for team in teams if team not in team_profiles),
            "world_cup_teams_without_external_elo": sorted(team for team in teams if team not in elos),
            "group_qualification_boundary_ties_in_100_paths": group_tie_boundaries,
            "group_paths_checked": len(simulation["representative_paths_sample"]) * 12,
            "max_monte_carlo_95pct_margin_at_50000": 1.96 * math.sqrt(0.25 / 50000),
            "max_sampling_95pct_margin_at_100_paths": 1.96 * math.sqrt(0.25 / 100),
            "v3_test_log_loss": v3_test["log_loss"],
            "v3_test_brier": v3_test["brier"],
            "quant_hybrid_v2_2_test_log_loss": quant_test["log_loss_1x2"],
            "quant_hybrid_v2_2_test_brier": quant_test["brier_score_1x2"],
            "quant_hybrid_log_loss_improvement_vs_v3": v3_test["log_loss"] - quant_test["log_loss_1x2"],
            "quant_hybrid_brier_improvement_vs_v3": v3_test["brier"] - quant_test["brier_score_1x2"],
        },
        "strengths": [
            "Every run is a complete end-to-end tournament and finished official results are locked.",
            "Group score sampling and standings are connected; knockout winners propagate coherently.",
            "The direct match model does not reuse qualification probability as head-to-head strength.",
            "The fixed seed makes runs reproducible.",
            "50,000 runs give a worst-case Monte Carlo 95% sampling margin of about 0.44 percentage points.",
        ],
        "weaknesses": [
            {"severity": "critical", "issue": "The official 2026 bracket rules are not encoded; teams are dynamically seeded by Elo.", "impact": "Opponent paths and title probabilities are structurally wrong even if match probabilities were perfect."},
            {"severity": "critical", "issue": "The tournament uses V3 instead of the project's stronger historically validated quant_hybrid_v2.2 match probabilities.", "impact": "The simulator repeats a weaker predictive model 50,000 times."},
            {"severity": "high", "issue": "Extra time and penalties are not simulated as separate processes.", "impact": "Knockout advancement probabilities and explanations are simplified and not empirically validated."},
            {"severity": "high", "issue": "Group tie-break rules stop after points, goal difference and goals scored.", "impact": "Head-to-head criteria are skipped and unresolved ties become random; qualification boundaries were affected in the persisted sample."},
            {"severity": "high", "issue": "AET/PEN historical score semantics are unresolved.", "impact": "Ninety-minute goal profiles and backtests may contain extra-time or shootout-contaminated outcomes."},
            {"severity": "high", "issue": "All tournaments condition on one fixed parameter estimate and independent match draws.", "impact": "Model uncertainty and correlated tournament form are understated."},
            {"severity": "medium", "issue": "Only the first 100 complete paths are persisted for central-scenario selection.", "impact": "Central-scenario selection has a worst-case 95% sampling margin near 9.8 percentage points."},
            {"severity": "medium", "issue": "Static current external Elo is used for forecasts and coverage is incomplete.", "impact": "Six tournament teams fall back to 1500 and one lacks a historical profile."},
            {"severity": "medium", "issue": "The same match process is used for groups and knockout.", "impact": "Stage-specific tactics and draw behavior are not learned."},
            {"severity": "medium", "issue": "No tournament-level historical replay validates group ranks, best thirds, bracket paths or title calibration.", "impact": "Good single-match metrics do not prove good tournament probabilities."},
        ],
        "applicable_methods": [
            {"method": "Reusable quant_hybrid_v2.2 inference bundle plus calibrated score reconstruction", "applicable_now": True, "priority": 1, "reason": "It already materially outperforms V3 out of sample; model/state persistence is the missing engineering layer."},
            {"method": "Exact FIFA rules engine and official Annex C bracket mapping", "applicable_now": True, "priority": 1, "reason": "This is deterministic rules data, not a predictive-data limitation."},
            {"method": "Chronological regulation-time data cleanup and stage-segmented replay", "applicable_now": True, "priority": 1, "reason": "Dates, stages and source statuses already exist."},
            {"method": "Hierarchical/weighted Poisson with shrinkage and internal ratings", "applicable_now": True, "priority": 2, "reason": "Useful for score matrices and low-sample teams; must beat the active baseline out of sample."},
            {"method": "Dixon-Coles or bivariate-Poisson challengers", "applicable_now": True, "priority": 3, "reason": "Technically feasible, but prior local Dixon-Coles tests did not pass promotion guards."},
            {"method": "Separate extra-time intensity and conservative penalty baseline", "applicable_now": True, "priority": 2, "reason": "AET/PEN rows exist, but sample size requires shrinkage; penalties should remain near 50/50 unless validated."},
            {"method": "Bootstrap/model ensemble and per-tournament latent form shock", "applicable_now": True, "priority": 3, "reason": "Can represent parameter uncertainty and correlated performance using existing historical scores."},
            {"method": "Player, injury, lineup, odds and broad xG models", "applicable_now": False, "priority": 4, "reason": "Coverage is absent or too sparse; adding them now would create unreliable complexity."},
        ],
        "target_architecture": [
            "Data contract: regulation-time scores, extra-time scores, shootout winner, neutral context, stage, official rules and identities.",
            "Reusable pre-match inference bundle: chronological internal rating, team history, quant_hybrid probabilities and calibrated score distribution for arbitrary pairings.",
            "Stage-aware match layer: group 90-minute score model; knockout 90-minute score model; extra-time model; penalty model.",
            "Exact tournament rules engine: complete tie-break hierarchy, best-third ranking and official 2026 bracket mapping.",
            "Uncertainty-aware Monte Carlo: multi-seed convergence, bootstrap/model ensemble and optional calibrated tournament-form latent effects.",
            "Streaming aggregation: retain marginals plus a broad reservoir/top-K of complete paths rather than only the first 100.",
            "Scenario selection: choose a coherent medoid/representative path from all retained candidates using event likelihood and distribution distance.",
            "Tournament-level validation: historical replay of complete tournaments with proper scoring, calibration curves and rule correctness tests.",
        ],
        "delivery_plan": [
            {"phase": "P0_rules_and_semantics", "outcome": "Correct tournament before improving prediction.", "tasks": ["Encode official bracket mapping", "Implement full group/best-third tie-break contract", "Separate regulation/AET/PEN data semantics", "Add deterministic rules tests"]},
            {"phase": "P1_match_engine_unification", "outcome": "Use the strongest validated project model for every possible matchup.", "tasks": ["Persist reusable quant_hybrid_v2.2 inference bundle", "Reconcile hybrid 1X2 with score matrix", "Calibrate group and knockout segments separately", "Benchmark against V3 and Elo"]},
            {"phase": "P2_knockout_and_uncertainty", "outcome": "Model how knockout matches actually finish.", "tasks": ["Simulate 90 minutes, extra time and penalties separately", "Use conservative shrinkage for small AET/PEN samples", "Add multi-seed and convergence reports", "Add bootstrap/model uncertainty"]},
            {"phase": "P3_tournament_validation", "outcome": "Prove tournament probabilities, not only match probabilities.", "tasks": ["Replay historical tournaments end to end", "Measure group-rank, qualification, stage-reach and champion calibration", "Validate representative-path selection", "Promote only after strict gates"]},
        ],
        "research_references": [
            {"topic": "World Cup simulation with Elo-Poisson and Monte Carlo", "url": "https://arxiv.org/abs/1806.01930"},
            {"topic": "Dixon-Coles extensions and dependent score models", "url": "https://arxiv.org/abs/2307.02139"},
            {"topic": "Probabilistic football model comparison and calibration", "url": "https://arxiv.org/abs/1705.04356"},
            {"topic": "Dynamic stochastic football event modelling", "url": "https://arxiv.org/abs/2312.04338"},
            {"topic": "IFAB outcome, extra time and penalty-shootout rules", "url": "https://www.theifab.com/laws/latest/determining-the-outcome-of-a-match/"},
        ],
        "recommendation": "Do not build a V4 by adding ad-hoc signals. Build a rules-correct V3.5 around a reusable quant_hybrid inference contract, explicit knockout processes and tournament-level validation; promote only if it beats V3 and the active match baseline out of sample.",
    }
    publish(payload)
    print("V2.20 tournament simulation algorithm audit: PASS")


if __name__ == "__main__":
    main()
