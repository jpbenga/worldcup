"""Promote V2.30 candidate predictions to active predictions after explicit confirmation.

This script is intentionally not called by the V2.30 validation chain.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, utc_now, write_json


PROMOTION_MANIFEST = "full_stats_engine_promotion_manifest_v2_30.json"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--confirm-promote-v2-30", action="store_true")
    parser.add_argument("--rollback-manifest", type=str, default=None)
    args = parser.parse_args()
    if args.rollback_manifest:
        manifest = load_json(Path(args.rollback_manifest))
        for item in manifest.get("archives", []):
            source = ROOT / item["archive"]
            target = ROOT / item["target"]
            if not source.exists():
                raise SystemExit(f"Rollback archive missing: {source}")
            shutil.copy2(source, target)
        print("Rolled back V2.30 full stats promotion from manifest.")
        return
    if not args.confirm_promote_v2_30:
        raise SystemExit("Refusing to promote without --confirm-promote-v2-30")
    decision = load_json(DATA_DIR / "generated" / "full_stats_engine_promotion_decision_v2_30.json")
    if not decision.get("promote_candidate"):
        raise SystemExit("Promotion decision does not allow promotion.")
    candidate = load_json(DATA_DIR / "generated" / "predictions_full_stats_candidate_v2_30.json")
    stamp = utc_now().replace(":", "").replace("-", "").replace(".", "")
    archives = []
    for path in (
        DATA_DIR / "generated" / "predictions.json",
        DATA_DIR / "snapshots" / "predictions.json",
        FRONTEND_DATA_DIR / "predictions.json",
    ):
        if path.exists():
            archive = path.with_name(f"{path.stem}_pre_full_stats_v2_30_{stamp}{path.suffix}")
            shutil.copy2(path, archive)
            archives.append({"target": path.relative_to(ROOT).as_posix(), "archive": archive.relative_to(ROOT).as_posix()})
        write_json(candidate, path)
    manifest = {
        "version": "v2.30",
        "promoted_at": utc_now(),
        "candidate": "backend/data/generated/predictions_full_stats_candidate_v2_30.json",
        "archives": archives,
        "rollback_command": f"python3 backend/scripts/promote_full_stats_engine_v2_30.py --rollback-manifest backend/data/generated/{PROMOTION_MANIFEST}",
    }
    write_json(manifest, DATA_DIR / "generated" / PROMOTION_MANIFEST)
    write_json(manifest, DATA_DIR / "snapshots" / PROMOTION_MANIFEST)
    print("Promoted V2.30 full stats candidate predictions to active predictions.")


if __name__ == "__main__":
    main()
