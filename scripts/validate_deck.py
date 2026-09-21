#!/usr/bin/env python3
"""PitchCraft deck validator.

Validates a deck.json against the Slide DSL contract (schemas/*.schema.json)
using only the Python standard library, so it runs anywhere.

Usage:
  python scripts/validate_deck.py output/deck.json
  python scripts/validate_deck.py output/deck.json --report output/qa-report.md

Exit codes: 0 = valid (may carry WARNINGs), 1 = invalid (FAILs or schema errors).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SLIDE_TYPES = {
    "cover", "section-divider", "executive-summary", "big-statement", "big-number", "key-insight",
    "framework", "process", "timeline", "journey", "funnel", "comparison", "before-after", "matrix",
    "table", "data-chart", "kpi-dashboard", "quote", "case-study", "problem-solution",
    "feature-breakdown", "architecture", "ecosystem", "workflow", "roadmap", "strategy",
    "recommendation", "checklist", "faq", "closing", "cta",
}
LAYOUT_FAMILIES = {
    "cover", "divider", "statement", "big-number", "key-insight", "framework-grid",
    "process-flow", "timeline", "funnel", "comparison", "before-after", "matrix-2x2",
    "table", "chart", "kpi-dashboard", "quote", "case-study", "problem-solution",
    "feature-grid", "roadmap", "checklist", "closing-cta",
}
VISUAL_STRATEGIES = {
    "typography-only", "structured-cards", "diagram", "svg-infographic", "data-visualization",
    "timeline", "matrix", "process-flow", "editorial-photography", "generated-illustration",
    "conceptual-visual", "iconography", "ui-mockup", "device-mockup", "comparison-table", "architecture-map",
}
BLOCK_KINDS = {"text", "bullets", "steps", "metrics", "table", "matrix", "quote", "callout"}
CHART_TYPES = {"bar", "column", "line", "area", "donut", "stacked-bar", "funnel"}
QA_STATUSES = {"PASS", "WARNING", "FAIL"}


class Findings:
    def __init__(self) -> None:
        self.items: list[tuple[str, str, str]] = []  # (slide_id, level, message)

    def add(self, slide: str, level: str, message: str) -> None:
        self.items.append((slide, level, message))

    @property
    def fails(self) -> int:
        return sum(1 for _, lvl, _ in self.items if lvl == "FAIL")

    @property
    def warnings(self) -> int:
        return sum(1 for _, lvl, _ in self.items if lvl == "WARNING")


def _check_block(f: Findings, sid: str, block: dict) -> None:
    kind = block.get("kind")
    if kind not in BLOCK_KINDS:
        f.add(sid, "FAIL", f"content block has invalid kind {kind!r}")
        return
    if kind == "text" and not str(block.get("text", "")).strip():
        f.add(sid, "FAIL", "text block is empty")
    if kind == "bullets":
        items = block.get("items", [])
        if not 1 <= len(items) <= 6:
            f.add(sid, "FAIL", f"bullets must have 1-6 items, got {len(items)}")
    if kind == "steps":
        items = block.get("items", [])
        if not 2 <= len(items) <= 7:
            f.add(sid, "FAIL", f"steps must have 2-7 items, got {len(items)}")
        if any(not str(i.get("title", "")).strip() for i in items):
            f.add(sid, "FAIL", "every step needs a title")
    if kind == "metrics":
        items = block.get("items", [])
        if not 1 <= len(items) <= 6:
            f.add(sid, "FAIL", f"metrics must have 1-6 items, got {len(items)}")
        if any(not str(i.get("value", "")).strip() or not str(i.get("label", "")).strip() for i in items):
            f.add(sid, "FAIL", "every metric needs value and label")
    if kind == "table":
        cols = block.get("columns", [])
        rows = block.get("rows", [])
        if len(cols) < 2:
            f.add(sid, "FAIL", "table needs >= 2 columns")
        if any(len(r) != len(cols) for r in rows):
            f.add(sid, "FAIL", "table row length differs from column count")
    if kind == "matrix":
        cells = block.get("cells", [])
        axes = block.get("axes", {})
        if len(cells) != 4:
            f.add(sid, "FAIL", "matrix needs exactly 4 cells")
        for axis in ("x", "y"):
            ax = axes.get(axis, {})
            if not (ax.get("low") and ax.get("high")):
                f.add(sid, "FAIL", f"matrix axis {axis!r} needs low and high labels")
    if kind == "quote" and not str(block.get("text", "")).strip():
        f.add(sid, "FAIL", "quote block is empty")
    if kind == "callout" and not str(block.get("text", "")).strip():
        f.add(sid, "FAIL", "callout block is empty")


def _check_chart(f: Findings, sid: str, chart: dict) -> None:
    ctype = chart.get("type")
    if ctype not in CHART_TYPES:
        f.add(sid, "FAIL", f"chart type {ctype!r} is not supported")
        return
    data = chart.get("data", {})
    labels = data.get("labels", [])
    series = data.get("series", [])
    if not labels or not series:
        f.add(sid, "FAIL", "chart needs labels and series")
        return
    if ctype == "funnel" and len(series) > 1:
        f.add(sid, "FAIL", "funnel chart takes exactly one series")
    for s in series:
        vals = s.get("values", [])
        if len(vals) != len(labels):
            f.add(sid, "FAIL", f"series {s.get('name', '?')!r} has {len(vals)} values but there are {len(labels)} labels")
        if not all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in vals):
            f.add(sid, "FAIL", f"series {s.get('name', '?')!r} has non-numeric values")
    if not str(chart.get("source", "")).strip():
        f.add(sid, "WARNING", "chart has no source line; on-slide provenance is expected")


def validate(deck: dict) -> Findings:
    f = Findings()
    if not isinstance(deck, dict):
        f.add("deck", "FAIL", "deck.json must be a JSON object")
        return f

    for key in ("metadata", "theme", "slides"):
        if key not in deck:
            f.add("deck", "FAIL", f"missing required key {key!r}")
    if f.fails:
        return f

    meta = deck["metadata"]
    for key in ("title", "language", "aspect_ratio"):
        if not str(meta.get(key, "")).strip():
            f.add("deck", "FAIL", f"metadata.{key} is required")
    if meta.get("aspect_ratio") not in (None, "16:9"):
        f.add("deck", "FAIL", "only 16:9 aspect_ratio is supported")

    slides = deck["slides"]
    if not isinstance(slides, list) or not slides:
        f.add("deck", "FAIL", "slides must be a non-empty array")
        return f

    seen_ids: set[str] = set()
    for i, slide in enumerate(slides, 1):
        sid = slide.get("id", f"<slide {i}>")
        for key in ("id", "type", "purpose", "message", "title", "layout_family", "visual_strategy", "content"):
            if key not in slide:
                f.add(sid, "FAIL", f"missing required field {key!r}")
        if "id" in slide:
            if slide["id"] in seen_ids:
                f.add(sid, "FAIL", "duplicate slide id")
            seen_ids.add(slide["id"])
        if slide.get("type") not in SLIDE_TYPES:
            f.add(sid, "FAIL", f"type {slide.get('type')!r} not in taxonomy")
        if slide.get("layout_family") not in LAYOUT_FAMILIES:
            f.add(sid, "FAIL", f"layout_family {slide.get('layout_family')!r} not supported by renderers")
        if slide.get("visual_strategy") not in VISUAL_STRATEGIES:
            f.add(sid, "FAIL", f"visual_strategy {slide.get('visual_strategy')!r} unknown")
        if not str(slide.get("message", "")).strip():
            f.add(sid, "FAIL", "every slide needs ONE primary message")
        content = slide.get("content", [])
        if not isinstance(content, list) or not content:
            f.add(sid, "FAIL", "content must be a non-empty array of blocks")
        else:
            for block in content:
                if isinstance(block, dict):
                    _check_block(f, sid, block)
        if "chart_spec" in slide:
            _check_chart(f, sid, slide["chart_spec"])
        if slide.get("layout_family") == "chart" and "chart_spec" not in slide:
            f.add(sid, "FAIL", "chart layout requires chart_spec")
        if slide.get("layout_family") == "table" and not any(b.get("kind") == "table" for b in content if isinstance(b, dict)):
            f.add(sid, "FAIL", "table layout requires a table block")
        if slide.get("layout_family") == "matrix-2x2" and not any(b.get("kind") == "matrix" for b in content if isinstance(b, dict)):
            f.add(sid, "FAIL", "matrix-2x2 layout requires a matrix block")
        qa = slide.get("qa", {})
        status = qa.get("status")
        if status is not None and status not in QA_STATUSES:
            f.add(sid, "FAIL", f"qa.status {status!r} must be PASS/WARNING/FAIL")
        if status == "FAIL":
            f.add(sid, "FAIL", "slide carries qa.status FAIL; repair before export")
        # Content QA heuristics (spec s.20): density and editability.
        bullets_total = sum(len(b.get("items", [])) for b in content if isinstance(b, dict) and b.get("kind") in ("bullets", "steps", "metrics"))
        if bullets_total > 14:
            f.add(sid, "WARNING", f"dense slide: {bullets_total} list/metric items; edit content down instead of shrinking fonts")
        if slide.get("image_spec", {}).get("text_in_image"):
            f.add(sid, "FAIL", "image_spec.text_in_image must be false: generators make images, the layout engine owns text")

    # Deck-level QA (spec s.21): layout rhythm.
    families = [s.get("layout_family") for s in slides]
    if len(families) >= 5:
        run, worst = 1, 1
        for a, b in zip(families, families[1:]):
            run = run + 1 if a == b and a not in ("cover", "divider") else 1
            worst = max(worst, run)
        if worst >= 4:
            f.add("deck", "WARNING", f"same layout_family repeated {worst}x in a row; vary visual rhythm")
    return f


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("deck", type=Path, help="path to deck.json")
    ap.add_argument("--report", type=Path, help="also write a Markdown QA report")
    args = ap.parse_args()

    try:
        deck = json.loads(args.deck.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL: cannot read {args.deck}: {exc}", file=sys.stderr)
        return 1

    f = validate(deck)
    for sid, level, msg in f.items:
        print(f"[{level:<7}] {sid}: {msg}")
    verdict = "VALID" if f.fails == 0 else "INVALID"
    print(f"\n{verdict}: {f.fails} fail(s), {f.warnings} warning(s), {len(deck.get('slides', []))} slide(s)")

    if args.report:
        lines = [
            "# PitchCraft QA Report",
            "",
            f"- Input: `{args.deck}`",
            f"- Verdict: **{verdict}** ({f.fails} FAIL, {f.warnings} WARNING)",
            "",
            "| Slide | Level | Finding |",
            "| --- | --- | --- |",
        ]
        lines += [f"| {sid} | {lvl} | {msg} |" for sid, lvl, msg in f.items]
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"Report written to {args.report}")

    return 0 if f.fails == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
