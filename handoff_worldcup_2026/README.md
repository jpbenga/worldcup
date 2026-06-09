# Bundle de recyclage — prototype Coupe du Monde 2026

Ce dossier est une extraction autonome et sans secret des briques football utiles du projet historique `drc-prototype`. Il ne constitue **pas** l'application Coupe du Monde finale : il fournit un socle vérifiable pour prédire des scores, produire une matrice, agréger des marchés, normaliser des données et backtester des signaux pré-match.

## Démarrage rapide

```bash
python -m pip install -r handoff_worldcup_2026/requirements_recycled.txt
python -m pytest handoff_worldcup_2026/tests
python handoff_worldcup_2026/examples/example_generate_score_matrix.py
python handoff_worldcup_2026/examples/example_derive_markets.py
python handoff_worldcup_2026/examples/example_backtest.py
```

## Contenu prêt à l'emploi

- `recycled_code/score_prediction/expected_goals.py` : modulation xG par Elo et construction de baselines glissantes.
- `recycled_code/score_matrix/score_matrix.py` : matrice Poisson avec correction Dixon–Coles et normalisation.
- `recycled_code/markets/market_derivation.py` : 1X2, doubles chances, over/under, BTTS et scores exacts.
- `recycled_code/backtesting/backtester.py` : validation de signaux face aux résultats réels.
- `recycled_code/data_processing/normalizers.py` : normalisation de noms et du format API-Football.

## Principes d'extraction

- Aucun fichier historique massif, `.env`, token ou identifiant API n'est inclus.
- Les modules runtime n'importent rien depuis l'ancien projet et utilisent uniquement la bibliothèque standard Python.
- La logique mathématique provient prioritairement de `drc-prototype/optimizer.py` et `drc-prototype/xg-backtest.js`; les paramètres optimisés historiques ne sont pas déclarés fiables pour une Coupe du Monde.
- Les marchés absents sous forme autonome dans l'ancien projet ont été ajoutés comme couche minimale autour de la matrice.

Lire ensuite `EXTRACTION_REPORT.md`, puis `NEXT_PROJECT_INTEGRATION_GUIDE.md`.
