# Upstream xG Feature Availability V1.3

## Scope

This read-only inspection measures whether the current historical dataset can
support future upstream xG challengers. It does not train a model, select a
parameter, evaluate a challenger, or modify World Cup 2026 predictions.

## Dataset coverage

- Total historical matches: `1311`
- Historical teams: `168`
- Competitions: `6`
- Competition tiers: `{'major_tournament': 1043, 'qualification': 268}`
- Competition families: `{'continental_championship': 851, 'continental_qualification': 268, 'world_championship': 192}`
- Seasons: `{'2020': 313, '2019': 306, '2023': 134, '2021': 111, '2016': 83, '2024': 83, '2014': 64, '2018': 64, '2022': 64, '2017': 57, '2015': 32}`

| Competition | Matches |
|---|---:|
| Euro Championship | 415 |
| Africa Cup of Nations | 334 |
| World Cup | 192 |
| Asian Cup | 134 |
| Copa America | 118 |
| CONCACAF Gold Cup | 118 |

| Split | Matches | Date min | Date max |
|---|---:|---|---|
| Train | 917 | 2014-06-12T20:00:00+00:00 | 2021-06-23T21:00:00+00:00 |
| Validation | 196 | 2021-06-24T00:00:00+00:00 | 2023-07-03T01:00:00+00:00 |
| Test | 198 | 2023-07-03T01:00:00+00:00 | 2024-07-15T00:30:00+00:00 |

## Low-sample and recent coverage

- Teams below 5 matches: `17`
- Teams below 8 matches: `39`
- Teams below 10 matches: `59`
- Recent window: `24` months before
  `2024-07-15T00:30:00+00:00`
- Teams with no match in that recent window: `70`
- Teams below 5 recent matches: `122`

The full team lists and counts are retained in the JSON artifact.

## Elo and identity availability

- Elo ratings rows: `244`
- Elo retrieval timestamps: `['2026-06-10T10:40:17Z']`
- Historical teams with an exact Elo-name match: `156`
- Historical teams covered by exact Elo name or identity mapping: `162`
- Historical teams without Elo coverage: `6`
- Identity-map rows: `48`
- Historical teams without an identity-map entry: `121`

## Temporal leakage risks

- team_ratings.json contains current/static Elo snapshots, not ratings known before each historical kickoff.
- The Elo snapshot was retrieved after every historical split; using it directly would leak future information.
- team_identity_map.json covers only a subset of historical teams and cannot by itself create historical Elo provenance.
- Time decay must calculate age relative to each predicted match and must never include later matches.

## Recommendations for V1.4

- Implement competition weighting and time decay first because their required fields already exist with historical dates.
- Evaluate low-sample fallback independently and report results for sparse teams versus adequately sampled teams.
- Use Elo in V1.4 only with reconstructed or sourced pre-match ratings; otherwise label it a limited leakage-risk experiment.
- Select every parameter on validation only, reserve test for final evaluation, and keep the combined candidate deferred.

## Decision

Competition, date and low-sample signals are available for isolated V1.4
experiments. Elo is current/static rather than historical pre-match evidence,
so an Elo-prior challenger must remain limited or wait for temporally aligned
ratings. Promotion remains `do_not_promote_yet`.
