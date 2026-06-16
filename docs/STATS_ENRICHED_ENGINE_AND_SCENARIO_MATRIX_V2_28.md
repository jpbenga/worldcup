# V2.28 — Stats-Enriched Engine Candidate & Scenario-Aware Score Matrix

## Contexte utilisateur

Jeanpaul a recadré l'objectif: les statistiques API-Football ne doivent pas servir seulement à expliquer un résultat après match. Elles doivent être explorées comme renfort moteur, avec gestion explicite de la couverture partielle et sans fuite temporelle. Le second problème reste la matrice de score: elle doit raconter les scénarios plausibles du match, pas seulement lister des scores exacts dont les pourcentages écrasent l'intuition footballistique.

## Changement d'objectif

V2.27 et V2.27.1 concluaient prudemment vers une couche post-match. V2.28 corrige la direction: les tirs, xG, possession, corners, passes et événements sont transformés en features retardées. Les statistiques d'un match ne sont jamais utilisées pour prédire ce même match, mais elles peuvent enrichir les prédictions des matchs futurs.

La couverture partielle n'est pas bloquante par principe. Elle devient acceptable si le modèle sait que la donnée manque, si l'absence est encodée, si le backtest reste chronologique, et si les segments avec et sans xG sont mesurés séparément. Aucun xG manquant n'est inventé.

## Features statistiques

Le builder V2.28 produit `3 134` lignes de features: `3 062` matchs historiques et `72` matchs 2026. Il exploite uniquement les statistiques API-Football déjà en cache. Parmi les matchs historiques, `50` fixtures ont des statistiques de match exploitables comme source retardée.

Features construites:

- rolling last 3, 5 et 10;
- xG pour/contre et différentiel quand disponible;
- tirs, tirs cadrés, possession, corners, passes réussies;
- buts pour/contre, clean sheets, large wins;
- ratio tirs cadrés/tirs;
- buts moins xG;
- indicateurs de couverture et de missingness;
- âge de récence de la dernière source statistique.

L'audit anti-fuite vérifie `1 894` dates sources. Toutes sont strictement antérieures à la date cible. Les lineups sont exclues du candidat moteur tant qu'un timestamp de publication pré-match n'est pas prouvé.

## Candidat moteur enrichi

Le candidat est un overlay borné au-dessus de `quant_hybrid_v2.2`. Il teste une grille `alpha = 0.0, 0.05, 0.1, 0.2, 0.35, 0.5` sur validation. L'overlay utilise les signaux statistiques retardés disponibles et des indicateurs de couverture. Les segments avec xG et sans xG sont mesurés séparément.

Résultat: le meilleur réglage de promotion est `alpha=0.0`. Cela signifie que les essais statistiques non nuls ont été évalués, mais que la couverture actuellement disponible n'améliore pas assez le moteur actif.

| Split | Modèle | Accuracy | Log loss | Brier |
|---|---|---:|---:|---:|
| Validation | `quant_hybrid_v2.2` | 59,48 % | 0,909854 | 0,534761 |
| Validation | candidat sélectionné | 59,48 % | 0,909854 | 0,534761 |
| Test | `quant_hybrid_v2.2` | 60,22 % | 0,881184 | 0,515803 |
| Test | candidat sélectionné | 60,22 % | 0,881184 | 0,515803 |

Segments test:

- avec xG retardé des deux côtés: `6` matchs, log loss `0,896195`;
- sans xG retardé complet: `454` matchs, log loss `0,880986`;
- favoris forts: `131` matchs, accuracy `84,73 %`;
- signal matrice de large victoire: `267` matchs;
- larges victoires réelles: `104` matchs.

La calibration des larges victoires reste un problème: sur le test, les larges victoires réelles sont à `22,61 %` et la probabilité moyenne de large victoire issue de la matrice est `13,97 %`. Sur les larges victoires réelles, le top 5 score exact ne touche que `11,54 %`. C'est précisément pourquoi l'interface ne doit plus réduire la lecture à quelques scores exacts.

## Décision promotion

Le candidat V2.28 n'est pas promu. Il ne bat pas `quant_hybrid_v2.2` en log loss ni en Brier sur test. Les prédictions actives restent inchangées. Optuna n'est pas relancé.

La conclusion n'est pas que les statistiques sont inutiles. La conclusion est que l'échantillon statistique actuellement couvert est trop sparse pour justifier une promotion. La bonne suite est d'étendre la couverture historique et d'entraîner ensuite un vrai modèle deux-têtes ou ensemble coverage-aware.

## Matrice scénario-aware

La limite actuelle est produit autant que modèle: un score exact modal comme `1-0` peut être correct mathématiquement, mais insuffisant footballistiquement. V2.28 construit une vue qui affiche d'abord les familles:

- score repère;
- victoire courte;
- victoire contrôlée;
- victoire large;
- carton possible;
- match ouvert / fermé;
- BTTS;
- clean sheet;
- scores représentatifs par scénario.

Décision produit: les pourcentages de scores exacts ne doivent plus être l'élément central. Ils restent disponibles en détail avancé. Le premier niveau doit afficher `Score repère SimuAI` et `Scénarios SimuAI`.

## Allemagne–Curaçao

La nouvelle vue conserve `1-0` comme score repère, sans en faire toute l'histoire. Elle expose:

- Allemagne favorite: `64,14 %`;
- victoire large: `14,73 %`;
- Allemagne marque 4+ buts: `9,65 %`;
- match ouvert / Over 3,5: `25,64 %`;
- carton possible: `1,64 %`;
- scores représentatifs: `1-0`, `3-0`, `4-0`, `3-1`, `5-0`.

Le `7-1` n'est pas promu comme score probable. Il devient un score extrême compatible avec la famille large victoire/carton.

## Contrat unifié

V2.28 définit un contrat cible `Unified Match Outcome Distribution`. Une seule distribution par match devra alimenter:

- 1N2;
- score repère;
- scores représentatifs;
- familles de scénarios;
- over/under;
- BTTS;
- cotes intéressantes;
- Road to the Trophy;
- simulation groupes;
- simulation knockout.

Road to the Trophy n'est pas modifié en V2.28. Il ne devra consommer ce contrat qu'après inférence arbitraire fiable, benchmark chronologique et replay tournoi.

## Recommandations V2.29

1. Étendre la collecte statistique cache-first sur davantage de couples compétition-saison.
2. Réentraîner un vrai candidat deux-têtes: core historique sans stats avancées et booster stats récentes.
3. Évaluer séparément les segments avec xG, sans xG, favoris forts, gros écarts et larges victoires.
4. Modifier l'UI pour afficher les scénarios avant les pourcentages de scores exacts.
5. Préparer le contrat unifié pour la fiche match avant toute intégration Road to the Trophy.

## Limites

- Seulement `50` matchs source ont des statistiques exploitables dans le cache actuel.
- Les xG retardés complets sont rares sur le test.
- Les lineups ne sont pas utilisées faute de timestamp pré-match prouvé.
- Aucun moteur public ni pronostic actif n'est modifié.
- Le candidat enrichi est évalué mais non promu.
