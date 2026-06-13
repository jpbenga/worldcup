# Road to the Trophy Scenario Orchestration V2.13.1B

The V2.13.1B scenario engine consumes the existing V2.13 living scenario and representative-path outputs. It does not retrain, rerun Optuna, change active predictions, or promote a candidate model.

The source ran 50,000 knockout simulations on one fixed, derived projected bracket. Complete individual paths were not persisted. V2.13.1B therefore publishes a coherent representative path inside that bracket and explicitly records `full_simulated_paths_available: false`.

The orchestration publishes synchronized generated, snapshot, and frontend copies. Team paths are derived from projected round matchups. Official mapping remains unavailable and the fallback is always labeled `simulation_derived_projection`.
