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
