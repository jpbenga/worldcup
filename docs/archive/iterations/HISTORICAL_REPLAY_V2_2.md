# Historical Replay V2.2

Replay follows `predict -> observe -> update` across train, validation and test. Validation contains `459` matches and test contains `460` matches from the V2.1 refreshed chronological splits. Test is evaluated once after selection and cannot trigger retuning.

The rating and team-history states advance only after each completed match result is observed. Future World Cup 2026 fixtures are excluded from every historical state and selection decision.

Split boundaries remain explicit in every artifact. Earlier observed results may
update state for a later chronological match, but final-test evidence never
changes the selected configuration or triggers retuning.
