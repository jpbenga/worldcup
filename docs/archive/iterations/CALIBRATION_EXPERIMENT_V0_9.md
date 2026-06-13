# Calibration Experiment V0.9

## Objective and isolation

V0.9 trains an explainable simple Poisson model on the `917` historical train
matches, evaluates it on the chronological validation and test splits, and
compares it with the neutral `1.35 / 1.35` prototype. It remains separate from
the active World Cup 2026 engine and does not modify future predictions.

## Model

The **Calibrated Simple Poisson Model v0.9** estimates global home/away scoring
rates plus smoothed team home/away attack and defence strengths. Smoothing
weight is `8`, sparse-team threshold is `5`, and expected goals are bounded to
`0.2–3.5`. Unknown teams fall back to global rates. Elo, competition effects,
neutral-site context and recent form are not modeled.

## Chronological evaluation

The model is trained on `917` matches involving `159` teams from
`2014-06-12` through `2021-06-23`. Validation contains `196` matches and test
contains `198`; both are later than the training period.

| Split | Metric | Prototype | Calibrated | Delta calibrated - prototype |
|---|---|---:|---:|---:|
| Validation | accuracy_1x2 | 0.4337 | 0.5306 | +0.0969 |
| Validation | log_loss_1x2 | 1.0802 | 1.0374 | -0.0428 |
| Validation | brier_score_1x2 | 0.6550 | 0.6232 | -0.0318 |
| Validation | exact_score_accuracy | 0.0918 | 0.0918 | +0.0000 |
| Validation | top_3_score_hit_rate | 0.3061 | 0.3214 | +0.0153 |
| Test | accuracy_1x2 | 0.4040 | 0.4596 | +0.0556 |
| Test | log_loss_1x2 | 1.1037 | 1.0412 | -0.0625 |
| Test | brier_score_1x2 | 0.6697 | 0.6277 | -0.0420 |
| Test | exact_score_accuracy | 0.1566 | 0.1515 | -0.0051 |
| Test | top_3_score_hit_rate | 0.3434 | 0.3434 | +0.0000 |

Lower is better for log loss and Brier score. Higher is better for accuracy
and score hit rates. The calibrated model improves 1X2 accuracy, log loss and
Brier score on both splits. It does not improve validation exact-score
accuracy, slightly reduces test exact-score accuracy, and leaves test top-3
score hit rate unchanged.

## Calibrated score and goal results

- Validation exact score accuracy: `0.0918`
- Validation top-3 score hit rate: `0.3214`
- Validation average predicted goals: `1.4723` home / `1.0957` away
- Validation average actual goals: `1.4082` home / `1.1735` away
- Test exact score accuracy: `0.1515`
- Test top-3 score hit rate: `0.3434`
- Test average predicted goals: `1.4413` home / `1.1485` away
- Test average actual goals: `1.3939` home / `1.0354` away

## Decision

- Decision: `experimental_only`
- Promotion recommendation: `do_not_promote_yet`
- Active engine replaced: `false`

The experiment is not promoted automatically. The dataset remains
medium-sufficiency; competition composition changes across chronological
splits, and AET/PEN, neutral-site and mixed-scope semantics remain unresolved.

## Next step

Review the validation/test deltas and segmented errors manually before a V1.0
experiment. A next challenger should test competition-aware or chronological
form features without touching the active engine.

## V1.0 diagnostic follow-up

V1.0 performs the requested error segmentation without retraining this model.
The analysis finds near-zero draw-class selections despite substantial actual
draw rates, strong modal `1-1` concentration, underestimation of 4+ goal
matches and uneven competition/team performance. Promotion remains
`do_not_promote_yet`. See `docs/CALIBRATION_ERROR_ANALYSIS_V1_0.md`.
