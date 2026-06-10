# API-Football Active Source

## Objectif

V0.5 utilise les fixtures réelles et futures de la Coupe du Monde 2026 comme
source active du pipeline. Angular continue à lire uniquement des snapshots
JSON générés localement.

## Acquisition

La clé API reste exclusivement dans `.env`. Le fetcher réalise quatre appels
contrôlés et ne sauvegarde jamais la clé :

```bash
python3 backend/scripts/fetch_worldcup_api_football.py --season 2026
```

Les réponses brutes sont enregistrées dans :

```text
backend/data/raw/api_football/worldcup_2026/
```

Le dossier contient les fixtures, équipes, standings, rounds et un
`fetch_summary.json` machine-readable. Une erreur d'endpoint est conservée dans
ce résumé sans création de données de remplacement.

## Normalisation et prédictions

```bash
python3 backend/scripts/normalize_api_football_worldcup.py
python3 backend/scripts/build_snapshots.py --source api_football --model both
```

La normalisation produit `api_football_matches.json` et
`api_football_teams.json`. Les groupes ne sont renseignés que lorsqu'ils sont
cohérents dans les standings. Les scores absents restent `null`.

Les fixtures ne fournissant pas d'historique calibré, le baseline utilise des
entrées xG neutres explicitement marquées comme valeurs prototype non
calibrées. Le modèle Elo parallèle utilise uniquement les ratings issus du
mapping validé.

## Snapshots Angular

Le pipeline active les fixtures API-Football dans `matches.json`, génère les
prédictions baseline/Elo et leur comparaison, puis copie les fichiers vers
`frontend/src/assets/data/`.

Les matchs étant futurs et sans résultats, `backtest_results.json` porte le
statut `not_evaluable`. Aucun résultat mock n'est utilisé pour évaluer ces
fixtures réelles.
