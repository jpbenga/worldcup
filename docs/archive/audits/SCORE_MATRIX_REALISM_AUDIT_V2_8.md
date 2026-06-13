# Score Matrix Realism Audit V2.8

V2.8 audits the active `quant_hybrid_v2.2` matrix without retraining, Optuna or changes to active predictions. The historical 460-match test is the decision set; the 72 World Cup fixtures are descriptive only.

Le 1X2 additionne de nombreuses cases de la matrice, alors que le score modal ne correspond qu’à une seule case. Un moteur peut donc être bien calibré en 1X2 tout en étant trop prudent dans la distribution des scores.

## Diagnosis

- World Cup modal scores 0-0/1-0/0-1/1-1: `71/72` (`98.6%`)
- World Cup modal scores with 3+ goals: `0/72`
- Historical actual 3+ goal matches: `226/460`
- Historical modal 3+ goal matches: `10/460`
- Historical actual versus modal favorite margin: `1.457` versus `0.852`

The matrix is materially conservative as a modal-score generator. That does not prove its broad markets are unusable: it proves exact-score presentation and tournament score simulation require separate scrutiny.

## Spain vs Cape Verde Islands

Spain is the `64.0%` favorite. The modal score is `1-0` at `14.8%`, with reconstructed expected goals `1.756` to `0.715`. Spain wins by one with probability `26.3%` and by two or more with probability `36.1%`.

The 1-0 cell is mathematically coherent because a modal score is only one cell. It is nevertheless footballistically cautious relative to the aggregate favorite signal and should be tested against historical strong-favorite margins rather than corrected from this example alone.

## Cause assessment

The strongest evidence points to lambda/total compression and an objective centered more on aggregate 1X2 than exact-score likelihood. Rating compression, draw mass and missing mismatch boost remain plausible but are not established as sole causes.

- **A. Compression des ratings / Elo gap trop faible** — severity `medium`. Evidence for: Strong-favorite modal margins remain narrow. Evidence against: Hybrid 1X2 still creates strong-favorite buckets. Recommended test: Compare rating gap with lambda gap by favorite bucket.
- **B. Lambdas attaque/défense trop proches de la moyenne** — severity `high`. Evidence for: Historical modal favorite margin trails actual by 0.604. Evidence against: Published lambda audit reports meaningful pairwise differences. Recommended test: Post-model favorite lambda-gap scaling.
- **C. Cap implicite sur favorite xG** — severity `medium`. Evidence for: Very few 3+ modal scores appear for strong favorites. Evidence against: V2.2 metadata reports no explicit lambda clipping. Recommended test: Inspect upper-tail favorite lambdas and clipping flags.
- **D. Trop forte probabilité de nul** — severity `medium`. Evidence for: Low-score draw cells are frequently modal. Evidence against: A draw correction can damage calibrated 1X2. Recommended test: Bounded strong-favorite draw-mass correction.
- **E. Distribution Poisson trop concentrée sur petits scores** — severity `high`. Evidence for: Actual 3+ total rate is 49.1% versus 2.2% modal. Evidence against: A modal distribution is inherently narrower than realized scores. Recommended test: Total-goals temperature challenger with score-likelihood guardrail.
- **F. Calibration optimisée pour log loss 1X2 plutôt que score likelihood** — severity `high`. Evidence for: The hybrid objective can aggregate outcome cells without rewarding realistic modal margins. Evidence against: Poisson score likelihood remains indirectly represented. Recommended test: Use historical score log likelihood as a challenger criterion.
- **G. Manque de feature mismatch / mismatch boost** — severity `medium`. Evidence for: Strong favorites lack an explicit post-model mismatch term. Evidence against: Ratings and attack/defence features already encode mismatch. Recommended test: Targeted mismatch boost benchmark, no full retrain.
- **H. Données historiques internationales trop prudentes** — severity `low`. Evidence for: International group and qualification games include cautious regimes. Evidence against: The same corpus also contains large mismatches. Recommended test: Segment totals and margins by competition tier.
- **I. Effet compétition/groupe conservateur** — severity `low`. Evidence for: World Cup group-stage priors may suppress totals. Evidence against: The historical issue also appears across competitions. Recommended test: Compare group-stage and qualification matrix realism.
