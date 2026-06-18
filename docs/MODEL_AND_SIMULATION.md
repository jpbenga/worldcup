# Model and Simulation

Le produit sépare deux responsabilités. `quant_hybrid_v2.2` est le moteur actif des prédictions pré-match individuelles. SimuAI Tournament Engine V3 est le moteur officiel de Road to the Trophy. Promouvoir V3 pour le tournoi n’a pas modifié les pronostics pré-match actifs.

V3 combine Elo courant, attaque et défense dérivées des scores historiques avec décroissance temporelle, puis produit une matrice de scores Poisson. En phase éliminatoire, le nul après 90 minutes est converti en probabilité de qualification à l’aide de l’écart Elo. La probabilité d’atteindre un tour n’est jamais utilisée comme force directe pour battre un adversaire.

Le backtest chronologique V2.14 porte sur 394 matchs de test. V3 obtient une log loss de `1.020`, contre `1.048` pour la baseline Elo. Dans le cas France–Suisse, l’ancien calcul favorisait la Suisse à `51.3 %`; V3 favorise la France à `68.7 %` tout en laissant une chance d’upset crédible à la Suisse.

Les garde-fous interdisent les inversions fortes non expliquées, les ajustements manuels par équipe et les signaux inventés. Blessures, lineups futures, qualité subjective d’effectif, odds et ranking FIFA absent ne sont pas utilisés.

V2.19 ne remplace pas V3 et ne modifie pas ses probabilités. Il sélectionne parmi les parcours complets persistés celui qui minimise la surprise globale des rangs, qualifications et tours. Les probabilités marginales sur 50 000 simulations restent séparées du scénario central affiché.

L'audit V2.20 conclut que les 50 000 tirages sont réels et suffisamment stables, mais que la priorité doit porter sur le modèle et les règles qu'ils répètent. Le moteur cible doit encoder le bracket officiel, nettoyer les scores 90 minutes/prolongation/tirs au but, réutiliser le meilleur modèle historiquement validé du projet pour les confrontations arbitraires et passer un replay historique complet au niveau tournoi.

## Audit de cohérence V2.26

La prédiction match visible et Road to the Trophy ne consomment pas encore la même distribution. `quant_hybrid_v2.2` produit les probabilités pré-match actives et une matrice Poisson `0-7`. Road to the Trophy V4 utilise une distribution tête-à-tête séparée fondée sur l'Elo externe et des profils de buts historiques pondérés, car le bundle actif n'est pas persisté pour les confrontations arbitraires futures.

Les résultats officiels terminés sont verrouillés dans la simulation tournoi, mais ils ne mettent pas à jour la force future d'une équipe. Sans tirs, possession ou xG, le moteur ne distingue pas un nul dominé d'un nul chanceux. La cible recommandée est une distribution de match unifiée, historiquement validée, réutilisable par la fiche match, la matrice et chaque phase du tournoi.

## Exploration statistique V2.27

API-Football rend disponibles, pour les trois matchs terminés testés, les statistiques de match, événements, compositions, statistiques joueurs et `expected_goals`. Ces données ne sont pas encore collectées par le refresh principal ni consommées par les moteurs. Elles permettent immédiatement une couche d'explication post-match, mais ne deviennent des features prédictives qu'après audit de couverture historique, gestion des valeurs manquantes et backtest chronologique.

La matrice de score contient déjà des familles de scénarios utiles obtenues par agrégation de cellules : marges de victoire, buts équipe, over/under, BTTS, clean sheet, victoire large et carton. Une future distribution unifiée doit exposer ces familles à la fiche match et à Road to the Trophy sans remplacer les prédictions actives avant validation.

## Couverture historique API-Football V2.27.1

Le dataset historique actif contient 3 062 matchs, 14 compétitions API-Football et 32 couples compétition-saison. L'audit V2.27.1 a appliqué un échantillon quota-sûr de 70 fixtures, cinq par compétition, après fallback depuis un plan idéal de 640 appels.

La couverture observée est forte pour les événements et compositions, plus fragile pour les statistiques match, les xG et les statistiques joueurs. Ces données sont donc validées comme matière d'explication post-match avec indicateur de disponibilité, mais pas encore comme features globales de `quant_hybrid_v2.2`, ni comme base suffisante pour un backtest historique sans audit exhaustif par compétition-saison.

## Candidat full stats V2.30

Après collecte complète V2.29, V2.30 reconstruit les features statistiques retardées depuis le cache historique complet. Le candidat `stats_enriched_full_v2_30` consomme tirs, xG quand disponible, possession, corners, passes, événements, agrégats joueurs, formes rolling et indicateurs de missingness. Les sources sont strictement antérieures au match cible et les lineups restent exclues faute de timestamp pré-match prouvé.

Sur test, le candidat améliore `quant_hybrid_v2.2` en log loss (`0,864783` contre `0,881184`), Brier (`0,506084` contre `0,515803`) et accuracy (`60,652 %` contre `60,217 %`). La décision V2.30 recommande la promotion du candidat full stats.

Depuis V2.30.1, le moteur actif des prédictions pré-match individuelles est `stats_enriched_full_v2_30`. `quant_hybrid_v2.2` reste archivé comme moteur précédent et rollback possible. Road to the Trophy reste inchangé tant qu'une distribution unifiée réutilisable pour toute confrontation future n'est pas validée.

## Candidat stats-enriched et scénarios V2.28

V2.28 recadre l'usage des statistiques: elles doivent être explorées comme features retardées pour les matchs futurs. Le builder produit des rolling features last 3/5/10, des indicateurs de couverture et des indicateurs de missingness; les xG absents ne sont pas inventés. L'audit anti-fuite confirme que les sources utilisées précèdent toujours le match cible.

Le candidat enrichi est évalué contre `quant_hybrid_v2.2`, mais non promu: le meilleur réglage de promotion reste l'absence d'overlay statistique, faute de couverture suffisante pour améliorer log loss et Brier. La matrice de score évolue en revanche côté contrat produit: le score exact modal devient un score repère, tandis que les familles de scénarios et scores représentatifs doivent être affichés avant les pourcentages exacts.

## Collecte statistique complète V2.29

V2.28 ne conclut pas sur le potentiel final des statistiques API-Football: son volume source était trop faible. V2.29 ajoute donc un collecteur complet, progressif et relançable pour les `3 062` matchs historiques mappés. La collecte vise `12 248` unités `fixture_id:endpoint`, avec cache-first, reprise exacte, plafond d'appels live, backoff et circuit breaker.

Le modèle ne doit pas être retesté avant une collecte suffisante. Les données brutes restent dans un cache local ignoré par Git; seuls le manifest, le résumé et la validation sont versionnés.
