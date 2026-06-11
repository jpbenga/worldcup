# Temporal Leakage Audit V2.1

The V2.1 data-only pipeline passed: `true`.

`{'no_future_fixtures': True, 'no_future_world_cup_2026_fixtures': True, 'no_club_matches': True, 'senior_friendlies_only': True, 'no_missing_scores': True, 'finished_statuses_only': True, 'no_duplicates': True, 'odds_not_used_as_feature': True, 'post_match_features_clearly_marked': True, 'post_match_features_not_used_for_same_match_prediction': True, 'no_model_retrained': True, 'no_optuna_rerun': True}`

No future fixture, future World Cup 2026 fixture, club match, missing score,
unfinished status or duplicate fixture ID may enter the refreshed dataset.
Statistics, events and lineups are retained only as explicitly post-match
coverage evidence; they are not used to predict their own match. Odds are not
used as a feature, no model is retrained and Optuna is not rerun.

Qualification competitions whose provider season is labelled 2026 may contain
already-completed matches. Those rows are historical, but the report preserves
this warning so a future V2.2 pipeline cannot confuse season labels with event
time.
