# Slide taxonomy — intent to layout

Pick by what the slide must DO, not by what looks pretty. `type` is the
semantic job; `layout_family` is the renderer layout; `visual_strategy` is
the treatment. Supported triples (anything else: choose the closest and note
it in `purpose`):

| type | layout_family | visual_strategy | Use when |
| --- | --- | --- | --- |
| cover | cover | editorial-photography / typography-only | opening frame |
| section-divider | divider | typography-only | chapter break |
| executive-summary | key-insight | structured-cards | whole argument in one frame |
| big-statement | statement | typography-only | one sentence must land alone |
| big-number | big-number | typography-only | a single number IS the message |
| key-insight | key-insight | structured-cards | title + lead + support, asymmetric |
| framework | framework-grid | svg-infographic / structured-cards | named model with 2-6 parts |
| process | process-flow | process-flow | ordered steps, arrows |
| timeline | timeline | timeline | chronology, milestones |
| journey | timeline / process-flow | timeline | customer/stakeholder journey |
| funnel | funnel | data-visualization | stage conversion |
| comparison | comparison | comparison-table | two options side by side |
| before-after | before-after | comparison-table | delta story |
| matrix | matrix-2x2 | matrix | 2 axes, 4 quadrants |
| table | table | comparison-table | more than 2 dimensions |
| data-chart | chart | data-visualization | numbers prove the point |
| kpi-dashboard | kpi-dashboard | data-visualization | 2-4 headline metrics |
| quote | quote | typography-only | borrowed authority |
| case-study | case-study | structured-cards | challenge -> approach -> results |
| problem-solution | problem-solution | comparison-table | tension then resolution |
| feature-breakdown | feature-grid | structured-cards | 3-6 parallel capabilities |
| architecture | framework-grid | architecture-map | system structure |
| ecosystem | framework-grid | architecture-map | actors and relations |
| workflow | process-flow | process-flow | who does what, in order |
| roadmap | roadmap | timeline | phases over time |
| strategy | framework-grid / matrix-2x2 | structured-cards | choices under constraint |
| recommendation | key-insight | structured-cards | the answer, crisply |
| checklist | checklist | iconography | what to do Monday morning |
| faq | feature-grid | structured-cards | 3-5 question cards |
| closing | statement / closing-cta | typography-only | the leave-behind |
| cta | closing-cta | typography-only | the ask + next step |

## Density and rhythm

- One primary communication job per slide (the `message` field).
- Main point graspable in ~3 seconds (methods.md #1).
- Vary visual rhythm across the deck: never 4+ identical layout families in
  a row (validator warns). Alternate open (statement/quote) and dense
  (framework/chart) frames.
- Prefer cutting content over shrinking type. Density guidance: <= 6
  bullets, <= 7 steps, <= 6 metrics, table <= 5 columns.

## Choosing layout for the same content

The same six facts can be a `framework-grid` (they form a model), a
`process-flow` (they happen in order), or a `checklist` (you must do them).
The AUDIENCE'S next action decides: understand -> grid; execute -> flow or
checklist; decide -> comparison/matrix.
