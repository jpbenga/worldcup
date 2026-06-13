# Production Readiness Validation V2.17

La validation V2.17 confirme la présence et la cohérence de l’audit opérateur, du doctor, du wrapper de refresh, du statut de fraîcheur, du preflight et du runbook quotidien. Elle vérifie également que la validation humaine V2.16 est consignée et que les scripts déclarent explicitement les responsabilités des moteurs.

Cette validation accepte un statut opérateur `warning` lorsque le worktree contient les refreshs Matchday locaux connus ou lorsque les données sont anciennes. Elle exige en revanche que le preflight passe, que la clé API ne soit jamais imprimée, et que les prédictions actives ainsi que `road_to_the_trophy_engine.json` restent inchangés.

V2.17 améliore l’exploitation locale sans réentraîner de modèle, sans relancer Optuna et sans introduire de nouvelle simulation. Les fichiers frontend de statut sont publiés comme contrats de données, mais l’interface n’est pas modifiée afin d’éviter de mélanger les assets Matchday préexistants hors scope.
