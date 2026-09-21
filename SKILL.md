---
name: pitchcraft
description: >
  Build marketing-grade presentations from a project workspace: sources,
  brand, fonts, data in — presentation deck out. Turns source material into
  a story, a slide plan, a validated Slide DSL (deck.json), and renders a
  self-contained HTML deck plus optional editable PPTX and PDF, with a
  mandatory visual/content QA loop and claim provenance. Use when the user
  asks to create a presentation, deck, pitch deck, slide deck, investor or
  marketing presentation from documents/workspace, or says pitchcraft.
---

# PitchCraft — Marketing Presentation Engine

A presentation is a structured visual communication system, not bullets on
slides. ONE SLIDE = ONE PRIMARY COMMUNICATION JOB. Code renders; you direct.

## Quick start

```
python scripts/validate_deck.py <ws>/output/deck.json --report <ws>/output/qa-report.md
python scripts/check_fonts.py <ws>/output/deck.json --root <ws>   # font strategy (v2)
python scripts/render_html.py <ws>/output/deck.json --root <ws> -o <ws>/output/deck.html
node scripts/export_pptx.mjs <ws>/output/deck.json      # optional; npm i pptxgenjs
```

Workspace convention (any subset; Phase 0 discovers what exists):
`sources/ fonts/ brand/ references/ assets/ data/ output/` +
`config/` (deck.config.yaml, brand.yaml, design-rules.md,
style-presets/) + `templates/` (DSL presets per layout family) — copy
from `templates/workspace/` or scaffold via the CLI below.

Users scaffold a workspace (BMad-style interview) with
`npx github:fancyism/pitchcraft init` — it scaffolds config/, templates/,
folders and a START.md with the exact prompt to give you. When you find a
START.md or config/deck.config.yaml in the project, treat it as the brief.

## Pipeline — run in order, checkpoint artifacts into output/

1. **Phase 0 Discovery** — inventory sources/brand/fonts/data; tool
   discovery (node? headless browser? image gen? web search?). Never
   invent capabilities; degrade gracefully to HTML+JSON and say so.
2. **Phase 1 Ingestion** — extract claims, stats, frameworks, quotes,
   timelines; provenance per claim -> `output/sources-map.json`. Distill
   long sources first (methods.md #13). Never fabricate.
3. **Phase 2 Brief** — audience, objective, desired action, tone, length,
   language, style -> `output/brief.md`. Ask the user ONLY what changes
   the deck materially; infer the rest from sources.
4. **Phase 3 Story** — pick ONE narrative spine (persuade / explain /
   pitch / advise / teach); write the emotional arc. `references/methods.md`.
5. **Phase 4 Slide plan** — per slide: id, beat, layout family, visual
   strategy, ONE-sentence message, source refs -> `output/slide-plan.md`.
   Start each slide from its template preset in `templates/` when present
   (title, framework, comparison, timeline, data, closing).
6. **Phase 5 DSL** — serialize to `output/deck.json` per
   `schemas/deck.schema.json`; authoring guide in
   `references/slide-dsl.md`; layout choice table in
   `references/taxonomy.md`. Validate — zero FAILs before rendering.
7. **Phase 6 Theme + assets** — resolve `metadata.style_preset` from
   `config/style-presets/`, then overlay `config/brand.yaml` (or
   brand/palette.json) and `config/design-rules.md`; compile fonts via
   `check_fonts.py` (chain: preferred -> embed -> safe stack -> PDF
   canonical; Thai PPTX maps to Leelawadee UI). Charts from real data;
   images only where information design can't do the job
   (`references/visual-strategy.md`). Thai decks: line-height >= 1.25,
   no negative tracking.
8. **Phase 7 Render** — commands above.
9. **Phase 8 QA loop** — screenshot every slide; inspect against
   `references/qa.md` (visual + content + deck-level); repair until no
   FAIL; grill the deck before shipping (methods.md "Grilling").
10. **Phase 9 Export** — agreed outputs + `preview/`; keep deck.json as
    source of truth.

## Contracts

- **Deck DSL**: `schemas/*.schema.json` are normative; validator mirrors
  them. `message` is required per slide — if you can't state it, the slide
  isn't designed.
- **HTML renderer**: stdlib Python, self-contained output (fonts/images
  base64-embedded), keyboard nav + progress + notes (press `n`) + print
  mode (PDF via headless chrome `--print-to-pdf`).
- **PPTX exporter**: keeps text/tables/charts editable; funnel/matrix fall
  back to clean text layouts. Requires pptxgenjs.
- **QA**: `qa.status: FAIL` blocks export. Provenance: claims map to
  sources; insufficient evidence -> mark uncertain or cut.

## Failure behavior

Missing tool -> use what exists, note the degradation, never fake output
(e.g., no image tool -> typography-only design). Ambiguous brief ->
one concrete proposal + the assumptions, not a questionnaire. Rendered
defect -> repair at content or token level, never per-slide hacks.

## References (one level deep)

`references/pipeline.md` · `slide-dsl.md` · `taxonomy.md` ·
`visual-strategy.md` · `typography.md` · `brand-tokens.md` · `qa.md` ·
`methods.md` — worked examples: `examples/pitchcraft-demo/` (EN) ·
`examples/geo-sme-thai/` (Thai, custom font + config workspace). Changes:
`CHANGELOG.md`. Stories: `docs/stories/`.
