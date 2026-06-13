# Isolated Calibration Challenger Results V1.2

## Objective and boundaries

V1.2 implements only the two first isolated challengers accepted in V1.1:
Draw-Calibrated Poisson and Dixon-Coles Rho Optimized. Both reuse fixed V0.9
historical predictions. Parameters are selected on the chronological validation
split only, and the test split is used only for final evaluation.

The active engine, World Cup 2026 predictions and main UX are unchanged. No
combined challenger is implemented and no model is promoted.

## V0.9 and V1.1 reminder

V0.9 remains the experimental base model. Its test log loss is
`1.0412`, Brier is `0.6277`,
and draw calibration gap is `+0.0506`.
The available neutral prototype reference has test log loss
`1.1037` and Brier
`0.6697`.
V1.1 prioritized draw calibration first and Dixon-Coles rho optimization
second, with promotion blocked pending isolated evidence and human review.

## Validation-only selection method

- Draw factor grid: `1.05, 1.10, 1.15, 1.20, 1.25, 1.30, 1.35, 1.40, 1.50`.
- Rho grid: `-0.20, -0.15, -0.10, -0.05, 0.00, 0.05, 0.10`.
- Selection objective: minimum validation log loss among candidates passing
  the documented challenger-specific validation guardrails.
- Test metrics never influence parameter selection.

## Challenger A — Draw-Calibrated Poisson

- Selected on validation only: `draw_factor=1.1`
- Test was used only after parameter selection: `true`
- Passed all prudential guardrails: `false`
- Candidate for future combination: `false`

| Split | Accuracy | Log loss | Brier | Draw gap | Top-3 | Modal 1-1 | High-conf wrong |
|---|---:|---:|---:|---:|---:|---:|---:|
| Validation | 0.5204 | 1.0409 | 0.6252 | -0.0464 | 0.3214 | 0.6378 | 10 |
| Test | 0.4646 | 1.0373 | 0.6256 | +0.0317 | 0.3434 | 0.6768 | 4 |

Test deltas versus V0.9 (challenger minus base): log loss `-0.0039`,
Brier `-0.0021`, accuracy `+0.0051`,
top-3 `+0.0000`, absolute draw-gap
`-0.0190`, modal 1-1 `+0.0000`,
and high-confidence wrong `+0`.

### Guardrails

- [ ] test_log_loss_improves_by_0_01
- [ ] test_brier_improves_by_0_01
- [ ] draw_gap_reduced_validation
- [x] draw_gap_reduced_test
- [ ] validation_log_loss_improved
- [ ] validation_brier_improved
- [ ] accuracy_guardrail_validation
- [x] accuracy_guardrail_test
- [x] top_3_guardrail_validation
- [x] top_3_guardrail_test
- [ ] modal_1_1_reduced
- [x] high_confidence_wrong_not_increased_validation
- [x] high_confidence_wrong_not_increased_test

## Challenger B — Dixon-Coles Rho Optimized

- Selected on validation only: `rho=0.1`
- Test was used only after parameter selection: `true`
- Passed all prudential guardrails: `false`
- Candidate for future combination: `false`

| Split | Accuracy | Log loss | Brier | Draw gap | Top-3 | Modal 1-1 | High-conf wrong |
|---|---:|---:|---:|---:|---:|---:|---:|
| Validation | 0.5255 | 1.0348 | 0.6220 | +0.0078 | 0.3112 | 0.1173 | 13 |
| Test | 0.4596 | 1.0555 | 0.6351 | +0.0859 | 0.3535 | 0.1717 | 8 |

Test deltas versus V0.9 (challenger minus base): log loss `+0.0143`,
Brier `+0.0074`, accuracy `+0.0000`,
top-3 `+0.0101`, absolute draw-gap
`+0.0353`, modal 1-1 `-0.5051`,
and high-confidence wrong `+4`.

### Guardrails

- [ ] test_log_loss_improves_by_0_01
- [ ] test_brier_improves_by_0_01
- [x] draw_gap_reduced_validation
- [ ] draw_gap_reduced_test
- [x] validation_log_loss_improved
- [x] validation_brier_improved
- [x] accuracy_guardrail_validation
- [x] accuracy_guardrail_test
- [ ] top_3_guardrail_validation
- [x] top_3_guardrail_test
- [x] modal_1_1_reduced
- [ ] high_confidence_wrong_not_increased_validation
- [ ] high_confidence_wrong_not_increased_test

## Comparison and honest conclusion

1. `draw_calibrated_poisson` — test log loss `1.0373`, Brier `0.6256`, all guardrails `false`
2. `dixon_coles_rho_optimized` — test log loss `1.0555`, Brier `0.6351`, all guardrails `false`

- Do not promote either challenger; promotion_recommendation remains do_not_promote_yet.
- Neither challenger passes every prudential gate for a future combination.

## Decision

- Status: `experimental`
- Promotion recommendation: `do_not_promote_yet`
- Combined challenger implemented: `false`
- Active engine replaced: `false`
- World Cup 2026 predictions modified: `false`

No challenger is promoted by this experiment. Any future combination remains
conditional on isolated guardrails and a separate human decision.
