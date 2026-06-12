# Live Results Overlay Release Notes V2.6

V2.6 adds a separate official-results overlay, post-match scoring, a
result-conditioned group simulation and a creative Projected Campaign proxy.
The existing group cards, match modal and `/simulation` route are enriched
without being replaced.

Finished cards can show the official score and a concise evaluation label.
The modal can compare frozen prediction and actual result. The simulation locks
finished scores, keeps live fixtures unfrozen, highlights qualification
movement and labels the campaign proxy honestly.

No model was retrained, Optuna was not rerun and no pre-match probability was
modified.
