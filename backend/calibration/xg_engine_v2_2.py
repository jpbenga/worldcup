"""V2.2 conservative expected-goals intensity model with low-sample shrinkage."""

from backend.calibration.xg_engine_v2 import expected_goals as _base_expected_goals
from backend.calibration.xg_engine_v2 import lambda_audit


def expected_goals(features, params):
    home, away, meta = _base_expected_goals(features, params)
    smoothing = float(params.get("smoothing", 0))
    threshold = float(params.get("low_sample_threshold", 0))
    extra = float(params.get("extra_low_sample_smoothing", 0))
    home_seen, away_seen = float(features["home_matches_seen"]), float(features["away_matches_seen"])
    home_smoothing = smoothing + (extra if home_seen < threshold else 0)
    away_smoothing = smoothing + (extra if away_seen < threshold else 0)
    base_home, base_away = float(params["base_home_goals"]), float(params["base_away_goals"])
    home = (home * home_seen + base_home * home_smoothing) / max(1.0, home_seen + home_smoothing)
    away = (away * away_seen + base_away * away_smoothing) / max(1.0, away_seen + away_smoothing)
    lower, upper = float(params["lambda_min"]), float(params["lambda_max"])
    home, away = min(upper, max(lower, home)), min(upper, max(lower, away))
    meta.update({"smoothing": smoothing, "home_effective_smoothing": home_smoothing, "away_effective_smoothing": away_smoothing})
    return home, away, meta


__all__ = ["expected_goals", "lambda_audit"]
