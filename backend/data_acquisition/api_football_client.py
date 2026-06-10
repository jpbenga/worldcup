"""Small API-Football client for controlled discovery calls."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import requests

from backend.config.settings import API_FOOTBALL_BASE_URL, API_FOOTBALL_KEY

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_ROOT = PROJECT_ROOT / "backend" / "data" / "raw" / "api_football"


class ApiFootballError(RuntimeError):
    """Raised when API-Football cannot return a usable JSON response."""


class ApiFootballClient:
    def __init__(self, max_calls: int = 10, timeout: int = 20) -> None:
        if not API_FOOTBALL_KEY:
            raise ApiFootballError("API_FOOTBALL_KEY is not configured in .env")
        self.max_calls = max_calls
        self.timeout = timeout
        self.call_count = 0

    def get(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        if self.call_count >= self.max_calls:
            raise ApiFootballError(f"Call limit reached ({self.max_calls})")
        self.call_count += 1
        clean_endpoint = endpoint.strip("/")
        url = f"{API_FOOTBALL_BASE_URL}/{clean_endpoint}"
        try:
            response = requests.get(
                url,
                headers={"x-apisports-key": API_FOOTBALL_KEY},
                params=params or {},
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise ApiFootballError(f"HTTP request failed for /{clean_endpoint}: {exc}") from exc
        try:
            payload = response.json()
        except requests.JSONDecodeError as exc:
            raise ApiFootballError(f"Invalid JSON returned by /{clean_endpoint}") from exc
        if not isinstance(payload, dict):
            raise ApiFootballError(f"Unexpected payload returned by /{clean_endpoint}")
        errors = payload.get("errors")
        count = len(payload.get("response", [])) if isinstance(payload.get("response"), list) else "n/a"
        print(f"API-Football /{clean_endpoint}: HTTP {response.status_code}, results={count}, errors={errors or 'none'}")
        return payload

    def save_raw_response(self, name: str, payload: dict[str, Any]) -> Path:
        path = RAW_ROOT / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return path
