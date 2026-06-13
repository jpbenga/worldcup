# World Cup 2026 Score Matrix Candidate V2.8

This candidate applies `A_gap_alpha_1.5_beta_0.75` to the 72 World Cup score matrices after it passed the historical-test guardrails. It is not active, does not replace `predictions.json`, and preserves every frozen hybrid 1X2 probability.

Spain vs Cape Verde Islands changes from modal `1-0` to `2-0`. The complete JSON retains old and new top scores, matrix-derived markets, the active 1X2 block and a per-match explanation.

Old modal distribution: `{'1-0': 34, '1-1': 21, '0-1': 10, '0-0': 6, '2-0': 1}`.

New modal distribution: `{'1-0': 27, '1-1': 21, '0-1': 10, '2-0': 8, '0-0': 6}`.

The candidate exists for human validation and simulation review only. Promotion requires an explicit later decision; V2.8 does not silently alter the product's active prediction contract.
