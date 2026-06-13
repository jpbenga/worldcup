# Data Signal Upgrade Recommendation V2.1

## Decision

`proceed_to_v2_2_limited_retrain`

V2.1 materially improves result-history freshness and breadth, but advanced
feature coverage is proven only on a bounded six-match sample. A future V2.2
may retrain a conservative result-history model using the refreshed
chronological splits. It should not yet depend on statistics, events, lineups
or the exploratory xG proxy at full scale.

## Freshness And Breadth

The historical dataset grows from `1,311` to `3,062` unique completed senior
international fixtures, adding `1,751` matches after excluding `429`
non-senior friendlies. Its final date moves from July
15, 2024 to March 31, 2026, reducing staleness from 696 days in V2.0 to 71
days. Eight competition families/names absent from the old normalized dataset
are added, principally World Cup qualifications, UEFA Nations League and
senior friendlies. The explicit international league-ID allowlist excludes
clubs, while team-name safeguards remove youth, women's and Olympic friendlies
mixed into the provider's global Friendlies league.

## Advanced Feature Evidence

Cached provider metadata describes statistics, events and lineups across many
competition-seasons. The bounded live probe returned all three payload types
for `6/6` completed matches, with venue names also present. This establishes
technical availability, not whole-dataset completeness. A reliable neutral
flag was not found. Standings are competition-dependent and are not inherently
pre-match features. Odds remain excluded because V2.1 did not establish
timestamped pre-match provenance.

## xG And Proxy

API-Football exposes provider `expected_goals` on only `2/12` sampled team-stat
rows. True provider xG is therefore available sparsely, not at coverage
sufficient for V2.2. An exploratory proxy using total shots, shots on goal and
corners is technically constructible for the six sampled matches, but the
coefficients are heuristic and the statistics are post-match. The sample is
too small to claim broad coverage or use the proxy directly in V2.2.

## V2.2 Feature Recommendation

Use:

- refreshed chronological results and internal ratings;
- competition family/tier with explicit friendlies and qualification tags;
- lagged goals, rest days, sample depth and venue name/country when reliably
  normalized;
- only lagged advanced-stat aggregates after a broader coverage audit.

Exclude for now:

- provider xG until broad coverage is proven;
- same-match statistics, events or lineups;
- the exploratory xG proxy as a primary signal;
- standings without timestamp-safe pre-match reconstruction;
- odds without proven pre-match timestamps;
- inferred neutral flags without reliable source evidence.

## Remaining Risks

The refreshed dataset changes competition composition substantially and
contains many friendlies and qualification matches. A future retrain must
segment them and compare against simple baselines. Advanced-stat coverage must
be measured across a much larger stratified sample. Team identity aliases,
regulation-time semantics for AET/PEN, and neutral-site quality also remain
unresolved. V2.1 authorizes only a limited, carefully benchmarked V2.2 retrain,
not active deployment.
