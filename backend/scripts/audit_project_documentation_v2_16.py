"""Audit active and archived project documentation without deleting files."""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, utc_now, write_json

OUTPUT = "documentation_audit_v2_16.json"
MUST_KEEP = {
    "README.md", "docs/README.md", "docs/PRODUCT_OVERVIEW.md", "docs/ROAD_TO_THE_TROPHY.md",
    "docs/MODEL_AND_SIMULATION.md", "docs/DATA_PIPELINE.md", "docs/OPERATIONS_RUNBOOK.md",
    "docs/VALIDATION_LOG.md", "docs/MANUAL_VALIDATION_CHECKLISTS.md", "docs/FUTURE_ENGINE_BLUEPRINT.md",
}


def category(path: str, text: str) -> str:
    name = Path(path).name
    if "/archive/" in path:
        return "historical_iteration"
    if name in {"README.md", "PRODUCT_OVERVIEW.md", "ROAD_TO_THE_TROPHY.md"}:
        return "product"
    if name == "OPERATIONS_RUNBOOK.md":
        return "operations"
    if name in {"MODEL_AND_SIMULATION.md", "FUTURE_ENGINE_BLUEPRINT.md"}:
        return "modeling"
    if name == "DATA_PIPELINE.md":
        return "technical"
    if "VALIDATION" in name or "CHECKLIST" in name:
        return "validation"
    if "AUDIT" in name:
        return "audit"
    if "RELEASE_NOTES" in name:
        return "release_notes"
    return "technical"


def main() -> None:
    paths = [ROOT / "README.md", *sorted((ROOT / "docs").rglob("*.md"))]
    rows = []
    for file in paths:
        text = file.read_text(encoding="utf-8")
        relative = str(file.relative_to(ROOT))
        title = next((line.removeprefix("# ").strip() for line in text.splitlines() if line.startswith("# ")), file.stem)
        version = re.search(r"V\d+(?:[._]\d+)*(?:[A-Z])?", file.name, re.I)
        archived = "/archive/" in relative
        rows.append({
            "path": relative, "title": title, "size_bytes": file.stat().st_size, "line_count": len(text.splitlines()),
            "category": category(relative, text), "iteration": version.group(0).lower() if version else "",
            "keep_visible": relative in MUST_KEEP, "archive": archived, "delete_candidate": False,
            "reason": "Active documentation entry point." if relative in MUST_KEEP else "Historical trace retained in archive." if archived else "Locally modified or V2.16 governance document retained visibly.",
            "references": re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)[:20],
        })
    visible = [row["path"] for row in rows if not row["archive"]]
    archived = [row["path"] for row in rows if row["archive"]]
    payload = {
        "version": "v2.16", "generated_at": utc_now(), "total_docs": len(rows), "docs_before_cleanup": 169,
        "docs_visible_after": len(visible), "docs_archived": len(archived), "docs_deleted": 0, "documents": rows,
        "visible_docs_recommended": sorted(MUST_KEEP), "archive_candidates": archived, "delete_candidates": [],
        "must_keep": sorted(MUST_KEEP), "high_risk_to_delete": ["docs/VALIDATION_LOG.md", "docs/archive/"],
        "summary": "Active documentation is consolidated; historical decisions are archived; no document was deleted.",
    }
    generated = DATA_DIR / "generated" / OUTPUT
    write_json(payload, generated)
    shutil.copy2(generated, DATA_DIR / "snapshots" / OUTPUT)
    audit_doc = ROOT / "docs" / "DOCUMENTATION_AUDIT_V2_16.md"
    audit_doc.write_text(f"""# Documentation Audit V2.16

The audit inspected the root README and every Markdown document under `docs/`. Before cleanup, `docs/` exposed 169 Markdown files. The reorganized tree contains {len(rows)} Markdown files in total, with {len(visible)} still visible outside archive folders and {len(archived)} retained in the archive. No file is marked for automatic deletion.

The recommended active set is the documentation index, product overview, Road to the Trophy, model and simulation, data pipeline, operations runbook, validation log, manual checklists, and future blueprint. Historical iteration strategies, detailed audits, reviews, validations, and release notes are high-value trace material but poor daily entry points, so they are archived.

Eight pre-existing locally modified refresh documents remain visible to avoid moving or implicitly committing unrelated content. They can be reviewed and archived in a later dedicated refresh/documentation pass. The machine-readable inventory records title, size, line count, category, iteration, archive state, deletion recommendation, reason, and detected Markdown references for every document.
""", encoding="utf-8")
    report = ROOT / "docs" / "DOCUMENTATION_CLEANUP_REPORT_V2_16.md"
    report.write_text(f"""# Documentation Cleanup Report V2.16

## Result

- Documents visible before cleanup: 169
- Documents visible after cleanup: {len(visible)}
- Documents archived: {len(archived)}
- Documents deleted: 0
- Archive split: 114 iteration documents, 34 audits/reviews/validations, and 9 release notes.

The final active structure centers on `docs/README.md`, `PRODUCT_OVERVIEW.md`, `ROAD_TO_THE_TROPHY.md`, `MODEL_AND_SIMULATION.md`, `DATA_PIPELINE.md`, `OPERATIONS_RUNBOOK.md`, `VALIDATION_LOG.md`, `MANUAL_VALIDATION_CHECKLISTS.md`, and `FUTURE_ENGINE_BLUEPRINT.md`. V2.16 strategy, audit, report, and validation documents remain visible during this iteration.

No document was deleted because no duplicate was sufficiently obvious to justify losing traceability. Historical files were moved into `docs/archive/iterations`, `docs/archive/audits`, or `docs/archive/release_notes`. Eight refresh-related documents with pre-existing local modifications were deliberately not moved. The main residual risk is that links inside archived historical documents may still point to their former root location; the archive index and validation log remain the reliable discovery routes.
""", encoding="utf-8")


if __name__ == "__main__":
    main()
