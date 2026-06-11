# Historical Replay V2.0

Historical evaluation follows `predict -> observe -> update -> next match`.
Validation replays `196`
matches and test replays `198`
matches. The XGBoost model is fitted on train only, while the internal rating and
recent-history state advance after each observed validation/test match.

All historical features are reconstructed chronologically before each result is observed. Optuna selects on validation only; the fixed configuration is then evaluated once on test. No World Cup 2026 fixture and no external static Elo rating enters training or selection.

The test remains final and is not fed back into Optuna or parameter selection.
Per-match replay outputs, full metrics, lambda diagnostics, and segment reports are
published separately for auditability.
