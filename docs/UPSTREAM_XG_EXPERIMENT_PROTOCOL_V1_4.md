# Upstream xG Experiment Protocol V1.4

## Purpose

V1.4 may implement Competition-Weighted xG, Time-Decay xG, Elo-Prior xG and
Low-Sample Fallback xG as isolated challengers. This protocol prevents test
selection, temporal leakage, confounded combinations and automatic promotion.

## Inputs and fixed splits

- Primary dataset: `backend/data/normalized/historical_matches_expanded.json`.
- Fixed chronological splits: `historical_train_matches.json`,
  `historical_validation_matches.json`, and `historical_test_matches.json`.
- Base comparison: `calibrated_simple_poisson_v0.9`.
- Optional Elo inputs: only ratings with documented historical pre-match
  provenance; current/static Elo must be labeled as leakage-risk evidence.
- Identity mapping: `backend/data/mappings/team_identity_map.json`.

No World Cup 2026 fixture may enter training, validation or test.

## Temporal integrity

Every feature must have been knowable before the predicted kickoff. Time decay
is calculated relative to each predicted match. Training rows after that match
are forbidden. Elo must be the rating known before kickoff or reconstructed
chronologically. A current Elo snapshot used for historical prediction is a
temporal leakage risk and cannot support promotion.

## Parameter selection

1. Fit model state on train only.
2. Select all weights, half-lives, caps, thresholds and smoothing parameters
   using validation only.
3. Freeze the selected parameter set.
4. Evaluate test once for final evidence.
5. Do not revise parameters after observing test.

Each challenger is implemented and evaluated separately. The upstream combined
candidate remains deferred until isolated components pass independently.

## Mandatory metrics

- `log_loss_1x2`
- `brier_score_1x2`
- `accuracy_1x2`
- `average_real_result_probability`
- `exact_score_accuracy`
- `top_3_score_hit_rate`
- `draw_calibration_gap`
- `favorite_calibration_gap`
- `modal_1_1_rate`
- `high_confidence_wrong_predictions`
- `performance_by_competition`
- `performance_by_low_sample_teams`
- `average_predicted_goals_vs_actual_goals`

Reports must also retain parameter trials, feature coverage, effective sample
sizes, missing-feature behavior and explicit temporal-leakage findings.

## Guardrails

A challenger may be called promising, never promoted automatically, only if:

- test log loss improves V0.9 by at least `0.01`;
- test Brier improves V0.9 by at least `0.01`;
- validation log loss and Brier support the same improvement direction;
- draw calibration is not severely worsened;
- high-confidence wrong predictions do not increase;
- modal `1-1` concentration does not increase;
- accuracy and top-3 exact-score hit rate do not materially degrade;
- no temporal leakage is introduced;
- low-sample and major-competition segments show no unexplained severe harm.

## Expected artifacts

Each isolated challenger should publish versioned parameters, validation
trials, fixed validation/test predictions, metric reports, feature-coverage
diagnostics, comparison with V0.9 and the neutral prototype, segmented results,
limitations and a promotion recommendation.

## Non-promotion rules

- Default recommendation remains `do_not_promote_yet`.
- Test success does not authorize parameter revision or promotion.
- Current/static Elo cannot justify promotion on historical results.
- No combined challenger is allowed before isolated successes.
- No active engine or World Cup 2026 prediction changes without a later,
  explicit human decision.
