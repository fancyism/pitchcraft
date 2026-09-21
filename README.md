# PitchCraft — Marketing Presentation Engine

Point your AI agent at a folder of sources. Get a marketing deck with a
validated structure, real sources on every number, and a QA loop that
catches broken slides before your audience does.

```
sources/ → ingest → story → slide plan → deck.json (Slide DSL)
        → theme + assets → render HTML/PPTX/PDF → visual QA → export
```

## Why it's different

Most AI decks fail the same three ways: no argument (bullets without a
spine), no accountability (numbers without sources), no inspection
(generated but never looked at). PitchCraft fixes all three structurally:

- **One job per slide.** Every slide carries a written message in a
  validated Slide DSL — if the sentence can't be stated, the slide isn't
  designed yet.
- **Every number has a source.** Claims map to provenance
  (`sources-map.json`); charts cite on-slide. The validator and QA loop
  enforce it.
- **Nothing ships un-inspected.** The pipeline renders, screenshots and
  checks every slide (overflow, contrast, rhythm, Thai tone marks) and
  repairs before export.

## What's in the box

- **SKILL.md** — the agent-facing pipeline (Claude Code, Codex, OpenCode,
  OMP, Cursor, any skills-compatible agent)
- **Slide DSL** — `schemas/deck.schema.json` + `slide.schema.json`;
  content separated from presentation, portable across renderers
- **Scripts (stdlib)** — `validate_deck.py` (schema + QA report),
  `render_html.py` (self-contained deck.html: keyboard nav, speaker
  notes, print-to-PDF), `check_fonts.py` (font strategy chain),
  `export_pptx.mjs` (editable PPTX; needs `npm i pptxgenjs`)
- **Workspace layer (v2)** — `templates/workspace/` with `config/`
  (deck.config.yaml, brand.yaml, design-rules.md) + 5 style presets
  (editorial · consulting · data · pitch · educational) + a `templates/`
  DSL preset library (title, framework, comparison, timeline, data,
  closing)
- **Thai support** — Anuphan embedded end-to-end, line-height ≥ 1.25
  enforced, PPTX maps to Leelawadee UI
- **8 reference docs + 2 worked examples** — see below

## Install & first deck (BMad-style flow)

**1 · Scaffold a workspace in your project** (interview asks 8 short
questions, then builds the full workspace: config, brand, templates,
style presets, START.md with a copy-paste prompt for your agent):

```bash
npx github:fancyism/pitchcraft init          # interactive (th/en)
npx github:fancyism/pitchcraft init --yes    # defaults, zero prompts
npx github:fancyism/pitchcraft check         # workspace readiness
```

**2 · Install the skill into your agent** (once per machine):

```bash
npx skills add fancyism/pitchcraft
```

**3 · Drop your material into `sources/`** (PDF/DOCX/CSV/MD + optional
`fonts/`, `brand/`, `data/`) and tell your agent:

> สร้าง presentation จาก workspace นี้ (pitchcraft/) ด้วย PitchCraft —
> ผู้ฟัง, เป้าหมาย, style ตาม config — Export HTML, PPTX, PDF + previews

The interview pre-fills `config/deck.config.yaml`; every later edit
happens in `config/`, never in generated files.

## Demos (both built by PitchCraft, both live)
- **English** — PitchCraft pitches itself from its own spec, every claim
  citing a spec section:
  https://fancyism.github.io/pitchcraft/examples/pitchcraft-demo/output/deck.html
- **Thai** — GEO for Thai SME owners, Anuphan variable font embedded,
  every statistic URL-sourced:
  https://fancyism.github.io/pitchcraft/examples/geo-sme-thai/output/deck.html
- Landing: https://fancyism.github.io/pitchcraft/

## Pipeline at a glance

| Phase | Output |
| --- | --- |
| 0 discovery + tool check | workspace inventory |
| 1 ingestion (distill, provenance) | `output/sources-map.json` |
| 2 brief | `output/brief.md` |
| 3 story (spine + emotional arc) | narrative in deck.json |
| 4 slide plan (from templates/) | `output/slide-plan.md` |
| 5 Slide DSL | `output/deck.json` (validated) |
| 6 style preset + brand.yaml + fonts | theme + `font-strategy.json` |
| 7 render | `output/deck.html` (+ PPTX/PDF) |
| 8 QA loop (visual+content+deck) | `output/qa-report.md` |
| 9 export + previews | `output/preview/*.png` |

## Quality bar

Professional consulting / premium editorial / startup strategy decks —
never giant-title-three-bullets AI filler. Charts from real data with
on-slide sources. Image generators make images; the layout engine owns
text and structure — never the whole slide.

## License

MIT · changelog: [CHANGELOG.md](CHANGELOG.md)
