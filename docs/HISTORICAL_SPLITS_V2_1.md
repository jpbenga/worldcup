# Historical Splits V2.1

V2.1 creates a deterministic chronological `70/15/15` split without model
training, randomization or parameter selection.

- Train: `2143` matches, `2014-06-12T20:00:00+00:00` to `2024-11-19T19:45:00+00:00`
- Validation: `459` matches, `2024-11-19T19:45:00+00:00` to `2025-09-06T11:45:00+00:00`
- Test: `460` matches, `2025-09-06T13:00:00+00:00` to `2026-03-31T18:45:00+00:00`
- Test freshness: `71` days

The previous split contained `1311` matches and ended
at `2024-07-15T00:30:00+00:00`. The refreshed split contains
`3062` matches and ends at `2026-03-31T18:45:00+00:00`. Competition
and team composition per split, exact date boundaries and leakage checks are
retained in the JSON report.
