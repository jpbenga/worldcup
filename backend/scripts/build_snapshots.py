"""Run the local pipeline with a mock or API-Football active fixture source."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import audit_prediction_diversity
import build_worldcup_views
import compare_prediction_models
import generate_predictions
import normalize_matches
import run_backtest
from pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, MODEL_VERSION, PROJECT_ROOT, load_json, utc_now, write_json

ENGINE = generate_predictions.ENGINE


def build_data_sources(updated_at: str, source: str, matches: list[dict[str, object]]) -> dict[str, object]:
    is_api = source == "api_football"
    is_future = bool(matches) and all(bool(match.get("is_future_fixture")) for match in matches)
    return {
        "version": MODEL_VERSION,
        "updated_at": updated_at,
        "active_source": source,
        "is_real_data": is_api,
        "is_future_fixture_set": is_future,
        "backtesting_status": "not_evaluable_future_fixtures" if is_api and is_future else "available_mock_results",
        "engine": ENGINE,
        "sources": [
            {
                "id": "active_matches",
                "label": "Active World Cup fixtures" if is_api else "Sample matches",
                "source_type": "api_football" if is_api else "mock",
                "source_name": "api_football_worldcup_2026" if is_api else "local_sample_file",
                "is_real_data": is_api,
                "path": "backend/data/normalized/matches.json",
                "description": (
                    "Fixtures réelles et futures API-Football Coupe du Monde 2026."
                    if is_api
                    else "Données de démonstration utilisées pour tester le pipeline."
                ),
            },
            {
                "id": "predictions",
                "label": "Prototype predictions",
                "source_type": "generated",
                "source_name": "prototype_prediction_engine",
                "is_real_data": False,
                "path": "backend/data/generated/predictions.json",
                "description": "Prédictions générées par un moteur prototype non calibré historiquement.",
            },
            {
                "id": "backtest_results",
                "label": "Backtest results",
                "source_type": "evaluated",
                "source_name": "sample_backtest_pipeline" if not is_api else "not_evaluable_future_fixtures",
                "is_real_data": False,
                "path": "backend/data/evaluated/backtest_results.json",
                "description": (
                    "Non disponible pour les fixtures réelles futures."
                    if is_api and is_future
                    else "Backtests de démonstration sur les prédictions baseline mock."
                ),
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


def activate_source(source: str) -> list[dict[str, object]]:
    if source == "mock":
        normalize_matches.main()
    else:
        api_matches = DATA_DIR / "normalized" / "api_football_matches.json"
        if not api_matches.exists():
            raise SystemExit(
                "API-Football normalized fixtures are missing. Run:\n"
                "python3 backend/scripts/fetch_worldcup_api_football.py --season 2026\n"
                "python3 backend/scripts/normalize_api_football_worldcup.py"
            )
        shutil.copy2(api_matches, DATA_DIR / "normalized" / "matches.json")
        print(f"Activated API-Football fixtures from {api_matches.relative_to(PROJECT_ROOT)}")
    return load_json(DATA_DIR / "normalized" / "matches.json")


def write_not_evaluable_backtest(matches: list[dict[str, object]]) -> None:
    write_json(
        {
            "status": "not_evaluable",
            "reason": "Future API-Football fixtures have no real results available for backtesting.",
            "fixture_count": len(matches),
            "summary": {"tested": 0, "won": 0, "hit_rate": None, "by_market": {}, "details": []},
            "results": [],
        },
        DATA_DIR / "evaluated" / "backtest_results.json",
    )
    print("Backtesting status: not_evaluable (future API-Football fixtures).")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", choices=("mock", "api_football"), default="api_football")
    parser.add_argument("--model", choices=("baseline", "elo", "both"), default="both")
    args = parser.parse_args(argv)

    matches = activate_source(args.source)
    generate_predictions.generate_models(args.model)
    if args.source == "api_football":
        write_not_evaluable_backtest(matches)
    elif args.model in {"baseline", "both"}:
        run_backtest.main()
    if args.model == "both":
        compare_prediction_models.main()
        if args.source == "api_football":
            audit_prediction_diversity.main()
    if args.source == "api_football":
        build_worldcup_views.main()

    data_sources = build_data_sources(utc_now(), args.source, matches)
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
    for optional in (
        "data_acquisition_status.json",
        "team_mapping_status.json",
        "teams.json",
        "worldcup_groups.json",
        "group_strengths.json",
        "prediction_diversity_audit.json",
    ):
        optional_path = DATA_DIR / "snapshots" / optional
        if optional_path.exists():
            snapshot_sources[optional] = optional_path
    for filename, source_path in snapshot_sources.items():
        publish_snapshot(filename, source_path)
    print(f"Published {len(snapshot_sources)} snapshots to backend/data/snapshots")
    print(f"Copied snapshots to {FRONTEND_DATA_DIR.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
