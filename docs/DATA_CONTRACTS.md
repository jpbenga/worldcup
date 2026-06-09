# Contrats de données

## Principes

- Les JSON backend utilisent `snake_case`.
- Les timestamps utilisent ISO 8601 en UTC, avec suffixe `Z`.
- `match_id` est stable et partagé par match, prédictions, résultats et
  backtests.
- Une prédiction publiée est immuable. Une nouvelle exécution crée une nouvelle
  `prediction_version`.
- Les probabilités sont des nombres entre `0` et `1`.
- Les résultats et backtests conservent les réussites comme les échecs.
- Angular convertit ces contrats vers les modèles `camelCase` documentés dans
  `ANGULAR_MODELS.md`.

## Match

```json
{
  "match_id": "france_senegal_001",
  "home_team": "France",
  "away_team": "Sénégal",
  "kickoff_at": "2026-06-15T21:00:00Z",
  "competition": "World Cup 2026",
  "stage": "group",
  "group": "A",
  "status": "scheduled"
}
```

Règles :

- `status` vaut `scheduled`, `live` ou `finished`.
- `group` est facultatif hors phase de groupes.
- Les scores réels ne sont pas nécessaires dans un match planifié. Ils peuvent
  être joints côté lecture depuis le contrat `RealResult`.

## Entrées modèle

Ce contrat n'est pas envoyé au frontend. Il permet de reproduire une prédiction.

```json
{
  "match_id": "france_senegal_001",
  "home_expected_goals": 1.65,
  "away_expected_goals": 1.1,
  "home_elo": 1920,
  "away_elo": 1750,
  "home_field_advantage": 0,
  "rho": -0.05,
  "max_goals": 8,
  "features_as_of": "2026-06-15T14:00:00Z"
}
```

`features_as_of` doit être antérieur au coup d'envoi afin d'éviter la fuite
temporelle.

## Score matrix

```json
{
  "match_id": "france_senegal_001",
  "max_goals": 5,
  "probabilities": [
    {
      "score": "0-0",
      "home_goals": 0,
      "away_goals": 0,
      "probability": 0.06
    },
    {
      "score": "1-0",
      "home_goals": 1,
      "away_goals": 0,
      "probability": 0.13
    }
  ]
}
```

Règles :

- La liste contient toutes les cases de `0-0` à
  `max_goals-max_goals`, soit `(max_goals + 1)²` éléments.
- `max_goals` est au minimum `5`; `8` est recommandé pour limiter la troncature.
- La somme des probabilités est égale à `1` à une tolérance de `1e-9`.
- Chaque objet respecte `score == "${home_goals}-${away_goals}"`.
- Les top scores sont dérivés en triant cette liste par probabilité décroissante.

Le moteur actuel retourne un dictionnaire `{ "1-0": 0.13 }`. Le backend doit
faire la conversion vers cette liste à la frontière JSON, sans déplacer la
logique métier dans Angular.

## Match prediction

```json
{
  "match_id": "france_senegal_001",
  "generated_at": "2026-06-15T14:03:00Z",
  "prediction_version": "v2026.06.15-1403",
  "score_matrix": {
    "match_id": "france_senegal_001",
    "max_goals": 5,
    "probabilities": []
  },
  "markets": {
    "home_win": 0.54,
    "draw": 0.25,
    "away_win": 0.21,
    "home_or_draw": 0.79,
    "away_or_draw": 0.46,
    "no_draw": 0.75,
    "over_0_5": 0.94,
    "over_1_5": 0.68,
    "over_2_5": 0.47,
    "over_3_5": 0.25,
    "under_2_5": 0.53,
    "under_3_5": 0.75,
    "btts_yes": 0.49,
    "btts_no": 0.51
  },
  "confidence": "medium",
  "top_scores": [
    {
      "score": "1-0",
      "home_goals": 1,
      "away_goals": 0,
      "probability": 0.13
    }
  ]
}
```

Règles :

- `confidence` vaut `low`, `medium` ou `high`. Sa méthode de calcul doit être
  documentée avant usage.
- `top_scores` contient un sous-ensemble trié de la matrice, généralement cinq
  éléments.
- `generated_at` et `prediction_version` ne changent jamais après publication.
- Invariants : `home_win + draw + away_win ~= 1`,
  `btts_yes + btts_no ~= 1`, `over_2_5 + under_2_5 ~= 1`.

## Real result

```json
{
  "match_id": "france_senegal_001",
  "home_score": 1,
  "away_score": 0,
  "status": "finished"
}
```

Les scores représentent le temps réglementaire. Pour une phase à élimination
directe, ajouter ultérieurement des champs explicites pour prolongation, tirs au
but et équipe qualifiée au lieu de surcharger `home_score` et `away_score`.

## Backtest result

```json
{
  "match_id": "france_senegal_001",
  "prediction_version": "v2026.06.15-1403",
  "generated_at": "2026-06-15T14:03:00Z",
  "market_name": "home_or_draw",
  "predicted_probability": 0.79,
  "actual_result": true,
  "validated": true,
  "real_result": {
    "home_score": 1,
    "away_score": 0
  },
  "evaluated_at": "2026-06-15T23:00:00Z"
}
```

Règles :

- `validated` indique si le marché prédit s'est réalisé. Il ne doit pas servir à
  filtrer les échecs hors de l'historique.
- `actual_result` est le booléen obtenu en évaluant `market_name` contre le
  résultat réel ; pour ce contrat, il est identique à `validated`.
- `predicted_probability`, `prediction_version` et `generated_at` proviennent
  du snapshot original, jamais d'un recalcul postérieur.
- Le backtesting n'évalue que des prédictions générées avant le coup d'envoi.

## Fichiers JSON proposés pour la V1

```text
backend/data/matches.json
backend/data/predictions.json
backend/data/results.json
backend/data/backtest_results.json
```

Chaque fichier peut contenir une liste de contrats du type correspondant. Ce
flux statique est suffisant pour la première application Angular.
