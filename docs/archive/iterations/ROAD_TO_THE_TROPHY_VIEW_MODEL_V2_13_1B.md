# Road to the Trophy View Model V2.13.1B

`road_to_the_trophy_view_model_v2_13_1B.json` is the single frontend contract for `/simulation`.

It includes:

- 12 group views with teams, matches, standings, projected qualifiers, and knockout links.
- Five knockout rounds containing 31 projected matchups.
- A separate third-place placeholder marked to confirm.
- Team-path lookup data for interactive highlighting.
- Product controls for groups, rounds, statuses, and reset.
- The projected winner, projected final, result summary, official-mapping state, and limitations.

The view model intentionally avoids claiming that the projected matchup IDs are official match numbers.

The enriched atlas contract also includes all 72 group match states, live standings,
team qualification probabilities, group stability labels, real/upcoming match
collections, round-to-round `next_match_id` connections, and complete inspector
payloads. Each team path now starts with its three group matches before listing
its projected knockout route.
