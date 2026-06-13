# Dual Matrix Release Notes V2.9

V2.9 adds a complete comparison layer between the official active prediction
matrix and the less-conservative V2.8 candidate. It publishes 72 per-match
comparisons, a 50,000-scenario conditioned candidate group simulation, an
active-versus-candidate simulation report, an alternative projected-campaign
proxy and an automated validation artifact.

The existing match cards, active score matrices, hybrid 1X2 probabilities and
active tournament simulation are not replaced. No model is retrained and
Optuna is not rerun. The candidate remains non-active because its historical
trade-off includes lower strict exact-score accuracy despite better
distribution-level metrics.

In the match modal, users can expand **Projection alternative V2.8 · Non
active** to compare active and alternative modal scores and top-3 lists. On
`/simulation`, the active view remains the default and a toggle exposes the
alternative simulation and campaign proxy. The impact block summarizes the
largest qualification changes.

The candidate simulation is comparative rather than official. Finished
official results are locked, but qualification deltas still contain Monte
Carlo variation. The Projected Campaign output remains a proxy because no
trustworthy official knockout bracket contract is available.
