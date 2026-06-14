"""Build a stable geometry contract for the Road to the Trophy SVG Atlas."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, utc_now, write_json

WIDTH, HEIGHT = 4300, 3040
ROUND_X = [1050, 1710, 2370, 3030, 3690]


def publish(name: str, payload: dict) -> None:
    target = DATA_DIR / "generated" / name
    write_json(payload, target)
    shutil.copy2(target, DATA_DIR / "snapshots" / name)
    shutil.copy2(target, FRONTEND_DATA_DIR / name)


def group_position(index: int) -> tuple[float, float]:
    return 50 + (index % 2) * 430, 80 + (index // 2) * 490


def match_position(round_index: int, match_index: int, count: int) -> tuple[float, float]:
    return ROUND_X[round_index], ((HEIGHT - 160) / count) * (match_index + 0.5)


def curve(x1: float, y1: float, x2: float, y2: float) -> str:
    middle = (x1 + x2) / 2
    return f"M {x1:.2f} {y1:.2f} C {middle:.2f} {y1:.2f}, {middle:.2f} {y2:.2f}, {x2:.2f} {y2:.2f}"


def main() -> None:
    engine = load_json(DATA_DIR / "generated/road_to_the_trophy_coherent_view_model_v2_21.json")
    timeline = load_json(DATA_DIR / "generated/road_to_the_trophy_scenario_timeline_v2_22.json")
    nodes, connections = [], []
    for index, group in enumerate(engine["groups"]):
        x, y = group_position(index)
        nodes.append({"id": f"group-{group['group']}", "type": "group", "label": f"Groupe {group['group']}", "x": x, "y": y, "width": 400, "height": 470})
        for link in group.get("knockout_links", []):
            target_index = next((i for i, row in enumerate(engine["rounds"][0]["matches"]) if row["match_id"] == link), -1)
            if target_index >= 0:
                tx, ty = match_position(0, target_index, 16)
                connections.append({"id": f"group-{group['group']}-to-{link}", "from": f"group-{group['group']}", "to": f"match-{link}", "path": curve(x + 400, y + 235, tx, ty), "type": "qualification"})
    for round_index, round_row in enumerate(engine["rounds"]):
        for match_index, match in enumerate(round_row["matches"]):
            x, y = match_position(round_index, match_index, len(round_row["matches"]))
            nodes.append({"id": f"match-{match['match_id']}", "type": "match", "label": round_row["label"], "x": x, "y": y - 52, "width": 330, "height": 104})
            if round_index < len(engine["rounds"]) - 1:
                next_round = engine["rounds"][round_index + 1]["matches"]
                target_index = next((i for i, row in enumerate(next_round) if row["match_id"] == match["next_match_id"]), -1)
                if target_index >= 0:
                    tx, ty = match_position(round_index + 1, target_index, len(next_round))
                    connections.append({"id": f"match-{match['match_id']}-to-{match['next_match_id']}", "from": f"match-{match['match_id']}", "to": f"match-{match['next_match_id']}", "path": curve(x + 330, y, tx, ty), "type": "advance"})
    current_diff = timeline.get("diffs", [])[-1] if timeline.get("diffs") else {}
    changed_matches = {row["match_id"] for row in current_diff.get("bracket_changes", [])}
    team_paths = [
        {
            "team": team,
            "team_id": "".join(ch for ch in team.upper() if ch.isalnum())[:12],
            "state": "current",
            "segments": [step["match_id"] for step in path.get("knockout_path", [])],
            "changed": any(step["match_id"] in changed_matches for step in path.get("knockout_path", [])),
            "highlight_level": "changed" if any(step["match_id"] in changed_matches for step in path.get("knockout_path", [])) else "normal",
        }
        for team, path in engine["team_paths"].items()
    ]
    payload = {
        "version": "v2.23",
        "generated_at": utc_now(),
        "atlas": {
            "viewBox": {"x": 0, "y": 0, "width": WIDTH, "height": HEIGHT},
            "nodes": nodes,
            "connections": connections,
            "team_paths": team_paths,
            "diff_paths": [row["match_id"] for row in current_diff.get("bracket_changes", [])],
        },
    }
    publish("road_to_the_trophy_svg_atlas_view_model_v2_23.json", payload)
    print(f"V2.23 SVG Atlas view model: {len(nodes)} nodes, {len(connections)} connections")


if __name__ == "__main__":
    main()
