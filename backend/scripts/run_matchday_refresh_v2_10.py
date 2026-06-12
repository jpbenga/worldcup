"""Run the complete result-aware World Cup matchday refresh pipeline."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, load_json, utc_now
from backend.scripts.v2_10_refresh_utils import (
    CANDIDATE, ENGINE, VERSION, child_environment, git_changes, is_expected_refresh, protected_hashes, publish,
)


def command(script: str, *arguments: str) -> list[str]:
    return [sys.executable, f"backend/scripts/{script}", *arguments]


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    fetch = parser.add_mutually_exclusive_group()
    fetch.add_argument("--fetch", action="store_true", help="Attempt one cached API-Football refresh.")
    fetch.add_argument("--no-fetch", action="store_true", help="Use only cached/already generated result data.")
    parser.add_argument("--simulations", type=int, default=50000)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-frontend-copy", action="store_true")
    parser.add_argument("--force", action="store_true", help="Continue after a failed step and force API refresh when fetching.")
    args = parser.parse_args(argv)
    if args.simulations <= 0:
        raise SystemExit("--simulations must be positive")

    steps = [
        ("results", command("fetch_worldcup_2026_results_v2_6.py", *(["--force-refresh"] if args.fetch else ["--no-fetch"]))),
        ("prediction_evaluation", command("evaluate_predictions_against_results_v2_6.py")),
        ("live_standings", command("build_live_group_standings_v2_7.py")),
        ("match_state", command("build_match_state_view_model_v2_7.py")),
        ("active_conditioned_simulation", command("run_worldcup_tournament_simulation_v2_6.py", "--simulations", str(args.simulations))),
        ("candidate_simulation", command("run_candidate_tournament_simulation_v2_9.py", "--simulations", str(args.simulations))),
        ("active_candidate_comparison", command("compare_active_vs_candidate_simulation_v2_9.py")),
        ("active_projected_campaign", command("build_worldcup_projected_campaign_v2_6.py")),
        ("candidate_projected_campaign", command("build_candidate_projected_campaign_v2_9.py")),
        ("result_consistency_validation", command("validate_result_consistency_v2_7.py")),
        ("dual_matrix_validation", command("validate_dual_matrix_v2_9.py")),
    ]
    if args.dry_run:
        print(json.dumps({
            "version": VERSION, "dry_run": True, "fetch_enabled": args.fetch, "simulation_count": args.simulations,
            "skip_frontend_copy": args.skip_frontend_copy, "steps": [{"name": name, "command": cmd} for name, cmd in steps],
            "note": "No final artifact was written.",
        }, indent=2))
        return

    before_hashes, before_changes = protected_hashes(), git_changes()
    records = []
    failed = False
    for name, cmd in steps:
        started = time.monotonic()
        result = subprocess.run(cmd, cwd=ROOT, env=child_environment(args.skip_frontend_copy), text=True, capture_output=True)
        record = {
            "name": name, "command": cmd, "status": "pass" if result.returncode == 0 else "fail",
            "return_code": result.returncode, "duration_seconds": round(time.monotonic() - started, 3),
            "stdout": result.stdout.strip(), "stderr": result.stderr.strip(),
        }
        records.append(record)
        print(f"[{record['status'].upper()}] {name}: {record['stdout'] or record['stderr']}")
        if result.returncode:
            failed = True
            if not args.force:
                break

    after_hashes, after_changes = protected_hashes(), git_changes()
    modified_during_run = sorted(set(after_changes) - set(before_changes))
    results = load_json(DATA_DIR / "generated" / "worldcup_2026_results_v2_6.json")
    model_modified = before_hashes != after_hashes
    manifest = {
        "version": VERSION, "generated_at": utc_now(), "engine_version": ENGINE, "candidate_version": CANDIDATE,
        "fetch_enabled": args.fetch, "fetch_mode": "api_if_configured" if args.fetch else "cached_only",
        "simulation_count": args.simulations, "skip_frontend_copy": args.skip_frontend_copy, "force": args.force,
        "steps": records, "outputs": sorted(path for path in after_changes if is_expected_refresh(path)),
        "result_summary": {
            "finished_matches": results["finished_count"], "live_matches": results["live_count"],
            "not_started_matches": results["not_started_count"],
        },
        "model_integrity": {
            "pre_match_predictions_modified": model_modified, "protected_hashes_before": before_hashes,
            "protected_hashes_after": after_hashes, "retrain_run": False, "optuna_run": False,
        },
        "git_hygiene": {
            "preexisting_modified_files": before_changes,
            "expected_modified_files": sorted(path for path in modified_during_run if is_expected_refresh(path)),
            "unexpected_modified_files": sorted(path for path in modified_during_run if not is_expected_refresh(path)),
        },
        "status": "fail" if failed or model_modified else "pass",
    }
    publish(manifest, "matchday_refresh_manifest_v2_10.json", args.skip_frontend_copy)
    (ROOT / "docs" / "MATCHDAY_REFRESH_MANIFEST_V2_10.md").write_text(f"""# Matchday Refresh Manifest V2.10

Status: **{manifest['status'].upper()}**. The operational refresh executed `{len(records)}` of `{len(steps)}` ordered steps with fetch mode `{manifest['fetch_mode']}` and `{args.simulations:,}` active/candidate simulations.

Result summary: `{manifest['result_summary']}`.

Protected pre-match prediction and model hashes changed: `{model_modified}`. Retraining and Optuna were not run.

Preexisting modified files remain visible in the JSON manifest. New unexpected files produced during this refresh: `{manifest['git_hygiene']['unexpected_modified_files']}`. The manifest never treats preexisting workspace changes as pipeline output.
""", encoding="utf-8")
    if manifest["status"] != "pass":
        raise SystemExit("V2.10 matchday refresh failed; inspect matchday_refresh_manifest_v2_10.json")
    print(f"V2.10 matchday refresh: PASS; finished={results['finished_count']}; simulations={args.simulations}")


if __name__ == "__main__":
    main()
