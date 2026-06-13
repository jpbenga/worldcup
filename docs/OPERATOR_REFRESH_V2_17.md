# Operator Refresh V2.17

Le wrapper opérateur orchestre le pipeline Matchday V2.10 existant et sa validation :

```bash
python3 backend/scripts/run_operator_refresh_v2_17.py --dry-run
python3 backend/scripts/run_operator_refresh_v2_17.py --no-fetch --simulations 50000
python3 backend/scripts/run_operator_refresh_v2_17.py --fetch --simulations 50000 --validate
```

Le mode `--dry-run` affiche exactement les commandes prévues et ne modifie aucun fichier. `--no-fetch` reconstruit depuis les données disponibles; `--fetch` autorise la récupération API; `--validate` exécute le validateur V2.10 après refresh. Les scripts dépendants sont vérifiés avant exécution et une erreur interrompt proprement l’orchestration.

Le manifest opérateur enregistre le mode, les étapes, la validation, les sorties critiques, avertissements et erreurs. Il affirme explicitement que les prédictions actives et Road to the Trophy ne doivent pas changer. La clé API n’est jamais affichée.
