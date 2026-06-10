"""Read validated team mappings and expose experimental Elo match features."""

from __future__ import annotations

import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEAM_IDENTITY_MAP_PATH = PROJECT_ROOT / "backend" / "data" / "mappings" / "team_identity_map.json"


def normalize_name(name: str) -> str:
    folded = unicodedata.normalize("NFKD", name.casefold())
    without_accents = "".join(character for character in folded if not unicodedata.combining(character))
    return " ".join(re.sub(r"[^a-z0-9]+", " ", without_accents).split())


@lru_cache(maxsize=1)
def _elo_by_team_name() -> dict[str, int]:
    mappings: list[dict[str, Any]] = json.loads(TEAM_IDENTITY_MAP_PATH.read_text(encoding="utf-8"))
    ratings: dict[str, int] = {}
    for item in mappings:
        elo = item.get("elo")
        mapping = item.get("mapping", {})
        if not isinstance(elo, dict) or mapping.get("status") not in {"auto_validated", "manual_validated"}:
            continue
        rating = elo.get("elo_rating")
        if not isinstance(rating, int):
            continue
        names = (
            item.get("team_id"),
            item.get("display_name"),
            item.get("api_football", {}).get("name"),
            elo.get("team_name"),
        )
        for name in names:
            if isinstance(name, str) and name:
                ratings[normalize_name(name)] = rating
    return ratings


def get_team_elo(team_name: str) -> int | None:
    """Return a validated mapped Elo rating, or None when none exists."""
    return _elo_by_team_name().get(normalize_name(team_name))


def get_match_elo_features(home_team: str, away_team: str) -> dict[str, int | float | bool | None]:
    """Return symmetric Elo strengths only when both teams have mapped ratings."""
    home_elo = get_team_elo(home_team)
    away_elo = get_team_elo(away_team)
    if home_elo is None or away_elo is None:
        return {
            "home_elo": None,
            "away_elo": None,
            "elo_diff": None,
            "home_elo_advantage": None,
            "away_elo_advantage": None,
            "elo_available": False,
        }

    home_advantage = 1.0 / (1.0 + 10.0 ** (-(home_elo - away_elo) / 400.0))
    return {
        "home_elo": home_elo,
        "away_elo": away_elo,
        "elo_diff": home_elo - away_elo,
        "home_elo_advantage": home_advantage,
        "away_elo_advantage": 1.0 - home_advantage,
        "elo_available": True,
    }
