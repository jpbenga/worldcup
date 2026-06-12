# SimuMondial 2026

Prototype personnel et non commercial de simulation probabiliste pour la Coupe
du Monde 2026.

Le dépôt contient un pipeline backend qui active les fixtures réelles
API-Football de la Coupe du Monde 2026, génère des matrices de scores prototype
et publie une interface de revue par groupes.

## Lancer l'application localement

```bash
cd "/Users/chloe/Desktop/dossier sans titre/worldcup"

python3 backend/scripts/build_snapshots.py

cd frontend
nvm use
npm install
npm start
```

L'application est ensuite disponible sur `http://localhost:4200`.

## Backend

```bash
python3 backend/scripts/build_snapshots.py
```

Les sorties sont écrites dans :

```text
backend/data/snapshots/matches.json
backend/data/snapshots/predictions.json
backend/data/snapshots/backtest_results.json
backend/data/snapshots/data_sources.json
backend/data/snapshots/teams.json
backend/data/snapshots/worldcup_groups.json
backend/data/snapshots/group_strengths.json
backend/data/snapshots/prediction_diversity_audit.json
```

## Frontend

Le frontend utilise Angular 22, Tailwind CSS et Node `22.22.3`.

```bash
cd frontend
nvm use
npm install
npm start
```

Build de production :

```bash
cd frontend
nvm use
npm run build
```

## Manual validation

Before moving to the next project phase, run:

```bash
python3 backend/scripts/build_snapshots.py

cd frontend
nvm use
npm install
npm start
```

Then open:

```text
http://localhost:4200
```

Use:

```text
docs/MANUAL_VALIDATION_CHECKLISTS.md
```

to manually validate data coherence, provenance badges, UI behavior, and JSON
consistency. Record the human decision and any reservations in
`docs/VALIDATION_LOG.md`.

## Real data acquisition spike

Create a local `.env` file from `.env.example` and set your own key:

```env
API_FOOTBALL_KEY=your_key_here
API_FOOTBALL_BASE_URL=https://v3.football.api-sports.io
```

Install the minimal Python dependencies, then run controlled explorations:

```bash
python3 -m pip install -r backend/requirements.txt
python3 -m playwright install chromium

python3 backend/scripts/explore_api_football.py --mode ping
python3 backend/scripts/explore_api_football.py --mode discovery
python3 backend/scripts/explore_api_football.py --mode worldcup
python3 backend/scripts/explore_api_football.py --mode samples

python3 backend/scripts/explore_elo_ratings.py --mode raw-html
python3 backend/scripts/explore_elo_ratings.py --mode network
python3 backend/scripts/explore_elo_ratings.py --mode rendered-table
python3 backend/scripts/normalize_external_data.py
```

Then read:

```text
docs/REAL_DATA_ACQUISITION_REPORT.md
docs/DATA_SOURCE_DECISIONS.md
```

## Team identity mapping

Build and validate the explicit API-Football to Elo identity layer:

```bash
python3 backend/scripts/build_team_identity_map.py
python3 backend/scripts/validate_team_mappings.py
python3 backend/scripts/build_snapshots.py
```

The mapping is documented in `docs/TEAM_MAPPING_GUIDE.md`. It does not connect
Elo ratings to the prediction engine or alter probabilities.

## Experimental Elo model

Generate the stable baseline, the separate Elo-adjusted experiment, and their
comparison:

```bash
python3 backend/scripts/build_snapshots.py --model both

cd frontend
nvm use
npm start
```

The baseline remains available in `predictions.json`. The experiment and its
moderate adjustment are documented in `docs/ELO_MODEL_EXPERIMENT.md`.

## API-Football active source

Fetch and activate the real future World Cup 2026 fixtures:

```bash
python3 backend/scripts/fetch_worldcup_api_football.py --season 2026
python3 backend/scripts/normalize_api_football_worldcup.py
python3 backend/scripts/build_snapshots.py --source api_football --model both
```

The current engine is a replaceable, non-historically-calibrated prototype.
Future fixtures are never evaluated against mock results. See
`docs/API_FOOTBALL_ACTIVE_SOURCE.md`, `docs/PROTOTYPE_ENGINE_STATUS.md` and
`docs/PREDICTION_ENGINE_AUDIT_V0_5.md`.

API-Football est la source par défaut. Le pipeline ne bascule jamais
silencieusement vers le mock ; ce mode doit être demandé explicitement avec
`--source mock`.

## Prediction engine discovery

V0.6 documents the current prototype, recovered historical references and the
path toward a future calibrated engine without changing prediction logic:

```text
docs/CURRENT_ENGINE_AUDIT.md
docs/ENGINE_REFERENCE_INVENTORY.md
docs/HISTORICAL_DATA_STRATEGY.md
docs/FUTURE_ENGINE_BLUEPRINT.md
docs/adr/ADR-0001-prototype-engine-now-calibrated-engine-later.md
```

Regenerate the tracked reference inventory with:

```bash
python3 backend/scripts/discover_engine_references.py
```

The recommended next implementation phase is **V0.7 — Historical Data
Acquisition Spike**.

## Historical data acquisition spike

V0.7 explores API-Football international history and publishes an isolated,
real dataset without changing the active 2026 prediction engine:

```bash
python3 backend/scripts/explore_historical_api_football.py --limit-seasons 5
python3 backend/scripts/fetch_historical_international_matches.py --preset conservative
python3 backend/scripts/normalize_historical_matches.py
python3 backend/scripts/audit_historical_dataset.py
```

The conservative dataset contains `192` finished World Cup fixtures from 2014,
2018 and 2022 in `backend/data/normalized/historical_matches.json`. It excludes
all future 2026 fixtures and is documented as an experimental training
candidate, not a sufficient final dataset. See
`docs/HISTORICAL_API_FOOTBALL_EXPLORATION.md` and
`docs/HISTORICAL_DATASET_AUDIT.md`.

## Expanded historical dataset and chronological split

V0.8 keeps the V0.7 World Cup-only dataset intact and creates a separate
multi-competition dataset:

```bash
python3 backend/scripts/explore_expanded_historical_competitions.py --max-requests 60
python3 backend/scripts/fetch_expanded_historical_matches.py --preset conservative --max-requests 100
python3 backend/scripts/normalize_expanded_historical_matches.py
python3 backend/scripts/audit_expanded_historical_dataset.py
python3 backend/scripts/create_historical_dataset_splits.py
```

`historical_matches_expanded.json` contains `1,311` real finished matches from
six senior international competitions. Its deterministic chronological split
contains `917` train, `196` validation and `198` test matches. No model is
trained and active World Cup 2026 predictions remain unchanged.

## First historical calibration experiment

V0.9 trains a separate, experimental simple Poisson model on the historical
train split and evaluates it chronologically without replacing the active
engine:

```bash
python3 backend/scripts/run_first_calibration_experiment.py
python3 backend/scripts/compare_calibrated_vs_prototype.py
```

The model uses smoothed team home/away attack and defence strengths and remains
isolated under `backend/calibration/`. It improves 1X2, log loss and Brier
metrics over the neutral prototype on validation and test, but is explicitly
not promoted. See `docs/CALIBRATION_EXPERIMENT_V0_9.md`.

## Calibration error analysis

V1.0 analyzes the existing V0.9 validation/test predictions without retraining
the model or changing World Cup 2026 outputs:

```bash
python3 backend/scripts/analyze_calibration_errors_v1_0.py
```

The report segments errors by competition, season, team, result, confidence and
goal total. It documents draw-class underprediction, modal `1-1`
concentration, high-total underestimation and problematic matches. Promotion
remains `do_not_promote_yet`; see `docs/CALIBRATION_ERROR_ANALYSIS_V1_0.md`.

## Improved challenger design

V1.1 is a design-only phase for isolated V1.2 challengers. It defines
draw-calibrated, optimized Dixon-Coles rho, competition-weighted, time-decay
and Elo-prior candidates, with a combined candidate deferred until isolated
benefits are proven.

See `docs/CHALLENGER_ENGINE_DESIGN_V1_1.md` and
`docs/CHALLENGER_EVALUATION_PROTOCOL.md`. No model is implemented or retrained,
and promotion remains `do_not_promote_yet`.

## Isolated calibration challengers

V1.2 implements only draw-calibrated Poisson and validation-selected
Dixon-Coles rho as isolated historical experiments:

```bash
python3 backend/scripts/run_isolated_challenger_experiments_v1_2.py
```

The script selects parameters on validation only, evaluates the fixed choices
on test, and publishes `docs/CHALLENGER_RESULTS_V1_2.md`. It does not implement
a combined challenger, replace the active engine, modify World Cup 2026
predictions, or promote a model.

## Upstream xG challenger design

V1.3 is a design-only response to the V1.2 result: post-probability
corrections did not pass the guardrails, so the next isolated experiments must
improve expected-goals generation upstream.

```bash
python3 backend/scripts/inspect_upstream_xg_feature_availability_v1_3.py
```

The read-only inspection publishes feature coverage and the V1.3 design. See
`docs/UPSTREAM_XG_FEATURE_CHALLENGER_DESIGN_V1_3.md`,
`docs/UPSTREAM_XG_FEATURE_AVAILABILITY_V1_3.md`, and
`docs/UPSTREAM_XG_EXPERIMENT_PROTOCOL_V1_4.md`. No challenger is implemented,
no model is trained, and promotion remains `do_not_promote_yet`.

## Upstream xG isolated challengers

V1.4 implements the competition-weighted, time-decay and low-sample fallback
xG challengers as separate train-only experiments. It also runs current/static
Elo as an explicitly non-promotable temporal-leakage-risk diagnostic.

```bash
python3 backend/scripts/run_upstream_xg_challenger_experiments_v1_4.py
```

Parameters are selected on validation only and test is reserved for final
evaluation. No combined challenger is implemented, the active engine and 2026
predictions remain unchanged, and promotion remains `do_not_promote_yet`. See
`docs/UPSTREAM_XG_CHALLENGER_RESULTS_V1_4.md`.

## Quant hybrid engine V2.0

V2.0 rebuilds the experimental modeling stack around a chronological internal
rating, leakage-safe pre-match features, regularized XGBoost market models,
Optuna validation-only selection, a Poisson score distribution, historical
replay, secondary-market evaluation, and 1,500 Monte Carlo simulations per
match.

```bash
python3 -m pip install -r backend/requirements.txt
python3 backend/scripts/run_quant_engine_rebuild_v2_0.py
```

Use `--full-optuna` for the 1,000-trial mode. The runner evaluates the fixed
configuration once on test and conditionally replaces the active engine only
if every deployment gate passes. Otherwise it publishes the V2.0 artifacts
separately and leaves active World Cup 2026 predictions unchanged. See
`docs/QUANT_ENGINE_V2_0_RESULTS.md` and
`docs/ACTIVE_ENGINE_DEPLOYMENT_V2_0.md`.

## Historical data refresh V2.1

V2.1 is a data-only follow-up to the non-deployed V2.0 engine. It refreshes
completed senior-international history, measures API-Football statistics,
events and lineup availability, audits exploratory xG-proxy feasibility,
creates refreshed chronological splits and checks temporal leakage.

```bash
python3 backend/scripts/discover_api_football_feature_coverage_v2_1.py
python3 backend/scripts/fetch_recent_international_history_v2_1.py
python3 backend/scripts/fetch_match_features_v2_1.py
python3 backend/scripts/build_xg_proxy_feature_report_v2_1.py
python3 backend/scripts/build_refreshed_historical_splits_v2_1.py
python3 backend/scripts/audit_temporal_leakage_v2_1.py
```

V2.1 does not train XGBoost, run Optuna or modify active 2026 predictions. See
`docs/DATA_SIGNAL_UPGRADE_RECOMMENDATION_V2_1.md`.

## Limited quant retrain V2.2

V2.2 retrains the conservative V2 quant architecture exclusively on the
refreshed V2.1 chronological splits. It deliberately excludes sparse provider
xG, exploratory xG proxy, odds, and current-match post-match statistics,
events, or lineups.

```bash
python3 backend/scripts/run_limited_quant_retrain_v2_2.py
python3 backend/scripts/run_limited_quant_retrain_v2_2.py --quick
python3 backend/scripts/run_limited_quant_retrain_v2_2.py --full
```

The standard 500-trial validation-only run passed every strict deployment gate
and promoted `quant_hybrid_v2.2` to the active World Cup 2026 prediction
engine. See `docs/QUANT_ENGINE_V2_2_RESULTS.md` and
`docs/ACTIVE_ENGINE_DEPLOYMENT_V2_2.md`.

## Active matrix market audit V2.3

V2.3 audits the deployed V2.2 score matrix on all supported secondary markets
without retraining, Optuna, new data or active-prediction regeneration.

```bash
python3 backend/scripts/audit_active_matrix_markets_v2_3.py
```

The audit separates matrix-derived markets, published aggregate XGBoost-direct
metrics and active hybrid 1X2 probabilities. It also publishes calibration
buckets, segment reports and a descriptive market audit of the 72 active World
Cup 2026 fixtures. See `docs/ACTIVE_MATRIX_MARKET_AUDIT_V2_3.md`.

## Active 2026 release candidate V2.4

V2.4 verifies and packages the active `quant_hybrid_v2.2` predictions as a
frontend release candidate, integrates the V2.3 market-performance summary and
runs a 50,000-scenario group-stage tournament simulation.

```bash
python3 backend/scripts/verify_active_quant_engine_v2_4.py
python3 backend/scripts/build_2026_prediction_release_candidate_v2_4.py
python3 backend/scripts/run_worldcup_tournament_simulation_v2_4.py --simulations 50000
```

The active files contain 72 metadata-complete predictions. V2.4 simulates all
12 groups and the best-third qualification route; it does not invent a
knockout bracket that is not present in the source fixtures.

## Existing UI enrichment V2.5

V2.5 keeps the group-first Angular interface and existing match modal while
connecting them to the V2.4 release-candidate contract. Group cards expose a
compact active signal, the modal adds progressive match analysis, and
`/simulation` presents the 50,000 group-stage scenarios.

```bash
python3 backend/scripts/validate_frontend_prediction_assets_v2_5.py

cd frontend
nvm use
npm run build
npm test -- --watch=false
```

The simulation route covers groups only. No knockout bracket is invented, and
V2.5 does not change active prediction probabilities.

## Live results and conditioned simulation V2.6

V2.6 keeps pre-match predictions frozen and publishes official results,
post-match evaluation and conditioned group simulation as separate layers.

```bash
python3 backend/scripts/fetch_worldcup_2026_results_v2_6.py
python3 backend/scripts/evaluate_predictions_against_results_v2_6.py
python3 backend/scripts/run_worldcup_tournament_simulation_v2_6.py
python3 backend/scripts/discover_worldcup_knockout_structure_v2_6.py
python3 backend/scripts/build_worldcup_projected_campaign_v2_6.py
```

The existing cards and modal display official results only when available.
`/simulation` locks finished scores and shows a clearly labelled Projected
Campaign proxy because no official knockout bracket is currently available.

## Result consistency and live standings V2.7

V2.7 publishes a unified frontend match state and live group standings built
only from finished official results.

```bash
python3 backend/scripts/build_live_group_standings_v2_7.py
python3 backend/scripts/build_match_state_view_model_v2_7.py
python3 backend/scripts/validate_result_consistency_v2_7.py
```

Cards and the existing modal consume the same match-state artifact.
`/simulation` distinguishes the real current table from conditioned
qualification projections. Modal score and 1X2 favorite divergence is
explained without changing frozen probabilities.

## Score matrix realism V2.8

V2.8 audits whether the active V2.2 Poisson score projection is too
conservative, using the frozen 460-match historical test as the decision set.

```bash
python3 backend/scripts/audit_score_matrix_realism_v2_8.py
python3 backend/scripts/evaluate_score_matrix_challengers_v2_8.py
```

The audit confirms severe modal-score compression and publishes a bounded
favorite-gap challenger as a non-active World Cup candidate. Active hybrid
1X2 probabilities and `predictions.json` remain unchanged pending explicit
human validation.

## Dual matrix comparison V2.9

V2.9 exposes the accepted V2.8 candidate as a clearly labelled alternative,
without promoting it or replacing active predictions.

```bash
python3 backend/scripts/build_dual_matrix_comparison_v2_9.py
python3 backend/scripts/run_candidate_tournament_simulation_v2_9.py
python3 backend/scripts/compare_active_vs_candidate_simulation_v2_9.py
python3 backend/scripts/build_candidate_projected_campaign_v2_9.py
python3 backend/scripts/validate_dual_matrix_v2_9.py
```

The match modal offers a secondary active/alternative comparison and
`/simulation` compares both conditioned group scenarios. The active forecast
remains the official default; the alternative is always marked non-active.

## Operational matchday refresh V2.10

V2.10 runs every result-aware layer in one protected operational workflow:

```bash
python3 backend/scripts/run_matchday_refresh_v2_10.py --fetch --simulations 50000
python3 backend/scripts/audit_generated_artifact_hygiene_v2_10.py
python3 backend/scripts/validate_matchday_refresh_v2_10.py
```

Use `--no-fetch` for cached data and `--dry-run` to inspect the ordered plan.
The workflow protects frozen pre-match predictions and model artifacts with
before/after hashes; it never retrains, reruns Optuna or promotes the candidate.

## Structure

- `backend/` : pipeline simple de génération et de backtesting.
- `docs/` : contrats, modèles Angular et rapports de préparation.
- `frontend/` : application Angular qui affiche les snapshots JSON.
- `handoff_worldcup_2026/` : briques métier autonomes extraites du prototype
  historique.
- `prototype_ia_coupe_du_monde_2026.md` : document de cadrage produit.

Le moteur métier reste côté backend. Angular charge uniquement les snapshots
copiés dans `frontend/src/assets/data/`.

La structure et les règles de provenance sont détaillées dans
`docs/DATA_FOUNDATION.md`. Les fixtures actives sont réelles et les prédictions
proviennent désormais du moteur release-candidate historiquement validé
`quant_hybrid_v2.2`.
