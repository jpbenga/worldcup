"""Validate V2.13.1B Road to the Trophy generated contracts."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "backend" / "data"
FRONTEND = ROOT / "frontend" / "src" / "assets" / "data"
FILES = [
    "road_to_the_trophy_scenario_engine_v2_13_1B.json",
    "road_to_the_trophy_view_model_v2_13_1B.json",
    "worldcup_2026_official_bracket_mapping_v2_13_1B.json",
]


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    for name in FILES:
        generated = DATA / "generated" / name
        snapshot = DATA / "snapshots" / name
        frontend = FRONTEND / name
        assert generated.exists() and snapshot.exists() and frontend.exists(), name
        assert generated.read_bytes() == snapshot.read_bytes() == frontend.read_bytes(), name

    vm = read(DATA / "generated" / FILES[1])
    engine = read(DATA / "generated" / FILES[0])
    mapping = read(DATA / "generated" / FILES[2])
    assert vm["feature_name"] == "Road to the Trophy"
    assert vm["matches_total_target"] == 104
    assert vm["known_group_matches"] == 72
    assert vm["target_knockout_matches"] == 32
    assert len(vm["groups"]) == 12
    assert sum(len(group["matches"]) for group in vm["groups"]) == 72
    assert all(len(group["standings"]) == 4 for group in vm["groups"])
    assert all(len(group["matches"]) == 6 for group in vm["groups"])
    assert sum(len(item["matches"]) for item in vm["rounds"]) == 31
    assert vm["third_place"]["display_status"] == "to_confirm"
    assert engine["simulation_count"] == 50_000
    assert engine["full_simulated_paths_available"] is False
    assert mapping["official_bracket_available"] is False
    assert mapping["expected_knockout_matches"] == 32
    assert vm["credibility_audit"]["verdict"] == "FAIL_CALIBRATION_REVIEW_REQUIRED"

    report = {
        "version": "v2.13.1B",
        "passed": True,
        "status": "PASS",
        "checks": {
            "groups": 12,
            "group_matches": 72,
            "group_standings": 12,
            "projected_knockout_matches": 31,
            "third_place_placeholder": True,
            "simulation_count": 50_000,
            "official_bracket_claimed": False,
            "credibility_warning_present": True,
            "copies_match": True,
        },
    }
    for directory in (DATA / "generated", DATA / "snapshots", FRONTEND):
        (directory / "road_to_the_trophy_validation_v2_13_1B.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
    print("Road to the Trophy V2.13.1B validation: PASS")


if __name__ == "__main__":
    main()
