"""Safely orchestrate the existing V2.10 Matchday refresh."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.operator_utils_v2_17 import publish
from backend.scripts.pipeline_utils import utc_now


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--fetch", action="store_true")
    mode.add_argument("--no-fetch", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--simulations", type=int, default=50000)
    args = parser.parse_args()
    if args.simulations <= 0:
        raise SystemExit("--simulations must be positive")
    refresh_script = ROOT / "backend/scripts/run_matchday_refresh_v2_10.py"
    validate_script = ROOT / "backend/scripts/validate_matchday_refresh_v2_10.py"
    missing = [str(path.relative_to(ROOT)) for path in (refresh_script, validate_script) if not path.exists()]
    mode_name = "dry-run" if args.dry_run else "fetch" if args.fetch else "no-fetch"
    refresh = [sys.executable, str(refresh_script.relative_to(ROOT)), "--simulations", str(args.simulations), "--fetch" if args.fetch else "--no-fetch"]
    steps = [{"name": "matchday_refresh_v2_10", "command": refresh}]
    if args.validate:
        steps.append({"name": "validate_matchday_refresh_v2_10", "command": [sys.executable, str(validate_script.relative_to(ROOT))]})
    errors, records = list(missing), []
    if not args.dry_run and not errors:
        for step in steps:
            result = subprocess.run(step["command"], cwd=ROOT, text=True)
            records.append({**step, "return_code": result.returncode, "status": "pass" if result.returncode == 0 else "fail"})
            if result.returncode:
                errors.append(f"{step['name']} failed")
                break
    else:
        records = [{**step, "status": "planned"} for step in steps]
    manifest = {
        "version": "v2.17", "generated_at": utc_now(), "mode": mode_name, "simulations": args.simulations,
        "steps": records, "validation": {"requested": args.validate, "status": "not_run" if args.dry_run else "pass" if not errors and args.validate else "not_requested"},
        "critical_outputs": {"v2_10_manifest": "backend/data/generated/matchday_refresh_manifest_v2_10.json"},
        "active_predictions_changed": False, "road_to_the_trophy_engine_changed": False,
        "warnings": ["Dry-run: no refresh command executed."] if args.dry_run else [], "errors": errors,
    }
    if not args.dry_run:
        publish("operator_refresh_manifest_v2_17.json", manifest, frontend=True)
    for step in records:
        print(f"[{step['status'].upper()}] {' '.join(step['command'])}")
    if errors:
        raise SystemExit("; ".join(errors))


if __name__ == "__main__":
    main()
