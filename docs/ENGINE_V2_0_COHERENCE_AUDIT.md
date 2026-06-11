# Engine V2.0 Coherence Audit

The audit checks whether the favorite selected by blended 1X2 probabilities agrees
with the outcome implied by the modal Poisson score. A clear favorite has a gap of at
least `0.08` over the second-highest 1X2 probability.

- Favorite-score alignment: `50.0%`
- Clear-favorite alignment: `59.5%`
- Favorite matches with modal 1-1: `47.0%`
- Test modal 1-1: `47.5%`

Clear-favorite alignment below `50%` is an automatic product-satisfaction failure,
regardless of log-loss improvement. Misaligned examples are retained in the JSON.
