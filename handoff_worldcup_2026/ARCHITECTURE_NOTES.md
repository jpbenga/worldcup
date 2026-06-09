# Notes d'architecture

## Flux recommandé

```text
fournisseur -> adaptateur/normalizer -> match canonique + features pré-match
            -> expected_goals.compute_lambdas
            -> score_matrix.generate_score_matrix
            -> markets.derive_markets
            -> prediction snapshot immuable
            -> résultat réel -> backtesting.backtest_predictions
```

## Découpage retenu

- **score_prediction** calcule les intensités du modèle, sans connaître les marchés.
- **score_matrix** transforme deux intensités en distribution score par score.
- **markets** ne dépend que de la matrice, donc peut accueillir d'autres modèles.
- **backtesting** évalue des signaux sélectionnés; il ne régénère jamais une ancienne prédiction.
- **data_processing** protège le domaine contre le schéma d'un fournisseur.
- **utils** contient seulement des helpers sans logique métier.

## Choix entre versions historiques

`optimizer.py` est retenu comme référence des formules car ses fonctions sont explicites et son objectif de log loss est méthodologiquement plus solide. `xg-backtest.js` est retenu pour la fenêtre glissante et l'ordre chronologique. Les valeurs de `best_params.json` ne sont pas retenues car les métriques enregistrées montrent une exécution sans jeu d'entraînement valide. Les scripts `old/` servent seulement à confirmer l'existence d'évaluations OU/BTTS.

## Ce qui n'existe pas encore

L'ancien projet ne contient pas de moteur autonome de simulation de tournoi, de replay Monte-Carlo après résultat réel, de gestion de tableau à élimination directe, de persistance versionnée des prédictions ni de service applicatif. Ces éléments appartiennent au nouveau projet, pas au bundle recyclé.
