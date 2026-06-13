# Road to the Trophy Tech Research V2.13.1B

## Options evaluated

| Option | Strength | Cost or risk | Decision |
| --- | --- | --- | --- |
| Custom SVG | Precise connectors and zoom | More accessibility and responsive-state work | Future overlay only |
| CSS Grid/Flex | Native, responsive, semantic HTML, already used locally | Connectors are less expressive | Selected |
| D3 | Rich layout and transitions | New dependency and imperative integration | Rejected |
| Angular CDK | Strong interaction primitives | No bracket layout; new dependency | Rejected |
| Bracket libraries | Fast conventional bracket | Styling, accessibility, and 48-team format fit uncertain | Rejected |
| Canvas/WebGL | High rendering capacity | Poor fit for 32 interactive matches and semantic controls | Rejected |

## Decision

Use Angular 22 signals with semantic buttons, CSS Grid/Flex, and the existing Tailwind pipeline. The dataset is small, so a rendering library would add more integration cost than value. The selected architecture keeps keyboard controls, responsive behavior, and product-specific status language straightforward. A custom SVG connector layer can be added later without changing the view-model contract.

## Primary references reviewed

- Angular signals: https://angular.dev/guide/signals
- D3 hierarchy layouts: https://d3js.org/d3-hierarchy
- Brackets Viewer reference implementation: https://github.com/Drarig29/brackets-viewer.js
