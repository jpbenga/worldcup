"""Build a clearly labelled contender proxy when no official bracket exists."""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, load_json, utc_now
from backend.scripts.v2_6_live_utils import ENGINE_VERSION, VERSION, publish


def main() -> None:
    knockout = load_json(DATA_DIR / "generated" / "worldcup_knockout_structure_v2_6.json")
    if knockout["knockout_structure_available"]:
        raise SystemExit("Official bracket available; projected campaign proxy is not appropriate.")
    simulation = load_json(DATA_DIR / "generated" / "worldcup_tournament_simulation_conditioned_v2_6.json")
    ratings = {item["team_name"]: item for item in load_json(DATA_DIR / "normalized" / "team_ratings.json")}
    contenders = []
    for team, item in simulation["teams"].items():
        rating = ratings.get(team, {})
        elo = float(rating.get("elo_rating", 1500))
        elo_strength = 1 / (1 + math.exp(-(elo - 1750) / 180))
        proxy = 0.62 * item["qualification_probability"] + 0.23 * item["finish_first_probability"] + 0.15 * elo_strength
        likely_rank = max(range(1, 5), key=lambda rank: item[f"finish_{('first','second','third','fourth')[rank-1]}_probability"])
        contenders.append({
            "team": team, "group": item["group"], "qualification_probability": item["qualification_probability"],
            "group_winner_probability": item["finish_first_probability"], "elo_rating": rating.get("elo_rating"),
            "elo_rank": rating.get("rank"), "contender_proxy_score": proxy, "most_probable_group_finish": likely_rank,
            "campaign_steps": [
                {"label": "Phase de groupes", "detail": f"Rang le plus probable : {likely_rank}"},
                {"label": "Qualification", "detail": f"Probabilité : {item['qualification_probability']:.1%}"},
                {"label": "Après les groupes", "detail": "Bracket officiel indisponible; aucun adversaire inventé."},
            ],
        })
    contenders.sort(key=lambda item: item["contender_proxy_score"], reverse=True)
    report = {
        "version": VERSION, "engine_version": ENGINE_VERSION, "generated_at": utc_now(),
        "path_type": "projected_campaign_proxy", "is_official_champion_simulation": False,
        "champion_proxy": contenders[0]["team"], "champion_proxy_score": contenders[0]["contender_proxy_score"],
        "top_contenders": contenders[:10], "team_paths": {item["team"]: item["campaign_steps"] for item in contenders},
        "limitations": [
            "Knockout bracket unavailable; champion proxy is not an official champion probability.",
            "Proxy combines conditioned group qualification, group-win probability and current Elo context.",
            "No knockout opponent, final pairing or trophy path is invented.",
        ],
    }
    publish(report, "worldcup_projected_campaign_v2_6.json")
    (ROOT / "docs" / "WORLDCUP_PROJECTED_CAMPAIGN_V2_6.md").write_text(
        f"""# World Cup Projected Campaign V2.6

Because no official knockout bracket mapping is available, V2.6 publishes a
`projected_campaign_proxy`, not a simulated official champion path.

The leading proxy contender is `{contenders[0]["team"]}` with a composite
proxy score of `{contenders[0]["contender_proxy_score"]:.3f}`. The score
combines conditioned group qualification, group-winner probability and
current Elo context. It must not be interpreted as a champion probability.

No opponent, final pairing or knockout route is invented.

The proxy exists to make the simulation experience more expressive while
preserving epistemic honesty. Qualification probability remains the dominant
input, group-winner probability adds campaign momentum, and Elo contributes a
bounded strength context. The proxy score is a ranking device only and is not
calibrated as a probability of lifting the trophy.
""", encoding="utf-8")
    print(f"V2.6 projected campaign: proxy leader={contenders[0]['team']}")


if __name__ == "__main__":
    main()
