# Validation Log

## V0.2 / V0.2.1 — Data Foundation + Manual Validation Checklists

Date: 2026-06-10
Validator: Jeanpaul Benga
Commit: `e3913e7 Add manual validation checklists`

### Technical validation

- [x] Backend pipeline passed
- [x] JSON snapshots generated
- [x] Backend snapshots match Angular assets
- [x] Angular build passed
- [x] Angular tests passed
- [x] Forbidden artifacts check passed
- [x] Data provenance files present
- [x] Mock data clearly identified as non-real data

### Manual visual validation

- [ ] Home page checked
- [ ] Data status section checked
- [ ] Provenance badges checked
- [ ] Match cards checked
- [ ] Prediction probabilities checked
- [ ] Score matrix checked
- [ ] Market summary checked
- [ ] Prediction history checked
- [ ] Responsible notice checked
- [ ] Browser console checked
- [ ] Network JSON HTTP 200 checked

### Result

- [ ] Validated
- [ ] Validated with reservations
- [ ] Not validated

### Notes

Technical checks completed on 2026-06-10. The backend pipeline generated all
expected snapshots, JSON validation passed, backend snapshots matched Angular
assets, and the Angular build and tests passed with Node `22.22.3`.

The broad forbidden-artifacts command returned
`backend/scripts/build_snapshots.py` because its filename contains `build`.
A path-aware check confirmed that no forbidden build directory or artifact is
tracked.

Manual visual validation still requires human review before moving to V0.3.

### Issues to fix before next phase

- Complete the manual visual validation checklist and record the human decision.

## V0.3.1 — Team Identity Mapping

Date: 2026-06-10
Validator: Jeanpaul Benga
Commit: `8254b2b Add team identity mapping for API-Football and Elo`

### Technical validation

- [x] `build_team_identity_map.py` passed
- [x] `validate_team_mappings.py` passed
- [x] `team_identity_map.json` present
- [x] `team_aliases.json` present
- [x] `unmapped_teams.json` present
- [x] `team_mapping_report.json` present
- [x] `team_mapping_status.json` present
- [x] API-Football teams count checked
- [x] Elo teams count checked
- [x] coverage checked
- [x] duplicate checks passed
- [x] `build_snapshots.py` passed
- [x] Angular build passed
- [x] Angular tests passed
- [x] secret scan passed
- [x] forbidden artifacts check passed

### Mapping summary

```text
API-Football teams: 48
Elo teams: 244
Mapped: 48
Auto validated: 48
Needs review: 0
Unmapped API teams: 0
Coverage: 100 %
Status: PASS
Exact mappings: 42
Alias mappings: 6
```

### Alias mappings requiring human review

```text
1. API-Football: Czech Republic → Elo: Czechia | code: CZE | method: alias | confidence: 0.98 | Elo: 1740, rank: 35
2. API-Football: Türkiye → Elo: Turkey | code: TUR | method: alias | confidence: 0.98 | Elo: 1911, rank: 13
3. API-Football: Bosnia & Herzegovina → Elo: Bosnia and Herzegovina | code: BIH | method: alias | confidence: 0.98 | Elo: 1595, rank: 65
4. API-Football: Congo DR → Elo: DR Congo | code: CGO | method: alias | confidence: 0.98 | Elo: 1652, rank: 55
5. API-Football: Cape Verde Islands → Elo: Cape Verde | code: CPV | method: alias | confidence: 0.98 | Elo: 1578, rank: 68
6. API-Football: USA → Elo: United States | code: USA | method: alias | confidence: 0.98 | Elo: 1726, rank: 38
```

### Manual visual validation

- [ ] Alias mappings checked manually
- [ ] Sensitive aliases checked
- [ ] Elo ratings association checked
- [ ] Angular mapping summary checked
- [ ] Documentation checked

### Result

- [ ] Validated
- [ ] Validated with reservations
- [ ] Not validated

### Notes

Technical validation completed on 2026-06-10. Mapping generation, structural
validation, JSON checks, duplicate checks, snapshot generation, Angular build
and Angular tests passed.

The broad forbidden-artifacts command returned
`backend/scripts/build_snapshots.py` and
`backend/scripts/build_team_identity_map.py` because their filenames contain
`build`. A path-aware tracked-files check confirmed that no forbidden build
directory or artifact is versioned.

The secret scan returned expected source-code references to
`API_FOOTBALL_KEY` and `x-apisports-key`. A fixed-string scan confirmed that
the real API key has zero tracked matches.

Manual validation still requires human review before integrating Elo into the
prediction model.

### Issues to fix before next phase

- To be completed after human review.

## V0.4 — Elo Model Experiment

Date: 2026-06-10
Validator: Jeanpaul Benga
Commit: `08a0a08 Add experimental Elo-adjusted prediction model`

### Technical validation

- [x] Team mapping validation passed
- [x] Baseline predictions available
- [x] Elo predictions available
- [x] Model comparison available
- [x] Baseline remains unchanged
- [x] Elo remains experimental
- [x] JSON files valid
- [x] No probability aberration detected
- [x] Max absolute delta below `0.05`
- [x] Impact levels are low
- [x] Documentation exists
- [x] Missing Elo rating falls back exactly to baseline expected goals
- [x] Score-matrix probabilities remain in `[0, 1]` and normalized
- [x] Market probabilities remain in `[0, 1]`
- [x] 1X2 markets remain normalized
- [x] Angular build passed
- [x] Angular tests passed
- [x] Secret scan passed
- [x] Forbidden artifacts check passed

### Experiment summary

```text
Matches compared: 3
Elo available: 3/3
Impact none: 0
Impact low: 3
Impact medium: 0
Impact high: 0
Maximum absolute market delta: 0.0389
Elo weight: 0.20
Elo factor clamp: ±0.35
Backtesting model: baseline only
```

### Manual visual validation

- [x] Model comparison inspected manually
- [x] France vs Senegal delta reviewed
- [x] Brazil vs Japan delta reviewed
- [x] Canada vs Morocco delta reviewed
- [x] Top scores baseline vs Elo checked
- [x] Elo ratings association checked
- [x] Deltas judged reasonable
- [x] Experimental status accepted

### Observed comparison summary

```text
France vs Senegal:
- Elo: 2063 vs 1860
- Top score baseline: 2-0
- Top score Elo: 2-0
- Impact: low
- Largest delta: home_win +0.0389

Brazil vs Japan:
- Elo: 1991 vs 1906
- Top score baseline: 2-0
- Top score Elo: 2-0
- Impact: low
- Largest delta: home_win +0.0239

Canada vs Morocco:
- Elo: 1788 vs 1827
- Top score baseline: 1-1
- Top score Elo: 1-1
- Impact: low
- Largest delta: away_win +0.0123
```

### Result

- [x] Validated
- [ ] Validated with reservations
- [ ] Not validated

### Notes

Human review completed. Elo impact is moderate and coherent for the current
V0.4 experiment. The baseline model remains preserved, and Elo is accepted as
an experimental parallel model only.

### Issues to fix before next phase

- Keep Elo marked as experimental.
- Do not make Elo the default model without additional backtesting.
- Future phases must compare predictive quality before promoting Elo.

## V0.5 — API-Football Active Source with Prototype Engine

Date: 2026-06-10
Validator: technical automation only

### Technical validation

- [x] API-Football fetch completed without endpoint errors
- [x] 72 fixtures and 48 teams normalized
- [x] API-Football fixtures activated in `matches.json`
- [x] Baseline and Elo prototype predictions generated
- [x] Model comparison generated
- [x] Engine marked experimental and not historically calibrated
- [x] Future fixtures marked real and future
- [x] Backtesting marked `not_evaluable`
- [x] No mock results used for real future fixtures
- [x] Mock source compatibility retained
- [x] Prediction probabilities and 1X2 markets normalized
- [x] Angular build passed
- [x] Angular tests passed
- [x] Secret and artifact audit passed

### Manual visual validation

- [ ] Real fixtures checked
- [ ] Active API-Football source checked
- [ ] Prototype-engine warning checked
- [ ] No-false-backtesting message checked
- [ ] Baseline/Elo predictions and comparison checked

### Result

- [ ] Validated
- [ ] Validated with reservations
- [ ] Not validated

### Notes

Technical validation produced `72` real future fixtures, `48` teams, `72`
baseline predictions, `72` Elo predictions and `72` model comparisons.
Standings and rounds were fetched successfully. The active-source backtesting
snapshot contains no evaluated result and is explicitly marked
`not_evaluable`.

The prototype uses neutral baseline inputs when historical features are
unavailable. These inputs and every generated prediction are marked as
experimental and not historically calibrated.

## V0.5.1 — Real Data Only + UX Review

Date: 2026-06-10
Validator: technical automation only

### Technical validation

- [x] API-Football confirmed as the default source without silent mock fallback
- [x] enriched teams, groups, standings and group strengths generated
- [x] prediction diversity audit generated and reviewed
- [x] 72 baseline and 72 Elo modal scores honestly reported as `1-1`
- [x] grouped Angular UX and match-detail modal built
- [x] Angular build passed
- [x] Angular tests passed
- [x] secret and artifact audit passed

### Manual visual validation

- [ ] group tabs and compact fixture cards checked
- [ ] team logos, standings and group strengths checked
- [ ] modal detail and close interactions checked
- [ ] prediction uniformity warning checked
- [ ] mobile and desktop rendering checked

### Result

- [ ] Validated
- [ ] Validated with reservations
- [ ] Not validated

### Notes

V0.5 remains unvalidated. V0.5.1 technical checks do not replace the requested
human review and do not introduce fake backtesting.

The standalone recycled Python tests were not run because `pytest` is not
installed in the system Python environment. The active backend generation
pipeline, Angular production build and Angular test suite passed.

## V0.6 — Prediction Engine Discovery & Future Blueprint

Commit: TBD

### Technical validation

- [x] Current engine audit completed
- [x] Engine reference inventory completed
- [x] Historical dependency review completed
- [x] Historical data strategy created
- [x] Future engine blueprint created
- [x] ADR created
- [x] No prediction logic changed
- [x] No generated prediction values changed intentionally

### Human validation

- [ ] Reviewed by Jeanpaul Benga

### Result

- [ ] Validated
- [ ] Validated with reservations
- [ ] Not validated

### Notes

The recommended next implementation phase is **V0.7 — Historical Data
Acquisition Spike**. V0.6 changes documentation and adds a deterministic
reference-inventory script only; it does not replace, calibrate or rerun the
prediction engine.

## V0.7 — Historical Data Acquisition Spike

Commit: TBD

### Technical validation

- [x] API-Football historical exploration completed
- [x] Historical fixtures fetched
- [x] Historical matches normalized
- [x] Historical dataset audit completed
- [x] Future 2026 fixtures excluded from historical dataset
- [x] No model training introduced
- [x] No prediction logic changed
- [x] No fake backtesting introduced
- [x] No secret committed

### Human validation

- [ ] Reviewed by Jeanpaul Benga

### Result

- [ ] Validated
- [ ] Validated with reservations
- [ ] Not validated

### Notes

The controlled exploration executed `5` API requests and found `872` finished
fixtures across five checked international competition seasons. The
conservative fetch executed `3` requests and normalized `192` real finished
World Cup fixtures from 2014, 2018 and 2022. The dataset contains no future
2026 fixture, duplicate ID or missing score.

Dataset sufficiency is rated `medium`: useful for a controlled experimental
baseline, but insufficient for the final advanced engine. No model was trained
and no backtesting was performed.

## V0.8 — Expanded Historical Dataset & Chronological Split

Commit: e2912d1 Expand historical international dataset and create chronological splits

### Technical validation

- [x] Expanded competition exploration completed
- [x] Expanded historical fetch completed
- [x] Expanded historical matches normalized
- [x] Historical dataset audit completed
- [x] Chronological split created
- [x] 2026 future fixtures excluded
- [x] Club competitions excluded
- [x] No model training introduced
- [x] No prediction logic changed
- [x] No fake backtesting introduced
- [x] No secret committed

### Human validation

- [x] Reviewed by Jeanpaul Benga
- [x] Expanded historical dataset accepted
- [x] Dataset larger than V0.7 accepted
- [x] Competitions beyond World Cup accepted
- [x] Chronological split accepted
- [x] 2026 future fixtures excluded
- [x] No model training introduced
- [x] Dataset sufficiency accepted as medium
- [x] Dataset accepted for first calibration experiments only

### Observed dataset summary

```text
Exploration:
- Competitions explored: 14
- API requests executed: 43
- Finished fixtures detected: 5,901

Expanded dataset:
- Matches: 1,311
- Teams: 168
- Competitions: 6
- Date range: 2014 to 2024
- Future 2026 fixtures: excluded
- Duplicate fixtures: none

Chronological split:
- Train: 917
- Validation: 196
- Test: 198
- Split type: strict chronological

Status:
- Dataset sufficiency: medium
- Intended use: first calibration experiments only
- Motor/prediction logic changed: no
```

### Result

- [x] Validated
- [ ] Validated with reservations
- [ ] Not validated

### Notes

Human review completed. The expanded historical dataset is accepted as a
stronger experimental base than V0.7. It includes 1,311 real international
matches from 2014 to 2024 across 6 competitions and 168 teams, with a strict
chronological split. The dataset remains medium-sufficiency and should be used
only for first calibration experiments, not as a final robust training source.

## V0.9 — First Calibration Experiment on Historical Dataset

Commit: a0814c0 Add first historical calibration experiment

### Technical validation

- [x] Historical calibrated model trained
- [x] Validation predictions generated
- [x] Test predictions generated
- [x] Validation metrics generated
- [x] Test metrics generated
- [x] Prototype comparison generated
- [x] No 2026 predictions modified
- [x] Current engine not replaced
- [x] Results documented honestly
- [x] No secret committed

### Human validation

- [x] Reviewed by Jeanpaul Benga
- [x] Calibrated model accepted as experimental
- [x] Validation metrics reviewed
- [x] Test metrics reviewed
- [x] Prototype comparison reviewed
- [x] Improvement over prototype acknowledged
- [x] Promotion recommendation accepted as do_not_promote_yet
- [x] Current engine remains unchanged
- [x] 2026 predictions remain unchanged

### Observed calibration summary

```text
Model:
- Type: calibrated Simple Poisson
- Train matches: 917
- Train teams: 159
- Smoothing: weight 8, min team matches 5
- xG bounds: 0.2–3.5
- Status: experimental
- Historically calibrated: true

Validation:
- Matches: 196
- Accuracy 1X2: 53.06%
- Log loss: 1.0374
- Brier: 0.6232
- Exact score accuracy: 9.18%
- Top-3 exact score hit rate: 32.14%

Test:
- Matches: 198
- Accuracy 1X2: 45.96%
- Log loss: 1.0412
- Brier: 0.6277
- Exact score accuracy: 15.15%
- Top-3 exact score hit rate: 34.34%

Comparison vs neutral prototype:
- Validation accuracy delta: +9.69 pts
- Validation log loss delta: -0.0428
- Validation Brier delta: -0.0318
- Test accuracy delta: +5.56 pts
- Test log loss delta: -0.0625
- Test Brier delta: -0.0420
- Test exact score delta: -0.51 pt
- Promotion recommendation: do_not_promote_yet
```

### Result

- [x] Validated
- [ ] Validated with reservations
- [ ] Not validated

### Notes

Human review completed. The first calibrated Simple Poisson model improves over
the neutral prototype on validation and test for 1X2 accuracy, log loss and
Brier score. However, exact-score performance is not consistently better and
the model remains experimental. The recommendation `do_not_promote_yet` is
accepted. The current production prototype engine and World Cup 2026
predictions remain unchanged.

### Next step

Analyze segmented errors before creating a second challenger or promoting any
calibrated model.

## V1.0 — Calibration Error Analysis & Segmentation

Commit: ecc025a Analyze calibration errors and segmentation

### Technical validation

- [ ] Error analysis generated
- [ ] Competition segmentation completed
- [ ] Season segmentation completed
- [ ] Team segmentation completed
- [ ] Bias analysis completed
- [ ] Score distribution analysis completed
- [ ] Worst matches identified
- [ ] Recommendations documented
- [ ] No model retrained
- [ ] No 2026 predictions modified
- [ ] No promotion decision changed
- [ ] No secret committed

### Human validation

- [x] Reviewed by Jeanpaul Benga
- [x] Error analysis accepted
- [x] Competition segmentation reviewed
- [x] Season segmentation reviewed
- [x] Team segmentation reviewed
- [x] Draw bias reviewed
- [x] Favorite bias reviewed
- [x] Score distribution reviewed
- [x] Worst matches reviewed
- [x] Promotion recommendation accepted as do_not_promote_yet
- [x] V1.1 priorities accepted

### Result

- [x] Validated
- [ ] Validated with reservations
- [ ] Not validated

### Notes

Human review completed. V1.0 confirms that the calibrated Simple Poisson v0.9
improves over the neutral prototype but remains unsuitable for promotion. The
main issues are severe draw underprediction, excessive `1-1` modal-score
concentration, underestimation of high-scoring matches and fragile favorite
confidence. V1.1 should focus on challenger design around draw calibration,
score diversity, competition effects, recent form/time decay, Elo prior
integration and better treatment of low-sample teams.

## V1.1 — Improved Calibrated Engine Challenger Design

Commit: 617e512 Design improved calibrated engine challengers

### Technical validation

- [x] V1.0 human validation recorded
- [x] Challenger design document created
- [x] Evaluation protocol created
- [x] Challenger design JSON created
- [x] Promotion rules documented
- [x] No model implemented
- [x] No model retrained
- [x] No 2026 predictions modified
- [x] No promotion decision changed
- [x] No secret committed

### Human validation

- [x] Reviewed by Jeanpaul Benga
- [x] Challenger design accepted
- [x] Draw calibration priority accepted
- [x] Dixon-Coles rho priority accepted
- [x] Competition-weighted challenger accepted
- [x] Time-decay challenger accepted
- [x] Elo-prior challenger accepted
- [x] Combined challenger deferred
- [x] Promotion rules accepted
- [x] V1.2 can implement isolated challengers

### Observed design summary

```text
Challengers:
- Draw-Calibrated Poisson
- Dixon-Coles Rho Optimized
- Competition-Weighted Poisson
- Time-Decay Poisson
- Elo-Prior Poisson
- Combined Candidate deferred

Priorities:
- First: Draw calibration
- Second: Dixon-Coles rho optimization

Evaluation:
- 13 mandatory metrics
- Validation and test required
- Human validation required before promotion
- Test log loss improvement threshold: >= 0.01
- Test Brier improvement threshold: >= 0.01

Status:
- Design only
- No model implemented
- No model retrained
- 2026 predictions unchanged
- Promotion recommendation remains do_not_promote_yet
```

### Result

- [x] Validated
- [ ] Validated with reservations
- [ ] Not validated

### Notes

Human review completed. V1.1 is accepted as a design-only step. V1.2 can
implement isolated challengers one by one, starting with draw calibration and
Dixon-Coles rho. The combined challenger remains deferred until isolated tests
prove which components improve the model. No promotion is allowed without
validation and the default recommendation remains `do_not_promote_yet`.

## V1.2 — Isolated Calibration Challenger Experiments

Commit: dde8e23 Evaluate isolated calibration challengers

### Technical validation

- [x] Draw-calibrated challenger implemented
- [x] Dixon-Coles rho challenger implemented
- [x] Parameters selected on validation only
- [x] Test used only for final evaluation
- [x] V0.9 comparison generated
- [x] Guardrails evaluated
- [x] No combined challenger implemented
- [x] No model promoted
- [x] No 2026 predictions modified
- [x] No main engine replacement
- [x] No secret committed

### Human validation

- [x] Reviewed by Jeanpaul Benga
- [x] Draw-calibrated challenger reviewed
- [x] Dixon-Coles rho challenger reviewed
- [x] Guardrail failures accepted
- [x] No challenger accepted for promotion
- [x] No challenger accepted for combination
- [x] Current engine remains unchanged
- [x] 2026 predictions remain unchanged

### Observed challenger summary

```text
Draw-Calibrated Poisson:
- selected draw_factor: 1.10
- validation log loss: 1.0409
- validation Brier: 0.6252
- validation accuracy: 52.04%
- test log loss: 1.0373
- test Brier: 0.6256
- test accuracy: 46.46%
- test delta vs V0.9 log loss: -0.0039
- test delta vs V0.9 Brier: -0.0021
- test draw gap delta: -0.0190
- guardrails: failed

Dixon-Coles Rho Optimized:
- selected rho: 0.10
- validation log loss: 1.0348
- validation Brier: 0.6220
- validation modal 1-1: 11.73%
- test log loss: 1.0555
- test Brier: 0.6351
- test modal 1-1: 17.17%
- test delta vs V0.9 log loss: +0.0143
- test delta vs V0.9 Brier: +0.0074
- test modal 1-1 delta: -0.5051
- guardrails: failed

Decision:
- best challenger: Draw-Calibrated Poisson, but not promising enough
- promotion recommendation: do_not_promote_yet
- candidate for combination: none
- combined challenger implemented: no
```

### Result

- [ ] Validated
- [x] Validated with reservations
- [ ] Not validated

### Notes

Human review completed. V1.2 is technically valid and useful, but neither
isolated challenger passes the promotion guardrails. Draw calibration slightly
improves test log loss and Brier but not enough to qualify, and it degrades
validation. Dixon-Coles rho strongly reduces 1-1 modal concentration but
regresses on test and increases high-confidence wrong predictions. No
challenger should be promoted or combined yet. The next work should focus on
improving upstream xG generation through competition weighting, time decay,
Elo priors and better low-sample team handling.

## V1.3 — Upstream xG Feature Challenger Design

Commit: 449fc2f Design upstream xG feature challengers

### Technical validation

- [x] V1.2 result incorporated
- [x] Upstream xG challenger design created
- [x] V1.4 experiment protocol created
- [x] Feature availability inspected
- [x] Temporal leakage risks documented
- [x] No model implemented
- [x] No model retrained
- [x] No 2026 predictions modified
- [x] No promotion decision changed
- [x] No secret committed

### Human validation

- [x] Reviewed by Jeanpaul Benga
- [x] Upstream xG direction accepted
- [x] Competition-weighted xG challenger accepted
- [x] Time-decay xG challenger accepted
- [x] Elo-prior xG challenger accepted with temporal leakage restriction
- [x] Low-sample fallback challenger accepted
- [x] Combined upstream challenger deferred
- [x] V1.4 protocol accepted
- [x] No-promotion boundary accepted

### Observed design summary

```text
V1.3 diagnosis:
- V1.2 post-probability corrections were insufficient.
- Future improvements should target upstream xG generation.

Feature availability:
- historical matches: 1,311
- teams: 168
- competitions: 6
- Elo coverage: 162/168 teams
- Elo limitation: current/static snapshot only
- low-sample teams: <5 = 17, <8 = 39, <10 = 59

V1.4 challengers:
- Competition-Weighted xG
- Time-Decay xG
- Elo-Prior xG
- Low-Sample Fallback xG
- Combined upstream candidate deferred

Temporal constraint:
- current/static Elo cannot justify promotion on historical backtests.
- Elo must be historical pre-match or explicitly marked leakage-risk.

Status:
- Design only
- No model implemented
- No model retrained
- 2026 predictions unchanged
- Promotion recommendation remains do_not_promote_yet
```

### Result

- [x] Validated
- [ ] Validated with reservations
- [ ] Not validated

### Notes

Human review completed. V1.3 is accepted as a design-only step. The next
implementation phase should focus on isolated upstream xG challengers:
competition weighting, time decay, Elo prior only with strict
temporal-leakage handling, and low-sample fallback. The combined upstream
challenger remains deferred until isolated components prove value. No model is
promoted and the default recommendation remains `do_not_promote_yet`.

## V1.4 — Upstream xG Isolated Challenger Experiments

Commit: TBD

### Technical validation

- [ ] Competition-weighted xG implemented
- [ ] Time-decay xG implemented
- [ ] Low-sample fallback xG implemented
- [ ] Elo-prior handled with temporal leakage restriction
- [ ] Parameters selected on validation only
- [ ] Test used only for final evaluation
- [ ] V0.9 comparison generated
- [ ] Segment reports generated
- [ ] Guardrails evaluated
- [ ] No combined challenger implemented
- [ ] No model promoted
- [ ] No 2026 predictions modified
- [ ] No main engine replacement
- [ ] No secret committed

### Human validation

- [ ] Reviewed by Jeanpaul Benga

### Result

- [ ] Validated
- [ ] Validated with reservations
- [ ] Not validated

## V2.0 — Quant Hybrid Engine with Active Deployment

Commit: TBD

### Technical validation

- [x] Prompt analysis completed
- [x] XGBoost dependency added
- [x] Optuna dependency added
- [x] Dependency imports validated
- [x] Internal chronological rating implemented
- [x] Feature builder uses pre-match data only
- [x] XGBoost models implemented
- [x] Optuna validation-only optimization implemented
- [x] Historical replay implemented
- [x] Monte Carlo simulation implemented with 1500 simulations per match
- [x] Secondary market evaluation generated
- [x] DNB metrics distinguish wins, losses and pushes
- [x] Favorite-score alignment audited
- [x] Deployment decision documented
- [x] Active engine replaced if model established
- [x] 2026 predictions regenerated if deployed
- [x] JSON artifacts validation passed
- [x] Python compilation passed
- [x] Frontend build passed
- [x] Frontend tests passed
- [x] No secret committed

### Human validation

- [ ] Reviewed by Jeanpaul Benga

### Result

- [ ] Validated
- [ ] Validated with reservations
- [ ] Not validated

### Automated result

```text
Deployment decision: do_not_deploy
Validation log loss / Brier: 0.9602 / 0.5694
Test log loss / Brier: 1.0513 / 0.6367
Test delta vs V0.9 log loss / Brier: +0.0101 / +0.0090
Test modal 1-1: 47.5%
Clear-favorite score alignment: 59.5%
Train-to-validation log-loss gap: 0.2122
DNB >= 0.60 coverage: 62.6%
DNB >= 0.60 win rate excluding pushes: 78.0%
DNB >= 0.60 non-loss including pushes: 85.5%
Active history staleness: 696 days
Active 2026 predictions modified by V2.0: no
```

V2.0 is technically reproducible but not established. It overfits validation,
regresses against V0.9 on final test, remains too concentrated on modal `1-1`,
and lacks sufficiently fresh historical inputs for responsible active 2026
deployment.
