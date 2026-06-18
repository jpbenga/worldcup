# V2.30 — Full Stats-Enriched Engine Production Candidate

## Contexte

V2.28 avait testé les statistiques API-Football comme features retardées, mais seulement avec le cache disponible à ce moment-là. L'échantillon exploitable était trop petit pour conclure sur le potentiel moteur. V2.29 a ensuite terminé la collecte complète cache-first/live progressive sur le périmètre historique local.

V2.30 relance donc un candidat moteur enrichi avec la collecte complète. La règle produit appliquée est celle donnée par Jeanpaul : comparer les moteurs, mais préparer comme cible de production le moteur qui utilise le plus de données, sauf blocage technique sérieux.

## Collecte consommée

La collecte V2.29 est complète :

- unités prévues : `12 248` ;
- unités complétées : `12 248` ;
- unités restantes : `0` ;
- fixtures avec au moins une donnée statistique : `2 924` ;
- échecs : `0` ;
- rate limit : `0` ;
- `ready_for_model_retest=true`.

Les features V2.30 couvrent `3 134` lignes : `3 062` matchs historiques et `72` matchs 2026. Elles s'appuient sur `2 126` matchs sources avec statistiques exploitables, `228` matchs sources avec xG, `2 907` avec événements et `1 936` avec statistiques joueurs. Ce n'est plus l'échantillon de couverture V2.27.1/V2.28.

## Features retardées

Le builder reconstruit des rolling features last 3, 5 et 10, strictement antérieures au match cible :

- xG pour, contre et différentiel quand disponible ;
- tirs, tirs cadrés, possession, corners, passes, arrêts gardien ;
- buts moins xG et buts encaissés moins xG concédé ;
- clean sheets, larges victoires et forme récente ;
- événements et agrégats joueurs ;
- indicateurs de couverture et de missingness ;
- âge de récence de la dernière source.

Les xG manquants ne sont pas inventés. Les lineups restent exclues des features prédictives tant qu'un timestamp de publication pré-match n'est pas prouvé.

## Audit anti-fuite

L'audit V2.30 a vérifié `51 155` dates sources. Toutes sont strictement antérieures au match cible. Une première exécution a détecté un cas de timestamp identique ; le builder a été durci pour filtrer explicitement `source_date < target_date` avant de construire chaque fenêtre.

Résultat final : `PASS`.

## Comparaison moteurs

Le candidat sélectionné est `stats_enriched_full_v2_30`, avec `alpha=0.35` et `coverage_aware=false`. Optuna n'a pas été relancé ; V2.30 utilise une grille bornée pour isoler la valeur de la collecte complète.

| Split | Moteur | Accuracy | Log loss | Brier |
|---|---:|---:|---:|---:|
| Validation | `quant_hybrid_v2.2` | 59,477 % | 0,909854 | 0,534761 |
| Validation | full stats candidate | 61,002 % | 0,908072 | 0,533819 |
| Test | `quant_hybrid_v2.2` | 60,217 % | 0,881184 | 0,515803 |
| Test | full stats candidate | 60,652 % | 0,864783 | 0,506084 |

Sur test, le candidat améliore la log loss de `1,861 %`, le Brier de `1,884 %` et l'accuracy de `0,435` point. L'écart de calibration des favoris passe de `0,086947` à `0,064258`. L'écart large-victoire passe de `0,086353` à `0,069552`.

## Décision production

Aucun blocage sérieux n'est détecté :

- pas de fuite temporelle ;
- pas de xG inventé ;
- pas de dégradation forte log loss/Brier/accuracy ;
- pas de calibration dangereuse favoris ou larges victoires ;
- pas de patch par équipe ;
- prédictions actives non écrasées ;
- Road to the Trophy non modifié ;
- aucun secret littéral détecté dans les scripts V2.30.

Décision : `recommend_promotion`.

La promotion n'est pas exécutée dans V2.30. Le fichier candidat `predictions_full_stats_candidate_v2_30.json` est généré, et un script séparé de promotion existe avec archivage et rollback, mais il nécessite une confirmation explicite.

## Matrice scénario-aware

La matrice V2.30 est construite depuis les prédictions candidates, sans remplacer la matrice active. Elle affiche d'abord les familles de scénarios :

- score repère ;
- issue probable ;
- victoire courte, contrôlée, large ;
- carton possible ;
- Over 2,5 et Over 3,5 ;
- match ouvert ou fermé ;
- BTTS ;
- clean sheet ;
- scores représentatifs ;
- scores exacts seulement en détail avancé.

Allemagne–Curaçao est présent dans le set candidat et les matchs à fort déséquilibre sont listés. Les exemples les plus déséquilibrés incluent notamment Maroc–Haïti, Brésil–Haïti, Pays-Bas–Suède, Angleterre–Ghana et Espagne–Arabie saoudite.

## Road to the Trophy

Road to the Trophy n'est pas modifié par V2.30. Le candidat sait produire des prédictions candidates pour les fixtures connues, mais il ne fournit pas encore un contrat d'inférence arbitraire pour toutes les confrontations futures possibles de groupe ou knockout.

Une V2.31 reste nécessaire pour unifier Road to the Trophy autour d'une `Unified Match Outcome Distribution`, puis rejouer et benchmarker le tournoi.

## Artefacts

- `backend/data/generated/full_stats_lagged_features_v2_30.json`
- `backend/data/generated/full_stats_feature_leakage_audit_v2_30.json`
- `backend/data/generated/full_stats_enriched_engine_v2_30_results.json`
- `backend/data/generated/full_stats_engine_promotion_decision_v2_30.json`
- `backend/data/generated/predictions_full_stats_candidate_v2_30.json`
- `backend/data/generated/full_stats_scenario_aware_matrix_v2_30.json`
- `backend/data/generated/full_stats_engine_road_to_trophy_impact_v2_30.json`
- `backend/data/generated/full_stats_engine_candidate_validation_v2_30.json`

## Limites

- La promotion active n'est pas exécutée.
- La collecte brute reste hors commit.
- Les lineups restent exclues des features prédictives.
- Le candidat est un overlay borné, pas un réentraînement Optuna complet.
- Road to the Trophy nécessite encore un contrat d'inférence arbitraire.
