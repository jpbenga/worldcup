"""Publish a lightweight, secret-free acquisition status snapshot."""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_PATH = PROJECT_ROOT / "backend" / "data" / "snapshots" / "data_acquisition_status.json"
FRONTEND_PATH = PROJECT_ROOT / "frontend" / "src" / "assets" / "data" / "data_acquisition_status.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def update_source(source: dict[str, Any]) -> dict[str, Any]:
    snapshot = {"updated_at": utc_now(), "sources": []}
    if SNAPSHOT_PATH.exists():
        snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
        snapshot["updated_at"] = utc_now()

    sources = [item for item in snapshot.get("sources", []) if item.get("id") != source["id"]]
    sources.append(source)
    snapshot["sources"] = sorted(sources, key=lambda item: item["id"])

    SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    FRONTEND_PATH.parent.mkdir(parents=True, exist_ok=True)
    SNAPSHOT_PATH.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    shutil.copy2(SNAPSHOT_PATH, FRONTEND_PATH)
    return snapshot
