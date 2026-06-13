# Future Engine Blueprint

## Decision boundary

V0.6 does not replace the current engine. It defines a staged path from a
workflow prototype to a historically calibrated engine while preserving
published snapshot contracts and honest model metadata.

## Level comparison

| Dimension | 1. Current Prototype Engine | 2. Reconstructed Historical Engine | 3. Future Advanced Engine |
|---|---|---|---|
| Status | Active, experimental, not calibrated | Recommended realistic intermediate target | Advanced, non-immediate research target |
| Inputs | Neutral `1.35 / 1.35`, current mapped Elo | Chronological results, attack/defence strength, neutral/home context, pre-match Elo | Level 2 plus dynamic Elo, recent form, importance and consistent advanced stats |
| Model | Simple Poisson/Dixon-Coles; separate bounded Elo variant | Fitted Poisson/Dixon-Coles with team attack/defence parameters and Elo prior/feature | Hybrid statistical/ML model with calibrated probability outputs |
| Parameters | Hard-coded blend, `rho=-0.05`, Elo weight `0.20`, clamp `±0.35` | Fitted decay, attack/defence, neutral advantage, rho and Elo contribution | Tuned feature sets, model families, ensembles and calibration layers |
| Data | Future 2026 fixtures and static ratings | Finished international matches ordered by date | Broader versioned history plus robust optional features |
| Training | None | Chronological fitting, likely SciPy or Optuna | Automated tuning and model-family comparison |
| Backtesting | None for real future fixtures; mock signal checks only | Expanding-window out-of-sample evaluation | Continuous post-match monitoring and champion/challenger evaluation |
| Metrics | Diversity audit and market deltas | Negative log likelihood/log loss, Brier score, RPS and calibration | Level 2 plus segmented performance, drift and calibration monitoring |
| Output JSON | Existing stable snapshots | Same contracts with new explicit model version/calibration metadata | Same or deliberately versioned contracts |
| Main risk | Uniform, misleadingly precise-looking predictions | Leakage, sparse teams, unstable parameters and poor competition weighting | Complexity without enough data; opaque gains and maintenance cost |

## Level 1 — Current Prototype Engine

The current engine uses equal baseline xG for all 72 fixtures, a simple
Poisson/Dixon-Coles score matrix and a moderate separate Elo adjustment. It has
no fitting or historical calibration. Baseline and Elo both return `1-1` as
the modal score for `72/72` fixtures.

Its value is architectural: it proves the full product workflow, stable JSON
contracts, provenance, group UX and transparent audit behavior. It must remain
visibly experimental until replaced through measured evidence.

## Level 2 — Reconstructed Historical Engine

### Inputs

- chronologically ordered finished international matches;
- stable team identities;
- competition and importance category;
- neutral-site or home-context indicator;
- pre-match Elo or a chronologically reconstructed Elo;
- time-decayed historical goals.

### Model

Fit a Poisson/Dixon-Coles model with team attack and defence strengths,
competition-aware decay, a neutral/home advantage term and fitted low-score
correlation. Elo can act as a prior, regularizer or explicit feature, but its
value must be measured rather than assumed.

The model should generate differentiated expected goals per match. It should
continue feeding the existing score-matrix, markets and snapshot boundaries
where practical.

### Training and optimization

- Fit only on completed matches available before each evaluation date.
- Use SciPy for a transparent likelihood optimizer first.
- Consider Optuna only for bounded hyperparameter tuning after the objective
  and chronological evaluation are stable.
- Regularize team parameters, especially for teams with sparse history.
- Version dataset, feature logic, parameter set and model artifact together.

### Backtesting and metrics

Use expanding-window chronological backtesting. Primary metrics:

- negative log likelihood / log loss for probabilistic fit;
- Brier score for outcome probabilities;
- ranked probability score for ordered goal/outcome distributions;
- calibration curves and reliability by probability bucket;
- segmented results by era, competition, neutral venue and team-history depth.

Promotion requires a meaningful out-of-sample improvement over simple
baselines, not merely more varied top scores.

## Level 3 — Future Advanced Engine

The advanced target is a controlled comparison of model families, not a single
preselected algorithm. Candidate inputs include dynamic Elo, recent form,
competition importance, rest/travel context and consistent shot/xG features.
Candidate models may include regularized regression, gradient boosting or a
hybrid whose output is converted into a coherent score distribution.

Optuna may tune hyperparameters only inside chronological validation. Any
probabilities should receive explicit calibration testing and, where justified,
post-model calibration. A model registry should record data version, features,
parameters, metrics, calibration status and promotion decision.

Post-match monitoring should compare predicted distributions with actual
results, detect drift and retain failed predictions. Complexity is accepted
only when it improves robust out-of-sample metrics and remains explainable.

## Stable output and migration approach

The engine implementation should remain behind the existing JSON boundary.
During migration:

1. Keep current baseline outputs as a benchmark.
2. Publish the reconstructed model as a separate experimental version.
3. Compare both on completed out-of-sample matches.
4. Preserve `match_id`, score matrix, markets, top scores and provenance.
5. Promote a new primary model only after technical and human review.
6. Never overwrite historical predictions after results are known.

The contracts listed in `docs/CURRENT_ENGINE_AUDIT.md` are the compatibility
target. Any necessary incompatible schema change must be explicit and
versioned.

## Recommended next implementation phase

**V0.7 — Historical Data Acquisition Spike**

Do not implement a new model first. Measure historical API-Football coverage,
competition IDs, seasons, quota cost, neutral-venue quality, result chronology
and pre-match Elo feasibility. Produce a small audited historical sample and a
dataset coverage report before deciding the exact Level 2 implementation.

## V0.7 dataset input

`backend/data/normalized/historical_matches.json` is now the first real
training-candidate source for a future experiment. It contains `192` finished
World Cup fixtures from 2014, 2018 and 2022 and remains completely separate
from the future 2026 fixtures.

It is an experimental starting point, not the final historical dataset.
Before Level 2 fitting, V0.8 must define chronological train/validation splits,
resolve regulation-time semantics for AET/PEN fixtures, and establish a simple
benchmark. Broader qualifiers, friendlies and continental competitions remain
necessary before considering a robust promoted engine.

## V0.8 expanded dataset input

Future calibration experiments should now begin with
`backend/data/normalized/historical_matches_expanded.json`, not only the V0.7
World Cup-only dataset. The expanded source contains `1,311` finished matches
from six senior international competitions and provides deterministic
chronological train/validation/test files.

The source remains experimental. Rows preserve competition family, tier,
training-weight hint and source-scope confidence. V0.9 must segment or exclude
`mixed_scope_possible` rows, resolve AET/PEN score semantics and compare simple
baselines before fitting anything intended for promotion.

## V0.9 first calibration experiment

V0.9 implements a separate first challenger under `backend/calibration/`. The
Calibrated Simple Poisson Model v0.9 fits smoothed home/away team attack and
defence strengths on the `917`-match train split only, then evaluates the fixed
model on the chronological validation and test splits.

It improves 1X2 accuracy, log loss and Brier score over the neutral prototype
on both splits, but test exact-score accuracy is slightly worse and the known
dataset limitations remain unresolved. The active engine is unchanged and the
promotion recommendation is `do_not_promote_yet`. A later experiment should
test segmented competition effects, regulation-time score semantics and
chronological form before any promotion decision.

## V1.0 error-analysis result

V1.0 analyzes the fixed V0.9 predictions without fitting a new model. Draw is
almost never the predicted 1X2 class even though actual draw rates are `24.0%`
on validation and `31.8%` on test. The modal score remains heavily concentrated
on `1-1`, and the model underestimates the total goals of observed 4+ goal
matches. Africa Cup of Nations test performance is the weakest eligible
competition segment.

These observed errors justify testing draw calibration, competition effects,
recent form or time decay, and improved high-total behavior in a future
challenger. They do not justify promotion of V0.9.

## V1.1 challenger design

V1.1 defines isolated challengers for V1.2 without implementing them:
draw-calibrated Poisson, optimized Dixon-Coles rho, competition weighting,
time decay and an Elo prior after chronological provenance is verified. A
combined candidate is explicitly deferred until isolated changes demonstrate
benefits.

Selection requires improved validation and test log loss/Brier, reduced draw
calibration gap, guardrails on accuracy/top-3 and no increase in
high-confidence wrong predictions. No challenger is promoted automatically,
and the active engine and World Cup 2026 predictions remain unchanged.

## V1.2 isolated challenger result

V1.2 implements draw calibration and Dixon-Coles rho optimization as separate
historical experiments over fixed V0.9 predictions and xG. Parameter selection
uses validation only, and test is reserved for final evaluation. Results are
published in `docs/CHALLENGER_RESULTS_V1_2.md`; no combined challenger is
implemented, no model is promoted, and the active engine remains unchanged.

## V1.3 upstream xG challenger design

V1.2 confirms that post-probability adjustments alone do not reliably repair
the observed calibration defects. V1.3 therefore defines isolated upstream xG
challengers for competition weighting, chronological time decay, a bounded Elo
prior and low-sample fallback handling.

The feature inspection finds sufficient competition and date fields for
competition weighting and time decay, but current Elo is a static 2026
snapshot rather than historical pre-match evidence. V1.4 must not treat it as
temporally safe. The combined upstream candidate remains deferred, no model is
implemented, and promotion remains `do_not_promote_yet`.

## V1.4 upstream xG isolated challenger result

V1.4 implements competition weighting, time decay and low-sample fallback as
isolated weighted Simple Poisson experiments. It also measures a current/static
Elo prior strictly as non-promotable temporal-leakage-risk evidence.

No promotable challenger passes every guardrail. Competition weighting is
nearly neutral, low-sample fallback produces only a very small test gain while
validation regresses, and time decay improves validation before degrading test
and increasing modal `1-1` concentration. Static Elo produces attractive
apparent metrics but cannot support promotion and increases high-confidence
errors. The active engine and World Cup 2026 predictions remain unchanged.

## V2.0 quant hybrid rebuild

V2.0 implements the advanced hybrid direction as an isolated but deployable
candidate. It replaces external static Elo as a primary signal with an
internally reconstructed chronological rating, builds all features before each
result is observed, and combines regularized XGBoost 1X2 probabilities with an
independent-Poisson exact-score distribution.

Optuna selects parameters on validation only. Historical validation and test
are replayed in `predict -> observe -> update` order, secondary markets and DNB
pushes are evaluated explicitly, and Monte Carlo checks the stability of the
analytical Poisson model. Promotion is no longer categorically forbidden, but
the active engine changes only if all quantitative, coherence, leakage,
overfit, and operational-data gates pass. The measured decision is documented
in `docs/ACTIVE_ENGINE_DEPLOYMENT_V2_0.md`.

## V2.1 historical data refresh and feature coverage

V2.1 responds to V2.0's stale-data and overfit findings without retraining the
model. It expands completed senior-international history from `1,311` to
`3,062` matches after excluding `429` non-senior friendlies, and moves the
latest historical date from July 15, 2024 to
March 31, 2026. The refreshed chronological test period is only `71` days old
at generation time.

API-Football metadata and a bounded six-match probe show that statistics,
events and lineups can be available, but broad cross-era coverage is not yet
proven. Provider xG appears on only `2/12` sampled team-stat rows, and the
exploratory shots-based proxy is not approved as a primary feature. The V2.1 decision is
`proceed_to_v2_2_limited_retrain`: a future V2.2 may benchmark the refreshed
result-history signals, while advanced features require a larger coverage
audit first.

## V2.2 limited quant retrain

V2.2 retrains the existing quant architecture exclusively on the refreshed
V2.1 chronological splits. The standard 500-trial Optuna run retains 24
conservative pre-match result-history features and excludes sparse provider
statistics, events, lineups, provider xG, xG proxy and odds.

The final refreshed test reaches `0.8812` log loss and `0.5158` Brier, reduces
modal `1-1` to `23.7%`, reaches `82.3%` clear-favorite score alignment and
reduces the train-validation log-loss gap to `0.0178`. DNB at confidence
`0.60` reaches `87.6%` wins excluding pushes at `70.2%` coverage. Every strict
deployment gate passed, so `quant_hybrid_v2.2` replaced the active World Cup
2026 prediction engine. The comparisons with V2.0 and V0.9 remain directional
because their historical test periods differ.

## V2.3 active matrix secondary-market audit

V2.3 audits V2.2 without retraining or changing active predictions. It
reconstructs all supported secondary probabilities directly from each
published test score matrix, compares them with the aggregate XGBoost-direct
market evidence that V2.2 retained, and keeps active hybrid 1X2 separate.

The matrix is useful beyond exact score on broad markets: over 0.5 reaches
`91.7%` at full coverage, double chance 1X reaches `81.9%` at `75.7%`
coverage, and matrix DNB at confidence `0.60` reaches `87.6%` wins excluding
pushes and `90.1%` non-loss including pushes at `70.2%` coverage. The 90%
claim therefore applies only when pushes count as non-losses. BTTS yes, clean
sheets, winning margins and several high-total lines remain too sparse or
unstable for unqualified product display.

## V2.4 active prediction release candidate

V2.4 turns the accepted active engine into a product release candidate without
retuning. It verifies and metadata-enriches the 72 active prediction files,
publishes a frontend-oriented match contract, integrates the V2.3
secondary-market evidence and runs 50,000 group-stage tournament scenarios.

All 12 groups and 48 teams are simulated using the active score matrices. The
top two teams per group and eight best third-placed teams qualify. Full
tournament simulation remains unavailable because no complete knockout
fixture or bracket contract exists; V2.4 does not invent one. The next product
work can consume the documented match-detail, matrix, markets, group
simulation and transparency contracts.

## V2.5 existing UI enrichment

V2.5 consumes the V2.4 contracts in the existing Angular product structure.
It preserves group cards and the match modal, adds active prediction detail
through progressive disclosure, and introduces a dedicated group-simulation
route. A frontend-asset validator confirms that generated, snapshot and
Angular copies remain consistent.

This is a product-consumption iteration only. It does not retrain a model,
rerun Optuna, alter active probabilities or invent a knockout bracket.

## V2.6 live results and creative tournament path

V2.6 adds official results as a separate immutable evaluation layer. Frozen
pre-match predictions are compared with finished scores, and the group
simulation locks only finished official results while future fixtures continue
to use their original matrices.

The available fixture source still contains no official knockout mapping.
Instead of inventing one, V2.6 publishes a clearly labelled Projected Campaign
proxy combining conditioned group outlook and rating context. A full official
path remains blocked until a trustworthy bracket contract exists.

## V2.7 result consistency and prediction presentation

V2.7 consolidates the product state after live results arrive. A unified match
view model joins frozen prediction, official result, evaluation, normalized
status and display labels for both cards and the existing modal. Separate live
standings are calculated only from finished official scores and are shown
beside conditioned projections.

The presentation now explains why a single modal score can differ from the
aggregate 1X2 favorite and supplies the most probable score compatible with
that favorite. No probability is changed to manufacture visual agreement.

## V2.8 score matrix realism and favorite strength calibration

V2.8 establishes that the active score projection is materially conservative
as a modal-score and simulation source even though aggregate 1X2 and broad
markets remain useful. On the frozen historical test, actual matches contain
far more three-plus-goal outcomes and wider favorite margins than modal scores
represent.

Bounded post-model challengers are evaluated without retraining or Optuna.
The strongest favorite-gap scaling variant improves score log likelihood,
top-3, top-5, 1X2 Brier, over-2.5 Brier and favorite-margin realism while
preserving DNB decisions. It also lowers exact-score accuracy, so its World Cup
output is published only as a candidate for explicit human and simulation
review. The active `quant_hybrid_v2.2` probabilities remain frozen.

## V2.9 dual matrix display and candidate simulation comparison

V2.9 connects the non-active V2.8 candidate to product transparency and
tournament simulation without promoting it. Every World Cup match receives an
active-versus-alternative matrix comparison, and the candidate runs through a
separate 50,000-scenario conditioned group simulation with finished official
results locked.

The active forecast remains the default in the match experience and
simulation page. The alternative appears only through explicit labels,
secondary disclosure and a user-controlled toggle. Its qualification deltas
and projected-campaign proxy are comparative evidence, not official
predictions. No model, Optuna study or active probability is changed.

## V2.10 operational matchday refresh pipeline

V2.10 turns the separate result-aware scripts into one ordered operational
workflow. A single command refreshes official-result overlays, post-match
evaluation, live standings, unified match state, active and candidate
conditioned simulations, their comparison, projected-campaign proxies and
consistency validation.

The workflow records protected-file hashes, step output and Git hygiene in a
versioned manifest. Cached-only, online fetch, dry-run and frontend-copy
control modes support routine matchday operations without changing frozen
pre-match probabilities, retraining the model, rerunning Optuna or promoting
the candidate.

## V2.11 creative tournament experience

V2.11 composes the result-aware V2.10 layers into a dedicated product
aggregate and turns `/simulation` into a narrative tournament feature. The
experience leads with a projected campaign leader, then explains contender
movement, open groups, locked-result impact and the contrast between the
active forecast and the non-active alternative.

The official knockout bracket remains unavailable. The tournament leader is
therefore a non-official campaign proxy, not a fully simulated champion. V2.11
does not invent knockout opponents, change active probabilities, promote the
candidate, retrain the model or rerun Optuna.

## V2.12 prediction history and public transparency

V2.12 creates an append-only memory of all active World Cup forecasts. Frozen
pre-match predictions remain separate from actual results and post-match
evaluation labels. A public scoreboard, chronological performance timeline and
plain-language glossary make model successes, partial hits and misses visible.

The dedicated `/transparence` route emphasizes counts, sample size and Draw No
Bet pushes instead of presenting flattering rates without context. The
alternative projection remains a non-active comparison on finished matches.
No prediction is rewritten, no candidate is promoted, no model is retrained
and Optuna is not rerun.

## V2.13 living World Cup bracket and scenario engine

V2.13 adds a simulation-derived knockout scenario while preserving the absence
of an official bracket contract. It combines the conditioned 50,000-scenario
group outlook with a reproducible 50,000-path knockout projection, exposes a
representative route to the trophy and documents the full 104-match target.

The product language is simplified around SimuAI, Prono IA, Score recommandé,
Résultat officiel and Bilan du prono. Technical provenance leaves the main
screen, matchdays reduce group-view density, and the experimental variant moves
to a collapsed lab section. Active predictions remain frozen.
