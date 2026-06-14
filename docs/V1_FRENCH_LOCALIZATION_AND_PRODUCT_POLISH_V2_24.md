# V1 French Localization & Product Polish V2.24

## Objectif

Cette itération finalise l’expérience publique V1 en français sans modifier les prédictions actives, le moteur quantitatif, Optuna ni le moteur Road to the Trophy.

## Changements livrés

- Couche de localisation centralisée pour les 48 sélections, leurs alias et leurs formes compactes.
- Traduction des noms d’équipes sur les groupes, rencontres, classements, cotes et l’ensemble de Road to the Trophy.
- Traduction des marchés et issues de cotes, avec affichage décimal français.
- Locale Angular `fr-FR` activée pour les dates et nombres.
- Protection des noms longs dans les cartes et modales compactes.
- Suppression de la route et de la page publiques Transparence, du mode labo et des comparaisons historiques publiques.
- Suppression de la promesse trompeuse « Matrice complète » ; les cinq scores les plus probables restent clairement présentés.
- Road to the Trophy mis en avant comme expérience tournoi principale dans la navigation.

## Choix d’architecture

Les données sources et identifiants techniques restent inchangés. La traduction est appliquée à la frontière frontend, dans `I18nService` et les adaptateurs d’affichage. Cette séparation protège les calculs, les correspondances de matchs et les artefacts de simulation.

## Validation

- Audit automatisé : `backend/scripts/audit_frontend_french_localization_v2_24.py`
- Validation produit : `backend/scripts/validate_v1_french_product_polish_v2_24.py`
- Build Angular et tests unitaires obligatoires.
- Vérification visuelle manuelle de l’accueil, de la fiche match et de Road to the Trophy.
- Prédictions actives, moteur public et Optuna protégés par contrôle Git ciblé.

## Commande canonique de lancement avec actualisation

```bash
python3 backend/scripts/start_local_app_v2_18.py --force-refresh --fetch --fetch-odds --simulations 50000
```
