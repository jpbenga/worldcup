# Formats de données proposés

Les timestamps utilisent ISO 8601 UTC. `match_id` doit être stable entre données, prédictions et résultats. Les prédictions sont immuables et versionnées.

## Match

```json
{
  "match_id": "france_senegal_001",
  "home_team": "France",
  "away_team": "Sénégal",
  "kickoff_at": "2026-06-15T21:00:00Z",
  "competition": "World Cup 2026",
  "stage": "group",
  "group": "A"
}
```

## Entrées modèle recommandées

```json
{
  "match_id": "france_senegal_001",
  "home_expected_goals": 1.65,
  "away_expected_goals": 1.10,
  "home_elo": 1920,
  "away_elo": 1750,
  "home_field_advantage": 0,
  "rho": -0.05,
  "max_goals": 8,
  "features_as_of": "2026-06-15T14:00:00Z"
}
```

## Prédiction

```json
{
  "match_id": "france_senegal_001",
  "generated_at": "2026-06-15T14:03:00Z",
  "prediction_version": "v2026.06.15-1403",
  "score_matrix": {
    "0-0": 0.06,
    "1-0": 0.13,
    "1-1": 0.10,
    "2-0": 0.11,
    "2-1": 0.12
  },
  "markets": {
    "home_win": 0.54,
    "draw": 0.25,
    "away_win": 0.21,
    "home_or_draw": 0.79,
    "over_1_5": 0.68,
    "over_2_5": 0.47,
    "btts_yes": 0.49
  }
}
```

La matrice réelle doit contenir toutes les cases jusqu'à `max_goals`; l'extrait ci-dessus est abrégé. La somme doit être proche de 1.

## Signal pré-match à backtester

```json
{
  "match_id": "france_senegal_001",
  "generated_at": "2026-06-15T14:03:00Z",
  "prediction_version": "v2026.06.15-1403",
  "market": "home_or_draw",
  "probability": 0.79,
  "threshold": 0.75
}
```

## Résultat réel

```json
{
  "match_id": "france_senegal_001",
  "home_score": 1,
  "away_score": 0,
  "status": "finished"
}
```

Pour les phases à élimination directe, stocker séparément score à 90 minutes, prolongation, tirs au but et qualifié; ne pas surcharger `home_score`/`away_score` sans préciser le périmètre.

## Format fournisseur historique observé

Les fichiers `history_<league_id>.json` historiques utilisent les blocs `fixture`, `league`, `teams`, `goals` et parfois `stats.home/stats.away`. `normalizers.py` convertit le sous-ensemble fixture/résultat vers les formats ci-dessus. Le schéma brut fournisseur ne doit pas devenir le modèle de domaine du nouveau projet.
