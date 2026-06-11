# UI Enrichment Release Notes V2.5

V2.5 enriches the existing Angular interface with the active
`quant_hybrid_v2.2` release-candidate data.

- Group fixture cards now show the active modal score and favorite probability.
- The existing match modal now prioritizes active 1X2, top scores, structured
  markets, DNB explanation, coherence and score-matrix transparency.
- `/simulation` displays 50,000 group-stage scenarios, qualification leaders
  and rank probabilities for all 12 groups.
- A frontend-asset validator checks publication consistency and UI contract
  completeness.

No model was retrained, Optuna was not rerun, and active prediction
probabilities were not changed.

The existing home structure, group navigation, match cards, modal interaction,
provenance and history remain in place. Angular consumes
`worldcup_2026_predictions_release_candidate_v2_4.json` and
`worldcup_tournament_simulation_v2_4.json` directly; the V2.4 market summary
and engine verification are included in the frontend asset validation.

The remaining product limit is deliberate: simulation stops after the group
stage because no complete knockout bracket contract exists.
