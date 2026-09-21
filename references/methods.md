# Craft methods — distilled technique bank

Fifteen method pointers distilled from the BMad/CIS skill family
(presentation-master, storytelling, design-thinking, problem-solving,
distillator, create-story, market/domain/technical research). Apply them
inside the pipeline phases; each names its source technique.

## Frame craft (presentation-master)

1. **3-second rule** — the core idea of every slide must be graspable in
   ~3 seconds. Every frame has a job (inform, persuade, transition) or it
   gets cut. Design the eye's journey; whitespace builds focus.
2. **Hook -> tension -> payoff** as the universal deck spine: open with a
   hook that surprises or challenges, build the tension the audience
   recognizes, deliver the payoff only the deck's argument makes possible.
3. Audience-first framing: a pitch deck, a YouTube thumbnail and a
   conference talk are different instruments. Set framing in the brief
   (Phase 2) before designing any slide.

## Story craft (storytelling)

4. **Framework menu** matched to purpose x audience: Hero's Journey,
   Pixar Story Spine ("Once upon a time... Every day... Until one day...
   Because of that... Until finally..."), Customer Journey Story, Pitch
   Narrative, Brand/Origin/Vision Story, Data Storytelling. Recommend as:
   "for {audience} + {purpose}, use {framework} because {rationale}".
5. **Emotional arc by design**: name the opening emotion, the
   turning-point shift, and the carry-away emotion (Phase 3).
6. **One story, three lengths** — the same narrative as short (social
   caption), medium (exec summary email), extended (the deck). Ship the
   short + medium as leave-behinds when the deck lands.

## Problem craft (design-thinking + problem-solving)

7. **POV statement** for the problem slide: "[User type] needs [need]
   because [insight]" — then open the solution space with How-Might-We.
8. **Empathy map** (say/think/do/feel) to ground audience analysis when
   the brief is thin on real audience knowledge.
9. **Is/Is Not** to bound claims; Five Whys / Fishbone when a slide must
   explain a root cause; Decision Matrix and Force Field Analysis are
   ready-made trade-off slide structures.

## Evidence craft (research family)

10. **Web-verify before slide**: any market/competitive/technical claim in
    a deck gets verified against a live source when the runtime has web
    access; show the verification before the slide ships.
11. **Claim-evidence pairing**: every assertion slide carries a source
    line (`chart_spec.source` / `sources[]`) — `_Source: [URL/section]_`
    discipline, adapted to `sources-map.json`.
12. **Executive Summary + methodology + evidence-close**: research decks
    open with an executive summary and close with
    goals-achieved-with-evidence, risks, and next-step KPIs.

## Preparation craft (distillator + create-story)

13. **Distill before you design**: losslessly compress long sources to
    self-contained bullets (completeness check against source headings and
    named entities) before story architecture — noise in, noise out.
14. **Previous-deck intelligence**: when the workspace or repo has past
    decks/artifacts, mine them for established patterns (spines, token
    sets, chart conventions) before designing; consistency compounds.

## Session craft (CIS workflows + elicitation)

15. **Checkpoint per phase**: save the phase artifact (brief.md,
    slide-plan.md, deck.json), then checkpoint — continue, or run an
    elicitation pass (red-team the narrative, pre-mortem the pitch,
    5-Whys a weak slide, SCAMPER the structure) and fold improvements in
    before the next phase. Gate completion on the QA checklist; flip to
    ready only after validation.

## Grilling the deck (pre-ship stress test)

Before export, attack the deck: Which slide would a skeptic challenge?
Which number is weakest? Where does the spine assume something the audience
hasn't accepted yet? Fix or arm the speaker notes for those exact points
(Pre-mortem + Challenge-from-Critical-Perspective from the elicitation
registry). A deck that survives grilling lands.
