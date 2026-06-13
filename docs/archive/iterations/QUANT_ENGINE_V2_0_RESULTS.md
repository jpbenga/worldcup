# Quant Hybrid Engine V2.0 Results

## Outcome

V2.0 combines an internal chronological rating, pre-match features, regularized XGBoost
probabilities and an independent-Poisson score distribution. All historical features are reconstructed chronologically before each result is observed. Optuna selects on validation only; the fixed configuration is then evaluated once on test. No World Cup 2026 fixture and no external static Elo rating enters training or selection.

- Validation log loss / Brier: `0.9602` / `0.5694`
- Test log loss / Brier: `1.0513` / `0.6367`
- Test exact / top-3 / top-5: `14.1%` / `33.8%` / `51.0%`
- Test modal 1-1 rate: `47.5%`
- Test delta vs V0.9 log loss / Brier: `+0.0101` / `+0.0090`
- Deployment decision: `do_not_deploy`

## Deployment gates

- `main_metric_gain_or_secondary_utility`: `true`
- `validation_supports_gain`: `true`
- `modal_1_1_strongly_reduced`: `false`
- `favorite_score_product_coherent`: `true`
- `no_temporal_leakage`: `true`
- `no_obvious_overfit`: `false`
- `secondary_markets_exploitable`: `true`
- `active_input_freshness_and_team_coverage`: `false`

The active engine is changed only when every historical, product-coherence,
overfitting, secondary-market, and operational-data gate passes. Failed results are
retained in the JSON artifacts rather than hidden.
