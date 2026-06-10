"""Compare baseline and experimental Elo-adjusted prediction snapshots."""

from __future__ import annotations

import shutil

from pipeline_utils import DATA_DIR, FRONTEND_DATA_DIR, PROJECT_ROOT, load_json, write_json

MARKETS = ("home_win", "draw", "away_win", "over_2_5", "btts_yes")


def impact_level(deltas: dict[str, float]) -> str:
    strongest = max(abs(value) for value in deltas.values())
    if strongest < 0.005:
        return "none"
    if strongest < 0.04:
        return "low"
    if strongest < 0.10:
        return "medium"
    return "high"


def main() -> None:
    baseline = load_json(DATA_DIR / "generated" / "predictions_baseline.json")
    elo = load_json(DATA_DIR / "generated" / "predictions_elo.json")
    matches = load_json(DATA_DIR / "normalized" / "matches.json")
    elo_by_match = {prediction["match_id"]: prediction for prediction in elo}
    matches_by_id = {match["match_id"]: match for match in matches}
    baseline_ids = {prediction["match_id"] for prediction in baseline}
    if baseline_ids != set(elo_by_match):
        raise ValueError("Baseline and Elo prediction match IDs differ")
    comparisons = []

    for baseline_prediction in baseline:
        match_id = baseline_prediction["match_id"]
        elo_prediction = elo_by_match.get(match_id)
        match = matches_by_id.get(match_id)
        if elo_prediction is None or match is None:
            raise ValueError(f"Missing comparison input for {match_id}")
        deltas = {
            market: elo_prediction["markets"][market] - baseline_prediction["markets"][market] for market in MARKETS
        }
        features = elo_prediction["elo_features"]
        comparisons.append(
            {
                "match_id": match_id,
                "baseline_model_version": baseline_prediction["model_version"],
                "elo_model_version": elo_prediction["model_version"],
                "home_team": match["home_team"],
                "away_team": match["away_team"],
                "elo_available": features["elo_available"],
                "home_elo": features["home_elo"],
                "away_elo": features["away_elo"],
                "deltas": deltas,
                "baseline_top_score": baseline_prediction["top_scores"][0]["score"],
                "elo_top_score": elo_prediction["top_scores"][0]["score"],
                "impact_level": impact_level(deltas),
            }
        )

    generated_path = DATA_DIR / "generated" / "model_comparison.json"
    snapshot_path = DATA_DIR / "snapshots" / "model_comparison.json"
    frontend_path = FRONTEND_DATA_DIR / "model_comparison.json"
    write_json(comparisons, generated_path)
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    FRONTEND_DATA_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(generated_path, snapshot_path)
    shutil.copy2(generated_path, frontend_path)
    print(f"Compared {len(comparisons)} matches in {generated_path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
