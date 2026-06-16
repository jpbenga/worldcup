# V2.27.1 — Audit de couverture historique API-Football

## Contexte utilisateur

V2.27 avait démontré une couverture riche sur trois matchs récents, sans prouver que les mêmes données existaient sur l'historique utilisé par SimuMondial. Cet audit mesure un échantillon historique contrôlé avant toute création de feature modèle.

## Résumé exécutif

Le dataset actif contient `3062` matchs, `14` compétitions et `32` couples compétition-saison. Tous les matchs locaux sont déjà mappés à un fixture ID API-Football.

Tester cinq matchs pour chaque couple aurait demandé `640` appels. Pour respecter le plafond, l'audit a sélectionné `70` matchs, cinq par compétition, stratifiés de l'ancien au récent. Il a utilisé `0` appels live et `280` réponses en cache.

Conclusion: API-Football est utilisable maintenant pour une couche explicative post-match avec gestion explicite de la disponibilité. La couverture n'est pas encore suffisamment démontrée pour enrichir globalement l'algorithme ou conduire un backtest historique sans biais de sélection.

## Compétitions et années détectées

- Compétitions: Africa Cup of Nations, Asian Cup, CONCACAF Gold Cup, Copa America, Euro Championship, Friendlies, UEFA Nations League, World Cup, World Cup - Qualification Africa, World Cup - Qualification Asia, World Cup - Qualification CONCACAF, World Cup - Qualification Europe, World Cup - Qualification Oceania, World Cup - Qualification South America
- Années/saisons: 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026
- Plage de dates: `2014-06-12T20:00:00+00:00` à `2026-03-31T18:45:00+00:00`
- Mapping fixture ID: `3062/3062`

## Méthode d'échantillonnage

Le script découvre automatiquement le dataset local et tente d'abord jusqu'à cinq fixtures par compétition-saison. Le besoin idéal dépassant le quota, il applique le fallback documenté: cinq fixtures régulièrement espacées dans l'historique de chaque compétition. Les endpoints prioritaires sont `fixtures/statistics`, `fixtures/events`, `fixtures/lineups` et `fixtures/players`; aucune recherche ambiguë de fixture n'est nécessaire.

## Couverture globale observée

- Statistiques match: `74,3 %`
- xG: `55,7 %`
- Events: `98,6 %`
- Lineups: `98,6 %`
- Statistiques joueurs: `67,1 %`
- États agrégés: `{'not_ready': 24, 'fragile': 2, 'promising': 4}`

## Matrice de couverture

| Compétition | Saison | N | Stats | xG | Events | Lineups | Joueurs | Readiness |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Africa Cup of Nations | 2017 | 1 | 0,0 % | 0,0 % | 100,0 % | 100,0 % | 0,0 % | not_ready |
| Africa Cup of Nations | 2019 | 2 | 50,0 % | 0,0 % | 50,0 % | 50,0 % | 50,0 % | not_ready |
| Africa Cup of Nations | 2023 | 1 | 100,0 % | 100,0 % | 100,0 % | 100,0 % | 100,0 % | not_ready |
| Africa Cup of Nations | 2025 | 1 | 100,0 % | 100,0 % | 100,0 % | 100,0 % | 100,0 % | not_ready |
| Asian Cup | 2015 | 1 | 0,0 % | 0,0 % | 100,0 % | 100,0 % | 0,0 % | not_ready |
| Asian Cup | 2019 | 2 | 50,0 % | 0,0 % | 100,0 % | 100,0 % | 0,0 % | not_ready |
| Asian Cup | 2023 | 2 | 100,0 % | 100,0 % | 100,0 % | 100,0 % | 100,0 % | not_ready |
| CONCACAF Gold Cup | 2017 | 1 | 0,0 % | 0,0 % | 100,0 % | 100,0 % | 0,0 % | not_ready |
| CONCACAF Gold Cup | 2019 | 1 | 0,0 % | 0,0 % | 100,0 % | 100,0 % | 0,0 % | not_ready |
| CONCACAF Gold Cup | 2021 | 1 | 100,0 % | 0,0 % | 100,0 % | 100,0 % | 100,0 % | not_ready |
| CONCACAF Gold Cup | 2023 | 1 | 100,0 % | 100,0 % | 100,0 % | 100,0 % | 100,0 % | not_ready |
| CONCACAF Gold Cup | 2025 | 1 | 100,0 % | 100,0 % | 100,0 % | 100,0 % | 100,0 % | not_ready |
| Copa America | 2016 | 2 | 100,0 % | 0,0 % | 100,0 % | 100,0 % | 100,0 % | not_ready |
| Copa America | 2021 | 1 | 100,0 % | 0,0 % | 100,0 % | 100,0 % | 100,0 % | not_ready |
| Copa America | 2024 | 2 | 100,0 % | 100,0 % | 100,0 % | 100,0 % | 100,0 % | not_ready |
| Euro Championship | 2016 | 1 | 100,0 % | 0,0 % | 100,0 % | 100,0 % | 100,0 % | not_ready |
| Euro Championship | 2020 | 3 | 100,0 % | 0,0 % | 100,0 % | 100,0 % | 100,0 % | fragile |
| Euro Championship | 2024 | 1 | 100,0 % | 100,0 % | 100,0 % | 100,0 % | 100,0 % | not_ready |
| Friendlies | 2024 | 3 | 66,7 % | 66,7 % | 100,0 % | 100,0 % | 33,3 % | not_ready |
| Friendlies | 2025 | 2 | 100,0 % | 100,0 % | 100,0 % | 100,0 % | 100,0 % | not_ready |
| UEFA Nations League | 2024 | 5 | 100,0 % | 100,0 % | 100,0 % | 100,0 % | 100,0 % | promising |
| World Cup | 2014 | 2 | 0,0 % | 0,0 % | 100,0 % | 100,0 % | 0,0 % | not_ready |
| World Cup | 2018 | 1 | 100,0 % | 0,0 % | 100,0 % | 100,0 % | 100,0 % | not_ready |
| World Cup | 2022 | 2 | 100,0 % | 0,0 % | 100,0 % | 100,0 % | 100,0 % | not_ready |
| World Cup - Qualification Africa | 2023 | 5 | 40,0 % | 40,0 % | 100,0 % | 100,0 % | 0,0 % | not_ready |
| World Cup - Qualification Asia | 2026 | 5 | 80,0 % | 80,0 % | 100,0 % | 100,0 % | 60,0 % | fragile |
| World Cup - Qualification CONCACAF | 2026 | 5 | 100,0 % | 100,0 % | 100,0 % | 100,0 % | 100,0 % | promising |
| World Cup - Qualification Europe | 2024 | 5 | 100,0 % | 100,0 % | 100,0 % | 100,0 % | 100,0 % | promising |
| World Cup - Qualification Oceania | 2026 | 5 | 0,0 % | 0,0 % | 100,0 % | 100,0 % | 0,0 % | not_ready |
| World Cup - Qualification South America | 2026 | 5 | 100,0 % | 100,0 % | 100,0 % | 100,0 % | 100,0 % | promising |

## Disponibilité et limites

Les statistiques match mesurent tirs, possession, corners, passes et arrêts lorsqu'elles sont présentes. Les xG sont conservés comme absents lorsqu'ils ne sont pas renvoyés; aucune valeur n'est inventée. Les événements sont comparés au total de buts local comme contrôle minimal. Les compositions et statistiques joueurs sont mesurées séparément, avec leurs champs nuls.

L'échantillon couvre l'ancien, le milieu et le récent de chaque compétition, mais pas chaque saison. Les différences par saison restent donc indicatives et non exhaustives. Les flags de couverture fournisseur et cinq fixtures réussies ne suffisent pas à prouver une stabilité historique complète.

## Exploitabilité algorithme

- Backtest historique global: **non**, couverture par compétition-saison encore insuffisamment prouvée.
- Explication post-match: **oui**, avec fallback et indicateur de disponibilité.
- Futures features: **pas encore**; uniquement après audit exhaustif, agrégats retardés et backtest chronologique.
- Live: **pas encore**; nécessite une étude distincte des snapshots et délais.

## Recommandations V2.28

1. Livrer une couche post-match qui n'affiche que les champs réellement disponibles.
2. Étendre l'audit cache-first par lots à chacun des 32 couples compétition-saison.
3. Mesurer les valeurs nulles et ruptures de définition par année.
4. Construire ensuite un challenger de features retardées, limité aux segments validés et sans fuite temporelle.

## Prudences

Aucun moteur, aucune prédiction active, aucun entraînement, aucune exécution Optuna et aucun composant UI fonctionnel ne sont modifiés. Les réponses API brutes restent locales et hors commit.
