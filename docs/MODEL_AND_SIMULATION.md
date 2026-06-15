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
