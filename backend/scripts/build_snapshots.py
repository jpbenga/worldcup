"""Run the complete local pipeline and publish frontend-ready snapshots."""

from __future__ import annotations

import shutil

import generate_predictions
import normalize_matches
import run_backtest
from pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, MODEL_VERSION, PROJECT_ROOT, utc_now, write_json


def build_data_sources(updated_at: str) -> dict[str, object]:
    return {
        "version": MODEL_VERSION,
        "updated_at": updated_at,
        "sources": [
            {
                "id": "sample_matches",
                "label": "Sample matches",
                "source_type": "mock",
                "source_name": "local_sample_file",
                "is_real_data": False,
                "path": "backend/data/mock/sample_matches.json",
                "description": "Données de démonstration utilisées pour tester le pipeline.",
            },
            {
                "id": "normalized_matches",
                "label": "Normalized matches",
                "source_type": "normalized",
                "source_name": "local_normalizer",
                "is_real_data": False,
                "path": "backend/data/normalized/matches.json",
                "description": "Matchs mock convertis au format interne de l’application.",
            },
            {
                "id": "predictions",
                "label": "Generated predictions",
                "source_type": "generated",
                "source_name": "backend_prediction_pipeline",
                "is_real_data": False,
                "path": "backend/data/generated/predictions.json",
                "description": "Prédictions générées à partir des matchs normalisés mock.",
            },
            {
                "id": "backtest_results",
                "label": "Backtest results",
                "source_type": "evaluated",
                "source_name": "sample_backtest_pipeline",
                "is_real_data": False,
                "path": "backend/data/evaluated/backtest_results.json",
                "description": "Backtests de démonstration sur les prédictions mock.",
            },
        ],
    }


def main() -> None:
    normalize_matches.main()
    generate_predictions.main()
    run_backtest.main()

    data_sources = build_data_sources(utc_now())
    write_json(data_sources, DATA_DIR / "data_sources.json")

    snapshot_sources = {
        "matches.json": DATA_DIR / "normalized" / "matches.json",
        "predictions.json": DATA_DIR / "generated" / "predictions.json",
        "backtest_results.json": DATA_DIR / "evaluated" / "backtest_results.json",
        "data_sources.json": DATA_DIR / "data_sources.json",
    }
    acquisition_status = DATA_DIR / "snapshots" / "data_acquisition_status.json"
    if acquisition_status.exists():
        snapshot_sources["data_acquisition_status.json"] = acquisition_status
    mapping_status = DATA_DIR / "snapshots" / "team_mapping_status.json"
    if mapping_status.exists():
        snapshot_sources["team_mapping_status.json"] = mapping_status
    snapshots_dir = DATA_DIR / "snapshots"
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    FRONTEND_DATA_DIR.mkdir(parents=True, exist_ok=True)
    for filename, source in snapshot_sources.items():
        snapshot_target = snapshots_dir / filename
        if source.resolve() != snapshot_target.resolve():
            shutil.copy2(source, snapshot_target)
        shutil.copy2(source, FRONTEND_DATA_DIR / filename)

    print(f"Published {len(snapshot_sources)} snapshots to {snapshots_dir.relative_to(PROJECT_ROOT)}")
    print(f"Copied snapshots to {FRONTEND_DATA_DIR.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
