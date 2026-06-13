# Road to the Trophy

Road to the Trophy est l’expérience centrale de simulation et d’exploration du tournoi. L’utilisateur peut zoomer, se déplacer, inspecter un groupe, suivre une équipe et comprendre chaque rencontre du chemin projeté.

SimuAI Tournament Engine V3 est l’unique moteur public de cette fonctionnalité. Il génère 50 000 tournois complets, verrouille les résultats réels déjà joués, simule les matchs de groupes restants, recalcule les classements, varie les qualifiés et décide chaque match éliminatoire avec un modèle de confrontation tête-à-tête.

Le scénario affiché est un parcours complet cohérent choisi parmi les simulations. Il contient un vainqueur projeté, une finale projetée, les résultats de groupe, le tableau, les parcours d’équipe et les explications contextuelles des matchs. Les explications utilisent les facteurs mesurables disponibles et indiquent les données manquantes.

Limites connues : le mapping officiel du tableau 2026 n’est pas encore disponible; seules cent trajectoires complètes sont persistées pour l’exploration, même si les 50 000 ont été générées et agrégées; les blessures, compositions futures et valeurs d’effectif ne sont pas utilisées faute de données fiables.

Lorsqu’un nouveau résultat officiel est intégré par le refresh local V2.18, SimuAI Tournament Engine V3 et le scénario Road to the Trophy sont régénérés afin que le parcours public ne reste jamais basé sur un état plus ancien.
