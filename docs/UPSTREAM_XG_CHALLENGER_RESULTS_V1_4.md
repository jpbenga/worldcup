# Upstream xG Isolated Challenger Results V1.4

## Objective and boundaries

V1.4 implements isolated upstream xG challengers after V1.2 showed that
post-probability corrections were insufficient and V1.3 validated the upstream
direction. Parameters are selected on validation only and test is used only
after selection. The active engine and World Cup 2026 predictions are
unchanged; no combined challenger is implemented and no model is promoted.

## Methods and tested parameters

- Competition-Weighted xG fits weighted V0.9-form team strengths on train only
  using the three documented competition-weight grids. No friendly rows exist,
  so `friendly_weight` is not evaluable.
- Time-Decay xG fits train-only weights relative to every predicted match and
  tests half-lives `12`, `24`, `36`, and `48` months.
- Low-Sample Fallback xG tests thresholds/smoothing `(5, 8)`, `(8, 12)`, and
  `(10, 16)`.
- Elo-Prior xG uses the current/static Elo snapshot only as a non-promotable
  diagnostic with explicit temporal leakage risk.

## Competition-Weighted xG

- Selected parameters: `{'major_tournament_weight': 1.0, 'continental_championship_weight': 1.0, 'qualifier_weight': 0.8, 'friendly_weight': 0.5}`
- Validation log loss / Brier: `1.0374` / `0.6233`
- Test log loss / Brier: `1.0421` / `0.6284`
- Test draw / favorite calibration gaps: `+0.0494` / `-0.0046`
- Test modal 1-1 / high-confidence wrong: `68.2%` / `4`
- Test delta vs V0.9 log loss / Brier: `+0.0009` / `+0.0006`
- Passed all guardrails: `false`
- Candidate for future combination: `false`
- Failed guardrails: test_log_loss_improves_by_0_01, test_brier_improves_by_0_01, validation_brier_improved, modal_1_1_not_increased

The JSON artifact retains every validation trial and the required competition,
tier, season and low-sample segment reports.

## Time-Decay xG

- Selected parameters: `{'half_life_months': 48}`
- Validation log loss / Brier: `1.0288` / `0.6183`
- Test log loss / Brier: `1.0549` / `0.6362`
- Test draw / favorite calibration gaps: `+0.0515` / `+0.0007`
- Test modal 1-1 / high-confidence wrong: `93.9%` / `2`
- Test delta vs V0.9 log loss / Brier: `+0.0137` / `+0.0085`
- Passed all guardrails: `false`
- Candidate for future combination: `false`
- Failed guardrails: test_log_loss_improves_by_0_01, test_brier_improves_by_0_01, accuracy_not_materially_worse, modal_1_1_not_increased

The JSON artifact retains every validation trial and the required competition,
tier, season and low-sample segment reports.

## Low-Sample Fallback xG

- Selected parameters: `{'low_sample_threshold': 5, 'extra_smoothing_weight': 8}`
- Validation log loss / Brier: `1.0390` / `0.6239`
- Test log loss / Brier: `1.0404` / `0.6269`
- Test draw / favorite calibration gaps: `+0.0504` / `-0.0058`
- Test modal 1-1 / high-confidence wrong: `67.7%` / `4`
- Test delta vs V0.9 log loss / Brier: `-0.0008` / `-0.0008`
- Passed all guardrails: `false`
- Candidate for future combination: `false`
- Failed guardrails: test_log_loss_improves_by_0_01, test_brier_improves_by_0_01, validation_log_loss_improved, validation_brier_improved

The JSON artifact retains every validation trial and the required competition,
tier, season and low-sample segment reports.

## Elo-Prior xG diagnostic

- Executed: `true`
- Temporal leakage risk: `true`
- Promotion eligible: `false`
- Candidate for future combination: `false`
- Test log loss / Brier: `0.9991` / `0.5995`

Current/static Elo snapshot used on historical matches. This is temporal
leakage risk evidence and cannot support promotion.

## Ranking and conclusion

1. `elo_prior_xg_diagnostic`: test log loss `0.9991`, Brier `0.5995`, combination candidate `false`
2. `low_sample_fallback_xg`: test log loss `1.0404`, Brier `0.6269`, combination candidate `false`
3. `competition_weighted_xg`: test log loss `1.0421`, Brier `0.6284`, combination candidate `false`
4. `time_decay_xg`: test log loss `1.0549`, Brier `0.6362`, combination candidate `false`

- Do not promote any V1.4 challenger; promotion_recommendation remains do_not_promote_yet.
- No isolated upstream challenger passes every future-combination guardrail.
- Treat Elo results as non-promotable temporal-leakage-risk diagnostics only.

## Decision

- Promotion recommendation: `do_not_promote_yet`
- Combined challenger implemented: `false`
- Active engine replaced: `false`
- World Cup 2026 predictions modified: `false`

The full JSON retains validation trials, V0.9 deltas, segment metrics,
effective-weight diagnostics and guardrails. Human review is required before
any later experiment.
