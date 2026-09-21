# QA — visual, content, deck, repair

Visual quality alone is insufficient; content quality alone is insufficient.
The loop is mandatory: GENERATE -> RENDER -> INSPECT -> FIND -> FIX ->
RENDER AGAIN -> APPROVE. Never assume generated slides are correct.

## Visual QA (per slide, from a rendered screenshot)

Inspect: text overflow / clipped elements / bad line breaks / overlapping
elements / misalignment / inconsistent spacing / text too small (<12px) /
low contrast / bad image crop / unbalanced whitespace / poor hierarchy /
visual clutter / chart readability / brand-token violations / inconsistent
styling / repeated layouts / awkward icon alignment / font fallback
failures (tofu boxes).

States: PASS / WARNING / FAIL. No slide ships with FAIL.

## Content QA (per slide)

- One clear message? Graspable in ~3 seconds?
- Does every element serve the message?
- Factual claims supported? Numbers accurate against sources?
- Missing context? Too dense? Can something be removed without losing
  meaning? (Prefer editing content down over shrinking fonts.)

## Deck-level QA (after slides pass individually)

Narrative flow / visual rhythm / layout diversity (no 4+ run of one
family) / section transitions / density variation / color + typography
consistency / story completeness (does the spine land the desired action?).

Record everything in each slide's `qa` block and `output/qa-report.md`
(the validator writes the schema-level section; add visual/content
findings to it).

## Repair playbook

| Finding | Fix |
| --- | --- |
| overflow / clipping | cut words, then restructure block, last: smaller role |
| wall of bullets | split slide, or convert bullets->steps cards |
| no focal point | demote support, enlarge emphasis, add whitespace |
| chart unreadable | fewer categories, horizontal bars, direct labels |
| rhythm monotony | swap a card-grid slide for statement/timeline |
| brand drift | fix at TOKEN level, never slide by slide |

## Optional: calibrated AI judgments (TypeSafe)

When `TYPESAFE_API_KEY` is available, add a calibrated judgment pass after
human-checkable QA — one request, many questions over the same state
(per-question state = slide DSL + rendered-text description). Ground truth
for API/SDK: https://docs.typesafe.ai (see sdk/python.md or sdk/javascript.md).

- Per slide, one **Score** question per dimension — "clarity" (levels:
  message graspable in 3s / requires a read / unclear), "density" (sparse /
  right / overloaded), "hierarchy" (strong / adequate / weak). Levels must
  describe concrete situations.
- One **Noul** per label when several may apply: "brand_violation",
  "chart_misleading", "clipped_text".
- **Choice** only when routing a repair: pick which repair playbook entry
  applies to this slide's worst finding.

Policy: AI judgments ADVISE; the repair decision and the final PASS/FAIL
stay with the inspecting agent. Confidence near the middle = spread
distribution, not "medium quality" — read the docs' confidence guidance
before thresholding. Never let a judgment override an observed defect, and
never ship a FAIL because a model was unsure: verify visually.

## Source integrity

Claim -> source -> page/section/cell, kept in `output/sources-map.json`.
Never fabricate citations or silently invent statistics. Insufficient
evidence -> mark uncertain or cut the claim. Deck honesty is a quality bar,
not a nice-to-have.
