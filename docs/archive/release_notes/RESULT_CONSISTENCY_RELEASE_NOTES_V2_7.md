# Result Consistency Release Notes V2.7

V2.7 propagates official result state through the existing group cards, match
modal, live standings and simulation experience. Cards and modal now consume
the same unified match-state artifact instead of independently joining
prediction, result and evaluation files.

Live group standings are calculated only from finished official scores.
Matchday and status labels are normalized. The modal distinguishes modal score,
active 1X2 trend and the most probable score compatible with that trend, with
a short explanation when they differ.

The existing group-based UI and modal remain intact. No model was retrained,
Optuna was not rerun and no frozen pre-match probability was changed.
