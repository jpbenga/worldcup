# Monte Carlo Stability V2.0

Each validation and test match is simulated exactly `1500` times with seed `2026`.
The analytical Poisson matrix remains the exact model output; Monte Carlo is used to
measure sampling stability and prepare future tournament scenario simulation.

The test analytical-versus-simulated average absolute gap is
`0.0093`;
the maximum per-match average gap is
`0.0284`.
These values compare like-for-like Poisson probabilities, not the blended XGBoost
1X2 output. All test matches fall below a `0.03` average absolute gap, so the
sampling implementation is stable enough for future tournament-scenario work.
This stability does not validate the predictive model itself: model promotion still
depends on out-of-sample calibration, coherence, and operational-data gates.
