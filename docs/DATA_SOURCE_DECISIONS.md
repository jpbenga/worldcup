# Data Source Decisions

| Source | Usage envisagé | Statut | Avantages | Limites | Décision |
|---|---|---|---|---|---|
| API-Football | fixtures, teams, results, standings | tested / usable | World Cup 2026 présente, contrats structurés, identifiants stables | dépendance externe, quota, statistiques futures encore vides | utiliser comme source principale expérimentale des fixtures et résultats |
| Elo Ratings | team strength | tested / fragile | source spécialisée pour équipes nationales | page initiale alimentée par JavaScript, parsing HTML direct non fiable | ne pas intégrer avant une méthode d'extraction stable et validée |
| FIFA Ranking | team strength alternative | not tested yet | référence officielle potentielle | fréquence et format à étudier | conserver comme source complémentaire future |
| Mock data | tests techniques | keep | stable, reproductible, hors quota | données non réelles | garder pour les tests et le pipeline principal jusqu'à validation du mapping |

## Décisions immédiates

- Conserver le pipeline principal sur les données mock.
- Utiliser API-Football uniquement dans les scripts d'exploration et la
  normalisation expérimentale.
- Ne pas dépendre des statistiques de fixture avant qu'elles soient disponibles.
- Ne pas intégrer les cotes au moteur à ce stade.
- Traiter les noms et codes équipes comme un mapping explicite entre sources.
