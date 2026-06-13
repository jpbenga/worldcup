# Living World Cup Scenario V2.13

V2.13 transforme les sorties de simulation existantes en un tableau vivant du
tournoi. Le scénario conserve les `72` matchs de groupes connus et ajoute `32`
slots projetés à élimination directe, petite finale comprise, pour documenter
la cible complète de `104` matchs.

Le bracket officiel n'est pas disponible dans les données actuelles. Le
scénario porte donc explicitement le type
`simulation_derived_bracket_projection`. Les 32 qualifiés projetés sont tirés
des probabilités de rang et de qualification produites par les 50 000
simulations conditionnées. Un tableau dérivé est ensuite simulé 50 000 fois
avec une graine reproductible afin d'estimer le champion le plus fréquent, la
finale dominante et les présences dans chaque tour.

Le vainqueur projeté actuel est **Spain**. La finale représentative est
**Spain vs Switzerland**. Ces éléments répondent à la question produit
"quel est le chemin le plus probable ?" sans être présentés comme un bracket
FIFA officiel.

Après chaque rafraîchissement, les résultats terminés restent verrouillés dans
la simulation de groupes. Les qualifiés probables, le bracket dérivé, le
vainqueur projeté et les variations de qualification peuvent ainsi évoluer
sans réécrire les Pronos IA d'avant-match.

Limite principale : le scénario à élimination directe utilise un tableau
projeté fixe construit à partir des qualifiés les plus probables. Il décrit un
scénario dominant et non la totalité des combinaisons possibles du futur
bracket officiel.
