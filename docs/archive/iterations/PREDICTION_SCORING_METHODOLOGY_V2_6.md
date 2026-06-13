# Prediction Scoring Methodology V2.6

V2.6 evaluates only fixtures marked finished with a known official score.
Frozen pre-match score matrices and active hybrid 1X2 probabilities are read,
never rewritten.

Per match, the evaluator records exact-score, Top-3, Top-5 and 1X2 hits. DNB
selects the higher home/away DNB probability and reports win, loss or push.
Totals, BTTS, team-goal and clean-sheet statements are scored according to
whether the published probability was at least 50 percent and whether the
event occurred.

The product summary prefers specific factual language over a single vanity
score. Fewer than 20 finished matches sets `sample_size_too_small: true`, so
no strong aggregate claim is made.
