# Unified Local Refresh Validation V2.18

La validation unifiée vérifie le manifest, la décision de refresh, l’audit de workspace, la commande de lancement unique, le statut de fraîcheur, le doctor, Road to the Trophy officiel, son view model et la présence documentée de la transparence. Elle confirme également que le dry-run est non destructif et que la clé API reste locale.

Les prédictions actives et `quant_hybrid_v2.2` sont protégés par diff et hashes. Optuna n’est jamais lancé. Road to the Trophy peut être régénéré localement lorsque des résultats officiels changent, mais ces sorties Matchday restent hors du commit V2.18 sauf livraison explicitement dédiée.

La validation accepte des avertissements liés au workspace sale connu. Elle bloque en revanche l’absence de commande unique, un manifest incomplet, une prédiction active modifiée ou un moteur Road to the Trophy non officiel.
