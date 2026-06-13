# Rapport de démarrage du projet

## Résumé exécutif

L'analyse initiale a porté sur deux projets historiques (`drc-prototype` pour le
football et `drc-nba` pour le basket) ainsi que sur un bundle football autonome
préparé pour être réutilisé dans `handoff_worldcup_2026`.

Le bon point de départ n'est pas de reprendre les scripts historiques tels quels,
mais d'intégrer les modules Python autonomes du handoff. Ils couvrent déjà le
calcul de lambdas xG/Elo, la génération d'une matrice de scores, la déduction des
marchés principaux, une normalisation basique des données et un backtesting
minimal.

**Réponse explicite :** le repo contient déjà de quoi produire une matrice de
scores normalisée et faire un backtesting simple. Il ne faut pas réinventer ces
briques, mais il faut les adapter et les compléter pour la Coupe du Monde 2026,
la persistance versionnée, l'évaluation probabiliste et la simulation complète
du tournoi.

## Contenu du repo

| Chemin | Rôle | État |
|---|---|---|
| `handoff_worldcup_2026/` | Bundle Python autonome extrait du prototype football | Base recommandée |
| `backend/` | Pipeline minimal de prédiction et de backtesting | Prêt pour la V1 |
| `docs/` | Contrats, modèles Angular et rapports | À maintenir |
| `handoff_worldcup_2026/` | Bundle Python autonome extrait du prototype football | Base recommandée |
| `prototype_ia_coupe_du_monde_2026.md` | Document de cadrage produit | Source de contexte |

L'imbrication Git locale a été réparée le 10 juin 2026. La racine du dépôt
contient désormais directement les dossiers utiles.

## Fichiers importants

### Socle réutilisable

- `handoff_worldcup_2026/recycled_code/score_prediction/expected_goals.py` :
  calcul de lambdas modulés par xG/Elo et baselines glissantes.
- `handoff_worldcup_2026/recycled_code/score_matrix/score_matrix.py` :
  matrice Poisson, correction Dixon-Coles, normalisation et top scores.
- `handoff_worldcup_2026/recycled_code/markets/market_derivation.py` :
  1X2, doubles chances, over/under, BTTS et scores exacts.
- `handoff_worldcup_2026/recycled_code/backtesting/backtester.py` :
  validation simple de marchés face aux résultats terminés.
- `handoff_worldcup_2026/recycled_code/data_processing/normalizers.py` :
  normalisation de noms et adaptation d'un sous-ensemble API-Football.
- `handoff_worldcup_2026/tests/` : trois tests unitaires ciblés.
- `handoff_worldcup_2026/examples/` : exemples exécutables de la chaîne métier.

### Sources historiques analysées puis exclues du dépôt final

- `drc-prototype/optimizer.py` contenait les formules xG/Elo, Poisson/Dixon-Coles et
  optimisation chronologique.
- `drc-prototype/xg-backtest.js` contenait la baseline glissante et le backtest chronologique.
- `drc-prototype/backtest.js` contenait un historique détaillé de validations.
- `drc-prototype/history_*.json` utilisait le format fournisseur historique et des données de
  clubs, non adaptées directement aux sélections nationales.

Ces sources ne sont plus suivies car elles étaient fortement couplées et
contenaient des clés API codées en dur. Le handoff en conserve les briques
nettoyées utiles.

## Briques métier trouvées

| Brique | Disponibilité | Réutilisabilité | Adaptation nécessaire |
|---|---|---|---|
| Calcul xG/Elo | Oui | Élevée | Calibration sélections et terrain neutre |
| Matrice de scores | Oui | Élevée | Stabiliser le contrat JSON et mesurer la queue tronquée |
| Normalisation de matrice | Oui | Élevée | Conserver les contrôles de somme |
| Top scores exacts | Oui | Élevée | Adapter au contrat frontend |
| 1X2 et doubles chances | Oui | Élevée | Faible |
| Over/under et BTTS | Oui | Élevée | Faible |
| Backtesting de marchés | Oui, minimal | Moyenne | Historique versionné, résultat réel et métriques |
| Normalisation fournisseur | Oui, basique | Moyenne | Référentiel stable des sélections |
| Simulation de tournoi | Non | À construire | Groupes, meilleurs troisièmes et tableau final |
| Recalcul après résultat réel | Non orchestré | À construire | Pipeline de snapshots et re-simulation |
| Pipeline backend | Oui, exemple minimal | Élevée pour amorcer la V1 | Remplacer les données fictives et calibrer |
| Frontend Angular | Non | À construire | Lire des JSON/API, sans moteur métier |

## État du moteur de prédiction

Le moteur disponible est un socle statistique simple :

1. construction de xG de base à partir d'historiques glissants ;
2. modulation par différence Elo ;
3. génération Poisson avec correction Dixon-Coles ;
4. agrégation de la distribution en marchés.

Il fonctionne de manière autonome avec la bibliothèque standard Python. Il
n'est toutefois pas calibré pour les sélections nationales. Les paramètres
historiques de clubs, l'avantage domicile et `best_params.json` ne doivent pas
être repris comme valeurs fiables pour la Coupe du Monde.

## État de la matrice de scores

`generate_score_matrix` produit toutes les cases de `0-0` à
`max_goals-max_goals`, vérifie les probabilités négatives et normalise la masse
à 1. `top_exact_scores` trie les scores par probabilité.

La brique est directement exploitable. Son format runtime actuel est un
dictionnaire `{ "1-0": 0.13 }`, tandis que le contrat destiné au frontend est
une liste d'objets. Un adaptateur de sérialisation est donc nécessaire.

La renormalisation masque la masse au-delà de `max_goals`. Pour le prototype,
utiliser au moins `max_goals=5`, préférer `8`, puis documenter cette décision.

## État de la déduction des marchés

`derive_markets` calcule déjà :

- victoire domicile, nul, victoire extérieur ;
- `home_or_draw`, `away_or_draw`, `no_draw` ;
- over 0.5, 1.5, 2.5 et 3.5 ;
- under 2.5 et 3.5 ;
- BTTS oui/non ;
- top scores exacts.

La fonction renormalise défensivement sa matrice d'entrée. Les invariants
complémentaires sont couverts par un test. Les marchés combinés et handicaps
n'existent pas et ne sont pas prioritaires.

## État du backtesting

Le module extrait associe des prédictions à des résultats terminés et retourne
les validations, les échecs, le hit rate global et un résumé par marché. Les
scripts historiques montrent aussi une exécution chronologique et des rapports
détaillés.

La brique actuelle ne conserve pas encore dans chaque détail :

- la probabilité prédite ;
- `generated_at` et `prediction_version` ;
- le résultat réel complet ;
- `evaluated_at` ;
- les métriques de calibration comme Brier score et log loss.

Elle doit donc être enrichie avant de servir d'historique fiable. Les réussites
et les échecs doivent toujours être conservés.

## Formats de données observés

- Historique fournisseur : blocs `fixture`, `league`, `teams`, `goals` et
  parfois `stats`.
- Bundle extrait : dictionnaires Python en `snake_case`.
- Matrice runtime : dictionnaire `score -> probability`.
- Contrats cibles : JSON canonique en `snake_case`, puis interfaces Angular en
  `camelCase`.

Les contrats cibles sont définis dans `docs/DATA_CONTRACTS.md`.

## Tests et vérifications

Tests présents :

- normalisation et top scores de la matrice ;
- sommes complémentaires des marchés ;
- validation simple d'un backtest.

Vérifications réalisées les 9 et 10 juin 2026 :

- les trois exemples Python du handoff s'exécutent correctement ;
- le pipeline `backend/` génère trois prédictions conformes et backteste douze
  signaux en conservant réussites et échecs ;
- `python3 -m pytest handoff_worldcup_2026/tests -q` ne démarre pas car
  `pytest` n'est pas installé dans le Python système ;
- aucun test Angular n'existe, car aucune application Angular n'a encore été
  créée ;
- les `package.json` historiques n'exposent pas de vraie suite de tests.

## Briques absentes ou incomplètes

- calendrier et dataset canonique de la Coupe du Monde 2026 ;
- référentiel stable d'identifiants de sélections ;
- calibration sur matchs internationaux ;
- snapshots immuables et versionnés de prédictions ;
- stockage de l'historique de backtesting complet ;
- simulation des groupes, tie-breaks, meilleurs troisièmes et tableau final ;
- traitement séparé du temps réglementaire, prolongations et tirs au but ;
- orchestrateur de recalcul après chaque résultat ;
- données réelles et orchestration de production autour du pipeline backend ;
- frontend Angular et back-office personnel.

## Risques techniques

- Fuite temporelle si des données postérieures au coup d'envoi entrent dans une
  prédiction ou un backtest.
- Mauvaise calibration en réutilisant des paramètres de championnats de clubs.
- Identités d'équipes instables si les noms remplacent les identifiants.
- Confusion entre score à 90 minutes, après prolongation et résultat qualifié.
- Perte de masse dans la queue de distribution, masquée par renormalisation.
- Couplage aux formats API-Football si le schéma fournisseur devient le domaine.
- Réintroduction accidentelle de sources historiques contenant des secrets ou
  des environnements générés.

## Structure simple proposée

```text
worldcup/
├── frontend/                 # Application Angular
├── backend/
│   ├── prediction/           # xG/Elo et orchestration
│   ├── score_matrix/         # Génération et sérialisation
│   ├── markets/              # Agrégation depuis la matrice
│   ├── backtesting/          # Évaluation et historique
│   ├── simulations/          # Tournoi, plus tard
│   └── data/                 # JSON canoniques générés
├── docs/
└── handoff_worldcup_2026/    # Source nettoyée des briques métier
```

Pour la première version, un seul package Python sous `backend/` et des fichiers
JSON statiques suffisent. Il n'est pas nécessaire de créer des microservices.

## Prochaines étapes

1. Remplacer les données fictives par un petit jeu de données international
   vérifié.
2. Calibrer les entrées xG/Elo et la méthode de confiance.
3. Ajouter des métriques probabilistes au backtesting.
4. Initialiser Angular pour lire les JSON désormais stabilisés.
