# Matchday Workspace Hygiene Audit V2.18

L’audit de workspace explique pourquoi Git peut rester sale après un refresh local. Il lit `git status --porcelain`, identifie les fichiers associés aux résultats, simulations, prédictions évaluées, standings, matrices, manifests et sources, puis les classe comme refresh local attendu. Les autres changements sont signalés comme itération ou hors scope.

Chaque fichier reçoit son statut Git, son état tracked/untracked, une classification et une recommandation. L’audit ne considère jamais un fichier sale comme automatiquement commitable et ne supprime aucun fichier. Son objectif est de faciliter une indexation ciblée et de protéger les prédictions actives, les secrets et les changements utilisateur.

Dans le workspace actuel, de nombreux artefacts Matchday préexistent à V2.18. Ils restent locaux et hors du commit orchestrateur. Une livraison Matchday séparée pourra les examiner et les publier.
