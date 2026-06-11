# Historical Dataset Audit

## Result

- Total matches: `192`
- Competitions: `1`
- Seasons: `[2014, 2018, 2022]`
- Teams: `47`
- Date range: `2014-06-12T20:00:00+00:00` to `2022-12-18T15:00:00+00:00`
- Average goals per match: `2.688`
- Home win: `43.2%`
- Draw: `21.4%`
- Away win: `35.4%`
- Usable for training experiments: `true`
- Dataset sufficiency: `medium`

## Score distribution

`{'2-1': 22, '1-0': 20, '1-2': 18, '0-1': 17, '0-0': 15, '2-0': 15, '1-1': 14, '0-2': 11, '2-2': 9, '0-3': 7, '3-1': 6, '3-0': 6, '2-3': 4, '1-3': 3, '3-3': 3, '4-1': 3, '2-4': 2, '1-4': 2, '6-1': 2, '3-2': 2, '1-5': 1, '4-0': 1, '0-4': 1, '2-5': 1, '1-7': 1, '5-0': 1, '5-2': 1, '4-3': 1, '4-2': 1, '6-2': 1, '7-0': 1}`

## Most represented teams

`[{'team': 'France', 'matches': 19}, {'team': 'Argentina', 'matches': 18}, {'team': 'Brazil', 'matches': 17}, {'team': 'Croatia', 'matches': 17}, {'team': 'England', 'matches': 15}, {'team': 'Belgium', 'matches': 15}, {'team': 'Germany', 'matches': 13}, {'team': 'Netherlands', 'matches': 12}, {'team': 'Uruguay', 'matches': 12}, {'team': 'Switzerland', 'matches': 12}, {'team': 'Portugal', 'matches': 12}, {'team': 'Mexico', 'matches': 11}, {'team': 'Spain', 'matches': 11}, {'team': 'Costa Rica', 'matches': 11}, {'team': 'Japan', 'matches': 11}]`

## Limitations

- The conservative spike covers World Cups only; qualifiers, continental tournaments and friendlies are absent.
- Three tournaments can support a baseline experiment but are insufficient for a full advanced engine.
- Knockout scores may include extra time; regulation-time score fields must be defined before model fitting.
- Neutral-site quality, pre-match Elo history and advanced statistics are not yet joined.

## Decision

This dataset may support a controlled baseline-calibration experiment, but it
is not sufficient by itself for a full advanced engine. No model was trained
and no backtest was performed in V0.7.
