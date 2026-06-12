# World Cup Knockout Structure V2.6

The available local and V2.6 API-Football fixture files contain only the 72
group-stage fixtures. No Round of 32, Round of 16, quarter-final, semi-final or
final fixture mapping is available.

`knockout_structure_available` is therefore `false`. V2.6 does not invent an
official bracket or claim an official champion simulation. The product uses a
clearly labelled Projected Campaign proxy instead.

The discovery inspected both the dedicated V2.6 cached result response and the
previous World Cup fixture cache. Re-running discovery is safe: it reads
fixture metadata only, makes no prediction changes and will continue to block
official-path simulation until both knockout fixtures and an authoritative
slot mapping are available.
