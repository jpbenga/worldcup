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
`docs/DATA_FOUNDATION.md`. Les fixtures actives sont réelles et futures ; les
prédictions restent celles d'un moteur expérimental non calibré, clairement
signalé dans l'interface.
