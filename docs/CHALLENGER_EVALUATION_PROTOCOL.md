# Challenger Evaluation Protocol

## Purpose

This protocol defines how isolated V1.2 challengers are compared with the
neutral prototype and `calibrated_simple_poisson_v0.9`. It prevents selection
based on one attractive metric, one competition or more varied modal scores.

## Data and leakage rules

- Use the existing chronological train, validation and test splits.
- Fit model parameters and hyperparameters without using test results.
- Use no World Cup 2026 fixture as labeled data.
- Use only features available before each evaluated kickoff.
- Keep historical predictions, parameters and comparison artefacts versioned.
- Report low-sample and missing-feature behavior explicitly.

## Required metrics

Every challenger report must contain:

- 1X2 log loss;
- 1X2 Brier score;
- 1X2 accuracy;
- average probability assigned to the true result;
- exact-score accuracy;
- top-3 exact-score hit rate;
- draw calibration gap;
- favorite calibration gap;
- modal score distribution and `1-1` concentration;
- high-confidence wrong predictions;
- performance by competition;
- performance by season;
- performance by team sample-size bucket.

It must also retain average predicted/actual home and away goals, confidence
buckets and the worst log-loss matches.

## Comparison set

Each V1.2 challenger must be evaluated against:

1. `prototype_neutral_v0.5`;
2. `calibrated_simple_poisson_v0.9`;
3. other challengers in the same V1.2 evaluation batch.

The comparison must use identical completed historical matches and metrics.

## Prudential success gates

A challenger can be called **promising**, not promoted, only if it satisfies
all mandatory gates:

| Gate | Required threshold |
|---|---|
| Test log loss | Improve versus V0.9 by at least `0.01`. |
| Test Brier | Improve versus V0.9 by at least `0.01`. |
| Draw calibration | Reduce absolute draw calibration gap on validation and test. |
| Validation support | Beat V0.9 log loss and Brier on validation as well as test. |
| Accuracy guardrail | No decrease greater than `0.01` absolute on validation or test. |
| Top-3 guardrail | No decrease greater than `0.01` absolute on validation or test. |
| Modal score | Reduce `1-1` modal concentration without hiding a metric regression. |
| Confidence safety | Do not increase high-confidence wrong predictions. |

A challenger failing a mandatory gate remains experimental even if another
metric improves substantially.

## Segmented review gates

Before a challenger is considered promising:

- no major competition segment may show an unexplained material regression;
- weak segments, including AFCON test, must be reported explicitly;
- season drift must be compared with V0.9;
- low-sample teams must be separated from teams with at least five matches;
- favorite and draw behavior must be reviewed independently;
- worst-match diagnostics must be retained, not discarded as outliers.

## Promotion rules

- No challenger is promoted automatically.
- Every promotion requires explicit human validation.
- A challenger must beat V0.9 on validation **and** test.
- It must reduce at least one major defect identified by V1.0.
- It must not modify World Cup 2026 predictions before an explicit decision.
- It must preserve or deliberately version existing JSON contracts.
- It must produce comparisons against the prototype and V0.9.
- A combined challenger may include only isolated components that passed this
  protocol independently.

The default recommendation is `do_not_promote_yet`.

## Required artefacts

Each implemented challenger should publish:

- versioned parameters and training summary;
- validation and test historical predictions;
- validation and test metric reports;
- comparison against prototype and V0.9;
- segmented error analysis using the V1.0 schema;
- explicit promotion recommendation and human-validation status.

## V1.2 isolated selection thresholds

For the first isolated batch, draw-factor selection minimizes validation log
loss among candidates whose validation Brier is no more than `0.01` worse,
whose accuracy falls by no more than `0.02`, and whose predicted draw-class
rate moves closer to the actual draw rate. Dixon-Coles rho selection minimizes
validation log loss among candidates whose modal `1-1` rate does not increase,
whose Brier is no more than `0.01` worse, and whose top-3 score hit rate falls
by no more than `0.02`.

These are selection guards, not promotion gates. The stricter prudential
success gates above still determine whether a challenger can be called
promising.
