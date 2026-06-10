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
