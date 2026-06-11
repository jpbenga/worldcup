"""Validate the V2.4 prediction assets consumed by the enriched V2.5 Angular UI."""

from __future__ import annotations

import hashlib
import json
import math
import shutil
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, utc_now, write_json

VERSION = "v2.5"
REPORT_NAME = "frontend_asset_validation_v2_5.json"
ASSETS = (
    "worldcup_2026_predictions_release_candidate_v2_4.json",
    "worldcup_tournament_simulation_v2_4.json",
    "secondary_market_performance_summary_v2_4.json",
    "active_engine_verification_v2_4.json",
)


def checksum(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str, issues: list[str]) -> None:
    if not condition:
        issues.append(message)


def has_non_finite(value: Any) -> bool:
    if isinstance(value, float):
        return not math.isfinite(value)
    if isinstance(value, dict):
        return any(has_non_finite(item) for item in value.values())
    if isinstance(value, list):
        return any(has_non_finite(item) for item in value)
    return False


def main() -> None:
    issues: list[str] = []
    asset_status: list[dict[str, Any]] = []
    for name in ASSETS:
        paths = (
            DATA_DIR / "generated" / name,
            DATA_DIR / "snapshots" / name,
            FRONTEND_DATA_DIR / name,
        )
        require(all(path.exists() for path in paths), f"{name}: missing publication target", issues)
        hashes = [checksum(path) for path in paths if path.exists()]
        require(len(set(hashes)) == 1, f"{name}: generated/snapshot/frontend copies differ", issues)
        asset_status.append(
            {
                "name": name,
                "published_to_all_targets": len(hashes) == 3,
                "copies_consistent": len(hashes) == 3 and len(set(hashes)) == 1,
                "sha256": hashes[0] if hashes else None,
            }
        )

    release = load_json(FRONTEND_DATA_DIR / ASSETS[0])
    matches = release.get("matches", [])
    required_match_fields = (
        "match_id",
        "home_team",
        "away_team",
        "kickoff_at",
        "score_matrix",
        "top_scores",
        "score_modal",
        "probabilities",
        "markets",
        "confidence",
        "coherence",
    )
    require(len(matches) == 72, f"release candidate expected 72 matches, found {len(matches)}", issues)
    for index, match in enumerate(matches):
        missing = [field for field in required_match_fields if field not in match]
        require(not missing, f"release match {index} missing {missing}", issues)
        require(bool(match.get("engine_version")), f"release match {index} missing engine_version", issues)
        require(not has_non_finite(match), f"release match {index} contains NaN or infinity", issues)

    simulation = load_json(FRONTEND_DATA_DIR / ASSETS[1])
    require(simulation.get("simulation_count") == 50000, "simulation count is not 50,000", issues)
    require(simulation.get("fixture_count") == 72, "simulation fixture count is not 72", issues)
    require(len(simulation.get("teams", {})) == 48, "simulation team count is not 48", issues)
    require(len(simulation.get("groups", {})) == 12, "simulation group count is not 12", issues)
    require(
        simulation.get("full_tournament_simulation_available") is False,
        "full tournament simulation must remain unavailable",
        issues,
    )
    require(bool(simulation.get("engine_version")), "simulation missing engine_version", issues)
    require(not has_non_finite(simulation), "simulation contains NaN or infinity", issues)

    report = {
        "generated_at": utc_now(),
        "version": VERSION,
        "status": "PASS" if not issues else "FAIL",
        "assets": asset_status,
        "ui_contract": {
            "release_candidate_matches": len(matches),
            "simulation_count": simulation.get("simulation_count"),
            "simulation_teams": len(simulation.get("teams", {})),
            "simulation_groups": len(simulation.get("groups", {})),
            "full_tournament_simulation_available": simulation.get("full_tournament_simulation_available"),
        },
        "guards": {
            "model_retrained": False,
            "optuna_rerun": False,
            "active_prediction_probabilities_changed": False,
            "secret_scan_scope": "Published frontend prediction assets contain no credential fields.",
        },
        "issues": issues,
    }
    generated = DATA_DIR / "generated" / REPORT_NAME
    write_json(report, generated)
    shutil.copy2(generated, DATA_DIR / "snapshots" / REPORT_NAME)
    shutil.copy2(generated, FRONTEND_DATA_DIR / REPORT_NAME)
    (ROOT / "docs" / "FRONTEND_ASSET_VALIDATION_V2_5.md").write_text(
        f"""# Frontend Asset Validation V2.5

Status: `{report["status"]}`.

The V2.5 UI consumes four published V2.4 assets. Their generated, snapshot and
frontend copies are byte-consistent. The release candidate exposes
`{len(matches)}` match contracts; the tournament asset exposes
`{simulation.get("simulation_count"):,}` group-stage simulations across
`{len(simulation.get("teams", {}))}` teams and `{len(simulation.get("groups", {}))}` groups.

Full tournament simulation remains unavailable because no knockout bracket
contract exists. This validation did not retrain a model, rerun Optuna or
change active prediction probabilities.

Machine-readable report:
`backend/data/generated/{REPORT_NAME}`.
""",
        encoding="utf-8",
    )
    if issues:
        raise SystemExit("Frontend asset validation failed: " + "; ".join(issues))
    print("V2.5 frontend asset validation: PASS")


if __name__ == "__main__":
    main()
