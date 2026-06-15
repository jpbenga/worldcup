# V2.26 — Audit de cohérence matrice de score et simulation tournoi

## Contexte utilisateur

Cet audit répond à trois questions distinctes : l'effet réel du nul Espagne–Cap-Vert sur Road to the Trophy, la capacité de la matrice pré-match à représenter le 7-1 Allemagne–Curaçao, et la raison pour laquelle Road to the Trophy n'utilise pas la matrice visible dans la fiche match. Aucun moteur, pronostic actif ou composant frontend fonctionnel n'est modifié.

## Résumé exécutif

Le résultat Espagne 0-0 Cap-Vert est bien pris en compte : il est verrouillé dans les 50 000 tournois suivants. Il réduit la qualification espagnole de `98,52 %` à `94,76 %` et le titre de `18,688 %` à `18,028 %`. L'Espagne reste néanmoins la favorite et la championne du scénario central. Le moteur ne sait pas qu'elle a dominé : les données locales ne contiennent ni tirs, ni possession, ni xG pour ce match, et le résultat ne met pas à jour sa force future.

Le 7-1 allemand était présent dans la matrice avec une probabilité de `0,058 %`, mais hors des dix scores les plus probables. Le score recommandé `1-0` n'est donc pas contradictoire avec l'existence d'une queue de distribution. En revanche, l'expérience masque une information utile : la matrice donnait `14,73 %` à une victoire allemande par au moins trois buts et `9,65 %` à quatre buts allemands ou plus.

Road to the Trophy V4 n'utilise pas la matrice `quant_hybrid_v2.2`. Il construit une distribution séparée à partir de l'Elo externe et de profils de buts historiques pondérés. Cette séparation existe parce que le bundle actif `quant_hybrid_v2.2` n'est pas persisté comme contrat d'inférence réutilisable pour toutes les confrontations futures possibles. C'est une limite historique et d'architecture, pas une contrainte de performance.

## Réponse 1 — Espagne 0-0 Cap-Vert

### Impact mesuré

| Mesure | Avant verrouillage | Après verrouillage | Delta |
|---|---:|---:|---:|
| Espagne championne | 18,688 % | 18,028 % | -0,660 point |
| Espagne qualifiée | 98,520 % | 94,760 % | -3,760 points |
| Espagne première du groupe | 74,078 % | 57,018 % | -17,060 points |
| Cap-Vert qualifié | 30,310 % | 47,670 % | +17,360 points |
| Uruguay qualifié | 85,436 % | 84,336 % | -1,100 point |
| Arabie saoudite qualifiée | 36,354 % | 35,402 % | -0,952 point |

Le scénario central conserve l'Espagne première avec sept points et championne, mais son parcours change. Son premier adversaire projeté passe de la Bosnie-Herzégovine aux États-Unis et la finale projetée passe d'Espagne–Mexique à Espagne–Suisse. Le champion projeté reste stable.

Les probabilités avant/après d'atteindre la finale et la demi-finale ne sont pas récupérables depuis la timeline compacte V2.22 : ces marginales n'y sont pas persistées pour les états intermédiaires. Elles ne sont donc pas inventées dans cet audit.

### Score réel contre performance réelle

Le code V4 utilise des univers contrefactuels avec les mêmes flux aléatoires. Pour ce match, la seule différence intentionnelle est le remplacement du score simulé par le score officiel `0-0`. Les distributions des prochains matchs de l'Espagne continuent d'utiliser le même Elo courant et les mêmes profils historiques pondérés.

Le dépôt ne contient aucune statistique de tirs, possession, occasions ou xG pour Espagne–Cap-Vert. La domination espagnole n'est donc pas prise en compte. Le moteur sait que l'Espagne a fait nul ; il ne sait pas si ce nul résulte d'une mauvaise performance ou d'une forte domination sans réussite.

### Réponse claire

Le 0-0 pénalise réellement l'Espagne dans le groupe et légèrement dans la course au titre, sans suffire à lui retirer son statut de favorite. Road to the Trophy verrouille le résultat final mais ne réévalue pas la force future de l'Espagne et ne tient pas compte de sa domination.

## Réponse 2 — Allemagne 7-1 et gros scores

### Distribution pré-match

La matrice active Allemagne–Curaçao est une grille normalisée de `0-0` à `7-7`. Son score recommandé était `1-0` à `13,25 %`. Les probabilités ciblées étaient :

| Score | Probabilité |
|---|---:|
| 1-0 | 13,250 % |
| 2-0 | 11,423 % |
| 3-0 | 6,566 % |
| 4-0 | 2,830 % |
| 5-0 | 0,976 % |
| 6-0 | 0,281 % |
| 7-0 | 0,069 % |
| 7-1 | 0,058 % |

Le `7-1` était donc possible pour le modèle, mais caché hors top 10. La masse de victoire allemande par trois buts ou plus était `14,73 %`, par quatre buts ou plus `5,40 %`, et la probabilité que l'Allemagne marque au moins quatre buts `9,65 %`. L'Over 2,5 était à `47,29 %` et l'Over 3,5 à `25,64 %`.

### Troncature et sous-estimation

La grille est tronquée à sept buts par équipe puis renormalisée. Elle ne peut pas exposer séparément les scores à huit buts ou plus, et la masse omise n'est pas récupérable dans l'artefact publié. Par ailleurs, les xG prévus (`1,724` contre `0,842`) et l'écart de rating interne (`151`) décrivent un avantage réel mais modéré. Un seul 7-1 ne prouve pas une mauvaise calibration globale, mais il confirme le risque déjà identifié par l'audit V2.8 : les écarts extrêmes peuvent être compressés.

### Réponse claire

Le problème n'est pas que le modèle interdisait le gros score. Le problème principal est que le résumé par scores exacts les plus probables cachait une queue de large victoire significative. L'UI devrait afficher un signal « Risque de large victoire » et les masses agrégées 3+, 4+ et équipe à quatre buts ou plus, sans présenter `7-1` comme un score exact probable.

## Réponse 3 — Pourquoi Road to the Trophy n'utilise pas la matrice visible

### Modèles utilisés

| Couche | Modèle actuel |
|---|---|
| Prédiction match visible | `quant_hybrid_v2.2`, avec 1X2 hybride XGBoost/Poisson |
| Matrice visible | Projection Poisson active `0-7`, alimentée par les xG prédits |
| Simulation de groupe Road to the Trophy | Distribution Poisson séparée, Elo externe et profils de buts historiques pondérés |
| Simulation knockout | Même distribution directe, puis prolongation Poisson et tirs au but rétrécis vers 50/50 |
| Scénario central | Parcours complet représentatif choisi dans un réservoir uniforme des 50 000 tournois |

Les deux mondes partagent les identités, les fixtures, les scores officiels et une partie des données historiques. Ils ne partagent pas les matrices actives, les probabilités hybrides 1X2, les xG actifs ni les ratings internes actifs.

### Diagnostic de cohérence produit

Road to the Trophy doit pouvoir simuler n'importe quelle confrontation future. Or `quant_hybrid_v2.2` n'est pas disponible sous forme de bundle réutilisable pour une paire arbitraire. V4 a donc conservé le moteur tête-à-tête réutilisable de la lignée V3. Cette décision est techniquement compréhensible et explicitée dans les limitations, mais deux distributions différentes peuvent raconter deux histoires différentes pour le même match.

La plateforme est donc cohérente mécaniquement à l'intérieur de chaque couche, mais pas encore unifiée probabilistiquement entre la fiche match et le tournoi. Cette limite est acceptable à court terme si elle reste transparente. Elle ne constitue pas l'architecture cible.

### Réponse claire

La simulation n'utilise pas la matrice visible à cause d'une limite historique de persistance et de réutilisation du moteur actif, non à cause du coût des 50 000 simulations. Une distribution de match unifiée est nécessaire pour que prédiction match, matrice et Road to the Trophy reposent sur le même contrat probabiliste.

## Recommandations

1. Créer une **Unified Match Outcome Distribution** réutilisable pour toute paire d'équipes et tous les stades.
2. Réconcilier dans ce contrat le 1X2 hybride, la matrice de scores, les marchés agrégés et la queue de distribution.
3. Ajouter un signal « Risque de large victoire » avec victoire par 3+, victoire par 4+ et équipe à 4+ buts.
4. Continuer d'afficher le score recommandé et les top scores, mais ne plus les laisser résumer seuls le risque de score.
5. Séparer explicitement dans le produit l'impact du score réel de l'impact de la performance réelle.
6. Ajouter ultérieurement un module post-match seulement si des sources fiables de tirs, possession ou xG deviennent disponibles.

## Plan V2.27 éventuel

La priorité est haute, mais V2.27 doit commencer par un contrat et un benchmark, pas par une promotion directe. Il devra persister l'inférence arbitraire du meilleur modèle disponible, reconstruire une distribution cohérente avec ses probabilités 1X2, mesurer la calibration des queues de score, puis comparer Road to the Trophy actuel et un challenger unifié sur replay historique. Aucun patch par équipe ne doit être introduit.

## Limites restantes

- Les données de domination Espagne–Cap-Vert sont absentes.
- Les marginales finale/demi-finale avant le résultat ne sont pas persistées dans la timeline compacte.
- La matrice visible est normalisée sur une grille tronquée à sept buts.
- Le bracket officiel 2026 reste absent des données du projet.
- Les recommandations nécessitent des validations historiques avant toute modification du moteur public.
