# Design rules — deck-specific laws the agent must obey

Write rules that are CHECKABLE in QA, not vibes. Delete what you don't need.
These sit on top of the style preset and brand.yaml; conflicts resolve in
favor of this file.

## Layout

- Safe margins: 64px slides edges; nothing but page numbers outside
- Max 6 bullets / 7 steps / 6 metrics / 5 table columns per slide
- No layout family repeated 4+ slides in a row (validator warns)

## Typography

- Type scale: display 54-76 / title 44 / lead 24 / body 17-22 / caption 12.5
- Thai: line-height >= 1.25 everywhere, NO negative letter-spacing
- One number format per deck (thousands separator, decimals, unit placement)

## Color

- One accent color for attention; never fill large areas with it
- Text contrast: 4.5:1 body, 3:1 large text (WCAG AA)
- Charts: palette order primary -> accent -> secondary; <= 5 donut slices

## Numbers and claims

- Every number on a slide appears in sources-map.json with its source
- Chart axes start at zero for bars/columns unless labeled otherwise
- No stat without a year; no year without a source

## Fonts (strategy chain — spec §10)

- preferred font -> installed/embedded check (scripts/check_fonts.py)
  -> fallback stack -> PDF as canonical export when portability is uncertain
- Headline→vector conversion: SUPPORTED AS A CONCEPT, NOT IMPLEMENTED —
  reserve for display-only headlines; never convert body text (editability)

## Prohibited

- Image generators producing whole slides or text-in-image
- Decorative charts; dual axes; 3D effects
- Off-token colors invented per slide
