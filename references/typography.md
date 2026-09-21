# Typography system

## Roles

| Role | Use | Relative size (of 720px slide height) |
| --- | --- | --- |
| display | cover + statements | 76px / 54px |
| headline (title) | slide titles | 44px |
| subheadline | subtitles | 21px |
| lead | opening paragraph | 24px |
| body | bullets, panels | 17-22px |
| label | eyebrows, axis, tags | 12-15px, tracked +8-16% |
| caption/source | provenance lines | 12.5px |
| number | metrics | 34-150px, display face |

Controlled scale only — never invent intermediate sizes. Minimum on-slide
text: 12px (caption); body >= 17px. If content does not fit, cut content,
not type size.

## Stacks and fallbacks

Theme declares `display` / `body` / `mono` stacks. Every stack must end in
system fallbacks. Never assume the PPTX recipient owns a custom font: keep
`preferred_font` + `fallback_font` + `export_strategy` per deck; PDF/HTML is
the visual canonical version when font portability is uncertain.

Custom fonts: place woff2/woff/ttf/otf under `fonts/`, list in
`theme.typography.custom_fonts` — the HTML renderer base64-embeds them so
deck.html stays self-contained.

## Thai typography (critical)

- Line-height >= 1.25 everywhere (upper vowels + lower vowels need room);
  the theme's `line_height_body` minimum is enforced by the renderer.
- NO negative letter-spacing on Thai text (breaks tone marks); tracking
  only on uppercase Latin labels.
- Mixed Thai-English: wrap at word boundaries; avoid breaking inside a
  cluster; check numerals render in the Thai-capable face.
- Recommended Google fonts (fallback-safe): Prompt, Anuphan, IBM Plex Sans
  Thai, Noto Sans Thai, Sarabun; pair with Inter/Avenir for Latin display.

## Numerals

One number format per deck (validator of consistency is your eye in QA):
thousands separators, unit placement, decimal places decided once. Big
numbers set in the display face, tabular where available.

## Hierarchy discipline

One focal point per slide (`emphasis`): the eye should land title ->
focal element -> support, in that order, in ~3 seconds. Whitespace is the
cheapest hierarchy tool: when two elements compete, separate or demote one.

## Font strategy chain (v2)

preferred font -> installed/embedded check -> fallback stack -> PDF
canonical. `scripts/check_fonts.py` scans `fonts/`, validates
`theme.typography.custom_fonts`, and writes `output/font-strategy.json`:
what gets base64-embedded in deck.html, which safe stack PPTX uses
(Thai decks map to Leelawadee UI/Noto Sans Thai — recipients are not
assumed to own your fonts), and whether PDF should be the canonical
visual export. Variable fonts: declare the full weight range, e.g.
`"weight": "100 900"`. Headline->vector conversion is a documented
concept only — never convert body text (editability wins).
