# Road to the Trophy UI Regression Hotfix V2.21.1

## Symptôme

Après l'introduction de V4, la première carte groupe était vide et masquait une partie de l'Atlas. Les classements, équipes et matchs ne se rendaient plus, tandis que le bracket et le panneau latéral restaient partiellement visibles.

## Cause racine

Le view-model V4 ne fournissait pas tous les champs directement lus par le template Angular, notamment `simulation_probabilities`, `central_status` et `goals_for`. Une exception de rendu sur la première carte interrompait ensuite le reste de l'Atlas. Le frontend ne possédait aucune couche de normalisation entre les variantes historiques des JSON Road to the Trophy.

## Corrections

- Le contrat V4 publié contient les données complètes des 48 équipes, des 12 groupes, des 72 matchs de groupe et des cinq tours knockout.
- `road-to-the-trophy.adapter.ts` normalise une seule fois les variantes `standings`, `table`, `central_table`, `centralTable`, `matches`, `central_matches`, `centralMatches` et les variantes de probabilités.
- Une carte groupe incomplète n'est plus rendue.
- Un contrat invalide affiche un état compact au lieu d'un grand panneau vide.
- Le libellé de bannière possède désormais un espacement explicite.
- Un audit de contrat et une validation de régression V2.21.1 sont publiés.

## Validation visuelle

Le rendu `/simulation` a été vérifié à l'aide d'une capture automatisée locale : groupes, tables, matchs, bracket, finale Espagne-Équateur et panneau latéral sont visibles. Le build Angular passe. L'adaptateur dispose de tests unitaires couvrant une variante historique et un groupe incomplet.

## Lancement avec rafraîchissement systématique

La commande canonique demandée force la récupération des résultats, la reconstruction des vues dépendantes et V4 avant le lancement :

```bash
python3 backend/scripts/start_local_app_v2_18.py --force-refresh --fetch --simulations 50000
```

Cette commande est volontairement plus longue que `--auto-refresh`, car elle rafraîchit systématiquement les données à chaque lancement.

## Limites restantes

L'avertissement Angular sur le budget CSS de la page Simulation reste non bloquant. Le mapping officiel complet du bracket 2026 reste absent des données du projet.
