# Score Matrix Realism Strategy V2.8

V2.8 treats score-matrix realism as a distinct modelling objective. It does
not assume that the active `quant_hybrid_v2.2` engine is fully satisfactory
because its 1X2 and broad-market results are good.

Le 1X2 additionne de nombreuses cases de la matrice, alors que le score modal
ne correspond qu’à une seule case. Un moteur peut donc être bien calibré en
1X2 tout en étant trop prudent dans la distribution des scores.

A modal score can repeatedly become 0-0, 1-0, 0-1 or 1-1 when expected-goal
lambdas remain near one, favorite and outsider lambdas are compressed, draw
mass is high, or the Poisson projection is optimized indirectly for aggregate
outcomes rather than score likelihood. This damages product credibility:
users see a strong favorite but an apparently timid score, and tournament
simulation then inherits narrow margins, low goal totals and unrealistic
tiebreak distributions.

The correct response is measurement before correction. V2.8 audits lambdas,
modal scores, total-goal mass, strong-favorite buckets and realized historical
margins. The 460-match frozen historical test is the arbiter; the 72 World Cup
fixtures are descriptive and cannot select a challenger.

Post-model challengers are deliberately bounded. They test favorite lambda-gap
scaling, margin redistribution, total-goals temperature and draw-mass
correction without retraining XGBoost. Promotion requires score-likelihood and
realism improvement while preserving 1X2, DNB, over/under, top-3 and top-5
guardrails. A constrained hybrid reconstruction is feasible future work, but
it needs its own validation protocol.

A blind full retrain or Optuna rerun would multiply selection pressure,
obscure the source of any improvement and risk damaging the accepted active
engine. V2.8 therefore publishes diagnostics and, only when historical
guardrails pass, a non-active candidate for explicit human review.
