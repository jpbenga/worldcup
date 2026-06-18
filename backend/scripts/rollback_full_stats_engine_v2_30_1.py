"""Rollback V2.30.1 full-stats prediction promotion from archived files."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, utc_now, write_json

VERSION = "v2.30.1"
MANIFEST = DATA_DIR / "generated" / "full_stats_engine_promotion_manifest_v2_30_1.json"
ROLLBACK_MANIFEST_NAME = "full_stats_engine_rollback_manifest_v2_30_1.json"


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def main() -> None:
    manifest = load_json(MANIFEST)
    restored = []
    for item in manifest.get("archive_paths", []):
        archive = ROOT / item["archive_path"]
        target = ROOT / item["active_path"]
        if not archive.exists():
            raise SystemExit(f"Archive missing: {archive}")
        shutil.copy2(archive, target)
        restored.append({"role": item["role"], "archive_path": rel(archive), "restored_path": rel(target)})
    rollback = {
        "version": VERSION,
        "rolled_back_at": utc_now(),
        "promotion_manifest": rel(MANIFEST),
        "restored": restored,
        "road_to_trophy_changed": False,
    }
    for base in (DATA_DIR / "generated", DATA_DIR / "snapshots", FRONTEND_DATA_DIR):
        write_json(rollback, base / ROLLBACK_MANIFEST_NAME)
    print(f"{VERSION} rollback restored {len(restored)} predictions files")


if __name__ == "__main__":
    main()
