# PitchCraft Specification (distilled source)

Source of truth for the PitchCraft demo deck. Distilled 2026-09-20 from the
full production spec ("BUILD A PRODUCTION-GRADE PRESENTATION SKILL", 33
sections + final mandate). Every demo-deck claim cites a section below.

## §2 Core design principle

Never treat presentation generation as "LLM writes some bullets, puts
bullets on slides." Treat presentations as structured visual communication
systems. Every slide has: purpose, message, evidence, content, visual
strategy, layout, hierarchy, rendering method. ONE SLIDE = ONE PRIMARY
COMMUNICATION JOB.

## §3 Pipeline

SOURCE -> RESEARCH/EXTRACTION -> STORYLINE -> SLIDE ARCHITECTURE ->
VISUAL STRATEGY -> ASSET GENERATION -> LAYOUT -> RENDER -> VISUAL QA ->
REPAIR -> EXPORT. Do not immediately generate slides; first understand the
project.

## §4 Slide DSL

A reusable intermediate representation (Deck -> Metadata, Theme, Narrative,
Slides[] with typed fields). The DSL separates CONTENT from PRESENTATION
RENDERING, making the deck portable across HTML, PPTX, PDF, images.

## §5 Slide taxonomy

Reusable slide families: cover, section divider, executive summary, big
statement, big number, key insight, framework, process, timeline, journey,
funnel, comparison, before-after, matrix, 2x2, table, data chart, KPI
dashboard, quote, case study, problem-solution, feature breakdown,
architecture, ecosystem, workflow, roadmap, strategy, recommendation,
checklist, FAQ, closing, CTA — 31 families. Layouts are selected by
semantic intent, not randomly.

## §6 Visual strategy engine

Per slide, choose a visual representation from 16 strategies (typography-
only, structured cards, diagram, SVG infographic, data visualization,
timeline, matrix, process flow, editorial photography, generated
illustration, conceptual visual, iconography, UI mockup, device mockup,
comparison table, architecture map). Do not generate decorative images when
information design would communicate the idea better.

## §9 Data visualization

Charts are generated from actual data: bar, column, line, area, scatter,
bubble, donut, waterfall, funnel, stacked bars, heatmap, tables, KPI
blocks — 7 types ship in the v1 renderers. Chart selection depends on
analytical purpose (trend -> line, comparison -> bar, composition ->
stacked/donut). Never decorative; no misleading axes; show sources.

## §10 Typography

Typography roles (display, headline, subheadline, body, label, caption,
number, quote), a controlled type scale, consistent fonts across slides.
Thai typography needs particular attention: line height, word wrapping,
leading, mixed Thai-English text. Fallback fonts mandatory.

## §19-21 QA loops

Visual QA is mandatory: GENERATE -> RENDER -> INSPECT -> FIND PROBLEMS ->
FIX -> RENDER AGAIN -> APPROVE. Inspect 18 visual defect classes per slide;
content QA (one clear message, several-second comprehension, supported
claims); deck-level QA (narrative flow, visual rhythm, layout diversity —
"card grid x5" is the named bad pattern). States PASS/WARNING/FAIL; no
final slide ships with FAIL.

## §22 Source integrity

Claim -> source -> page/section/cell provenance. Never fabricate citations;
never silently invent statistics; insufficient evidence -> mark uncertain.

## §23 Output structure

output/: deck.pptx, deck.pdf, deck.html, deck.json (the DSL), slide-plan.md,
qa-report.md, sources-map.json, preview/slide-NN.png.

## §26 Tool discovery

Inspect the runtime environment before implementation; do not invent
nonexistent APIs; degrade gracefully.

## §30 Design quality bar

Target: professional consulting presentation, premium editorial
presentation, high-end educational presentation, startup strategy deck,
agency/client presentation. Avoid the stereotypical low-quality AI deck:
giant title, three generic bullets, random illustration, same card grid
repeated, poor information hierarchy. The deck should feel intentionally
art-directed.

## §33 + Final Mandate

Do not stop after writing documentation; the final goal is a WORKING
SKILL. The core moat: SOURCE INTELLIGENCE + STORY INTELLIGENCE + SLIDE DSL
+ VISUAL STRATEGY + MULTI-RENDERER + VISUAL QA LOOP — six layers.
"Build this as a reusable AI presentation engine, not a one-off slide
generator."
