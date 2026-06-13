# Matchday Refresh Runbook V2.10

Run the refresh after a match finishes, after a result correction, or at the
end of a matchday. The normal online command is:

```bash
python3 backend/scripts/run_matchday_refresh_v2_10.py --fetch --simulations 50000
```

Use `--no-fetch` to rebuild every derived layer exclusively from cached or
already generated result data. Use `--dry-run` to print the exact ordered
commands without writing final artifacts. `--skip-frontend-copy` updates
generated and snapshot data while leaving Angular assets untouched. `--force`
continues after a failed step for diagnosis; it does not authorize model or
active-prediction changes.

After a run, inspect `matchday_refresh_manifest_v2_10.json`, then run:

```bash
python3 backend/scripts/audit_generated_artifact_hygiene_v2_10.py
python3 backend/scripts/validate_matchday_refresh_v2_10.py
```

Expected changes are result overlays, post-match evaluation, live standings,
unified match state, conditioned active/candidate simulations, their
comparison, projected-campaign proxies, validations and the refresh manifest.
Active `predictions.json`, quant engine results and Optuna output must never
change. If one does, stop, inspect the manifest hashes and do not commit.

If API-Football fails, the fetch script reports the failure and uses cached
data when available. If no new result is available, the pipeline may still
regenerate equivalent derived artifacts; verify the result summary before
committing. Before commit, inspect the hygiene report, run Angular validation
when frontend assets changed, and stage only explicit V2.10 and intended
refresh files. Never use `git add .`.
