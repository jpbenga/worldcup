# Score Matrix Challengers V2.8

V2.8 evaluates bounded post-model score-matrix transformations on the frozen 460-match historical test. World Cup 2026 fixtures are never used for selection. No XGBoost model is retrained and Optuna is not rerun.

## Baseline

The active matrix reaches exact/top-3/top-5 accuracy of `14.6%` / `35.9%` / `51.3%`, score log loss `3.1647`, 1X2 Brier `0.5212` and over-2.5 Brier `0.2455`.

## Challengers

Tested families include favorite-gap lambda scaling, strong-favorite margin redistribution, total-goals temperature and strong-favorite draw-mass correction. Challenger E, a constrained hybrid reconstruction matching 1X2, over 2.5 and team-goal targets, is assessed as feasible but deferred because it requires a dedicated numerical solver and validation protocol.

The best measured challenger is `A_gap_alpha_1.5_beta_0.75`. Its exact/top-3/top-5 accuracy is `12.8%` / `37.6%` / `52.0%`, score log loss `3.1371`, 1X2 Brier `0.5098` and over-2.5 Brier `0.2439`.

The exact-score rate decreases from `14.6%` to `12.8%`. This trade-off remains visible: the candidate is supported by improved score likelihood, top-3/top-5, broad-market Brier and favorite-margin realism, not by an exact-score accuracy claim.

## Decision

Promotion decision: **generate_candidate_not_active**. The best challenger improves historical score likelihood and favorite-margin realism while passing every broad-market guardrail.

A candidate file is generated only when every historical guardrail passes and the improvement is positive. Even then it remains explicitly non-active and preserves frozen hybrid 1X2 probabilities.
