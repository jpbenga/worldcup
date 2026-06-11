# Feature Audit V2.2

The V2.2 builder retains `24` conservative numeric pre-match features reconstructed from prior results. V2.2 uses only the refreshed V2.1 chronological splits. Every feature is built before the current result is observed; test is evaluated once after validation-only selection. Sparse provider statistics, events, lineups, provider xG, exploratory xG proxy and odds are excluded.

Advanced provider feature families were available on a six-match probe but their broad historical coverage was not established. They are therefore excluded rather than imputed into a misleading signal. Features retained and excluded are enumerated in `feature_audit_v2_2.json`.

- Advanced features used: none
- Current-match post-match data used: false
- Provider xG used: false
- Leakage detected: `false`
