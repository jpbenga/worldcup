"""Shared publication and release-candidate helpers for V2.4."""

from __future__ import annotations

import math
import shutil
from pathlib import Path
from typing import Any

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, write_json

ROOT = Path(__file__).resolve().parents[2]
ENGINE_VERSION = "quant_hybrid_v2.2"
VERSION = "v2.4"


def publish(payload: Any, name: str) -> None:
    target = DATA_DIR / "generated" / name
    write_json(payload, target)
    shutil.copy2(target, DATA_DIR / "snapshots" / name)
    shutil.copy2(target, FRONTEND_DATA_DIR / name)


def fixture_map() -> dict[str, dict[str, Any]]:
    return {str(item["match_id"]): item for item in load_json(DATA_DIR / "normalized" / "matches.json")}


def score_entries(prediction: dict[str, Any]) -> list[dict[str, Any]]:
    raw = prediction["score_matrix"]
    return raw["probabilities"] if isinstance(raw, dict) else raw


def normalized_probability(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value)) and 0 <= float(value) <= 1


def enriched_prediction(prediction: dict[str, Any], fixture: dict[str, Any]) -> dict[str, Any]:
    metadata = {
        "fixture_id": fixture.get("api_football_fixture_id"),
        "home_team": fixture.get("home_team"),
        "away_team": fixture.get("away_team"),
        "kickoff_at": fixture.get("kickoff_at"),
        "group": fixture.get("group"),
        "stage": fixture.get("stage"),
        "round": fixture.get("round"),
        "venue": fixture.get("venue"),
        "city": fixture.get("city"),
    }
    return prediction | {key: value for key, value in metadata.items() if value is not None}
