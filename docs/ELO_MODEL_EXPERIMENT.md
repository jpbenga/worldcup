# Elo Model Experiment V0.4

## Objectif

V0.4 mesure l'impact de ratings Elo validés sur les prédictions baseline. Le
modèle Elo est expérimental : il ne remplace ni `predictions.json`, ni le
backtesting baseline, ni le modèle actuel affiché comme prédiction principale.

## Données utilisées

Les ratings proviennent de `backend/data/mappings/team_identity_map.json`. Cette
couche est obligatoire afin de relier sans ambiguïté les noms des matchs aux
équipes Elo. Un rating absent n'est jamais inventé : si une équipe ne possède
pas de mapping validé, la prédiction Elo reprend exactement les expected goals
du baseline.

## Ajustement

Le baseline calcule d'abord ses expected goals selon sa logique existante.
L'expérience applique ensuite :

```text
elo_factor = clamp((home_elo - away_elo) / 400, -0.35, 0.35)
adjusted_home_xg = baseline_home_xg * (1 + elo_factor * 0.20)
adjusted_away_xg = baseline_away_xg * (1 - elo_factor * 0.20)
```

Le poids par défaut `0.20` et le plafond `0.35` limitent volontairement
l'impact. Le signal baseline reste dominant.

## Fichiers générés

- `predictions.json` : baseline compatible avec le pipeline actuel ;
- `predictions_baseline.json` : copie explicite du baseline ;
- `predictions_elo.json` : modèle Elo expérimental ;
- `model_comparison.json` : deltas baseline vers Elo par match ;
- snapshots équivalents dans `backend/data/snapshots/` et
  `frontend/src/assets/data/`.

Le backtesting continue à lire uniquement `predictions.json`.

## Commandes

```bash
python3 backend/scripts/build_team_identity_map.py
python3 backend/scripts/validate_team_mappings.py
python3 backend/scripts/build_snapshots.py --model both
python3 backend/scripts/compare_prediction_models.py
```

Pour revenir au pipeline baseline :

```bash
python3 backend/scripts/build_snapshots.py
```

## Comparaison et décision

La comparaison expose les deltas 1X2, over 2.5, BTTS, les top scores et un
niveau d'impact. Ces résultats doivent être relus humainement avant toute
décision métier. V0.4 ne démontre pas encore que l'ajustement améliore la
qualité prédictive et ne l'intègre pas au modèle final.
