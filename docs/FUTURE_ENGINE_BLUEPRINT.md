# Future Engine Blueprint

## État actuel

Deux moteurs ont des responsabilités distinctes. `quant_hybrid_v2.2` reste le moteur actif pour les prédictions pré-match individuelles. SimuAI Tournament Engine V3 est le moteur officiel de Road to the Trophy et génère les parcours complets du tournoi. Les anciens moteurs, candidats et comparaisons restent accessibles dans les archives, mais ne sont plus des sources publiques concurrentes.

## Priorités

1. Améliorer la qualité, la fraîcheur et la couverture des données API-Football.
2. Intégrer le mapping officiel du tableau éliminatoire dès qu’il est disponible.
3. Évaluer des données joueurs, blessures et compositions uniquement lorsqu’elles deviennent fiables et pré-match.
4. Étendre les backtests chronologiques et la calibration segmentée.
5. Enrichir les explications sans inventer de facteurs absents.
6. Renforcer le déploiement, le monitoring, la reproductibilité et la reprise opérationnelle.

## Règles de promotion

Toute évolution doit être comparée à une baseline, testée hors échantillon et documentée. Une complexité supplémentaire n’est acceptable que si elle améliore les performances robustes ou l’explicabilité. Les données futures ne doivent jamais contaminer l’entraînement historique. Les prédictions publiées ne doivent pas être réécrites après connaissance des résultats.

Road to the Trophy doit conserver une seule source publique de vérité. Les expériences techniques peuvent rester auditées en archive, mais ne doivent pas créer plusieurs scénarios concurrents dans l’interface.
