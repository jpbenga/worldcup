# Simulation Coherence Repair V2.19

## Contexte utilisateur

Le scénario Road to the Trophy affichait la Belgique avec environ 89 % de chances de qualification, mais seulement 2 points dans le parcours représentatif. Un tel résultat reste possible, mais il est trop marginal pour être présenté sans explication comme scénario central. L’objectif V2.19 est de rendre le scénario affiché crédible et cohérent de bout en bout, sans choisir manuellement les équipes attendues.

## Diagnostic et audit du scénario actuel

Le scénario V2.14 précédent provenait bien d’une simulation complète : ses scores produisaient ses points, son classement produisait ses qualifiés et son tableau suivait le même parcours. Le problème venait de la méthode de sélection. Elle imposait d’abord le champion le plus fréquent, puis évaluait surtout la proximité des vainqueurs du tableau avec les probabilités marginales. La représentativité des douze groupes n’entrait pas réellement dans le score.

L’audit a identifié trois contradictions fortes dans l’ancien affichage : Netherlands avec 1 point malgré 87,9 % de qualification, Belgium avec 2 points malgré 88,8 %, et Norway avec 2 points malgré 76,8 %. Ces scénarios sont possibles, mais trop surprenants pour servir ensemble de centre du produit.

## Cas Belgique

La Belgique possède `88,774 %` de chances marginales d’atteindre les seizièmes. Dans l’ancien scénario, elle terminait troisième avec 2 points. Parmi les 100 parcours complets persistés, elle finit à 2 points ou moins dans seulement `8 %` des cas. Ce résultat était donc cohérent comme surprise, mais non représentatif comme scénario central.

La nouvelle sélection choisit la simulation complète `#12`. La Belgique y termine deuxième avec 6 points. Aucune règle ne mentionne ni ne favorise la Belgique : le changement découle du score global de représentativité appliqué à toutes les équipes.

## Cas Suisse et résultats à élimination directe

L'audit utilisateur a révélé que la sélection centrale précédente faisait battre successivement le Mexique et l'Uruguay par la Suisse alors que ses probabilités tête-à-tête étaient respectivement `47,6 %` et `46,3 %`. Ces deux résultats étaient possibles et provenaient réellement d'un tournoi simulé; leur probabilité conjointe était d'environ `22,1 %`. La Suisse n'était donc pas forcée. Toutefois, le score central évaluait surtout la fréquence d'atteindre les tours, pas la vraisemblance de chaque victoire réellement tirée, ce qui rendait cet enchaînement insuffisamment pénalisé.

La correction évalue désormais chaque résultat éliminatoire avec sa probabilité tête-à-tête. Elle sélectionne la simulation complète `#12`. Dans ce scénario, la Suisse est favorite à `56,5 %` face à l'Autriche mais perd lors d'une surprise à `43,5 %`. L'interface marque explicitement le qualifié et explique cette surprise. La règle est identique pour toutes les équipes et ne force pas systématiquement le favori.

## Méthode de sélection du scénario central

V2.19 exploite les 100 parcours complets persistés par SimuAI Tournament Engine V3. Chaque parcours reçoit un score fondé sur la surprise marginale de chaque rang de groupe, de chaque qualification ou élimination, de chaque résultat tête-à-tête réellement tiré et du champion. Le parcours avec le meilleur score global devient le scénario central. Cette correction évite de récompenser indirectement une succession de victoires d'outsider uniquement parce que l'équipe atteint souvent les tours avancés.

La méthode n’impose ni champion, ni favori, ni équipe particulière. Elle ne reconstruit pas des morceaux indépendants et ne fabrique aucun score. Le scénario sélectionné est un tournoi réellement généré lors des 50 000 simulations; son score de représentativité est `0,6162`.

## Correction appliquée

Le script `repair_road_to_the_trophy_scenario_coherence_v2_19.py` audite l’ancien scénario, calcule les distributions observables dans l’échantillon de parcours complets, sélectionne un parcours central et publie un scénario, un rapport et un view model cohérents. Le view model sépare explicitement le classement du scénario central des probabilités marginales calculées sur 50 000 tournois.

L’interface affiche désormais, pour chaque groupe, une zone « Classement du scénario central » et une zone « Chances sur 50 000 simulations ». Les lignes sont triées du premier au quatrième selon les points et critères de départage calculés. Le classement principal ne mélange plus rang simulé et probabilité marginale. Dans le tableau éliminatoire, le qualifié retenu est marqué explicitement et chaque surprise possède une explication indiquant qu'elle a été tirée malgré une probabilité inférieure à 50 %.

## Garde-fous de cohérence

- les six scores de chaque groupe doivent produire exactement les points affichés;
- les points, différence de buts et buts marqués doivent produire le classement;
- le classement et les meilleurs troisièmes doivent produire les 32 qualifiés;
- les 32 qualifiés doivent être les entrants du premier tour;
- chaque vainqueur doit rejoindre exactement le tour suivant;
- le scénario central doit provenir d’un parcours complet;
- aucune correction ou préférence par équipe n’est autorisée;
- les probabilités marginales restent séparées du scénario affiché.

## Validation

La validation V2.19 passe les douze groupes, les 72 matchs de groupe, le tableau et les parcours. Le cas Belgique passe. Les prédictions actives, `quant_hybrid_v2.2` et le résumé Optuna restent inchangés. SimuAI Tournament Engine V3 reste le moteur officiel; V2.19 corrige uniquement la sélection et la présentation du scénario central.

## Limites restantes

Seuls 100 parcours complets sont persistés pour sélectionner le scénario central, même si les 50 000 tournois sont réellement générés et agrégés. Les probabilités de rang détaillées sont donc estimées sur cet échantillon persistant, tandis que les probabilités de qualification et de tours proviennent des 50 000 simulations. Le mapping officiel du tableau 2026 reste indisponible et le seeding projeté demeure explicitement non officiel.
