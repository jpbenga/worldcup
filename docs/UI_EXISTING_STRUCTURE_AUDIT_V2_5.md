# UI Existing Structure Audit V2.5

The Angular 22 application already had the right product skeleton: a single
home page, group tabs, compact fixture cards and a match-detail modal. Tailwind
utilities define a consistent dark slate, cyan and violet visual language.

V2.5 preserves the group-first journey and the existing modal. It does not add
match-detail pages or replace the card system. Existing compatibility
snapshots remain available, while the V2.4 release-candidate contract becomes
the source for active prediction enrichment.

Routing already existed, so a dedicated `/simulation` route is the smallest
coherent addition for the larger tournament-probability table.

## Existing component map

- `HomeComponent` composes source status, group exploration, the selected-match
  modal and prediction history.
- `GroupTabsComponent` owns the group selector and renders the existing compact
  fixture buttons. It delegates team and standings display to
  `TeamBadgeComponent`, `GroupStandingsComponent` and
  `GroupStrengthSummaryComponent`.
- `MatchModalComponent` is the established match-detail interaction.
  `ScoreMatrixComponent` and the existing market components establish the
  presentation patterns for probability data.
- `PredictionService`, `MatchService` and `WorldCupService` load JSON snapshots
  from `frontend/src/assets/data`.

## Visual constraints retained

The interface uses rounded slate surfaces, restrained cyan/violet accents,
small uppercase context labels, responsive grids and horizontal overflow for
dense tables. V2.5 keeps those patterns, component names and the modal flow.
The home-page group structure, cards, team blocks, standings, provenance and
history are not replaced or heavily reorganized.
