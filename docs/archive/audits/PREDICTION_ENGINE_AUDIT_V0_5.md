# Prediction Engine Audit V0.5

## Result

- Matches audited: `72`
- Baseline top-score distribution: `{'1-1': 72}`
- Elo top-score distribution: `{'1-1': 72}`
- Baseline 1-1 rate: `100.0%`
- Elo 1-1 rate: `100.0%`
- Top scores changed by Elo: `0`
- Elo unavailable: `0`
- Maximum market delta: `0.0435`

## Diagnosis

Predictions are highly concentrated on 1-1 because every real fixture currently receives the same neutral baseline expected goals. Elo adjusts markets but does not change the modal score.

This is not a sorting bug or a missing-Elo fallback. The active real-data
baseline assigns neutral `1.35 / 1.35` expected goals to every fixture because
validated historical team features are not yet available. The moderate Elo
layer changes market probabilities, but does not change the most likely score.

## Decision

Do not force diversity and do not present these predictions as calibrated.
Keep the prototype visible, expose its inputs, and replace neutral baseline
features only when validated historical data is available.

V0.6 documents the replacement boundary and future calibrated-engine path in
`docs/CURRENT_ENGINE_AUDIT.md` and `docs/FUTURE_ENGINE_BLUEPRINT.md`. It does
not change these audited prediction values.
