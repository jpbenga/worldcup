# Engine Reference Inventory

## Scope

Generated from tracked and untracked non-ignored files in `backend/`, `docs/`, `handoff_worldcup_2026/`,
`README.md` and `prototype_ia_coupe_du_monde_2026.md`. Generated data, secrets
and the inventory outputs themselves are excluded.

## Summary

- Findings: `501`
- Files with findings: `51`
- Categories: `{'backtest': 59, 'data': 23, 'dependency': 30, 'documentation': 300, 'metric': 15, 'model': 74}`
- Most frequent terms: `{'Elo': 205, 'xG': 48, 'historique': 41, 'calibration': 29, 'backtest': 28, 'Poisson': 24, 'Dixon': 21, 'expected goals': 17, 'Dixon-Coles': 15, 'log loss': 8, 'optuna': 7, 'scipy': 7}`

## Historical dependency candidates

- Runtime backend acquisition: `beautifulsoup4`, `playwright`, `python-dotenv`, `requests`.
- Testing: `pytest`.
- Legacy optimizer candidates explicitly documented: `numpy`, `scipy`, `optuna`.
- No tracked dependency file declares `pandas`, `statsmodels`, `scikit-learn`,
  `penaltyblog`, `xgboost`, `lightgbm` or `catboost`.

## Findings

| File | Line | Term | Category | Short excerpt |
|---|---:|---|---|---|
| `docs/CURRENT_ENGINE_AUDIT.md` | 23 | `Elo` | documentation | -> optional bounded Elo adjustment |
| `docs/CURRENT_ENGINE_AUDIT.md` | 24 | `Dixon-Coles` | documentation | -> Poisson/Dixon-Coles score matrix |
| `docs/CURRENT_ENGINE_AUDIT.md` | 24 | `Dixon` | documentation | -> Poisson/Dixon-Coles score matrix |
| `docs/CURRENT_ENGINE_AUDIT.md` | 24 | `Poisson` | documentation | -> Poisson/Dixon-Coles score matrix |
| `docs/CURRENT_ENGINE_AUDIT.md` | 26 | `Elo` | documentation | -> baseline/Elo/comparison snapshots |
| `docs/CURRENT_ENGINE_AUDIT.md` | 31 | `Elo` | documentation | 'generate_predictions.generate_models("both")' for baseline and Elo outputs. |
| `docs/CURRENT_ENGINE_AUDIT.md` | 40 | `xG` | documentation | \| Baseline xG \| 'generate_predictions.baseline_expected_goals' \| Blends recent goals-for and goals-against inputs, then calls 'compute_lambdas'. \| |
| `docs/CURRENT_ENGINE_AUDIT.md` | 41 | `xG` | documentation | \| Lambda helper \| 'expected_goals.compute_lambdas' \| Modulates xG with a logistic Elo-strength formula and optional home advantage. \| |
| `docs/CURRENT_ENGINE_AUDIT.md` | 41 | `Elo` | documentation | \| Lambda helper \| 'expected_goals.compute_lambdas' \| Modulates xG with a logistic Elo-strength formula and optional home advantage. \| |
| `docs/CURRENT_ENGINE_AUDIT.md` | 43 | `Elo` | documentation | \| Elo lookup \| 'elo_features.get_match_elo_features' \| Reads validated API-Football-to-Elo mappings. \| |
| `docs/CURRENT_ENGINE_AUDIT.md` | 44 | `xG` | documentation | \| Elo variant \| 'elo_adjusted_model.adjust_expected_goals' \| Applies a bounded, moderate Elo factor to baseline xG. \| |
| `docs/CURRENT_ENGINE_AUDIT.md` | 44 | `Elo` | documentation | \| Elo variant \| 'elo_adjusted_model.adjust_expected_goals' \| Applies a bounded, moderate Elo factor to baseline xG. \| |
| `docs/CURRENT_ENGINE_AUDIT.md` | 45 | `Dixon-Coles` | data | \| Score matrix \| 'score_matrix.generate_score_matrix' \| Multiplies independent Poisson probabilities, applies Dixon-Coles low-score correction and normalizes. \| |
| `docs/CURRENT_ENGINE_AUDIT.md` | 45 | `Dixon` | data | \| Score matrix \| 'score_matrix.generate_score_matrix' \| Multiplies independent Poisson probabilities, applies Dixon-Coles low-score correction and normalizes. \| |
| `docs/CURRENT_ENGINE_AUDIT.md` | 45 | `Poisson` | data | \| Score matrix \| 'score_matrix.generate_score_matrix' \| Multiplies independent Poisson probabilities, applies Dixon-Coles low-score correction and normalizes. \| |
| `docs/CURRENT_ENGINE_AUDIT.md` | 52 | `xG` | documentation | ## How baseline xG is generated |
| `docs/CURRENT_ENGINE_AUDIT.md` | 72 | `Elo` | documentation | It then calls 'compute_lambdas' with neutral input Elo, no home-field advantage |
| `docs/CURRENT_ENGINE_AUDIT.md` | 76 | `xG` | documentation | The xG are neutral because the active 2026 fixture feed does not itself provide |
| `docs/CURRENT_ENGINE_AUDIT.md` | 78 | `calibration` | documentation | features would falsely imply calibration, so V0.5 deliberately chose explicit |
| `docs/CURRENT_ENGINE_AUDIT.md` | 81 | `Dixon-Coles` | documentation | ## Poisson and Dixon-Coles matrix |
| `docs/CURRENT_ENGINE_AUDIT.md` | 81 | `Dixon` | documentation | ## Poisson and Dixon-Coles matrix |
| `docs/CURRENT_ENGINE_AUDIT.md` | 81 | `Poisson` | documentation | ## Poisson and Dixon-Coles matrix |
| `docs/CURRENT_ENGINE_AUDIT.md` | 87 | `Poisson` | documentation | Poisson(home_goals \| home_lambda) * Poisson(away_goals \| away_lambda) |
| `docs/CURRENT_ENGINE_AUDIT.md` | 111 | `Elo` | documentation | ## Elo injection and unchanged modal scores |
| `docs/CURRENT_ENGINE_AUDIT.md` | 113 | `Elo` | documentation | The baseline records mapped Elo values as metadata but does not use them. |
| `docs/CURRENT_ENGINE_AUDIT.md` | 114 | `Elo` | documentation | The separate Elo variant reads validated ratings and computes: |
| `docs/CURRENT_ENGINE_AUDIT.md` | 125 | `Elo` | documentation | enough to move another exact score above '1-1'; therefore baseline and Elo both |
| `docs/CURRENT_ENGINE_AUDIT.md` | 135 | `Elo` | documentation | - Elo predictions with 'engine_status = "experimental"' and |
| `docs/CURRENT_ENGINE_AUDIT.md` | 142 | `backtest` | backtest | calibration, no tournament simulation, no valid backtest for future fixtures, |
| `docs/CURRENT_ENGINE_AUDIT.md` | 142 | `calibration` | backtest | calibration, no tournament simulation, no valid backtest for future fixtures, |
| `docs/CURRENT_ENGINE_AUDIT.md` | 143 | `calibration` | documentation | no probabilistic calibration metrics, a finite matrix tail and a simple |
| `docs/CURRENT_ENGINE_AUDIT.md` | 150 | `xG` | documentation | - 'drc-prototype/optimizer.py': explicit xG/Elo formulas, |
| `docs/CURRENT_ENGINE_AUDIT.md` | 150 | `Elo` | documentation | - 'drc-prototype/optimizer.py': explicit xG/Elo formulas, |
| `docs/CURRENT_ENGINE_AUDIT.md` | 151 | `Dixon-Coles` | documentation | Poisson/Dixon-Coles and chronological optimization with log loss; |
| `docs/CURRENT_ENGINE_AUDIT.md` | 151 | `Dixon` | documentation | Poisson/Dixon-Coles and chronological optimization with log loss; |
| `docs/CURRENT_ENGINE_AUDIT.md` | 151 | `Poisson` | documentation | Poisson/Dixon-Coles and chronological optimization with log loss; |
| `docs/CURRENT_ENGINE_AUDIT.md` | 151 | `log loss` | metric | Poisson/Dixon-Coles and chronological optimization with log loss; |
| `docs/CURRENT_ENGINE_AUDIT.md` | 152 | `xG` | backtest | - 'drc-prototype/xg-backtest.js': rolling baseline and chronological backtest; |
| `docs/CURRENT_ENGINE_AUDIT.md` | 152 | `backtest` | backtest | - 'drc-prototype/xg-backtest.js': rolling baseline and chronological backtest; |
| `docs/CURRENT_ENGINE_AUDIT.md` | 153 | `backtest` | backtest | - 'drc-prototype/backtest.js': detailed validation history; |
| `docs/CURRENT_ENGINE_AUDIT.md` | 165 | `Poisson` | documentation | \| Statistical modeling \| No declared runtime library; current Poisson implementation uses standard-library 'math'. \| |
| `docs/CURRENT_ENGINE_AUDIT.md` | 166 | `optuna` | dependency | \| Optimization \| 'scipy' and 'optuna' are explicitly listed as optional legacy optimizer candidates. \| |
| `docs/CURRENT_ENGINE_AUDIT.md` | 166 | `scipy` | dependency | \| Optimization \| 'scipy' and 'optuna' are explicitly listed as optional legacy optimizer candidates. \| |
| `docs/CURRENT_ENGINE_AUDIT.md` | 167 | `scikit` | dependency | \| Machine learning \| No tracked dependency on scikit-learn, XGBoost, LightGBM or CatBoost. \| |
| `docs/CURRENT_ENGINE_AUDIT.md` | 167 | `xgboost` | dependency | \| Machine learning \| No tracked dependency on scikit-learn, XGBoost, LightGBM or CatBoost. \| |
| `docs/CURRENT_ENGINE_AUDIT.md` | 167 | `lightgbm` | dependency | \| Machine learning \| No tracked dependency on scikit-learn, XGBoost, LightGBM or CatBoost. \| |
| `docs/CURRENT_ENGINE_AUDIT.md` | 167 | `catboost` | dependency | \| Machine learning \| No tracked dependency on scikit-learn, XGBoost, LightGBM or CatBoost. \| |
| `docs/CURRENT_ENGINE_AUDIT.md` | 168 | `penaltyblog` | dependency | \| Football modeling \| No tracked dependency on 'penaltyblog'; football formulas are local. \| |
| `docs/CURRENT_ENGINE_AUDIT.md` | 173 | `numpy` | dependency | 'numpy' is also explicitly listed as an optional legacy optimizer candidate. |
| `docs/CURRENT_ENGINE_AUDIT.md` | 174 | `scikit` | dependency | No clear historical dependency on 'pandas', 'statsmodels', 'scikit-learn', |
| `docs/CURRENT_ENGINE_AUDIT.md` | 174 | `statsmodels` | dependency | No clear historical dependency on 'pandas', 'statsmodels', 'scikit-learn', |
| `docs/CURRENT_ENGINE_AUDIT.md` | 174 | `pandas` | dependency | No clear historical dependency on 'pandas', 'statsmodels', 'scikit-learn', |
| `docs/CURRENT_ENGINE_AUDIT.md` | 175 | `penaltyblog` | dependency | 'penaltyblog', 'xgboost', 'lightgbm' or 'catboost' was found. |
| `docs/CURRENT_ENGINE_AUDIT.md` | 175 | `xgboost` | dependency | 'penaltyblog', 'xgboost', 'lightgbm' or 'catboost' was found. |
| `docs/CURRENT_ENGINE_AUDIT.md` | 175 | `lightgbm` | dependency | 'penaltyblog', 'xgboost', 'lightgbm' or 'catboost' was found. |
| `docs/CURRENT_ENGINE_AUDIT.md` | 175 | `catboost` | dependency | 'penaltyblog', 'xgboost', 'lightgbm' or 'catboost' was found. |
| `docs/CURRENT_ENGINE_AUDIT.md` | 191 | `calibration` | backtest | \| 'data_sources.json' \| Honest source, calibration and backtesting status. \| |
| `docs/CURRENT_ENGINE_AUDIT.md` | 198 | `calibration` | documentation | explicit engine/calibration metadata. Any incompatible change requires a |
| `docs/FUTURE_ENGINE_BLUEPRINT.md` | 14 | `Elo` | documentation | \| Inputs \| Neutral '1.35 / 1.35', current mapped Elo \| Chronological results, attack/defence strength, neutral/home context, pre-match Elo \| Level 2 plus dynamic Elo, recent form, importance and consistent advanced stats |
| `docs/FUTURE_ENGINE_BLUEPRINT.md` | 15 | `Dixon-Coles` | documentation | \| Model \| Simple Poisson/Dixon-Coles; separate bounded Elo variant \| Fitted Poisson/Dixon-Coles with team attack/defence parameters and Elo prior/feature \| Hybrid statistical/ML model with calibrated probability outputs  |
| `docs/FUTURE_ENGINE_BLUEPRINT.md` | 15 | `Dixon` | documentation | \| Model \| Simple Poisson/Dixon-Coles; separate bounded Elo variant \| Fitted Poisson/Dixon-Coles with team attack/defence parameters and Elo prior/feature \| Hybrid statistical/ML model with calibrated probability outputs  |
| `docs/FUTURE_ENGINE_BLUEPRINT.md` | 15 | `Poisson` | documentation | \| Model \| Simple Poisson/Dixon-Coles; separate bounded Elo variant \| Fitted Poisson/Dixon-Coles with team attack/defence parameters and Elo prior/feature \| Hybrid statistical/ML model with calibrated probability outputs  |
| `docs/FUTURE_ENGINE_BLUEPRINT.md` | 15 | `Elo` | documentation | \| Model \| Simple Poisson/Dixon-Coles; separate bounded Elo variant \| Fitted Poisson/Dixon-Coles with team attack/defence parameters and Elo prior/feature \| Hybrid statistical/ML model with calibrated probability outputs  |
| `docs/FUTURE_ENGINE_BLUEPRINT.md` | 16 | `calibration` | documentation | \| Parameters \| Hard-coded blend, 'rho=-0.05', Elo weight '0.20', clamp '±0.35' \| Fitted decay, attack/defence, neutral advantage, rho and Elo contribution \| Tuned feature sets, model families, ensembles and calibration l |
| `docs/FUTURE_ENGINE_BLUEPRINT.md` | 16 | `Elo` | documentation | \| Parameters \| Hard-coded blend, 'rho=-0.05', Elo weight '0.20', clamp '±0.35' \| Fitted decay, attack/defence, neutral advantage, rho and Elo contribution \| Tuned feature sets, model families, ensembles and calibration l |
| `docs/FUTURE_ENGINE_BLUEPRINT.md` | 18 | `optuna` | dependency | \| Training \| None \| Chronological fitting, likely SciPy or Optuna \| Automated tuning and model-family comparison \| |
| `docs/FUTURE_ENGINE_BLUEPRINT.md` | 18 | `scipy` | dependency | \| Training \| None \| Chronological fitting, likely SciPy or Optuna \| Automated tuning and model-family comparison \| |
| `docs/FUTURE_ENGINE_BLUEPRINT.md` | 20 | `calibration` | documentation | \| Metrics \| Diversity audit and market deltas \| Negative log likelihood/log loss, Brier score, RPS and calibration \| Level 2 plus segmented performance, drift and calibration monitoring \| |
| `docs/FUTURE_ENGINE_BLUEPRINT.md` | 20 | `log loss` | metric | \| Metrics \| Diversity audit and market deltas \| Negative log likelihood/log loss, Brier score, RPS and calibration \| Level 2 plus segmented performance, drift and calibration monitoring \| |
| `docs/FUTURE_ENGINE_BLUEPRINT.md` | 20 | `Brier` | metric | \| Metrics \| Diversity audit and market deltas \| Negative log likelihood/log loss, Brier score, RPS and calibration \| Level 2 plus segmented performance, drift and calibration monitoring \| |
| `docs/FUTURE_ENGINE_BLUEPRINT.md` | 20 | `RPS` | metric | \| Metrics \| Diversity audit and market deltas \| Negative log likelihood/log loss, Brier score, RPS and calibration \| Level 2 plus segmented performance, drift and calibration monitoring \| |
| `docs/FUTURE_ENGINE_BLUEPRINT.md` | 20 | `negative log likelihood` | metric | \| Metrics \| Diversity audit and market deltas \| Negative log likelihood/log loss, Brier score, RPS and calibration \| Level 2 plus segmented performance, drift and calibration monitoring \| |
| `docs/FUTURE_ENGINE_BLUEPRINT.md` | 21 | `calibration` | documentation | \| Output JSON \| Existing stable snapshots \| Same contracts with new explicit model version/calibration metadata \| Same or deliberately versioned contracts \| |
| `docs/FUTURE_ENGINE_BLUEPRINT.md` | 26 | `xG` | documentation | The current engine uses equal baseline xG for all 72 fixtures, a simple |
| `docs/FUTURE_ENGINE_BLUEPRINT.md` | 27 | `Dixon-Coles` | documentation | Poisson/Dixon-Coles score matrix and a moderate separate Elo adjustment. It has |
| `docs/FUTURE_ENGINE_BLUEPRINT.md` | 27 | `Dixon` | documentation | Poisson/Dixon-Coles score matrix and a moderate separate Elo adjustment. It has |
| `docs/FUTURE_ENGINE_BLUEPRINT.md` | 27 | `Poisson` | documentation | Poisson/Dixon-Coles score matrix and a moderate separate Elo adjustment. It has |
| `docs/FUTURE_ENGINE_BLUEPRINT.md` | 27 | `Elo` | documentation | Poisson/Dixon-Coles score matrix and a moderate separate Elo adjustment. It has |
| `docs/FUTURE_ENGINE_BLUEPRINT.md` | 28 | `calibration` | documentation | no fitting or historical calibration. Baseline and Elo both return '1-1' as |
| `docs/FUTURE_ENGINE_BLUEPRINT.md` | 28 | `Elo` | documentation | no fitting or historical calibration. Baseline and Elo both return '1-1' as |
| `docs/FUTURE_ENGINE_BLUEPRINT.md` | 43 | `Elo` | documentation | - pre-match Elo or a chronologically reconstructed Elo; |
| `docs/FUTURE_ENGINE_BLUEPRINT.md` | 48 | `Dixon-Coles` | documentation | Fit a Poisson/Dixon-Coles model with team attack and defence strengths, |
| `docs/FUTURE_ENGINE_BLUEPRINT.md` | 48 | `Dixon` | documentation | Fit a Poisson/Dixon-Coles model with team attack and defence strengths, |
| `docs/FUTURE_ENGINE_BLUEPRINT.md` | 48 | `Poisson` | documentation | Fit a Poisson/Dixon-Coles model with team attack and defence strengths, |
| `docs/FUTURE_ENGINE_BLUEPRINT.md` | 48 | `fit` | documentation | Fit a Poisson/Dixon-Coles model with team attack and defence strengths, |
| `docs/FUTURE_ENGINE_BLUEPRINT.md` | 50 | `Elo` | documentation | correlation. Elo can act as a prior, regularizer or explicit feature, but its |
| `docs/FUTURE_ENGINE_BLUEPRINT.md` | 53 | `expected goals` | documentation | The model should generate differentiated expected goals per match. It should |
| `docs/FUTURE_ENGINE_BLUEPRINT.md` | 59 | `fit` | documentation | - Fit only on completed matches available before each evaluation date. |
| `docs/FUTURE_ENGINE_BLUEPRINT.md` | 60 | `scipy` | dependency | - Use SciPy for a transparent likelihood optimizer first. |
| `docs/FUTURE_ENGINE_BLUEPRINT.md` | 61 | `optuna` | dependency | - Consider Optuna only for bounded hyperparameter tuning after the objective |
| `docs/FUTURE_ENGINE_BLUEPRINT.md` | 61 | `objective` | documentation | - Consider Optuna only for bounded hyperparameter tuning after the objective |
| `docs/FUTURE_ENGINE_BLUEPRINT.md` | 70 | `log loss` | metric | - negative log likelihood / log loss for probabilistic fit; |
| `docs/FUTURE_ENGINE_BLUEPRINT.md` | 70 | `negative log likelihood` | metric | - negative log likelihood / log loss for probabilistic fit; |
| `docs/FUTURE_ENGINE_BLUEPRINT.md` | 70 | `fit` | documentation | - negative log likelihood / log loss for probabilistic fit; |
| `docs/FUTURE_ENGINE_BLUEPRINT.md` | 71 | `Brier` | metric | - Brier score for outcome probabilities; |
| `docs/FUTURE_ENGINE_BLUEPRINT.md` | 72 | `ranked probability score` | metric | - ranked probability score for ordered goal/outcome distributions; |
| `docs/FUTURE_ENGINE_BLUEPRINT.md` | 73 | `calibration` | documentation | - calibration curves and reliability by probability bucket; |
| `docs/FUTURE_ENGINE_BLUEPRINT.md` | 82 | `Elo` | documentation | preselected algorithm. Candidate inputs include dynamic Elo, recent form, |
| `docs/FUTURE_ENGINE_BLUEPRINT.md` | 83 | `xG` | documentation | competition importance, rest/travel context and consistent shot/xG features. |
| `docs/FUTURE_ENGINE_BLUEPRINT.md` | 87 | `optuna` | dependency | Optuna may tune hyperparameters only inside chronological validation. Any |
| `docs/FUTURE_ENGINE_BLUEPRINT.md` | 88 | `calibration` | documentation | probabilities should receive explicit calibration testing and, where justified, |
| `docs/FUTURE_ENGINE_BLUEPRINT.md` | 89 | `calibration` | documentation | post-model calibration. A model registry should record data version, features, |
| `docs/FUTURE_ENGINE_BLUEPRINT.md` | 90 | `calibration` | documentation | parameters, metrics, calibration status and promotion decision. |
| `docs/FUTURE_ENGINE_BLUEPRINT.md` | 118 | `Elo` | documentation | and pre-match Elo feasibility. Produce a small audited historical sample and a |
| `docs/HISTORICAL_DATA_STRATEGY.md` | 7 | `train` | data | V0.6 does not fetch history, train a model or alter current predictions. |
| `docs/HISTORICAL_DATA_STRATEGY.md` | 14 | `Elo` | data | \| Elo Ratings \| 244 normalized ratings and validated mapping for all 48 World Cup teams. \| Current ratings are snapshots, not guaranteed pre-match historical ratings. \| |
| `docs/HISTORICAL_DATA_STRATEGY.md` | 29 | `Elo` | data | - pre-match Elo or the closest valid rating strictly before kickoff; |
| `docs/HISTORICAL_DATA_STRATEGY.md` | 33 | `xG` | data | shots on target, possession and provider xG. Sparse advanced statistics must |
| `docs/HISTORICAL_DATA_STRATEGY.md` | 61 | `Elo` | data | 8. Join only pre-match Elo values or reconstruct Elo chronologically from results. |
| `docs/HISTORICAL_DATA_STRATEGY.md` | 68 | `train` | data | - Split train, validation and test sets by date, never randomly across time. |
| `docs/HISTORICAL_DATA_STRATEGY.md` | 71 | `train` | data | - Tune parameters only on train/validation periods. |
| `docs/HISTORICAL_DATA_STRATEGY.md` | 73 | `train` | data | - Never train on future World Cup 2026 fixtures. |
| `docs/HISTORICAL_DATA_STRATEGY.md` | 74 | `Elo` | data | - Never use final standings, post-match statistics or current Elo as if they |
| `docs/HISTORICAL_DATA_STRATEGY.md` | 80 | `train` | data | train through T1 -> validate on T1..T2 |
| `docs/HISTORICAL_DATA_STRATEGY.md` | 81 | `train` | data | train through T2 -> validate on T2..T3 |
| `docs/HISTORICAL_DATA_STRATEGY.md` | 88 | `calibration` | data | Before model calibration, the historical dataset must pass: |
| `docs/adr/ADR-0001-prototype-engine-now-calibrated-engine-later.md` | 11 | `Elo` | documentation | modal score for '72/72' baseline fixtures and for all Elo variants because the |
| `docs/adr/ADR-0001-prototype-engine-now-calibrated-engine-later.md` | 12 | `xG` | documentation | baseline xG are neutral '1.35 / 1.35'. |
| `docs/adr/ADR-0001-prototype-engine-now-calibrated-engine-later.md` | 16 | `Dixon-Coles` | documentation | Poisson/Dixon-Coles, market and Elo-related components, but no trustworthy |
| `docs/adr/ADR-0001-prototype-engine-now-calibrated-engine-later.md` | 16 | `Dixon` | documentation | Poisson/Dixon-Coles, market and Elo-related components, but no trustworthy |
| `docs/adr/ADR-0001-prototype-engine-now-calibrated-engine-later.md` | 16 | `Poisson` | documentation | Poisson/Dixon-Coles, market and Elo-related components, but no trustworthy |
| `docs/adr/ADR-0001-prototype-engine-now-calibrated-engine-later.md` | 16 | `Elo` | documentation | Poisson/Dixon-Coles, market and Elo-related components, but no trustworthy |
| `docs/adr/ADR-0001-prototype-engine-now-calibrated-engine-later.md` | 23 | `force` | documentation | - Do not force artificial prediction diversity. |
| `docs/adr/ADR-0001-prototype-engine-now-calibrated-engine-later.md` | 32 | `xG` | documentation | - Uniform modal scores remain visible until validated inputs replace neutral xG. |
| `docs/adr/ADR-0001-prototype-engine-now-calibrated-engine-later.md` | 34 | `calibration` | documentation | - A replacement model must prove out-of-sample performance and calibration. |
| `README.md` | 127 | `Elo` | documentation | Build and validate the explicit API-Football to Elo identity layer: |
| `README.md` | 136 | `Elo` | documentation | Elo ratings to the prediction engine or alter probabilities. |
| `README.md` | 138 | `Elo` | documentation | ## Experimental Elo model |
| `README.md` | 140 | `Elo` | documentation | Generate the stable baseline, the separate Elo-adjusted experiment, and their |
| `README.md` | 201 | `historique` | documentation | historique. |
| `backend/backtesting/backtester.py` | 1 | `backtest` | backtest | """Small chronological-friendly market backtester adapted from prototype backtest scripts.""" |
| `backend/data_acquisition/elo_ratings_client.py` | 1 | `Elo` | data | """Minimal Elo Ratings exploration via raw HTML, network capture, and rendered DOM.""" |
| `backend/data_acquisition/elo_ratings_client.py` | 20 | `Elo` | data | RAW_ROOT = PROJECT_ROOT / "backend" / "data" / "raw" / "elo" |
| `backend/data_acquisition/elo_ratings_client.py` | 30 | `Elo` | data | KEYWORDS = ("rating", "rank", "team", "country", "data", "json", "elo") |
| `backend/data_acquisition/elo_ratings_client.py` | 137 | `Elo` | data | "source_type": "elo", |
| `backend/prediction/elo_adjusted_model.py` | 1 | `expected goals` | model | """Moderate experimental Elo adjustment layered on top of baseline expected goals.""" |
| `backend/prediction/elo_adjusted_model.py` | 1 | `Elo` | model | """Moderate experimental Elo adjustment layered on top of baseline expected goals.""" |
| `backend/prediction/elo_adjusted_model.py` | 22 | `Elo` | model | """Apply a bounded Elo adjustment, with exact baseline fallback.""" |
| `backend/prediction/elo_adjusted_model.py` | 24 | `expected goals` | model | raise ValueError("Expected goals must be non-negative") |
| `backend/prediction/elo_adjusted_model.py` | 26 | `Elo` | model | raise ValueError("Elo weight must be between 0 and 1") |
| `backend/prediction/elo_features.py` | 1 | `Elo` | model | """Read validated team mappings and expose experimental Elo match features.""" |
| `backend/prediction/elo_features.py` | 27 | `Elo` | model | elo = item.get("elo") |
| `backend/prediction/elo_features.py` | 29 | `Elo` | model | if not isinstance(elo, dict) or mapping.get("status") not in {"auto_validated", "manual_validated"}: |
| `backend/prediction/elo_features.py` | 31 | `Elo` | model | rating = elo.get("elo_rating") |
| `backend/prediction/elo_features.py` | 38 | `Elo` | model | elo.get("team_name"), |
| `backend/prediction/elo_features.py` | 47 | `Elo` | model | """Return a validated mapped Elo rating, or None when none exists.""" |
| `backend/prediction/elo_features.py` | 52 | `Elo` | model | """Return symmetric Elo strengths only when both teams have mapped ratings.""" |
| `backend/prediction/expected_goals.py` | 1 | `xG` | backtest | """Expected-goal helpers extracted from drc-prototype/optimizer.py and xg-backtest.js.""" |
| `backend/prediction/expected_goals.py` | 1 | `backtest` | backtest | """Expected-goal helpers extracted from drc-prototype/optimizer.py and xg-backtest.js.""" |
| `backend/prediction/expected_goals.py` | 7 | `Elo` | model | """Convert an Elo difference into a home-win strength probability.""" |
| `backend/prediction/expected_goals.py` | 19 | `xG` | model | """Modulate baseline team xG with Elo strength and home-field advantage.""" |
| `backend/prediction/expected_goals.py` | 19 | `Elo` | model | """Modulate baseline team xG with Elo strength and home-field advantage.""" |
| `backend/prediction/expected_goals.py` | 21 | `expected goals` | model | raise ValueError("Expected goals must be non-negative") |
| `backend/prediction/expected_goals.py` | 37 | `xG` | model | """Build matchup xG baselines using the prototype's rolling attack/defence blend.""" |
| `backend/score_matrix/score_matrix.py` | 1 | `Dixon-Coles` | model | """Autonomous Poisson/Dixon-Coles score-matrix generator recycled from the prototype.""" |
| `backend/score_matrix/score_matrix.py` | 1 | `Dixon` | model | """Autonomous Poisson/Dixon-Coles score-matrix generator recycled from the prototype.""" |
| `backend/score_matrix/score_matrix.py` | 1 | `Poisson` | model | """Autonomous Poisson/Dixon-Coles score-matrix generator recycled from the prototype.""" |
| `backend/score_matrix/score_matrix.py` | 47 | `expected goals` | model | raise ValueError("Expected goals must be non-negative") |
| `backend/scripts/audit_prediction_diversity.py` | 24 | `Elo` | model | elo = load_json(DATA_DIR / "generated" / "predictions_elo.json") |
| `backend/scripts/audit_prediction_diversity.py` | 28 | `Elo` | model | elo_dist = distribution(elo) |
| `backend/scripts/audit_prediction_diversity.py` | 31 | `Elo` | model | elo_inputs = [prediction.get("model_inputs", {}) for prediction in elo] |
| `backend/scripts/audit_prediction_diversity.py` | 32 | `Elo` | model | elo_diffs = [prediction.get("elo_features", {}).get("elo_diff") for prediction in elo] |
| `backend/scripts/audit_prediction_diversity.py` | 38 | `expected goals` | model | "neutral baseline expected goals. Elo adjusts markets but does not change the modal score." |
| `backend/scripts/audit_prediction_diversity.py` | 38 | `Elo` | model | "neutral baseline expected goals. Elo adjusts markets but does not change the modal score." |
| `backend/scripts/audit_prediction_diversity.py` | 70 | `xG` | model | "Replace neutral baseline xG with validated team-specific historical features in a future phase.", |
| `backend/scripts/audit_prediction_diversity.py` | 71 | `xG` | model | "Expose Elo and xG inputs so users can understand the uniform top-score output.", |
| `backend/scripts/audit_prediction_diversity.py` | 71 | `Elo` | model | "Expose Elo and xG inputs so users can understand the uniform top-score output.", |
| `backend/scripts/audit_prediction_diversity.py` | 72 | `force` | model | "Do not force artificial score diversity.", |
| `backend/scripts/audit_prediction_diversity.py` | 90 | `Elo` | model | - Elo top-score distribution: '{elo_dist}' |
| `backend/scripts/audit_prediction_diversity.py` | 92 | `Elo` | model | - Elo 1-1 rate: '{one_one_elo:.1%}' |
| `backend/scripts/audit_prediction_diversity.py` | 93 | `Elo` | model | - Top scores changed by Elo: '{audit['top_score_changed_count']}' |
| `backend/scripts/audit_prediction_diversity.py` | 94 | `Elo` | model | - Elo unavailable: '{audit['elo_unavailable_count']}' |
| `backend/scripts/audit_prediction_diversity.py` | 101 | `Elo` | model | This is not a sorting bug or a missing-Elo fallback. The active real-data |
| `backend/scripts/audit_prediction_diversity.py` | 102 | `expected goals` | model | baseline assigns neutral '1.35 / 1.35' expected goals to every fixture because |
| `backend/scripts/audit_prediction_diversity.py` | 103 | `Elo` | model | validated historical team features are not yet available. The moderate Elo |
| `backend/scripts/audit_prediction_diversity.py` | 108 | `force` | model | Do not force diversity and do not present these predictions as calibrated. |
| `backend/scripts/audit_prediction_diversity.py` | 114 | `Elo` | model | print(f"Audited {total} predictions; baseline 1-1 rate={one_one_baseline:.1%}, Elo 1-1 rate={one_one_elo:.1%}.") |
| `backend/scripts/build_snapshots.py` | 56 | `backtest` | backtest | "label": "Backtest results", |
| `backend/scripts/build_snapshots.py` | 114 | `Elo` | model | parser.add_argument("--model", choices=("baseline", "elo", "both"), default="both") |
| `backend/scripts/build_snapshots.py` | 140 | `Elo` | model | if args.model in {"elo", "both"}: |
| `backend/scripts/build_team_identity_map.py` | 1 | `Elo` | model | """Build an explicit, reviewable API-Football to Elo team identity map.""" |
| `backend/scripts/build_team_identity_map.py` | 109 | `Elo` | model | "elo": { |
| `backend/scripts/build_team_identity_map.py` | 172 | `Elo` | model | "Some teams require human validation before using Elo ratings in the model.", |
| `backend/scripts/build_team_identity_map.py` | 173 | `Elo` | model | "Elo ratings remain excluded from the prediction engine.", |
| `backend/scripts/compare_prediction_models.py` | 1 | `Elo` | model | """Compare baseline and experimental Elo-adjusted prediction snapshots.""" |
| `backend/scripts/compare_prediction_models.py` | 25 | `Elo` | model | elo = load_json(DATA_DIR / "generated" / "predictions_elo.json") |
| `backend/scripts/compare_prediction_models.py` | 27 | `Elo` | model | elo_by_match = {prediction["match_id"]: prediction for prediction in elo} |
| `backend/scripts/compare_prediction_models.py` | 31 | `Elo` | model | raise ValueError("Baseline and Elo prediction match IDs differ") |
| `backend/scripts/explore_elo_ratings.py` | 1 | `Elo` | model | """Explore Elo Ratings through three controlled acquisition strategies.""" |
| `backend/scripts/explore_elo_ratings.py` | 51 | `Elo` | model | rendered_path = PROJECT_ROOT / "backend" / "data" / "raw" / "elo" / "samples" / "elo_rankings_rendered_table.json" |
| `backend/scripts/explore_elo_ratings.py` | 59 | `Elo` | model | "label": "Elo Ratings", |
| `backend/scripts/explore_elo_ratings.py` | 88 | `Elo` | model | raise SystemExit(f"Elo Ratings raw request failed: {exc}") from exc |
| `backend/scripts/explore_elo_ratings.py` | 91 | `Elo` | model | f"Elo Ratings exploration failed: {exc}. " |
| `backend/scripts/fetch_worldcup_api_football.py` | 40 | `force` | model | parser.add_argument("--force-refresh", action="store_true") |
| `backend/scripts/generate_predictions.py` | 1 | `Elo` | model | """Generate baseline and experimental Elo-adjusted predictions.""" |
| `backend/scripts/generate_predictions.py` | 159 | `Elo` | model | if model in {"elo", "both"}: |
| `backend/scripts/generate_predictions.py` | 160 | `Elo` | model | elo = [generate_elo_prediction(match, generated_at) for match in matches] |
| `backend/scripts/generate_predictions.py` | 161 | `Elo` | model | write_json(elo, DATA_DIR / "generated" / "predictions_elo.json") |
| `backend/scripts/generate_predictions.py` | 162 | `Elo` | model | print(f"Generated {len(elo)} experimental Elo predictions.") |
| `backend/scripts/generate_predictions.py` | 167 | `Elo` | model | parser.add_argument("--model", choices=("baseline", "elo", "both"), default="baseline") |
| `backend/scripts/normalize_api_football_worldcup.py` | 94 | `Elo` | data | "elo_rating": item.get("elo", {}).get("elo_rating"), |
| `backend/scripts/normalize_api_football_worldcup.py` | 95 | `Elo` | data | "elo_rank": item.get("elo", {}).get("rank"), |
| `backend/scripts/normalize_external_data.py` | 18 | `Elo` | data | ELO_SAMPLE = DATA_ROOT / "raw" / "elo" / "samples" / "elo_rankings_rendered_table.json" |
| `backend/scripts/normalize_external_data.py` | 92 | `Elo` | data | "source_type": "elo", |
| `backend/scripts/validate_team_mappings.py` | 23 | `Elo` | model | for field in ("team_id", "display_name", "country_code", "api_football", "elo", "mapping"): |
| `backend/scripts/validate_team_mappings.py` | 29 | `Elo` | model | ([team["elo"]["team_name"] for team in teams], "elo.team_name"), |
| `docs/ANGULAR_FRONTEND_NOTES.md` | 50 | `historique` | documentation | - 'PredictionHistoryComponent' affiche l'historique complet. |
| `docs/ANGULAR_MODELS.md` | 72 | `historique` | documentation | Pour afficher un historique reproductible, l'implémentation Angular pourra |
| `docs/ANGULAR_MODELS.md` | 104 | `historique` | documentation | \| 'PredictionHistoryComponent' \| Historique complet des validations et échecs \| |
| `docs/ANGULAR_MODELS.md` | 117 | `historique` | backtest | \| 'BacktestingService' \| Charger et filtrer l'historique des validations \| |
| `docs/API_FOOTBALL_ACTIVE_SOURCE.md` | 46 | `historique` | documentation | Les fixtures ne fournissant pas d'historique calibré, le baseline utilise des |
| `docs/API_FOOTBALL_ACTIVE_SOURCE.md` | 47 | `xG` | documentation | entrées xG neutres explicitement marquées comme valeurs prototype non |
| `docs/API_FOOTBALL_ACTIVE_SOURCE.md` | 48 | `Elo` | documentation | calibrées. Le modèle Elo parallèle utilise uniquement les ratings issus du |
| `docs/API_FOOTBALL_ACTIVE_SOURCE.md` | 54 | `Elo` | documentation | prédictions baseline/Elo et leur comparaison, puis copie les fichiers vers |
| `docs/API_FOOTBALL_ACTIVE_SOURCE.md` | 58 | `force` | documentation | les résumés de force Elo et l'audit de diversité des prédictions. Angular |
| `docs/API_FOOTBALL_ACTIVE_SOURCE.md` | 58 | `Elo` | documentation | les résumés de force Elo et l'audit de diversité des prédictions. Angular |
| `docs/BACKEND_MIGRATION_NOTES.md` | 37 | `xG` | documentation | - approxime les xG de base avec un mélange simple forme offensive/défensive ; |
| `docs/BACKEND_MIGRATION_NOTES.md` | 37 | `forme` | documentation | - approxime les xG de base avec un mélange simple forme offensive/défensive ; |
| `docs/BACKEND_MIGRATION_NOTES.md` | 65 | `xG` | documentation | - Les paramètres xG/Elo, 'rho', la confiance et 'max_goals=5' ne sont pas |
| `docs/BACKEND_MIGRATION_NOTES.md` | 65 | `Elo` | documentation | - Les paramètres xG/Elo, 'rho', la confiance et 'max_goals=5' ne sont pas |
| `docs/BACKEND_MIGRATION_NOTES.md` | 68 | `backtest` | backtest | - Le backtest d'exemple mesure la réalisation d'un marché, pas la calibration |
| `docs/BACKEND_MIGRATION_NOTES.md` | 68 | `calibration` | backtest | - Le backtest d'exemple mesure la réalisation d'un marché, pas la calibration |
| `docs/DATA_CONTRACTS.md` | 160 | `backtest` | backtest | ## Backtest result |
| `docs/DATA_CONTRACTS.md` | 184 | `historique` | documentation | filtrer les échecs hors de l'historique. |
| `docs/DATA_FOUNDATION.md` | 18 | `backtest` | backtest | \| 'backend/data/evaluated/' \| Résultats de backtest et mesures \| |
| `docs/DATA_FOUNDATION.md` | 46 | `backtest` | backtest | 3. exécute le backtest ; |
| `docs/DATA_SOURCE_DECISIONS.md` | 6 | `Elo` | documentation | \| Elo Ratings \| team strength \| tested via raw HTML + Playwright network + rendered DOM / usable with review \| TSV structurés découverts, 244 ratings normalisés, comparaison DOM possible \| source non contractuelle, mappi |
| `docs/DATA_SOURCE_DECISIONS.md` | 18 | `Elo` | documentation | - Préférer 'World.tsv' + 'en.teams.tsv' à l'extraction DOM pour Elo Ratings. |
| `docs/DATA_SOURCE_DECISIONS.md` | 19 | `Elo` | documentation | - Revalider manuellement la fraîcheur et le mapping Elo avant toute utilisation |
| `docs/DATA_SOURCE_DECISIONS.md` | 24 | `Elo` | documentation | - La couche d'identité API-Football vers Elo est obligatoire avant toute fusion |
| `docs/DATA_SOURCE_DECISIONS.md` | 30 | `Elo` | documentation | - Le mapping ne constitue pas une autorisation d'utiliser Elo dans le moteur : |
| `docs/DATA_SOURCE_DECISIONS.md` | 33 | `Elo` | documentation | ## Décision V0.4 — Elo Model Experiment |
| `docs/DATA_SOURCE_DECISIONS.md` | 36 | `Elo` | documentation | - Autoriser un modèle Elo séparé uniquement pour mesurer des deltas. |
| `docs/DATA_SOURCE_DECISIONS.md` | 38 | `Elo` | documentation | - Appliquer un poids modéré de '0.20' et plafonner le facteur Elo à '±0.35'. |
| `docs/DATA_SOURCE_DECISIONS.md` | 39 | `expected goals` | documentation | - Retomber exactement sur les expected goals baseline si un rating manque. |
| `docs/DATA_SOURCE_DECISIONS.md` | 49 | `Elo` | documentation | - Continuer à publier baseline, Elo et comparaison dans des snapshots séparés. |
| `docs/ELO_MODEL_EXPERIMENT.md` | 1 | `Elo` | documentation | # Elo Model Experiment V0.4 |
| `docs/ELO_MODEL_EXPERIMENT.md` | 5 | `Elo` | documentation | V0.4 mesure l'impact de ratings Elo validés sur les prédictions baseline. Le |
| `docs/ELO_MODEL_EXPERIMENT.md` | 6 | `Elo` | documentation | modèle Elo est expérimental : il ne remplace ni 'predictions.json', ni le |
| `docs/ELO_MODEL_EXPERIMENT.md` | 13 | `Elo` | documentation | équipes Elo. Un rating absent n'est jamais inventé : si une équipe ne possède |
| `docs/ELO_MODEL_EXPERIMENT.md` | 14 | `expected goals` | documentation | pas de mapping validé, la prédiction Elo reprend exactement les expected goals |
| `docs/ELO_MODEL_EXPERIMENT.md` | 14 | `Elo` | documentation | pas de mapping validé, la prédiction Elo reprend exactement les expected goals |
| `docs/ELO_MODEL_EXPERIMENT.md` | 19 | `expected goals` | documentation | Le baseline calcule d'abord ses expected goals selon sa logique existante. |
| `docs/ELO_MODEL_EXPERIMENT.md` | 35 | `Elo` | documentation | - 'predictions_elo.json' : modèle Elo expérimental ; |
| `docs/ELO_MODEL_EXPERIMENT.md` | 36 | `Elo` | documentation | - 'model_comparison.json' : deltas baseline vers Elo par match ; |
| `docs/IGNORED_REQUIREMENTS.md` | 105 | `historique` | documentation | le détail d'un match, la matrice, les marchés et l'historique. |
| `docs/MANUAL_VALIDATION_CHECKLISTS.md` | 157 | `historique` | documentation | * [ ] l'historique affiche les validations ET les échecs. |
| `docs/MANUAL_VALIDATION_CHECKLISTS.md` | 202 | `Elo` | documentation | - [ ] Elo Ratings est testé. |
| `docs/MANUAL_VALIDATION_CHECKLISTS.md` | 203 | `Elo` | documentation | - [ ] parsing Elo possible ou non est documenté. |
| `docs/MANUAL_VALIDATION_CHECKLISTS.md` | 214 | `Elo` | documentation | - [ ] les limites du plan et du parsing Elo sont comprises. |
| `docs/MANUAL_VALIDATION_CHECKLISTS.md` | 226 | `Elo` | documentation | - [ ] la couverture API-Football vers Elo est affichée. |
| `docs/MANUAL_VALIDATION_CHECKLISTS.md` | 229 | `Elo` | documentation | - [ ] chaque équipe mappée possède un identifiant API, un nom Elo et un code pays. |
| `docs/MANUAL_VALIDATION_CHECKLISTS.md` | 230 | `Elo` | documentation | - [ ] aucun identifiant API, 'team_id' ou nom Elo n'est dupliqué. |
| `docs/MANUAL_VALIDATION_CHECKLISTS.md` | 243 | `Elo` | documentation | - [ ] l'encart “API-Football ↔ Elo Ratings” affiche les bons compteurs. |
| `docs/MANUAL_VALIDATION_CHECKLISTS.md` | 245 | `Elo` | documentation | - [ ] le frontend indique qu'Elo n'est pas connecté au moteur de prédiction. |
| `docs/MANUAL_VALIDATION_CHECKLISTS.md` | 261 | `Elo` | documentation | ## Checklist V0.4 — Elo Model Experiment |
| `docs/MANUAL_VALIDATION_CHECKLISTS.md` | 265 | `Elo` | documentation | - [ ] Le modèle Elo génère un fichier séparé. |
| `docs/MANUAL_VALIDATION_CHECKLISTS.md` | 271 | `Elo` | documentation | - [ ] Les matchs sans Elo fallback correctement. |
| `docs/MANUAL_VALIDATION_CHECKLISTS.md` | 272 | `Elo` | documentation | - [ ] Angular affiche clairement que le modèle Elo est expérimental. |
| `docs/MANUAL_VALIDATION_CHECKLISTS.md` | 306 | `Elo` | documentation | - [ ] la modale distingue clairement baseline et variation Elo. |
| `docs/MANUAL_VALIDATION_CHECKLISTS.md` | 361 | `Elo` | documentation | - [ ] Elo predictions générées. |
| `docs/PREDICTION_ENGINE_AUDIT_V0_5.md` | 7 | `Elo` | documentation | - Elo top-score distribution: '{'1-1': 72}' |
| `docs/PREDICTION_ENGINE_AUDIT_V0_5.md` | 9 | `Elo` | documentation | - Elo 1-1 rate: '100.0%' |
| `docs/PREDICTION_ENGINE_AUDIT_V0_5.md` | 10 | `Elo` | documentation | - Top scores changed by Elo: '0' |
| `docs/PREDICTION_ENGINE_AUDIT_V0_5.md` | 11 | `Elo` | documentation | - Elo unavailable: '0' |
| `docs/PREDICTION_ENGINE_AUDIT_V0_5.md` | 16 | `expected goals` | documentation | Predictions are highly concentrated on 1-1 because every real fixture currently receives the same neutral baseline expected goals. Elo adjusts markets but does not change the modal score. |
| `docs/PREDICTION_ENGINE_AUDIT_V0_5.md` | 16 | `Elo` | documentation | Predictions are highly concentrated on 1-1 because every real fixture currently receives the same neutral baseline expected goals. Elo adjusts markets but does not change the modal score. |
| `docs/PREDICTION_ENGINE_AUDIT_V0_5.md` | 18 | `Elo` | documentation | This is not a sorting bug or a missing-Elo fallback. The active real-data |
| `docs/PREDICTION_ENGINE_AUDIT_V0_5.md` | 19 | `expected goals` | documentation | baseline assigns neutral '1.35 / 1.35' expected goals to every fixture because |
| `docs/PREDICTION_ENGINE_AUDIT_V0_5.md` | 20 | `Elo` | documentation | validated historical team features are not yet available. The moderate Elo |
| `docs/PREDICTION_ENGINE_AUDIT_V0_5.md` | 25 | `force` | documentation | Do not force diversity and do not present these predictions as calibrated. |
| `docs/PROJECT_START_REPORT.md` | 11 | `xG` | documentation | calcul de lambdas xG/Elo, la génération d'une matrice de scores, la déduction des |
| `docs/PROJECT_START_REPORT.md` | 11 | `Elo` | documentation | calcul de lambdas xG/Elo, la génération d'une matrice de scores, la déduction des |
| `docs/PROJECT_START_REPORT.md` | 39 | `xG` | documentation | calcul de lambdas modulés par xG/Elo et baselines glissantes. |
| `docs/PROJECT_START_REPORT.md` | 39 | `Elo` | documentation | calcul de lambdas modulés par xG/Elo et baselines glissantes. |
| `docs/PROJECT_START_REPORT.md` | 41 | `Dixon-Coles` | documentation | matrice Poisson, correction Dixon-Coles, normalisation et top scores. |
| `docs/PROJECT_START_REPORT.md` | 41 | `Dixon` | documentation | matrice Poisson, correction Dixon-Coles, normalisation et top scores. |
| `docs/PROJECT_START_REPORT.md` | 41 | `Poisson` | documentation | matrice Poisson, correction Dixon-Coles, normalisation et top scores. |
| `docs/PROJECT_START_REPORT.md` | 53 | `Dixon-Coles` | documentation | - 'drc-prototype/optimizer.py' contenait les formules xG/Elo, Poisson/Dixon-Coles et |
| `docs/PROJECT_START_REPORT.md` | 53 | `Dixon` | documentation | - 'drc-prototype/optimizer.py' contenait les formules xG/Elo, Poisson/Dixon-Coles et |
| `docs/PROJECT_START_REPORT.md` | 53 | `Poisson` | documentation | - 'drc-prototype/optimizer.py' contenait les formules xG/Elo, Poisson/Dixon-Coles et |
| `docs/PROJECT_START_REPORT.md` | 53 | `xG` | documentation | - 'drc-prototype/optimizer.py' contenait les formules xG/Elo, Poisson/Dixon-Coles et |
| `docs/PROJECT_START_REPORT.md` | 53 | `Elo` | documentation | - 'drc-prototype/optimizer.py' contenait les formules xG/Elo, Poisson/Dixon-Coles et |
| `docs/PROJECT_START_REPORT.md` | 55 | `xG` | backtest | - 'drc-prototype/xg-backtest.js' contenait la baseline glissante et le backtest chronologique. |
| `docs/PROJECT_START_REPORT.md` | 55 | `backtest` | backtest | - 'drc-prototype/xg-backtest.js' contenait la baseline glissante et le backtest chronologique. |
| `docs/PROJECT_START_REPORT.md` | 56 | `backtest` | backtest | - 'drc-prototype/backtest.js' contenait un historique détaillé de validations. |
| `docs/PROJECT_START_REPORT.md` | 56 | `historique` | backtest | - 'drc-prototype/backtest.js' contenait un historique détaillé de validations. |
| `docs/PROJECT_START_REPORT.md` | 57 | `historique` | documentation | - 'drc-prototype/history_*.json' utilisait le format fournisseur historique et des données de |
| `docs/PROJECT_START_REPORT.md` | 68 | `xG` | documentation | \| Calcul xG/Elo \| Oui \| Élevée \| Calibration sélections et terrain neutre \| |
| `docs/PROJECT_START_REPORT.md` | 68 | `calibration` | documentation | \| Calcul xG/Elo \| Oui \| Élevée \| Calibration sélections et terrain neutre \| |
| `docs/PROJECT_START_REPORT.md` | 68 | `Elo` | documentation | \| Calcul xG/Elo \| Oui \| Élevée \| Calibration sélections et terrain neutre \| |
| `docs/PROJECT_START_REPORT.md` | 74 | `historique` | backtest | \| Backtesting de marchés \| Oui, minimal \| Moyenne \| Historique versionné, résultat réel et métriques \| |
| `docs/PROJECT_START_REPORT.md` | 85 | `xG` | documentation | 1. construction de xG de base à partir d'historiques glissants ; |
| `docs/PROJECT_START_REPORT.md` | 86 | `Elo` | documentation | 2. modulation par différence Elo ; |
| `docs/PROJECT_START_REPORT.md` | 87 | `Dixon-Coles` | documentation | 3. génération Poisson avec correction Dixon-Coles ; |
| `docs/PROJECT_START_REPORT.md` | 87 | `Dixon` | documentation | 3. génération Poisson avec correction Dixon-Coles ; |
| `docs/PROJECT_START_REPORT.md` | 87 | `Poisson` | documentation | 3. génération Poisson avec correction Dixon-Coles ; |
| `docs/PROJECT_START_REPORT.md` | 136 | `calibration` | documentation | - les métriques de calibration comme Brier score et log loss. |
| `docs/PROJECT_START_REPORT.md` | 136 | `log loss` | metric | - les métriques de calibration comme Brier score et log loss. |
| `docs/PROJECT_START_REPORT.md` | 136 | `Brier` | metric | - les métriques de calibration comme Brier score et log loss. |
| `docs/PROJECT_START_REPORT.md` | 138 | `historique` | documentation | Elle doit donc être enrichie avant de servir d'historique fiable. Les réussites |
| `docs/PROJECT_START_REPORT.md` | 143 | `historique` | documentation | - Historique fournisseur : blocs 'fixture', 'league', 'teams', 'goals' et |
| `docs/PROJECT_START_REPORT.md` | 158 | `backtest` | backtest | - validation simple d'un backtest. |
| `docs/PROJECT_START_REPORT.md` | 175 | `calibration` | documentation | - calibration sur matchs internationaux ; |
| `docs/PROJECT_START_REPORT.md` | 177 | `historique` | backtest | - stockage de l'historique de backtesting complet ; |
| `docs/PROJECT_START_REPORT.md` | 187 | `backtest` | backtest | prédiction ou un backtest. |
| `docs/PROJECT_START_REPORT.md` | 188 | `calibration` | documentation | - Mauvaise calibration en réutilisant des paramètres de championnats de clubs. |
| `docs/PROJECT_START_REPORT.md` | 202 | `xG` | documentation | │ ├── prediction/ # xG/Elo et orchestration |
| `docs/PROJECT_START_REPORT.md` | 202 | `Elo` | documentation | │ ├── prediction/ # xG/Elo et orchestration |
| `docs/PROJECT_START_REPORT.md` | 205 | `historique` | backtest | │ ├── backtesting/ # Évaluation et historique |
| `docs/PROJECT_START_REPORT.md` | 219 | `xG` | documentation | 2. Calibrer les entrées xG/Elo et la méthode de confiance. |
| `docs/PROJECT_START_REPORT.md` | 219 | `Elo` | documentation | 2. Calibrer les entrées xG/Elo et la méthode de confiance. |
| `docs/PROTOTYPE_ENGINE_STATUS.md` | 10 | `expected goals` | documentation | - des expected goals à partir d'entrées simples ; |
| `docs/PROTOTYPE_ENGINE_STATUS.md` | 11 | `Dixon-Coles` | documentation | - une matrice de scores Poisson/Dixon-Coles ; |
| `docs/PROTOTYPE_ENGINE_STATUS.md` | 11 | `Dixon` | documentation | - une matrice de scores Poisson/Dixon-Coles ; |
| `docs/PROTOTYPE_ENGINE_STATUS.md` | 11 | `Poisson` | documentation | - une matrice de scores Poisson/Dixon-Coles ; |
| `docs/PROTOTYPE_ENGINE_STATUS.md` | 13 | `Elo` | documentation | - une variante Elo expérimentale et une comparaison avec le baseline. |
| `docs/PROTOTYPE_ENGINE_STATUS.md` | 23 | `Elo` | documentation | fixtures, et que la variante Elo ne change aucun de ces scores modaux. Cette |
| `docs/PROTOTYPE_ENGINE_STATUS.md` | 24 | `xG` | documentation | uniformité vient des xG neutres '1.35 / 1.35', pas d'un bug de tri ou d'une |
| `docs/PROTOTYPE_ENGINE_STATUS.md` | 25 | `Elo` | documentation | absence de ratings Elo. Elle est affichée dans l'interface et ne doit pas être |
| `docs/PROTOTYPE_ENGINE_STATUS.md` | 28 | `historique` | documentation | Il ne réalise ni simulation de tournoi, ni apprentissage historique, ni |
| `docs/PROTOTYPE_ENGINE_STATUS.md` | 52 | `historique` | documentation | historique international chronologique avant de reconstruire un |
| `docs/PROTOTYPE_ENGINE_STATUS.md` | 53 | `Dixon-Coles` | documentation | Poisson/Dixon-Coles calibré. Voir 'docs/CURRENT_ENGINE_AUDIT.md', |
| `docs/PROTOTYPE_ENGINE_STATUS.md` | 53 | `Dixon` | documentation | Poisson/Dixon-Coles calibré. Voir 'docs/CURRENT_ENGINE_AUDIT.md', |
| `docs/PROTOTYPE_ENGINE_STATUS.md` | 53 | `Poisson` | documentation | Poisson/Dixon-Coles calibré. Voir 'docs/CURRENT_ENGINE_AUDIT.md', |
| `docs/REAL_DATA_ACQUISITION_REPORT.md` | 13 | `forme` | documentation | - clé configurée : oui, affichée uniquement sous forme masquée ; |
| `docs/REAL_DATA_ACQUISITION_REPORT.md` | 59 | `historique` | documentation | comparaison et historique direct ; |
| `docs/REAL_DATA_ACQUISITION_REPORT.md` | 70 | `Elo` | documentation | ### Elo Ratings |
| `docs/REAL_DATA_ACQUISITION_REPORT.md` | 76 | `Elo` | documentation | - mapping nécessaire : nom Elo vers code et identifiant équipe API-Football ; |
| `docs/REAL_DATA_ACQUISITION_REPORT.md` | 82 | `Elo` | documentation | ## Elo Ratings raw acquisition |
| `docs/REAL_DATA_ACQUISITION_REPORT.md` | 113 | `forme` | documentation | utilise une forme longue dans le TSV et une forme courte dans le DOM ; |
| `docs/REAL_DATA_ACQUISITION_REPORT.md` | 114 | `Elo` | documentation | - limitations: pas de contrat d'API documenté, codes Elo à mapper vers |
| `docs/REAL_DATA_ACQUISITION_REPORT.md` | 119 | `Elo` | documentation | Utiliser les TSV Elo uniquement comme source expérimentale parallèle. Préférer |
| `docs/REAL_DATA_ACQUISITION_REPORT.md` | 125 | `Elo` | documentation | - 'international-football.net' affiche un tableau basé sur Elo Ratings ; |
| `docs/REAL_DATA_ACQUISITION_REPORT.md` | 127 | `Elo` | documentation | - un Elo interne pourrait être recalculé depuis les résultats historiques |
| `docs/REAL_DATA_ACQUISITION_REPORT.md` | 142 | `Elo` | documentation | Elo rating |
| `docs/REAL_DATA_ACQUISITION_REPORT.md` | 159 | `Elo` | documentation | - valider un mapping d'équipes avant toute fusion avec une source Elo ; |
| `docs/REAL_DATA_ACQUISITION_REPORT.md` | 161 | `Elo` | documentation | - conserver Elo comme source expérimentale parallèle fondée sur les TSV. |
| `docs/REAL_DATA_ACQUISITION_REPORT.md` | 173 | `Elo` | documentation | ratings Elo sans modifier le pipeline principal. |
| `docs/REAL_DATA_ACQUISITION_REPORT.md` | 179 | `Elo` | documentation | - entrées Elo hors périmètre API-Football actuel : '196' ; |
| `docs/REPO_STRUCTURE_NOTES.md` | 32 | `historique` | documentation | avait perdu ses fichiers de travail après une réécriture d'historique, mais son |
| `docs/REPO_STRUCTURE_NOTES.md` | 38 | `historique` | documentation | Python ou le virtualenv historique. |
| `docs/TEAM_MAPPING_GUIDE.md` | 5 | `Elo` | documentation | La couche V0.3.1 relie les équipes normalisées API-Football aux libellés Elo |
| `docs/TEAM_MAPPING_GUIDE.md` | 6 | `Elo` | documentation | Ratings et à un code pays interne. Elle ne branche pas les ratings Elo au |
| `docs/TEAM_MAPPING_GUIDE.md` | 40 | `Elo` | documentation | et le rating Elo, puis le statut, la méthode, la confiance et le besoin de |
| `docs/TEAM_MAPPING_GUIDE.md` | 41 | `Elo` | documentation | revue. 'unmapped_teams.json' sépare les équipes API non résolues des entrées Elo |
| `docs/TEAM_MAPPING_GUIDE.md` | 46 | `Elo` | documentation | \| API-Football \| Elo Ratings \| |
| `docs/TEAM_MAPPING_GUIDE.md` | 83 | `Elo` | documentation | - [ ] aucun doublon de 'team_id', identifiant API ou nom Elo ; |
| `docs/TEAM_MAPPING_GUIDE.md` | 87 | `Elo` | documentation | - [ ] Elo reste non connecté au moteur de prédiction. |
| `docs/TEAM_MAPPING_GUIDE.md` | 96 | `Elo` | documentation | - [ ] Les ratings Elo semblent associés à la bonne équipe. |
| `docs/VALIDATION_LOG.md` | 61 | `Elo` | documentation | Commit: '8254b2b Add team identity mapping for API-Football and Elo' |
| `docs/VALIDATION_LOG.md` | 73 | `Elo` | documentation | - [x] Elo teams count checked |
| `docs/VALIDATION_LOG.md` | 86 | `Elo` | documentation | Elo teams: 244 |
| `docs/VALIDATION_LOG.md` | 100 | `Elo` | documentation | 1. API-Football: Czech Republic → Elo: Czechia \| code: CZE \| method: alias \| confidence: 0.98 \| Elo: 1740, rank: 35 |
| `docs/VALIDATION_LOG.md` | 101 | `Elo` | documentation | 2. API-Football: Türkiye → Elo: Turkey \| code: TUR \| method: alias \| confidence: 0.98 \| Elo: 1911, rank: 13 |
| `docs/VALIDATION_LOG.md` | 102 | `Elo` | documentation | 3. API-Football: Bosnia & Herzegovina → Elo: Bosnia and Herzegovina \| code: BIH \| method: alias \| confidence: 0.98 \| Elo: 1595, rank: 65 |
| `docs/VALIDATION_LOG.md` | 103 | `Elo` | documentation | 4. API-Football: Congo DR → Elo: DR Congo \| code: CGO \| method: alias \| confidence: 0.98 \| Elo: 1652, rank: 55 |
| `docs/VALIDATION_LOG.md` | 104 | `Elo` | documentation | 5. API-Football: Cape Verde Islands → Elo: Cape Verde \| code: CPV \| method: alias \| confidence: 0.98 \| Elo: 1578, rank: 68 |
| `docs/VALIDATION_LOG.md` | 105 | `Elo` | documentation | 6. API-Football: USA → Elo: United States \| code: USA \| method: alias \| confidence: 0.98 \| Elo: 1726, rank: 38 |
| `docs/VALIDATION_LOG.md` | 112 | `Elo` | documentation | - [ ] Elo ratings association checked |
| `docs/VALIDATION_LOG.md` | 138 | `Elo` | documentation | Manual validation still requires human review before integrating Elo into the |
| `docs/VALIDATION_LOG.md` | 145 | `Elo` | documentation | ## V0.4 — Elo Model Experiment |
| `docs/VALIDATION_LOG.md` | 149 | `Elo` | documentation | Commit: '08a0a08 Add experimental Elo-adjusted prediction model' |
| `docs/VALIDATION_LOG.md` | 155 | `Elo` | documentation | - [x] Elo predictions available |
| `docs/VALIDATION_LOG.md` | 158 | `Elo` | documentation | - [x] Elo remains experimental |
| `docs/VALIDATION_LOG.md` | 164 | `expected goals` | documentation | - [x] Missing Elo rating falls back exactly to baseline expected goals |
| `docs/VALIDATION_LOG.md` | 164 | `Elo` | documentation | - [x] Missing Elo rating falls back exactly to baseline expected goals |
| `docs/VALIDATION_LOG.md` | 177 | `Elo` | documentation | Elo available: 3/3 |
| `docs/VALIDATION_LOG.md` | 183 | `Elo` | documentation | Elo weight: 0.20 |
| `docs/VALIDATION_LOG.md` | 184 | `Elo` | documentation | Elo factor clamp: ±0.35 |
| `docs/VALIDATION_LOG.md` | 194 | `Elo` | documentation | - [x] Top scores baseline vs Elo checked |
| `docs/VALIDATION_LOG.md` | 195 | `Elo` | documentation | - [x] Elo ratings association checked |
| `docs/VALIDATION_LOG.md` | 203 | `Elo` | documentation | - Elo: 2063 vs 1860 |
| `docs/VALIDATION_LOG.md` | 205 | `Elo` | documentation | - Top score Elo: 2-0 |
| `docs/VALIDATION_LOG.md` | 210 | `Elo` | documentation | - Elo: 1991 vs 1906 |
| `docs/VALIDATION_LOG.md` | 212 | `Elo` | documentation | - Top score Elo: 2-0 |
| `docs/VALIDATION_LOG.md` | 217 | `Elo` | documentation | - Elo: 1788 vs 1827 |
| `docs/VALIDATION_LOG.md` | 219 | `Elo` | documentation | - Top score Elo: 1-1 |
| `docs/VALIDATION_LOG.md` | 232 | `Elo` | documentation | Human review completed. Elo impact is moderate and coherent for the current |
| `docs/VALIDATION_LOG.md` | 233 | `Elo` | documentation | V0.4 experiment. The baseline model remains preserved, and Elo is accepted as |
| `docs/VALIDATION_LOG.md` | 238 | `Elo` | documentation | - Keep Elo marked as experimental. |
| `docs/VALIDATION_LOG.md` | 239 | `Elo` | backtest | - Do not make Elo the default model without additional backtesting. |
| `docs/VALIDATION_LOG.md` | 240 | `Elo` | documentation | - Future phases must compare predictive quality before promoting Elo. |
| `docs/VALIDATION_LOG.md` | 252 | `Elo` | documentation | - [x] Baseline and Elo prototype predictions generated |
| `docs/VALIDATION_LOG.md` | 270 | `Elo` | documentation | - [ ] Baseline/Elo predictions and comparison checked |
| `docs/VALIDATION_LOG.md` | 281 | `Elo` | documentation | baseline predictions, '72' Elo predictions and '72' model comparisons. |
| `docs/VALIDATION_LOG.md` | 300 | `Elo` | documentation | - [x] 72 baseline and 72 Elo modal scores honestly reported as '1-1' |
| `handoff_worldcup_2026/ARCHITECTURE_NOTES.md` | 25 | `xG` | backtest | 'optimizer.py' est retenu comme référence des formules car ses fonctions sont explicites et son objectif de log loss est méthodologiquement plus solide. 'xg-backtest.js' est retenu pour la fenêtre glissante et l'ordre ch |
| `handoff_worldcup_2026/ARCHITECTURE_NOTES.md` | 25 | `backtest` | backtest | 'optimizer.py' est retenu comme référence des formules car ses fonctions sont explicites et son objectif de log loss est méthodologiquement plus solide. 'xg-backtest.js' est retenu pour la fenêtre glissante et l'ordre ch |
| `handoff_worldcup_2026/ARCHITECTURE_NOTES.md` | 25 | `log loss` | backtest | 'optimizer.py' est retenu comme référence des formules car ses fonctions sont explicites et son objectif de log loss est méthodologiquement plus solide. 'xg-backtest.js' est retenu pour la fenêtre glissante et l'ordre ch |
| `handoff_worldcup_2026/DATA_FORMATS.md` | 89 | `historique` | documentation | ## Format fournisseur historique observé |
| `handoff_worldcup_2026/EXTRACTION_REPORT.md` | 5 | `Dixon` | documentation | Le projet historique contient une chaîne football exploitable mais fortement couplée à des scripts ponctuels : ingestion API-Football, enrichissement des rencontres avec statistiques/xG, historique Elo, calcul de lambdas |
| `handoff_worldcup_2026/EXTRACTION_REPORT.md` | 5 | `Poisson` | documentation | Le projet historique contient une chaîne football exploitable mais fortement couplée à des scripts ponctuels : ingestion API-Football, enrichissement des rencontres avec statistiques/xG, historique Elo, calcul de lambdas |
| `handoff_worldcup_2026/EXTRACTION_REPORT.md` | 5 | `xG` | documentation | Le projet historique contient une chaîne football exploitable mais fortement couplée à des scripts ponctuels : ingestion API-Football, enrichissement des rencontres avec statistiques/xG, historique Elo, calcul de lambdas |
| `handoff_worldcup_2026/EXTRACTION_REPORT.md` | 5 | `backtest` | backtest | Le projet historique contient une chaîne football exploitable mais fortement couplée à des scripts ponctuels : ingestion API-Football, enrichissement des rencontres avec statistiques/xG, historique Elo, calcul de lambdas |
| `handoff_worldcup_2026/EXTRACTION_REPORT.md` | 5 | `attaque` | documentation | Le projet historique contient une chaîne football exploitable mais fortement couplée à des scripts ponctuels : ingestion API-Football, enrichissement des rencontres avec statistiques/xG, historique Elo, calcul de lambdas |
| `handoff_worldcup_2026/EXTRACTION_REPORT.md` | 5 | `défense` | documentation | Le projet historique contient une chaîne football exploitable mais fortement couplée à des scripts ponctuels : ingestion API-Football, enrichissement des rencontres avec statistiques/xG, historique Elo, calcul de lambdas |
| `handoff_worldcup_2026/EXTRACTION_REPORT.md` | 5 | `historique` | documentation | Le projet historique contient une chaîne football exploitable mais fortement couplée à des scripts ponctuels : ingestion API-Football, enrichissement des rencontres avec statistiques/xG, historique Elo, calcul de lambdas |
| `handoff_worldcup_2026/EXTRACTION_REPORT.md` | 5 | `Elo` | documentation | Le projet historique contient une chaîne football exploitable mais fortement couplée à des scripts ponctuels : ingestion API-Football, enrichissement des rencontres avec statistiques/xG, historique Elo, calcul de lambdas |
| `handoff_worldcup_2026/EXTRACTION_REPORT.md` | 11 | `historique` | documentation | \| Composant \| Source historique \| Destination \| Réutilisabilité \| |
| `handoff_worldcup_2026/EXTRACTION_REPORT.md` | 13 | `xG` | backtest | \| Probabilité Elo et lambdas xG/Elo \| 'drc-prototype/optimizer.py', 'drc-prototype/xg-backtest.js' \| 'recycled_code/score_prediction/expected_goals.py' \| Élevée après calibration \| |
| `handoff_worldcup_2026/EXTRACTION_REPORT.md` | 13 | `backtest` | backtest | \| Probabilité Elo et lambdas xG/Elo \| 'drc-prototype/optimizer.py', 'drc-prototype/xg-backtest.js' \| 'recycled_code/score_prediction/expected_goals.py' \| Élevée après calibration \| |
| `handoff_worldcup_2026/EXTRACTION_REPORT.md` | 13 | `calibration` | backtest | \| Probabilité Elo et lambdas xG/Elo \| 'drc-prototype/optimizer.py', 'drc-prototype/xg-backtest.js' \| 'recycled_code/score_prediction/expected_goals.py' \| Élevée après calibration \| |
| `handoff_worldcup_2026/EXTRACTION_REPORT.md` | 13 | `Elo` | backtest | \| Probabilité Elo et lambdas xG/Elo \| 'drc-prototype/optimizer.py', 'drc-prototype/xg-backtest.js' \| 'recycled_code/score_prediction/expected_goals.py' \| Élevée après calibration \| |
| `handoff_worldcup_2026/EXTRACTION_REPORT.md` | 14 | `Dixon` | documentation | \| Poisson et Dixon–Coles \| mêmes sources \| 'recycled_code/score_matrix/score_matrix.py' \| Élevée \| |
| `handoff_worldcup_2026/EXTRACTION_REPORT.md` | 14 | `Poisson` | documentation | \| Poisson et Dixon–Coles \| mêmes sources \| 'recycled_code/score_matrix/score_matrix.py' \| Élevée \| |
| `handoff_worldcup_2026/EXTRACTION_REPORT.md` | 15 | `xG` | backtest | \| Baseline xG glissante \| 'drc-prototype/xg-backtest.js' \| 'recycled_code/score_prediction/expected_goals.py' \| Moyenne à élevée \| |
| `handoff_worldcup_2026/EXTRACTION_REPORT.md` | 15 | `backtest` | backtest | \| Baseline xG glissante \| 'drc-prototype/xg-backtest.js' \| 'recycled_code/score_prediction/expected_goals.py' \| Moyenne à élevée \| |
| `handoff_worldcup_2026/EXTRACTION_REPORT.md` | 16 | `xG` | backtest | \| Backtest chronologique / validation \| 'drc-prototype/xg-backtest.js', 'drc-prototype/backtest.js', 'drc-prototype/optimizer.py' \| 'recycled_code/backtesting/backtester.py' \| Moyenne \| |
| `handoff_worldcup_2026/EXTRACTION_REPORT.md` | 16 | `backtest` | backtest | \| Backtest chronologique / validation \| 'drc-prototype/xg-backtest.js', 'drc-prototype/backtest.js', 'drc-prototype/optimizer.py' \| 'recycled_code/backtesting/backtester.py' \| Moyenne \| |
| `handoff_worldcup_2026/EXTRACTION_REPORT.md` | 22 | `xG` | backtest | - Les interfaces HTML/serveurs de 'backtest.js', 'xg-backtest.js' et '3_scanner.js' : présentation couplée aux scripts, non nécessaire au moteur. |
| `handoff_worldcup_2026/EXTRACTION_REPORT.md` | 22 | `backtest` | backtest | - Les interfaces HTML/serveurs de 'backtest.js', 'xg-backtest.js' et '3_scanner.js' : présentation couplée aux scripts, non nécessaire au moteur. |
| `handoff_worldcup_2026/EXTRACTION_REPORT.md` | 26 | `Elo` | documentation | - Les historiques JSON, archives Elo, résultats et fichiers de paris : volumineux, spécifiques aux ligues, non nécessaires au bundle et susceptibles de contenir des données non redistribuables. |
| `handoff_worldcup_2026/EXTRACTION_REPORT.md` | 38 | `optuna` | dependency | - Reproduction facultative de l'optimiseur historique : 'numpy', 'scipy', 'optuna' et un dataset chronologique propre. |
| `handoff_worldcup_2026/EXTRACTION_REPORT.md` | 38 | `scipy` | dependency | - Reproduction facultative de l'optimiseur historique : 'numpy', 'scipy', 'optuna' et un dataset chronologique propre. |
| `handoff_worldcup_2026/EXTRACTION_REPORT.md` | 38 | `numpy` | dependency | - Reproduction facultative de l'optimiseur historique : 'numpy', 'scipy', 'optuna' et un dataset chronologique propre. |
| `handoff_worldcup_2026/EXTRACTION_REPORT.md` | 38 | `historique` | documentation | - Reproduction facultative de l'optimiseur historique : 'numpy', 'scipy', 'optuna' et un dataset chronologique propre. |
| `handoff_worldcup_2026/EXTRACTION_REPORT.md` | 44 | `Dixon` | documentation | - Dixon–Coles peut produire des probabilités négatives avec un 'rho' inadapté; le générateur lève alors une erreur. |
| `handoff_worldcup_2026/EXTRACTION_REPORT.md` | 45 | `calibration` | documentation | - La Coupe du Monde comporte peu de données récentes par sélection, des terrains neutres, prolongations et tirs au but : la calibration de ligue ne peut pas être reprise telle quelle. |
| `handoff_worldcup_2026/EXTRACTION_REPORT.md` | 47 | `historique` | documentation | - Les formats API-Football sont documentés comme source historique, mais doivent être placés derrière un adaptateur fournisseur. |
| `handoff_worldcup_2026/EXTRACTION_REPORT.md` | 52 | `calibration` | documentation | 2. Utiliser la matrice et les marchés tels quels pour un premier prototype, puis tester calibration et sensibilité à 'max_goals'/'rho'. |
| `handoff_worldcup_2026/EXTRACTION_REPORT.md` | 56 | `calibration` | documentation | 6. Ajouter Brier score, log loss, calibration par bucket et suivi par version de modèle. |
| `handoff_worldcup_2026/EXTRACTION_REPORT.md` | 56 | `log loss` | metric | 6. Ajouter Brier score, log loss, calibration par bucket et suivi par version de modèle. |
| `handoff_worldcup_2026/EXTRACTION_REPORT.md` | 56 | `Brier` | metric | 6. Ajouter Brier score, log loss, calibration par bucket et suivi par version de modèle. |
| `handoff_worldcup_2026/LIMITATIONS.md` | 3 | `calibration` | documentation | - **Calibration :** aucune valeur par défaut n'est revendiquée comme calibrée pour les sélections nationales ou la Coupe du Monde 2026. |
| `handoff_worldcup_2026/LIMITATIONS.md` | 5 | `Dixon` | documentation | - **Matrice :** Poisson suppose une structure simple; Dixon–Coles ne corrige que les faibles scores. La renormalisation masque la queue au-delà de 'max_goals'. |
| `handoff_worldcup_2026/LIMITATIONS.md` | 5 | `Poisson` | documentation | - **Matrice :** Poisson suppose une structure simple; Dixon–Coles ne corrige que les faibles scores. La renormalisation masque la queue au-delà de 'max_goals'. |
| `handoff_worldcup_2026/LIMITATIONS.md` | 7 | `calibration` | backtest | - **Backtesting :** le module minimal mesure des validations de signaux, mais pas la calibration, le Brier score, la log loss, le ROI ou les intervalles de confiance. |
| `handoff_worldcup_2026/LIMITATIONS.md` | 7 | `log loss` | backtest | - **Backtesting :** le module minimal mesure des validations de signaux, mais pas la calibration, le Brier score, la log loss, le ROI ou les intervalles de confiance. |
| `handoff_worldcup_2026/LIMITATIONS.md` | 7 | `Brier` | backtest | - **Backtesting :** le module minimal mesure des validations de signaux, mais pas la calibration, le Brier score, la log loss, le ROI ou les intervalles de confiance. |
| `handoff_worldcup_2026/NEXT_PROJECT_INTEGRATION_GUIDE.md` | 34 | `backtest` | backtest | ## Lancer un backtest |
| `handoff_worldcup_2026/NEXT_PROJECT_INTEGRATION_GUIDE.md` | 50 | `optuna` | dependency | Le runtime actuel utilise uniquement Python standard. 'pytest' sert aux tests. NumPy/SciPy/Optuna ne sont nécessaires que si l'optimiseur historique est reconstruit. |
| `handoff_worldcup_2026/NEXT_PROJECT_INTEGRATION_GUIDE.md` | 50 | `scipy` | dependency | Le runtime actuel utilise uniquement Python standard. 'pytest' sert aux tests. NumPy/SciPy/Optuna ne sont nécessaires que si l'optimiseur historique est reconstruit. |
| `handoff_worldcup_2026/NEXT_PROJECT_INTEGRATION_GUIDE.md` | 50 | `numpy` | dependency | Le runtime actuel utilise uniquement Python standard. 'pytest' sert aux tests. NumPy/SciPy/Optuna ne sont nécessaires que si l'optimiseur historique est reconstruit. |
| `handoff_worldcup_2026/NEXT_PROJECT_INTEGRATION_GUIDE.md` | 50 | `historique` | documentation | Le runtime actuel utilise uniquement Python standard. 'pytest' sert aux tests. NumPy/SciPy/Optuna ne sont nécessaires que si l'optimiseur historique est reconstruit. |
| `handoff_worldcup_2026/NEXT_PROJECT_INTEGRATION_GUIDE.md` | 56 | `xG` | documentation | - Calcul de lambdas xG/Elo paramétrable. |
| `handoff_worldcup_2026/NEXT_PROJECT_INTEGRATION_GUIDE.md` | 56 | `Elo` | documentation | - Calcul de lambdas xG/Elo paramétrable. |
| `handoff_worldcup_2026/NEXT_PROJECT_INTEGRATION_GUIDE.md` | 64 | `calibration` | documentation | - Entraînement/calibration chronologique Coupe du Monde. |
| `handoff_worldcup_2026/README.md` | 3 | `historique` | documentation | Ce dossier est une extraction autonome et sans secret des briques football utiles du projet historique 'drc-prototype'. Il ne constitue **pas** l'application Coupe du Monde finale : il fournit un socle vérifiable pour pr |
| `handoff_worldcup_2026/README.md` | 17 | `xG` | documentation | - 'recycled_code/score_prediction/expected_goals.py' : modulation xG par Elo et construction de baselines glissantes. |
| `handoff_worldcup_2026/README.md` | 17 | `Elo` | documentation | - 'recycled_code/score_prediction/expected_goals.py' : modulation xG par Elo et construction de baselines glissantes. |
| `handoff_worldcup_2026/README.md` | 18 | `Dixon` | documentation | - 'recycled_code/score_matrix/score_matrix.py' : matrice Poisson avec correction Dixon–Coles et normalisation. |
| `handoff_worldcup_2026/README.md` | 18 | `Poisson` | documentation | - 'recycled_code/score_matrix/score_matrix.py' : matrice Poisson avec correction Dixon–Coles et normalisation. |
| `handoff_worldcup_2026/README.md` | 25 | `historique` | documentation | - Aucun fichier historique massif, '.env', token ou identifiant API n'est inclus. |
| `handoff_worldcup_2026/README.md` | 27 | `xG` | backtest | - La logique mathématique provient prioritairement de 'drc-prototype/optimizer.py' et 'drc-prototype/xg-backtest.js'; les paramètres optimisés historiques ne sont pas déclarés fiables pour une Coupe du Monde. |
| `handoff_worldcup_2026/README.md` | 27 | `backtest` | backtest | - La logique mathématique provient prioritairement de 'drc-prototype/optimizer.py' et 'drc-prototype/xg-backtest.js'; les paramètres optimisés historiques ne sont pas déclarés fiables pour une Coupe du Monde. |
| `handoff_worldcup_2026/README.md` | 28 | `forme` | documentation | - Les marchés absents sous forme autonome dans l'ancien projet ont été ajoutés comme couche minimale autour de la matrice. |
| `handoff_worldcup_2026/REUSABLE_COMPONENTS.md` | 3 | `expected goals` | documentation | ## Expected Goals / Elo Lambda Engine |
| `handoff_worldcup_2026/REUSABLE_COMPONENTS.md` | 3 | `Elo` | documentation | ## Expected Goals / Elo Lambda Engine |
| `handoff_worldcup_2026/REUSABLE_COMPONENTS.md` | 5 | `xG` | backtest | **Ancien chemin :** 'drc-prototype/optimizer.py' ('clubelo_win_probability', 'compute_lambdas') et 'drc-prototype/xg-backtest.js' ('calculatePoissonPro'). |
| `handoff_worldcup_2026/REUSABLE_COMPONENTS.md` | 5 | `backtest` | backtest | **Ancien chemin :** 'drc-prototype/optimizer.py' ('clubelo_win_probability', 'compute_lambdas') et 'drc-prototype/xg-backtest.js' ('calculatePoissonPro'). |
| `handoff_worldcup_2026/REUSABLE_COMPONENTS.md` | 7 | `Poisson` | documentation | **Rôle :** transforme des xG de base en intensités Poisson domicile/extérieur modulées par Elo; produit aussi des baselines glissantes attaque/défense. |
| `handoff_worldcup_2026/REUSABLE_COMPONENTS.md` | 7 | `xG` | documentation | **Rôle :** transforme des xG de base en intensités Poisson domicile/extérieur modulées par Elo; produit aussi des baselines glissantes attaque/défense. |
| `handoff_worldcup_2026/REUSABLE_COMPONENTS.md` | 7 | `attaque` | documentation | **Rôle :** transforme des xG de base en intensités Poisson domicile/extérieur modulées par Elo; produit aussi des baselines glissantes attaque/défense. |
| `handoff_worldcup_2026/REUSABLE_COMPONENTS.md` | 7 | `défense` | documentation | **Rôle :** transforme des xG de base en intensités Poisson domicile/extérieur modulées par Elo; produit aussi des baselines glissantes attaque/défense. |
| `handoff_worldcup_2026/REUSABLE_COMPONENTS.md` | 7 | `Elo` | documentation | **Rôle :** transforme des xG de base en intensités Poisson domicile/extérieur modulées par Elo; produit aussi des baselines glissantes attaque/défense. |
| `handoff_worldcup_2026/REUSABLE_COMPONENTS.md` | 8 | `xG` | documentation | **Entrées :** xG, delta Elo, poids xG/Elo, avantage terrain; ou quatre historiques glissants. |
| `handoff_worldcup_2026/REUSABLE_COMPONENTS.md` | 8 | `Elo` | documentation | **Entrées :** xG, delta Elo, poids xG/Elo, avantage terrain; ou quatre historiques glissants. |
| `handoff_worldcup_2026/REUSABLE_COMPONENTS.md` | 11 | `calibration` | documentation | **Réutilisabilité :** élevée pour la formule, calibration obligatoire. |
| `handoff_worldcup_2026/REUSABLE_COMPONENTS.md` | 13 | `calibration` | documentation | **Limites :** aucune calibration internationale fournie; l'avantage terrain doit être neutralisé/adapté. |
| `handoff_worldcup_2026/REUSABLE_COMPONENTS.md` | 17 | `Dixon` | backtest | **Ancien chemin :** boucles Poisson/Dixon–Coles dans 'drc-prototype/optimizer.py' et 'drc-prototype/xg-backtest.js'. |
| `handoff_worldcup_2026/REUSABLE_COMPONENTS.md` | 17 | `Poisson` | backtest | **Ancien chemin :** boucles Poisson/Dixon–Coles dans 'drc-prototype/optimizer.py' et 'drc-prototype/xg-backtest.js'. |
| `handoff_worldcup_2026/REUSABLE_COMPONENTS.md` | 17 | `xG` | backtest | **Ancien chemin :** boucles Poisson/Dixon–Coles dans 'drc-prototype/optimizer.py' et 'drc-prototype/xg-backtest.js'. |
| `handoff_worldcup_2026/REUSABLE_COMPONENTS.md` | 17 | `backtest` | backtest | **Ancien chemin :** boucles Poisson/Dixon–Coles dans 'drc-prototype/optimizer.py' et 'drc-prototype/xg-backtest.js'. |
| `handoff_worldcup_2026/REUSABLE_COMPONENTS.md` | 24 | `scipy` | dependency | **Adaptations :** remplacement de SciPy par la PMF standard, normalisation explicite, top scores, contrôles d'erreur. |
| `handoff_worldcup_2026/REUSABLE_COMPONENTS.md` | 29 | `xG` | backtest | **Ancien chemin :** agrégations partielles 1X2/double chance dans 'drc-prototype/xg-backtest.js' et évaluations OU/BTTS dans 'drc-prototype/old/analyze_markets.js'. |
| `handoff_worldcup_2026/REUSABLE_COMPONENTS.md` | 29 | `backtest` | backtest | **Ancien chemin :** agrégations partielles 1X2/double chance dans 'drc-prototype/xg-backtest.js' et évaluations OU/BTTS dans 'drc-prototype/old/analyze_markets.js'. |
| `handoff_worldcup_2026/REUSABLE_COMPONENTS.md` | 41 | `xG` | backtest | **Ancien chemin :** 'drc-prototype/xg-backtest.js', 'drc-prototype/backtest.js', 'drc-prototype/optimizer.py'. |
| `handoff_worldcup_2026/REUSABLE_COMPONENTS.md` | 41 | `backtest` | backtest | **Ancien chemin :** 'drc-prototype/xg-backtest.js', 'drc-prototype/backtest.js', 'drc-prototype/optimizer.py'. |
| `handoff_worldcup_2026/REUSABLE_COMPONENTS.md` | 49 | `log loss` | metric | **Limites :** pas de log loss/Brier score, cotes, ROI, persistance ou contrôle temporel automatique. |
| `handoff_worldcup_2026/REUSABLE_COMPONENTS.md` | 49 | `Brier` | metric | **Limites :** pas de log loss/Brier score, cotes, ROI, persistance ou contrôle temporel automatique. |
| `handoff_worldcup_2026/REUSABLE_COMPONENTS.md` | 61 | `historique` | documentation | **Limites :** adaptateur spécifique au schéma API-Football; le mapping manuel historique de clubs européens n'est pas pertinent tel quel pour les sélections. |
| `handoff_worldcup_2026/examples/example_generate_score_matrix.py` | 10 | `xG` | model | print(f"Équipe A xG ajusté: {home_lambda:.2f}; Équipe B: {away_lambda:.2f}") |
| `handoff_worldcup_2026/recycled_code/backtesting/backtester.py` | 1 | `backtest` | backtest | """Small chronological-friendly market backtester adapted from prototype backtest scripts.""" |
| `handoff_worldcup_2026/recycled_code/score_matrix/score_matrix.py` | 1 | `Dixon-Coles` | model | """Autonomous Poisson/Dixon-Coles score-matrix generator recycled from the prototype.""" |
| `handoff_worldcup_2026/recycled_code/score_matrix/score_matrix.py` | 1 | `Dixon` | model | """Autonomous Poisson/Dixon-Coles score-matrix generator recycled from the prototype.""" |
| `handoff_worldcup_2026/recycled_code/score_matrix/score_matrix.py` | 1 | `Poisson` | model | """Autonomous Poisson/Dixon-Coles score-matrix generator recycled from the prototype.""" |
| `handoff_worldcup_2026/recycled_code/score_matrix/score_matrix.py` | 47 | `expected goals` | model | raise ValueError("Expected goals must be non-negative") |
| `handoff_worldcup_2026/recycled_code/score_prediction/expected_goals.py` | 1 | `xG` | backtest | """Expected-goal helpers extracted from drc-prototype/optimizer.py and xg-backtest.js.""" |
| `handoff_worldcup_2026/recycled_code/score_prediction/expected_goals.py` | 1 | `backtest` | backtest | """Expected-goal helpers extracted from drc-prototype/optimizer.py and xg-backtest.js.""" |
| `handoff_worldcup_2026/recycled_code/score_prediction/expected_goals.py` | 7 | `Elo` | model | """Convert an Elo difference into a home-win strength probability.""" |
| `handoff_worldcup_2026/recycled_code/score_prediction/expected_goals.py` | 19 | `xG` | model | """Modulate baseline team xG with Elo strength and home-field advantage.""" |
| `handoff_worldcup_2026/recycled_code/score_prediction/expected_goals.py` | 19 | `Elo` | model | """Modulate baseline team xG with Elo strength and home-field advantage.""" |
| `handoff_worldcup_2026/recycled_code/score_prediction/expected_goals.py` | 21 | `expected goals` | model | raise ValueError("Expected goals must be non-negative") |
| `handoff_worldcup_2026/recycled_code/score_prediction/expected_goals.py` | 37 | `xG` | model | """Build matchup xG baselines using the prototype's rolling attack/defence blend.""" |
| `handoff_worldcup_2026/requirements_recycled.txt` | 6 | `numpy` | dependency | # numpy |
| `handoff_worldcup_2026/requirements_recycled.txt` | 7 | `scipy` | dependency | # scipy |
| `handoff_worldcup_2026/requirements_recycled.txt` | 8 | `optuna` | dependency | # optuna |
| `prototype_ia_coupe_du_monde_2026.md` | 69 | `historique` | documentation | - Est-ce que l’historique des prédictions les rassure ? |
| `prototype_ia_coupe_du_monde_2026.md` | 357 | `historique` | documentation | 9. L’historique compare la prédiction initiale au résultat réel |
| `prototype_ia_coupe_du_monde_2026.md` | 389 | `historique` | documentation | Mise à jour de l’historique IA |
| `prototype_ia_coupe_du_monde_2026.md` | 468 | `historique` | documentation | - afficher un historique crédible ; |
| `prototype_ia_coupe_du_monde_2026.md` | 494 | `historique` | documentation | Historique des signaux IA |
| `prototype_ia_coupe_du_monde_2026.md` | 542 | `historique` | documentation | - sur une page complète : afficher l’historique complet, réussites et échecs. |
| `prototype_ia_coupe_du_monde_2026.md` | 812 | `historique` | documentation | ### Historique |
| `prototype_ia_coupe_du_monde_2026.md` | 862 | `historique` | documentation | - historique partiel des signaux IA ; |
| `prototype_ia_coupe_du_monde_2026.md` | 887 | `historique` | documentation | - historique des signaux IA. |
| `prototype_ia_coupe_du_monde_2026.md` | 1003 | `forme` | documentation | - forme récente ; |
| `prototype_ia_coupe_du_monde_2026.md` | 1030 | `Poisson` | documentation | probability = poisson(home_goals, home_xg) * poisson(away_goals, away_xg) |
| `prototype_ia_coupe_du_monde_2026.md` | 1225 | `historique` | documentation | - page historique ; |
| `prototype_ia_coupe_du_monde_2026.md` | 1372 | `historique` | documentation | - Historique IA |

## Interpretation

The repository contains cleaned mathematical components and documentation about
the former optimizer, but not a complete recoverable trained engine. References
point to rolling attack/defence baselines, Elo modulation, Poisson/Dixon-Coles,
chronological optimization and log loss. Historical parameters and a trustworthy
training dataset were intentionally not retained.
