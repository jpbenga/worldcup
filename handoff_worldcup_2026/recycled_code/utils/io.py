"""Dependency-free JSON helpers for examples and integration."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

def load_json(path: str | Path) -> Any:
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)

def dump_json(data: Any, path: str | Path) -> None:
    with Path(path).open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
