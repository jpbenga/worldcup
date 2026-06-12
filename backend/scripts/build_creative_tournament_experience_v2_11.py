"""Build the V2.11 creative tournament experience from existing projections."""

from __future__ import annotations

import math
import shutil
import sys
from pathlib import Path
from statistics import pstdev
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, utc_now, write_json

VERSION = "v2.11"
ENGINE = "quant_hybrid_v2.2"
CANDIDATE = "score_matrix_candidate_v2.8"
OUTPUT = "creative_tournament_experience_v2_11.json"


def publish(payload: dict[str, Any]) -> None:
    generated = DATA_DIR / "generated" / OUTPUT
    write_json(payload, generated)
    shutil.copy2(generated, DATA_DIR / "snapshots" / OUTPUT)
    shutil.copy2(generated, FRONTEND_DATA_DIR / OUTPUT)


def percent_points(value: float) -> str:
    return f"{value * 100:+.1f}"


def projection_rows(simulation: dict[str, Any], group: str) -> list[dict[str, Any]]:
    return sorted(
        (
            {
                "team": team,
                "qualification_probability": simulation["teams"][team]["qualification_probability"],
                "group_winner_probability": simulation["teams"][team]["finish_first_probability"],
            }
            for team in simulation["groups"][group]
        ),
        key=lambda row: row["qualification_probability"],
        reverse=True,
    )


def contender_status(delta: float, in_active_top: bool, in_candidate_top: bool) -> str:
    if delta >= 0.025:
        return "rising"
    if delta <= -0.025:
        return "falling"
    if in_active_top != in_candidate_top:
        return "volatile"
    return "stable"


def group_story_type(chaos: float, locked: list[dict[str, Any]], candidate_delta: float, leader_probability: float) -> str:
    if locked and chaos >= 45:
        return "upset_watch"
    if candidate_delta >= 0.04:
        return "volatile"
    if leader_probability >= 0.88 and chaos < 45:
        return "favorite_control"
    if chaos >= 58:
        return "open_group"
    return "low_change"


def main() -> None:
    manifest = load_json(DATA_DIR / "generated" / "matchday_refresh_manifest_v2_10.json")
    active_sim = load_json(DATA_DIR / "generated" / "worldcup_tournament_simulation_conditioned_v2_6.json")
    candidate_sim = load_json(DATA_DIR / "generated" / "worldcup_tournament_simulation_candidate_v2_9.json")
    comparison = load_json(DATA_DIR / "generated" / "active_vs_candidate_simulation_comparison_v2_9.json")
    active_campaign = load_json(DATA_DIR / "generated" / "worldcup_projected_campaign_v2_6.json")
    candidate_campaign = load_json(DATA_DIR / "generated" / "worldcup_projected_campaign_candidate_v2_9.json")
    live = load_json(DATA_DIR / "generated" / "worldcup_live_group_standings_v2_7.json")
    match_state = load_json(DATA_DIR / "generated" / "worldcup_match_state_view_model_v2_7.json")
    results = load_json(DATA_DIR / "generated" / "worldcup_2026_results_v2_6.json")
    dual = load_json(DATA_DIR / "generated" / "dual_matrix_comparison_v2_9.json")
    knockout = load_json(DATA_DIR / "generated" / "worldcup_knockout_structure_v2_6.json")

    active_contenders = {row["team"]: row for row in active_campaign["top_contenders"]}
    candidate_contenders = {row["team"]: row for row in candidate_campaign["top_contenders"]}
    active_rank = {row["team"]: rank for rank, row in enumerate(active_campaign["top_contenders"], 1)}
    candidate_rank = {row["team"]: rank for rank, row in enumerate(candidate_campaign["top_contenders"], 1)}
    deltas = {row["team"]: row for row in comparison["team_deltas"]}

    contender_names: list[str] = []
    for source in (
        active_campaign["top_contenders"],
        candidate_campaign["top_contenders"],
        comparison["teams_rising_most"],
        comparison["teams_falling_most"],
    ):
        for row in source:
            if row["team"] not in contender_names:
                contender_names.append(row["team"])

    top_contenders = []
    for team in contender_names:
        active_team = active_sim["teams"][team]
        candidate_team = candidate_sim["teams"][team]
        delta = candidate_team["qualification_probability"] - active_team["qualification_probability"]
        status = contender_status(delta, team in active_rank, team in candidate_rank)
        reason = {
            "rising": "Le scénario alternatif renforce nettement ses chances de qualification.",
            "falling": "Le scénario alternatif réduit nettement ses chances de qualification.",
            "volatile": "Sa place parmi les leaders change selon la projection choisie.",
            "stable": "Son statut reste cohérent entre prédiction active et scénario alternatif.",
        }[status]
        top_contenders.append(
            {
                "rank": active_rank.get(team) or candidate_rank.get(team) or len(contender_names),
                "team": team,
                "group": active_team["group"],
                "active_score": active_contenders.get(team, {}).get("contender_proxy_score"),
                "candidate_score": candidate_contenders.get(team, {}).get("contender_proxy_score"),
                "qualification_probability": active_team["qualification_probability"],
                "candidate_qualification_probability": candidate_team["qualification_probability"],
                "group_winner_probability": active_team["finish_first_probability"],
                "active_vs_candidate_delta": delta,
                "status": status,
                "reason": reason,
            }
        )
    top_contenders.sort(key=lambda row: (row["rank"], -row["qualification_probability"]))

    states = {row["match_id"]: row for row in match_state["matches"]}
    aliases = {"Czechia": "Czech Republic"}
    locked_result_impact = []
    locked_by_group: dict[str, list[dict[str, Any]]] = {}
    for fixture in results["fixtures"]:
        if fixture["status"] != "finished":
            continue
        state = states.get(fixture["match_id"], {})
        group = state.get("group", "")
        home = aliases.get(fixture["home_team"], fixture["home_team"])
        away = aliases.get(fixture["away_team"], fixture["away_team"])
        home_delta = active_sim["changes_vs_v2_4"].get(home, 0.0)
        away_delta = active_sim["changes_vs_v2_4"].get(away, 0.0)
        home_goals = fixture["actual_score"]["home"]
        away_goals = fixture["actual_score"]["away"]
        winner = home if home_goals > away_goals else away if away_goals > home_goals else "Draw"
        impact = {
            "match": f"{fixture['home_team']} {home_goals}-{away_goals} {fixture['away_team']}",
            "group": group,
            "winner": winner,
            "qualification_delta": {
                fixture["home_team"]: percent_points(home_delta),
                fixture["away_team"]: percent_points(away_delta),
            },
            "summary": (
                f"Résultat officiel verrouillé : {fixture['home_team']} évolue de {percent_points(home_delta)} points "
                f"et {fixture['away_team']} de {percent_points(away_delta)} points face à la projection pré-tournoi."
            ),
        }
        locked_result_impact.append(impact)
        locked_by_group.setdefault(group, []).append(impact)

    affected_groups = {row["group"]: row for row in comparison["groups_most_affected"]}
    group_storylines = []
    for group in sorted(active_sim["groups"]):
        letter = group.replace("Group ", "")
        active_rows = projection_rows(active_sim, group)
        candidate_rows = projection_rows(candidate_sim, group)
        probabilities = [row["qualification_probability"] for row in active_rows]
        spread = max(probabilities) - min(probabilities)
        closeness = max(0.0, 1 - spread)
        density = max(0.0, 1 - pstdev(probabilities) * 3)
        candidate_delta = affected_groups[group]["average_absolute_qualification_delta"]
        locked = locked_by_group.get(letter, [])
        chaos = min(100.0, 100 * (0.45 * closeness + 0.30 * density + 0.20 * min(1, candidate_delta / 0.07) + 0.05 * bool(locked)))
        story_type = group_story_type(chaos, locked, candidate_delta, active_rows[0]["qualification_probability"])
        label = {
            "favorite_control": "Favori solide",
            "open_group": "Groupe ouvert",
            "upset_watch": "Impact résultat réel",
            "volatile": "Projection alternative change le groupe",
            "low_change": "Groupe instable" if chaos >= 48 else "Projection stable",
        }[story_type]
        open_rank = min(active_rows, key=lambda row: abs(row["qualification_probability"] - 0.5))
        group_storylines.append(
            {
                "group": letter,
                "title": f"Groupe {letter} · {label}",
                "summary": (
                    f"{active_rows[0]['team']} mène la projection active. "
                    f"{'Un résultat réel change déjà le contexte. ' if locked else ''}"
                    f"L’écart moyen avec le scénario alternatif est de {candidate_delta:.1%}."
                ),
                "current_standings": live["groups"][letter]["standings"],
                "active_projection": active_rows,
                "candidate_projection": candidate_rows,
                "most_likely_winner": active_rows[0]["team"],
                "qualification_favorites": [row["team"] for row in active_rows[:2]],
                "most_open_rank": f"{open_rank['team']} · qualification {open_rank['qualification_probability']:.1%}",
                "chaos_score": round(chaos, 1),
                "active_candidate_difference": f"Écart moyen de qualification : {candidate_delta:.1%}",
                "locked_results": locked,
                "story_type": story_type,
                "label": label,
            }
        )
    group_storylines.sort(key=lambda row: row["chaos_score"], reverse=True)

    leader_name = active_campaign["champion_proxy"]
    leader_active = active_sim["teams"][leader_name]
    leader_candidate = candidate_sim["teams"][leader_name]
    same_leader = leader_name == candidate_campaign["champion_proxy"]
    confidence = "stable" if same_leader and abs(leader_candidate["qualification_probability"] - leader_active["qualification_probability"]) < 0.04 else "contested"
    if active_campaign["top_contenders"][0]["contender_proxy_score"] - active_campaign["top_contenders"][1]["contender_proxy_score"] < 0.01:
        confidence = "open"

    bracket_available = bool(knockout["knockout_structure_available"])
    payload = {
        "version": VERSION,
        "engine_version": ENGINE,
        "candidate_version": CANDIDATE,
        "candidate_status": "alternative_non_active",
        "generated_at": utc_now(),
        "refresh": {
            "source_manifest": "matchday_refresh_manifest_v2_10",
            "simulation_count": manifest["simulation_count"],
            "finished_matches": manifest["result_summary"]["finished_matches"],
            "live_matches": manifest["result_summary"]["live_matches"],
            "not_started_matches": manifest["result_summary"]["not_started_matches"],
        },
        "tournament_leader": {
            "team": leader_name,
            "label": "Projected tournament leader",
            "active_proxy_rank": active_rank[leader_name],
            "candidate_proxy_rank": candidate_rank.get(leader_name),
            "active_qualification_probability": leader_active["qualification_probability"],
            "candidate_qualification_probability": leader_candidate["qualification_probability"],
            "active_group_winner_probability": leader_active["finish_first_probability"],
            "candidate_group_winner_probability": leader_candidate["finish_first_probability"],
            "confidence_label": confidence,
            "is_official_champion_simulation": False,
            "explanation": "Favori projeté et leader de campagne. Il s’agit d’un proxy non officiel tant que le bracket officiel est indisponible.",
        },
        "top_contenders": top_contenders,
        "projected_campaign": {
            "path_type": "projected_campaign_proxy",
            "bracket_available": bracket_available,
            "is_official_champion_simulation": False,
            "leader": leader_name,
            "group_exit_probability": leader_active["qualification_probability"],
            "group_winner_probability": leader_active["finish_first_probability"],
            "contender_status": confidence,
            "estimated_adversity": "Bracket officiel indisponible : adversaires à élimination directe non estimés.",
            "steps": active_campaign["top_contenders"][0]["campaign_steps"],
            "proxy_limit": "La projection s’arrête au potentiel de campagne et n’invente aucun parcours officiel.",
        },
        "active_vs_alternative": {
            "summary": "La projection alternative non active explore un scénario moins conservateur sans remplacer la prédiction active.",
            "active_leader": active_campaign["champion_proxy"],
            "alternative_leader": candidate_campaign["champion_proxy"],
            "modal_scores_changed": dual["modal_changed_count"],
            "favorite_margins_increased": dual["label_distribution"].get("favorite_margin_increased", 0),
            "most_affected_groups": [row["group"].replace("Group ", "") for row in comparison["groups_most_affected"][:5]],
            "teams_rising": [row["team"] for row in comparison["teams_rising_most"][:5]],
            "teams_falling": [row["team"] for row in comparison["teams_falling_most"][:5]],
            "leader_changed": comparison["candidate_impact_on_projected_campaign_proxy"]["leader_changed"],
            "interpretation": "La projection alternative ne remplace pas la prédiction active. Elle montre un scénario moins conservateur.",
        },
        "group_storylines": group_storylines,
        "rising_teams": comparison["teams_rising_most"],
        "falling_teams": comparison["teams_falling_most"],
        "open_groups": [
            {"group": row["group"], "title": row["title"], "chaos_score": row["chaos_score"], "label": row["label"]}
            for row in group_storylines[:5]
        ],
        "locked_result_impact": locked_result_impact,
        "limitations": [
            "The projected champion is a campaign proxy while the official knockout bracket is unavailable. It must not be labelled as a fully simulated World Cup champion.",
            "Bracket officiel indisponible : aucun adversaire, pairing ou parcours à élimination directe n’est inventé.",
            "La projection alternative est non active et ne remplace aucune prédiction active.",
            "Les deltas entre simulations incluent une part de variation Monte Carlo.",
        ],
    }
    publish(payload)

    (ROOT / "docs" / "CREATIVE_TOURNAMENT_EXPERIENCE_DATA_V2_11.md").write_text(
        f"""# Creative Tournament Experience Data V2.11

The V2.11 aggregate turns the existing V2.10 refresh outputs into a product-facing tournament narrative. It does not train a model, rerun Optuna, change active probabilities or promote the alternative projection.

## Current snapshot

- Projected tournament leader: `{leader_name}`
- Leader confidence label: `{confidence}`
- Simulations: `{manifest['simulation_count']:,}`
- Official results locked: `{len(locked_result_impact)}`
- Group storylines: `{len(group_storylines)}`
- Most open groups: `{", ".join(row['group'] for row in group_storylines[:5])}`
- Active leader: `{active_campaign['champion_proxy']}`
- Alternative non-active leader: `{candidate_campaign['champion_proxy']}`

## Product contract

The aggregate combines active and alternative projected campaigns, conditioned qualification probabilities, current standings, result-aware deltas, group volatility and dual-matrix evidence. `chaos_score` is a narrative ranking based on probability closeness, within-group density, active-versus-alternative movement and locked-result context.

The projected champion is a campaign proxy while the official knockout bracket is unavailable. It must not be labelled as a fully simulated World Cup champion. The alternative remains a comparative, less conservative scenario and never replaces the active forecast.
""",
        encoding="utf-8",
    )
    print(f"V2.11 creative tournament experience built: {leader_name}, {len(group_storylines)} groups")


if __name__ == "__main__":
    main()
