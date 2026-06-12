# Creative Tournament Experience Release Notes V2.11

V2.11 upgrades `/simulation` from a primarily statistical group-simulation
view into a narrative tournament experience. It introduces a projected
tournament leader hero, a campaign-path explanation, combined active and
alternative contenders, group storylines, open-group rankings, locked-result
impact cards and a clearer active-versus-alternative comparison.

The experience is powered by
`creative_tournament_experience_v2_11.json`, a new product aggregate built
only from existing V2.6, V2.7, V2.9 and V2.10 outputs. It creates no new match
probabilities. The active `quant_hybrid_v2.2` engine remains unchanged, the
`score_matrix_candidate_v2.8` projection remains non-active, no model is
retrained and Optuna is not rerun.

The official knockout bracket is unavailable. The UI therefore uses
`Favori projeté`, `Projection de campagne` and `Proxy non officiel`. It does
not present the leader as a fully simulated champion and does not invent
knockout opponents or an official trophy path.

The existing group probability explorer remains available below the new story
blocks. Existing match cards, group views and match modals are not changed.
V2.11 is an additive product upgrade with explicit limitations and preserved
active forecasts.
