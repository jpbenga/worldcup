# Angular Frontend Notes

## Choix techniques

Le frontend utilise Angular 22 avec des composants standalone et Tailwind CSS
3.4. Angular fournit le typage, les services HTTP et le routing minimal.
Tailwind permet de construire rapidement un dashboard sombre, responsive et
lisible sans ajouter de bibliothèque UI.

Le moteur de prédiction ne se trouve pas dans Angular. Le frontend affiche
uniquement les snapshots JSON générés par le backend.

## Flux de données

```text
backend/data/*.json
      -> copie
frontend/src/assets/data/*.json
      -> HttpClient + adaptateurs snake_case/camelCase
      -> composants Angular
```

Assets utilisés :

- `frontend/src/assets/data/sample_matches.json`
- `frontend/src/assets/data/predictions.json`
- `frontend/src/assets/data/backtest_results.json`

## Services

- `MatchService` charge les matchs et convertit les clés vers `Match`.
- `PredictionService` charge les matrices, marchés et top scores vers
  `MatchPrediction`.
- `BacktestingService` extrait le tableau `results` et retourne tous les
  `BacktestResult`, validés comme non validés.

## Composants

- `HomeComponent` compose la page et charge les trois flux.
- `MatchListComponent` affiche les prédictions disponibles.
- `MatchCardComponent` résume un match, le score principal et le 1X2.
- `MatchDetailComponent` affiche le snapshot sélectionné.
- `ScoreMatrixComponent` trie et affiche les dix scores les plus probables.
- `MarketSummaryComponent` affiche les marchés dérivés.
- `PredictionHistoryComponent` affiche l'historique complet.
- `ResponsibleNoticeComponent` rappelle les limites statistiques.

La route `/` pointe vers `HomeComponent`. Le détail s'affiche sous la liste au
clic, sans routing supplémentaire.

## Tailwind

Tailwind 3 est utilisé volontairement afin de conserver la configuration
classique demandée :

- `frontend/tailwind.config.js`
- `frontend/postcss.config.js`
- directives `@tailwind` dans `frontend/src/styles.scss`

Le design utilise principalement les palettes `slate`, `cyan`, `emerald`,
`amber`, `rose` et `violet`, avec des cartes arrondies, bordures discrètes et
grilles responsives.

## Régénérer et recopier les snapshots

Depuis la racine du dépôt :

```bash
python3 backend/scripts/generate_sample_predictions.py
python3 backend/scripts/run_sample_backtest.py

cp backend/data/predictions.json frontend/src/assets/data/predictions.json
cp backend/data/backtest_results.json frontend/src/assets/data/backtest_results.json
cp backend/data/sample_matches.json frontend/src/assets/data/sample_matches.json
```

## Lancer le frontend

Angular 22 exige Node `22.22.3` ou une version compatible plus récente. Le
fichier `frontend/.nvmrc` fixe la version validée.

```bash
cd frontend
nvm use
npm install
npm start
```

## Builder et tester

```bash
cd frontend
nvm use
npm run build
npm test -- --watch=false
```

Le build de production écrit ses fichiers dans `frontend/dist/frontend/`. Les
dossiers `node_modules/`, `dist/` et `.angular/` restent ignorés par Git.

## Point d'environnement observé

Dans l'environnement de préparation, certaines commandes npm escaladées
utilisaient Node 18 malgré le Node 22 actif dans le shell courant. Le build a
donc été validé en préfixant explicitement le chemin Node 22 :

```bash
PATH=$HOME/.nvm/versions/node/v22.22.3/bin:$PATH npm run build
```
