# Quant Engine Rebuild Decision V2.0

## Why rebuild

V1.2 showed that post-probability draw and Dixon-Coles corrections did not pass
the guardrails. V1.4 showed that isolated competition weighting, time decay and
low-sample smoothing also failed to establish a promotable engine. Repeated
small adjustments around the V0.9 Simple Poisson structure are therefore
stopped in favor of one controlled hybrid rebuild.

## Why XGBoost and Optuna

XGBoost can learn bounded nonlinear interactions among chronological rating,
recent scoring, attack/defence, competition and sample-depth features without
requiring a deep-learning stack. Low tree depth and explicit regularization are
mandatory because the dataset is small.

Optuna provides reproducible validation-only search over rating, scoring and
regularized XGBoost parameters. The final test remains untouched until the
selected configuration is frozen.

## Rating and replay decision

External static Elo is abandoned as a primary signal because it leaks future
strength into historical matches. V2 builds a chronological internal rating:
read pre-match ratings, predict, observe, update, then move to the next match.
The same online discipline applies to recent form and team scoring features.

Historical replay is mandatory because a static fit does not represent what
would have been knowable at each kickoff.

## Product targets

Secondary markets become a major target because they expose useful structure
beyond a single 1X2 label and make calibration defects easier to diagnose.
Draw No Bet is reported with wins, losses and pushes separately. Exact score
remains a secondary metric:

> Exact score accuracy around 8-10% may already be reasonable. The engine must therefore be judged primarily on probabilistic calibration, 1X2, secondary markets, DNB, and product coherence.

Product coherence is a deployment gate:

> A model that repeatedly assigns a favorite in 1X2 markets while keeping 1-1 as the modal score for most matches is product-incoherent unless explicitly justified by the full score distribution.

## Conditional active replacement

V2 may replace the active engine only if final out-of-sample evidence establishes
it: meaningful V0.9 improvement, useful secondary markets at non-trivial
coverage, sharply lower `1-1` concentration, acceptable favorite-score
alignment, no temporal leakage and no obvious validation/test contradiction.

If any deployment gate fails, V2 remains experimental, active predictions are
not modified, and the report must explain the blocking evidence. Promotion is
an outcome of the evidence, not an assumption of this rebuild.
