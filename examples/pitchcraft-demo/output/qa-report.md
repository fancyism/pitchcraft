# PitchCraft QA Report — demo deck

- **Deck:** `examples/pitchcraft-demo/output/deck.json` (12 slides, 16:9)
- **Inspected:** rendered `deck.html`, screenshot per slide (1280×720, Chromium),
  2026-09-20 (initial) and 2026-09-21 (post-repair re-inspection)
- **Verdict: PASS — 0 FAIL, 2 WARNING** (both accepted, rationale below)

## Pipeline findings (scripts/validate_deck.py)

VALID: 0 fail(s), 0 warning(s), 12 slide(s). Chart data shape, block
contracts, taxonomy enums, layout diversity, and provenance lines all
schema-clean on final deck.json.

## Visual + content QA loop (GENERATE → RENDER → INSPECT → FIX → RENDER → APPROVE)

Iteration 1 findings and repairs (all fixed and re-inspected):

| # | Slide | Finding | Repair | Re-inspect |
| --- | --- | --- | --- | --- |
| 1 | cover | Light text on light surface (no bg image) — illegible | Cover family now paints the primary ink background; light text correct in image and no-image cases | PASS |
| all | HUD | Full-width progress bar overlapped slide footers (sources / page numbers) — looked like ghosted text | HUD redesigned to a compact centered pill; redundant counter removed | PASS |
| 5,6 | cards | Step labels inline on short titles, stacked on long ones — inconsistent anatomy | `.step-head` forced to block layout; labels always above titles | PASS |
| 6 | process | Connector arrows overlapped next card's text (25px arrow in 18px gap) | Flow gap widened to 36px; arrow offset −31px | PASS |
| — | global | Inner padding (56/64px) vs footer inset (72px) misaligned | Unified on `--pad: 64px` | PASS |
| 10 | quote | Attribution duplicated the sources footer | `sources[]` dropped; attribution carries the provenance | PASS |

Capture-integrity lesson (recorded for the skill): identical file sizes
across "different" slides = broken capture, not a clean deck — the first
re-capture round produced byte-identical blanks because hash-only
navigation does not reload. The renderer now listens to `hashchange`, and
the capture script cache-busts per slide. Verify capture variance before
trusting vision QA.

## Final per-slide status

| # | id | Layout | Status | Notes |
| --- | --- | --- | --- | --- |
| 1 | cover | cover | PASS | dark ink cover, light type |
| 2 | the-tell | statement | PASS | |
| 3 | three-seconds | big-number | PASS | |
| 4 | bullets-vs-system | problem-solution | PASS | accent border on Solution panel is intentional differentiation |
| 5 | six-layers | framework-grid | PASS | |
| 6 | pipeline | process-flow | PASS | |
| 7 | coverage | chart | PASS | native column chart, on-slide source |
| 8 | before-after | before-after | WARNING | center badge optically biased left (grid centers it; panel content weight differs) — accepted |
| 9 | proof | case-study | WARNING | metric label baselines vary optically across digits (12/6/0/100%) — accepted, sub-perceptual |
| 10 | mandate | quote | PASS | |
| 11 | ships-today | roadmap | PASS | |
| 12 | cta | closing-cta | PASS | |

## Deck-level QA

- Narrative flow: pitch spine intact (Problem → Insight → Solution → Product → Proof → Ask), arc recorded in deck.json.
- Visual rhythm: 12 distinct layout families, no repeat ≥ 2; open frames (2, 3, 10) break the dense middle.
- Typography: one display role, controlled scale, no font below 12.5px.
- Brand: default editorial tokens only; no off-token colors introduced.
- Source integrity: every claim mapped in sources-map.json; chart source on-slide; no fabricated numbers (schema enum counts).

## Exports

- `deck.html` — self-contained (25 KB), keyboard nav, notes (`n`), print-to-PDF mode
- `deck.pptx` — 12 editable slides + 12 notes + 1 native chart (pptxgenjs)
- `deck.json` — Slide DSL, validated
- `preview/slide-01..12.png` — Chromium captures at 1280×720
