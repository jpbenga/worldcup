# Model and Simulation

Le produit sépare deux responsabilités. `quant_hybrid_v2.2` est le moteur actif des prédictions pré-match individuelles. SimuAI Tournament Engine V3 est le moteur officiel de Road to the Trophy. Promouvoir V3 pour le tournoi n’a pas modifié les pronostics pré-match actifs.

V3 combine Elo courant, attaque et défense dérivées des scores historiques avec décroissance temporelle, puis produit une matrice de scores Poisson. En phase éliminatoire, le nul après 90 minutes est converti en probabilité de qualification à l’aide de l’écart Elo. La probabilité d’atteindre un tour n’est jamais utilisée comme force directe pour battre un adversaire.

Le backtest chronologique V2.14 porte sur 394 matchs de test. V3 obtient une log loss de `1.020`, contre `1.048` pour la baseline Elo. Dans le cas France–Suisse, l’ancien calcul favorisait la Suisse à `51.3 %`; V3 favorise la France à `68.7 %` tout en laissant une chance d’upset crédible à la Suisse.

Les garde-fous interdisent les inversions fortes non expliquées, les ajustements manuels par équipe et les signaux inventés. Blessures, lineups futures, qualité subjective d’effectif, odds et ranking FIFA absent ne sont pas utilisés.
