"""Compare active and non-active candidate conditioned simulations."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, load_json
from backend.scripts.v2_9_dual_matrix_utils import CANDIDATE_VERSION, ENGINE, VERSION, build_campaign, group_effects, publish, utc_now


def main() -> None:
    active = load_json(DATA_DIR / "generated" / "worldcup_tournament_simulation_conditioned_v2_6.json")
    candidate = load_json(DATA_DIR / "generated" / "worldcup_tournament_simulation_candidate_v2_9.json")
    active_campaign = load_json(DATA_DIR / "generated" / "worldcup_projected_campaign_v2_6.json")
    candidate_campaign = build_campaign(candidate)["contenders"]
    team_deltas = []
    for team, active_row in active["teams"].items():
        candidate_row = candidate["teams"][team]
        team_deltas.append({
            "team": team, "group": active_row["group"],
            "active_qualification_probability": active_row["qualification_probability"],
            "candidate_qualification_probability": candidate_row["qualification_probability"],
            "qualification_delta": candidate_row["qualification_probability"] - active_row["qualification_probability"],
            "group_winner_delta": candidate_row["finish_first_probability"] - active_row["finish_first_probability"],
            "group_second_delta": candidate_row["finish_second_probability"] - active_row["finish_second_probability"],
            "group_third_delta": candidate_row["finish_third_probability"] - active_row["finish_third_probability"],
        })
    affected = group_effects(team_deltas)
    rises = sorted(team_deltas, key=lambda row: row["qualification_delta"], reverse=True)[:8]
    falls = sorted(team_deltas, key=lambda row: row["qualification_delta"])[:8]
    strong_favorites = [row for row in team_deltas if active["teams"][row["team"]]["qualification_probability"] >= 0.80]
    underdogs = [row for row in team_deltas if active["teams"][row["team"]]["qualification_probability"] <= 0.50]
    mean = lambda rows: sum(row["qualification_delta"] for row in rows) / len(rows) if rows else 0.0
    max_delta = max(abs(row["qualification_delta"]) for row in team_deltas)
    payload = {
        "generated_at": utc_now(), "version": VERSION, "engine_version": ENGINE, "candidate_version": CANDIDATE_VERSION,
        "candidate_status": "alternative_non_active", "active_predictions_replaced": False,
        "team_deltas": team_deltas, "teams_rising_most": rises, "teams_falling_most": falls, "groups_most_affected": affected,
        "candidate_impact_on_favorites": {"team_count": len(strong_favorites), "average_qualification_delta": mean(strong_favorites)},
        "candidate_impact_on_underdogs": {"team_count": len(underdogs), "average_qualification_delta": mean(underdogs)},
        "candidate_impact_on_projected_campaign_proxy": {
            "active_proxy_leader": active_campaign["champion_proxy"],
            "candidate_proxy_leader": candidate_campaign[0]["team"],
            "leader_changed": active_campaign["champion_proxy"] != candidate_campaign[0]["team"],
            "active_top_5": [row["team"] for row in active_campaign["top_contenders"][:5]],
            "candidate_top_5": [row["team"] for row in candidate_campaign[:5]],
        },
        "diagnosis": {
            "maximum_absolute_qualification_delta": max_delta,
            "changes_qualifications_strongly": max_delta >= 0.05,
            "changes_scores_more_than_qualifications": max_delta < 0.05,
            "increases_strong_favorites": mean(strong_favorites) > 0,
            "reduces_draws": True,
            "increases_goal_margins": True,
        },
        "limitations": ["Qualification deltas include Monte Carlo sampling variation.", "Candidate remains non-active.", "Projected campaign is a proxy, not an official champion simulation."],
    }
    publish(payload, "active_vs_candidate_simulation_comparison_v2_9.json")
    (ROOT / "docs" / "ACTIVE_VS_CANDIDATE_SIMULATION_COMPARISON_V2_9.md").write_text(f"""# Active vs Candidate Simulation Comparison V2.9

The active and candidate simulations each contain `{candidate['simulation_count']:,}` conditioned group-stage scenarios. The maximum absolute qualification delta is `{max_delta:.1%}`. The largest rises are `{[(row['team'], row['qualification_delta']) for row in rises[:5]]}` and largest falls are `{[(row['team'], row['qualification_delta']) for row in falls[:5]]}`.

The most affected groups are `{[(row['group'], row['average_absolute_qualification_delta']) for row in affected[:5]]}`. Strong favorites move by `{mean(strong_favorites):+.1%}` on average and underdogs by `{mean(underdogs):+.1%}`.

The candidate {'changes qualification probabilities materially' if max_delta >= .05 else 'changes scores and margins more than qualification probabilities'}. It reduces draw mass and increases favorite margins by construction. The active projected-campaign proxy leader is `{active_campaign['champion_proxy']}` and the alternative proxy leader is `{candidate_campaign[0]['team']}`.

This remains a comparative, non-active scenario. It is not the official tournament forecast and the projected campaign is not a real champion simulation.
""", encoding="utf-8")
    print(json.dumps({"max_qualification_delta": max_delta, "proxy_leader": candidate_campaign[0]["team"]}))


if __name__ == "__main__":
    main()
