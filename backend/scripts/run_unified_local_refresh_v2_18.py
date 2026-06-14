"""Refresh all local layers that depend on official results."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import utc_now
from backend.scripts.unified_local_refresh_utils_v2_18 import protected_hashes, publish, rebuild_v4, refresh_decision, run

STEPS = [
    ("operator_doctor", "operator_doctor_v2_17.py", []),
    ("matchday_results_and_views", "run_matchday_refresh_v2_10.py", []),
    ("matchday_validation", "validate_matchday_refresh_v2_10.py", []),
    ("prediction_history", "build_prediction_history_v2_12.py", []),
    ("model_scoreboard", "build_model_scoreboard_v2_12.py", []),
    ("performance_timeline", "build_prediction_timeline_v2_12.py", []),
    ("data_freshness", "build_data_freshness_status_v2_17.py", []),
    ("road_to_the_trophy_validation", "validate_tournament_simulation_engine_v4_v2_21.py", []),
    ("road_to_the_trophy_timeline_validation", "validate_road_to_the_trophy_scenario_timeline_v2_22.py", []),
    ("svg_atlas_audit", "audit_road_to_the_trophy_svg_atlas_v2_23.py", []),
    ("svg_atlas_view_model", "build_road_to_the_trophy_svg_atlas_view_model_v2_23.py", []),
    ("odds_snapshot", "fetch_api_football_odds_v2_23.py", []),
    ("odds_value_signals", "build_match_odds_value_signals_v2_23.py", []),
    ("svg_atlas_and_odds_validation", "validate_svg_atlas_and_odds_experience_v2_23.py", []),
]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--fetch", action="store_true")
    mode.add_argument("--no-fetch", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--simulations", type=int, default=50000)
    parser.add_argument("--skip-frontend-copy", action="store_true")
    parser.add_argument("--fetch-odds", action="store_true")
    args = parser.parse_args()
    decision = refresh_decision(args.simulations, args.force)
    mode_name = "dry-run" if args.dry_run else "fetch" if args.fetch else "no-fetch"
    planned = []
    for name, script, extra in STEPS:
        exists = (ROOT / "backend/scripts" / script).exists()
        heavy = name == "matchday_results_and_views"
        should_run = exists and (args.force or decision["refresh_needed"] or name in ("operator_doctor", "data_freshness"))
        arguments = list(extra)
        if name == "odds_snapshot" and args.fetch_odds:
            arguments = ["--fetch"]
        if name == "matchday_results_and_views":
            arguments = ["--simulations", str(args.simulations), "--fetch" if args.fetch else "--no-fetch"]
            if args.skip_frontend_copy: arguments.append("--skip-frontend-copy")
        planned.append({"name": name, "script": script, "arguments": arguments, "status": "planned" if should_run else "skipped", "reason": "refresh_required" if should_run else "safe_to_skip", "outputs": []})
    planned.insert(6, {"name": "tournament_engine_v4_and_road_to_the_trophy", "script": "internal_v4_rebuild", "arguments": [], "status": "planned" if decision["road_to_the_trophy_rebuild_needed"] else "skipped", "reason": "official_results_changed" if decision["road_to_the_trophy_rebuild_needed"] else "safe_to_skip", "outputs": ["tournament_simulation_engine_v4_results_v2_21.json", "road_to_the_trophy_engine.json"]})
    manifest = {
        "version": "v2.18", "generated_at": utc_now(), "mode": mode_name, "simulations": args.simulations, "force": args.force,
        "data_changed": decision["refresh_needed"], "new_results_detected": max(0, decision["finished_results"] - decision["v3_locked_results"]),
        "steps": planned, "outputs": {"results": [], "transparency": [], "road_to_the_trophy": [], "frontend_assets": []},
        "active_predictions_changed": False, "road_to_the_trophy_regenerated": False, "validations": {}, "warnings": [], "errors": [],
    }
    if args.dry_run:
        for step in planned: print(f"[{step['status'].upper()}] {step['script']} ({step['reason']})")
        return
    before = protected_hashes()
    for step in planned:
        if step["status"] == "skipped": continue
        if step["script"] == "internal_v4_rebuild":
            try:
                rebuild_v4()
                step["status"] = "pass"
                manifest["road_to_the_trophy_regenerated"] = True
            except Exception as exc:
                step["status"] = "fail"; manifest["errors"].append(f"{step['name']}: {exc}"); break
        else:
            result = run(step["script"], *step["arguments"])
            step["status"] = "pass" if result.returncode == 0 else "fail"
            step["stdout"] = result.stdout.strip(); step["stderr"] = result.stderr.strip()
            if result.returncode:
                manifest["errors"].append(f"{step['name']}: {result.stderr or result.stdout}"); break
        print(f"[{step['status'].upper()}] {step['name']}")
    manifest["active_predictions_changed"] = before != protected_hashes()
    if manifest["active_predictions_changed"]: manifest["errors"].append("Protected active predictions changed")
    manifest["validations"] = {"passed": not manifest["errors"]}
    publish("unified_local_refresh_manifest_v2_18.json", manifest, frontend=not args.skip_frontend_copy)
    if manifest["errors"]: raise SystemExit("Unified refresh failed; inspect manifest")


if __name__ == "__main__":
    main()
