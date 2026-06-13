# Operations Runbook

## Main local command

```bash
python3 backend/scripts/start_local_app_v2_18.py --auto-refresh --fetch --simulations 50000
```

Alternatives :

```bash
python3 backend/scripts/start_local_app_v2_18.py --auto-refresh --no-fetch --simulations 50000
python3 backend/scripts/start_local_app_v2_18.py --force-refresh --fetch --simulations 50000
python3 backend/scripts/start_local_app_v2_18.py --no-refresh
python3 backend/scripts/start_local_app_v2_18.py --auto-refresh --no-start
```

Cette commande est locale uniquement. La clé API reste côté Python; Angular lit seulement les assets générés. La transparence et Road to the Trophy V3 sont reconstruits lorsque les résultats officiels changent. La simulation lourde n’est sautée que lorsque le détecteur confirme que cela est sûr.

## Daily operator workflow

```bash
python3 backend/scripts/operator_doctor_v2_17.py
python3 backend/scripts/run_operator_refresh_v2_17.py --dry-run
python3 backend/scripts/run_operator_refresh_v2_17.py --fetch --simulations 50000 --validate
python3 backend/scripts/build_data_freshness_status_v2_17.py
python3 backend/scripts/preflight_v2_17.py
```

Le doctor et le dry-run doivent précéder tout refresh. Le refresh réel peut modifier de nombreux artefacts Matchday; vérifier le scope avant de les indexer.

## Matchday refresh

Depuis la racine du dépôt :

```bash
python3 backend/scripts/run_matchday_refresh_v2_10.py --fetch --simulations 50000
python3 backend/scripts/validate_matchday_refresh_v2_10.py
```

Le refresh peut modifier de nombreux artefacts generated, snapshots et frontend. Vérifier précisément le diff avant toute indexation.

## Frontend

```bash
cd frontend
nvm use
npm install
npm start
```

L’application est disponible sur `http://localhost:4200`.

```bash
npm run build
npm test -- --watch=false
```

## Local frontend

```bash
cd frontend
nvm use
npm start
```

## Before commit

```bash
python3 backend/scripts/preflight_v2_17.py
cd frontend
nvm use
npm run build
npm test -- --watch=false
cd ..
```

## What must not change

- artefacts `quant_hybrid_v2.2`;
- `predictions.json`;
- résumé d’étude Optuna;
- `road_to_the_trophy_engine.json`;
- secrets et fichier `.env`;
- artefacts locaux de refresh hors scope.

## Contrôles avant push

```bash
git status --short
git diff --check
git diff --cached --check
git ls-files | grep -E 'node_modules|dist|build|venv|__pycache__|\.pyc|\.env$|\.idx' | head
git grep -n "API_FOOTBALL_KEY\|x-apisports-key" -- . ':!.env.example'
find . -type f -size +10M -not -path "./.git/*" -not -path "./frontend/node_modules/*" -print
```

Ne jamais utiliser `git add .` dans un worktree contenant des refreshs ou artefacts hors scope. Les prédictions actives et le moteur Road to the Trophy doivent faire l’objet d’un diff explicite avant chaque livraison.
