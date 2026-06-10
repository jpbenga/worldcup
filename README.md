# SimuMondial 2026

Prototype personnel et non commercial de simulation probabiliste pour la Coupe
du Monde 2026.

Le dépôt contient un premier pipeline backend capable de générer une matrice de
scores, d'en déduire des marchés statistiques et de comparer ces prédictions à
des résultats fictifs.

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
`docs/DATA_FOUNDATION.md`. Les données actuelles sont des données de
démonstration, clairement signalées dans l'interface.
