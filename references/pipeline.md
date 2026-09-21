# PitchCraft Pipeline

Execute phases in order. Never start by generating slides. Checkpoint artifacts
live in `output/` so any phase can be resumed without redoing the deck.

## Phase 0 — Workspace discovery

Map the workspace before touching content:

```
sources/   PDFs, DOCX, XLSX/CSV, Markdown, TXT, existing decks
fonts/     woff2/woff/ttf/otf files
brand/     logos, palettes, guidelines, icon rules
references/ presentation screenshots for style analysis
assets/    images, SVGs, screenshots
data/      datasets backing charts
templates/ deck.config.yaml overrides
output/    everything the pipeline writes
```

Do NOT generate slides yet. First: inventory files, brand resources, fonts,
datasets. Then **tool discovery**: verify what the runtime actually has —
node/npm (pptxgenjs export), headless browser or browser MCP (previews/PDF),
image-generation tool, web search (claim verification). Never invent
capabilities; degrade to HTML+JSON only and say so.

## Phase 1 — Source ingestion

Read every relevant source. Extract: claims, statistics, definitions,
frameworks, quotes, timelines, comparisons, processes, recommendations,
datasets, citations. Track provenance for every important factual claim
(`claim -> source file -> page/section/cell`) in `output/sources-map.json`.
Never fabricate facts or citations. If evidence is thin, mark the claim
uncertain — do not round it into confidence.

Distill long sources first (see `methods.md` #11): lossless bullet
compression, self-contained bullets, completeness check against source
headings and named entities before use.

## Phase 2 — Communication brief

Determine or infer, then write `output/brief.md`:

```json
{
  "audience": "SME business owners",
  "knowledge_level": "knows SEO, not AI search",
  "objective": "explain why GEO matters",
  "desired_action": "start a GEO audit",
  "tone": "expert but accessible",
  "slides": 12,
  "aspect_ratio": "16:9",
  "language": "th",
  "style": "editorial consulting",
  "outputs": ["html", "pptx", "pdf", "previews"]
}
```

## Phase 3 — Story architecture

Choose ONE narrative spine by communication intent (see `methods.md` #2-#4):

| Intent | Spine |
| --- | --- |
| Persuade / sell | Problem -> Insight -> Evidence -> Solution -> Action |
| Explain | Why -> What -> How -> Example -> Next step |
| Pitch | Problem, Market, Solution, Product, Proof, Model, GTM, Competition, Financials, Ask |
| Advise | Exec summary -> Evidence -> Analysis -> Recommendation |
| Teach | Teach -> Demonstrate -> Apply |

Write the emotional arc explicitly: opening emotion, turning-point shift,
carry-away emotion. If the material is a pitch, the deck's spine is the pitch
narrative; do not force everything into problem-solution.

## Phase 4 — Slide plan

`output/slide-plan.md`: one row per slide — id, beat in the arc, layout
family, visual strategy, message (one sentence), source refs. Every slide
gets exactly ONE primary communication job; if a slide needs two messages,
it is two slides.

## Phase 5 — Slide DSL

Serialize the plan into `output/deck.json` per `schemas/deck.schema.json`
(guide: `slide-dsl.md`). Validate:

```
python scripts/validate_deck.py output/deck.json --report output/qa-report.md
```

## Phase 6 — Theme + assets

Compile brand/ and fonts/ into theme tokens (`brand-tokens.md`), analyze
references/ into design principles, generate image assets only where an
information-design treatment is not better (`visual-strategy.md`). Charts
come from real `data/` values, never invented.

## Phase 7 — Render

```
python scripts/render_html.py output/deck.json --root . -o output/deck.html
node scripts/export_pptx.mjs output/deck.json        # if npm + pptxgenjs present
```

## Phase 8 — Visual QA loop

GENERATE -> RENDER -> INSPECT -> FIND PROBLEMS -> FIX -> RENDER AGAIN ->
APPROVE. Screenshot every slide (browser tool or headless chrome); inspect
against the checklists in `qa.md`. No slide ships with FAIL. Deck-level pass
checks rhythm and repetition (a run of 4+ identical layouts is a WARNING).

## Phase 9 — Export + handoff

Produce the agreed outputs; keep `deck.json` (the source of truth),
`slide-plan.md`, `qa-report.md`, `sources-map.json`, `preview/` in `output/`.
PDF = print mode of deck.html (each slide is one page; headless chrome
`--print-to-pdf` honors it).
