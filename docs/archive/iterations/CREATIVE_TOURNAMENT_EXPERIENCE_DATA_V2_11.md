# Creative Tournament Experience Data V2.11

The V2.11 aggregate turns the existing V2.10 refresh outputs into a product-facing tournament narrative. It does not train a model, rerun Optuna, change active probabilities or promote the alternative projection.

## Current snapshot

- Projected tournament leader: `Spain`
- Leader confidence label: `stable`
- Simulations: `50,000`
- Official results locked: `3`
- Group storylines: `12`
- Most open groups: `B, K, G, I, C`
- Active leader: `Spain`
- Alternative non-active leader: `Spain`

## Product contract

The aggregate combines active and alternative projected campaigns, conditioned qualification probabilities, current standings, result-aware deltas, group volatility and dual-matrix evidence. `chaos_score` is a narrative ranking based on probability closeness, within-group density, active-versus-alternative movement and locked-result context.

The projected champion is a campaign proxy while the official knockout bracket is unavailable. It must not be labelled as a fully simulated World Cup champion. The alternative remains a comparative, less conservative scenario and never replaces the active forecast.
