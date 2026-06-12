# Dual Matrix Display Strategy V2.9

V2.9 integrates the accepted V2.8 candidate as a comparative product layer,
not as a promotion. The candidate improves score likelihood, top-3, top-5,
broad-market Brier and favorite-margin realism, but lowers strict exact-score
accuracy. That trade-off is useful evidence, not permission to silently
replace the active forecast.

The active prediction remains the official pre-match forecast. The candidate
matrix is displayed only as an alternative scenario for comparison and
simulation realism analysis.

The product therefore uses two explicit labels: **Prédiction active** for the
frozen `quant_hybrid_v2.2` forecast and **Projection alternative · Non active**
for the less-conservative candidate. Active content remains the default.
Alternative content is secondary, repliable in the match modal and selectable
on the simulation page. Cards are unchanged.

The match comparison explains modal-score, top-score, expected-goal and market
changes without saying that an alternative score is now official. The
simulation comparison measures whether altered score margins materially move
qualification and group-rank probabilities. Projected Campaign remains a
clearly labelled proxy because the official knockout bracket is unavailable.

This is a roadmap-level product and simulation experiment rather than a small
UI patch: it connects a historically evaluated modelling challenger to
transparent match-level and tournament-level consequences while preserving
the accepted active engine.
