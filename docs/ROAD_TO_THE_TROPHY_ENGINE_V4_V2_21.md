# Road to the Trophy Engine V4 V2.21

## Décision

V2.21 remplace le moteur de simulation public par une architecture plus rigoureuse avec les données réellement exploitables dans le projet. Il rejoue 50 000 tournois complets en verrouillant les résultats officiels connus et 50 000 tournois contrefactuels avec des flux aléatoires communs par tournoi, sans verrouiller ces résultats. Cette comparaison isole leur impact sur les probabilités et sur le scénario central.

Le moteur reste honnête sur deux limites bloquantes : le dépôt ne contient pas encore le mapping officiel des slots knockout 2026, et le bundle d'inférence `quant_hybrid_v2.2` n'est pas persisté pour produire une matrice de score sur une confrontation future arbitraire.

## Matchs de groupe

Chaque rencontre non jouée utilise une matrice de scores Poisson indépendante construite à partir de l'Elo courant et des profils offensifs et défensifs pondérés dans le temps. Les résultats terminés sont verrouillés avant toute simulation.

Le classement applique successivement :

1. points ;
2. différence de buts ;
3. buts marqués ;
4. mini-classement tête-à-tête entre équipes encore à égalité ;
5. Elo comme proxy déterministe final uniquement lorsque les données de fair-play et de tirage au sort sont absentes.

Le proxy final est une limitation explicite, pas un signal caché de force ajouté au classement.

## Knockout

V4 ne tire plus directement un qualifié depuis une probabilité agrégée. Chaque match suit trois processus :

1. score à 90 minutes depuis la matrice de score ;
2. si nul, score de prolongation avec des intensités ramenées à 30 minutes ;
3. si toujours nul, tirs au but proches de 50/50 avec un signal Elo fortement réduit.

Sur les 50 000 tournois actuels, les 1 550 000 matchs knockout ont tous une résolution traçable : temps réglementaire, prolongations ou tirs au but.

## Scénario central

Le moteur précédent choisissait parmi les 100 premiers parcours sauvegardés. V4 applique un réservoir uniforme de 2 000 parcours distribué sur l'ensemble des 50 000 simulations.

Chaque parcours candidat reçoit un score de surprise globale calculé sur :

- les rangs finaux dans les douze groupes ;
- chaque résultat tête-à-tête du tableau ;
- la probabilité finale du champion.

Le meilleur score brut minimise la surprise moyenne. Pour une mise à jour vivante, tous les parcours situés à moins de 5 % de ce minimum sont considérés statistiquement proches. Parmi eux, le moteur choisit celui qui reste le plus proche du scénario précédent. Cette continuité ne peut donc pas sauver un ancien scénario devenu peu représentatif ; elle sert uniquement à départager des candidats encore centraux.

Le champion le plus probable n'est jamais imposé comme condition préalable. Un scénario peut donc contenir une surprise plausible, mais un enchaînement improbable de surprises est pénalisé.

Dans cette exécution, la méthode choisit l'Espagne, également champion marginal le plus probable à 18,272 %. Cette convergence est observée, pas forcée. Le rapport publie aussi le meilleur candidat obtenu avec une règle champion-first afin de permettre l'audit comparatif.

## Impact des résultats réels

Les cinq résultats officiels connus changent le scénario central. Dans l'exécution contrôlée par nombres aléatoires communs, l'Espagne reste championne avant et après, mais les classements de groupes, les affiches et le chemin retenu évoluent. Le maintien du champion n'est pas interprété comme une absence d'impact.

Les deux univers utilisent le même moteur, le même nombre de simulations et un flux aléatoire commun pour chaque tournoi apparié. Même lorsqu'un score réel est verrouillé, le tirage contrefactuel correspondant est consommé pour ne pas décaler les tirages suivants. La différence est ainsi attribuable aux résultats verrouillés et à leurs conséquences sur les groupes et le tableau projeté, avec une variance comparative fortement réduite.

L'interface Road to the Trophy conserve l'Atlas existant et ajoute un panneau « impact des résultats réels ». Il montre :

- le champion du scénario avant et après ;
- les résultats nouvellement intégrés ;
- les équipes dont les chances de qualification et de titre ont le plus évolué.

Le workflow local `start_local_app_v2_18.py --auto-refresh` détecte désormais un écart entre les résultats terminés et ceux verrouillés dans V4. Lorsqu'un nouvel écart apparaît, il rejoue V4, publie le nouveau scénario vivant puis exécute sa validation avant de lancer l'application.

## Ce qui reste à faire

Les recommandations applicables immédiatement sont implémentées. Deux améliorations importantes nécessitent d'abord de nouvelles données ou un nouveau contrat :

- importer et tester le mapping officiel complet des slots knockout 2026 ;
- persister un bundle d'inférence calibré `quant_hybrid_v2.2` capable de générer des probabilités et une matrice de score pour toute confrontation future.

Ces limites sont affichées dans les artefacts et dans le moteur public. Elles ne sont pas masquées par des règles spécifiques à une équipe.
