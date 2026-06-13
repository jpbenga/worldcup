# Active Matrix Market Audit V2.3

V2.3 audits the active V2.2 score matrix without retraining, Optuna, new data or active-prediction changes. Matrix-derived, XGBoost-direct and active-hybrid sources are kept separate.

The matrix is useful beyond exact score: exact score is `14.6%`, while top-5 is `51.3%` and several broad secondary markets are reliable at meaningful coverage. The strongest eligible matrix market at confidence 0.60 is `over_0_5` at `91.7%` accuracy and `100.0%` coverage.

DNB reaches `87.6%` wins excluding pushes and `90.1%` non-loss including pushes at `70.2%` coverage. It exceeds 90% only under the non-loss-including-pushes definition at this threshold; that is not a 90% win rate.

Recommended for UI: broad, high-coverage markets such as over 0.5, selected DNB with its push definition, double chance and selected team-goal/over 1.5 markets. Hide or warn on low-coverage winning margins, exact draw scores, BTTS yes and over 2.5 until their calibration and coverage improve.

## Direct answers

- The matrix is genuinely useful beyond exact score, especially for broad markets; it is not uniformly strong across every derivative.
- Reliable display candidates: over 0.5, double chance 1X/12, DNB with explicit push treatment, home/away over 0.5 and over 1.5 with confidence filtering.
- Weak or unstable candidates: BTTS yes, clean sheets, exact draw scores, winning margins and high-total lines with sparse selections.
- The strongest percentages on over 2.5 and winning margins do not justify promotion because their coverage is small.
- DNB exceeds 90% at confidence 0.60 only as non-loss including pushes. Its win rate excluding pushes is 87.6%.
