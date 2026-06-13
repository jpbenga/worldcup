# Unified Local Refresh V2.18

L’orchestrateur global s’utilise avec `--dry-run`, `--no-fetch`, `--fetch` ou `--force`, avec 50 000 simulations par défaut. Le dry-run affiche chaque script prévu ou sauté sans modifier le workspace. Le mode no-fetch reconstruit depuis les caches locaux; le mode fetch autorise uniquement le script Python local à interroger API-Football.

Lorsque des résultats officiels supplémentaires sont détectés, le pipeline Matchday est exécuté, puis l’historique des prédictions, le scoreboard et la timeline sont reconstruits. SimuAI Tournament Engine V3 génère à nouveau 50 000 tournois complets, le scénario représentatif et Road to the Trophy officiel. La fraîcheur et les validations terminent la chaîne.

Le manifest V2.18 conserve mode, raisons, étapes, sorties, validations et erreurs. Les prédictions actives restent protégées; l’orchestrateur échoue si leurs hashes changent. Il ne réentraîne jamais le modèle et ne relance jamais Optuna.
