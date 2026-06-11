# Limited Quant Retrain Strategy V2.2

## Purpose

V2.0 proved that the chronological internal-rating, XGBoost, Poisson, replay and market-evaluation architecture works, but it was not deployed. Its final test degraded V0.9, its train-validation gap indicated overfit, modal `1-1` remained too concentrated, and its historical input ended in July 2024.

V2.1 justifies one controlled retrain because it expands completed senior-international history from 1,311 to 3,062 matches and moves the latest result to March 31, 2026. The refreshed splits pass the temporal-leakage audit. This changes the amount, composition and freshness of evidence without changing the modeling question.

The goal of V2.2 is to test whether fresher and larger historical results improve the quant engine before introducing high-sparsity post-match feature families.

## Limited Scope

V2.2 retains the V2 architecture and uses only conservative chronological result-history signals: pre-match internal rating, rating differences, matches seen, recent goals, smoothed attack and defence, competition family/tier, recency, days since last match and low-sample flags. Every row is built before the current result is observed.

Statistics, events and lineups are post-match feeds and must not be used naively for the current match. Their six-match probe availability does not establish broad historical coverage. Provider xG is sparse and cannot serve as global truth. The exploratory xG proxy is technically possible but remains unproven across the corpus. All these families, along with odds and future fixtures, are excluded from V2.2.

The retrain is limited rather than full to isolate whether refreshed results resolve V2.0's generalization and product-coherence failures. Adding sparse feature families at the same time would make attribution impossible and increase selection pressure.

## Deployment Boundary

Active deployment requires final-test log loss and Brier improvements over both V2.0 and V0.9, directionally consistent validation/test gains, a strongly reduced train-validation gap, materially lower modal `1-1`, at least 55% clear-favorite score alignment, useful DNB improvement, exploitable secondary markets, no temporal leakage and no obvious overfit.

Any degraded final-test calibration, excessive `1-1`, weak DNB, low-coverage market claim, leakage, overfit, or incomplete evidence blocks deployment. World Cup 2026 fixtures may be read only after a successful deployment decision to generate active predictions; they never train, validate or select V2.2.
