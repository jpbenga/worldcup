# Prediction History, Transparency & Model Scoreboard Strategy V2.12

## Why prediction history matters

A prediction engine becomes accountable only when its forecasts remain visible
after the result is known. V2.12 creates a durable memory for every World Cup
fixture: the frozen pre-match forecast, the actual result, the post-match
evaluation and a concise public explanation. Good outcomes, partial hits and
misses all remain visible.

A prediction history never rewrites pre-match forecasts. It appends actual outcomes and evaluation labels after the match is known.

Pre-match predictions and real results remain separate layers. The forecast
records what the engine knew before kickoff. The result layer records what
happened. The evaluation layer compares them without changing either source.
This prevents hindsight edits and makes every metric auditable.

## Public scoreboard

A public scoreboard turns individual evaluations into an understandable
summary. It reports exact score, Top-3, Top-5, 1X2, favorite, Draw No Bet and
secondary-market performance. Draw No Bet always separates wins, losses and
pushes; a push is neither silently counted as a win nor a loss.

The scoreboard remains descriptive when the sample is small. Fewer than ten
evaluated matches triggers a prominent warning because one result can move
rates sharply. The product shows counts beside rates, preserves misses and
avoids claims of stable model quality before enough evidence exists.

## Active and alternative projections

The active `quant_hybrid_v2.2` forecast remains the reference history. The
alternative `score_matrix_candidate_v2.8` projection is compared on the same
finished matches only as a non-active scenario. It can illuminate whether a
less conservative matrix changes score coverage, but it is never promoted or
used to rewrite the active record.

## Readable transparency

Metrics use plain-language explanations. Top-3 and Top-5 describe whether the
real score appeared in a ranked pre-match list. Coverage describes how many
selections could be evaluated. Sample size describes how many finished matches
support a rate. Cards, badges, short timeline entries and expandable match
details keep the page readable without turning transparency into a spreadsheet.

V2.12 uses a dedicated `/transparence` route. It begins with sample context and
the high-level scoreboard, then reveals markets, chronology, notable hits,
misses and the full evaluated-match history through progressive disclosure.
