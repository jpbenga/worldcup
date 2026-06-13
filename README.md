# SimuMondial 2026

SimuMondial 2026 est une application de pronostics probabilistes et d’exploration de la Coupe du Monde. Elle combine les fixtures et résultats réels disponibles, des prédictions pré-match SimuAI et une expérience interactive Road to the Trophy.

## Fonctionnalités principales

- vue des groupes, matchs et résultats;
- pronostics pré-match produits par `quant_hybrid_v2.2`;
- détail de match et transparence des probabilités;
- Road to the Trophy alimenté par SimuAI Tournament Engine V3;
- 50 000 simulations complètes du tournoi avec groupes et qualifiés variables;
- parcours d’équipe, tableau projeté et explications contextuelles.

Road to the Trophy présente un scénario probabiliste cohérent, pas une certitude ni un tableau officiel FIFA. Les prédictions doivent être interprétées comme des estimations.

## Lancer l’application

```bash
cd "/Users/chloe/Desktop/dossier sans titre/worldcup/frontend"
nvm use
npm install
npm start
```

L’application est disponible sur `http://localhost:4200`.

## Commandes utiles

```bash
python3 backend/scripts/run_matchday_refresh_v2_10.py --fetch --simulations 50000
python3 backend/scripts/validate_matchday_refresh_v2_10.py

cd frontend
npm run build
npm test -- --watch=false
```

La documentation active commence dans [`docs/README.md`](docs/README.md). Les décisions et audits historiques sont conservés dans `docs/archive/`.
