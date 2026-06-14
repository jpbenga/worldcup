# Future Engine Blueprint

## État actuel

Deux moteurs ont des responsabilités distinctes. `quant_hybrid_v2.2` reste le moteur actif pour les prédictions pré-match individuelles. SimuAI Tournament Engine V3 est le moteur officiel de Road to the Trophy et génère les parcours complets du tournoi. Les anciens moteurs, candidats et comparaisons restent accessibles dans les archives, mais ne sont plus des sources publiques concurrentes.

## Priorités

1. Encoder le mapping officiel 2026, les départages complets et les meilleurs troisièmes.
2. Nettoyer les sémantiques score à 90 minutes, prolongation et tirs au but.
3. Rendre `quant_hybrid_v2.2` inférable pour toute confrontation du tournoi et réconcilier 1X2/matrice.
4. Simuler séparément 90 minutes, prolongation et tirs au but.
5. Ajouter replay historique tournoi, calibration segmentée, multi-seed et incertitude modèle.
6. Évaluer joueurs, blessures, compositions, odds et xG uniquement lorsque leur couverture pré-match devient fiable.

## Règles de promotion

Toute évolution doit être comparée à une baseline, testée hors échantillon et documentée. Une complexité supplémentaire n’est acceptable que si elle améliore les performances robustes ou l’explicabilité. Les données futures ne doivent jamais contaminer l’entraînement historique. Les prédictions publiées ne doivent pas être réécrites après connaissance des résultats.

Road to the Trophy doit conserver une seule source publique de vérité. Les expériences techniques peuvent rester auditées en archive, mais ne doivent pas créer plusieurs scénarios concurrents dans l’interface.
