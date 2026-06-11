# Historical API-Football Exploration

## Result

- Generated at: `2026-06-11T05:58:30Z`
- Requests planned: `5`
- Requests executed: `5`
- Seasons checked: `5`
- Finished fixtures found in checked seasons: `872`
- Usable for training: `true`

## Competition inventory

| Key | League ID | Competition | Available seasons | Checked seasons | Finished fixtures found |
|---|---:|---|---|---|---:|
| `world_cup` | 1 | World Cup | 2022, 2018, 2014, 2010 | 2022 | 64 |
| `world_cup_qualification_europe` | 32 | World Cup - Qualification Europe | 2024, 2020, 2018 | 2024 | 204 |
| `world_cup_qualification_africa` | 29 | World Cup - Qualification Africa | 2023, 2022, 2018 | 2023 | 256 |
| `world_cup_qualification_asia` | 30 | World Cup - Qualification Asia | 2022, 2018 | 2022 | 230 |
| `world_cup_qualification_concacaf` | 31 | World Cup - Qualification CONCACAF | 2022, 2018 | 2022 | 118 |
| `world_cup_qualification_oceania` | 33 | World Cup - Qualification Oceania | 2022, 2018 | none | 0 |
| `world_cup_qualification_south_america` | 34 | World Cup - Qualification South America | 2022, 2018 | none | 0 |
| `friendlies` | 10 | Friendlies | 2025, 2024, 2023, 2022, 2021, 2020, 2019, 2018, 2017 | none | 0 |
| `euro` | 4 | Euro Championship | 2024, 2020, 2016, 2012, 2008 | none | 0 |
| `copa_america` | 9 | Copa America | 2024, 2021, 2019, 2016, 2015 | none | 0 |
| `africa_cup_of_nations` | 6 | Africa Cup of Nations | 2025, 2023, 2021, 2019, 2017, 2015 | none | 0 |
| `asian_cup` | 7 | Asian Cup | 2023, 2019, 2015, 2011 | none | 0 |
| `gold_cup` | 22 | CONCACAF Gold Cup | 2025, 2023, 2021, 2019, 2017, 2015 | none | 0 |
| `uefa_nations_league` | 5 | UEFA Nations League | 2024, 2022, 2020, 2018 | none | 0 |

## Limitations

- Fixture counts cover only explicitly checked league/season pairs, not every available international competition.
- Advanced statistics and neutral-site quality were not evaluated in this controlled spike.

## Next steps

- Fetch the conservative World Cup 2014, 2018 and 2022 dataset.
- Normalize only finished fixtures with real scores and audit chronology before any training.
