# Prediction History, Transparency & Model Scoreboard Release Notes V2.12

V2.12 adds an append-only public memory for all 72 World Cup predictions. Each
history entry preserves the frozen active pre-match forecast and attaches
actual results and evaluation labels only after a match is finished. Pending
matches explicitly remain unevaluated.

The new model scoreboard reports exact score, Top-3, Top-5, 1X2, favorite,
Draw No Bet and secondary-market outcomes. Draw No Bet wins, losses and pushes
are separate. Counts accompany rates, and a prominent warning appears while
fewer than ten matches are evaluated.

A chronological performance timeline groups evidence by date, matchday and
group. The dedicated `/transparence` route presents the scoreboard through
cards, a timeline, notable partial hits, visible misses, an expandable match
history and a plain-language glossary. Finished-match modals include a discreet
link to this public record.

The alternative projection remains a non-active comparison. V2.12 does not
change active predictions, retrain the model, rerun Optuna, invent results or
hide failures.
