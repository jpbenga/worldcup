"""Single local command to refresh when needed and launch SimuMondial."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def call(script: str, *args: str) -> None:
    print(f"[RUN] {script} {' '.join(args)}")
    result = subprocess.run([sys.executable, f"backend/scripts/{script}", *args], cwd=ROOT)
    if result.returncode:
        raise SystemExit(f"{script} failed with code {result.returncode}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    refresh = parser.add_mutually_exclusive_group()
    refresh.add_argument("--auto-refresh", action="store_true")
    refresh.add_argument("--no-refresh", action="store_true")
    refresh.add_argument("--force-refresh", action="store_true")
    fetch = parser.add_mutually_exclusive_group()
    fetch.add_argument("--fetch", action="store_true")
    fetch.add_argument("--no-fetch", action="store_true")
    parser.add_argument("--simulations", type=int, default=50000)
    parser.add_argument("--fetch-odds", action="store_true", help="Fetch API-Football odds explicitly; may consume quota.")
    parser.add_argument("--no-start", action="store_true")
    args = parser.parse_args()
    call("operator_doctor_v2_17.py")
    call("check_local_refresh_needed_v2_18.py", "--simulations", str(args.simulations), *(["--force"] if args.force_refresh else []))
    sys.path.insert(0, str(ROOT))
    from backend.scripts.pipeline_utils import DATA_DIR, load_json
    decision = load_json(DATA_DIR / "generated/local_refresh_needed_v2_18.json")
    should_refresh = args.force_refresh or (args.auto_refresh and decision["refresh_needed"])
    if should_refresh:
        unified_args = ["--simulations", str(args.simulations), "--fetch" if args.fetch else "--no-fetch"]
        if args.force_refresh: unified_args.append("--force")
        if args.fetch_odds: unified_args.append("--fetch-odds")
        call("run_unified_local_refresh_v2_18.py", *unified_args)
    else:
        print("[SKIP] Unified refresh not required or disabled.")
    call("build_data_freshness_status_v2_17.py")
    if args.no_start:
        print("[SKIP] Frontend launch disabled by --no-start.")
        return
    if not (ROOT / "frontend/package.json").exists() or not shutil.which("npm"):
        raise SystemExit("Frontend package or npm is missing")
    command = 'source "$HOME/.nvm/nvm.sh" && nvm use && npm start'
    print("[RUN] frontend npm start")
    raise SystemExit(subprocess.run(["/bin/zsh", "-lc", command], cwd=ROOT / "frontend").returncode)


if __name__ == "__main__":
    main()
