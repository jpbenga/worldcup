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
- récupération possible : oui, via les TSV structurés chargés par le site ;
- format observé : conteneur HTML rendu avec SlickGrid et fichiers TSV ;
- champs disponibles : rang, code équipe, rating et statistiques historiques ;
- mapping nécessaire : nom Elo vers code et identifiant équipe API-Football ;
- fiabilité du parsing : exploitable pour le spike, à valider humainement ;
- ratings normalisés : `244` ;
- limite : les TSV sont une interface publique observée mais non un contrat
  d'API garanti.

## Elo Ratings raw acquisition

### Pages tested

- https://www.eloratings.net/
- https://www.eloratings.net/2026_World_Cup
- https://www.eloratings.net/latest

### Methods tested

- raw HTML avec `requests` : les trois pages répondent HTTP 200, mais ne
  contiennent qu'un conteneur et les références JavaScript ;
- Playwright network capture : un chargement par page, `89` réponses capturées ;
- Playwright rendered DOM extraction : `244` lignes de classement détectées sur
  la page d'accueil.

### Findings

- JSON endpoint found: non pour les ratings. Les `15` réponses JSON observées
  sont des données de localisation CLDR ;
- structured endpoint found: oui, fichiers TSV publics chargés par la page ;
- endpoints structurés principaux :
  - `https://www.eloratings.net/World.tsv`
  - `https://www.eloratings.net/en.teams.tsv`
  - `https://www.eloratings.net/2026_World_Cup.tsv`
  - `https://www.eloratings.net/latest.tsv`
- rendered table extraction: usable comme contrôle secondaire ;
- normalized ratings produced: oui, à partir de `World.tsv` joint à
  `en.teams.tsv` ;
- number of ratings extracted: `244` ;
- TSV/DOM comparison: les `244/244` couples rang/rating concordent. Un libellé
  utilise une forme longue dans le TSV et une forme courte dans le DOM ;
- limitations: pas de contrat d'API documenté, codes Elo à mapper vers
  API-Football, fraîcheur à surveiller.

### Decision

Utiliser les TSV Elo uniquement comme source expérimentale parallèle. Préférer
le TSV au parsing DOM, conserver la comparaison DOM comme contrôle, et attendre
une validation humaine du mapping avant toute intégration au moteur.

### Alternatives if the source becomes fragile

- `international-football.net` affiche un tableau basé sur Elo Ratings ;
- des datasets GitHub/Kaggle existent mais peuvent être incomplets ou périmés ;
- un Elo interne pourrait être recalculé depuis les résultats historiques
  API-Football.

Ces alternatives sont documentées mais ne sont pas intégrées automatiquement.

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
- conserver Elo comme source expérimentale parallèle fondée sur les TSV.

## Prochaine étape recommandée

Créer une V0.4 limitée au mapping validé des équipes et à l'import manuel d'un
petit snapshot API-Football vers un pipeline parallèle. Ne remplacer le
pipeline principal qu'après validation humaine des correspondances, statuts et
résultats.

## V0.3.1 — Team Identity Mapping

La couche d'identité relie les `48` équipes API-Football normalisées aux
ratings Elo sans modifier le pipeline principal.

- résultat : `48/48` équipes API mappées, couverture `100 %` ;
- méthodes : `42` noms exacts et `6` alias explicites ;
- revue requise : `0` ;
- équipes API non mappées : `0` ;
- entrées Elo hors périmètre API-Football actuel : `196` ;
- intégration au moteur de prédiction : non.

Les règles, alias et étapes de revue sont détaillés dans
`docs/TEAM_MAPPING_GUIDE.md`.
