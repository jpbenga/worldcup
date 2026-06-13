# Product Screens Specification V2.4

V2.4 prepares data contracts and functional scope without a full visual rewrite.

## Screens

- Home: active engine status, next fixtures, tournament simulation highlights and transparency link.
- Match list: all 72 fixtures grouped by group and round, with modal score, 1X2 and confidence.
- Match detail: teams, kickoff, top scores, 1X2, preferred markets, DNB push explanation and coherence warning.
- Score matrix: accessible 0-7 grid, highlighted modal score and top-five scores.
- Derived markets: grouped double chance, DNB, totals, BTTS and team goals, with reliability labels from V2.4.
- Tournament/groups: group teams, first/second/third/fourth probabilities, qualification and elimination probability.
- Transparency: engine version, historical metrics, market definitions, limitations and verification status.
- Future AI history: later prediction-version history and result tracking; not implemented in V2.4.
- Future mini back office: later release-health, data-refresh and artifact-validation controls; not implemented in V2.4.

The current frontend may continue consuming existing assets. New screens should prefer the V2.4 release-candidate and simulation contracts while preserving the active prediction source as a compatibility layer.
