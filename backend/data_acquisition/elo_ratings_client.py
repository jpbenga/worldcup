"""Minimal, respectful client for exploring Elo Ratings."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import requests

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_ROOT = PROJECT_ROOT / "backend" / "data" / "raw" / "elo"
SOURCE_URL = "https://eloratings.net/"


class EloRatingsClient:
    def fetch_page(self, timeout: int = 20) -> str:
        response = requests.get(SOURCE_URL, headers={"User-Agent": "worldcup-data-spike/0.3"}, timeout=timeout)
        response.raise_for_status()
        return response.text

    def save_page(self, html: str) -> Path:
        path = RAW_ROOT / "discovery" / "eloratings_page_sample.html"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8")
        return path

    def parse_sample(self, html: str, limit: int = 20) -> list[dict[str, Any]]:
        pattern = re.compile(
            r"<tr[^>]*>.*?<td[^>]*>\s*(\d+)\s*</td>.*?<a[^>]*>([^<]+)</a>.*?<td[^>]*>\s*(\d{3,4})\s*</td>",
            re.IGNORECASE | re.DOTALL,
        )
        rows = []
        for rank, team_name, rating in pattern.findall(html):
            rows.append({"rank": int(rank), "team_name": team_name.strip(), "elo_rating": int(rating)})
            if len(rows) >= limit:
                break
        return rows

    def save_sample(self, rows: list[dict[str, Any]]) -> Path:
        path = RAW_ROOT / "samples" / "elo_ratings_sample.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return path
