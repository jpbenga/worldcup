# Team Identity Mapping Guide

## Objectif

La couche V0.3.1 relie les équipes normalisées API-Football aux libellés Elo
Ratings et à un code pays interne. Elle ne branche pas les ratings Elo au
moteur de prédiction et ne modifie aucune probabilité.

## Fichiers

- `backend/data/mappings/team_aliases.json` : alias explicites et relus ;
- `backend/data/mappings/team_identity_map.json` : correspondances
  déterministes utilisables ;
- `backend/data/mappings/unmapped_teams.json` : éléments non résolus et
  suggestions à revoir ;
- `backend/data/mappings/team_mapping_report.json` : métriques de génération ;
- `backend/data/snapshots/team_mapping_status.json` : résumé publié pour
  Angular.

## Génération et validation

```bash
python3 backend/scripts/build_team_identity_map.py
python3 backend/scripts/validate_team_mappings.py
python3 backend/scripts/build_snapshots.py
```

Le générateur applique, dans l'ordre :

1. le nom strictement identique ;
2. le nom identique après normalisation des accents et de la ponctuation ;
3. un alias explicite inscrit dans `team_aliases.json` ;
4. des candidats flous uniquement comme aide à la revue.

Une correspondance floue n'est jamais ajoutée automatiquement à
`team_identity_map.json`.

`team_identity_map.json` est une liste des correspondances retenues. Chaque
objet contient l'identité interne, l'identifiant et le nom API-Football, le nom
et le rating Elo, puis le statut, la méthode, la confiance et le besoin de
revue. `unmapped_teams.json` sépare les équipes API non résolues des entrées Elo
hors du périmètre courant.

## Alias explicites actuels

| API-Football | Elo Ratings |
|---|---|
| Bosnia & Herzegovina | Bosnia and Herzegovina |
| Cape Verde Islands | Cape Verde |
| Congo DR | DR Congo |
| Czech Republic | Czechia |
| Türkiye | Turkey |
| USA | United States |

Autres variantes explicites prévues pour de futurs imports :
`Korea Republic/South Korea`, `Côte d'Ivoire/Ivory Coast`,
`IR Iran/Iran` et `UAE/United Arab Emirates`.

## Revue manuelle d'un nouveau cas

1. Lire l'équipe API et les candidats dans `unmapped_teams.json`.
2. Vérifier l'identité avec une source humaine fiable et le code pays.
3. En cas de certitude, ajouter uniquement l'alias nécessaire à
   `team_aliases.json`.
4. Relancer la génération et le validateur.
5. Vérifier les doublons, le rapport et l'encart Angular.
6. Consigner toute réserve dans `docs/VALIDATION_LOG.md`.

Ne pas ajouter d'alias si deux pays ou sélections peuvent raisonnablement
correspondre au même libellé. Un cas ambigu doit rester `needs_review` ou
`unmapped`.

Pour accepter humainement une suggestion, déplacer sa correspondance vérifiée
dans `team_identity_map.json` avec `mapping.status=manual_validated`,
`mapping.method=manual`, `needs_human_review=false` et une note sourcée. Pour
la rejeter, conserver le cas hors du mapping et inscrire `status=rejected` avec
la justification. Toute modification manuelle doit ensuite passer le
validateur. Pour survivre à une régénération, une correspondance acceptée doit
aussi être représentée par un alias explicite.

## Checklist rapide

- [ ] aucun doublon de `team_id`, identifiant API ou nom Elo ;
- [ ] chaque alias est déterministe et humainement vérifié ;
- [ ] aucune correspondance floue n'est marquée `matched` ;
- [ ] les compteurs du rapport correspondent aux fichiers produits ;
- [ ] Elo reste non connecté au moteur de prédiction.

## Human validation checklist

- [ ] Chaque équipe World Cup API-Football a un mapping ou une raison claire d'absence.
- [ ] Aucun mapping ambigu n'est auto-validé.
- [ ] Les alias sensibles ont été vérifiés.
- [ ] Les pays avec plusieurs noms anglais/français ont été vérifiés.
- [ ] Les doublons sont absents.
- [ ] Les ratings Elo semblent associés à la bonne équipe.
- [ ] Les mappings `needs_review` sont traités avant intégration au modèle.
