# Tournament Simulation Algorithm Audit V2.20

## Verdict exécutif

Les 50 000 tournois sont réellement générés. Chaque itération simule les matchs de groupes restants, recalcule les classements, choisit 32 qualifiés, construit un tableau et propage les vainqueurs jusqu'au champion. Le volume est statistiquement suffisant pour stabiliser les probabilités marginales conditionnelles : à 50 %, l'incertitude Monte Carlo maximale à 95 % est d'environ `±0,44 point`.

Le problème principal n'est donc pas le nombre de simulations. Le moteur répète 50 000 fois plusieurs hypothèses trop simplifiées ou incorrectes. Une simulation massive mesure précisément les conséquences du modèle; elle ne rend pas le modèle juste.

La priorité recommandée n'est pas un moteur V4 rempli de nouveaux signaux. Il faut construire un V3.5 correct sur les règles, réutilisant le meilleur modèle historiquement validé du projet, séparant réellement les processus knockout et prouvant ses probabilités au niveau tournoi.

## Fonctionnement actuel

### Matchs de groupes

V3 utilise un modèle Poisson indépendant. Chaque équipe reçoit une intensité de buts fondée sur un Elo externe courant, sa moyenne pondérée de buts marqués et la moyenne pondérée de buts encaissés par l'adversaire. La décroissance est exponentielle. Le score est tiré dans une matrice `0–0` à `7–7`, normalisée.

Les mêmes probabilités sont réutilisées dans les 50 000 tournois. Les résultats officiels terminés sont verrouillés. Les autres matchs sont tirés indépendamment, puis les points, différence de buts et buts marqués sont recalculés.

### Classements et meilleurs troisièmes

Le classement utilise points, différence de buts et buts marqués. Si l'égalité persiste, V3 utilise un tirage aléatoire. Il ne calcule pas les critères tête-à-tête. Dans les 100 parcours persistés, `45` groupes sur `1 200` présentent une égalité touchant la frontière entre qualification et élimination après les trois critères implémentés.

Les deux premiers passent. Les douze troisièmes sont triés par points, différence et buts marqués; les huit premiers passent. Les critères réglementaires restants ne sont pas implémentés.

### Matchs knockout

V3 ne tire pas de score knockout. Il tire directement un vainqueur selon :

```text
P(qualification A) = P(victoire A en 90 min) + P(nul en 90 min) × probabilité Elo de A
```

La prolongation n'est pas simulée. Les tirs au but ne sont pas simulés. Toute la masse du nul est allouée en une étape via Elo. L'IFAB prévoit pourtant une éventuelle prolongation de deux périodes pouvant aller jusqu'à 15 minutes, puis une séance de tirs au but.

### Bracket

Les 32 qualifiés sont triés par Elo, séparés en deux moitiés puis appariés haut contre bas, avec quelques échanges pour éviter un duel immédiat entre équipes du même groupe. Ce tableau est explicitement non officiel.

Cette limite est désormais prioritaire : le calendrier et les règles 2026 définissent des slots fixes et un mapping des huit meilleurs troisièmes. Continuer à semer selon Elo produit des adversaires, chemins et probabilités de titre structurellement incorrects.

### Scénario central

Les 50 000 parcours sont agrégés, mais seuls les 100 premiers sont persistés. V2.19 sélectionne un parcours complet cohérent parmi ces 100, en évaluant rangs de groupe, qualifications, résultats tête-à-tête et champion. La cohérence est correcte, mais la représentativité reste limitée par l'échantillon persistant : à 100 parcours, la marge d'échantillonnage maximale à 95 % approche `±9,8 points`.

## Ce qui est solide

- 50 000 tournois complets sont réellement générés.
- Les résultats réels terminés sont verrouillés.
- Les scores de groupe produisent réellement les points et qualifiés.
- Chaque vainqueur knockout rejoint correctement le tour suivant.
- La force tête-à-tête n'utilise plus la probabilité d'atteindre un tour.
- Le seed fixe rend l'exécution reproductible.
- Le backtest V3 est chronologique et meilleur que sa baseline Elo simple.

## Faiblesses mesurées

### 1. Le meilleur modèle du projet n'alimente pas le tournoi

V3 obtient sur son test une log loss de `1,020` et un Brier de `0,613`. Le moteur actif `quant_hybrid_v2.2` obtient `0,881` et `0,516`. Les jeux de test ne sont pas strictement identiques, donc ce n'est pas un duel expérimental parfait, mais l'écart est suffisamment important pour imposer une comparaison unifiée avant toute nouvelle sophistication.

`quant_hybrid_v2.2` possède 24 features chronologiques, un rating interne sans fuite temporelle, une composante XGBoost régularisée et une distribution de scores. Son obstacle actuel est d'ingénierie : le bundle modèle + état nécessaire à l'inférence de confrontations arbitraires n'est pas persisté comme contrat réutilisable par le tournoi.

### 2. Les règles de compétition sont incomplètes

V3 saute les critères tête-à-tête et utilise de l'aléatoire après points, différence et buts marqués. Les meilleurs troisièmes ont le même problème. Le bracket est inventé par seeding Elo alors que le format officiel utilise des slots prédéfinis et un mapping dépendant des groupes des meilleurs troisièmes.

Une bonne probabilité de match ne peut pas compenser une mauvaise règle de tournoi.

### 3. Le knockout est trop simplifié

Le modèle ne distingue pas :

- score après 90 minutes;
- score après prolongation;
- qualification aux tirs au but.

Les `25` matchs historiques marqués AET et les `67` marqués PEN ne possèdent pas encore une sémantique nettoyée garantissant le score à 90 minutes. Ils ne doivent pas être utilisés naïvement. Avec ce petit volume, le meilleur modèle réaliste est un modèle de prolongation fortement régularisé et une baseline de tirs au but proche de `50/50`, tant qu'une amélioration robuste n'est pas prouvée.

### 4. Le corpus historique reste moyen

Le corpus V3 contient `1 311` matchs, six compétitions et `168` équipes. La médiane est de `13` matchs par équipe; `59` équipes ont moins de dix matchs. Une équipe du tournoi n'a aucun profil V3 et six n'ont pas d'Elo externe correspondant. Ces équipes retombent vers des valeurs par défaut.

Le corpus mélange aussi compétitions, qualifications et phases finales. Les styles, niveaux et mécanismes de sélection diffèrent. Les matchs AET/PEN et le contexte terrain neutre restent imparfaitement définis.

### 5. L'incertitude du modèle est absente

Chaque tournoi utilise les mêmes paramètres et suppose les matchs indépendants conditionnellement aux forces fixes. Les 50 000 tirages capturent l'aléa des scores, mais pas :

- l'incertitude sur les paramètres;
- la possibilité qu'une équipe soit durablement meilleure ou moins bonne pendant le tournoi;
- la fatigue, les suspensions ou changements de composition;
- les corrélations entre performances successives.

Le résultat peut donc paraître plus précis qu'il ne l'est réellement.

## Comparaison aux méthodes sérieuses

### Elo + Poisson + Monte Carlo

C'est une famille sérieuse, explicable et adaptée aux données disponibles. Des travaux de simulation de Coupe du Monde utilisent une régression Poisson intégrant Elo, puis Monte Carlo pour les probabilités de tours. V3 appartient à cette famille, mais ses coefficients sont heuristiques, son Elo est statique et son tournoi n'applique pas toutes les règles.

### Poisson hiérarchique avec shrinkage

Une hiérarchie attaque/défense permet de partager l'information entre équipes et de régulariser les faibles échantillons. Elle est très pertinente ici, puisque 59 équipes ont moins de dix matchs. Elle doit intégrer rating interne chronologique, compétition, neutralité et décroissance temporelle.

### Dixon-Coles, Poisson bivarié et distributions alternatives

Ces méthodes corrigent la dépendance entre scores et certaines fréquences faibles, notamment `0-0`, `1-0`, `0-1`, `1-1`. Elles sont applicables, mais pas automatiquement meilleures. Les essais Dixon-Coles précédents du projet n'ont pas passé les garde-fous hors échantillon. Elles doivent rester des challengers, jamais être promues pour leur réputation seule.

### Modèles ML et ensembles calibrés

Le projet dispose déjà de `quant_hybrid_v2.2`, qui combine rating interne, historique pré-match, intensités de buts et XGBoost régularisé. C'est aujourd'hui la meilleure piste applicable. Un ensemble n'est utile que si ses probabilités sont calibrées et si sa matrice de scores reste cohérente avec le 1X2.

### Modèles dynamiques événementiels

Les processus de Cox et modèles in-play peuvent modéliser score courant, cartons et temps additionnel. Ils sont sérieux, mais non applicables au pré-tournoi avec les données actuelles : événements, cartons, lineups et statistiques avancées n'ont pas une couverture fiable.

## Architecture cible réaliste

### Couche 1 — Contrat de données

Normaliser explicitement score à 90 minutes, prolongation, tirs au but, terrain neutre, stade de compétition, identité équipe et règles officielles. Rejeter ou isoler toute ligne ambiguë.

### Couche 2 — Bundle d'inférence pré-match

Persister un bundle réutilisable de `quant_hybrid_v2.2` : modèle XGBoost, paramètres, rating interne à date, historique équipe et générateur de matrice. Il doit pouvoir prédire n'importe quelle confrontation future sans réentraîner pendant la simulation.

La matrice de scores doit être réconciliée avec les probabilités 1X2 hybrides, par calibration contrainte ou reconstruction maximum-entropie. Le tournoi ne doit pas choisir entre « bonnes probabilités » et « scores cohérents ».

### Couche 3 — Processus knockout explicite

1. Tirer le score après 90 minutes.
2. En cas de nul, tirer la prolongation avec une intensité spécifique et fortement régularisée.
3. En cas de nouveau nul, tirer les tirs au but selon une baseline conservatrice, proche de 50/50 tant qu'un avantage prédictif n'est pas validé.

### Couche 4 — Moteur de règles exact

Implémenter l'ordre réglementaire complet des départages, le classement des meilleurs troisièmes et le mapping officiel du round of 32. Chaque décision de départage doit être auditée dans le parcours.

### Couche 5 — Monte Carlo avec incertitude

Conserver 50 000 comme minimum, mais ajouter :

- diagnostic de convergence multi-seed;
- intervalles Monte Carlo;
- bootstrap ou ensemble de paramètres;
- choc latent de forme par équipe et tournoi, uniquement s'il améliore le replay historique;
- agrégation streaming et reservoir représentatif bien plus large que 100 parcours.

### Couche 6 — Validation au niveau tournoi

Rejouer chronologiquement des tournois historiques complets. Mesurer :

- calibration des rangs et qualifications;
- Brier/RPS des probabilités d'atteindre chaque tour;
- calibration champion/finaliste;
- exactitude du moteur de règles;
- stabilité multi-seed;
- qualité du scénario représentatif.

Un bon backtest de match est nécessaire mais insuffisant.

## Plan concret

### P0 — Corriger avant d'optimiser

1. Encoder le bracket officiel et les règles exactes.
2. Nettoyer les sémantiques 90 min/AET/PEN.
3. Ajouter des tests déterministes de groupes, meilleurs troisièmes et bracket.

### P1 — Unifier le modèle de match

1. Rendre `quant_hybrid_v2.2` inférable pour toute confrontation.
2. Comparer V3, Elo, Poisson hiérarchique et quant hybrid sur le même replay.
3. Réconcilier score matrix et 1X2.
4. Calibrer séparément groupes et knockout.

### P2 — Modéliser le knockout et l'incertitude

1. Séparer 90 minutes, prolongation et tirs au but.
2. Ajouter multi-seed, convergence et intervalles.
3. Tester bootstrap et forme latente; rejeter ce qui n'améliore pas le replay.

### P3 — Prouver le moteur complet

1. Rejouer des tournois historiques de bout en bout.
2. Publier métriques et courbes de calibration.
3. Promouvoir seulement si les gains sont robustes sur matchs, groupes et tournoi.

## Méthodes non applicables aujourd'hui

Les blessures, lineups futures, valeurs d'effectif, odds et xG large couverture ne doivent pas entrer dans le moteur tant que leur couverture pré-match n'est pas fiable. Leur absence doit augmenter l'incertitude affichée, pas être remplacée par une intuition.

## Références

- Simulation de Coupe du Monde Elo-Poisson et Monte Carlo : https://arxiv.org/abs/1806.01930
- Extensions Dixon-Coles et modèles de scores dépendants : https://arxiv.org/abs/2307.02139
- Comparaison et calibration de modèles probabilistes football : https://arxiv.org/abs/1705.04356
- Modélisation dynamique d'événements football : https://arxiv.org/abs/2312.04338
- Règles IFAB sur prolongation et tirs au but : https://www.theifab.com/laws/latest/determining-the-outcome-of-a-match/

## Décision recommandée

Ne pas ajouter de patch par équipe et ne pas augmenter simplement le nombre de simulations. Construire un V3.5 correct sur les règles autour d'un bundle d'inférence `quant_hybrid_v2.2`, d'un knockout explicite et d'une validation tournoi complète. Cette trajectoire est la meilleure combinaison actuelle de performance, réalisme, auditabilité et faisabilité avec les données exploitables du projet.
