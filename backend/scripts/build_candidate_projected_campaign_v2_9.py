"""Build a non-official projected-campaign proxy from the candidate simulation."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, load_json
from backend.scripts.v2_9_dual_matrix_utils import CANDIDATE_VERSION, ENGINE, VERSION, build_campaign, publish, utc_now


def main() -> None:
    simulation = load_json(DATA_DIR / "generated" / "worldcup_tournament_simulation_candidate_v2_9.json")
    active = load_json(DATA_DIR / "generated" / "worldcup_projected_campaign_v2_6.json")
    contenders = build_campaign(simulation)["contenders"]
    payload = {
        "generated_at": utc_now(), "version": VERSION, "engine_version": ENGINE, "candidate_version": CANDIDATE_VERSION,
        "candidate_status": "alternative_non_active", "path_type": "projected_campaign_proxy",
        "is_official_champion_simulation": False, "champion_proxy": contenders[0]["team"],
        "champion_proxy_score": contenders[0]["contender_proxy_score"], "active_champion_proxy": active["champion_proxy"],
        "top_contenders": contenders[:10], "team_paths": {row["team"]: row["campaign_steps"] for row in contenders},
        "limitations": [
            "Candidate proxy is non-active and is not an official champion simulation.",
            "Knockout bracket unavailable; no opponent or trophy path is invented.",
            "Proxy combines alternative group qualification, group-win probability and Elo context.",
        ],
    }
    publish(payload, "worldcup_projected_campaign_candidate_v2_9.json")
    active_names = [row["team"] for row in active["top_contenders"][:5]]
    candidate_names = [row["team"] for row in contenders[:5]]
    (ROOT / "docs" / "WORLDCUP_PROJECTED_CAMPAIGN_CANDIDATE_V2_9.md").write_text(f"""# World Cup Projected Campaign Candidate V2.9

The active projected-campaign proxy leader is `{active['champion_proxy']}`. The alternative candidate proxy leader is `{contenders[0]['team']}`.

- Active top contenders: `{active_names}`
- Candidate top contenders: `{candidate_names}`

This comparison describes how the alternative group-score distribution changes a proxy ranking. It is not a real champion simulation or a probability of lifting the trophy. The official knockout bracket remains unavailable, so V2.9 does not invent opponents, pairings or a trophy path.
""", encoding="utf-8")
    print(json.dumps({"active_proxy": active["champion_proxy"], "candidate_proxy": contenders[0]["team"]}))


if __name__ == "__main__":
    main()
