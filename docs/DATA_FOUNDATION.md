# Data Foundation V0.2

## Objectif

La fondation de données sépare explicitement les entrées, les transformations,
les sorties du modèle et les évaluations. Chaque snapshot publié expose sa
provenance afin que l'interface ne présente jamais une donnée de démonstration
comme une donnée réelle.

## Catégories

| Dossier | Rôle |
|---|---|
| `backend/data/mock/` | Jeux de démonstration locaux |
| `backend/data/raw/` | Futures données sources reçues sans transformation |
| `backend/data/normalized/` | Données converties au contrat interne |
| `backend/data/generated/` | Prédictions produites par le modèle |
| `backend/data/evaluated/` | Résultats de backtest et mesures |
| `backend/data/snapshots/` | Contrats stables publiés pour les consommateurs |

Les fichiers actuels sont tous dérivés de données `mock`. Les matchs, scores
finaux et paramètres de modèle ne représentent pas les rencontres officielles
de la Coupe du Monde 2026.

## Provenance

`backend/data/data_sources.json` décrit les sources actives, leur catégorie,
leur chemin et le booléen `is_real_data`. Les matchs normalisés, prédictions et
résultats évalués transportent aussi leur provenance dans leur propre contrat.

L'interface Angular charge la copie publiée dans
`frontend/src/assets/data/data_sources.json` et affiche des badges explicites.

## Workflow unique

Depuis la racine du dépôt :

```bash
python3 backend/scripts/build_snapshots.py
```

Cette commande :

1. normalise les matchs de démonstration ;
2. génère les prédictions ;
3. exécute le backtest ;
4. produit le registre de provenance ;
5. publie les quatre snapshots dans `backend/data/snapshots/` et les copie vers
   `frontend/src/assets/data/`.

## Prochaine étape : données manuelles ou API

Une source manuelle validée pourra être déposée dans `raw/`, puis normalisée
avec `source_type: manual`. Une intégration API suivra le même chemin avec
`source_type: api` et `is_real_data: true`, après contrôle de la fraîcheur, des
identifiants de match et des conditions de licence.
