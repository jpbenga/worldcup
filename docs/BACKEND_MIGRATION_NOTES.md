# Backend Migration Notes

## Objectif

Le dossier `backend/` fournit un premier pipeline autonome et simple :

```text
sample_matches.json
      -> generate_sample_predictions.py
      -> predictions.json
      -> run_sample_backtest.py
      -> backtest_results.json
```

Le dossier `handoff_worldcup_2026/` reste intact comme source d'origine.

## Modules copiés

| Source | Cible |
|---|---|
| `handoff_worldcup_2026/recycled_code/score_prediction/expected_goals.py` | `backend/prediction/expected_goals.py` |
| `handoff_worldcup_2026/recycled_code/score_matrix/score_matrix.py` | `backend/score_matrix/score_matrix.py` |
| `handoff_worldcup_2026/recycled_code/markets/market_derivation.py` | `backend/markets/market_derivation.py` |
| `handoff_worldcup_2026/recycled_code/backtesting/backtester.py` | `backend/backtesting/backtester.py` |

Les quatre modules ont été copiés sans changement de logique métier. L'import
relatif de `market_derivation.py` reste valide dans le package `backend`.

## Adaptateurs ajoutés

`backend/scripts/generate_sample_predictions.py` :

- approxime les xG de base avec un mélange simple forme offensive/défensive ;
- utilise `compute_lambdas`, `generate_score_matrix` et `derive_markets` ;
- convertit la matrice runtime `{score: probability}` vers le contrat JSON ;
- sépare les top scores des marchés ;
- écrit un snapshot `sample-v1` dans `backend/data/predictions.json`.

`backend/scripts/run_sample_backtest.py` :

- utilise le backtester copié pour le résumé ;
- évalue quatre marchés ;
- conserve les validations et les échecs avec la version, la probabilité et le
  résultat réel ;
- écrit `backend/data/backtest_results.json`.

## Commandes

Depuis la racine Git opérationnelle :

```bash
python3 backend/scripts/generate_sample_predictions.py
python3 backend/scripts/run_sample_backtest.py
```

## Points de vigilance

- Les matchs et résultats sont fictifs et servent uniquement à valider le flux.
- Les paramètres xG/Elo, `rho`, la confiance et `max_goals=5` ne sont pas
  calibrés pour la Coupe du Monde.
- La matrice est renormalisée après troncature.
- Le backtest d'exemple mesure la réalisation d'un marché, pas la calibration
  probabiliste.
- Toute prédiction réelle devra figer les données disponibles avant le coup
  d'envoi.
