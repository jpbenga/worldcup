# Road to the Trophy SVG Atlas & Odds Value Experience V2.23

## Contexte utilisateur

V2.23 enrichit l'Atlas existant sans refaire le moteur tournoi ni transformer SimuMondial en interface de bookmaker. Le besoin est double : rendre les chemins du tournoi plus intuitifs et intégrer les cotes comme donnée d'analyse responsable.

## Audit de l'Atlas SVG existant

L'Atlas utilisait déjà un SVG inline, des courbes de Bézier calculées dans Angular, D3 Selection/Zoom/Transition, Angular Signals, un zoom/pan fluide et la timeline V2.22. Il ne possédait pas de `defs`, markers, gradients, couches sémantiques, ghost paths ni support reduced motion.

## Possibilités SVG custom étudiées

| Piste | Intérêt UX | Complexité / risque | Faisabilité | Décision |
| --- | --- | --- | --- | --- |
| Connexions groupe vers bracket | Forte | Faible | Immédiate, sans dépendance | Conservée et identifiée |
| Chemin sélectionné | Forte | Faible | Immédiate | Gradient cyan/violet |
| Ancien chemin ghost | Forte | Moyenne | Immédiate avec timeline | Ajouté en comparaison |
| Nouveau chemin accentué | Forte | Faible | Immédiate | Accent ambre/rose |
| Markers et gradients | Moyenne | Faible | Immédiate | Ajoutés dans `defs` |
| Badges SVG | Moyenne | Moyenne | Possible | Différé pour éviter la surcharge |
| Animation avant/après | Forte | Moyenne | CSS existant | Transition légère uniquement |
| Reduced motion | Forte | Faible | Immédiate | Ajouté |
| Responsive viewBox / export image | Moyenne | Moyenne | ViewBox prêt, export à étudier | Préparé |

Aucune dépendance n'a été ajoutée. Angular, CSS, SVG custom et D3 déjà présents couvrent le besoin.

## Stratégie UX Atlas

Le SVG est organisé en couches : ghost, connexions groupes, connexions bracket, chemins sélectionnés et chemins changés. Les identifiants sont stables (`group-A-to-*`, `match-*-connection`). Le chemin sélectionné utilise un gradient lumineux ; un changement avant/après affiche l'ancien chemin en pointillés et le nouveau en accent. Le SVG reste derrière les cartes et le zoom/pan D3 est conservé.

## Stratégie cotes API-Football

Le fetch est explicitement opt-in via `--fetch-odds`, limité à un appel paginé et utilise le client backend existant. La clé reste uniquement dans l'environnement backend. Sans endpoint, abonnement ou cache disponible, un snapshot `available: false` est publié sans bloquer l'application.

## Définition de « Cote intéressante »

Une cote intéressante est un écart robuste entre une probabilité déjà produite par `quant_hybrid_v2.2` et la probabilité implicite normalisée du marché. V2.23 ne crée aucune probabilité modèle.

Pour chaque bookmaker et marché complet, l'overround est retiré :

`market_probability = (1 / decimal_odds) / sum(1 / odds_i)`

Les probabilités de marché et les cotes sont ensuite agrégées par médiane sur au moins trois bookmakers. Le signal exige :

- expected value >= 5 % ;
- edge >= 4 points ;
- confiance modèle différente de `low` ;
- cote fraîche, moins de 48 heures ;
- marché complet et au moins trois bookmakers ;
- match non commencé.

Marchés comparables : 1X2, double chance, draw no bet, over/under 2,5 et BTTS, uniquement lorsque le libellé API correspond exactement et que SimuAI produit la probabilité.

## Garde-fous responsables

L'UI utilise « Cote intéressante », « écart modèle / marché » et « signal statistique ». Elle n'utilise aucun langage de garantie ou d'incitation. La micro-copy obligatoire est : « Signal statistique, sans garantie de résultat. »

## Fichiers et validation

Les scripts V2.23 produisent un audit SVG, un view-model géométrique, un snapshot de cotes, des signaux de valeur et une validation consolidée. Le moteur tournoi V4, les prédictions actives et Optuna ne sont pas modifiés.
