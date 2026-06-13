# Quant Engine V2.2 Results

V2.2 is a limited retrain of the V2 quant architecture on 3,062 refreshed completed senior-international matches. V2.2 uses only the refreshed V2.1 chronological splits. Every feature is built before the current result is observed; test is evaluated once after validation-only selection. Sparse provider statistics, events, lineups, provider xG, exploratory xG proxy and odds are excluded.

- Validation log loss / Brier: `0.9099` / `0.5348`
- Test log loss / Brier: `0.8812` / `0.5158`
- Test accuracy / exact / top-3 / top-5: `60.2%` / `14.6%` / `35.9%` / `51.3%`
- Test modal 1-1: `23.7%`
- Decision: `deploy_active_engine`

The comparison with V2.0 and V0.9 is directional because those versions used older test periods. The strict active-deployment decision nevertheless requires every listed gate to pass. Failed gates remain visible in the result JSON.
