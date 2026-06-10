# Real Data Acquisition Report

## Objectif

Vérifier, avec un nombre limité d'appels, que des données football réelles sont
récupérables, compréhensibles et transformables sans remplacer le pipeline mock
actuel.

## Sources testées

### API-Football

- clé configurée : oui, affichée uniquement sous forme masquée ;
- plan détecté : `Pro`, actif lors du test du 10 juin 2026 ;
- quota détecté : `7 500` requêtes par jour ;
- endpoints testés : `/status`, `/leagues`, `/countries`, `/teams/countries`,
  `/fixtures`, `/teams`, `/standings`, `/fixtures/rounds`,
  `/fixtures/statistics`, `/predictions`, `/odds` ;
- endpoints accessibles : tous les endpoints testés ont répondu HTTP 200 ;
- endpoints refusés : aucun pendant ce spike ;
- World Cup 2026 trouvée : oui, `league_id: 1`, saison `2026` ;
- World Cup 2022 disponible comme référence : oui ;
- fixtures : `72` objets retournés pour 2026 ;
- teams : `48` objets retournés pour 2026 ;
- standings : `1` enveloppe de classement retournée ;
- rounds : `3` valeurs retournées ;
- statistics : endpoint accessible, mais `0` résultat pour la fixture future testée ;
- predictions : `1` objet retourné pour la fixture testée ;
- odds : `1` objet retourné pour la fixture testée.

Les dumps complets sont conservés dans
`backend/data/raw/api_football/`. La réponse `/status` publiée a été assainie
pour retirer les informations personnelles de compte.

#### Structures observées

Une fixture contient les blocs principaux :

```json
{
  "fixture": {"id": 1489369, "date": "...", "venue": {}, "status": {}},
  "league": {"id": 1, "name": "World Cup", "season": 2026, "round": "Group Stage - 1"},
  "teams": {"home": {}, "away": {}},
  "goals": {"home": null, "away": null},
  "score": {}
}
```

Un objet équipe contient `id`, `name`, `code`, `country`, `national`, `logo`
et un bloc `venue`. Les prédictions contiennent `predictions`, `league`,
`teams`, `comparison` et `h2h`. Les cotes contiennent `league`, `fixture`,
`update` et `bookmakers`.

#### Champs utiles

- application : identifiants fixture/équipe, compétition, saison, round,
  équipes, date, statut, scores ;
- modèle futur : résultats historiques, statistiques lorsqu'elles existent,
  comparaison et historique direct ;
- mapping requis : identifiants externes, codes pays, noms alternatifs et
  statuts API vers le contrat interne.

#### Limites

- disponibilité des statistiques dépendante du moment et de la fixture ;
- données soumises au quota et au plan externe ;
- prédictions et cotes disponibles mais non nécessaires au moteur actuel ;
- les données réelles ne sont pas encore intégrées au pipeline principal.

### Elo Ratings

- source : https://eloratings.net/ ;
- récupération possible : page initiale joignable ;
- format observé : conteneur HTML dont les données sont chargées par JavaScript ;
- champs disponibles dans la réponse initiale : aucun classement exploitable ;
- mapping nécessaire : nom Elo vers code et identifiant équipe API-Football ;
- fiabilité du parsing : insuffisante ;
- ratings normalisés : aucun, volontairement ;
- limite : une méthode stable et autorisée d'accès aux données doit être
  identifiée avant intégration.

## Mapping vers notre format interne

```text
API-Football fixture
  -> external_fixture_id, competition, season, round, home_team, away_team,
     kickoff_at, status, scores, source_type=api

API-Football team
  -> external_team_id, team_name, country, code, source_type=api

Elo rating
  -> team_name, country_code, elo_rating, rank, source metadata
```

Les preuves de transformation sont dans :

```text
backend/data/normalized/external_matches_sample.json
backend/data/normalized/external_teams_sample.json
backend/data/normalized/team_ratings.json
```

## Décisions recommandées

- utiliser API-Football comme source principale candidate des fixtures,
  équipes, résultats et standings ;
- garder les données mock pour les tests techniques et le pipeline principal ;
- valider un mapping d'équipes avant toute fusion avec une source Elo ;
- ne pas utiliser les odds pour l'instant ;
- ne pas dépendre d'un parsing Elo fragile.

## Prochaine étape recommandée

Créer une V0.4 limitée au mapping validé des équipes et à l'import manuel d'un
petit snapshot API-Football vers un pipeline parallèle. Ne remplacer le
pipeline principal qu'après validation humaine des correspondances, statuts et
résultats.
