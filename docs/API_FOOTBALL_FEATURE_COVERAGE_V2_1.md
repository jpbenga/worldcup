# API-Football Feature Coverage V2.1

## Scope

V2.1 inspected the cached API-Football `/leagues` inventory for
`14` explicitly allowlisted senior-international competitions and
`64` competition-season records. No API request was needed,
so request count is `0`.

Provider metadata claims that finished-fixture statistics, events and lineups
exist for many major competitions and qualifiers. Standings are competition
dependent; odds coverage is sparse and remains benchmark-only. These metadata
flags are not treated as proof of row-level availability.

## Available Features

`{'fixtures': True, 'statistics': True, 'events': True, 'lineups': True, 'standings': True, 'odds': True}`

## Safety And Limitations

All checked competitions are World/international entries from an explicit
allowlist; club competitions are excluded. Future World Cup 2026 fixtures are
not acquired by this discovery step. The next script probes row-level
statistics, events and lineups on a bounded sample of completed matches.
