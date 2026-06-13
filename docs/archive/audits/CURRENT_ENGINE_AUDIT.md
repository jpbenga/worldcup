# Current Engine Audit

## Scope and conclusion

V0.6 audits the current prediction path without changing it. The repository
contains a small, deterministic and replaceable prediction engine. It is useful
for exercising acquisition, normalization, snapshots and UX, but it is not a
trained or historically calibrated forecasting model.

The repository also contains cleaned traces of an older engine. Those traces
are enough to reconstruct its broad methodology, but not a trustworthy trained
model: the historical source files, reliable fitted parameters and validated
training dataset are absent.

## Current execution path

The active path is:

```text
API-Football fixture normalization
  -> neutral model_inputs
  -> baseline_expected_goals
  -> optional bounded Elo adjustment
  -> Poisson/Dixon-Coles score matrix
  -> derived markets and top scores
  -> baseline/Elo/comparison snapshots
  -> diversity audit
```

`backend/scripts/build_snapshots.py` activates API-Football by default and asks
`generate_predictions.generate_models("both")` for baseline and Elo outputs.
Future fixtures are explicitly marked `not_evaluable`; the mock backtester is
not run against them.

## Functions composing the current engine

| Area | Function | Current role |
|---|---|---|
| Normalization | `normalize_api_football_worldcup.normalize_matches` | Creates canonical fixtures and injects neutral prototype inputs. |
| Baseline xG | `generate_predictions.baseline_expected_goals` | Blends recent goals-for and goals-against inputs, then calls `compute_lambdas`. |
| Lambda helper | `expected_goals.compute_lambdas` | Modulates xG with a logistic Elo-strength formula and optional home advantage. |
| Historical helper | `expected_goals.rolling_xg_baselines` | Implements an unused rolling attack/defence blend inherited from the old prototype. |
| Elo lookup | `elo_features.get_match_elo_features` | Reads validated API-Football-to-Elo mappings. |
| Elo variant | `elo_adjusted_model.adjust_expected_goals` | Applies a bounded, moderate Elo factor to baseline xG. |
| Score matrix | `score_matrix.generate_score_matrix` | Multiplies independent Poisson probabilities, applies Dixon-Coles low-score correction and normalizes. |
| Markets | `markets.derive_markets` | Aggregates the matrix into 1X2, double chance, totals, BTTS and exact scores. |
| Serialization | `generate_predictions.prediction_from_expected_goals` | Builds the stable prediction JSON shape and confidence label. |
| Comparison | `compare_prediction_models.main` | Computes selected market deltas and modal-score changes. |
| Audit | `audit_prediction_diversity.main` | Measures top-score concentration without changing probabilities. |
| Backtesting | `backtesting.backtest_predictions` | Minimal signal/result evaluator used only for explicit mock workflows. |

## How baseline xG is generated

For each normalized real fixture, the normalizer currently writes:

```text
home_elo = 1500
away_elo = 1500
home_recent_goals_for = 1.35
home_recent_goals_against = 1.35
away_recent_goals_for = 1.35
away_recent_goals_against = 1.35
```

`baseline_expected_goals` calculates:

```text
home_xg = 0.6 * home_recent_goals_for + 0.4 * away_recent_goals_against
away_xg = 0.6 * away_recent_goals_for + 0.4 * home_recent_goals_against
```

It then calls `compute_lambdas` with neutral input Elo, no home-field advantage
and `w_elo=0.6`. Because every input is equal, every real fixture receives the
same baseline lambda pair: `1.35 / 1.35`.

The xG are neutral because the active 2026 fixture feed does not itself provide
a validated chronological history of team performance. Inventing differentiated
features would falsely imply calibration, so V0.5 deliberately chose explicit
neutral prototype defaults.

## Poisson and Dixon-Coles matrix

`generate_score_matrix` evaluates all score pairs from `0-0` through `5-5` in
the active generator. Each cell begins as:

```text
Poisson(home_goals | home_lambda) * Poisson(away_goals | away_lambda)
```

`dixon_coles_adjustment` modifies only `0-0`, `0-1`, `1-0` and `1-1`; the
active generator passes `rho=-0.05`. The finite matrix is then normalized to a
total probability mass of one. This is a useful score-distribution primitive,
but its parameters are not fitted to international match history and its
renormalization hides probability mass beyond the score cap.

## Market derivation

`derive_markets` reads only the normalized score matrix. It sums cells into:

- home win, draw and away win;
- home-or-draw, away-or-draw and no-draw;
- over 0.5, 1.5, 2.5 and 3.5;
- under 2.5 and 3.5;
- BTTS yes/no;
- top exact scores.

This separation is an important replacement boundary: a future model may
produce a different score matrix while preserving the market derivation and
frontend contracts.

## Elo injection and unchanged modal scores

The baseline records mapped Elo values as metadata but does not use them.
The separate Elo variant reads validated ratings and computes:

```text
elo_factor = clamp((home_elo - away_elo) / 400, -0.35, 0.35)
adjusted_home_xg = baseline_home_xg * (1 + elo_factor * 0.20)
adjusted_away_xg = baseline_away_xg * (1 - elo_factor * 0.20)
```

If either rating is unavailable, the variant falls back exactly to baseline.
For the 72 active fixtures, all ratings are available and markets move by at
most about `0.0435`. The bounded adjustment changes probability mass, but not
enough to move another exact score above `1-1`; therefore baseline and Elo both
have `1-1` as modal score for `72/72` fixtures.

## Experimental metadata and documented limits

The current engine identifies itself through:

- `ENGINE.name = "Prototype Prediction Engine"`;
- `ENGINE.status = "experimental"`;
- `ENGINE.historically_calibrated = false`;
- Elo predictions with `engine_status = "experimental"` and
  `historically_calibrated = false`;
- neutral inputs with
  `input_basis = "neutral_prototype_defaults_not_historically_calibrated"`;
- API-Football future backtesting status `not_evaluable`.

Existing documentation also records: no historical training, no international
calibration, no tournament simulation, no valid backtest for future fixtures,
no probabilistic calibration metrics, a finite matrix tail and a simple
low-score correction.

## Recovered historical traces

The handoff documents identify old files that are intentionally not present:

- `drc-prototype/optimizer.py`: explicit xG/Elo formulas,
  Poisson/Dixon-Coles and chronological optimization with log loss;
- `drc-prototype/xg-backtest.js`: rolling baseline and chronological backtest;
- `drc-prototype/backtest.js`: detailed validation history;
- `drc-prototype/history_*.json`: provider-specific club history.

The cleaned repository preserves formulas and notes, not a trained engine.
`best_params.json` was explicitly rejected because its recorded optimization
did not use a valid training set. The historical sources also contained
sensitive and tightly coupled code, so `drc-prototype/` must not be restored.

## Historical dependency candidates

| Category | Findings |
|---|---|
| Statistical modeling | No declared runtime library; current Poisson implementation uses standard-library `math`. |
| Optimization | `scipy` and `optuna` are explicitly listed as optional legacy optimizer candidates. |
| Machine learning | No tracked dependency on scikit-learn, XGBoost, LightGBM or CatBoost. |
| Football modeling | No tracked dependency on `penaltyblog`; football formulas are local. |
| Data acquisition | `requests`, `beautifulsoup4`, `playwright`, `python-dotenv`. |
| Visualization | Angular/Tailwind frontend only; no Python visualization dependency. |
| Testing | `pytest` is documented for the recycled Python bundle; Angular uses Vitest. |

`numpy` is also explicitly listed as an optional legacy optimizer candidate.
No clear historical dependency on `pandas`, `statsmodels`, `scikit-learn`,
`penaltyblog`, `xgboost`, `lightgbm` or `catboost` was found.

## Replaceable contract

A future calibrated engine may replace feature construction, fitting and score
probability generation, but it must preserve or deliberately version these
published contracts:

| Contract | Stability requirement |
|---|---|
| `matches.json` | Stable fixture identity, teams, kickoff, provenance and status. |
| `predictions.json` | Primary prediction shape, score matrix, markets, confidence and metadata. |
| `predictions_baseline.json` | Comparable baseline output during migration. |
| `predictions_elo.json` | Separate experimental comparison output until superseded explicitly. |
| `model_comparison.json` | Match-aligned deltas and model versions. |
| `backtest_results.json` | No future-fixture fabrication; retain evaluated and failed results. |
| `data_sources.json` | Honest source, calibration and backtesting status. |
| `worldcup_groups.json` | Group UX contract independent of the prediction model. |
| `group_strengths.json` | Group summary contract; methodology must be versioned if changed. |
| `prediction_diversity_audit.json` | Reproducible concentration audit for any promoted model. |

Within `predictions*.json`, preserve stable `match_id`, generated/model
versions, a normalized score-matrix list, market names, top-score objects and
explicit engine/calibration metadata. Any incompatible change requires a
versioned migration rather than a silent rewrite.
