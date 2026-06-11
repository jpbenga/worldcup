"""V2.2 chronological historical replay using the V2.2 xG intensity model."""

import backend.calibration.historical_replay_v2 as _base
from backend.calibration.xg_engine_v2_2 import expected_goals

_base.expected_goals = expected_goals

build_predictions = _base.build_predictions
coherence_audit = _base.coherence_audit
evaluate_predictions = _base.evaluate_predictions
segment_metrics = _base.segment_metrics

__all__ = ["build_predictions", "coherence_audit", "evaluate_predictions", "segment_metrics"]
