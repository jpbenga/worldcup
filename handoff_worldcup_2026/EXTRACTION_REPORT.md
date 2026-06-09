# Rapport d'extraction

## 1. Résumé de ce qui a été trouvé

Le projet historique contient une chaîne football exploitable mais fortement couplée à des scripts ponctuels : ingestion API-Football, enrichissement des rencontres avec statistiques/xG, historique Elo, calcul de lambdas xG/Elo, distribution Poisson corrigée Dixon–Coles, agrégation 1X2/double chance et backtests chronologiques. La version mathématique la plus explicite est dans `drc-prototype/optimizer.py`; `drc-prototype/xg-backtest.js` confirme son usage en situation chronologique et apporte la baseline glissante attaque/défense.

Des secrets ou fichiers de configuration sensibles ont été détectés et exclus du bundle.

## 2. Composants réutilisables

| Composant | Source historique | Destination | Réutilisabilité |
|---|---|---|---|
| Probabilité Elo et lambdas xG/Elo | `drc-prototype/optimizer.py`, `drc-prototype/xg-backtest.js` | `recycled_code/score_prediction/expected_goals.py` | Élevée après calibration |
| Poisson et Dixon–Coles | mêmes sources | `recycled_code/score_matrix/score_matrix.py` | Élevée |
| Baseline xG glissante | `drc-prototype/xg-backtest.js` | `recycled_code/score_prediction/expected_goals.py` | Moyenne à élevée |
| Backtest chronologique / validation | `drc-prototype/xg-backtest.js`, `drc-prototype/backtest.js`, `drc-prototype/optimizer.py` | `recycled_code/backtesting/backtester.py` | Moyenne |
| Normalisation noms/fixtures | `drc-prototype/audit_teams.py`, `drc-prototype/1_download.js`, `drc-prototype/update.js` | `recycled_code/data_processing/normalizers.py` | Moyenne |
| Déduction de marchés | logique partielle dans les backtests | `recycled_code/markets/market_derivation.py` | Élevée, ajout minimal |

## 3. Composants non retenus et pourquoi

- Les interfaces HTML/serveurs de `backtest.js`, `xg-backtest.js` et `3_scanner.js` : présentation couplée aux scripts, non nécessaire au moteur.
- La logique de paris, bankroll, Kelly, cotes et bookmakers : hors périmètre du prototype de compétition et potentiellement risquée.
- Les scripts API (`1_download.js`, `update.js`, `enrich-all-history.js`) : ils contiennent de la configuration sensible et sont liés à un fournisseur. Seuls leurs formats et transformations pures ont été conservés.
- `best_params.json` : les pertes déclarées et tailles d'entraînement indiquent une optimisation invalide/inexploitable; les valeurs ne doivent pas devenir des défauts.
- Les historiques JSON, archives Elo, résultats et fichiers de paris : volumineux, spécifiques aux ligues, non nécessaires au bundle et susceptibles de contenir des données non redistribuables.
- Les anciennes versions sous `drc-prototype/old/` : remplacées par des versions plus récentes ou trop couplées.
- Les environnements `venv/` et `node_modules/` : dépendances générées, jamais sources réutilisables.

## 4. Fichiers copiés ou adaptés

Aucun fichier source n'a été copié aveuglément. Les formules et contrats utiles ont été isolés et adaptés en modules Python autonomes. Les adaptations principales sont : suppression des accès disque globaux, suppression des appels réseau et secrets, validation des entrées, normalisation explicite de la matrice tronquée, représentation uniforme `"home-away"`, imports locaux et tests minimaux.

## 5. Dépendances nécessaires

- Runtime du bundle : Python 3.9+ et bibliothèque standard.
- Tests : `pytest`.
- Reproduction facultative de l'optimiseur historique : `numpy`, `scipy`, `optuna` et un dataset chronologique propre.
- Ingestion future : client HTTP/fournisseur à choisir dans le nouveau projet; volontairement absent du bundle.

## 6. Points de vigilance

- Une matrice bornée à `max_goals` perd de la masse de probabilité; le bundle la renormalise afin que les marchés soient cohérents.
- Dixon–Coles peut produire des probabilités négatives avec un `rho` inadapté; le générateur lève alors une erreur.
- La Coupe du Monde comporte peu de données récentes par sélection, des terrains neutres, prolongations et tirs au but : la calibration de ligue ne peut pas être reprise telle quelle.
- Le backtesting doit figer `generated_at`, `prediction_version` et les données disponibles avant coup d'envoi pour éviter la fuite temporelle.
- Les formats API-Football sont documentés comme source historique, mais doivent être placés derrière un adaptateur fournisseur.

## 7. Recommandations pour le nouveau projet

1. Adopter les formats canoniques de `DATA_FORMATS.md` et stocker chaque prédiction immuablement.
2. Utiliser la matrice et les marchés tels quels pour un premier prototype, puis tester calibration et sensibilité à `max_goals`/`rho`.
3. Réentraîner les paramètres sur des matchs internationaux avec validation chronologique et comparaison à une baseline.
4. Séparer temps réglementaire, prolongations et tirs au but dans la simulation de tournoi.
5. Construire un orchestrateur de milliers de simulations au-dessus de ces briques; il n'existe pas dans l'ancien projet.
6. Ajouter Brier score, log loss, calibration par bucket et suivi par version de modèle.
