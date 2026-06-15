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
# Road to the Trophy V2.21.1

- [ ] Les 12 cartes groupe affichent quatre équipes, un classement et leurs matchs.
- [ ] Aucune carte vide ne masque l'Atlas.
- [ ] La finale, le champion projeté et le panneau latéral sont renseignés.
- [ ] Le focus groupe, équipe et match fonctionne.
- [ ] Zoom `+`, zoom `-`, déplacement et Reset fonctionnent.
- [ ] Les filtres groupe, tour et statut fonctionnent.
- [ ] Le panneau « impact des résultats réels » s'ouvre sans casser l'Atlas.
- [ ] Un contrat invalide affiche un état compact et ne rend pas de grande carte vide.

## Scenario Timeline V2.22

- [ ] La timeline affiche Avant, chaque résultat réel et Maintenant.
- [ ] Précédent, Suivant et Maintenant changent bien l'état affiché.
- [ ] Avant ce résultat / Après ce résultat fait évoluer visuellement l'Atlas.
- [ ] Groupes, équipes et matchs modifiés sont surlignés.
- [ ] Le panneau latéral explique les changements et les équipes impactées.
- [ ] Focus groupe, focus équipe, zoom, pan et Reset restent fonctionnels.
- [ ] Sur mobile, la timeline défile horizontalement sans masquer l'Atlas.

## SVG Atlas & Odds Value Experience V2.23

- [ ] Les chemins sélectionnés et modifiés sont immédiatement distinguables.
- [ ] La comparaison avant/après affiche un ancien chemin en ghost path.
- [ ] Zoom, pan, focus groupe, équipe et match restent fonctionnels.
- [ ] Le mode reduced motion désactive les transitions fortes.
- [ ] Une cote intéressante apparaît uniquement sur un match disposant d'un signal robuste.
- [ ] Le détail affiche SimuAI, marché, edge, source et disclaimer.
- [ ] Un match sans signal affiche un état sobre sans badge promotionnel.
- [ ] L'application reste utilisable si les cotes sont indisponibles.

## SVG & Odds UX Clarification V2.23.1

- [ ] Aucune flèche SVG ni contour doré inexpliqué n'est visible.
- [ ] La légende distingue clairement sélection, modification et ancien parcours.
- [ ] Survoler une courbe révèle un parcours d'équipe.
- [ ] Cliquer une courbe sélectionne l'équipe et renseigne l'inspecteur.
- [ ] Reset désélectionne le parcours sans casser le zoom/pan.
- [ ] La modal affiche le bookmaker unique et toutes les cotes utiles disponibles.
- [ ] « Cote intéressante » apparaît comme badge sans masquer les autres issues.
- [ ] Les états sans signal et sans cotes sont explicites.

## V1 French Localization & Product Polish V2.24

- [ ] L’accueil, la fiche match et Road to the Trophy sont entièrement compréhensibles en français.
- [ ] Les 48 noms de sélections sont traduits sans confusion ni débordement.
- [ ] Les marchés, issues et cotes utilisent des libellés et décimales français.
- [ ] Aucun accès public à Transparence, au mode labo ou aux comparaisons historiques ne subsiste.
- [ ] Les cinq scores les plus probables sont présentés sans promesse de matrice complète.
- [ ] Road to the Trophy est immédiatement identifiable comme l’expérience tournoi principale.
- [ ] Les noms longs restent lisibles sur ordinateur et mobile.

## Match Matrix & Tournament Simulation Coherence Audit V2.26

- [ ] Les trois réponses distinguent clairement faits mesurés, limites et recommandations.
- [ ] Le 0-0 Espagne–Cap-Vert est présenté comme un score verrouillé sans prétendre mesurer la domination.
- [ ] Le 7-1 Allemagne–Curaçao est visible comme scénario de queue, sans être présenté comme score probable.
- [ ] Le risque de large victoire est expliqué par une masse agrégée, pas par un score exact isolé.
- [ ] La séparation entre `quant_hybrid_v2.2` et Road to the Trophy V4 est compréhensible.
- [ ] Aucun moteur, pronostic actif ou choix manuel par équipe n'a été modifié.
