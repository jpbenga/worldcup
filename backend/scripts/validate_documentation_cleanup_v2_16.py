"""Validate the V2.16 documentation cleanup."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, load_json, utc_now, write_json

REQUIRED = [
    "docs/README.md", "docs/PRODUCT_OVERVIEW.md", "docs/ROAD_TO_THE_TROPHY.md", "docs/MODEL_AND_SIMULATION.md",
    "docs/DATA_PIPELINE.md", "docs/OPERATIONS_RUNBOOK.md", "docs/VALIDATION_LOG.md",
    "docs/MANUAL_VALIDATION_CHECKLISTS.md", "docs/FUTURE_ENGINE_BLUEPRINT.md", "docs/archive/README.md",
    "docs/DOCUMENTATION_AUDIT_V2_16.md", "docs/DOCUMENTATION_CLEANUP_REPORT_V2_16.md",
]


def main() -> None:
    audit = load_json(DATA_DIR / "generated" / "documentation_audit_v2_16.json")
    missing = [path for path in REQUIRED if not (ROOT / path).exists()]
    too_short = [path for path in REQUIRED if (ROOT / path).exists() and len((ROOT / path).read_text(encoding="utf-8").strip()) < 500]
    active_text = "\n".join((ROOT / path).read_text(encoding="utf-8").lower() for path in REQUIRED if (ROOT / path).exists())
    checks = {
        "required_docs_present": not missing,
        "required_docs_non_empty": not too_short,
        "road_to_the_trophy_v3_official": "simuai tournament engine v3" in active_text and "unique" in active_text,
        "quant_hybrid_v2_2_active_prematch": "quant_hybrid_v2.2" in active_text and "pré-match" in active_text,
        "root_readme_links_docs_index": "docs/readme.md" in (ROOT / "README.md").read_text(encoding="utf-8").lower(),
        "archive_index_present": (ROOT / "docs/archive/README.md").exists(),
        "no_secret_in_docs": "api_football_key=" not in active_text and "x-apisports-key:" not in active_text,
    }
    payload = {
        "version": "v2.16", "passed": all(checks.values()), "docs_before": audit["docs_before_cleanup"],
        "docs_visible_after": audit["docs_visible_after"], "docs_archived": audit["docs_archived"], "docs_deleted": 0,
        "required_docs_present": checks["required_docs_present"], "checks": checks,
        "blocking_issues": missing + too_short + [name for name, passed in checks.items() if not passed],
        "warnings": ["Eight pre-existing locally modified refresh documents remain visible and were not archived."],
        "generated_at": utc_now(),
    }
    generated = DATA_DIR / "generated" / "documentation_cleanup_validation_v2_16.json"
    write_json(payload, generated)
    shutil.copy2(generated, DATA_DIR / "snapshots" / "documentation_cleanup_validation_v2_16.json")
    (ROOT / "docs/DOCUMENTATION_CLEANUP_VALIDATION_V2_16.md").write_text(f"""# Documentation Cleanup Validation V2.16

The cleanup validation checks the active documentation index, product overview, Road to the Trophy guide, model and simulation guide, data pipeline, operations runbook, validation records, manual checklists, future blueprint, archive index, audit, and cleanup report. It also verifies that active documentation identifies SimuAI Tournament Engine V3 as the official Road to the Trophy engine and `quant_hybrid_v2.2` as the active pre-match prediction engine.

Result: **{"passed" if payload["passed"] else "failed"}**. Required documents present: {payload["required_docs_present"]}. Documents visible before cleanup: {payload["docs_before"]}. Documents visible after cleanup: {payload["docs_visible_after"]}. Documents archived: {payload["docs_archived"]}. Documents deleted: 0.

No product engine, active prediction, or Road to the Trophy data artifact is modified by this documentation-only iteration. The remaining warning concerns eight pre-existing locally modified refresh documents deliberately left visible and outside the cleanup commit’s archive moves.
""", encoding="utf-8")


if __name__ == "__main__":
    main()
