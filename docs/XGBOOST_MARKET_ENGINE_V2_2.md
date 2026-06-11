# XGBoost Market Engine V2.2

V2.2 trains one multiclass 1X2 model and thirteen binary secondary-market models. Tree depth is capped at three, regularization is mandatory, and validation early stopping is used during Optuna selection. The frozen round count and parameters are then fitted on train only before the single final-test evaluation.

The measured train-validation log-loss gap is `0.0178`. Test never selects parameters. Gain importance for all fourteen models is retained in `xgboost_market_results_v2_2.json`; permutation importance was excluded to keep the limited retrain focused.
