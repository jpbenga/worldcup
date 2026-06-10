"""Minimal Elo Ratings exploration via raw HTML, network capture, and rendered DOM."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import Page, Response, sync_playwright

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_ROOT = PROJECT_ROOT / "backend" / "data" / "raw" / "elo"
DISCOVERY_ROOT = RAW_ROOT / "discovery"
SAMPLES_ROOT = RAW_ROOT / "samples"
NORMALIZED_PATH = PROJECT_ROOT / "backend" / "data" / "normalized" / "team_ratings.json"

TARGETS = {
    "home": "https://www.eloratings.net/",
    "worldcup_2026": "https://www.eloratings.net/2026_World_Cup",
    "latest": "https://www.eloratings.net/latest",
}
KEYWORDS = ("rating", "rank", "team", "country", "data", "json", "elo")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_text(path: Path, value: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")
    return path


def write_json(path: Path, value: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def repair_mojibake(value: str) -> str:
    if "Ã" not in value and "â" not in value:
        return value
    try:
        return value.encode("latin-1").decode("utf-8")
    except UnicodeError:
        return value


class EloRatingsClient:
    def __init__(self, timeout_seconds: int = 25) -> None:
        self.timeout_seconds = timeout_seconds
        self.user_agent = "worldcup-data-spike/0.3.1"

    def fetch_raw_pages(self) -> dict[str, dict[str, Any]]:
        summary: dict[str, dict[str, Any]] = {}
        for name, url in TARGETS.items():
            response = requests.get(url, headers={"User-Agent": self.user_agent}, timeout=self.timeout_seconds)
            response.raise_for_status()
            html = response.text
            soup = BeautifulSoup(html, "html.parser")
            scripts = [str(tag.get("src")) for tag in soup.find_all("script") if tag.get("src")]
            urls = sorted(set(re.findall(r"https?://[^\s\"'<>]+", html)))
            summary[name] = {
                "url": url,
                "final_url": response.url,
                "status": response.status_code,
                "size": len(response.content),
                "scripts": scripts,
                "absolute_urls": urls,
                "keyword_counts": {keyword: html.lower().count(keyword) for keyword in KEYWORDS},
            }
            write_text(DISCOVERY_ROOT / f"{name}_raw.html", html)
        write_json(DISCOVERY_ROOT / "raw_html_summary.json", summary)
        return summary

    def capture_network(self) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        json_root = DISCOVERY_ROOT / "network_json_responses"
        data_root = DISCOVERY_ROOT / "network_data_responses"
        json_root.mkdir(parents=True, exist_ok=True)
        data_root.mkdir(parents=True, exist_ok=True)

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            for name, url in TARGETS.items():
                page = browser.new_page(user_agent=self.user_agent)
                page.on(
                    "response",
                    lambda response, target=name: self._record_response(response, target, records, json_root, data_root),
                )
                self._load_page(page, url)
                page.close()
            browser.close()

        write_json(DISCOVERY_ROOT / "network_requests.json", records)
        return records

    def capture_rendered_tables(self) -> list[dict[str, Any]]:
        all_rows: list[dict[str, Any]] = []
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            for name, url in TARGETS.items():
                page = browser.new_page(user_agent=self.user_agent)
                self._load_page(page, url)
                html = page.content()
                visible_text = page.locator("body").inner_text()
                write_text(DISCOVERY_ROOT / f"{name}_rendered.html", html)
                rows = self._parse_rendered_rows(html, visible_text, url)
                if name == "home":
                    all_rows = rows
                page.close()
            browser.close()

        write_json(SAMPLES_ROOT / "elo_rankings_rendered_table.json", all_rows)
        return all_rows

    def normalize_rankings(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not self.rankings_are_reliable(rows):
            write_json(NORMALIZED_PATH, [])
            return []
        retrieved_at = utc_now()
        normalized = [
            {
                "team_name": row["team_name"],
                "country_code": None,
                "elo_rating": row["elo_rating"],
                "rank": row["rank"],
                "source_type": "elo",
                "source_name": "eloratings.net",
                "source_url": TARGETS["home"],
                "retrieved_at": retrieved_at,
            }
            for row in sorted(rows, key=lambda item: item["rank"])
        ]
        write_json(NORMALIZED_PATH, normalized)
        return normalized

    def parse_world_tsv(self) -> list[dict[str, Any]]:
        records_path = DISCOVERY_ROOT / "network_requests.json"
        if not records_path.exists():
            return []
        records = json.loads(records_path.read_text(encoding="utf-8"))
        world_record = next(
            (
                item
                for item in records
                if item.get("target") == "home"
                and urlparse(item.get("url", "")).path.endswith("/World.tsv")
                and item.get("local_file")
            ),
            None,
        )
        names_record = next(
            (
                item
                for item in records
                if item.get("target") == "home"
                and urlparse(item.get("url", "")).path.endswith("/en.teams.tsv")
                and item.get("local_file")
            ),
            None,
        )
        if world_record is None or names_record is None:
            return []
        names_path = DISCOVERY_ROOT / names_record["local_file"]
        names = {
            row[0]: repair_mojibake(row[1])
            for row in csv.reader(io.StringIO(names_path.read_text(encoding="utf-8")), delimiter="\t")
            if len(row) >= 2
        }
        path = DISCOVERY_ROOT / world_record["local_file"]
        rows = list(csv.reader(io.StringIO(path.read_text(encoding="utf-8")), delimiter="\t"))
        parsed: list[dict[str, Any]] = []
        for row in rows:
            if len(row) < 4 or not row[0].isdigit() or not row[3].isdigit() or row[2] not in names:
                continue
            parsed.append(
                {
                    "rank": int(row[0]),
                    "team_name": names[row[2]].strip(),
                    "elo_rating": int(row[3]),
                    "raw_text": " | ".join(row),
                    "source_url": TARGETS["home"],
                }
            )
        return parsed

    def rankings_are_reliable(self, rows: list[dict[str, Any]]) -> bool:
        unique_teams = {row["team_name"] for row in rows}
        ranks = [row["rank"] for row in rows]
        ratings = [row["elo_rating"] for row in rows]
        return (
            len(rows) >= 200
            and len(unique_teams) == len(rows)
            and min(ranks) == 1
            and ranks == sorted(ranks)
            and all(300 <= rating <= 2500 for rating in ratings)
        )

    def _load_page(self, page: Page, url: str) -> None:
        page.goto(url, wait_until="domcontentloaded", timeout=self.timeout_seconds * 1000)
        try:
            page.wait_for_load_state("networkidle", timeout=10_000)
        except Exception:
            pass
        page.wait_for_timeout(2_000)

    def _record_response(
        self,
        response: Response,
        target: str,
        records: list[dict[str, Any]],
        json_root: Path,
        data_root: Path,
    ) -> None:
        content_type = response.headers.get("content-type", "")
        record: dict[str, Any] = {
            "target": target,
            "url": response.url,
            "method": response.request.method,
            "status": response.status,
            "content_type": content_type,
            "size": None,
            "local_file": None,
        }
        try:
            body = response.body()
            record["size"] = len(body)
            if "json" in content_type.lower():
                payload = json.loads(body.decode("utf-8"))
                digest = hashlib.sha256(response.url.encode("utf-8")).hexdigest()[:12]
                filename = f"{target}_{digest}.json"
                write_json(json_root / filename, payload)
                record["local_file"] = f"network_json_responses/{filename}"
            elif "tab-separated-values" in content_type.lower():
                basename = Path(urlparse(response.url).path).name or "response.tsv"
                filename = f"{target}_{basename}"
                write_text(data_root / filename, body.decode("utf-8"))
                record["local_file"] = f"network_data_responses/{filename}"
        except Exception as exc:
            record["capture_error"] = str(exc)
        records.append(record)

    def _parse_rendered_rows(self, html: str, visible_text: str, source_url: str) -> list[dict[str, Any]]:
        soup = BeautifulSoup(html, "html.parser")
        candidates: list[list[str]] = []
        for selector in ("tr", ".slick-row"):
            for element in soup.select(selector):
                cells = [cell.get_text(" ", strip=True) for cell in element.select("td, th, .slick-cell")]
                if cells:
                    candidates.append(cells)
        if not candidates:
            candidates = [line.split() for line in visible_text.splitlines() if line.strip()]

        rows: list[dict[str, Any]] = []
        seen: set[tuple[int, str]] = set()
        for cells in candidates:
            parsed = self._parse_cells(cells)
            if parsed is None:
                continue
            key = (parsed["rank"], parsed["team_name"])
            if key in seen:
                continue
            seen.add(key)
            parsed["raw_text"] = " | ".join(cells)
            parsed["source_url"] = source_url
            rows.append(parsed)
        return sorted(rows, key=lambda item: item["rank"])

    def _parse_cells(self, cells: list[str]) -> dict[str, Any] | None:
        values = [value.strip() for value in cells if value.strip()]
        if len(values) < 3 or not values[0].isdigit() or not values[2].isdigit():
            return None
        rank = int(values[0])
        rating = int(values[2])
        team_name = values[1]
        if not 1 <= rank <= 300 or not 300 <= rating <= 2500 or not re.search(r"[A-Za-zÀ-ÿ]", team_name):
            return None
        return {"rank": rank, "team_name": team_name, "elo_rating": rating}
