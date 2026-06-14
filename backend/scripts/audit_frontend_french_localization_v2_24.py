"""Audit the public French localization and V1 product polish."""

from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, utc_now, write_json


def publish(name: str, payload: dict) -> None:
    target = DATA_DIR / "generated" / name
    write_json(payload, target)
    shutil.copy2(target, DATA_DIR / "snapshots" / name)
    shutil.copy2(target, FRONTEND_DATA_DIR / name)


def main() -> None:
    app = ROOT / "frontend/src/app"
    public_files = [
        app / "pages/home/home.component.html",
        app / "pages/simulation/simulation.component.html",
        app / "components/match-modal/match-modal.component.html",
        app / "components/group-tabs/group-tabs.component.html",
    ]
    public_text = "\n".join(path.read_text() for path in public_files)
    routes = (app / "app.routes.ts").read_text()
    countries = (app / "i18n/country-names.fr.ts").read_text()
    markets = (app / "i18n/market-labels.fr.ts").read_text()
    styles = (ROOT / "frontend/src/styles.scss").read_text()
    groups = json.loads((ROOT / "frontend/src/assets/data/worldcup_groups.json").read_text())
    source_teams = sorted({team["name"] for group in groups for team in group["teams"]})
    missing_teams = [team for team in source_teams if not re.search(rf"(^|\n)\s*['\"]?{re.escape(team)}['\"]?:", countries)]
    forbidden = [
        token for token in (
            'routerLink="/transparence"', "Mode labo", "Matrice complète des scores",
            "Transparence et comparaison historique", "Draw No Bet", ">BTTS",
        ) if token in public_text
    ]
    payload = {
        "version": "v2.24",
        "generated_at": utc_now(),
        "scope": "public_frontend",
        "country_localization": {
            "source_team_count": len(source_teams),
            "dictionary_entries": countries.count("{ full:"),
            "missing_source_teams": missing_teams,
            "long_name_strategy": "team-name" in styles and "overflow-wrap" in styles,
        },
        "market_localization": {
            "market_dictionary_present": all(label in markets for label in ("Remboursé si nul", "Les deux équipes marquent", "Plus ou moins de 2,5 buts")),
            "french_decimal_odds": "toLocaleString('fr-FR'" in markets,
        },
        "product_polish": {
            "public_transparency_route_removed": "transparence" not in routes,
            "road_to_trophy_prominent": public_text.count("road-cta") >= 2,
            "lab_mode_removed": "Mode labo" not in public_text,
            "complete_matrix_claim_removed": "Matrice complète des scores" not in public_text,
        },
        "remaining_forbidden_public_strings": forbidden,
    }
    payload["verdict"] = "PASS" if not missing_teams and not forbidden and all(payload["product_polish"].values()) else "FAIL"
    publish("frontend_french_localization_audit_v2_24.json", payload)
    print(f"V2.24 French localization audit: {payload['verdict']}")


if __name__ == "__main__":
    main()
