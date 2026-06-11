# World Cup Tournament Simulation V2.4

V2.4 runs `50,000` deterministic-seed tournament simulations from the 72 active group-stage score matrices. It calculates each team's probability of finishing first, second, third or fourth, qualifying through the top two or best-third route, and being eliminated in the group.

Full tournament simulation available: `false`. The repository does not contain knockout fixtures or a complete bracket, so V2.4 does not invent one. Qualification follows the 2026 group rule: the top two in each of 12 groups plus the eight best third-placed teams.

Top qualification probabilities: `[('England', 0.9331), ('Spain', 0.9288), ('Morocco', 0.89618), ('Netherlands', 0.88442), ('Argentina', 0.87452), ('Germany', 0.87168), ('Brazil', 0.86038), ('Belgium', 0.84196), ('Switzerland', 0.84162), ('USA', 0.82352)]`. Tie resolution uses points, goal difference and goals scored, then a seeded random tie-break because complete official disciplinary and head-to-head tie-break inputs are unavailable.
