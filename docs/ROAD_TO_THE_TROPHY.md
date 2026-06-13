# Road to the Trophy

Road to the Trophy est l’expérience centrale de simulation et d’exploration du tournoi. L’utilisateur peut zoomer, se déplacer, inspecter un groupe, suivre une équipe et comprendre chaque rencontre du chemin projeté.

SimuAI Tournament Engine V3 est l’unique moteur public de cette fonctionnalité. Il génère 50 000 tournois complets, verrouille les résultats réels déjà joués, simule les matchs de groupes restants, recalcule les classements, varie les qualifiés et décide chaque match éliminatoire avec un modèle de confrontation tête-à-tête.

Le scénario affiché est un parcours complet cohérent choisi parmi les parcours persistés par un score global de représentativité V2.19. La sélection évalue les rangs de groupe, qualifications et tours éliminatoires sans imposer un champion ni une équipe. Il contient un vainqueur projeté, une finale projetée, les résultats de groupe, le tableau, les parcours d’équipe et les explications contextuelles des matchs.

Dans chaque groupe, le classement du scénario central et les chances sur 50 000 simulations sont présentés séparément. Une probabilité marginale décrit une fréquence sur tous les tournois; elle n’est pas le classement du parcours affiché.

Limites connues : le mapping officiel du tableau 2026 n’est pas encore disponible; seules cent trajectoires complètes sont persistées pour l’exploration, même si les 50 000 ont été générées et agrégées; les blessures, compositions futures et valeurs d’effectif ne sont pas utilisées faute de données fiables.

Lorsqu’un nouveau résultat officiel est intégré par le refresh local V2.18, SimuAI Tournament Engine V3, le scénario central V2.19 et son contrôle de cohérence sont régénérés.
