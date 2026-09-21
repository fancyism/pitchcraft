# Changelog
## v2.1 — 2026-09-21 — BMad-style installer

Added `bin/pitchcraft.js` (zero-dep Node CLI):
- `init [dir]` — interactive interview (th/en, 8 questions) scaffolds a
  full presentation workspace: folders, config/deck.config.yaml +
  brand.yaml pre-filled from answers, design rules, 5 style presets,
  6 template families, START.md with a copy-paste agent prompt;
  `--yes` / `--style= --lang= --title= --audience= --slides=` flags;
  piped-stdin safe for CI
- `check [dir]` — workspace readiness report
- Run without npm publish: `npx github:fancyism/pitchcraft <cmd>`

## v2 — 2026-09-22 — Workspace config, templates, font strategy, Thai demo

Added:
- `config/` workspace layer: `deck.config.yaml`, `brand.yaml`,
  `design-rules.md`, and five style presets (`editorial, consulting,
  data, pitch, educational`) as token bundles
- `templates/` DSL preset library (title, framework, comparison,
  timeline, data, closing) — agent-consumed, renderers unchanged
- `scripts/check_fonts.py`: font strategy chain (preferred -> embed ->
  safe stack -> PDF canonical), Thai-aware PPTX mapping, emits
  `output/font-strategy.json`
- `examples/geo-sme-thai/`: Thai demo deck (10 slides, Anuphan variable
  font embedded, every claim URL-sourced, full QA artifacts) — proves
  Thai typography rules end-to-end
- `docs/stories/` implementation stories, this changelog

Changed:
- `export_pptx.mjs`: Thai-language decks map to a Thai-capable system
  font stack (Leelawadee UI) instead of Verdana
- `SKILL.md`: workspace conventions + Phase 4/6 wiring for templates,
  presets, brand.yaml, font strategy
- Schema: optional `metadata.style_preset` for config traceability
- README + landing page copy

v1 demos and renderer outputs remain compatible (v1 example re-validated
and re-rendered unchanged).

## v1 — 2026-09-21 — Initial release

Skill + Slide DSL (schemas) + validator + self-contained HTML renderer +
editable PPTX exporter (pptxgenjs) + QA loop references + EN demo deck
built from the engine's own spec.
