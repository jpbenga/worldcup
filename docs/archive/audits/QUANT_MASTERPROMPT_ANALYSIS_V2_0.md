# Quant Master Prompt Analysis V2.0

## What the prompt requests

The prompt asks for a large, conditionally deployable rebuild of the football
prediction engine. It requires an internal chronological rating, pre-match
features, a Poisson score distribution, XGBoost models for 1X2 and secondary
markets, Optuna validation-only selection, online historical replay, 1,500
Monte Carlo simulations per match, product-coherence audits, and an evidence-
based deployment decision.

Unlike V0.9 through V1.4, V2.0 may replace the active engine and regenerate
World Cup 2026 predictions, but only if the final historical test establishes
the new engine.

## Technical risks

- The historical corpus has only 917 train matches, 196 validation matches and
  198 test matches across changing competition composition. A high-capacity
  model can overfit easily.
- The dataset contains goals, teams, dates and competition metadata, but no
  provider xG, shots, squad quality, confirmed neutral-site flag, injuries or
  lineups. The V2 "xG" layer therefore estimates expected goals from historical
  goals and ratings; it is not event-data xG.
- Optimizing every secondary-market model inside every Optuna trial would
  multiply selection pressure on a small validation set and make results less
  trustworthy.
- Active deployment would overwrite user-visible 2026 predictions. It must be
  blocked unless final test, coherence and market evidence all pass.

## Temporal leakage risks

- Current/static external Elo is forbidden as a primary signal. V2 constructs
  an internal rating by reading pre-match ratings, predicting, observing the
  result and updating only afterward.
- Recent-form and attack/defence features must use only matches before each
  kickoff.
- Optuna may inspect validation only. Test is evaluated after parameters are
  frozen and cannot trigger parameter changes.
- World Cup 2026 fixtures may be used only after a deployment decision and
  never for training or selection.

## Ambiguities and decisions

- "xG" is interpreted as model-estimated scoring intensity because true xG is
  absent. Documentation will state this limitation explicitly.
- Neutral/home context is encoded conservatively as unavailable/neutral because
  venue semantics are not reliable enough for a fitted advantage.
- Optuna optimizes the hybrid 1X2 core and Poisson distribution objective.
  Secondary XGBoost models are trained after core selection with the selected
  regularized tree parameters, then evaluated independently. This reduces
  validation overfitting while satisfying the required secondary-market work.
- Historical replay uses chronological `predict -> observe -> update` features.
  Validation and test remain separate reporting periods, but test replay starts
  from state updated through all earlier train and validation matches, which is
  legitimate online information.
- Exact score is secondary. Calibration, 1X2, DNB, secondary markets, modal
  concentration and favorite-score coherence drive deployment.

## Strictly respected requirements

- XGBoost and Optuna are versioned dependencies.
- Internal ratings are chronological and pre-match.
- Historical replay is explicit.
- DNB reports wins, losses and pushes separately.
- Monte Carlo uses 1,500 simulations per match.
- Modal `1-1` and favorite-score coherence are audited.
- No secret or external static Elo primary signal is used.
- No test or 2026 fixture influences selection.
- Poor results and low-coverage market claims remain visible.

## Deployment policy

The runner may deploy only when final test improves V0.9 materially, validation
and test are directionally consistent, secondary markets are useful at
non-trivial coverage, modal `1-1` concentration falls substantially, clear-
favorite score alignment is at least 50%, and no leakage or obvious overfit is
detected. Otherwise it publishes experimental artifacts and leaves active 2026
predictions untouched.
