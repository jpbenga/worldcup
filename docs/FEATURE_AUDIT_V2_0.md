# Feature Audit V2.0

The builder produces `24` numeric features. Every row is
built from rating and team history available strictly before kickoff; the current
match result is observed only after its prediction row exists. Updates then feed the
next chronological match.

All historical features are reconstructed chronologically before each result is observed. Optuna selects on validation only; the fixed configuration is then evaluated once on test. No World Cup 2026 fixture and no external static Elo rating enters training or selection.

- Pre-match only: `true`
- Current-match stats used: `false`
- External static Elo used: `false`
- Leakage detected: `false`
- Rows by split: `{'train': 917, 'validation': 196, 'test': 198}`

Unknown venue context is encoded neutrally because the normalized historical source
does not expose a reliable neutral-site flag.
