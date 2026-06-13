# Historical Data Refresh Plan V2.1

## Objective

V2.0 built the required quant infrastructure but its historical signal ends on
July 15, 2024. The model overfit validation and regressed on final test, while
the active 2026 deployment assessment found a 696-day historical-data gap.
V2.1 is therefore data-only: it refreshes finished senior-international
results, measures advanced-feature availability, and prepares leakage-safe
chronological splits without training XGBoost or running Optuna.

> The V2.1 objective is not to make the model more complex, but to determine whether stronger and fresher pre-match signals exist.

## Acquisition Scope

The refresh targets recent missing seasons for UEFA Nations League,
international friendlies, World Cup qualifications in Europe, Africa, Asia,
CONCACAF, Oceania and South America, plus recent AFCON and Gold Cup seasons.
Existing World Cup, Euro, Copa America, AFCON, Asian Cup and Gold Cup history is
retained. Club competitions are excluded by an explicit league-ID allowlist.

API-Football endpoints:

- `/fixtures?league=<id>&season=<year>` for bounded recent-history refresh;
- `/fixtures/statistics?fixture=<id>` for post-match statistics availability;
- `/fixtures/events?fixture=<id>` for event availability;
- `/fixtures/lineups?fixture=<id>` for lineup availability;
- cached `/leagues` coverage metadata for seasons, standings and odds claims.

## Quota And Cache Policy

Existing raw responses are reused. Fixture refresh is limited to an explicit
recent-season plan, and feature probing uses only a small representative sample
of finished matches. Every response is cached under
`backend/data/raw/api_football/v2_1/`; scripts record request counts and produce
clean failure reports when API access or quota is unavailable.

## Temporal Safety

Only fixtures with `FT`, `AET` or `PEN` status and complete scores enter the
refreshed dataset. Future fixtures, all future World Cup 2026 fixtures, club
matches, duplicates and missing-score rows are excluded. Qualification seasons
labelled 2026 may contribute only matches already completed before execution.

Statistics, events and lineups are post-match evidence in V2.1. They are
audited for coverage and may support future lagged or aggregate pre-match
features, but they must never be attached to the prediction row of the same
match. Odds remain a separate benchmark unless timestamped pre-match
provenance is established.

## Feature Decision Rule

A candidate V2.2 feature must have explicit provenance, stable semantics,
adequate cross-competition coverage, a defensible pre-match transformation,
and no dependence on information learned after kickoff. Sparse or inconsistent
signals are documented and excluded rather than imputed into a misleading
feature.
