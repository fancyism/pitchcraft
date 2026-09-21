# Brand system and design tokens

## Compile brand/ once per deck

Read `brand/` for logo, palette, typography, spacing, icon rules,
photography rules, guidelines. Compile into theme tokens — never hard-code
brand values slide by slide:

```json
"theme": {
  "colors": { "primary": "#…", "secondary": "#…", "accent": "#…",
              "surface": "#…", "surface_alt": "#…", "text": "#…",
              "text_muted": "#…", "border": "#…" },
  "typography": { "display": "stack", "body": "stack", "mono": "stack",
                  "line_height_body": 1.55,
                  "custom_fonts": [{"family":"X","path":"fonts/x.woff2"}] },
  "spacing": { "xs": 4, "sm": 8, "md": 16, "lg": 32 },
  "radius": { "sm": 8, "md": 14, "lg": 20 }
}
```

Tokens become CSS custom properties in the HTML renderer and the color map
in the PPTX exporter. Contrast: text-on-surface must meet WCAG AA (4.5:1
body, 3:1 large); muted text is for support, never claims.

No brand/ folder? Ship the default editorial theme (warm paper, deep
green-ink primary, burnt-orange accent) — consistent defaults beat ad-hoc
palette invention.

## Logo rules

Cover and closing only, unless guidelines say otherwise. Clear space = the
logo's cap-height on every side. Never recolor, stretch, or place on a busy
image without a scrim.

## Reference analysis (references/ screenshots)

Analyze for: layout skeleton, visual hierarchy, spacing rhythm, density,
typography pairing, grid, card structure, image treatment, iconography,
border radius, stroke weights, shadows, color behavior, chart treatment.

Extract DESIGN PRINCIPLES ("42px gutters", "one accent per quadrant",
"numbers always oversized 3x"). Reconstruct the design language — never
copy layouts pixel-for-pixel, never reuse copyrighted assets or logos.

## Design system primitives

Think in components, not slides: Canvas, Grid, Stack, Row, Column, Card,
Text, Heading, Image, Icon, Divider, Badge, Metric, Chart, Diagram, Callout.
Two decks from the same brand should share tokens and components so the
second deck costs half the first. The CSS layer of the HTML renderer
implements these primitives; reuse them before inventing new structure.

## Workspace brand inputs (v2)

`config/brand.yaml` is the primary input (identity, colors, typography,
logo/icon/photography rules); `brand/palette.json` with the same color
keys is accepted as an alternative. Resolution order: style preset
(`config/style-presets/<name>.yaml`) -> brand.yaml overlay ->
`config/design-rules.md` as deck-specific law. Record the chosen preset
in `metadata.style_preset` so the chain stays auditable.
