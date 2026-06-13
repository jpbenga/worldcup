# API-Football Active Source

## Objectif

V0.5 utilise les fixtures réelles et futures de la Coupe du Monde 2026 comme
source active du pipeline. Angular continue à lire uniquement des snapshots
JSON générés localement.

Depuis V0.5.1, API-Football est aussi la source par défaut de
`build_snapshots.py`. Si ses fichiers sont absents, le pipeline échoue avec une
erreur explicite : il ne revient jamais silencieusement aux données mock. Le
mode mock reste disponible uniquement via `--source mock`.

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

La normalisation produit `api_football_matches.json`, `api_football_teams.json`
et le contrat générique `teams.json`. Les groupes ne sont renseignés que
lorsqu'ils sont cohérents dans les standings. La table API annexe de classement
des meilleurs troisièmes n'écrase pas les groupes A à L. Les scores absents
restent `null`.

Les fixtures ne fournissant pas d'historique calibré, le baseline utilise des
entrées xG neutres explicitement marquées comme valeurs prototype non
calibrées. Le modèle Elo parallèle utilise uniquement les ratings issus du
mapping validé.

## Snapshots Angular

Le pipeline active les fixtures API-Football dans `matches.json`, génère les
prédictions baseline/Elo et leur comparaison, puis copie les fichiers vers
`frontend/src/assets/data/`.

Il publie aussi les équipes enrichies, les groupes, les classements disponibles,
les résumés de force Elo et l'audit de diversité des prédictions. Angular
présente ces données par groupe et ouvre le détail d'un match dans une modale.

Les matchs étant futurs et sans résultats, `backtest_results.json` porte le
statut `not_evaluable`. Aucun résultat mock n'est utilisé pour évaluer ces
fixtures réelles.
