# Local Refresh Needed V2.18

`check_local_refresh_needed_v2_18.py` décide si le lancement local doit reconstruire les données. Il compare le nombre de résultats terminés avec le nombre de résultats verrouillés dans la dernière simulation V3, la fraîcheur, le nombre de simulations demandé, la présence des manifests et validations, la version officielle de Road to the Trophy et les assets frontend indispensables.

Le rapport distingue le besoin de refresh général, de reconstruction transparence, de reconstruction Road to the Trophy et de copie frontend. Il indique aussi si la simulation lourde peut être sautée sans risque. L’option `--force` transforme explicitement toutes les décisions en rebuild demandé.

La détection ne récupère pas l’API, ne modifie aucun résultat et ne lance aucune simulation. Elle publie seulement un diagnostic local auditable. Un statut stale ne prétend jamais que les données sont fraîches.
