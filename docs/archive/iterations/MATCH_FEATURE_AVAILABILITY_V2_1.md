# Match Feature Availability V2.1

V2.1 probed `6` recent completed matches across distinct competitions,
using at most `18` API calls. Statistics were available for
`6/6` matches, events for
`6/6`, and lineups for
`6/6`. Venue names were present for
`5/6`, while a reliable neutral flag
was unavailable.

These payloads are explicitly post-match-only. They may support future lagged
team aggregates, but using a match's own shots, events or lineup outcomes to
predict that same match would be temporal leakage. Odds were not fetched or
used as a feature. Sparse or unavailable fields remain documented rather than
invented.
