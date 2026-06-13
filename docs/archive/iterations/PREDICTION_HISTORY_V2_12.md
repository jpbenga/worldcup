# Prediction History V2.12

V2.12 publishes an append-only history for all `72` World Cup fixtures. It contains `3` finished matches, `3` evaluated predictions and `69` pending predictions.

Every entry keeps the active `quant_hybrid_v2.2` pre-match score matrix summary, probabilities, favorite and markets separate from the actual-result and post-match evaluation layers. A result can be appended after full time, but the pre-match forecast is never recomputed or rewritten. Matches without a final result keep `evaluation.available=false`.

The alternative `score_matrix_candidate_v2.8` projection is included only as a clearly labelled, non-active comparison. It does not replace the active forecast. Public summaries expose exact hits, partial hits and misses instead of hiding poor outcomes.

A prediction history never rewrites pre-match forecasts. It appends actual outcomes and evaluation labels after the match is known.
