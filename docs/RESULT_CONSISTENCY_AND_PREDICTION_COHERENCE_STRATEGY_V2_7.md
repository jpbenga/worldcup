# Result Consistency and Prediction Coherence Strategy V2.7

Official scores must propagate to cards, modal context, live standings and
conditioned simulation because partial propagation makes correct data look
untrustworthy. V2.7 therefore creates one match-state view model for the
frontend and one standings artifact calculated exclusively from finished
official results.

Pre-match predictions remain frozen. The modal presents prediction, actual
result and evaluation as distinct layers, preserving the historical claim
while explaining what happened afterward.

Le score modal est une seule case de la matrice de scores. Le favori 1X2 est
la somme de toutes les cases correspondant à une victoire, un nul ou une
défaite. Il est donc possible qu’un score de nul comme 0-0 soit la case
individuelle la plus probable, tout en ayant une équipe favorite au 1X2
lorsque toutes ses victoires possibles sont additionnées.

When these signals diverge, the product shows the modal score, the 1X2 trend
and the most probable score compatible with that trend. It explains the
aggregation rather than describing a mathematically valid distribution as
contradictory.
