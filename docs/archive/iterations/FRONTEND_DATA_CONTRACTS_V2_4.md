# Frontend Data Contracts V2.4

## Files

- `predictions.json`: active-engine source predictions; use for backward-compatible existing screens.
- `worldcup_2026_predictions_release_candidate_v2_4.json`: preferred V2.4 match-list and detail contract.
- `secondary_market_performance_summary_v2_4.json`: plain-language evidence and product-display guidance.
- `worldcup_tournament_simulation_v2_4.json`: group ranking and qualification probabilities.
- `active_engine_verification_v2_4.json`: release-health and provenance status.

## Rendering

The release-candidate match object requires fixture identity, teams, kickoff, group/stage, engine and release versions, score matrix, top scores, 1X2 probabilities, structured markets, confidence, coherence and source metadata. Optional venue, city and round metadata remain in the active source file.

A match list should show teams, kickoff, group, modal score, 1X2 and confidence. Match detail can render top scores first, then the full matrix, structured markets and coherence warning. The simulation screen should display group tables as probabilities: finish position, qualification and elimination. These probabilities describe tournament scenarios and are not individual match predictions.

Transparency screens should pair market probabilities with V2.4 performance guidance. Markets flagged for warnings or hiding must not be presented as equally reliable to broad, high-coverage markets.
