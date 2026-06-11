"""V2.2 chronological internal rating.

V2.2 intentionally retains the proven V2.0 predict-observe-update implementation.
The refreshed-data experiment changes the candidate parameter space, not the rating
update contract.
"""

from backend.calibration.internal_rating_v2 import InternalRating, RatingConfig, competition_weight

__all__ = ["InternalRating", "RatingConfig", "competition_weight"]
