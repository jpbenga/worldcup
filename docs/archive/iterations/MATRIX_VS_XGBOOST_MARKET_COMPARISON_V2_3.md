# Matrix vs XGBoost Market Comparison V2.3

Secondary XGBoost probabilities were published only as aggregate V2.2 metrics, not per match. V2.3 therefore compares aggregate Brier and threshold reports without reconstructing or retraining models. Active hybrid probabilities are distinct only for 1X2; active secondary fields are matrix-derived.

- 1X2 matrix Brier: `0.5212`
- 1X2 XGBoost Brier: `0.5207`
- 1X2 active hybrid Brier: `0.5158`
- Matrix wins by secondary Brier: `['away_over_0_5', 'away_over_1_5', 'double_chance_1X', 'double_chance_12']`
- XGBoost wins by secondary Brier: `['over_1_5', 'over_2_5', 'over_3_5', 'both_teams_to_score_yes', 'home_over_0_5', 'home_over_1_5', 'double_chance_X2']`

Markets should remain matrix-derived where coherent score-distribution probabilities beat direct XGBoost Brier. Direct XGBoost is preferable only where its published aggregate Brier is lower. No distinct secondary hybrid claim is supportable from the current artifacts.
