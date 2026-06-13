# xG Proxy Feasibility V2.1

API-Football exposes a provider `expected_goals` field on only
`2/12` sampled team-stat rows. This is real provider
xG evidence, but its `16.7%`
sample coverage is far too sparse to support V2.2.

- True provider xG available: `true` (sparse)
- True provider xG coverage sufficient: `false`
- Exploratory xG proxy possible: `true`
- Statistical coverage sufficient at scale: `false`
- Complete sample coverage: `6/6` (`100.0%`)
- Formula: `0.05 * shots_total + 0.18 * shots_on_goal + 0.03 * corners`

The exploratory proxy is fragile: its coefficients are heuristic, it omits shot location
and chance quality, and its source statistics are post-match. The six-match
sample does not establish large-scale coverage. It must never be described as
true xG or used for the same match. The JSON report records
competition/season scope, per-team exploratory values, bias risks and the V2.2
recommendation.
