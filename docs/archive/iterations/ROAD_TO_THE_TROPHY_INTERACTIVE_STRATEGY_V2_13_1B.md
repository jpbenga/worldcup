# Road to the Trophy Interactive Strategy V2.13.1B

Road to the Trophy must let the user explore the tournament path, not just read a probability summary.

The feature is designed as a Tournament Atlas rather than a static bracket. The World Cup story begins with 12 groups and 72 known fixtures; a knockout bracket without those matches cannot explain why a team reaches a slot. The product target is therefore all 104 matches: group results and upcoming predictions, followed by the 32 knockout target matches.

The global view gives the user a mental map. Panning and zooming let them travel through it. A group focus reveals the current standings, six matches, and projected qualifiers. Clicking any team highlights its route and opens a journey inspector containing its current rank, qualification probability, three group matches, projected opponents, and advancement probabilities. Clicking a match opens its real or projected detail.

The 50,000 simulations provide qualification and advancement probabilities plus a coherent representative scenario. Because complete paths were not persisted, the interface must not imply that every displayed route is the single most frequent complete path. It must also distinguish results already locked as real, simulation projections, and slots that remain to confirm.

The official knockout mapping is unavailable. Road to the Trophy therefore treats the bracket as a projected scenario and never presents it as FIFA’s official bracket. The atlas architecture keeps this boundary visible while allowing the scenario to be genuinely useful and enjoyable to explore.
