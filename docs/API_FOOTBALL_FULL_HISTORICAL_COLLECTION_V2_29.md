# V2.29 — Respectful Full Historical API-Football Stats Collector

## Contexte

V2.27.1 a audité un échantillon quota-sûr. V2.28 a démontré la mécanique de features retardées, mais son candidat moteur utilisait un volume trop petit: `50` matchs source exploitables. Cette limite ne permet pas de conclure sur la valeur finale des statistiques API-Football.

V2.29 ajoute donc l'infrastructure de collecte complète, progressive et relançable. L'objectif n'est pas d'entraîner un moteur maintenant. L'objectif est de récupérer proprement toutes les données disponibles pour les `3 062` matchs historiques mappés entre 2014 et 2026.

## Périmètre

Endpoints ciblés:

- `fixtures/statistics`
- `fixtures/events`
- `fixtures/lineups`
- `fixtures/players`

Volume théorique:

- `3 062` fixtures historiques;
- `4` endpoints;
- `12 248` unités de travail;
- `11 968` unités restantes après reprise des `280` réponses déjà en cache historique V2.27/V2.27.1.

## Collecteur

Le script `backend/scripts/collect_api_football_historical_stats_full_v2_29.py` construit une file idempotente `fixture_id:endpoint`. Chaque unité est traitée séparément et le manifest est sauvegardé après chaque endpoint avec `--save-every 1`.

Options supportées:

- `--dry-run`
- `--use-cache`
- `--resume`
- `--max-live-calls`
- `--endpoints`
- `--competition`
- `--season`
- `--fixture-id`
- `--sleep-seconds`
- `--max-retries`
- `--timeout-seconds`
- `--save-every`
- `--stop-on-rate-limit`
- `--respect-retry-after`

Le cache brut est stocké hors commit dans:

`backend/data/cache/api_football/historical_stats/{fixture_id}/{endpoint}.json`

Une règle `.gitignore` dédiée empêche son ajout accidentel.

## Respect API

La stratégie par défaut privilégie la sécurité:

- concurrence `1`;
- cache-first;
- `1,5` seconde minimale entre appels live;
- budget maximal par run via `--max-live-calls`;
- arrêt propre quand le budget est atteint;
- lecture de `Retry-After` quand présent;
- backoff exponentiel avec jitter sur `429`, `5xx` et timeout;
- circuit breaker après `5` erreurs rate-limit/serveur consécutives;
- aucun secret dans les logs ou artefacts.

Les headers de rate limit sont capturés quand disponibles. Le mini-run V2.29 a détecté des headers `x-ratelimit-limit` et `x-ratelimit-remaining`, mais pas `Retry-After`.

## Tests exécutés

Dry-run complet:

- fixtures planifiées: `3 062`;
- unités planifiées: `12 248`;
- appels live: `0`;
- unités reprises depuis cache legacy: `280`.

Mini-run live contrôlé:

- plafond: `20` appels;
- résultat: `10` réponses non vides, `10` réponses vides;
- erreurs: `0`;
- rate-limit: `0`.

Reprise immédiate:

- plafond: `20` appels;
- le collecteur a continué sur les fixtures suivantes sans refaire les appels précédents;
- résultat cumulé: `280` cached, `20` fetched, `20` empty, `0` failed;
- unités restantes: `11 928`.

## Résumé actuel

Le résumé V2.29 lit le manifest et le cache, sans appel API. Après les tests:

- unités totales: `12 248`;
- unités complétées: `320`;
- unités restantes: `11 928`;
- fixtures avec au moins une donnée en cache: `79`;
- `ready_for_model_retest`: `false`.

Cette progression valide l'infrastructure, pas la couverture finale. Le modèle ne doit pas être retesté avant une collecte beaucoup plus large.

## Commande progressive recommandée

Commande à lancer seulement avec confirmation utilisateur:

```bash
python3 backend/scripts/collect_api_football_historical_stats_full_v2_29.py \
  --use-cache \
  --resume \
  --max-live-calls 1000 \
  --sleep-seconds 1.5 \
  --endpoints statistics,events,lineups,players
```

Elle doit être répétée sur plusieurs sessions/jours. Chaque run reprend exactement là où le précédent s'est arrêté.

## Limites

- V2.29 ne lance pas la collecte complète en une fois.
- V2.29 n'entraîne aucun moteur.
- Les prédictions actives, Road to the Trophy et Optuna restent inchangés.
- Le cache brut local n'est pas versionné.
- Les réponses vides sont conservées comme information utile: elles évitent de rappeler inutilement le même endpoint.
