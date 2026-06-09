# Repo Structure Notes

## Racine Git finale

La racine Git opérationnelle est désormais :

```text
/Users/chloe/Desktop/dossier sans titre/worldcup
```

Elle contient directement :

```text
backend/
docs/
handoff_worldcup_2026/
README.md
prototype_ia_coupe_du_monde_2026.md
.gitignore
```

## Réparation effectuée

Le workspace contenait auparavant deux dépôts Git imbriqués :

```text
/Users/chloe/Desktop/dossier sans titre/worldcup/.git
/Users/chloe/Desktop/dossier sans titre/worldcup/worldcup/.git
```

Le dépôt extérieur ne contenait presque aucun fichier suivi. Le dépôt intérieur
avait perdu ses fichiers de travail après une réécriture d'historique, mais son
reflog contenait encore le commit `94b4f5c`, avec le projet complet et le
virtualenv déjà retiré du suivi.

Les fichiers utiles du commit `94b4f5c` ont été restaurés à la racine
extérieure, sans copier le dépôt Git imbriqué, `drc-nba/`, `.idx/`, les caches
Python ou le virtualenv historique.

`drc-prototype/` a également été exclu du dépôt final : plusieurs scripts
historiques contenaient une clé API codée en dur. Les briques réutilisables et
nettoyées restent disponibles dans `handoff_worldcup_2026/`.

## Sauvegarde locale

Une sauvegarde de l'état antérieur à la réparation a été créée ici :

```text
/Users/chloe/Desktop/dossier sans titre/worldcup-before-codex-repair-20260610-003049
```

Elle doit être conservée jusqu'à vérification complète du dépôt distant.

## Structure recommandée

Une seule racine Git doit rester active. Les futurs dossiers, notamment
`frontend/`, devront être créés directement sous cette racine. Aucun nouveau
dossier `worldcup/` imbriqué ne doit être ajouté.
