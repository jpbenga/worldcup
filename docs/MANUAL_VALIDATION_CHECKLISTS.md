# Manual Validation Checklists

Ces checklists couvrent les contrôles encore utiles au produit. Les anciennes checklists d’itération sont conservées dans `docs/archive/`.

## Matchday Refresh

- [ ] La commande unique V2.18 détecte correctement si un refresh est nécessaire.
- [ ] Le dry-run V2.18 ne modifie aucun fichier.
- [ ] Transparence et Road to the Trophy sont reconstruits après un nouveau résultat.
- [ ] Le refresh termine sans erreur.
- [ ] Les résultats réels et statuts sont cohérents avec la source.
- [ ] Les matchs terminés sont verrouillés.
- [ ] Les snapshots et assets frontend correspondent.
- [ ] Les limites ou échecs de récupération sont documentés.

## Road to the Trophy

- [ ] Un seul scénario SimuAI est visible.
- [ ] SimuAI Tournament Engine V3 est la source officielle.
- [ ] Groupes, équipes, matchs et tours sont explorables.
- [ ] Zoom, pan, filtres et détails fonctionnent.
- [ ] Le parcours affiché est cohérent de bout en bout.
- [ ] Les explications de favoris et d’upsets sont compréhensibles.

### Cohérence V2.19

- [ ] Le classement du scénario central est séparé des chances sur 50 000 simulations.
- [ ] Les scores, points, classement, qualifiés, bracket et parcours sont cohérents.
- [ ] Le cas Belgique paraît central et ses probabilités restent visibles.
- [ ] Aucun choix manuel par équipe n’est introduit.

## Simulation

- [ ] 50 000 tournois complets sont déclarés.
- [ ] Les résultats réels joués sont verrouillés.
- [ ] Les groupes et qualifiés peuvent varier.
- [ ] Le knockout utilise le modèle tête-à-tête.
- [ ] Le mapping non officiel est clairement signalé.

## Match et modal

- [ ] Score réel, live ou prono est immédiatement identifiable.
- [ ] Les probabilités et libellés sont cohérents.
- [ ] Les états mobile et desktop restent lisibles.
- [ ] Aucun jargon technique inutile ne domine le parcours.

## Sécurité et avant push

- [ ] `operator_doctor_v2_17.py` ne signale aucun blocage.
- [ ] `preflight_v2_17.py` passe.
- [ ] Le statut de fraîcheur correspond au dernier manifest disponible.
- [ ] Build et tests passent.
- [ ] Les prédictions actives n’ont pas changé involontairement.
- [ ] Aucun secret, `.env`, build ou dépendance n’est indexé.
- [ ] Les changements hors scope restent non indexés.
- [ ] `git diff --cached --check` passe.
- [ ] La décision humaine est consignée dans `docs/VALIDATION_LOG.md`.
