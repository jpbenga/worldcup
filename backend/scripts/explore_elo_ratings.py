"""Explore Elo Ratings through three controlled acquisition strategies."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import requests

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.data_acquisition.elo_ratings_client import DISCOVERY_ROOT, EloRatingsClient, TARGETS
from backend.data_acquisition.status import update_source


def raw_html(client: EloRatingsClient) -> None:
    summary = client.fetch_raw_pages()
    print(f"Raw HTML: {len(summary)} page(s), summary={DISCOVERY_ROOT / 'raw_html_summary.json'}")


def network(client: EloRatingsClient) -> None:
    records = client.capture_network()
    json_count = sum(1 for record in records if "json" in str(record.get("content_type", "")).lower())
    tsv_count = sum(1 for record in records if "tab-separated-values" in str(record.get("content_type", "")).lower())
    print(f"Network capture: {len(records)} response(s), JSON responses={json_count}, TSV responses={tsv_count}")


def rendered_table(client: EloRatingsClient) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    rows = client.capture_rendered_tables()
    structured_rows = client.parse_world_tsv()
    preferred_rows = structured_rows if client.rankings_are_reliable(structured_rows) else rows
    normalized = client.normalize_rankings(preferred_rows)
    print(
        f"Rendered table rows={len(rows)}, structured World.tsv rows={len(structured_rows)}, "
        f"normalized ratings={len(normalized)}"
    )
    return rows, normalized


def update_status(client: EloRatingsClient, rows: list[dict[str, object]], normalized: list[dict[str, object]]) -> None:
    network_path = DISCOVERY_ROOT / "network_requests.json"
    records = json.loads(network_path.read_text(encoding="utf-8")) if network_path.exists() else []
    json_count = sum(1 for record in records if "json" in str(record.get("content_type", "")).lower())
    tsv_count = sum(
        1 for record in records if "tab-separated-values" in str(record.get("content_type", "")).lower()
    )
    if not rows:
        rendered_path = PROJECT_ROOT / "backend" / "data" / "raw" / "elo" / "samples" / "elo_rankings_rendered_table.json"
        rows = json.loads(rendered_path.read_text(encoding="utf-8")) if rendered_path.exists() else []
    if not normalized:
        normalized_path = PROJECT_ROOT / "backend" / "data" / "normalized" / "team_ratings.json"
        normalized = json.loads(normalized_path.read_text(encoding="utf-8")) if normalized_path.exists() else []
    update_source(
        {
            "id": "elo_ratings",
            "label": "Elo Ratings",
            "configured": True,
            "reachable": True,
            "usable": bool(normalized),
            "worldcup_2026_found": False,
            "notes": (
                f"Three pages explored; JSON responses={json_count}; TSV responses={tsv_count}; rendered rows={len(rows)}; "
                f"normalized ratings={len(normalized)}."
            ),
        }
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("raw-html", "network", "rendered-table", "all"), required=True)
    args = parser.parse_args()
    client = EloRatingsClient()
    rows: list[dict[str, object]] = []
    normalized: list[dict[str, object]] = []
    try:
        if args.mode in ("raw-html", "all"):
            raw_html(client)
        if args.mode in ("network", "all"):
            network(client)
        if args.mode in ("rendered-table", "all"):
            rows, normalized = rendered_table(client)
        update_status(client, rows, normalized)
    except requests.RequestException as exc:
        raise SystemExit(f"Elo Ratings raw request failed: {exc}") from exc
    except Exception as exc:
        raise SystemExit(
            f"Elo Ratings exploration failed: {exc}. "
            "Install dependencies and Chromium with: python3 -m pip install -r backend/requirements.txt && "
            "python3 -m playwright install chromium"
        ) from exc


if __name__ == "__main__":
    main()
