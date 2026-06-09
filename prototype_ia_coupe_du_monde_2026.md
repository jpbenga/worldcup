# Prototype personnel — IA de simulation et de pronostics Coupe du Monde 2026

## 1. Résumé du projet

L’objectif est de créer un **prototype personnel**, partageable avec des amis, autour de la Coupe du Monde 2026.

L’application permettrait de :

- consulter les matchs de la Coupe du Monde ;
- afficher des informations live ou post-match ;
- générer une matrice de scores probables pour chaque rencontre ;
- déduire automatiquement des marchés liés aux paris sportifs à partir de cette matrice ;
- simuler la Coupe du Monde complète des milliers de fois ;
- mettre à jour les prédictions après chaque match réel ;
- afficher ce que l’IA avait anticipé correctement ou non ;
- proposer un accès payant symbolique, par exemple 5 €, pour débloquer toutes les prédictions.

Le prototype n’a pas vocation, dans un premier temps, à devenir une plateforme publique de paris sportifs. Il s’agit d’un **outil d’analyse probabiliste**, de simulation et de comparaison entre intuition humaine et modèle statistique.

---

## 2. Pitch du projet

> Une application qui simule la Coupe du Monde 2026 des milliers de fois, estime les probabilités de score de chaque match, déduit automatiquement les marchés associés, puis met à jour ses prédictions après chaque résultat réel.

Formulation plus courte :

> **Une IA qui transforme les données football en scénarios, probabilités et marchés lisibles pour la Coupe du Monde 2026.**

---

## 3. Contexte Coupe du Monde 2026

La Coupe du Monde 2026 se joue avec un format élargi :

- 48 équipes ;
- 12 groupes de 4 équipes ;
- 104 matchs au total ;
- qualification des deux premiers de chaque groupe ;
- qualification également des 8 meilleurs troisièmes ;
- phase à élimination directe à partir des 32es de finale.

Sources utiles :

- FIFA — calendrier et format Coupe du Monde 2026 : https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/articles/match-schedule-fixtures-results-teams-stadiums
- API-Football — guide Coupe du Monde 2026 : https://www.api-football.com/news/post/fifa-world-cup-2026-guide-to-using-data-with-api-sports
- API-Football — documentation générale : https://www.api-football.com/documentation-v3

---

## 4. Objectif du prototype

Le but du prototype est de valider quatre choses :

1. **La faisabilité technique**
   - Peut-on récupérer les matchs ?
   - Peut-on générer des probabilités de score ?
   - Peut-on simuler un tournoi complet ?
   - Peut-on mettre à jour les prédictions après les vrais résultats ?

2. **La lisibilité de l’interface**
   - Est-ce qu’un ami comprend rapidement ce que l’IA propose ?
   - Est-ce que la matrice de score est compréhensible ?
   - Est-ce que les marchés déduits sont utiles ?

3. **L’intérêt utilisateur**
   - Est-ce que les gens reviennent après les matchs ?
   - Est-ce qu’ils veulent comparer leur intuition avec l’IA ?
   - Est-ce que l’historique des prédictions les rassure ?

4. **L’intérêt commercial**
   - Est-ce qu’un paiement symbolique de 5 € semble acceptable ?
   - Est-ce que l’accès payant donne envie ?
   - Est-ce que l’argument “50 000 simulations” est compris ?

---

## 5. Périmètre du MVP

### Inclus dans le prototype

Le prototype doit inclure :

- une page d’accueil ;
- une liste des matchs ;
- une page détail match ;
- une matrice de scores ;
- les marchés déduits de la matrice ;
- un simulateur de tournoi ;
- une page “ce que l’IA avait anticipé” ;
- une page de transparence ;
- une page d’accès premium, même si le paiement est simulé au début ;
- un mini back-office pour déclencher ou suivre les mises à jour.

### Non inclus dans la première version

À éviter au début :

- modèle live très complexe minute par minute ;
- gestion complète des comptes utilisateurs ;
- application mobile native ;
- algorithme de mise automatique ;
- promesse de gain ;
- intégration trop poussée avec plusieurs bookmakers ;
- gestion juridique complète d’une plateforme de pronostics publique.

---

## 6. Principe central : la matrice de scores

Pour chaque match, le moteur produit une matrice de probabilités de score.

Exemple fictif :

| Score | Probabilité |
|---|---:|
| 0-0 | 6 % |
| 1-0 | 13 % |
| 1-1 | 10 % |
| 2-0 | 11 % |
| 2-1 | 12 % |
| 0-1 | 7 % |
| 1-2 | 5 % |
| 3-1 | 4 % |

La matrice peut couvrir les scores de `0-0` à `5-5`.

Il faut prévoir une catégorie résiduelle pour les scores rares :

```text
Autres scores = probabilité restante
```

Cela évite de perdre une partie de la masse de probabilité lorsque le score dépasse 5 buts pour une équipe.

---

## 7. Déduction automatique des marchés

La matrice ne sert pas seulement à prédire un score. Elle sert aussi à déduire des marchés.

### 7.1 Résultat du match

À partir de la matrice :

```text
Victoire équipe A = somme des probabilités où buts_A > buts_B
Match nul = somme des probabilités où buts_A = buts_B
Victoire équipe B = somme des probabilités où buts_A < buts_B
```

Marchés associés :

| Marché | Calcul |
|---|---|
| 1 | Victoire équipe A |
| X | Match nul |
| 2 | Victoire équipe B |
| 1X | Victoire équipe A ou nul |
| X2 | Victoire équipe B ou nul |
| 12 | Une équipe gagne, pas de nul |

---

### 7.2 Over / Under

Exemples :

```text
Over 0.5 = somme des scores où total_buts >= 1
Over 1.5 = somme des scores où total_buts >= 2
Over 2.5 = somme des scores où total_buts >= 3
Over 3.5 = somme des scores où total_buts >= 4

Under 2.5 = somme des scores où total_buts <= 2
Under 3.5 = somme des scores où total_buts <= 3
```

Marchés associés :

| Marché | Interprétation |
|---|---|
| +0,5 but | au moins 1 but |
| +1,5 buts | au moins 2 buts |
| +2,5 buts | au moins 3 buts |
| -2,5 buts | maximum 2 buts |
| -3,5 buts | maximum 3 buts |

---

### 7.3 Les deux équipes marquent

```text
BTTS Oui = somme des scores où buts_A >= 1 et buts_B >= 1
BTTS Non = 1 - BTTS Oui
```

Marchés associés :

| Marché | Calcul |
|---|---|
| Les deux équipes marquent — Oui | buts_A >= 1 et buts_B >= 1 |
| Les deux équipes marquent — Non | au moins une équipe ne marque pas |

---

### 7.4 Scores exacts

La matrice permet d’afficher les scores exacts les plus probables.

Exemple :

| Rang | Score | Probabilité |
|---:|---|---:|
| 1 | 1-0 | 13 % |
| 2 | 2-1 | 12 % |
| 3 | 2-0 | 11 % |
| 4 | 1-1 | 10 % |
| 5 | 0-0 | 6 % |

---

### 7.5 Marchés combinés

La matrice permet aussi de créer des marchés plus avancés :

| Marché | Exemple de calcul |
|---|---|
| Équipe A gagne et +1,5 buts | buts_A > buts_B et total_buts >= 2 |
| Équipe A gagne sans encaisser | buts_A > buts_B et buts_B = 0 |
| Équipe A gagne et les deux marquent | buts_A > buts_B et buts_A >= 1 et buts_B >= 1 |
| Match serré | écart de buts <= 1 |
| Nul faible score | score nul et total_buts <= 2 |
| Équipe A marque +0,5 | buts_A >= 1 |
| Équipe A marque +1,5 | buts_A >= 2 |

---

## 8. Structure des données d’une prédiction match

Exemple de structure JSON :

```json
{
  "match_id": "france_senegal_001",
  "home_team": "France",
  "away_team": "Sénégal",
  "generated_at": "2026-06-15T14:03:00Z",
  "prediction_version": "v2026.06.15-1403",
  "score_matrix": {
    "0-0": 0.06,
    "1-0": 0.13,
    "1-1": 0.10,
    "2-0": 0.11,
    "2-1": 0.12,
    "0-1": 0.07
  },
  "markets": {
    "home_win": 0.54,
    "draw": 0.25,
    "away_win": 0.21,
    "home_or_draw": 0.79,
    "over_1_5": 0.68,
    "over_2_5": 0.47,
    "btts_yes": 0.49
  },
  "confidence": "medium"
}
```

---

## 9. Simulation du tournoi

Le moteur ne simule pas seulement les matchs individuellement. Il simule le tournoi complet.

### 9.1 Étapes d’une simulation

Pour une simulation unique :

```text
1. Jouer tous les matchs de groupe
2. Calculer les classements
3. Identifier les deux premiers de chaque groupe
4. Identifier les huit meilleurs troisièmes
5. Construire le tableau des 32es
6. Simuler les 32es
7. Simuler les 16es
8. Simuler les quarts
9. Simuler les demies
10. Simuler la finale
11. Stocker le champion et le parcours complet
```

### 9.2 Répétition Monte Carlo

On répète ce processus un grand nombre de fois :

```text
Nombre de simulations prototype : 10 000
Nombre de simulations cible : 50 000
Nombre de simulations avancé : 100 000+
```

Pour le prototype personnel, 10 000 peut suffire.
Pour la communication produit, 50 000 est plus parlant et plus crédible.

---

## 10. Résultats à afficher après les simulations

Pour chaque équipe :

| Statistique | Exemple |
|---|---:|
| Chance de sortir du groupe | 78 % |
| Chance d’aller en 8es | 54 % |
| Chance d’aller en quarts | 32 % |
| Chance d’aller en demies | 18 % |
| Chance d’aller en finale | 9 % |
| Chance de gagner la Coupe du Monde | 4 % |

Pour chaque match :

| Statistique | Exemple |
|---|---:|
| Victoire équipe A | 54 % |
| Nul | 25 % |
| Victoire équipe B | 21 % |
| Over 2,5 | 47 % |
| BTTS Oui | 49 % |
| Score exact le plus probable | 1-0 |

---

## 11. Workflow de mise à jour des données

C’est une fonctionnalité importante du projet.

L’application doit pouvoir intégrer les résultats réels, puis relancer les simulations à partir de l’état réel du tournoi.

---

### 11.1 Workflow simple du prototype

Pour la version personnelle, il est possible de commencer avec un workflow semi-manuel.

```text
1. Le match réel se termine
2. Le score est récupéré via API-Football ou saisi manuellement
3. Le match est marqué comme terminé
4. Le classement du groupe est recalculé
5. Les prédictions précédentes sont archivées
6. Les simulations sont relancées
7. Une nouvelle version des prédictions est générée
8. Le frontend affiche les nouvelles probabilités
9. L’historique compare la prédiction initiale au résultat réel
```

Dans cette version, un bouton admin peut suffire :

```text
Bouton : "Intégrer le résultat et relancer les simulations"
```

---

### 11.2 Workflow automatisé plus tard

Une version automatisée pourrait fonctionner ainsi :

```text
Cron toutes les 1 à 5 minutes
      ↓
Récupération des matchs du jour
      ↓
Détection des changements de statut
      ↓
Si un match passe à "terminé"
      ↓
Mise à jour du score réel
      ↓
Recalcul du classement
      ↓
Relance de 50 000 simulations
      ↓
Publication des nouveaux résultats
      ↓
Mise à jour de l’historique IA
```

---

### 11.3 Déclencheurs de recalcul

Il existe plusieurs niveaux possibles.

#### Niveau 1 — Live léger

Pendant le match, on met à jour :

- score live ;
- minute ;
- tirs ;
- tirs cadrés ;
- cartons ;
- possession ;
- événements majeurs.

Mais on ne relance pas forcément 50 000 simulations à chaque événement.

---

#### Niveau 2 — Événement majeur

Plus tard, on pourrait recalculer partiellement après :

- but ;
- carton rouge ;
- blessure importante ;
- mi-temps ;
- prolongation ;
- séance de tirs au but.

Pour le prototype, ce niveau peut être ignoré.

---

#### Niveau 3 — Fin de match

C’est le niveau prioritaire.

À la fin d’un match :

```text
Résultat réel validé
      ↓
État du tournoi mis à jour
      ↓
50 000 simulations relancées
      ↓
Nouvelles probabilités publiées
```

---

## 12. Versioning des prédictions

Chaque prédiction doit être horodatée et rattachée à une version.

Exemple :

```text
Version IA : v2026.06.15-1403
Générée le : 15 juin 2026 à 14:03
Match : France - Sénégal
Coup d’envoi : 15 juin 2026 à 21:00
```

Cela permet de prouver que la prédiction était disponible avant le match.

### Pourquoi c’est important

Le versioning sert à :

- éviter les accusations de modification après coup ;
- comparer proprement prédiction et résultat réel ;
- afficher un historique crédible ;
- montrer ce que l’IA avait réellement anticipé ;
- renforcer la confiance des utilisateurs.

---

## 13. Page “Ce que l’IA avait anticipé”

Cette page sert d’argument commercial.

Elle permet à quelqu’un qui arrive sur le site de voir que l’IA a déjà identifié certains bons signaux.

Le wording doit rester prudent.
Éviter :

```text
Tous les paris gagnants de l’IA
Pronostics garantis
Tickets sûrs
Gagnez de l’argent
```

Préférer :

```text
Ce que l’IA avait anticipé
Historique des signaux IA
Prédictions validées par les matchs
Signaux détectés avant coup d’envoi
```

---

### 13.1 Exemple de bloc marketing

```text
Ce que l’IA avait anticipé récemment

France - Sénégal
Signal IA avant-match :
France gagne ou nul — 78 %
Résultat réel :
France 1-0 Sénégal
Statut :
Signal validé

Brésil - Japon
Signal IA avant-match :
Plus de 1,5 buts — 72 %
Résultat réel :
Brésil 2-0 Japon
Statut :
Signal validé

Argentine - Canada
Signal IA avant-match :
Les deux équipes marquent — 61 %
Résultat réel :
Argentine 2-0 Canada
Statut :
Signal non validé
```

---

### 13.2 Ne pas afficher uniquement les réussites

Pour être crédible, il faut aussi afficher les prédictions ratées.

Sinon, on tombe dans un biais de sélection.

L’idéal :

- sur la page d’accueil : afficher quelques bons signaux récents ;
- sur une page complète : afficher l’historique complet, réussites et échecs.

Exemple :

| Match | Signal IA | Probabilité | Résultat réel | Statut |
|---|---|---:|---|---|
| France - Sénégal | France ou nul | 78 % | 1-0 | Validé |
| Brésil - Japon | +1,5 buts | 72 % | 2-0 | Validé |
| Argentine - Canada | BTTS Oui | 61 % | 2-0 | Non validé |
| Espagne - Maroc | Espagne gagne | 54 % | 1-1 | Non validé |

---

## 14. Écran “Impact du dernier match”

Très bon écran pour montrer l’intérêt de relancer les simulations.

Exemple :

```text
Impact de France 1-0 Sénégal

Avant le match :
France 1re du groupe : 42 %
France qualifiée : 78 %
France vainqueur final : 8,4 %

Après le match :
France 1re du groupe : 56 %
France qualifiée : 89 %
France vainqueur final : 9,7 %

Impact :
+14 points pour la 1re place du groupe
+11 points pour la qualification
+1,3 point pour le titre
```

Cet écran rend le moteur vivant.
Il montre que les prédictions ne sont pas figées.

---

## 15. Écran “Centre de mises à jour IA”

Cette page peut être publique en version simplifiée.

Exemple :

```text
Dernière mise à jour IA

Dernier match intégré :
France 1-0 Sénégal

Nouvelles simulations :
50 000 scénarios rejoués

Mis à jour :
15 juin 2026 — 22:58

Impact principal :
France : +7,4 % de chances de terminer 1re du groupe
Sénégal : -5,1 % de chances de qualification
```

---

## 16. Back-office personnel

Pour le prototype, un petit back-office peut suffire.

### Fonctionnalités admin

- voir les matchs du jour ;
- voir le statut API ;
- importer ou mettre à jour les scores ;
- lancer les simulations ;
- voir la dernière version publiée ;
- corriger manuellement un score si besoin ;
- voir les erreurs éventuelles.

Exemple :

```text
Admin — Pipeline IA

Matchs surveillés aujourd’hui : 4
Matchs terminés : 2
Simulations en attente : 1
Dernier run : succès
Durée du dernier run : 42 secondes
Nombre de scénarios : 50 000
Version publiée : v2026.06.15-2258
```

---

## 17. Architecture technique simple

Pour un prototype personnel, il faut privilégier la simplicité.

### Option recommandée

```text
Frontend : Next.js ou React
Backend : Python FastAPI ou Node.js
Simulation : Python
Base de données : SQLite ou PostgreSQL
Paiement : Stripe Checkout, ou paiement simulé au début
Données foot : API-Football
Déploiement : Vercel / Render / Railway / serveur perso
```

### Architecture logique

```text
API-Football
      ↓
Backend
      ↓
Base de données
      ↓
Moteur de prédiction
      ↓
Moteur de simulation
      ↓
Résultats JSON / DB
      ↓
Frontend
      ↓
Page gratuite / page premium
```

---

## 18. Architecture MVP encore plus simple

Pour aller vite :

```text
1. Script Python local
2. Récupération des fixtures
3. Génération des matrices
4. Simulation du tournoi
5. Export predictions.json
6. Frontend statique qui lit predictions.json
7. Mise à jour manuelle après chaque match
```

Avantage :

- rapide à construire ;
- peu coûteux ;
- facile à partager ;
- pas besoin d’infrastructure complexe ;
- suffisant pour tester avec des amis.

Inconvénient :

- moins automatisé ;
- moins scalable ;
- moins fiable si beaucoup d’utilisateurs.

---

## 19. Tables de base de données possibles

### Table `matches`

```text
id
api_fixture_id
home_team
away_team
kickoff_at
group_name
stage
status
home_score
away_score
winner
last_checked_at
```

---

### Table `prediction_runs`

```text
id
version
run_type
trigger_type
trigger_match_id
number_of_simulations
started_at
finished_at
status
published
```

---

### Table `match_predictions`

```text
id
match_id
prediction_run_id
generated_at
score_matrix_json
markets_json
confidence
is_premium
```

---

### Table `team_tournament_predictions`

```text
id
team_id
prediction_run_id
group_qualification_probability
round_of_32_probability
round_of_16_probability
quarter_final_probability
semi_final_probability
final_probability
winner_probability
```

---

### Table `prediction_history`

```text
id
match_id
prediction_run_id
market_name
predicted_probability
threshold
actual_result
validated
evaluated_at
```

---

## 20. API backend possible

### Matchs

```text
GET /api/matches
GET /api/matches/:id
GET /api/matches/:id/prediction
```

### Simulations

```text
GET /api/simulations/latest
POST /api/admin/simulations/run
GET /api/admin/simulations/:id
```

### Historique

```text
GET /api/history/signals
GET /api/history/matches
```

### Premium

```text
POST /api/checkout
GET /api/premium/predictions
```

Pour le prototype, le premium peut être simulé :

```text
Code d’accès : JP2026
```

ou :

```text
Lien privé envoyé aux amis
```

---

## 21. Page gratuite

Objectif : donner envie sans tout dévoiler.

Contenu possible :

```text
Coupe du Monde 2026 — Simulations IA

50 000 scénarios simulés
104 matchs analysés
Matrice de scores pour chaque rencontre
Marchés déduits automatiquement
Mises à jour après chaque résultat réel
```

Blocs gratuits :

- liste des matchs ;
- scores live ou résultats ;
- quelques tendances générales ;
- aperçu flouté des prédictions ;
- historique partiel des signaux IA ;
- CTA vers l’accès premium.

---

## 22. Page premium

Objectif : afficher toute la valeur.

Contenu :

```text
Débloquez toutes les prédictions IA — 5 €

Inclus :
- toutes les matrices de scores ;
- probabilités 1X2 ;
- double chance ;
- over/under ;
- les deux équipes marquent ;
- scores exacts les plus probables ;
- chances de qualification ;
- chances d’aller en finale ;
- chances de gagner la Coupe du Monde ;
- mises à jour après les matchs réels ;
- historique des signaux IA.
```

Pour un prototype entre amis, cette page peut simplement être protégée par un code.

---

## 23. Page détail match

Exemple :

```text
France - Sénégal
Groupe A
Coup d’envoi : 15 juin 2026 — 21:00

Prédiction IA
France gagne : 54 %
Nul : 25 %
Sénégal gagne : 21 %

Scores les plus probables
1-0 : 13 %
2-1 : 12 %
2-0 : 11 %
1-1 : 10 %

Marchés déduits
France ou nul : 79 %
Plus de 1,5 buts : 68 %
Moins de 3,5 buts : 76 %
Les deux équipes marquent : 49 %

Confiance du modèle
Moyenne
```

---

## 24. Page transparence

Cette page est importante pour la crédibilité.

Texte possible :

```text
Notre IA ne devine pas les résultats.
Elle estime des probabilités.

Pour chaque match, le moteur génère une matrice de scores possibles.
Chaque score reçoit une probabilité.
À partir de cette matrice, nous calculons automatiquement les marchés :
résultat du match, double chance, over/under, les deux équipes marquent,
scores exacts et marchés combinés.

Le tournoi complet est ensuite simulé des milliers de fois.
Les probabilités de qualification, de finale et de victoire finale sont calculées
à partir de ces simulations.

Après chaque match réel, le résultat est intégré et les simulations sont rejouées
à partir du nouvel état du tournoi.
```

Phrase pédagogique importante :

```text
Une probabilité de 60 % ne signifie pas que l’événement va forcément se produire.
Cela signifie que, dans nos simulations, cet événement se produit environ 6 fois sur 10.
```

---

## 25. Avertissement important

Même pour un prototype personnel, il faut être clair.

Texte recommandé :

```text
Les prédictions affichées sont des estimations statistiques.
Elles ne garantissent aucun résultat.
Elles ne constituent pas un conseil financier ni une incitation à parier.
Les paris sportifs comportent un risque de perte d’argent.
Service réservé aux personnes majeures.
```

Éviter les formulations :

```text
Pari sûr
Gain garanti
Ticket gagnant
100 % fiable
Devenez rentable
```

Préférer :

```text
Probabilité estimée
Signal statistique
Marché détecté
Tendance IA
Confiance du modèle
Analyse informative
```

---

## 26. Moteur de prédiction : version simple

Pour le prototype, il n’est pas nécessaire de créer un modèle trop complexe.

Une version simple peut utiliser :

- rating de l’équipe ;
- forme récente ;
- buts marqués ;
- buts encaissés ;
- niveau moyen des adversaires ;
- compétition ;
- avantage géographique éventuel ;
- données historiques.

Le moteur peut produire deux valeurs principales :

```text
expected_goals_home
expected_goals_away
```

Ensuite, on génère une distribution de scores.

---

## 27. Pseudo-code pour une matrice de score

```python
def generate_score_matrix(home_xg, away_xg, max_goals=5):
    matrix = {}

    for home_goals in range(max_goals + 1):
        for away_goals in range(max_goals + 1):
            probability = poisson(home_goals, home_xg) * poisson(away_goals, away_xg)
            matrix[f"{home_goals}-{away_goals}"] = probability

    total = sum(matrix.values())

    # Normalisation optionnelle
    for score in matrix:
        matrix[score] = matrix[score] / total

    return matrix
```

---

## 28. Pseudo-code pour déduire les marchés

```python
def derive_markets(score_matrix):
    markets = {
        "home_win": 0,
        "draw": 0,
        "away_win": 0,
        "over_1_5": 0,
        "over_2_5": 0,
        "under_2_5": 0,
        "btts_yes": 0,
        "btts_no": 0
    }

    for score, probability in score_matrix.items():
        home_goals, away_goals = map(int, score.split("-"))
        total_goals = home_goals + away_goals

        if home_goals > away_goals:
            markets["home_win"] += probability
        elif home_goals == away_goals:
            markets["draw"] += probability
        else:
            markets["away_win"] += probability

        if total_goals >= 2:
            markets["over_1_5"] += probability

        if total_goals >= 3:
            markets["over_2_5"] += probability
        else:
            markets["under_2_5"] += probability

        if home_goals >= 1 and away_goals >= 1:
            markets["btts_yes"] += probability
        else:
            markets["btts_no"] += probability

    markets["home_or_draw"] = markets["home_win"] + markets["draw"]
    markets["away_or_draw"] = markets["away_win"] + markets["draw"]
    markets["no_draw"] = markets["home_win"] + markets["away_win"]

    return markets
```

---

## 29. Pseudo-code de simulation du tournoi

```python
def simulate_tournament(fixtures, teams, prediction_model):
    group_results = []

    for match in group_stage_matches(fixtures):
        matrix = prediction_model.predict_score_matrix(match)
        simulated_score = sample_score_from_matrix(matrix)
        group_results.append((match, simulated_score))

    standings = compute_group_standings(group_results)
    qualified_teams = compute_qualified_teams(standings)

    bracket = build_round_of_32_bracket(qualified_teams)

    while not bracket.is_finished():
        for match in bracket.current_round_matches():
            matrix = prediction_model.predict_score_matrix(match)
            simulated_score = sample_knockout_score(matrix)
            winner = determine_winner(simulated_score, match)
            bracket.advance(winner)

    return bracket.champion
```

---

## 30. Pseudo-code du recalcul après un vrai match

```python
def integrate_finished_match(match_id, real_score):
    update_match_result(match_id, real_score)
    archive_previous_predictions(match_id)
    recompute_group_standings()
    run = create_prediction_run(
        trigger_type="finished_match",
        trigger_match_id=match_id,
        number_of_simulations=50000
    )
    results = run_tournament_simulations(number_of_simulations=50000)
    store_results(run.id, results)
    publish_results(run.id)
    evaluate_prediction_history(match_id)
```

---

## 31. Fonction “confiance du modèle”

Les probabilités brutes peuvent être difficiles à lire.

Il est utile d’ajouter un niveau de confiance :

```text
Signal faible
Signal moyen
Signal fort
```

Exemple de règles simples :

```text
Signal fort :
probabilité >= 70 %

Signal moyen :
probabilité entre 58 % et 70 %

Signal faible :
probabilité entre 50 % et 58 %
```

Mais attention : un signal fort ne veut pas dire résultat garanti.
Il signifie seulement que le modèle observe une probabilité élevée.

---

## 32. Fonction “ma propre intuition vs IA”

Très intéressante pour tes amis.

Exemple :

```text
Ton intuition :
France gagne et +1,5 buts

Lecture IA :
France gagne : 54 %
+1,5 buts : 68 %
France gagne et +1,5 buts : 41 %

Conclusion :
L’IA confirme partiellement ton intuition.
Elle voit bien un match favorable à la France, mais le scénario combiné reste modéré.
```

Cette fonctionnalité rend l’application plus personnelle et plus interactive.

---

## 33. Roadmap du prototype

### Phase 1 — Cadrage

- définir les écrans ;
- définir les données nécessaires ;
- choisir la stack ;
- préparer le schéma de données ;
- créer un fichier de configuration des équipes et matchs.

### Phase 2 — Moteur match

- récupérer ou saisir les matchs ;
- générer une matrice de scores ;
- déduire les marchés ;
- afficher les résultats sur une page détail match.

### Phase 3 — Simulateur tournoi

- simuler les groupes ;
- calculer les classements ;
- construire les tours à élimination directe ;
- simuler jusqu’au champion ;
- répéter 10 000 puis 50 000 fois.

### Phase 4 — Interface

- page accueil ;
- liste des matchs ;
- détail match ;
- page premium ;
- page historique ;
- page transparence.

### Phase 5 — Mise à jour

- intégrer les vrais résultats ;
- relancer les simulations ;
- versionner les prédictions ;
- afficher l’impact avant/après.

### Phase 6 — Partage amis

- héberger le prototype ;
- protéger la page premium par code ;
- partager le lien ;
- récupérer les retours ;
- améliorer l’UX.

---

## 34. Priorités pour ne pas se disperser

Priorité absolue :

```text
1. Générer une matrice de score
2. Déduire les marchés
3. Simuler le tournoi
4. Afficher proprement les résultats
5. Mettre à jour après un résultat réel
```

À ne pas prioriser au début :

```text
1. Paiement réel
2. Comptes utilisateurs
3. Live avancé
4. Application mobile
5. Modèle prédictif trop complexe
6. Back-office complet
```

---

## 35. Indicateurs à suivre

Pour savoir si le prototype plaît :

- combien d’amis ouvrent le lien ;
- combien consultent plusieurs matchs ;
- combien regardent la page “ce que l’IA avait anticipé” ;
- combien demandent les prédictions premium ;
- combien reviennent après un match ;
- quelles prédictions ils trouvent utiles ;
- quelles pages ils ne comprennent pas.

---

## 36. Risques du projet

### Risque 1 — Trop de complexité

Solution : commencer avec un modèle simple et une mise à jour semi-manuelle.

### Risque 2 — Trop de promesses

Solution : parler de probabilités, pas de certitudes.

### Risque 3 — Données incomplètes

Solution : prévoir une saisie manuelle de secours.

### Risque 4 — Interprétation “pari garanti”

Solution : ajouter des avertissements clairs et un wording prudent.

### Risque 5 — Mauvaise lisibilité

Solution : éviter les tableaux trop techniques sur les premières pages.

---

## 37. Nom possible du projet

Idées :

- WorldCup AI Lab
- Mondial Predictor
- CoupeIA 2026
- SimuMondial
- MatchMatrix 2026
- Scenario 2026
- FootForecast 2026
- Mondial Matrix
- IA Mondial
- ScoreMatrix 2026

Nom simple recommandé pour prototype :

> **SimuMondial 2026**

---

## 38. Résumé final

Le prototype doit montrer une idée simple :

> L’IA ne donne pas un résultat magique. Elle simule des milliers de futurs possibles, puis transforme ces simulations en probabilités lisibles.

Les trois piliers du produit :

```text
1. Matrice de scores
2. Marchés déduits
3. Simulations du tournoi
```

Les deux fonctionnalités qui rendent l’application vraiment intéressante :

```text
1. Rejouer les simulations après chaque vrai résultat
2. Montrer ce que l’IA avait anticipé avant les matchs
```

La meilleure promesse produit :

> Compare ton intuition avec les probabilités issues de milliers de simulations.

La meilleure phrase de transparence :

> Une probabilité n’est pas une certitude. C’est une mesure de fréquence dans les scénarios simulés.

---

## 39. Prochaine étape recommandée

Construire une première version très simple :

```text
1. Un fichier avec 10 matchs fictifs
2. Une matrice de score générée automatiquement
3. Des marchés déduits
4. Une simulation de tournoi simplifiée
5. Une interface avec 3 pages :
   - Accueil
   - Détail match
   - Historique IA
```

Une fois cette base fonctionnelle, il sera beaucoup plus facile d’ajouter :

- API-Football ;
- Coupe du Monde complète ;
- 50 000 simulations ;
- mise à jour réelle ;
- page premium ;
- back-office.
