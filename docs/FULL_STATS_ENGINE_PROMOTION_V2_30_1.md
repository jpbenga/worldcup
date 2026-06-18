# V2.30.1 — Promote Full Stats Engine for Match Predictions

## Contexte

V2.30 a validé le candidat `stats_enriched_full_v2_30` après consommation de la collecte complète API-Football. La règle produit est appliquée : le moteur enrichi, qui utilise le plus de données, devient la cible de production sauf blocage sérieux.

La promotion V2.30.1 concerne uniquement les prédictions pré-match individuelles. Road to the Trophy et le moteur tournoi ne sont pas modifiés.

## Décision source

La décision V2.30 utilisée comme garde-fou est `recommend_promotion`, avec `0` blocage. L'audit fuite est `PASS`, les prédictions actives étaient encore inchangées avant promotion, et le candidat améliore les métriques test.

## Promotion effectuée

Ancien moteur : `quant_hybrid_v2.2`.

Nouveau moteur actif : `stats_enriched_full_v2_30`.

Les fichiers remplacés sont :

- `backend/data/generated/predictions.json` ;
- `backend/data/snapshots/predictions.json` ;
- `frontend/src/assets/data/predictions.json`.

Le label public reste `SimuAI`. Le manifest technique actif est publié dans `active_prediction_engine_manifest.json`.

## Archives et rollback

Les anciens fichiers actifs sont archivés dans :

- `backend/data/archives/v2_30_1_pre_full_stats_promotion/predictions.generated.json` ;
- `backend/data/archives/v2_30_1_pre_full_stats_promotion/predictions.snapshot.json` ;
- `backend/data/archives/v2_30_1_pre_full_stats_promotion/predictions.frontend.json`.

Le rollback est préparé par `backend/scripts/rollback_full_stats_engine_v2_30_1.py`. Il restaure les trois fichiers archivés et écrit un manifest de rollback. Il n'est pas exécuté dans V2.30.1.

## Métriques

| Moteur | Accuracy test | Log loss test | Brier test |
|---|---:|---:|---:|
| `quant_hybrid_v2.2` | 60,217 % | 0,881184 | 0,515803 |
| `stats_enriched_full_v2_30` | 60,652 % | 0,864783 | 0,506084 |

Gains mesurés :

- log loss : `-0,016401` ;
- Brier : `-0,009719` ;
- accuracy : `+0,004348`.

## Audit diff

L'audit diff V2.30.1 passe :

- mêmes fixtures : `true` ;
- nombre de matchs avant : `72` ;
- nombre de matchs promus : `72` ;
- schéma compatible : `true` ;
- changement moyen 1N2 : `0,029409` ;
- changement max 1N2 : `0,088274`.

Les trois matchs les plus modifiés sont Nouvelle-Zélande–Belgique, Uruguay–Espagne et Belgique–Égypte. Les changements restent cohérents avec une promotion de moteur, pas avec un patch par équipe.

## Validation

La validation V2.30.1 est `PASS` :

- décision V2.30 vérifiée ;
- prédictions actives archivées ;
- prédictions backend et frontend promues ;
- manifest de promotion créé ;
- rollback disponible ;
- schéma compatible ;
- Road to Trophy non modifié par la promotion ;
- Optuna non relancé ;
- cache brut API non commité ;
- aucun secret littéral exposé.

Angular build passe. Angular tests passent : `3` fichiers, `5` tests.

## Road to the Trophy

Road to the Trophy reste inchangé par V2.30.1. Des diffs Road to Trophy existent déjà dans le worktree local hors scope, mais la promotion V2.30.1 ne les indexe pas et ne modifie pas le moteur tournoi.

## Limites restantes

- Road to the Trophy ne consomme pas encore le moteur full stats.
- Une V2.31 reste nécessaire pour une `Unified Match Outcome Distribution` arbitraire.
- Le gros artefact de features V2.30 reste déjà présent dans l'historique et GitHub signale sa taille.
