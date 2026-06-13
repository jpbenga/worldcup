# Matchday and Status Normalization V2.7

V2.7 normalizes each fixture round into `Group Stage - Matchday 1`, `Group
Stage - Matchday 2` or `Group Stage - Matchday 3`. The same `matchday_label`
is consumed by cards and the existing modal.

Status comes from the official-results layer and uses only `finished`, `live`,
`not_started`, `postponed`, `cancelled` or `unknown`. A finished fixture must
have an official score and final evaluation. A live fixture can show its
current score but cannot receive final evaluation. An unplayed fixture remains
prediction-only.

This normalization deliberately does not rewrite the older normalized fixture
snapshot. It is a frontend view layer that keeps the historical source and
current official status separate.
