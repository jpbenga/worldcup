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
