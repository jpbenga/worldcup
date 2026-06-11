# Historical Dataset Split

## Method

Strict deterministic chronological split: first 70% train, next 15%
validation, final 15% test. No randomization, model training or prediction
evaluation occurs in this step.

## Counts and ranges

- Train: `917` — `2014-06-12T20:00:00+00:00` to `2021-06-23T21:00:00+00:00`
- Validation: `196` — `2021-06-24T00:00:00+00:00` to `2023-07-03T01:00:00+00:00`
- Test: `198` — `2023-07-03T01:00:00+00:00` to `2024-07-15T00:30:00+00:00`

## Leakage checks

`{'future_2026_fixtures_excluded': True, 'date_order_valid': True, 'duplicate_fixture_ids_across_splits': False}`

Competition composition differs by period and must be considered in future
calibration experiments.
