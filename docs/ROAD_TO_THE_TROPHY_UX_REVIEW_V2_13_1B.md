# Road to the Trophy UX Review V2.13.1B

## Corrective review

The original V2.13.1B interface was rejected because it looked like filtered lists rather than an interactive tournament. It exposed teams but hid group matches and standings, showed only one knockout round at a time, and did not provide spatial navigation or a complete route.

## Tournament Atlas review

- Road to the Trophy and Tournament Atlas are visible product concepts.
- The overview represents 12 group nodes containing 72 match entries and 32 knockout target nodes.
- Every group displays its live ranking, points, qualification probabilities, and all six fixtures.
- Real group results and upcoming SimuAI scores are visually distinct.
- Connections show how projected group qualifiers feed the round of 32 and how winners move between rounds.
- Mouse drag, wheel zoom, touch pinch, zoom buttons, animated group focus, animated round focus, overview, and reset are available.
- Clicking a team highlights its group and projected path and opens the team journey inspector.
- Clicking a group or knockout match opens a contextual match inspector.
- The inspector displays group history, projected opponents, probabilities, and the absence of an official bracket.
- Status filters affect group match entries and knockout nodes.
- Mobile keeps the atlas touch-navigable and places the inspector below it.

## Product boundary

The alternative model is not central. Match cards outside `/simulation`, active predictions, retraining, and Optuna remain untouched. The knockout scenario is always labeled projected and to confirm.
