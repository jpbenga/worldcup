# Road to the Trophy SVG & Odds UX Clarification V2.23.1

## Problème utilisateur

V2.23 ajoutait des flèches, des accents dorés et un signal de cote trop filtré. Ces choix rendaient la lecture décorative plutôt qu'interactive : les couleurs n'étaient pas évidentes, les courbes ne permettaient pas de suivre une équipe et les cotes ordinaires restaient invisibles.

## Ce qui a été supprimé

- tous les markers et flèches SVG ;
- les gradients mélangés cyan/violet et ambre/rose ;
- les contours dorés appliqués aux groupes, matchs changés et trophée ;
- l'affichage limité aux seules « cotes intéressantes ».

## Sémantique couleur retenue

- neutre ardoise : connexion non sélectionnée ;
- cyan : parcours d'équipe sélectionné ou survolé ;
- violet : élément modifié, uniquement pendant une comparaison avant/après ;
- gris pointillé : ancien parcours en ghost path ;
- vert : résultat réel verrouillé.

Une légende compacte explique cette sémantique dans l'Atlas.

## Interaction courbe vers parcours équipe

Chaque parcours projeté possède une couche SVG cliquable et accessible au clavier. Le survol révèle le parcours ; le clic sélectionne l'équipe, met en évidence son chemin complet et renseigne l'inspecteur existant avec son groupe, ses matchs et ses adversaires projetés. Reset désélectionne le parcours. Zoom et pan D3 sont conservés.

## Bookmaker de référence et affichage des cotes

Le bookmaker est choisi de façon déterministe selon la couverture de matchs, puis la couverture des marchés utiles, la disponibilité d'un timestamp et enfin le nom stable API-Football. Le bookmaker retenu est **10Bet**.

La modal affiche ses cotes pour 1X2, double chance, draw no bet, over/under 2,5 et both teams to score lorsque disponibles. Toutes les cotes utiles restent visibles. Une issue franchissant les seuils responsables reçoit simplement le badge « Cote intéressante » avec SimuAI, marché, edge et EV.

## Validation

Le moteur tournoi V4, `quant_hybrid_v2.2`, les prédictions actives et Optuna restent inchangés. La validation V2.23.1 contrôle l'absence de flèches et de doré inexpliqué, l'interactivité des parcours, le bookmaker unique, la visibilité des marchés et le langage responsable.
