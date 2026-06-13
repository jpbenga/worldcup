# Operations Runbook

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
