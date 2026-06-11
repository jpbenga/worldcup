# Historical Data Strategy

## Goal

Build a trustworthy chronological dataset for a future historically calibrated
international-football prediction engine. This document is a blueprint only:
V0.6 does not fetch history, train a model or alter current predictions.

## Available sources and assets

| Asset | Current value | Limitation for training |
|---|---|---|
| API-Football | Active fixtures, teams, standings, rounds and raw response structure. World Cup 2022 is reported available. | Current normalized set contains future 2026 fixtures, not a historical training corpus. |
| Elo Ratings | 244 normalized ratings and validated mapping for all 48 World Cup teams. | Current ratings are snapshots, not guaranteed pre-match historical ratings. |
| World Cup 2026 fixtures | 72 real future fixtures with stable IDs and dates. | Must never be used as labeled training data before results exist. |
| Teams and standings | Identity, logos, groups and current tournament structure. | Standings before the tournament contain no performance signal. |
| Raw API-Football responses | Auditable provider payloads and endpoint evidence. | Coverage, quotas and historical statistics availability require a dedicated spike. |

## Required historical record

The minimum canonical `historical_matches.json` record should contain:

- stable provider fixture ID and internal match ID;
- home and away team IDs plus names as-of the match;
- kickoff date and chronological ordering;
- competition, season, stage and competition importance;
- finished status and regulation-time home/away goals;
- neutral-site indicator and venue/country context;
- pre-match Elo or the closest valid rating strictly before kickoff;
- source provenance and retrieval timestamp.

Useful optional features, only when consistently available, include shots,
shots on target, possession and provider xG. Sparse advanced statistics must
not silently change the training population or leak post-match information.

## Competition coverage

A useful first dataset should combine:

1. Previous World Cups.
2. World Cup qualification campaigns.
3. Continental championships and their qualifiers.
4. International friendlies, with lower importance weighting.
5. Other finished senior international fixtures with reliable identity mapping.

Competition type, match importance and neutral venue must remain explicit.
Club data and club-calibrated parameters are not directly transferable to
national teams.

## API-Football acquisition strategy

V0.7 should first discover provider coverage and quota cost, then:

1. Enumerate target `league_id` and `season` pairs.
2. Fetch finished fixtures per league/season.
3. Fetch previous World Cup seasons where available.
4. Fetch World Cup qualifiers and friendlies where available.
5. Save immutable raw payloads under a clearly versioned historical raw path.
6. Normalize to `historical_matches.json` without altering active 2026 fixtures.
7. Validate duplicates, team mappings, dates, statuses, scores and neutral-site fields.
8. Join only pre-match Elo values or reconstruct Elo chronologically from results.

The fetcher must use the local ignored `.env`, respect quota limits, save no
secret and produce a machine-readable acquisition summary.

## Chronology and leakage controls

- Split train, validation and test sets by date, never randomly across time.
- Compute every rolling feature from matches strictly before the predicted match.
- Store `features_as_of` and assert it is earlier than kickoff.
- Tune parameters only on train/validation periods.
- Reserve the most recent completed period for out-of-sample evaluation.
- Never train on future World Cup 2026 fixtures.
- Never use final standings, post-match statistics or current Elo as if they
  were pre-match features.

An expanding-window evaluation is preferred:

```text
train through T1 -> validate on T1..T2
train through T2 -> validate on T2..T3
...
final untouched test period
```

## Quality gates

Before model calibration, the historical dataset must pass:

- finished matches only, with valid regulation-time scores;
- unique provider fixture IDs and stable team identities;
- documented coverage by year and competition;
- explicit missingness rates for every optional feature;
- verified chronology and no post-kickoff feature timestamps;
- reproducible raw-to-normalized transformation;
- manual sample review across competitions and eras.

## Storage and versioning

Recommended future artifacts:

```text
backend/data/raw/api_football/historical/<league>/<season>/
backend/data/normalized/historical_matches.json
backend/data/generated/historical_dataset_report.json
docs/HISTORICAL_DATA_ACQUISITION_REPORT.md
```

Dataset versions should record source endpoints, acquisition dates, filters,
normalizer version, row counts and a content checksum. Raw payloads remain
separate from model-ready features.

## Recommended next phase

Proceed with **V0.7 — Historical Data Acquisition Spike**. Its purpose is to
measure API-Football historical coverage, quota cost, identity quality and
chronological feature feasibility before implementing any calibrated model.

## V0.7 result

The controlled exploration used `5` API requests and checked one season from
each of five international competition families: World Cup, and European,
African, Asian and CONCACAF World Cup qualification. These checked seasons
contained `872` finished fixtures in total. The cached league inventory also
confirms available seasons for friendlies, continental championships, Gold Cup
and UEFA Nations League, but those fixtures were not downloaded in V0.7.

The conservative fetch then used `3` requests and downloaded the complete
API-Football fixture sets for World Cup `2014`, `2018` and `2022`:

- `64` fixtures per season;
- `192` finished fixtures normalized;
- `47` teams;
- date range from `2014-06-12` through `2022-12-18`;
- no 2026 fixture, future fixture, missing score or duplicate fixture ID.

The dataset is real and suitable as the first experimental input for a
controlled baseline-calibration exercise. It is not sufficient for the final
engine because it covers only three World Cups, lacks qualifiers/friendlies and
pre-match Elo history, and retains `AET/PEN` fixtures whose regulation-time
score semantics must be defined before fitting.

Recommended next phase: **V0.8 — Historical Dataset Split & Baseline
Calibration Experiment**, beginning with an explicit chronological split and
score-semantics decision before any model promotion.

## V0.8 result

V0.8 preserves `historical_matches.json` and publishes the separate
`historical_matches_expanded.json` dataset. The conservative expanded fetch
adds Euro Championship, Copa America, Africa Cup of Nations, Asian Cup and
CONCACAF Gold Cup seasons to the three World Cups.

- `1,311` real finished matches;
- `168` teams;
- `6` named senior international competitions;
- seasons from `2014` through `2024`;
- `268` rows explicitly identified as continental qualifications;
- no future 2026 fixture and no club competition.

This is substantially better than V0.7 because it covers multiple
confederations and a decade of tournament cycles. It remains experimental:
API-Football can group qualification and final-tournament scope under the same
league/season, leaving `243` rows tagged `mixed_scope_possible`; AET/PEN score
semantics, pre-match Elo and neutral-site validation also remain unresolved.

The deterministic chronological split is `917` train, `196` validation and
`198` test matches. Recommended next phase: **V0.9 — First Calibration
Experiment on Historical Dataset**, with no promotion to the active engine.

## V0.9 result

The first calibration experiment fits a smoothed team-strength Poisson model
on the train split only. It uses no future 2026 fixtures, Elo, post-match
features or active prediction snapshots. The fixed model is evaluated on the
`196` validation and `198` test matches.

Compared with the neutral `1.35 / 1.35` prototype, the calibrated experiment
improves validation and test 1X2 accuracy, log loss and Brier score. Exact-score
performance is mixed: validation is unchanged and test is slightly worse.
Because the dataset remains medium-sufficiency and unresolved AET/PEN,
neutral-site and mixed-scope issues remain, the model stays experimental and
is not promoted.
