# XGBoost Market Engine V2.0

The experiment trains one `multi:softprob` 1X2 model and thirteen
`binary:logistic` secondary-market models. Depth is bounded, regularization is
mandatory, and the shared hyperparameters are selected by Optuna on validation only.

Selected parameters: `{'rating_scale': 350, 'rating_k_factor': 30, 'goal_margin_multiplier': True, 'competition_weighting': True, 'context_advantage': 0, 'base_home_goals': 1.2999999999999998, 'base_away_goals': 1.35, 'beta_rating': 0.45000000000000007, 'rating_factor_cap': 0.4, 'recent_weight': 0.4, 'strength_weight': 0.5, 'blend_weight_xgb': 0.39999999999999997, 'max_depth': 4, 'eta': 0.03, 'subsample': 0.7, 'colsample_bytree': 1.0, 'min_child_weight': 1, 'lambda': 5.0, 'alpha': 1.0, 'num_boost_round': 350}`.

Train, validation, and test reports are published to expose overfit risk. The measured
train-to-validation log-loss gap is
`+0.2122`.
Feature importance for the multiclass model and every binary market model is retained
in `xgboost_market_results_v2_0.json`. Test data never chooses a tree parameter.
