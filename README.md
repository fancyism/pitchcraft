# PitchCraft — Marketing Presentation Engine

An agent skill that turns a project workspace into a marketing-grade
presentation: **sources, brand, fonts, data in → deck out.**

PitchCraft treats a presentation as a structured visual communication
system — not bullets on slides. Every slide has one primary communication
job, a validated intermediate representation (the **Slide DSL**), a
deterministic renderer, and a mandatory QA loop with claim provenance.

```
sources/ → ingest → story → slide plan → deck.json (Slide DSL)
        → theme+assets → render HTML/PPTX/PDF → visual QA → export
```

## What you get

- **SKILL.md** — the agent-facing pipeline (works in Claude Code, Codex,
  OpenCode, OMP, Cursor, or any agent that reads skills)
- **Slide DSL** — `schemas/deck.schema.json` + `slide.schema.json`;
  content separated from presentation, portable across renderers
- **`scripts/validate_deck.py`** — stdlib-only DSL validator + QA report
- **`scripts/render_html.py`** — self-contained HTML deck: 16:9 canvas,
  theme tokens, inline SVG charts, keyboard nav, speaker notes, print mode
- **`scripts/export_pptx.mjs`** — editable PPTX (text/tables/charts stay
  editable; requires `npm i pptxgenjs`)
- **8 reference docs** — pipeline, DSL guide, slide taxonomy, visual
  strategy, typography (incl. Thai rules), brand tokens, QA, craft methods
- **`examples/pitchcraft-demo/`** — full worked example: sources →
  deck.json → rendered deck → QA report

## Install (any agent, via skills CLI)

```bash
npx skills add kanomwhandev/pitchcraft
```

Or clone and point your agent at the folder. Manual: copy this repo into
your skills directory (e.g. `.agents/skills/pitchcraft/`).

## Use

Tell your agent, in any workspace with material to present:

> Create a 12-slide presentation from this workspace. Audience: SME
> business owners. Goal: explain GEO and AI search. Use brand assets and
> fonts in this project. Style: premium editorial consulting. Export HTML,
> PPTX and PDF.

The agent runs the PitchCraft pipeline: discovers the workspace, ingests
sources with provenance, picks a narrative spine, plans slides, writes the
DSL, renders, QA-loops, exports.

## Demo

- Rendered demo deck (built by PitchCraft from its own spec):
  **https://kanomwhandev.github.io/pitchcraft/** — redirects to the deck
- Worked example: [`examples/pitchcraft-demo/`](examples/pitchcraft-demo/)

## Pipeline at a glance

| Phase | Output |
| --- | --- |
| 0 discovery + tool check | workspace inventory |
| 1 ingestion (distill, provenance) | `output/sources-map.json` |
| 2 communication brief | `output/brief.md` |
| 3 story architecture | narrative spine + emotional arc |
| 4 slide plan (one job per slide) | `output/slide-plan.md` |
| 5 Slide DSL | `output/deck.json` (validated) |
| 6 theme tokens + assets | theme in deck.json |
| 7 render | `output/deck.html` (+ PPTX/PDF) |
| 8 QA loop (visual+content+deck) | `output/qa-report.md` |
| 9 export + previews | `output/preview/*.png` |

## Quality bar

Professional consulting / premium editorial / startup strategy decks —
never the stereotypical AI deck (giant title, three generic bullets,
random illustration, same card grid on every slide). One message per
slide; charts from real data with on-slide sources; Thai typography gets
line-height >= 1.25 and no negative tracking.

## License

MIT
