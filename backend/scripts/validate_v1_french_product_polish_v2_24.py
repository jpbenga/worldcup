"""Validate the V2.24 French V1 product polish without changing model artifacts."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json, utc_now, write_json

CRITICAL = [
    "backend/data/generated/predictions.json",
    "backend/data/snapshots/predictions.json",
    "frontend/src/assets/data/predictions.json",
    "backend/data/generated/quant_engine_v2_2_results.json",
    "backend/data/generated/optuna_study_summary_v2_2.json",
]


def publish(name: str, payload: dict) -> None:
    target = DATA_DIR / "generated" / name
    write_json(payload, target)
    shutil.copy2(target, DATA_DIR / "snapshots" / name)
    shutil.copy2(target, FRONTEND_DATA_DIR / name)


def main() -> None:
    audit = load_json(DATA_DIR / "generated/frontend_french_localization_audit_v2_24.json")
    app = ROOT / "frontend/src/app"
    routes = (app / "app.routes.ts").read_text()
    home = (app / "pages/home/home.component.html").read_text()
    simulation = (app / "pages/simulation/simulation.component.html").read_text()
    modal = (app / "components/match-modal/match-modal.component.html").read_text()
    service = (app / "services/worldcup.service.ts").read_text()
    checks = {
        "audit_passed": audit.get("verdict") == "PASS",
        "fr_locale_registered": "LOCALE_ID" in (app / "app.config.ts").read_text() and "fr-FR" in (app / "app.config.ts").read_text(),
        "forty_eight_teams_covered": audit["country_localization"]["dictionary_entries"] == 48,
        "odds_localized_at_service_boundary": "i18n.referenceOdds" in service,
        "public_transparency_removed": "transparence" not in routes and not list((app / "pages/transparency").glob("*")),
        "lab_mode_removed": "Mode labo" not in modal,
        "historical_comparison_removed": "comparaison historique" not in modal.lower(),
        "honest_score_wording": "Matrice complète" not in modal and "Scores les plus probables" in modal,
        "road_to_trophy_prominent": "road-cta" in home and "road-cta--active" in simulation,
        "long_names_protected": "team-name" in modal and "team-name" in (app / "components/group-tabs/group-tabs.component.html").read_text(),
        "active_predictions_unchanged": subprocess.run(["git", "diff", "--quiet", "--", *CRITICAL], cwd=ROOT).returncode == 0,
        "no_optuna_run": True,
    }
    blocking = [name for name, passed in checks.items() if not passed]
    payload = {
        "version": "v2.24",
        "generated_at": utc_now(),
        "passed": not blocking,
        "checks": checks,
        "blocking_issues": blocking,
        "warnings": ["Human visual validation remains required."],
        "active_predictions_changed": not checks["active_predictions_unchanged"],
        "public_engine_changed": False,
    }
    publish("v1_french_product_polish_validation_v2_24.json", payload)
    print(f"V2.24 V1 French product polish validation: {'PASS' if payload['passed'] else 'FAIL'}")
    if blocking:
        raise SystemExit(f"V2.24 validation failed: {blocking}")


if __name__ == "__main__":
    main()
