# Road to the Trophy Scenario Timeline V2.22

## Contexte et diagnostic

Le panneau V2.21 décrivait l'impact agrégé des résultats réels, mais ne permettait pas de voir les itérations du scénario. V2.22 transforme cet impact en historique navigable d'un unique scénario SimuAI : avant les résultats, après chaque résultat réel, puis maintenant.

## Benchmark UX

| Pattern | Clarté | Complexité | Atlas | Mobile | Décision |
|---|---:|---:|---:|---:|---|
| Timeline scrubber | Forte | Faible | Excellente | Bonne avec scroll | Retenu |
| Stepper événementiel | Forte | Faible | Excellente | Bonne | Retenu dans le scrubber |
| Côte à côte | Moyenne | Forte | Risque de surcharge | Faible | Écarté par défaut |
| Overlay ghost paths | Forte | Forte | Bonne | Moyenne | Futur possible |
| Diff highlights | Forte | Moyenne | Excellente | Bonne | Retenu |
| Animated morph | Forte | Forte | Risque Angular/D3 | Moyenne | Limité aux transitions CSS |
| Small multiples | Moyenne | Forte | Surcharge | Faible | Écarté |
| Impact cards | Forte | Faible | Complémentaire | Bonne | Retenu dans l'inspecteur |
| Focus équipe avant/après | Forte | Moyenne | Excellente | Bonne | Retenu via focus existant |
| Focus groupe avant/après | Forte | Moyenne | Excellente | Bonne | Retenu via focus existant |
| Replay automatique | Moyenne | Moyenne | Risque de distraction | Faible | Non retenu maintenant |

## Choix technologique

Les options étudiées sont Angular Signals et CSS/SVG existants, D3 transitions, GSAP Flip, Angular CDK et une architecture backend de diff robuste sans dépendance.

Le choix actuel combine :

- backend Python pour produire les états et diffs déterministes ;
- Angular Signals pour sélectionner l'état et le côté avant/après ;
- D3 déjà présent uniquement pour préserver zoom et pan ;
- CSS pour les accents, transitions et responsive.

Aucune dépendance n'est ajoutée. GSAP Flip serait utile pour des déplacements DOM complexes, mais les nodes de l'Atlas gardent des positions stables. Angular CDK apporterait surtout overlays et accessibilité, sans résoudre le besoin central. Le diff backend réduit le risque et garde l'expérience explicable.

## Modèle de données

La timeline contient une baseline, un état après chacun des cinq résultats réels et l'état public actuel. Chaque état embarque champion, finale, groupes, bracket et parcours d'équipe. Chaque transition contient résultat déclencheur, groupes modifiés, variations de qualification, matchs du bracket modifiés, parcours modifiés, finale, champion et score d'importance.

Les simulations progressives utilisent le même seed et les mêmes flux aléatoires par tournoi. Le dernier état est toujours le scénario V4 public canonique.

## Règles UX

- Un seul scénario public : l'état actuel SimuAI.
- La timeline montre son histoire, jamais plusieurs moteurs concurrents.
- Le mode avant/après remplace l'état dans le même Atlas ; il n'affiche pas deux Atlas surchargés.
- Les groupes et matchs modifiés reçoivent un accent doré ; les équipes dont les probabilités évoluent reçoivent un accent ciblé.
- Le panneau latéral explique la transition sélectionnée.
- Sur mobile, le scrubber devient horizontalement défilable.

## Validation et limites

La timeline contient six états et cinq diffs. Le champion Espagne reste stable, tandis que groupes, probabilités et certains chemins évoluent. Le build et les tests Angular passent. Les prédictions actives, `quant_hybrid_v2.2`, le moteur public et Optuna restent inchangés.

La génération progressive est volontairement coûteuse pendant un refresh forcé, car elle rejoue les états avec des flux communs. Les anciens chemins en overlay fantôme et le replay automatique restent des pistes futures, non nécessaires pour une première expérience claire.
