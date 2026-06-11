# Manual Validation Checklists

## Objectif

Les tests automatisés vérifient des contrats et des comportements connus, mais
ils ne remplacent pas le regard humain sur la cohérence des données, la
lisibilité de l'interface et la compréhension de la provenance.

Utiliser cette checklist à la fin de chaque étape fonctionnelle, avant de
considérer une version comme prête pour la suivante. La personne qui valide
doit comparer l'interface aux fichiers JSON publiés et noter toute anomalie
dans `docs/VALIDATION_LOG.md`.

## Commandes de préparation

```bash
cd "/Users/chloe/Desktop/dossier sans titre/worldcup"
python3 backend/scripts/build_snapshots.py

cd frontend
nvm use
npm install
npm start
```

URL locale :

```text
http://localhost:4200
```

Pour vérifier aussi le build et les tests avant la revue visuelle :

```bash
cd "/Users/chloe/Desktop/dossier sans titre/worldcup/frontend"
nvm use
npm run build
npm test -- --watch=false
```

## Méthode de validation

1. Exécuter les commandes de préparation sans ignorer les erreurs.
2. Vérifier les snapshots backend et leurs copies dans les assets Angular.
3. Ouvrir la page d'accueil Angular sur desktop puis en largeur mobile.
4. Comparer les valeurs visibles aux fichiers JSON.
5. Contrôler les requêtes réseau et la console du navigateur.
6. Noter les anomalies, leur impact et les étapes pour les reproduire.
7. Choisir une décision dans `docs/VALIDATION_LOG.md`.

Pour chaque anomalie, noter au minimum :

```text
Date :
Version / commit :
Page ou fichier :
Étapes de reproduction :
Résultat observé :
Résultat attendu :
Impact :
Décision avant prochaine phase :
```

## Pages et fichiers à vérifier

Page Angular :

```text
http://localhost:4200
```

Fichiers JSON principaux :

```text
backend/data/mock/sample_matches.json
backend/data/normalized/matches.json
backend/data/generated/predictions.json
backend/data/evaluated/backtest_results.json
backend/data/snapshots/matches.json
backend/data/snapshots/predictions.json
backend/data/snapshots/backtest_results.json
backend/data/snapshots/data_sources.json
frontend/src/assets/data/
```

## Règle de validation

Une étape ne peut être considérée comme validée que si :

* [ ] le pipeline backend passe ;
* [ ] les snapshots JSON sont générés ;
* [ ] Angular démarre ;
* [ ] les données affichées correspondent aux JSON ;
* [ ] la provenance des données est visible ;
* [ ] aucune donnée mock n'est présentée comme réelle ;
* [ ] aucune erreur console critique n'est visible ;
* [ ] les anomalies sont notées.

## Checklist générale avant validation d'une version

### Préparation technique

* [ ] le commit ou la version à valider est identifié ;
* [ ] le worktree ne contient pas de changement inattendu ;
* [ ] le pipeline de génération passe ;
* [ ] le build frontend passe ;
* [ ] les tests automatisés passent ou leurs erreurs sont documentées ;
* [ ] aucun secret ou artefact interdit n'est versionné.

### Revue humaine

* [ ] les données sources sont identifiées ;
* [ ] les données affichées sont cohérentes avec les snapshots ;
* [ ] les limites et données de démonstration sont explicites ;
* [ ] les parcours principaux sont utilisables ;
* [ ] les états vides, chargements et erreurs ne montrent rien d'ambigu ;
* [ ] la console et le réseau navigateur ne présentent aucune erreur critique ;
* [ ] le rendu desktop et mobile est lisible.

### Décision

* [ ] les anomalies bloquantes sont corrigées ;
* [ ] les réserves acceptées sont consignées ;
* [ ] la décision humaine est inscrite dans `docs/VALIDATION_LOG.md`.

## Checklist V0.2 — Data Foundation

### Backend / fichiers

* [ ] `backend/data/mock/sample_matches.json` existe.
* [ ] `backend/data/normalized/matches.json` existe.
* [ ] `backend/data/generated/predictions.json` existe.
* [ ] `backend/data/evaluated/backtest_results.json` existe.
* [ ] `backend/data/snapshots/matches.json` existe.
* [ ] `backend/data/snapshots/predictions.json` existe.
* [ ] `backend/data/snapshots/backtest_results.json` existe.
* [ ] `backend/data/snapshots/data_sources.json` existe.
* [ ] les fichiers dans `frontend/src/assets/data/` correspondent aux snapshots backend.

### Provenance

* [ ] `data_sources.json` indique clairement que les données actuelles sont mock.
* [ ] `is_real_data` est `false` pour les données sample.
* [ ] les prédictions sont marquées comme générées.
* [ ] les backtests sont marqués comme évalués/démonstratifs.
* [ ] aucune donnée mock n'est appelée “réelle”.

### Interface Angular

* [ ] la page d'accueil s'affiche.
* [ ] la section “État des données” est visible.
* [ ] le badge “Données démo” ou équivalent est visible.
* [ ] les cartes de match affichent une provenance compréhensible.
* [ ] les prédictions affichent les probabilités principales.
* [ ] la matrice de scores est lisible.
* [ ] les marchés sont lisibles.
* [ ] l'historique affiche les validations ET les échecs.
* [ ] le message responsable est visible.
* [ ] l'interface reste lisible sur desktop.
* [ ] l'interface reste lisible sur mobile ou largeur réduite.

### Cohérence des données affichées

* [ ] le nombre de matchs affichés correspond à `matches.json`.
* [ ] le nombre de prédictions affichées correspond à `predictions.json`.
* [ ] les `match_id` affichés existent dans les fichiers JSON.
* [ ] les top scores affichés correspondent à ceux de `predictions.json`.
* [ ] les probabilités sont affichées en pourcentages lisibles.
* [ ] les probabilités 1X2 semblent cohérentes.
* [ ] les badges validé / non validé correspondent à `backtest_results.json`.
* [ ] aucune donnée vide ou `undefined` n'est visible dans l'interface.

### Console navigateur

* [ ] aucune erreur critique dans la console.
* [ ] aucun 404 sur les fichiers JSON.
* [ ] les assets JSON chargent en HTTP 200.

### Décision V0.2

- [ ] Validé
- [ ] Validé avec réserves
- [ ] Non validé

Notes :

```text
À compléter par la personne qui effectue la validation.
```

## Checklist V0.3 — Real Data Acquisition Spike

### Sécurité et acquisition

- [ ] `.env` existe localement mais n'est pas suivi par Git.
- [ ] `.env.example` existe et ne contient pas de vraie clé.
- [ ] API-Football ping fonctionne ou l'erreur est documentée.
- [ ] les endpoints testés sont listés.
- [ ] les réponses brutes sont sauvegardées sans secret.
- [ ] la structure des objets API-Football est documentée.
- [ ] World Cup 2026 disponible ou non est clairement indiqué.
- [ ] Elo Ratings est testé.
- [ ] parsing Elo possible ou non est documenté.
- [ ] `DATA_SOURCE_DECISIONS.md` contient une décision claire.
- [ ] Angular affiche l'état des sources réelles.
- [ ] aucun secret n'est visible dans l'interface.
- [ ] aucun secret n'est commité.

### Revue humaine

- [ ] les résultats du rapport correspondent aux fichiers raw.
- [ ] les mappings expérimentaux sont cohérents avec les objets sources.
- [ ] la section “Sources réelles explorées” est lisible.
- [ ] les limites du plan et du parsing Elo sont comprises.
- [ ] la décision de passer à l'intégration réelle est consignée.

## Checklist V0.3.1 — Team Identity Mapping

### Génération et cohérence

- [ ] `team_identity_map.json` existe.
- [ ] `unmapped_teams.json` existe.
- [ ] `team_mapping_report.json` existe.
- [ ] `build_team_identity_map.py` termine sans erreur.
- [ ] `validate_team_mappings.py` retourne `PASS` ou un statut expliqué.
- [ ] la couverture API-Football vers Elo est affichée.
- [ ] tous les mappings `needs_review` sont listés.
- [ ] les `48` équipes API-Football sont présentes dans le rapport.
- [ ] chaque équipe mappée possède un identifiant API, un nom Elo et un code pays.
- [ ] aucun identifiant API, `team_id` ou nom Elo n'est dupliqué.
- [ ] les six alias explicites documentés sont corrects.
- [ ] aucune correspondance floue n'est auto-validée.
- [ ] les éléments ambigus restent `needs_review` ou `unmapped`.
- [ ] les alias USA/United States sont vérifiés.
- [ ] les alias Korea Republic/South Korea sont vérifiés.
- [ ] les alias Congo DR/DR Congo sont vérifiés.
- [ ] les alias Côte d'Ivoire/Ivory Coast sont vérifiés.
- [ ] les alias Türkiye/Turkey sont vérifiés.
- [ ] la décision humaine est notée dans `docs/VALIDATION_LOG.md`.

### Interface et sécurité

- [ ] l'encart “API-Football ↔ Elo Ratings” affiche les bons compteurs.
- [ ] l'absence du snapshot de statut ne bloque pas l'interface.
- [ ] le frontend indique qu'Elo n'est pas connecté au moteur de prédiction.
- [ ] aucune probabilité n'a changé à cause du mapping.
- [ ] aucun secret ni fichier `.env` n'est suivi par Git.

### Décision V0.3.1

- [ ] Validé
- [ ] Validé avec réserves
- [ ] Non validé

Notes :

```text
À compléter par la personne qui effectue la validation humaine.
```

## Checklist V0.4 — Elo Model Experiment

- [ ] Le mapping équipe est validé.
- [ ] Le modèle baseline existe toujours.
- [ ] Le modèle Elo génère un fichier séparé.
- [ ] `predictions_baseline.json` existe.
- [ ] `predictions_elo.json` existe.
- [ ] `model_comparison.json` existe.
- [ ] Les deltas sont lisibles.
- [ ] Aucun impact extrême non expliqué.
- [ ] Les matchs sans Elo fallback correctement.
- [ ] Angular affiche clairement que le modèle Elo est expérimental.
- [ ] Les probabilités restent dans `[0, 1]`.
- [ ] Les marchés 1X2 restent normalisés.
- [ ] La décision humaine est notée dans `VALIDATION_LOG.md`.

### Décision V0.4

- [ ] Validé
- [ ] Validé avec réserves
- [ ] Non validé

Notes :

```text
À compléter par la personne qui effectue la validation humaine.
```

## Checklist V0.5.1 — Real Data Only + UX Review

### Source et snapshots

- [ ] la commande sans `--source` active API-Football.
- [ ] l'absence des données API-Football provoque une erreur claire, sans fallback mock.
- [ ] le mode mock fonctionne uniquement avec `--source mock`.
- [ ] `teams.json`, `worldcup_groups.json`, `group_strengths.json` et `prediction_diversity_audit.json` existent.
- [ ] les 12 groupes A à L contiennent chacun 4 équipes et 6 matchs.
- [ ] le classement annexe des meilleurs troisièmes n'écrase aucun groupe.
- [ ] les logos d'équipes disponibles sont affichés.
- [ ] aucune fixture mock n'est présentée dans le parcours principal.

### Audit du moteur

- [ ] l'avertissement d'uniformité des prédictions est visible.
- [ ] le taux de score modal `1-1` correspond à l'audit JSON.
- [ ] la modale distingue clairement baseline et variation Elo.
- [ ] aucune diversité artificielle n'a été introduite.
- [ ] le caractère expérimental et non calibré reste visible.
- [ ] aucun faux backtesting n'est présenté pour les fixtures futures.

### Revue UX humaine

- [ ] les onglets de groupes sont utilisables sur desktop.
- [ ] les onglets de groupes sont utilisables en largeur mobile.
- [ ] les équipes, forces de groupe et classements sont lisibles.
- [ ] les états vides des classements sont explicites.
- [ ] chaque carte de match ouvre la bonne modale.
- [ ] la modale se ferme par le bouton, le fond et la touche Échap.
- [ ] les matrices et marchés de la modale correspondent aux snapshots.
- [ ] aucune erreur critique ni aucun 404 n'apparaît dans le navigateur.

### Décision V0.5.1

- [ ] Validé
- [ ] Validé avec réserves
- [ ] Non validé

Notes :

```text
À compléter exclusivement après la revue visuelle humaine.
```

## Checklist V0.6 — Prediction Engine Discovery & Blueprint

- [ ] Current engine audit completed
- [ ] Engine reference inventory completed
- [ ] Historical dependencies reviewed
- [ ] Historical data strategy documented
- [ ] Future engine blueprint created
- [ ] ADR created
- [ ] No prediction logic changed
- [ ] No snapshots regenerated unnecessarily
- [ ] No secret committed
- [ ] Next implementation phase identified

## Checklist V0.7 — Historical Data Acquisition Spike

- [ ] API-Football historical exploration completed
- [ ] Historical fixtures fetched
- [ ] Historical matches normalized
- [ ] Historical matches are real data
- [ ] Future 2026 fixtures are not mixed into historical dataset
- [ ] Scores are present for all historical matches
- [ ] Dataset audit completed
- [ ] Dataset limitations documented
- [ ] No model training introduced
- [ ] No prediction logic changed
- [ ] No fake backtesting introduced
- [ ] No secret committed

## Checklist V0.8 — Expanded Historical Dataset & Chronological Split

- [ ] Competitions beyond World Cup explored
- [ ] Euro checked
- [ ] Copa América checked
- [ ] Africa Cup of Nations checked
- [ ] AFC Asian Cup checked
- [ ] CONCACAF Gold Cup checked
- [ ] Qualifiers/friendlies clearly tagged if included
- [ ] Expanded historical matches normalized
- [ ] 2026 future fixtures excluded
- [ ] Club competitions excluded
- [ ] Scores present for all matches
- [ ] Dataset audit completed
- [ ] Chronological split created
- [ ] No random split used
- [ ] No model training introduced
- [ ] No prediction logic changed
- [ ] Dataset limitations documented
- [ ] No secret committed

## Checklist V0.9 — First Calibration Experiment

- [ ] Historical train/validation/test splits loaded
- [ ] Calibrated model trained on train split only
- [ ] Validation predictions generated
- [ ] Test predictions generated
- [ ] 1X2 metrics calculated
- [ ] Exact score metrics calculated
- [ ] Prototype comparison generated
- [ ] No 2026 predictions modified
- [ ] Current app engine not replaced
- [ ] Results documented honestly
- [ ] Promotion recommendation explicit
- [ ] No fake backtesting introduced
- [ ] No secret committed

## Checklist V1.0 — Calibration Error Analysis & Segmentation

- [ ] Validation/test predictions loaded
- [ ] Competition segmentation completed
- [ ] Season segmentation completed
- [ ] Team segmentation completed
- [ ] Draw bias analyzed
- [ ] Favorite bias analyzed
- [ ] Confidence buckets analyzed
- [ ] Score distribution analyzed
- [ ] Worst matches identified
- [ ] Recommendations generated from observed results
- [ ] No model retrained
- [ ] No 2026 predictions modified
- [ ] No promotion decision changed
- [ ] No secret committed

## Checklist V1.1 — Improved Calibrated Engine Challenger Design

- [ ] V1.0 human validation recorded
- [ ] Challenger design document created
- [ ] Evaluation protocol created
- [ ] Draw-calibrated challenger specified
- [ ] Dixon-Coles rho challenger specified
- [ ] Competition-weighted challenger specified
- [ ] Time-decay challenger specified
- [ ] Elo-prior challenger specified
- [ ] Combined challenger deferred until isolated tests
- [ ] Promotion rules defined
- [ ] No model implemented
- [ ] No model retrained
- [ ] No 2026 predictions modified
- [ ] No promotion decision changed
- [ ] No secret committed

## Checklist V1.2 — Isolated Calibration Challenger Experiments

- [ ] Draw-calibrated challenger implemented
- [ ] Dixon-Coles rho challenger implemented
- [ ] Parameters selected on validation only
- [ ] Test used only for final evaluation
- [ ] V0.9 comparison generated
- [ ] Guardrails evaluated
- [ ] No combined challenger implemented
- [ ] No model promoted
- [ ] No 2026 predictions modified
- [ ] No main engine replacement
- [ ] Results documented honestly
- [ ] No secret committed

## Checklist V1.3 — Upstream xG Feature Challenger Design

- [ ] V1.2 result incorporated
- [ ] Upstream xG challenger design created
- [ ] Competition-weighted xG specified
- [ ] Time-decay xG specified
- [ ] Elo-prior xG specified
- [ ] Low-sample fallback specified
- [ ] Combined upstream challenger deferred
- [ ] V1.4 experiment protocol created
- [ ] Feature availability inspected
- [ ] Temporal leakage risks documented
- [ ] No model implemented
- [ ] No model retrained
- [ ] No 2026 predictions modified
- [ ] No promotion decision changed
- [ ] No secret committed

## Checklist V1.4 — Upstream xG Isolated Challenger Experiments

- [ ] Competition-weighted xG implemented
- [ ] Time-decay xG implemented
- [ ] Low-sample fallback xG implemented
- [ ] Elo-prior handled with temporal leakage restriction
- [ ] Parameters selected on validation only
- [ ] Test used only for final evaluation
- [ ] V0.9 comparison generated
- [ ] Segment reports generated
- [ ] Guardrails evaluated
- [ ] No combined challenger implemented
- [ ] No model promoted
- [ ] No 2026 predictions modified
- [ ] No main engine replacement
- [ ] Results documented honestly
- [ ] No secret committed

## Checklist V2.0 — Quant Hybrid Engine with Active Deployment

- [ ] Prompt analysis completed
- [ ] XGBoost dependency added
- [ ] Optuna dependency added
- [ ] Dependency imports validated
- [ ] Internal chronological rating implemented
- [ ] Feature builder uses pre-match data only
- [ ] XGBoost 1X2 model implemented
- [ ] XGBoost secondary market models implemented
- [ ] Optuna optimization implemented
- [ ] Optuna optimizes validation only
- [ ] Test evaluated only once after selection
- [ ] Historical replay implemented
- [ ] Predict -> observe -> update confirmed
- [ ] Monte Carlo simulation implemented with 1500 simulations per match
- [ ] Secondary market evaluation implemented
- [ ] DNB metrics distinguish wins, losses and pushes
- [ ] Score exact evaluated realistically
- [ ] Favorite-score alignment audited
- [ ] 1-1 concentration audited
- [ ] No external static Elo used as primary signal
- [ ] Deployment decision documented
- [ ] Active engine replaced if and only if model established
- [ ] Previous active predictions archived if deployed
- [ ] 2026 predictions regenerated if deployed
- [ ] No secret committed

## Checklist V2.1 — Historical Data Refresh & Feature Coverage Upgrade

- [ ] V2.0 human validation recorded with strong reservations
- [ ] API-Football coverage discovered
- [ ] Recent international history refreshed
- [ ] Finished matches only
- [ ] Club matches excluded
- [ ] Future World Cup 2026 fixtures excluded
- [ ] Match statistics availability audited
- [ ] Events availability audited
- [ ] Lineups availability audited
- [ ] Venue/neutrality availability audited
- [ ] xG or xG-proxy feasibility audited
- [ ] Chronological refreshed splits created
- [ ] Temporal leakage audit passed
- [ ] No model retrained
- [ ] No Optuna rerun
- [ ] No 2026 active predictions modified
- [ ] No secret committed

## Checklist V0.5 — API-Football Active Source with Prototype Engine

- [ ] fetch API-Football réussi.
- [ ] fixtures brutes sauvegardées.
- [ ] teams brutes sauvegardées.
- [ ] fixtures normalisées.
- [ ] teams normalisées.
- [ ] `matches.json` contient les fixtures API-Football.
- [ ] Angular affiche Source active : API-Football.
- [ ] Angular affiche Données réelles : oui.
- [ ] Angular affiche Fixtures futures : oui.
- [ ] Angular affiche moteur prototype non calibré.
- [ ] backtesting non disponible pour futures fixtures.
- [ ] baseline predictions générées.
- [ ] Elo predictions générées.
- [ ] model comparison générée.
- [ ] aucune donnée mock n'est présentée comme active.
- [ ] aucune probabilité aberrante visible.
- [ ] aucun secret n'est commité.

### Décision V0.5

- [ ] Validé
- [ ] Validé avec réserves
- [ ] Non validé

Notes :

```text
À compléter par la personne qui effectue la validation humaine.
```
