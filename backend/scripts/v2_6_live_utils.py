"""Shared publication helpers for the V2.6 live-results product layer."""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, write_json

ROOT = Path(__file__).resolve().parents[2]
VERSION = "v2.6"
ENGINE_VERSION = "quant_hybrid_v2.2"


def publish(payload: Any, name: str) -> None:
    generated = DATA_DIR / "generated" / name
    write_json(payload, generated)
    shutil.copy2(generated, DATA_DIR / "snapshots" / name)
    if os.getenv("MATCHDAY_SKIP_FRONTEND_COPY") != "1":
        shutil.copy2(generated, FRONTEND_DATA_DIR / name)


def release_matches() -> list[dict[str, Any]]:
    payload = load_json(DATA_DIR / "generated" / "worldcup_2026_predictions_release_candidate_v2_4.json")
    return payload["matches"]
