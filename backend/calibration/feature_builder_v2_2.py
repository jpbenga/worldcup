"""Conservative V2.2 pre-match feature builder.

Only chronological result-history features are used. Sparse provider statistics,
events, lineups, provider xG and exploratory xG proxies are deliberately excluded.
"""

from backend.calibration.feature_builder_v2 import (
    FEATURE_NAMES,
    TeamHistory,
    build_chronological_features as _build,
    feature_matrix,
)


def build_chronological_features(split_matches, config):
    rows, timeline, audit, rating, history = _build(split_matches, config)
    audit.update(
        {
            "version": "v2.2",
            "features_retained": FEATURE_NAMES,
            "features_excluded": [
                "current_match_statistics",
                "current_match_events",
                "current_match_lineups",
                "provider_xg",
                "experimental_xg_proxy",
                "odds",
                "advanced_rolling_provider_statistics",
            ],
            "advanced_features_available": [
                "statistics",
                "events",
                "lineups",
                "sparse_provider_xg",
            ],
            "advanced_features_used": [],
            "exclusion_reason": "Coverage is not established globally; V2.2 isolates the effect of fresher and larger result history.",
            "training_dataset": "historical_splits_v2_1",
        }
    )
    return rows, timeline, audit, rating, history


__all__ = ["FEATURE_NAMES", "TeamHistory", "build_chronological_features", "feature_matrix"]
