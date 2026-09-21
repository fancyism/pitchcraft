# Visual strategy engine

For every slide, decide the visual representation BEFORE rendering. Do not
generate decorative images when information design would communicate better.

## Decision order

1. Is the idea a NUMBER? -> big-number / kpi-dashboard (typography).
2. Is it ORDER? -> process-flow / timeline / roadmap.
3. Is it STRUCTURE? -> framework-grid / matrix-2x2 / architecture-map (SVG).
4. Is it COMPARISON? -> comparison / before-after / table.
5. Is it QUANTITY OVER CATEGORIES? -> chart (see below).
6. Is it a CLAIM or EMOTION? -> statement / quote (typography-only).
7. Only then: does an editorial/conceptual IMAGE add meaning a diagram
   cannot? -> assets + image_spec.

## Chart selection (analytical purpose, never decoration)

| Purpose | Type |
| --- | --- |
| trend over time | line / area |
| comparison across categories | bar (horizontal; labels read better) / column |
| part-to-whole | stacked-bar / donut (donut <= 5 slices) |
| stage-to-stage flow | funnel |
| single headline quantity | big-number, not a chart |

Honesty rules: axis starts at zero for bars/columns unless labeled; no dual
axes; no 3D; source line on-slide (`chart_spec.source`); values come from
`data/` or a cited source. Charts render as inline SVG (crisp at any zoom).

## SVG / diagram engine

Frameworks, processes, journeys, funnels, matrices, ecosystems -> vector
(SVG), never raster, never image-generator. The HTML renderer draws these
from DSL structure; for bespoke diagrams emit inline SVG with: semantic
groups, a consistent stroke (1-1.5px), the theme palette, and labels as
`<text>` (searchable, editable), not paths.

## Image generation policy

IMAGE GENERATOR = IMAGE. LAYOUT ENGINE = TEXT + STRUCTURE.

Good uses: editorial hero (cover), conceptual/metaphor visual, environment
or scene, background texture (keep 42%+ safe area for type), character or
product visualization.

Bad uses (refuse and use layout instead): body text, tables, detailed
frameworks, KPI numbers, charts, complex labels, citations, anything that
must remain editable.

Compose deliberately: state composition + safe_area in image_spec so
typography has a home. If no image tool exists in the runtime, ship
typography-only — a clean type system beats a broken image pipeline.

## Photography (when using real photos)

Editorial grade: one idea per image, natural light, no stock-photo grins,
treatment consistent across the deck (same warmth, same contrast). Credit in
`assets[].credit`. Never copy a reference deck's copyrighted assets.
