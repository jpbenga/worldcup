# Guide d'intégration dans le prochain projet

## Fichiers à importer en priorité

1. `recycled_code/score_matrix/score_matrix.py`
2. `recycled_code/markets/market_derivation.py`
3. `recycled_code/score_prediction/expected_goals.py`
4. `recycled_code/backtesting/backtester.py`
5. `recycled_code/data_processing/normalizers.py`

Copier `recycled_code/` comme package ou l'installer depuis un futur package Python. Conserver les formats de `DATA_FORMATS.md` à la frontière stockage/API.

## Générer une matrice de score

```python
from recycled_code.score_prediction.expected_goals import compute_lambdas
from recycled_code.score_matrix.score_matrix import generate_score_matrix

home_lambda, away_lambda = compute_lambdas(1.6, 1.1, delta_elo=120, home_field_advantage=0)
matrix = generate_score_matrix(home_lambda, away_lambda, max_goals=8, rho=-0.05)
```

Sur terrain neutre, commencer avec `home_field_advantage=0`, puis calibrer. Tester plusieurs `max_goals` pour mesurer la masse tronquée.

## Déduire les marchés

```python
from recycled_code.markets.market_derivation import derive_markets
markets = derive_markets(matrix)
```

Le dictionnaire contient 1X2, doubles chances, over/under demandés, BTTS et cinq scores exacts principaux.

## Lancer un backtest

```python
from recycled_code.backtesting.backtester import backtest_predictions
report = backtest_predictions(predictions, results)
```

Chaque prédiction sélectionnée doit porter `match_id` et `market`; chaque résultat doit suivre le format canonique. En production, persister aussi `generated_at`, `prediction_version`, les probabilités complètes et les features disponibles avant match.

## Installer les dépendances

```bash
python -m pip install -r handoff_worldcup_2026/requirements_recycled.txt
python -m pytest handoff_worldcup_2026/tests
```

Le runtime actuel utilise uniquement Python standard. `pytest` sert aux tests. NumPy/SciPy/Optuna ne sont nécessaires que si l'optimiseur historique est reconstruit.

## Parties prêtes à l'emploi

- Génération et normalisation de matrice score par score.
- Agrégation des marchés demandés.
- Calcul de lambdas xG/Elo paramétrable.
- Validation simple de signaux par résultat.
- Adaptation basique du schéma API-Football.

## Parties à réécrire/construire

- Collecteur réseau sécurisé avec variables d'environnement et gestion de quota.
- Feature store international, référentiel d'équipes et pipeline de qualité.
- Entraînement/calibration chronologique Coupe du Monde.
- Simulateur de groupes, classements, tie-breaks, tableau final, prolongations et tirs au but.
- Re-simulation de milliers de scénarios après chaque résultat.
- Stockage immuable/versionné, métriques avancées, API et interface utilisateur.
