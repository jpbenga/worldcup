# Road to the Trophy Simulation Credibility Audit V2.13.1B

## Verdict

`FAIL_CALIBRATION_REVIEW_REQUIRED`

The repository does execute two genuine blocks of 50,000 random draws. The conditioned group-stage simulator samples the 72 score matrices 50,000 times. The V2.13 knockout script then samples 50,000 knockout paths on one fixed projected bracket. Every published empirical probability is an exact multiple of `1/50,000`, which is strong evidence that counters were produced from those draws.

These are not 50,000 complete World Cups from group stage through the final. Complete paths are not persisted, and the knockout entrant bracket does not vary between simulations.

An independent in-memory rerun of the knockout loop produced exactly 50,000
champions and matched every published top-champion counter. This verifies the
knockout execution. The repository still lacks a run manifest containing input
hashes and persisted complete paths, so provenance is not yet audit-grade.

## France versus Switzerland

France has Elo 2063 and Switzerland Elo 1891. A standard Elo expected-score calculation gives France about 72.9% against Switzerland. The current knockout scenario instead gives Switzerland 51.3%.

The inversion is caused by the knockout strength formula:

```text
50% group qualification probability
25% group first-place probability
25% logistic Elo signal
```

Switzerland receives easier-group advantages from Group B, while France is penalized for facing Norway and Senegal in Group I. Group difficulty therefore overwhelms a 172-point Elo advantage even though group qualification probability is not a valid direct estimate of head-to-head knockout strength.

The issue is systemic: 10 of 31 projected knockout matches choose a lower-Elo team, including Mexico over Brazil and South Korea over Norway.

## Reproducibility

The group simulator uses a deterministic random seed, but previously created group tables from unsorted Python sets. Python set iteration can vary between processes, changing which team receives a seeded random tie-break draw. The construction is now sorted so future runs are reproducible across processes. Existing simulation artifacts predate this fix and must be regenerated before they can claim strict reproducibility.

## Required correction

The current knockout probabilities must be treated as uncalibrated scenario values. A credible replacement requires a dedicated neutral-site advancement model that directly combines validated team-strength signals and is backtested on historical knockout matches. Group difficulty may affect qualification and bracket placement, but must not directly become the probability of defeating an opponent.

Future simulation runs should persist complete end-to-end paths, input hashes, seed, run manifest, matchup counts, and calibration diagnostics.
