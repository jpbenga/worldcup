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
