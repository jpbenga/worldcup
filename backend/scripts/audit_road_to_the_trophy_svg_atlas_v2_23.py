"""Audit the existing Road to the Trophy SVG and interaction layer."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, utc_now, write_json

SCAN_ROOT = ROOT / "frontend/src"


def publish(name: str, payload: dict) -> None:
    target = DATA_DIR / "generated" / name
    write_json(payload, target)
    shutil.copy2(target, DATA_DIR / "snapshots" / name)
    shutil.copy2(target, FRONTEND_DATA_DIR / name)


def main() -> None:
    files = [path for path in SCAN_ROOT.rglob("*") if path.is_file()]
    readable = [path for path in files if path.suffix in {".ts", ".html", ".css", ".scss", ".svg"}]
    texts = {path: path.read_text(encoding="utf-8", errors="ignore") for path in readable}
    combined = "\n".join(texts.values())
    inline = [str(path.relative_to(ROOT)) for path, text in texts.items() if "<svg" in text]
    svg_files = [str(path.relative_to(ROOT)) for path in files if path.suffix == ".svg"]
    capabilities = {
        "team_paths_visible": "selectedTeamPath" in combined and "path-active" in combined,
        "group_to_knockout_connections": "groupPath(" in combined,
        "before_after_ghost_paths": "atlas-path--ghost" in combined,
        "changed_paths_highlighted": "node-changed" in combined,
        "hover_focus": ":hover" in combined,
        "selected_team_path": "selectedTeamPath" in combined,
        "reduced_motion_support": "prefers-reduced-motion" in combined,
    }
    weaknesses = [
        label for present, label in (
            ("<defs" in combined, "No reusable SVG defs for gradients, filters or markers."),
            ("marker-" in combined, "No directional markers on tournament connections."),
            (capabilities["before_after_ghost_paths"], "Before/after changes are not drawn as ghost paths."),
            (capabilities["reduced_motion_support"], "No reduced-motion handling for Atlas transitions."),
        ) if not present
    ]
    payload = {
        "version": "v2.23",
        "generated_at": utc_now(),
        "svg_usage": {
            "svg_files": svg_files,
            "inline_svg_components": inline,
            "paths_detected": combined.count("<path"),
            "groups_detected": combined.count("<g"),
            "defs_detected": "<defs" in combined,
            "markers_detected": "marker-" in combined,
            "gradients_detected": "Gradient" in combined,
        },
        "interaction_layer": {
            "d3_used": "d3-selection" in combined,
            "d3_zoom_used": "d3-zoom" in combined,
            "custom_zoom_used": "zoomBy(" in combined and "fitOverview(" in combined,
            "angular_signals_used": "signal(" in combined and "computed(" in combined,
            "timeline_state_used": "selectedStateId" in combined,
        },
        "atlas_capabilities": capabilities,
        "weaknesses": weaknesses,
        "opportunities": [
            "Introduce semantic SVG layers, stable ids, markers and subtle gradients.",
            "Draw previous changed connections as ghost paths during before/after comparison.",
            "Give selected and changed paths distinct visual semantics.",
            "Respect reduced-motion preferences without removing zoom and pan.",
        ],
        "verdict": "WARNING" if weaknesses else "PASS",
    }
    publish("road_to_the_trophy_svg_atlas_audit_v2_23.json", payload)
    print(f"V2.23 SVG Atlas audit: {payload['verdict']}")


if __name__ == "__main__":
    main()
