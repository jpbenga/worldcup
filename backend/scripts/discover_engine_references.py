"""Inventory prediction-engine references in version-controlled source candidates."""

from __future__ import annotations

import json
import re
import subprocess
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
JSON_OUTPUT = PROJECT_ROOT / "backend" / "data" / "generated" / "engine_reference_inventory.json"
DOC_OUTPUT = PROJECT_ROOT / "docs" / "ENGINE_REFERENCE_INVENTORY.md"

TERMS = (
    "optuna",
    "Dixon-Coles",
    "Dixon",
    "Poisson",
    "bivariate",
    "sklearn",
    "scikit",
    "statsmodels",
    "penaltyblog",
    "xgboost",
    "lightgbm",
    "catboost",
    "scipy",
    "numpy",
    "pandas",
    "expected goals",
    "xG",
    "backtest",
    "calibration",
    "log loss",
    "Brier",
    "ranked probability score",
    "RPS",
    "negative log likelihood",
    "NLL",
    "train",
    "fit",
    "optimize",
    "objective",
    "attaque",
    "défense",
    "force",
    "forme",
    "historique",
    "Elo",
)
TERM_PATTERNS = {
    term: re.compile(rf"(?<![A-Za-z0-9_]){re.escape(term)}(?![A-Za-z0-9_])", re.IGNORECASE) for term in TERMS
}
ROOTS = ("backend/", "docs/", "handoff_worldcup_2026/")
TOP_LEVEL_FILES = {"README.md", "prototype_ia_coupe_du_monde_2026.md"}
EXCLUDED = {
    "backend/scripts/discover_engine_references.py",
    "backend/data/generated/engine_reference_inventory.json",
    "docs/ENGINE_REFERENCE_INVENTORY.md",
}


def tracked_files() -> list[Path]:
    output = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    paths = []
    for raw_path in output.splitlines():
        if raw_path in EXCLUDED or raw_path.startswith("backend/data/"):
            continue
        if raw_path in TOP_LEVEL_FILES or raw_path.startswith(ROOTS):
            paths.append(PROJECT_ROOT / raw_path)
    return sorted(paths)


def category_for(path: str, term: str, excerpt: str) -> str:
    lowered = f"{path} {term} {excerpt}".lower()
    if "requirements" in path or term.lower() in {
        "optuna",
        "scipy",
        "numpy",
        "pandas",
        "statsmodels",
        "sklearn",
        "scikit",
        "penaltyblog",
        "xgboost",
        "lightgbm",
        "catboost",
    }:
        return "dependency"
    if "backtest" in lowered:
        return "backtest"
    if term.lower() in {"log loss", "brier", "ranked probability score", "rps", "negative log likelihood", "nll"}:
        return "metric"
    if "data_acquisition" in path or "normaliz" in lowered or "historical_data" in path.lower():
        return "data"
    if path.endswith(".md"):
        return "documentation"
    return "model"


def inventory() -> list[dict[str, object]]:
    findings = []
    for path in tracked_files():
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        relative = path.relative_to(PROJECT_ROOT).as_posix()
        for line_number, line in enumerate(lines, start=1):
            excerpt = " ".join(line.strip().split())[:220]
            for term, pattern in TERM_PATTERNS.items():
                if pattern.search(line):
                    findings.append(
                        {
                            "file": relative,
                            "line": line_number,
                            "term": term,
                            "excerpt": excerpt,
                            "category": category_for(relative, term, excerpt),
                        }
                    )
    return findings


def render_markdown(findings: list[dict[str, object]]) -> str:
    categories = Counter(str(item["category"]) for item in findings)
    terms = Counter(str(item["term"]) for item in findings)
    files = len({str(item["file"]) for item in findings})
    lines = [
        "# Engine Reference Inventory",
        "",
        "## Scope",
        "",
        "Generated from tracked and untracked non-ignored files in `backend/`, `docs/`, `handoff_worldcup_2026/`,",
        "`README.md` and `prototype_ia_coupe_du_monde_2026.md`. Generated data, secrets",
        "and the inventory outputs themselves are excluded.",
        "",
        "## Summary",
        "",
        f"- Findings: `{len(findings)}`",
        f"- Files with findings: `{files}`",
        f"- Categories: `{dict(sorted(categories.items()))}`",
        f"- Most frequent terms: `{dict(terms.most_common(12))}`",
        "",
        "## Historical dependency candidates",
        "",
        "- Runtime backend acquisition: `beautifulsoup4`, `playwright`, `python-dotenv`, `requests`.",
        "- Testing: `pytest`.",
        "- Legacy optimizer candidates explicitly documented: `numpy`, `scipy`, `optuna`.",
        "- No tracked dependency file declares `pandas`, `statsmodels`, `scikit-learn`,",
        "  `penaltyblog`, `xgboost`, `lightgbm` or `catboost`.",
        "",
        "## Findings",
        "",
        "| File | Line | Term | Category | Short excerpt |",
        "|---|---:|---|---|---|",
    ]
    for item in findings:
        excerpt = str(item["excerpt"]).replace("|", "\\|").replace("`", "'")
        lines.append(
            f"| `{item['file']}` | {item['line']} | `{item['term']}` | {item['category']} | {excerpt} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The repository contains cleaned mathematical components and documentation about",
            "the former optimizer, but not a complete recoverable trained engine. References",
            "point to rolling attack/defence baselines, Elo modulation, Poisson/Dixon-Coles,",
            "chronological optimization and log loss. Historical parameters and a trustworthy",
            "training dataset were intentionally not retained.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    findings = inventory()
    JSON_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    JSON_OUTPUT.write_text(json.dumps(findings, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    DOC_OUTPUT.write_text(render_markdown(findings), encoding="utf-8")
    print(f"Inventoried {len(findings)} engine references across {len({item['file'] for item in findings})} files.")


if __name__ == "__main__":
    main()
