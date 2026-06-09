# Limites connues

- **Calibration :** aucune valeur par défaut n'est revendiquée comme calibrée pour les sélections nationales ou la Coupe du Monde 2026.
- **Données :** les scripts réseau historiques ont été exclus à cause de leur couplage fournisseur et de configurations sensibles.
- **Matrice :** Poisson suppose une structure simple; Dixon–Coles ne corrige que les faibles scores. La renormalisation masque la queue au-delà de `max_goals`.
- **Temps de match :** les probabilités représentent le score à la fin du temps réglementaire; prolongations et tirs au but nécessitent des modèles séparés.
- **Backtesting :** le module minimal mesure des validations de signaux, mais pas la calibration, le Brier score, la log loss, le ROI ou les intervalles de confiance.
- **Marchés :** les combinés complexes, handicaps, mi-temps et marchés joueurs ne sont pas implémentés.
- **Identité des équipes :** la normalisation textuelle ne remplace pas un référentiel stable d'identifiants FIFA/fournisseur.
- **Simulation :** aucun orchestrateur de tournoi ou moteur Monte-Carlo complet n'a été trouvé dans l'ancien projet.
- **Imports :** aucun module extrait ne dépend de l'ancien projet; les dépendances historiques impossibles à garantir ont été documentées plutôt que copiées.
