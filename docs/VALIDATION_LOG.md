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

Commit: `634a39e Refresh historical data and feature coverage`

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

- [x] Reviewed by Jeanpaul Benga
- [x] V2.1 accepted as data-only enrichment
- [x] Decision accepted: proceed_to_v2_2_limited_retrain

### Result

- [x] Validated
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

## V2.0 — Quant Hybrid Engine with XGBoost and Optuna

Commit: `3b16043 Build quant hybrid engine with XGBoost and Optuna`

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
- [x] Active engine not replaced because model was not established
- [x] 2026 active predictions not modified
- [x] JSON artifacts validation passed
- [x] Python compilation passed
- [x] Frontend build passed
- [x] Frontend tests passed
- [x] No secret committed

### Human validation

- [x] Reviewed by Jeanpaul Benga
- [x] V2.0 accepted as technically successful
- [x] V2.0 rejected for active deployment
- [x] Overfitting concern accepted
- [x] 1-1 modal concentration concern accepted
- [x] DNB benchmark failure accepted
- [x] Data freshness limitation accepted
- [x] Decision accepted: do_not_deploy
- [x] Next step accepted: historical data refresh and feature coverage upgrade

### Observed V2.0 summary

```text
Engine:
- internal chronological rating
- 24 pre-match features
- XGBoost 3.2.0
- Optuna 4.9.0
- historical replay
- secondary markets
- Poisson score matrix
- Monte Carlo 1,500 simulations per match

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

### Result

- [ ] Validated
- [x] Validated with strong reservations
- [ ] Not validated

### Notes

Human review completed. V2.0 is accepted as a technically successful quant
rebuild but rejected for active deployment. The model demonstrates useful
infrastructure but does not generalize well enough on test, remains too
concentrated on 1-1, misses the DNB benchmark and shows overfitting. The next
phase must enrich and refresh the historical dataset before any further model
tuning or deployment attempt.

## V2.1 — Historical Data Refresh & Feature Coverage Upgrade

Commit: TBD

### Technical validation

- [x] V2.0 human validation recorded with strong reservations
- [x] API-Football coverage discovered
- [x] Recent international history refreshed
- [x] Finished matches only
- [x] Club matches excluded
- [x] Future World Cup 2026 fixtures excluded
- [x] Match statistics availability audited
- [x] Events availability audited
- [x] Lineups availability audited
- [x] Venue/neutrality availability audited
- [x] xG or xG-proxy feasibility audited
- [x] Chronological refreshed splits created
- [x] Temporal leakage audit passed
- [x] No model retrained
- [x] No Optuna rerun
- [x] No 2026 active predictions modified
- [x] JSON and documentation validation passed
- [x] Frontend build passed
- [x] Frontend tests passed
- [x] No secret committed

### Human validation

- [ ] Reviewed by Jeanpaul Benga

### Result

- [ ] Validated
- [ ] Validated with reservations
- [ ] Not validated

### Automated V2.1 result

```text
Coverage discovery:
- competitions checked: 14
- competition-seasons checked: 64
- cached discovery requests: 0

Historical refresh:
- API requests: 11
- old matches: 1,311
- refreshed matches: 3,062
- matches added: 1,751
- non-senior friendlies excluded: 429
- previous latest match: 2024-07-15
- refreshed latest match: 2026-03-31
- refreshed-history staleness: 71 days

Feature probe:
- API requests: 18
- sample matches: 6
- statistics available: 6/6
- events available: 6/6
- lineups available: 6/6
- reliable neutral flag: unavailable
- true provider xG: available on 2/12 sampled team-stat rows
- true provider xG coverage sufficient: no
- exploratory xG-proxy: technically possible
- broad proxy coverage proven: no

Decision:
- proceed_to_v2_2_limited_retrain
- model retrained: no
- Optuna rerun: no
- active 2026 predictions modified: no
```

## V2.2 — Limited Quant Retrain on Refreshed Dataset

Commit: `7d919e3 Retrain quant engine on refreshed historical data`

### Technical validation

- [x] V2.1 human validation recorded
- [x] V2.1 refreshed splits used
- [x] Internal rating V2.2 recalculated
- [x] Feature builder V2.2 created
- [x] XGBoost V2.2 trained
- [x] Optuna V2.2 run on validation only
- [x] Test evaluated once after selection
- [x] Historical replay V2.2 completed
- [x] Secondary markets V2.2 evaluated
- [x] DNB win/loss/push separated
- [x] Monte Carlo 1500 simulations completed
- [x] Coherence audit completed
- [x] V2.2 compared with V2.0
- [x] V2.2 compared with V0.9
- [x] Deployment decision documented
- [x] No future World Cup 2026 fixture used for training or selection
- [x] No secret committed

### Human validation

- [x] Reviewed by Jeanpaul Benga
- [x] V2.2 accepted as active quant engine
- [x] Deployment decision accepted: deploy_active_engine
- [x] Active engine accepted: quant_hybrid_v2.2
- [x] 72 active World Cup 2026 predictions accepted as required output
- [x] Historical test improvement accepted
- [x] DNB and secondary-market progress accepted

### Result

- [x] Validated
- [ ] Validated with reservations
- [ ] Not validated

### Automated V2.2 result

```text
Dataset: historical_splits_v2_1 only
Optuna: standard, 500 validation-only trials
Test log loss / Brier: 0.8812 / 0.5158
Train-validation log-loss gap: 0.0178
Test modal 1-1: 23.7%
Clear-favorite score alignment: 82.3%
DNB >= 0.60: 87.6% wins excluding pushes at 70.2% coverage
Decision: deploy_active_engine
Active engine replacement: yes
```

## V2.3 — Active Matrix Secondary Market Performance Audit

Commit: `a2260ae Audit active matrix secondary market performance`

### Technical validation

- [x] Active V2.2 engine audited
- [x] Matrix-derived markets separated from XGBoost direct markets
- [x] DNB wins/losses/pushes separated
- [x] Double chance audited
- [x] Over/under markets audited
- [x] BTTS audited
- [x] Team goal markets audited
- [x] Clean sheet markets audited
- [x] Winning margin markets audited
- [x] Confidence thresholds audited
- [x] Calibration buckets generated
- [x] Matrix vs XGBoost comparison generated
- [x] World Cup 2026 market audit generated
- [x] No model retrained
- [x] No Optuna rerun
- [x] No active prediction regeneration
- [x] No secret committed

### Human validation

- [x] Reviewed by Jeanpaul Benga
- [x] V2.3 accepted as market-performance audit
- [x] Matrix-derived, XGBoost direct and hybrid sources separated
- [x] Secondary-market performance accepted as useful context
- [x] Decision accepted: integrate market-performance summary into the next roadmap iteration, not as a standalone micro-iteration

### Result

- [x] Validated
- [ ] Validated with reservations
- [ ] Not validated

### Automated V2.3 result

```text
Engine audited: quant_hybrid_v2.2
Historical test matches: 460
Active World Cup 2026 fixtures: 72
Matrix DNB >= 0.60: 87.6% wins excluding pushes
Matrix DNB >= 0.60: 90.1% non-loss including pushes
Matrix DNB >= 0.60 coverage: 70.2%
Matrix over 0.5 >= 0.60: 91.7% accuracy at 100.0% coverage
No model retrained: yes
No Optuna rerun: yes
No active predictions regenerated: yes
```

## V2.4 — Active 2026 Prediction Release Candidate & Tournament Simulation

Commit: TBD

### Technical validation

- [x] V2.2 human validation recorded
- [x] V2.3 human validation recorded
- [x] Active engine quant_hybrid_v2.2 verified
- [x] Active engine deployed if missing
- [x] 72 active predictions verified
- [x] 72 release-candidate predictions generated
- [x] Score matrices validated
- [x] Top scores validated
- [x] Markets validated
- [x] Secondary-market performance summary integrated
- [x] Tournament/group simulation generated
- [x] 50,000 simulations completed
- [x] Frontend data contracts documented
- [x] Product screens spec documented
- [x] No model retrained
- [x] No Optuna rerun
- [x] No secret committed

### Human validation

- [ ] Reviewed by Jeanpaul Benga

### Result

- [ ] Validated
- [ ] Validated with reservations
- [ ] Not validated

### Automated V2.4 result

```text
Active engine: quant_hybrid_v2.2
Active engine valid: yes
Active predictions: 72
Metadata enrichment applied: yes
Model probabilities regenerated: no
Release-candidate predictions: 72
Release-candidate incoherence flags: 25
Group-stage simulations: 50,000
Teams / groups: 48 / 12
Full tournament simulation: unavailable; knockout bracket not present
```

## V2.5 — Existing UI Enrichment & Tournament Simulation Experience

Commit: b8c6d2e Enrich existing UI with active predictions and simulation

### Technical validation

- [x] Existing Angular structure audited
- [x] Group-first journey and existing match modal preserved
- [x] Existing group-based match UI preserved
- [x] Existing match modal preserved
- [x] Match cards enriched without clutter
- [x] Match modal enriched with prediction details
- [x] Secondary markets integrated in modal
- [x] DNB/push explained briefly
- [x] Top scores explained briefly
- [x] Score matrix available without clutter
- [x] Tournament simulation experience added
- [x] Group simulation probabilities displayed
- [x] Knockout limitation documented
- [x] Frontend assets validated
- [x] TypeScript contracts updated
- [x] Angular build passed
- [x] Angular tests passed
- [x] No model retrained
- [x] No Optuna rerun
- [x] No active prediction probability changed
- [x] No secret committed

### Human validation

- [x] Reviewed by Jeanpaul Benga
- [x] Existing group-based UI accepted
- [x] Existing match modal accepted
- [x] UI enrichment accepted
- [x] Tournament simulation route accepted
- [x] Decision accepted: continue roadmap without UI rebuild
- [x] Next step accepted: live results overlay, prediction scoring and creative tournament path

### Result

- [x] Validated
- [ ] Validated with reservations
- [ ] Not validated

### Automated V2.5 result

```text
Frontend asset validation: PASS
Release-candidate matches: 72
Group-stage simulations: 50,000
Teams / groups: 48 / 12
Full tournament simulation: unavailable
Angular tests: 1 existing app-creation test passed; coverage remains limited
Model retrained / Optuna rerun / active probabilities changed: no / no / no
```

## V2.6 — Live Results Overlay, Prediction Scoring & Creative Tournament Path

Commit: cd6d502 Add live results overlay and creative tournament path

### Technical validation

- [x] V2.5 human validation recorded
- [x] World Cup 2026 results fetched or status file generated
- [x] Results layer separated from pre-match predictions
- [x] Prediction-vs-result evaluation generated
- [x] Match cards show result status without clutter
- [x] Match modal shows prediction vs actual result when available
- [x] DNB win/loss/push evaluated for played matches
- [x] Secondary markets evaluated for played matches
- [x] Conditional tournament simulation generated
- [x] Finished matches locked in simulation
- [x] Knockout structure limitation documented
- [x] Official most-probable path correctly omitted because bracket is unavailable
- [x] Projected campaign proxy generated
- [x] Simulation UX enriched creatively
- [x] Angular build passed
- [x] Angular tests passed
- [x] No model retrained
- [x] No Optuna rerun
- [x] Pre-match probabilities not modified
- [x] No secret committed

### Human validation

- [x] Reviewed by Jeanpaul Benga
- [x] Live results overlay accepted as useful
- [x] Post-match evaluation accepted as useful
- [x] Conditional simulation accepted as useful
- [x] Projected campaign concept accepted
- [x] Next issue identified: result propagation and UI consistency
- [x] Next issue identified: favorite-vs-score-modal explanation

### Result

- [x] Validated
- [ ] Validated with reservations
- [ ] Not validated

### Automated V2.6 result

```text
Results source: API-Football, one cached request
Fixtures: 72
Finished / live / not started: 1 / 0 / 71
Evaluated finished matches: 1
Sample size too small: yes
Exact score / Top-3 / Top-5 / 1X2 hits: 0 / 0 / 1 / 1
DNB wins / losses / pushes: 1 / 0 / 0
Conditioned simulations: 50,000
Finished matches locked / future simulated: 1 / 71
Knockout structure available: no
Projected campaign proxy leader: Spain
Angular build and tests: passed
Model retrained / Optuna rerun / pre-match probabilities modified: no / no / no
```

## V2.7 — Result Consistency, Live Group Standings & Coherent Prediction Presentation

Commit: b43ac9e Fix result consistency and prediction coherence

### Technical validation

- [x] V2.6 human validation recorded
- [x] Unified match state view model generated
- [x] Results propagated to cards
- [x] Results propagated to modal
- [x] Live group standings generated from official results
- [x] Mexico 2-0 South Africa reflected in Group A
- [x] Matchday/status normalized
- [x] Score modal vs 1X2 favorite explanation added
- [x] Score consistent with favorite computed
- [x] Simulation page uses live standings
- [x] Result consistency validation passed
- [x] Angular build passed
- [x] Angular tests passed
- [x] No model retrained
- [x] No Optuna rerun
- [x] Pre-match probabilities not modified
- [x] No secret committed

### Human validation

- [x] Reviewed by Jeanpaul Benga
- [x] Result propagation accepted
- [x] Live group standings accepted
- [x] Cards and modal consistency accepted
- [x] Score modal vs 1X2 favorite explanation accepted
- [x] Next issue identified: score matrix appears too conservative
- [x] Next roadmap iteration accepted: score matrix realism and favorite strength calibration

### Result

- [x] Validated
- [ ] Validated with reservations
- [ ] Not validated

### Automated V2.7 result

```text
Unified match states: 72
Finished official results reflected: 1
Live standings groups: 12
Mexico: played 1, wins 1, goals 2-0, difference +2, points 3
South Africa: played 1, losses 1, goals 0-2, difference -2, points 0
Normalized matchdays: 72
Modal-score / 1X2-favorite divergences explained: 25
Result consistency validation: PASS
Angular build and tests: passed
Model retrained / Optuna rerun / pre-match probabilities modified: no / no / no
```

## V2.8 — Score Matrix Realism & Favorite Strength Calibration

Commit: 449b2a6 Audit and calibrate score matrix realism

### Technical validation

- [x] V2.7 human validation recorded
- [x] Score matrix realism strategy created
- [x] World Cup 2026 modal score distribution audited
- [x] Historical test modal score distribution audited
- [x] Strong favorite buckets audited
- [x] Spain vs Cape Verde case audited
- [x] Conservatism diagnosis produced
- [x] Causes classified
- [x] Matrix challengers evaluated
- [x] 1X2 guardrails checked
- [x] DNB guardrails checked
- [x] Over/under guardrails checked
- [x] Candidate generated if objectively better
- [x] No active prediction replacement without validation
- [x] Angular build passed if frontend changed
- [x] Angular tests passed if frontend changed
- [x] No model retrained
- [x] No Optuna rerun
- [x] Active prediction probabilities not modified
- [x] No secret committed

### Human validation

- [x] Reviewed by Jeanpaul Benga
- [x] Score matrix conservatism diagnosis accepted
- [x] Historical evidence accepted
- [x] Spain vs Cape Verde case accepted as representative
- [x] Candidate A_gap_alpha_1.5_beta_0.75 accepted as useful non-active candidate
- [x] Decision accepted: do not promote automatically
- [x] Next roadmap iteration accepted: compare active matrix vs candidate projection in product and simulation

### Result

- [x] Validated
- [ ] Validated with reservations
- [ ] Not validated

### Automated V2.8 result

```text
Conservatism detected: yes
World Cup modal 0-0/1-0/0-1/1-1: 71/72
World Cup modal 3+ goals: 0/72
Historical actual/modal 3+ goals: 226/460 versus 10/460
Best challenger: A_gap_alpha_1.5_beta_0.75
Candidate status: generated, not active
Active hybrid probabilities modified: no
Model retrained / Optuna rerun: no / no
```

## V2.9 — Dual Matrix Display & Candidate Simulation Comparison

Commit: 4858457 Compare active and alternative score matrices

### Technical validation

- [x] V2.8 human validation recorded
- [x] Dual matrix strategy created
- [x] Active vs candidate comparison generated
- [x] Spain vs Cape Verde comparison documented
- [x] Candidate group simulation generated
- [x] Active vs candidate simulation comparison generated
- [x] Candidate projected campaign generated
- [x] Simulation UI enriched with active/alternative comparison
- [x] Match modal enriched with non-active alternative projection
- [x] Candidate clearly labelled as non-active
- [x] Active predictions not replaced
- [x] Dual matrix validation passed
- [x] Angular build passed
- [x] Angular tests passed
- [x] No model retrained
- [x] No Optuna rerun
- [x] No secret committed

### Human validation

- [x] Reviewed by Jeanpaul Benga
- [x] Active vs candidate comparison accepted
- [x] Candidate simulation comparison accepted
- [x] Projection alternative accepted as non-active
- [x] Active predictions remain official
- [x] Next roadmap iteration accepted: operational matchday refresh pipeline

### Result

- [x] Validated
- [ ] Validated with reservations
- [ ] Not validated

## V2.10 — Operational Matchday Refresh Pipeline

Commit: e5bd67e Add operational matchday refresh pipeline

### Technical validation

- [x] V2.9 human validation recorded
- [x] Matchday refresh strategy created
- [x] Single refresh pipeline created
- [x] Results refresh integrated
- [x] Prediction evaluation integrated
- [x] Live standings refresh integrated
- [x] Match state view model refresh integrated
- [x] Active conditioned simulation integrated
- [x] Candidate simulation integrated
- [x] Active/candidate comparison integrated
- [x] Projected campaigns integrated
- [x] Refresh manifest generated
- [x] Artifact hygiene audit generated
- [x] Runbook created
- [x] Refresh validation passed
- [x] Active predictions unchanged
- [x] No model retrained
- [x] No Optuna rerun
- [x] Angular build passed if frontend changed
- [x] Angular tests passed if frontend changed
- [x] No secret committed

### Human validation

- [x] Reviewed by Jeanpaul Benga
- [x] Matchday refresh pipeline accepted
- [x] 11-step refresh accepted
- [x] Fetch/no-fetch/dry-run workflow accepted
- [x] Artifact hygiene accepted
- [x] Active predictions remained unchanged
- [x] Next roadmap iteration accepted: creative tournament simulation experience

### Result

- [x] Validated
- [ ] Validated with reservations
- [ ] Not validated

## V2.11 — Creative Tournament Experience Upgrade

Commit: 92aac5a Upgrade creative tournament simulation experience

### Technical validation

- [x] V2.10 human validation recorded
- [x] Creative tournament strategy created
- [x] Creative tournament aggregate generated
- [x] Tournament leader computed
- [x] Top contenders computed
- [x] Group storylines generated
- [x] Locked result impact integrated
- [x] Active vs alternative interpretation generated
- [x] /simulation hero upgraded
- [x] Projected Campaign displayed honestly
- [x] Top contenders displayed
- [x] Open groups displayed
- [x] Active vs alternative comparison improved
- [x] Proxy champion clearly labelled non-official
- [x] Bracket not invented
- [x] Creative experience validation passed
- [x] Angular build passed
- [x] Angular tests passed
- [x] Active predictions unchanged
- [x] Candidate not promoted
- [x] No retrain
- [x] No Optuna rerun
- [x] No secret committed

### Human validation

- [x] Reviewed by Jeanpaul Benga
- [x] Creative simulation experience accepted
- [x] Projected campaign accepted as non-official proxy
- [x] Active vs alternative simulation comparison accepted
- [x] Group storylines accepted
- [x] V2.11 accepted as roadmap progress
- [x] Next roadmap iteration accepted: prediction history, transparency and model scoreboard

### Result

- [x] Validated
- [ ] Validated with reservations
- [ ] Not validated

## V2.12 — Prediction History, Public Transparency & Model Scoreboard

Commit: TBD

### Technical validation

- [x] V2.11 human validation recorded
- [x] Prediction history strategy created
- [x] Prediction history generated
- [x] Model scoreboard generated
- [x] Performance timeline generated
- [x] Public transparency copy generated
- [x] Transparency UI section added
- [x] Match modal history summary added if appropriate
- [x] DNB wins/losses/pushes separated
- [x] Small sample warning implemented
- [x] Active vs alternative explanation implemented
- [x] Prediction history validation passed
- [x] Angular build passed
- [x] Angular tests passed
- [x] Active predictions unchanged
- [x] Candidate not promoted
- [x] No retrain
- [x] No Optuna rerun
- [x] No secret committed

### Human validation

- [ ] Reviewed by Jeanpaul Benga

### Result

- [ ] Validated
- [ ] Validated with reservations
- [ ] Not validated
