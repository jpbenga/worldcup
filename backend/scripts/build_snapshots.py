"""Run the local pipeline and publish baseline or experimental model snapshots."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import compare_prediction_models
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
                "description": "Prédictions baseline générées à partir des matchs normalisés mock.",
            },
            {
                "id": "backtest_results",
                "label": "Backtest results",
                "source_type": "evaluated",
                "source_name": "sample_backtest_pipeline",
                "is_real_data": False,
                "path": "backend/data/evaluated/backtest_results.json",
                "description": "Backtests de démonstration sur les prédictions baseline mock.",
            },
        ],
    }


def publish_snapshot(filename: str, source_path: Path) -> None:
    snapshots_dir = DATA_DIR / "snapshots"
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    FRONTEND_DATA_DIR.mkdir(parents=True, exist_ok=True)
    snapshot_target = snapshots_dir / filename
    if source_path.resolve() != snapshot_target.resolve():
        shutil.copy2(source_path, snapshot_target)
    shutil.copy2(source_path, FRONTEND_DATA_DIR / filename)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=("baseline", "elo", "both"), default="baseline")
    args = parser.parse_args(argv)

    normalize_matches.main()
    generate_predictions.generate_models(args.model)
    if args.model in {"baseline", "both"}:
        run_backtest.main()
    if args.model == "both":
        compare_prediction_models.main()

    data_sources = build_data_sources(utc_now())
    write_json(data_sources, DATA_DIR / "data_sources.json")
    snapshot_sources = {
        "matches.json": DATA_DIR / "normalized" / "matches.json",
        "predictions.json": DATA_DIR / "generated" / "predictions.json",
        "backtest_results.json": DATA_DIR / "evaluated" / "backtest_results.json",
        "data_sources.json": DATA_DIR / "data_sources.json",
    }
    if args.model in {"baseline", "both"}:
        snapshot_sources["predictions_baseline.json"] = DATA_DIR / "generated" / "predictions_baseline.json"
    if args.model in {"elo", "both"}:
        snapshot_sources["predictions_elo.json"] = DATA_DIR / "generated" / "predictions_elo.json"
    if args.model == "both":
        snapshot_sources["model_comparison.json"] = DATA_DIR / "generated" / "model_comparison.json"
    for optional in ("data_acquisition_status.json", "team_mapping_status.json"):
        source = DATA_DIR / "snapshots" / optional
        if source.exists():
            snapshot_sources[optional] = source

    for filename, source in snapshot_sources.items():
        publish_snapshot(filename, source)
    print(f"Published {len(snapshot_sources)} snapshots to backend/data/snapshots")
    print(f"Copied snapshots to {FRONTEND_DATA_DIR.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
