# Matchday Refresh Pipeline Strategy V2.10

The result-aware product layer previously required separate V2.6 result and
evaluation commands, V2.7 standings and match-state commands, and V2.9
candidate comparison commands. That separation was useful during development
but creates operational risk after a match: running steps out of order can
leave cards, standings, simulations and projected campaigns describing
different result snapshots.

V2.10 defines one ordered workflow. It refreshes or rereads official results,
evaluates frozen forecasts, rebuilds live standings and unified match state,
runs active and candidate conditioned simulations together, rebuilds both
campaign proxies, and executes both consistency validators. A manifest records
every command, result summary, protected-file hashes and Git hygiene.

A matchday refresh never changes pre-match probabilities. It only refreshes
result-aware derived layers.

Real results remain a separate overlay because forecasts must stay auditable
after kickoff. The active and candidate simulations are recalculated together
so their comparison uses the same official locked results and simulation
count. Neither simulation promotes the candidate.

The orchestrator protects active predictions, model results and Optuna output
with SHA-256 hashes before and after execution. It reports preexisting changes
separately from files produced during the run. Explicit staging remains
mandatory; `git add .` is not part of the workflow. This prevents legacy,
manual-source or unrelated workspace files from entering a matchday refresh
commit accidentally.
