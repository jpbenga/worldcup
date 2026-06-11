# Active Engine Deployment V2.0

Decision: `do_not_deploy`.

The fixed model improves validation strongly but regresses against V0.9 on the final
test by `+0.0101` log loss and `+0.0090` Brier. Its train-to-validation log-loss gap
is `0.2122`, which triggers the explicit overfit guard. DNB at confidence `0.60`
reaches `78.0%` wins excluding pushes and `85.5%` non-loss including pushes at
`62.6%` coverage; it does not exceed the proposed 90% benchmark.

The deployment decision is automatic but conservative: every gate must pass. The
active World Cup 2026 prediction files are replaced and archived only after clear
historical gains, reduced 1-1 concentration, acceptable favorite-score coherence,
useful secondary markets, no leakage, no obvious overfit, and adequate operational
input freshness/team coverage.

Failed gates:
- `modal_1_1_strongly_reduced`
- `no_obvious_overfit`
- `active_input_freshness_and_team_coverage`

Active history staleness is
`696` days and 2026
fixture-team historical coverage is
`97.9%`. When the
decision is `do_not_deploy`, existing active predictions are intentionally untouched.
