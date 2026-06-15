# V2.27 — Exploration API-Football et catalogue de scénarios match

## Contexte utilisateur

Cette itération répond à deux questions : quelles statistiques API-Football peuvent réellement enrichir SimuMondial, et quels scénarios footballistiques la matrice pré-match savait déjà identifier pour Allemagne–Curaçao. L'objectif est d'explorer avant de modifier. Aucun moteur, pronostic actif ou composant frontend fonctionnel n'est changé.

## Résumé exécutif

API-Football expose bien davantage que le score final pour les trois matchs terminés vérifiés. Les endpoints `fixtures/statistics`, `fixtures/events`, `fixtures/lineups` et `fixtures/players` ont tous retourné des données pour Allemagne–Curaçao, Espagne–Cap-Vert et Suède–Tunisie. Les payloads contiennent notamment tirs, tirs cadrés, possession, corners, passes, arrêts, xG, événements, formations et statistiques joueurs.

Cette disponibilité change la lecture du précédent audit : les statistiques Espagne–Cap-Vert n'étaient pas présentes dans le pipeline local utilisé par Road to the Trophy, mais elles sont récupérables via API-Football. L'API mesure bien la domination espagnole : `27-6` aux tirs, `7-1` aux tirs cadrés, `74 %-26 %` de possession et `2,29-0,30` xG. Le moteur actuel ne collecte ni n'utilise ces données.

Pour Allemagne–Curaçao, la matrice savait identifier bien plus que le score recommandé `1-0`. Elle donnait `58,29 %` à une victoire allemande, `14,73 %` à une victoire par au moins trois buts, `9,65 %` à quatre buts allemands ou plus, et `25,64 %` à un match de quatre buts ou plus. Le produit masquait ces familles en résumant la distribution par quelques scores exacts.

## Exploration API-Football

### Méthode et quota

L'exploration a été effectuée en mode quota sûr, avec un maximum de quatorze appels. La clé était présente mais n'a jamais été écrite dans les artefacts. Les réponses brutes ont été mises en cache localement et restent hors commit. L'abonnement actif autorise `7 500` requêtes quotidiennes ; l'exploration a utilisé quatorze appels live, puis zéro lors des exécutions suivantes grâce au cache.

Les endpoints vérifiés sont :

- `fixtures/statistics`
- `fixtures/events`
- `fixtures/lineups`
- `fixtures/players`
- `predictions`
- `odds`

Les détails de fixtures et résultats étaient déjà présents dans le cache World Cup du projet. L'endpoint agrégé `teams/statistics` n'a pas été interrogé : il décrit une équipe dans une ligue et une saison, pas une performance post-match précise.

### Données disponibles

Sur les trois fixtures testées, la couverture observée est `3/3` pour statistiques match, événements, compositions, statistiques joueurs et xG. Les champs de statistiques détectés comprennent :

- tirs cadrés, non cadrés, bloqués, dans et hors surface ;
- tirs totaux ;
- possession ;
- corners, fautes, hors-jeu ;
- cartons jaunes et rouges ;
- arrêts gardien et `goals_prevented` ;
- passes totales, réussies et pourcentage ;
- `expected_goals`.

Les événements contiennent le type, le détail, le temps, l'équipe, le joueur et l'assistant. Les cas observés incluent buts, penalty, cartons et remplacements. Aucun incident VAR n'est observé sur ces trois matchs ; cela ne prouve pas que le champ ou l'événement est indisponible ailleurs. Les payloads testés ne contiennent ni `attacks` ni `dangerous attacks`.

Les compositions fournissent entraîneur, formation, onze de départ et remplaçants. Les statistiques joueurs fournissent minutes, note, tirs, buts, passes, tacles, duels, dribbles, fautes, cartes et penalties, avec des valeurs parfois nulles.

### Trois familles de données

**A. Pré-match**

Les équipes, le calendrier, les cotes et éventuellement les compositions publiées avant le coup d'envoi peuvent être utilisées avant match. Une donnée de composition doit être horodatée et réellement disponible avant le match pour éviter toute fuite.

**B. Live**

Le score, les événements, cartons, remplacements et snapshots statistiques peuvent alimenter plus tard un moteur live séparé. Ils ne doivent pas réécrire la prédiction pré-match gelée.

**C. Post-match**

Tirs, possession, xG, corners, passes, événements et statistiques joueurs peuvent expliquer le résultat et alimenter des variables retardées pour les matchs futurs. Ils ne doivent jamais être utilisés rétroactivement comme s'ils étaient connus avant le match évalué.

### Qualité, fraîcheur et limites

La couverture `3/3` est un signal favorable, pas une preuve de couverture historique. Avant d'utiliser ces champs dans un modèle, il faut mesurer leur disponibilité par compétition, saison, équipe et date, vérifier les valeurs nulles et effectuer un backtest chronologique. Les xG et notes joueurs proviennent de l'API et doivent également être audités pour stabilité méthodologique.

## Cas Espagne–Cap-Vert

API-Football retourne pour l'Espagne :

- `27` tirs, dont `7` cadrés ;
- `74 %` de possession ;
- `11` corners ;
- `801` passes, dont `734` réussies ;
- `2,29` xG.

Le Cap-Vert obtient `6` tirs, `1` cadré, `26 %` de possession et `0,30` xG. Le nul officiel verrouille correctement le scénario tournoi, mais la performance indique une domination espagnole nette. Une future couche post-match pourrait expliquer : « résultat décevant, performance sous-jacente dominante ». Cette information ne doit pas annuler le nul ni être injectée dans la prédiction pré-match.

## Cas Allemagne–Curaçao

API-Football retourne pour l'Allemagne `27` tirs, `12` cadrés, `65 %` de possession et `3,91` xG, contre `8` tirs, `2` cadrés et `0,40` xG pour Curaçao. Les événements incluent huit buts, dont un penalty, et les remplacements. Les données post-match confirment une forte domination, avec une réalisation supérieure aux xG.

## Catalogue des scénarios Allemagne–Curaçao

La matrice active est une distribution normalisée de `0-0` à `7-7`. Chaque famille ci-dessous est calculée en additionnant les cellules qui respectent une définition footballistique explicite.

### Résultat et scores

- Allemagne gagne : `58,29 %`
- Nul : `23,61 %`
- Curaçao gagne : `18,10 %`
- Score recommandé `1-0` : `13,25 %`
- Score réel `7-1` : `0,058 %`

Le score exact réel était très improbable individuellement. Cela ne signifie pas que la famille « victoire large » était négligeable.

### Marges, buts et rythme

- Victoire courte Allemagne, marge d'un but : `25,50 %`
- Victoire contrôlée Allemagne, marge de deux buts : `18,06 %`
- Victoire large Allemagne, marge de trois buts ou plus : `14,73 %`
- Allemagne gagne par quatre buts ou plus : `5,40 %`
- Carton Allemagne, marge de cinq buts ou plus : `1,65 %`
- Allemagne marque quatre buts ou plus : `9,65 %`
- Allemagne marque cinq buts ou plus : `3,08 %`
- Plus de 2,5 buts : `47,29 %`
- Plus de 3,5 buts : `25,64 %`
- Match fermé, au plus deux buts : `52,71 %`
- Match ouvert, au moins quatre buts : `25,64 %`

### BTTS et clean sheet

- Les deux équipes marquent : `46,77 %`
- Au moins une équipe ne marque pas : `53,23 %`
- Allemagne gagne sans encaisser : `35,40 %`
- Allemagne gagne en encaissant : `22,89 %`

## Diagnostic produit

Une liste de top scores répond seulement à la question « quelles cellules exactes sont les plus probables ? ». Elle ne répond pas à « quelles histoires de match sont plausibles ? ». Plusieurs scores lourds individuellement modestes deviennent une famille importante une fois agrégés.

Une future section **Scénarios SimuAI** devrait présenter :

- résultat probable ;
- score recommandé et top scores ;
- victoire courte, contrôlée, large et carton ;
- buts équipe et total de buts ;
- over/under ;
- BTTS et clean sheet ;
- cotes intéressantes ;
- après match, lecture de la performance réelle si les statistiques sont disponibles.

Pour Allemagne–Curaçao, l'interface aurait dû afficher simultanément : score recommandé `1-0`, victoire allemande par 3+ buts `14,73 %`, Allemagne à 4+ buts `9,65 %` et Over 3,5 `25,64 %`.

## Recommandations d'intégration

1. Ajouter d'abord une couche d'explication post-match, séparée des prédictions pré-match.
2. Construire un audit historique de couverture pour statistiques match, événements, xG, compositions et joueurs.
3. Créer seulement ensuite des features retardées, avec coupure chronologique stricte.
4. Préparer un moteur live séparé si les snapshots pendant match sont suffisamment fiables.
5. Afficher les familles de scénarios calculées depuis la distribution existante sans modifier le moteur.

## Plan V2.28 éventuel

**V2.28 — Unified Match Outcome Distribution & Scenario Families** doit créer un contrat unique alimentant 1N2, scores exacts, scénarios agrégés, over/under, BTTS, victoire large, cotes intéressantes et Road to the Trophy. Les statistiques API-Football doivent être intégrées en deux temps : d'abord comme couche explicative post-match, puis comme features futures uniquement après audit de couverture et backtest chronologique.

## Limites restantes

- Trois matchs ne suffisent pas à établir la couverture historique.
- Les valeurs nulles existent dans les statistiques équipe et joueur.
- Aucun événement VAR n'a été observé dans l'échantillon.
- Attacks et dangerous attacks ne sont pas présents dans les payloads testés.
- La matrice active reste tronquée à sept buts par équipe.
- Aucun moteur ou composant UI n'est modifié dans V2.27.
