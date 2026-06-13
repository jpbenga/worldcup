# UI Enrichment Strategy V2.5

V2.5 uses progressive disclosure rather than a visual rebuild.

- Group cards add one compact active-prediction row: modal score and favorite
  probability.
- The existing match modal promotes active V2.2/V2.4 data: score modal, 1X2,
  top scores, coherence, selected markets and DNB push explanation.
- Market details, the full score matrix and transparency metadata use native
  disclosure panels so the first view remains readable.
- The simulation route reuses the established group tabs, cards, borders and
  typography.

Legacy baseline/Elo comparison remains secondary transparency context. V2.5
does not retrain, retune or regenerate active probabilities.

## Information choices

The card shows the modal score and favorite probability because they answer the
fastest scan questions without becoming a market table. Confidence remains in
the modal, beside the score and 1X2 summary.

Secondary markets are grouped in a disclosure panel. DNB includes the short
push definition directly where it is used. Top scores appear as five compact
values with a one-line definition; the larger matrix stays collapsed by
default. Favorite-score disagreement receives a visible amber note because it
changes how the summary should be read.

No market is removed from the contract or declared universally good or bad.
The modal gives broad signals first and keeps technical context available.
Tournament probabilities live on `/simulation`, where rank and qualification
columns have enough space to remain legible.
