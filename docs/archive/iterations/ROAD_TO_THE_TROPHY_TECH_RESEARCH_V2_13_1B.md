# Road to the Trophy Tech Research V2.13.1B

## Need identified after UX review

The first CSS-only implementation failed the central product requirement. It provided filters around a list of projected matches, but no spatial model of the tournament, no continuous route from groups to the trophy, no group match story, and no way to pan or zoom through 104 matches. The technology decision must therefore optimize for exploration, not merely implementation simplicity.

## Local stack audit

The frontend uses Angular 22, standalone components, Angular signals, RxJS, Tailwind 3, and no previous visualization library or Angular CDK. `/simulation` is a dedicated route. The production initial-bundle warning budget is 500 kB. The dataset contains 72 group fixtures and 32 knockout target slots, which is large enough to need navigation but far below Canvas/WebGL rendering pressure.

## Options evaluated

### Custom SVG plus Angular

SVG offers excellent connectors, highlighted routes, and scalable geometry. Rendering rich standings and six match summaries inside every group through SVG text would, however, be cumbersome and less accessible than semantic HTML. SVG is selected for connections only.

### CSS Grid and Flex

CSS remains appropriate inside cards and inspectors. It is insufficient as the primary world layout because the complete tournament needs spatial navigation, curved connections, focus transitions, and zoom.

### D3 modules

`d3-zoom` supports mouse drag, wheel zoom, touch pinch, bounded scales, programmatic transforms, and animated tours. `d3-selection` and `d3-transition` allow Angular to retain ownership of the DOM while D3 controls only the viewport transform. This small modular use avoids importing the complete D3 bundle.

### Angular CDK

CDK provides useful overlays, focus management, and virtual scrolling, but it does not solve the spatial tournament map. The current inspector is persistent rather than an overlay and 104 items do not require virtualization. CDK is not added.

### Cytoscape.js and ELK

Cytoscape provides graph layouts, pan, zoom, and graph interactions. ELK Layered provides directional layered layout, orthogonal routing, compound graphs, and crossing reduction. Both are strong for unknown or generic graphs. The World Cup flow is a known narrative layout with rich HTML nodes, so introducing a second renderer or asynchronous layout engine would reduce product control without solving a current unknown.

### Bracket libraries

`brackets-viewer.js` and related bracket models are optimized for conventional elimination brackets. They do not naturally represent the 72-match group stage, live standings, projected qualification, real/projected/to-confirm states, or the transition from 12 groups to a 32-team projected bracket. Their rigidity is a poor fit.

### Canvas and WebGL

Performance would be ample, but text accessibility, semantic interaction, and rich card rendering would be worse. A 104-match atlas does not justify these technologies.

## Selected architecture

The Tournament Atlas uses Angular-rendered semantic HTML nodes on a deterministic 4,300 by 3,040 world canvas. A custom SVG layer draws group-to-knockout and round-to-round connections. D3 Zoom transforms the whole world and supplies mouse, touch, bounded zoom, animated focus, and reset-to-overview behavior. Angular signals control selected team, match, group, round, status, and inspector content.

Dependencies added and justified:

- `d3-zoom`: direct spatial navigation.
- `d3-selection`: attaches zoom behavior without replacing Angular rendering.
- `d3-transition`: animated movement between overview, groups, and rounds.
- Matching `@types` packages for strict TypeScript integration.

The production bundle remains below its 500 kB warning budget.

## Primary references

- D3 Zoom: https://d3js.org/d3-zoom
- ELK Layered: https://eclipse.dev/elk/reference/algorithms/org-eclipse-elk-layered.html
- Cytoscape.js layouts: https://js.cytoscape.org/
- Brackets Viewer: https://github.com/Drarig29/brackets-viewer.js
