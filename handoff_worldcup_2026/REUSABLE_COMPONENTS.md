# Composants réutilisables

## Expected Goals / Elo Lambda Engine

**Ancien chemin :** `drc-prototype/optimizer.py` (`clubelo_win_probability`, `compute_lambdas`) et `drc-prototype/xg-backtest.js` (`calculatePoissonPro`).
**Nouveau chemin :** `handoff_worldcup_2026/recycled_code/score_prediction/expected_goals.py`.
**Rôle :** transforme des xG de base en intensités Poisson domicile/extérieur modulées par Elo; produit aussi des baselines glissantes attaque/défense.
**Entrées :** xG, delta Elo, poids xG/Elo, avantage terrain; ou quatre historiques glissants.
**Sortie :** tuple `(home_lambda, away_lambda)`.
**Dépendances :** bibliothèque standard.
**Réutilisabilité :** élevée pour la formule, calibration obligatoire.
**Adaptations :** extraction hors des globals, noms explicites, validations, paramétrage.
**Limites :** aucune calibration internationale fournie; l'avantage terrain doit être neutralisé/adapté.

## Score Matrix Generator

**Ancien chemin :** boucles Poisson/Dixon–Coles dans `drc-prototype/optimizer.py` et `drc-prototype/xg-backtest.js`.
**Nouveau chemin :** `handoff_worldcup_2026/recycled_code/score_matrix/score_matrix.py`.
**Rôle :** génère chaque score de `0-0` à `max_goals-max_goals`, corrige les faibles scores et normalise la masse tronquée.
**Entrées :** `home_expected_goals`, `away_expected_goals`, `max_goals`, `rho`, `normalize`.
**Sortie :** dictionnaire `score -> probabilité`.
**Dépendances :** bibliothèque standard (`math`).
**Réutilisabilité :** élevée.
**Adaptations :** remplacement de SciPy par la PMF standard, normalisation explicite, top scores, contrôles d'erreur.
**Limites :** indépendance conditionnelle hors correction faible score; plage finie.

## Market Derivation

**Ancien chemin :** agrégations partielles 1X2/double chance dans `drc-prototype/xg-backtest.js` et évaluations OU/BTTS dans `drc-prototype/old/analyze_markets.js`.
**Nouveau chemin :** `handoff_worldcup_2026/recycled_code/markets/market_derivation.py`.
**Rôle :** agrège la matrice en 1X2, doubles chances, over/under, BTTS et top scores exacts.
**Entrée :** matrice `score -> probabilité`.
**Sortie :** dictionnaire de marchés.
**Dépendances :** générateur de top scores local.
**Réutilisabilité :** élevée.
**Adaptations :** couche minimale nouvelle demandée, normalisation défensive de l'entrée.
**Limites :** pas encore de handicaps asiatiques, marchés de mi-temps ou combinés arbitraires.

## Backtester

**Ancien chemin :** `drc-prototype/xg-backtest.js`, `drc-prototype/backtest.js`, `drc-prototype/optimizer.py`.
**Nouveau chemin :** `handoff_worldcup_2026/recycled_code/backtesting/backtester.py`.
**Rôle :** compare des signaux pré-match aux résultats finis et agrège le taux de réussite par marché.
**Entrées :** listes de prédictions sélectionnées et résultats canoniques.
**Sortie :** total testé/gagné, hit rate, résumé par marché, détail.
**Dépendances :** bibliothèque standard.
**Réutilisabilité :** moyenne.
**Adaptations :** suppression du HTML et des fichiers globaux, support générique de marchés.
**Limites :** pas de log loss/Brier score, cotes, ROI, persistance ou contrôle temporel automatique.

## Football Data Normalizers

**Ancien chemin :** `drc-prototype/audit_teams.py`, `drc-prototype/1_download.js`, `drc-prototype/update.js`, `drc-prototype/enrich-all-history.js`.
**Nouveau chemin :** `handoff_worldcup_2026/recycled_code/data_processing/normalizers.py`.
**Rôle :** normalise les noms d'équipes et convertit fixtures/résultats API-Football vers les contrats canoniques.
**Entrées :** nom ou objet brut fournisseur.
**Sortie :** nom comparable ou objet canonique.
**Dépendances :** bibliothèque standard.
**Réutilisabilité :** moyenne.
**Adaptations :** uniquement fonctions pures; réseau, clés et écritures retirés.
**Limites :** adaptateur spécifique au schéma API-Football; le mapping manuel historique de clubs européens n'est pas pertinent tel quel pour les sélections.
