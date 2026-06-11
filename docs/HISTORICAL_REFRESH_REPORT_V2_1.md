# Historical Refresh Report V2.1

V2.1 combined the existing `1311`-match dataset with completed,
allowlisted senior-international fixtures from a bounded recent-season plan.
The refreshed dataset contains `3062` matches, adding
`1751` unique fixtures.

- Date range before: `2014-06-12T20:00:00+00:00` to `2024-07-15T00:30:00+00:00`
- Date range after: `2014-06-12T20:00:00+00:00` to `2026-03-31T18:45:00+00:00`
- Latest-history age: `71` days
- API requests: `11`
- Non-senior friendlies excluded: `429`
- Added competitions: `['Friendlies', 'UEFA Nations League', 'World Cup - Qualification Africa', 'World Cup - Qualification Asia', 'World Cup - Qualification CONCACAF', 'World Cup - Qualification Europe', 'World Cup - Qualification Oceania', 'World Cup - Qualification South America']`
- Added teams: `58`

Only completed fixtures with integer scores enter the normalized output.
Club league IDs and future World Cup 2026 fixtures are excluded. Qualification
seasons labelled 2026 contribute only already-finished matches. Failures, cache
usage, duplicate counts and quota impact remain explicit in the JSON report.
