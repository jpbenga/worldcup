"""Shared publication and metric helpers for V2.12 transparency artifacts."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, write_json

ROOT = Path(__file__).resolve().parents[2]
VERSION = "v2.12"
ENGINE = "quant_hybrid_v2.2"
CANDIDATE = "score_matrix_candidate_v2.8"


def publish(payload: Any, name: str) -> None:
    generated = DATA_DIR / "generated" / name
    write_json(payload, generated)
    shutil.copy2(generated, DATA_DIR / "snapshots" / name)
    shutil.copy2(generated, FRONTEND_DATA_DIR / name)


def hit_metric(values: list[bool]) -> dict[str, float | int]:
    hits = sum(values)
    total = len(values)
    return {"hits": hits, "total": total, "rate": hits / total if total else 0.0}


def dnb_metric(outcomes: list[str]) -> dict[str, float | int]:
    wins = outcomes.count("win")
    losses = outcomes.count("loss")
    pushes = outcomes.count("push")
    decided = wins + losses
    total = decided + pushes
    return {
        "wins": wins,
        "losses": losses,
        "pushes": pushes,
        "total": total,
        "win_rate_excluding_pushes": wins / decided if decided else 0.0,
        "non_loss_including_pushes": (wins + pushes) / total if total else 0.0,
    }


def public_headline(evaluation: dict[str, Any]) -> str:
    if not evaluation["available"]:
        return "Prédiction pré-match figée"
    if evaluation["exact_score_hit"]:
        return "Score exact trouvé"
    if evaluation["one_x_two_hit"] and evaluation["top_5_hit"]:
        return "Bonne tendance et score dans le Top-5"
    if evaluation["one_x_two_hit"]:
        return "Bonne tendance 1X2, score différent"
    if evaluation["top_5_hit"]:
        return "Score dans le Top-5, tendance 1X2 ratée"
    return "Prédiction ratée, à analyser"
