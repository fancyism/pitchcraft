# Slide DSL authoring guide

`deck.json` is the deck. Renderers are interchangeable views of it. Keep
CONTENT separate from PRESENTATION: the DSL describes meaning and structure;
layout families map structure to visuals.

Canonical contract: `schemas/deck.schema.json` + `schemas/slide.schema.json`.
Validate with `scripts/validate_deck.py` (stdlib-only, mirrors the schemas).

## Deck

```json
{
  "metadata": { "title": "...", "audience": "...", "objective": "...",
    "desired_action": "...", "language": "en", "aspect_ratio": "16:9",
    "style": "premium editorial consulting", "style_preset": "editorial" },
  "theme": { "colors": {}, "typography": {} },
  "narrative": { "structure": "Problem -> Insight -> Evidence -> Solution -> Action",
                 "arc": ["beat per slide, one entry per slide"] },
  "slides": [ ... ]
}
```

## Slide

Required: `id, type, purpose, message, title, layout_family,
visual_strategy, content`. Optional: `eyebrow, subtitle, evidence, sources,
assets, chart_spec, image_spec, emphasis, speaker_notes, qa`.

- `message` — the ONE sentence the slide must land. If you cannot write it,
  the slide is not designed; do not proceed to rendering.
- `type` — semantic family (taxonomy). `layout_family` — concrete renderer
  layout. `visual_strategy` — how meaning becomes visual. Choose by intent,
  never randomly; see `taxonomy.md`.
- `content` — ordered blocks. The renderer picks the primary block per
  layout family; extra blocks render beneath.

## Content blocks

| kind | fields | notes |
| --- | --- | --- |
| `text` | text | lead paragraph |
| `bullets` | items[] (max 6) | parallel, self-contained lines |
| `steps` | items[]{label?, title, text?} (2-7) | cards / flow / lanes / panels |
| `metrics` | items[]{value, label, delta?, source?} | KPI numbers |
| `table` | columns[], rows[][] | comparison table |
| `matrix` | axes{x,y: low/high}, cells[4]{x,y,title,text} | 2x2 |
| `quote` | text, attribution | |
| `callout` | title?, text, tone | takeaway / warning / positive |

## chart_spec

```json
{ "type": "column", "title": "…", "takeaway": "the one sentence this chart proves",
  "source": "data/report.csv — shown on-slide",
  "data": { "labels": ["Q1","Q2"], "series": [{"name":"Revenue","values":[120,180]}], "unit": "%" } }
```

Type follows analytical purpose: trend->line/area, comparison->bar/column,
composition->stacked-bar/donut, stage flow->funnel. Values must come from
`data/` or a cited source; `source` is required on-slide (validator warns).

## image_spec (brief for generated assets)

Generators make IMAGES; the layout engine owns TEXT + STRUCTURE. Never ask a
generator to produce a whole slide. `text_in_image` must be false.

```json
{ "purpose": "hero_visual", "subject": "…", "aspect_ratio": "16:9",
  "composition": "subject-right", "safe_area": "left 42%",
  "text_in_image": false, "background_complexity": "medium" }
```

Good: editorial hero, conceptual/metaphor visual, environment, background.
Bad: body text, tables, frameworks, KPIs, charts, labels — anything that
must stay editable.

## assets

`[{ "role": "hero|supporting|background|logo", "path": "assets/x.png",
"alt": "…", "credit": "…" }]` — local paths resolve against the workspace
root and are base64-embedded into deck.html.

## qa

`{ "status": "PASS|WARNING|FAIL", "checks": [{name, result, note}], "notes": }`
— filled during the QA loop. FAIL blocks export (validator enforces).

## Style discipline

- ids: kebab-case slugs, stable across revisions.
- Titles <= 70 chars where possible; bullets are lines, not paragraphs.
- Numbers formatted once, consistently across slides.
- Provenance: any claim a skeptic would challenge goes in `evidence[]` +
  `sources[]` (methods.md #9).
