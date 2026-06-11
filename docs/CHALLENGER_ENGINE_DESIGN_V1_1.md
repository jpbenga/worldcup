# Improved Calibrated Engine Challenger Design V1.1

## Scope and decision

V1.1 is a design-only phase for isolated V1.2 challengers. It does not
implement or train a model, replace the active prototype engine, modify World
Cup 2026 predictions, or change the promotion recommendation from
`do_not_promote_yet`.

V0.9 must not be promoted yet. It improves 1X2 log loss and Brier score over
the neutral prototype, but V1.0 found severe draw-class underprediction, modal
`1-1` concentration, high-total underestimation, unstable confidence buckets,
uneven competition performance and many low-sample teams.

## Design principle

Reuse useful ideas from the old engine, but reimplement them cleanly without
importing sensitive files or unreliable fitted parameters. `drc-prototype/`
must not be restored. Any inherited concept must be independently specified,
implemented, fitted and evaluated against the versioned historical splits.

## Stable boundaries

Every V1.2 challenger must remain separate from the active engine and preserve
the published historical prediction contract:

- stable `match_id`, teams, kickoff and provenance;
- explicit model version, family, experimental status and calibration flag;
- normalized score matrix, markets and top scores;
- actual result fields only for completed historical evaluation;
- separate generated comparison and diagnostic artefacts;
- no write to active `predictions*.json` or World Cup 2026 snapshots.

## Observed V1.0 targets

| Problem | Validation | Test | Design consequence |
|---|---:|---:|---|
| Actual draw rate / predicted draw class | 24.0% / 0.5% | 31.8% / 0.0% | Prioritize draw calibration and low-score correction. |
| Modal `1-1` / actual `1-1` | 63.8% / 9.2% | 67.7% / 15.7% | Measure modal concentration for every challenger. |
| Predicted / actual goals in 4+ goal matches | 2.59 / 5.02 | 2.61 / 4.60 | Test recency and alternatives that permit stronger tails. |
| Largest confidence gap, bucket 0.60-0.70 | -26.6 pts | +22.4 pts | Require confidence-bucket reporting. |
| Low-sample teams | 39/75 | 60/93 | Test priors and preserve sample warnings. |
| Weak competition segment | World Cup validation | AFCON test | Test competition effects without hiding segment regressions. |

## Challenger A — Draw-Calibrated Poisson

**Priority:** 1

**Target:** Correct draw underprediction while retaining coherent 1X2
probabilities.

**V1.2 isolated experiment:**

- fit a bounded multiplicative draw adjustment on validation only;
- renormalize home/draw/away probabilities after adjustment;
- compare a small documented parameter grid;
- preserve the original score matrix as source evidence unless a separate,
  explicitly versioned matrix adjustment is tested;
- reject settings that simply overpredict draws.

**Success criteria:**

- draw calibration gap decreases on validation and test;
- test log loss and Brier improve;
- 1X2 accuracy does not fall by more than 1 percentage point;
- high-confidence wrong predictions do not increase.

## Challenger B — Dixon-Coles Rho Optimized

**Priority:** 2

**Target:** Improve low-score behavior and reduce excessive modal `1-1`
concentration.

**V1.2 isolated experiment:**

- test a bounded rho grid using train/validation only;
- report effects on `0-0`, `1-0`, `0-1` and `1-1`;
- evaluate draw calibration, log loss, Brier and modal score concentration;
- do not optimize rho solely for exact-score accuracy.

**Success criteria:**

- lower validation and test log loss or Brier;
- lower modal `1-1` concentration;
- improved draw calibration without increasing high-confidence errors.

## Challenger C — Competition-Weighted Poisson

**Priority:** 3

**Target:** Address different scoring and selection processes across
competitions.

**V1.2 isolated experiment:**

- compare global rates with competition-family or competition-tier intercepts;
- keep friendlies low-weight if introduced later;
- preserve per-competition reports and sample warnings;
- reject improvements driven by one segment while major segments regress.

**Success criteria:**

- improve weak segments, especially AFCON test;
- improve aggregate test log loss and Brier;
- avoid material degradation in World Cup, Euro and other major tournaments.

## Challenger D — Time-Decay Poisson

**Priority:** 4

**Target:** Reduce temporal drift and stale team-strength estimates.

**V1.2 isolated experiment:**

- test exponential half-lives of 12, 24 and 36 months;
- calculate weights strictly from dates available before evaluation;
- retain minimum effective-sample safeguards;
- report effective sample sizes and validation/test stability.

**Success criteria:**

- improve test log loss and Brier;
- remain stable across validation and test;
- avoid excessive variance for low-sample teams.

## Challenger E — Elo-Prior Poisson

**Priority:** 5

**Target:** Improve favorite and low-sample team calibration by using Elo as a
bounded prior rather than an unmeasured post-hoc adjustment.

**V1.2 isolated experiment prerequisites:**

- use ratings known before kickoff or reconstruct them chronologically;
- blend Elo and historical strengths with a bounded, documented weight;
- test stronger fallback value for low-sample teams;
- prevent Elo from overwhelming historical evidence.

**Success criteria:**

- improve low-sample team and favorite calibration;
- improve validation and test log loss/Brier;
- reduce high-confidence wrong favorites.

## Challenger F — Combined Candidate

**Priority:** deferred

Combine only isolated changes from A–E that independently pass the evaluation
protocol. Do not implement this candidate until each included component has a
documented causal benefit. The combined candidate must be compared with the
neutral prototype, V0.9 and every included isolated challenger.

## V1.2 execution order

1. Implement A and B because they directly target the largest observed draw
   and modal-score defects.
2. Evaluate C and D as independent feature/weighting experiments.
3. Implement E only after chronological pre-match Elo provenance is verified.
4. Consider F only after isolated successes pass validation and test gates.

## Promotion boundary

No challenger is promoted automatically. V1.2 outputs remain historical
experiments. Promotion requires the protocol in
`docs/CHALLENGER_EVALUATION_PROTOCOL.md`, explicit human review and a separate
decision that authorizes any future 2026 prediction change.
