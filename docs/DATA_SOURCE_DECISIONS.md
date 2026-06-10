# Data Source Decisions

| Source | Usage envisagé | Statut | Avantages | Limites | Décision |
|---|---|---|---|---|---|
| API-Football | fixtures, teams, results, standings | tested / usable | World Cup 2026 présente, contrats structurés, identifiants stables | dépendance externe, quota, statistiques futures encore vides | utiliser comme source principale expérimentale des fixtures et résultats |
| Elo Ratings | team strength | tested via raw HTML + Playwright network + rendered DOM / usable with review | TSV structurés découverts, 244 ratings normalisés, comparaison DOM possible | source non contractuelle, mapping des noms/codes et fraîcheur à valider | conserver comme source expérimentale parallèle, sans intégration moteur avant validation humaine |
| FIFA Ranking | team strength alternative | not tested yet | référence officielle potentielle | fréquence et format à étudier | conserver comme source complémentaire future |
| Mock data | tests techniques | keep | stable, reproductible, hors quota | données non réelles | garder pour les tests et le pipeline principal jusqu'à validation du mapping |

## Décisions immédiates

- Conserver le pipeline principal sur les données mock.
- Utiliser API-Football uniquement dans les scripts d'exploration et la
  normalisation expérimentale.
- Ne pas dépendre des statistiques de fixture avant qu'elles soient disponibles.
- Ne pas intégrer les cotes au moteur à ce stade.
- Traiter les noms et codes équipes comme un mapping explicite entre sources.
- Préférer `World.tsv` + `en.teams.tsv` à l'extraction DOM pour Elo Ratings.
- Revalider manuellement la fraîcheur et le mapping Elo avant toute utilisation
  dans le modèle.

## Décision V0.3.1 — Team Identity Mapping

- La couche d'identité API-Football vers Elo est obligatoire avant toute fusion
  de données entre les deux sources.
- Les correspondances exactes et les alias explicites peuvent être publiés dans
  le mapping déterministe.
- Toute suggestion floue reste en revue humaine et ne peut pas être
  auto-validée.
- Le mapping ne constitue pas une autorisation d'utiliser Elo dans le moteur :
  les ratings restent parallèles et n'affectent aucune probabilité.
