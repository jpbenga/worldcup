# Documentation Cleanup Strategy V2.16

La documentation a grandi avec chaque expérience, audit et validation. Cette traçabilité est précieuse, mais la présence de plus de cent documents au même niveau masque aujourd’hui les informations utiles au quotidien. Documentation cleanup must reduce cognitive load without destroying project traceability.

La nouvelle architecture distingue documentation produit, technique, opérations, validation et archive. Les documents actifs visibles à la racine `docs/` sont l’index, la vue produit, Road to the Trophy, modèles et simulation, pipeline data, runbook, journal de validation, checklist manuelle et feuille de route. Les stratégies détaillées d’itération passent dans `archive/iterations`, les audits dans `archive/audits` et les release notes dans `archive/release_notes`.

Aucune décision ou validation importante n’est supprimée. Les fichiers modifiés localement avant l’itération restent en place pour ne pas mélanger leur contenu au nettoyage. Les suppressions sont réservées aux doublons exacts ou fichiers vides; aucun cas suffisamment certain n’a été retenu. À l’avenir, une livraison doit d’abord mettre à jour les documents actifs, puis archiver ses notes spécifiques après validation humaine.
