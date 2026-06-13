# Prediction Evaluation Color System V2.13.1A

Le composant `PredictionOutcomeBadge` définit six états lisibles. `success`
utilise le vert et le symbole `✓`. `partial` utilise le cyan et `≈`. `fail`
utilise le rouge et `×`. `push` utilise l'ambre et `↔`. `pending` utilise le
gris et `…`. `neutral` utilise un point et une surface sombre.

La couleur n'est jamais le seul signal. Chaque badge affiche un titre et un
détail comme Trouvé, Non trouvé, Réussi, Raté, Présent, Absent ou Remboursé.
Les fonds restent sombres, les bordures renforcent la distinction et les
teintes de texte gardent un contraste élevé.

Score exact, Top 3, résultat du match et marchés réussis utilisent success.
Un Top 5 réussi est partial car il indique une couverture utile sans précision
forte. Les échecs sont fail, Draw No Bet remboursé est push et les matchs non
joués restent pending.

Ce système rend le bilan immédiatement compréhensible et évite une liste de
valeurs oui/non sans hiérarchie.
