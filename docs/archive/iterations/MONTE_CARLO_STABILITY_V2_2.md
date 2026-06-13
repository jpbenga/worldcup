# Monte Carlo Stability V2.2

Each validation and test match receives exactly 1,500 deterministic Poisson simulations with seed 2026. The analytical score matrix remains the model output; Monte Carlo measures sampling stability only.

The test analytical-versus-simulated average absolute gap is `0.0093` and the maximum match gap is `0.0281`. This validates simulation stability, not predictive promotion.

The same seed and simulation count make reruns directly comparable. Promotion
still depends on historical calibration, market utility, coherence, leakage
and overfit gates.
