# Figure Spec

Deterministic JSON → SVG structured diagrams — for system architecture, workflow pipelines, and audit cascades where node positions, connections, and groupings are semantically important.

## Design Patterns

**Layered Architecture**: Stack rows of related nodes, each row is a group, add inter-layer arrows with semantic labels (uses↓, produces↑, checks↓).

**Hub-and-Spoke**: Central node (e.g., Executor), peripheral nodes (skills, tools), solid arrows for primary relations, dashed for feedback.

**Pipeline with Feedback**: Left-to-right main flow, feedback arrows curve below.

**Audit Cascade**: Three-stage horizontal cascade with inputs feeding in from top, outputs exiting right, each stage in its own group.

## Canvas Sizing Guide

- Single-column figure: ~500×350 px
- Two-column (full-width): ~900×500 px
- Tall topology: ~700×700 px

## Visual Review Checklist

- No overlaps: nodes don't collide with each other or group boundaries
- Readability: font sizes consistent, labels aren't clipped
- Edge clarity: arrows hit nodes at clean angles, labels near edges are legible
- Group alignment: background rectangles frame their members cleanly
- Color distinction: categories visually distinct in both color and grayscale
- Fix issues in the spec (never the generated SVG) and re-render

## Anti-Patterns

- Don't use groups as hierarchy: groups frame peer nodes, not containment
- Don't nest groups: renderer draws them as background rectangles; nested groups look like Russian dolls
- Don't cross-draw long diagonals: if an arrow crosses 3+ rows, rethink the layout
- Don't mix font sizes for same role: keep one size per node category
