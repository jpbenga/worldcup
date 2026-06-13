# Data Pipeline

Le pipeline acquiert les fixtures et résultats via API-Football, normalise les identités d’équipes et combine ces données avec l’historique international et les ratings Elo disponibles. Les résultats réels alimentent les standings live et verrouillent les matchs déjà joués dans Road to the Trophy.

Les responsabilités de stockage sont séparées :

- `backend/data/raw/` conserve les réponses sources;
- `backend/data/normalized/` contient les données structurées;
- `backend/data/generated/` contient les sorties calculées;
- `backend/data/snapshots/` conserve les copies publiées et reproductibles;
- `frontend/src/assets/data/` expose les contrats consommés par Angular.

Le matchday refresh récupère les nouveaux états, reconstruit les vues dépendantes et valide leur cohérence. Les artefacts générés ne doivent être commités que lorsqu’ils font partie d’une livraison explicitement validée. Les caches temporaires, builds, dépendances, environnements virtuels, secrets et fichiers `.env` ne doivent jamais être commités.

Les données futures 2026 restent séparées des données historiques utilisées pour les backtests. Une donnée indisponible ou trop sparse doit être documentée comme limite, jamais inventée.
