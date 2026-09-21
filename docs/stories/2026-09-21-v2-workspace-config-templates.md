# Story v2 — Workspace config, templates library, font strategy, Thai demo

- **Status:** in-progress (started 2026-09-21)
- **Source:** user brief (local://paste-2.md) — deltas over shipped v1
- **Decisions locked with user 2026-09-21 (grilling session):**
  Q1 full upgrade under the `pitchcraft` name · Q2 templates = DSL-level
  presets consumed by the agent · Q3 five style presets as token bundles ·
  Q4 font strategy as rules + script, headline→vector documented-only ·
  Q5 self-sourced OFL Thai font (Anuphan) + Thai demo deck · Q6 this story
  file before implementation · Q7 README/landing copy refresh after build.

## Tasks (in order)

1. **Workspace config templates** — `templates/workspace/config/`:
   `deck.config.yaml` (extended from v1), `brand.yaml`, `design-rules.md`,
   `style-presets/{editorial,consulting,data,pitch,educational}.yaml`.
2. **Templates library (DSL presets)** — `templates/workspace/templates/`
   with six families from the brief: `title/ framework/ comparison/
   timeline/ data/ closing/`, each `template.yaml` = layout family default
   + block skeleton + density/spacing hints. Agent-consumed; renderers
   unchanged.
3. **Font strategy script** — `scripts/check_fonts.py`: scan `fonts/`,
   read `theme.typography`, emit strategy (embed list for HTML base64,
   PPTX safe-stack mapping incl. Thai `Leelawadee UI` when language=th,
   `export_strategy` recommendation, PDF-canonical advice) as
   `output/font-strategy.json` + console report.
4. **Renderer touches (minimal)** — export_pptx.mjs: Thai-aware font map
   when `metadata.language` starts `th`. render_html.py: no required
   change (variable fonts already supported via `custom_fonts[].weight`
   range e.g. `"100 900"`; Thai line-height floor already enforced).
5. **Thai demo deck** — `examples/geo-sme-thai/`: sources with cited URLs
   (GEO/AI-search stats, 2026-09-22 web-verified), config/ (adapted from
   templates), fonts/Anuphan.ttf (OFL, Google Fonts), ~10-slide Thai deck
   for SME owners, full output artifacts + previews + QA report.
6. **Docs** — SKILL.md (workspace conventions + Phase 6 font/config
   steps), references/brand-tokens.md (+brand.yaml/palette.json),
   references/typography.md (+strategy chain), references/slide-dsl.md
   (+style_preset), CHANGELOG.md (new).
7. **Copy refresh** — README.md + index.html per copywriting principles
   (clarity, specificity, one idea per section, strong CTA).
8. **Regression + test plan** (below).
9. **Deploy** — commit, push, reinstall to `.agents/skills/pitchcraft`,
   update workspace AGENTS.md entry.

## Acceptance criteria

- AC1 `validate_deck.py` passes both decks (v1 demo + Thai demo), 0 FAIL.
- AC2 `check_fonts.py` on the Thai workspace emits a strategy JSON that
  names Anuphan (embed), a Thai-safe PPTX stack, and an export_strategy.
- AC3 Thai deck renders with Anuphan visible in the screenshot (not
  fallback tofu), line-height ≥ 1.25 honored; PPTX opens with Thai-safe
  fonts and notes.
- AC4 Every factual claim in the Thai deck maps to a URL in
  `sources-map.json`; chart numbers match sources.
- AC5 v1 regression: v1 demo revalidates, re-renders, PPTX re-exports
  without defects; preview set unchanged in content.
- AC6 Templates + presets are valid YAML, loadable by an agent, and the
  Thai demo's deck.json demonstrably derives from at least 3 of them.
- AC7 README/landing mention v2 capabilities truthfully; Pages serves the
  Thai demo (second Pages entry point or linked path).

## Test plan

- `python scripts/validate_deck.py` on both decks (schema + content rules)
- `python scripts/check_fonts.py` on Thai workspace; inspect JSON output
- `python scripts/render_html.py` + puppeteer captures; vision QA pass on
  Thai slides (Thai glyph rendering, contrast, overflow)
- `node scripts/export_pptx.mjs`; zip-inspection: slides count, notes,
  chart, Thai text present
- Manual: load both decks in browser, keyboard nav, notes toggle, print
  mode (PDF via headless chrome)

## Non-goals (v2)

- Headline→vector conversion (documented in design-rules only)
- Template library beyond six families; interactive/preset extras
- TypeSafe judgment tier changes (stays optional, as documented)
