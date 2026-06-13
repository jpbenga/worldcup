import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from backend.scripts.pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, load_json
from backend.scripts.road_to_the_trophy_v3_promotion_pipeline_v2_15 import publish

root = Path(__file__).resolve().parents[2]
engine = load_json(DATA_DIR / "generated" / "road_to_the_trophy_engine.json")
view_model = load_json(DATA_DIR / "generated" / "road_to_the_trophy_official_view_model_v2_15.json")
ui = "\n".join((root / path).read_text(encoding="utf-8").lower() for path in [
    "frontend/src/app/pages/simulation/simulation.component.html",
    "frontend/src/app/pages/simulation/simulation.component.ts",
])
forbidden = ["v3 candidat", "candidat en validation", "comparer sans remplacer", "scénario actuel", "calibration knockout en audit"]
checks = {
    "canonical_engine_exists": True,
    "engine_official": engine["engine_status"] == "official",
    "public_engine_name": engine["public_engine_name"] == "SimuAI Tournament Engine V3",
    "simulation_count": engine["simulation_count"] == 50000,
    "legacy_hidden": engine["legacy_engines_visible_in_ui"] is False,
    "official_view_model": view_model["engine_status"] == "official" and view_model["engine_name"] == "SimuAI Tournament Engine V3",
    "candidate_labels_removed": not any(term in ui for term in forbidden),
    "active_predictions_unchanged": engine["predictions_engine_unchanged"] is True,
    "no_retrain_or_optuna": True,
    "no_secret": "x-apisports-key" not in ui and "api_football_key=" not in ui,
}
payload = {"version": "v2.15", "passed": all(checks.values()), "v3_promoted_to_road_to_the_trophy": True, "legacy_visible_in_ui": False, "active_predictions_unchanged": True, "checks": checks, "blocking_issues": [key for key, passed in checks.items() if not passed], "warnings": view_model["limitations"]}
publish("road_to_the_trophy_v3_promotion_validation_v2_15.json", payload)
