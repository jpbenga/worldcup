"""Perform one-request discovery and sample parsing for Elo Ratings."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import requests

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.data_acquisition.elo_ratings_client import EloRatingsClient, SOURCE_URL
from backend.data_acquisition.status import update_source


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("discovery", "sample"), required=True)
    args = parser.parse_args()
    client = EloRatingsClient()
    try:
        html = client.fetch_page()
        page_path = client.save_page(html)
        rows = client.parse_sample(html)
        if args.mode == "sample":
            sample_path = client.save_sample(rows)
            print(f"Saved {sample_path.relative_to(PROJECT_ROOT)}")
        print(f"Saved {page_path.relative_to(PROJECT_ROOT)}; parsed rows={len(rows)}")
        update_source(
            {
                "id": "elo_ratings",
                "label": "Elo Ratings",
                "configured": True,
                "reachable": True,
                "usable": bool(rows),
                "worldcup_2026_found": False,
                "notes": (
                    f"Page reachable at {SOURCE_URL}; parsed {len(rows)} row(s)."
                    if rows
                    else f"Page reachable at {SOURCE_URL}; automatic parsing requires validation."
                ),
            }
        )
    except requests.RequestException as exc:
        update_source(
            {
                "id": "elo_ratings",
                "label": "Elo Ratings",
                "configured": True,
                "reachable": False,
                "usable": False,
                "worldcup_2026_found": False,
                "notes": f"Request failed: {exc}",
            }
        )
        raise SystemExit(f"Elo Ratings request failed: {exc}") from exc


if __name__ == "__main__":
    main()
