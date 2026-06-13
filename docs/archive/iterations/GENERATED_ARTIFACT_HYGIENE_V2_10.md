# Generated Artifact Hygiene V2.10

The hygiene audit classifies every currently modified or untracked repository file. Category counts: `{'expected_refresh_artifact': 62, 'manual_source_file': 2, 'legacy_artifact': 9}`.

Active prediction files protected: `True`. Unexpected changes: `[]`.

Expected refresh artifacts include result overlays, evaluations, live standings, unified match state, conditioned active/candidate simulations, comparisons, projected campaigns and validations. Legacy baseline/Elo/diversity artifacts, manual source files, active prediction files and model-training artifacts are classified separately.

Preexisting workspace changes remain visible through `preexisting_before_refresh`; they are never silently described as new refresh output or automatically staged. Before commit, stage explicit V2.10 files only and investigate any active-prediction or model-training artifact marked modified.
