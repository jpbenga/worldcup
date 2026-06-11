# Calibration Error Analysis V1.0

## Objective and sources

V1.0 diagnoses the fixed `calibrated_simple_poisson_v0.9` predictions on the
chronological validation and test splits. It reads existing historical
predictions, matches and the prototype comparison only. No model is retrained,
no World Cup 2026 prediction is regenerated, and promotion remains blocked.

## Validation results

- Matches: `196`
- Accuracy 1X2: `53.1%`
- Log loss: `1.0374`
- Brier: `0.6232`
- Draw actual / predicted class: `24.0%` / `0.5%`
- Favorite actual win / average probability: `52.6%` / `48.1%`
- Worst log-loss match: `Belgium–Morocco` (`0-2`, log loss `2.3819`)
- Confidence buckets: 0.33-0.40: n=38, gap=+0.174, 0.40-0.50: n=88, gap=+0.073, 0.50-0.60: n=49, gap=+0.032, 0.60-0.70: n=16, gap=-0.266, 0.70+: n=5, gap=-0.133

### Competition segments

| Competition | Matches | Accuracy | Log loss | Brier |
|---|---:|---:|---:|---:|
| Africa Cup of Nations | 52 | 44.2% | 1.0316 | 0.6235 |
| CONCACAF Gold Cup | 50 | 62.0% | 1.0053 | 0.6030 |
| Copa America | 15 | 53.3% | 1.0224 | 0.6153 |
| Euro Championship | 15 | 53.3% | 1.0589 | 0.6376 |
| World Cup | 64 | 53.1% | 1.0658 | 0.6371 |

### Season segments

| Season | Matches | Accuracy | Log loss | Brier |
|---|---:|---:|---:|---:|
| 2020 | 15 | 53.3% | 1.0589 | 0.6376 |
| 2021 | 98 | 53.1% | 1.0093 | 0.6070 |
| 2022 | 64 | 53.1% | 1.0658 | 0.6371 |
| 2023 | 19 | 52.6% | 1.0702 | 0.6481 |

### Team and score diagnostics

- Worst eligible team by log loss: `Panama` (`1.5364`)
- Low-sample teams: `39`
- Modal 1-1 / actual 1-1: `63.8%` / `9.2%`
- High-confidence wrong predictions: `12`
- Unexpected upsets retained: `20`
- Unexpected draws retained: `20`

### Problematic matches

- Three worst log-loss matches: `Belgium–Morocco` (0-2, 2.382), `Canada–Morocco` (1-2, 2.031), `Costa Rica–Panama` (1-2, 1.949)
- Highest-confidence wrong predictions: `Belgium–Morocco` (72.2%), `Burkina Faso–Ethiopia` (71.2%), `Netherlands–Ecuador` (66.5%)

## Test results

- Matches: `198`
- Accuracy 1X2: `46.0%`
- Log loss: `1.0412`
- Brier: `0.6277`
- Draw actual / predicted class: `31.8%` / `0.0%`
- Favorite actual win / average probability: `46.0%` / `47.1%`
- Worst log-loss match: `Belgium–Slovakia` (`0-1`, log loss `2.1716`)
- Confidence buckets: 0.33-0.40: n=50, gap=+0.023, 0.40-0.50: n=84, gap=-0.007, 0.50-0.60: n=45, gap=-0.117, 0.60-0.70: n=14, gap=+0.224, 0.70+: n=5, gap=-0.155

### Competition segments

| Competition | Matches | Accuracy | Log loss | Brier |
|---|---:|---:|---:|---:|
| Africa Cup of Nations | 52 | 38.5% | 1.0796 | 0.6532 |
| Asian Cup | 51 | 54.9% | 1.0379 | 0.6252 |
| CONCACAF Gold Cup | 12 | 50.0% | 0.9980 | 0.6088 |
| Copa America | 32 | 50.0% | 1.0017 | 0.6038 |
| Euro Championship | 51 | 41.2% | 1.0403 | 0.6238 |

### Season segments

| Season | Matches | Accuracy | Log loss | Brier |
|---|---:|---:|---:|---:|
| 2023 | 115 | 47.0% | 1.0526 | 0.6362 |
| 2024 | 83 | 44.6% | 1.0254 | 0.6161 |

### Team and score diagnostics

- Worst eligible team by log loss: `Switzerland` (`1.2972`)
- Low-sample teams: `60`
- Modal 1-1 / actual 1-1: `67.7%` / `15.7%`
- High-confidence wrong predictions: `4`
- Unexpected upsets retained: `20`
- Unexpected draws retained: `20`

### Problematic matches

- Three worst log-loss matches: `Belgium–Slovakia` (0-1, 2.172), `USA–Panama` (1-1, 1.762), `Netherlands–Austria` (2-3, 1.712)
- Highest-confidence wrong predictions: `Belgium–Slovakia` (72.1%), `USA–Panama` (70.7%), `Canada–Uruguay` (63.0%)


## Overall findings

- Validation: actual draws are 24.0%, while draw is the predicted class in 0.5% of matches.
- Validation: favorites win 52.6% of matches against an average favorite probability of 48.1%; upset rate is 23.5%.
- Validation: in 51 matches with 4+ goals, the model predicts 2.59 goals on average versus 5.02 actual.
- Validation: largest eligible confidence calibration gap is -26.6% in bucket 0.60-0.70 (n=16).
- Validation: 39 of 75 teams have fewer than five matches in the split.
- Validation: largest eligible team points overestimate is Qatar (+5.03); largest underestimate is USA (-8.57).
- Test: actual draws are 31.8%, while draw is the predicted class in 0.0% of matches.
- Test: favorites win 46.0% of matches against an average favorite probability of 47.1%; upset rate is 22.2%.
- Test: in 47 matches with 4+ goals, the model predicts 2.61 goals on average versus 4.60 actual.
- Test: largest eligible confidence calibration gap is +22.4% in bucket 0.60-0.70 (n=14).
- Test: 60 of 93 teams have fewer than five matches in the split.
- Test: largest eligible team points overestimate is USA (+4.61); largest underestimate is Spain (-10.06).
- Worst competition segment with at least five matches is Africa Cup of Nations on test (log loss 1.0796, accuracy 38.5%, n=52).
- Worst season segment with at least five matches is 2023 on validation (log loss 1.0702, n=19).
- Validation: 1-1 is modal in 63.8% of predictions versus 9.2% of actual scores.
- Test: 1-1 is modal in 67.7% of predictions versus 15.7% of actual scores.
- V0.9 still improves test log loss by -0.0625 and test Brier by -0.0420 versus the neutral prototype.

## Priority recommendations

- Measure a draw-probability adjustment on validation: draw-class predictions trail actual draws by 23.5%.
- Investigate high-score underestimation on validation; 4+ goal matches are underpredicted by 2.43 goals on average.
- Calibrate confidence bucket 0.60-0.70 on validation; observed accuracy differs from average confidence by -26.6%.
- Treat team rankings on validation cautiously and expand coverage: 39/75 teams have low split samples.
- Measure a draw-probability adjustment on test: draw-class predictions trail actual draws by 31.8%.
- Investigate high-score underestimation on test; 4+ goal matches are underpredicted by 1.98 goals on average.
- Calibrate confidence bucket 0.60-0.70 on test; observed accuracy differs from average confidence by +22.4%.
- Treat team rankings on test cautiously and expand coverage: 60/93 teams have low split samples.
- Audit competition effects beginning with Africa Cup of Nations on test; it has the highest eligible competition log loss (1.0796).
- Review temporal drift around season 2023; it has the highest eligible season log loss (1.0702).
- Reduce modal 1-1 concentration on validation; predicted modal rate exceeds actual rate by 54.6%.
- Reduce modal 1-1 concentration on test; predicted modal rate exceeds actual rate by 52.0%.
- Keep promotion recommendation do_not_promote_yet until a second challenger passes the same splits.

## V1.1 challenger hypotheses

- Test a fitted Dixon-Coles rho or explicit draw-calibration layer.
- Test recent-form attack features or a heavier-tailed score model for high-total matches.
- Test a post-model probability calibration layer using validation data only.
- Test competition-aware intercepts or weighting because segment performance differs by competition.
- Test a chronological recent-form window or time decay to address observed season drift.
- Expand history for teams repeatedly flagged with low split sample sizes before tuning team parameters.

## Decision

- Promotion recommendation: `do_not_promote_yet`
- Model retrained: `false`
- Active engine changed: `false`
- World Cup 2026 predictions changed: `false`

The next step is **V1.1 — Second Calibration Challenger Design**, after human
review of the full JSON rankings and problematic matches.

## V1.1 design follow-up

Human review accepted the V1.0 diagnosis and retained
`do_not_promote_yet`. V1.1 converts the observed defects into isolated,
testable challenger specifications and a prudential evaluation protocol. It
does not implement or train a new model. See
`docs/CHALLENGER_ENGINE_DESIGN_V1_1.md`.
