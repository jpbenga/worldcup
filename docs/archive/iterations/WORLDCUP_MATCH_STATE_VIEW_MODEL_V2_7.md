# World Cup Match State View Model V2.7

The V2.7 match-state view model is the single frontend source for all `72` fixtures. Each record joins the frozen V2.4 prediction, current V2.6 result status, finished-match evaluation, normalized matchday, standings impact and display labels used by both cards and the existing modal.

`25` matches have a modal-score outcome that differs from the active 1X2 favorite. Those matches include a score compatible with the favorite and a concise explanation rather than being labelled contradictory.

Finished results remain a separate layer and never rewrite pre-match matrices or probabilities. Non-finished matches never receive a final evaluation.
