#!/usr/bin/env python3
"""PitchCraft HTML renderer.

Renders a Slide DSL deck.json into ONE self-contained deck.html:
16:9 canvas, theme tokens as CSS custom properties, inline SVG charts,
keyboard navigation, progress bar, speaker notes, print/PDF mode.

stdlib only. Fonts and local images are base64-embedded so the file is
portable anywhere.

Usage:
  python scripts/render_html.py examples/<ws>/output/deck.json \
      --root examples/<ws> -o examples/<ws>/output/deck.html
"""
from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import sys
from html import escape
from pathlib import Path

# ---------------------------------------------------------------- tokens ----

DEFAULT_THEME = {
    "colors": {
        "primary": "#254741", "secondary": "#7A8B99", "accent": "#C46A2F",
        "surface": "#FAF7F2", "surface_alt": "#F1ECE3",
        "text": "#201D1A", "text_muted": "#6B645B", "border": "#E3DCD0",
    },
    "typography": {
        "display": "\"Avenir Next\", \"Segoe UI\", \"Helvetica Neue\", Arial, \"Noto Sans\", sans-serif",
        "body": "\"Segoe UI\", \"Helvetica Neue\", Arial, \"Noto Sans\", \"Noto Sans Thai\", \"Leelawadee UI\", sans-serif",
        "mono": "\"Cascadia Code\", \"SF Mono\", Consolas, monospace",
        "line_height_body": 1.55,
    },
}

CHART_COLORS = ["__C_PRIMARY__", "__C_ACCENT__", "__C_SECONDARY__", "#A38B6A", "#5B7566", "#8C5B4F"]

MIME = {".woff2": "font/woff2", ".woff": "font/woff", ".ttf": "font/ttf", ".otf": "font/otf"}


def fmt_num(v: float) -> str:
    if isinstance(v, int):
        return f"{v:,}"
    r = round(v, 2)
    return f"{r:,.2f}".rstrip("0").rstrip(".")


def h(text: object) -> str:
    return escape(str(text), quote=True)


def block_of(content: list[dict], *kinds: str) -> dict | None:
    for b in content:
        if b.get("kind") in kinds:
            return b
    return None


# ----------------------------------------------------------------- fonts ----

def font_css(theme: dict, root: Path) -> str:
    css = []
    for f in theme.get("typography", {}).get("custom_fonts", []):
        path = (root / f["path"]).resolve()
        if not path.is_file():
            print(f"WARNING: font not found: {path}", file=sys.stderr)
            continue
        mime = MIME.get(path.suffix.lower())
        if not mime:
            continue
        b64 = base64.b64encode(path.read_bytes()).decode("ascii")
        weight = f.get("weight", "normal")
        style = f.get("style", "normal")
        css.append(
            f"@font-face{{font-family:{json.dumps(f['family'])};src:url(data:{mime};base64,{b64}) "
            f"format('{path.suffix.lstrip('.').replace('woff2','woff2')}');font-weight:{weight};font-style:{style};}}"
        )
    return "\n".join(css)


def asset_url(path: str, root: Path) -> str:
    """Embed local images/fonts as data URIs; pass http(s) URLs through."""
    if path.startswith(("http://", "https://", "data:")):
        return path
    p = (root / path).resolve()
    if not p.is_file():
        print(f"WARNING: asset not found: {p}", file=sys.stderr)
        return path
    mime = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
    return f"data:{mime};base64,{base64.b64encode(p.read_bytes()).decode('ascii')}"


# ---------------------------------------------------------------- charts ----

CHART_W, CHART_H = 1040, 400


def _palette_resolved(colors: dict) -> list[str]:
    pal = []
    for c in CHART_COLORS:
        for token, real in (("__C_PRIMARY__", "primary"), ("__C_ACCENT__", "accent"), ("__C_SECONDARY__", "secondary")):
            if c == token:
                pal.append(colors.get(real, "#254741"))
                break
        else:
            pal.append(c)
    return pal


def chart_svg(spec: dict, colors: dict) -> str:
    t = spec["type"]
    data = spec["data"]
    labels = [str(x) for x in data["labels"]]
    series = data["series"]
    unit = data.get("unit", "")
    pal = _palette_resolved(colors)
    muted = colors.get("text_muted", "#6B645B")
    border = colors.get("border", "#E3DCD0")
    s = [f'<svg viewBox="0 0 {CHART_W} {CHART_H}" role="img" class="chart" preserveAspectRatio="xMidYMid meet">']

    def label(x: float, y: float, text: str, anchor: str = "middle", bold: bool = False, fill: str | None = None) -> None:
        bold_attr = ' font-weight="700"' if bold else ""
        s.append(
            f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" fill="{fill or muted}" '
            f'font-size="15"{bold_attr}>{h(text)}</text>'
        )

    if t in ("column", "bar", "stacked-bar"):
        if t == "column":
            n = len(labels)
            gap, pad = 24, 60
            cw = (CHART_W - pad * 2 - gap * (n - 1)) / n
            vmax = max((v for sr in series for v in sr["values"]), default=1) or 1
            top, bottom = 34, CHART_H - 58
            for gi in range(0, 5):
                y = top + (bottom - top) * gi / 4
                s.append(f'<line x1="{pad}" y1="{y:.1f}" x2="{CHART_W - pad}" y2="{y:.1f}" stroke="{border}" stroke-width="1"/>')
                label(pad - 10, y + 5, fmt_num(vmax * (1 - gi / 4)), "end")
            for i, lab in enumerate(labels):
                x = pad + i * (cw + gap)
                for si, sr in enumerate(series):
                    v = sr["values"][i]
                    bh = (bottom - top) * (v / vmax)
                    bw = cw / len(series)
                    bx = x + si * bw
                    s.append(f'<rect x="{bx:.1f}" y="{bottom - bh:.1f}" width="{bw - 3:.1f}" height="{bh:.1f}" fill="{pal[si % len(pal)]}" rx="3"/>')
                if len(series) == 1:
                    v = series[0]["values"][i]
                    bh = (bottom - top) * (v / vmax)
                    label(x + cw / 2, bottom - bh - 9, fmt_num(v) + unit, bold=True, fill=colors.get("text", "#201D1A"))
                label(x + cw / 2, CHART_H - 26, lab)
        else:  # horizontal bars / stacked
            n = len(labels)
            lh = min(52, (CHART_H - 40) / n)
            pad, top = 190, 20
            vmax = max((sum(sr["values"][i] for sr in series) for i in range(n)), default=1) or 1
            for i, lab in enumerate(labels):
                y = top + i * lh
                label(pad - 14, y + lh / 2 + 5, lab, "end")
                if t == "bar":
                    for si, sr in enumerate(series):
                        v = sr["values"][i]
                        w = (CHART_W - pad - 40) * (v / vmax)
                        yoff = y + si * (lh - 14) / max(len(series), 1)
                        hh = (lh - 16) / max(len(series), 1)
                        s.append(f'<rect x="{pad}" y="{yoff + 4:.1f}" width="{w:.1f}" height="{hh:.1f}" fill="{pal[si % len(pal)]}" rx="3"/>')
                    if len(series) == 1:
                        w = (CHART_W - pad - 40) * (series[0]["values"][i] / vmax)
                        label(pad + w + 10, y + lh / 2 + 5, fmt_num(series[0]["values"][i]) + unit, "start", bold=True, fill=colors.get("text", "#201D1A"))
                else:  # stacked-bar
                    x = pad
                    total = sum(sr["values"][i] for sr in series)
                    for si, sr in enumerate(series):
                        v = sr["values"][i]
                        w = (CHART_W - pad - 40) * (v / vmax)
                        s.append(f'<rect x="{x:.1f}" y="{y + 6:.1f}" width="{w:.1f}" height="{lh - 20:.1f}" fill="{pal[si % len(pal)]}" rx="3"/>')
                        x += w
                    label(CHART_W - 30, y + lh / 2 + 5, fmt_num(total) + unit, "end", bold=True, fill=colors.get("text", "#201D1A"))

    elif t in ("line", "area"):
        pad_l, pad_r, top, bottom = 70, 30, 34, CHART_H - 58
        all_v = [v for sr in series for v in sr["values"]]
        vmin, vmax = min(all_v), max(all_v)
        span = (vmax - vmin) or 1
        n = len(labels)
        def X(i): return pad_l + i * (CHART_W - pad_l - pad_r) / max(n - 1, 1)
        def Y(v): return bottom - (bottom - top) * ((v - vmin) / span)
        for gi in range(5):
            y = top + (bottom - top) * gi / 4
            s.append(f'<line x1="{pad_l}" y1="{y:.1f}" x2="{CHART_W - pad_r}" y2="{y:.1f}" stroke="{border}"/>')
            label(pad_l - 10, y + 5, fmt_num(vmax - (vmax - vmin) * gi / 4), "end")
        for i, lab in enumerate(labels):
            label(X(i), CHART_H - 26, lab)
        for si, sr in enumerate(series):
            pts = [(X(i), Y(v)) for i, v in enumerate(sr["values"])]
            if t == "area":
                poly = pts + [(X(n - 1), bottom), (X(0), bottom)]
                s.append(f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in poly)}" fill="{pal[si % len(pal)]}" opacity="0.14"/>')
            s.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="{pal[si % len(pal)]}" stroke-width="3.5" stroke-linejoin="round" stroke-linecap="round"/>')
            for x, y in pts:
                s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="{pal[si % len(pal)]}"/>')
        if len(series) > 1:
            for si, sr in enumerate(series):
                lx = CHART_W - 30 - (len(series) - si) * 150
                s.append(f'<rect x="{lx}" y="8" width="14" height="4" rx="2" fill="{pal[si % len(pal)]}"/>')
                label(lx + 20, 14, sr["name"], "start")

    elif t == "donut":
        vals = series[0]["values"]
        total = sum(vals) or 1
        cx, cy, r, ir = CHART_W / 2, CHART_H / 2 - 10, 150, 92
        import math
        a0 = -math.pi / 2
        for i, v in enumerate(vals):
            a1 = a0 + 2 * math.pi * v / total
            large = 1 if a1 - a0 > math.pi else 0
            x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
            x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
            xi1, yi1 = cx + ir * math.cos(a1), cy + ir * math.sin(a1)
            xi0, yi0 = cx + ir * math.cos(a0), cy + ir * math.sin(a0)
            s.append(
                f'<path d="M{x0:.1f},{y0:.1f} A{r},{r} 0 {large} 1 {x1:.1f},{y1:.1f} '
                f'L{xi1:.1f},{yi1:.1f} A{ir},{ir} 0 {large} 0 {xi0:.1f},{yi0:.1f} Z" fill="{pal[i % len(pal)]}"/>'
            )
            a0 = a1
        s.append(f'<text x="{cx}" y="{cy - 4}" text-anchor="middle" fill="{colors.get("text", "#201D1A")}" font-size="34" font-weight="800">{h(fmt_num(total) + unit)}</text>')
        s.append(f'<text x="{cx}" y="{cy + 26}" text-anchor="middle" fill="{muted}" font-size="15">total</text>')
        lx = cx + r + 40 if cx + r + 240 < CHART_W else cx - r - 240
        for i, lab in enumerate(labels):
            y = cy - len(labels) * 14 + i * 28
            s.append(f'<rect x="{lx}" y="{y - 11}" width="14" height="14" rx="3" fill="{pal[i % len(pal)]}"/>')
            pct = vals[i] / total * 100
            label(lx + 22, y + 1, f"{lab} — {fmt_num(vals[i])}{unit} ({pct:.0f}%)", "start")

    elif t == "funnel":
        vals = series[0]["values"]
        vmax = max(vals) or 1
        n = len(vals)
        stage_h = min(64, (CHART_H - 60) / n)
        top = 24
        for i, v in enumerate(vals):
            w = (CHART_W * 0.62) * (v / vmax)
            y = top + i * stage_h
            s.append(f'<rect x="{(CHART_W - w) / 2:.1f}" y="{y:.1f}" width="{w:.1f}" height="{stage_h - 12:.1f}" fill="{pal[i % len(pal)]}" opacity="{1 - 0.55 * i / max(n - 1, 1)}" rx="6"/>')
            label((CHART_W - w) / 2 - 16, y + stage_h / 2, str(labels[i]), "end", bold=True, fill=colors.get("text", "#201D1A"))
            label((CHART_W + w) / 2 + 16, y + stage_h / 2, fmt_num(v) + unit, "start", bold=True, fill=colors.get("text", "#201D1A"))

    s.append("</svg>")
    return "".join(s)


# ---------------------------------------------------------------- blocks ----

def render_block(b: dict) -> str:
    k = b["kind"]
    if k == "text":
        return f'<p class="lead">{h(b["text"])}</p>'
    if k == "bullets":
        return '<ul class="bullets">' + "".join(f"<li>{h(x)}</li>" for x in b["items"]) + "</ul>"
    if k == "steps":
        n = len(b["items"])
        items = []
        for i in b["items"]:
            lab = '<span class="step-label">' + h(i["label"]) + "</span>" if i.get("label") else ""
            txt = '<p class="step-text">' + h(i["text"]) + "</p>" if i.get("text") else ""
            items.append(
                '<div class="step"><div class="step-head">' + lab
                + '<span class="step-title">' + h(i["title"]) + "</span></div>" + txt + "</div>"
            )
        return '<div class="steps" data-n="' + str(n) + '">' + "".join(items) + "</div>"
    if k == "metrics":
        items = "".join(
            f'<div class="metric"><span class="metric-value">{h(i["value"])}</span>'
            f'<span class="metric-label">{h(i["label"])}</span>'
            + (f'<span class="metric-delta">{h(i["delta"])}</span>' if i.get("delta") else "")
            + (f'<span class="metric-src">{h(i["source"])}</span>' if i.get("source") else "")
            + "</div>"
            for i in b["items"]
        )
        return f'<div class="metrics">{items}</div>'
    if k == "table":
        head = "".join(f"<th>{h(c)}</th>" for c in b["columns"])
        rows = "".join("<tr>" + "".join(f"<td>{h(c)}</td>" for c in r) + "</tr>" for r in b["rows"])
        return f'<table class="tbl"><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table>'
    if k == "matrix":
        ax, cells = b["axes"], {(_c["x"], _c["y"]): _c for _c in b["cells"]}
        def cell(x, y):
            c = cells.get((x, y), {"title": ""})
            return f'<div class="mx-cell"><span class="mx-title">{h(c["title"])}</span>' + (f'<p>{h(c["text"])}</p>' if c.get("text") else "") + "</div>"
        return (
            f'<div class="matrix" data-rows="2"><div class="mx-axis"><span>{h(ax["y"]["high"])}</span><span>{h(ax["y"]["low"])}</span></div>'
            f'<div class="mx-grid">{cell("low","high")}{cell("high","high")}{cell("low","low")}{cell("high","low")}</div>'
            f'<div class="mx-xaxis"><span>{h(ax["x"]["low"])}</span><span>{h(ax["x"]["high"])}</span></div></div>'
        )
    if k == "quote":
        return f'<blockquote class="q"><p>“{h(b["text"])}”</p>' + (
            f'<footer>— {h(b["attribution"])}</footer>' if b.get("attribution") else "") + "</blockquote>"
    if k == "callout":
        tone = b.get("tone", "default")
        return f'<aside class="callout tone-{tone}">' + (f'<strong>{h(b["title"])}</strong> ' if b.get("title") else "") + h(b["text"]) + "</aside>"
    return ""


# ---------------------------------------------------------------- slides ----

def slide_html(slide: dict, idx: int, total: int, theme: dict, root: Path) -> str:
    fam = slide["layout_family"]
    colors = theme.get("colors", {})
    parts: list[str] = []
    eyebrow = f'<div class="eyebrow">{h(slide["eyebrow"])}</div>' if slide.get("eyebrow") else ""
    subtitle = f'<p class="subtitle">{h(slide["subtitle"])}</p>' if slide.get("subtitle") else ""
    head = f"{eyebrow}<h2 class=\"title\">{h(slide['title'])}</h2>{subtitle}" if fam not in ("cover", "statement", "divider", "quote", "closing-cta") else ""
    content = slide.get("content", [])
    body: list[str] = []

    bg = next((a for a in slide.get("assets", []) if a["role"] == "background"), None)
    hero = next((a for a in slide.get("assets", []) if a["role"] == "hero"), None)
    if bg:
        parts.append(f'<img class="bg" src="{asset_url(bg["path"], root)}" alt="{h(bg.get("alt",""))}"/><div class="scrim"></div>')
    if hero and fam in ("key-insight", "case-study", "statement", "cover"):
        parts.append(f'<img class="hero" src="{asset_url(hero["path"], root)}" alt="{h(hero.get("alt",""))}"/>')

    steps = block_of(content, "steps")
    bullets = block_of(content, "bullets")
    text = block_of(content, "text")
    metrics = block_of(content, "metrics")
    table = block_of(content, "table")
    matrix = block_of(content, "matrix")
    quote = block_of(content, "quote")
    callout = block_of(content, "callout")
    chart = slide.get("chart_spec")

    if fam == "cover":
        meta = slide.get("subtitle", "")
        body.append('<div class="cover-middle">' + eyebrow + '<h1 class="display">' + h(slide["title"]) + "</h1>"
                    + ('<p class="cover-sub">' + h(meta) + "</p>" if meta else "") + "</div>")
        if theme.get("_audience"):
            body.append('<div class="cover-foot"><span>' + h(theme["_audience"]) + "</span></div>")
    elif fam == "divider":
        body.append(f'<div class="div-num">{idx:02d}</div><h1 class="display">{h(slide["title"])}</h1>'
                    + (f'<p class="subtitle">{h(slide["subtitle"])}</p>' if slide.get("subtitle") else ""))
    elif fam == "statement":
        body.append('<p class="statement">' + h(slide["title"]) + "</p>")
        if text and slide["title"] != text["text"]:
            body.append('<p class="statement-sub">' + h(text["text"]) + "</p>")
        if bullets:
            body.append(render_block(bullets))
    elif fam == "big-number":
        m = (metrics or {"items": [{"value": slide["title"], "label": slide.get("subtitle", "")}]})["items"][0]
        body.append(f'<div class="bignum"><span class="bignum-value">{h(m["value"])}</span>'
                    f'<span class="bignum-label">{h(m["label"])}</span></div>')
        if text:
            body.append(render_block(text))
        rest = (metrics or {"items": []})["items"][1:]
        if rest:
            body.append('<div class="metrics metrics-sm">' + "".join(
                f'<div class="metric"><span class="metric-value">{h(i["value"])}</span><span class="metric-label">{h(i["label"])}</span></div>' for i in rest) + "</div>")
    elif fam == "quote":
        q = quote or {"text": slide["title"], "attribution": slide.get("subtitle", "")}
        body.append(render_block(q))
    elif fam == "chart":
        if chart:
            body.append(f'<div class="chart-wrap">{chart_svg(chart, colors)}</div>')
            if chart.get("takeaway"):
                body.append(f'<aside class="callout"><strong>Takeaway.</strong> {h(chart["takeaway"])}</aside>')
        if callout:
            body.append(render_block(callout))
    elif fam == "funnel":
        if chart:
            body.append(f'<div class="chart-wrap">{chart_svg(chart, colors)}</div>')
        elif steps:
            body.append(render_block(steps))
    elif fam == "table":
        if table:
            body.append(render_block(table))
        if callout:
            body.append(render_block(callout))
    elif fam == "matrix-2x2":
        if matrix:
            body.append(render_block(matrix))
        if text:
            body.append(render_block(text))
    elif fam == "kpi-dashboard":
        if metrics:
            body.append(render_block(metrics))
        if chart:
            body.append(f'<div class="chart-wrap chart-sm">{chart_svg(chart, colors)}</div>')
        if callout:
            body.append(render_block(callout))
    elif fam in ("framework-grid", "feature-grid"):
        for b in content:
            if b["kind"] in ("steps", "bullets"):
                if b["kind"] == "bullets":
                    b = {"kind": "steps", "items": [{"title": x} for x in b["items"]]}
                body.append(render_block(b))
            elif b["kind"] not in ("text",):
                body.append(render_block(b))
        if text:
            body.append(render_block(text))
    elif fam == "process-flow":
        if steps:
            body.append(render_block(steps))
        if text:
            body.append(render_block(text))
    elif fam in ("timeline", "roadmap"):
        if steps:
            body.append(render_block(steps))
        if callout:
            body.append(render_block(callout))
    elif fam in ("comparison", "before-after", "problem-solution"):
        panels = steps["items"] if steps else []
        cls = "split panels-2"
        inner = ""
        for i, p in enumerate(panels):
            side = h(p.get("label", "")) or ("Before" if i == 0 and fam == "before-after" else "")
            inner += (f'<div class="panel{" panel-accent" if i == 1 else ""}">'
                      + (f'<div class="panel-tag">{side}</div>' if side else "")
                      + f'<h3>{h(p["title"])}</h3>' + (f'<p>{h(p["text"])}</p>' if p.get("text") else "") + "</div>")
        badge = {"comparison": "vs", "before-after": "→", "problem-solution": "⇒"}[fam]
        body.append(f'<div class="{cls}">{inner}<span class="split-badge">{badge}</span></div>')
        if metrics:
            body.append(render_block(metrics))
        if callout:
            body.append(render_block(callout))
    elif fam == "case-study":
        left = "".join(render_block(b) for b in content if b["kind"] in ("text", "bullets"))
        right = render_block(metrics) if metrics else (render_block(text) if text else "")
        body.append(f'<div class="case"><div class="case-left">{left}</div><div class="case-right">{right}</div></div>')
    elif fam == "checklist":
        if bullets:
            body.append('<ul class="checklist">' + "".join(f"<li>{h(x)}</li>" for x in bullets["items"]) + "</ul>")
        if callout:
            body.append(render_block(callout))
    elif fam == "closing-cta":
        body.append(f'<p class="statement">{h(slide["title"])}</p>')
        if steps:
            body.append(render_block(steps))
        if metrics:
            body.append(render_block(metrics))
        if text:
            body.append(render_block(text))
    elif fam == "key-insight":
        if text:
            body.append(render_block(text))
        if bullets:
            body.append(render_block(bullets))
        if callout:
            body.append(render_block(callout))
    else:
        for b in content:
            body.append(render_block(b))

    srcs = slide.get("sources") or []
    src_line = f'<div class="sources">Sources: {", ".join(h(x) for x in srcs)}</div>' if srcs else ""
    notes = h(slide.get("speaker_notes", ""))
    return (
        f'<section class="slide f-{fam}" id="s-{idx}" data-family="{fam}" data-notes="{notes}">'
        + "".join(parts)
        + f'<div class="slide-inner">{head or ""}<div class="content">{"".join(body)}</div>{src_line}</div>'
        + f'<div class="pagenum">{idx} / {total}</div>'
        + "</section>"
    )


# ------------------------------------------------------------------ shell ---

CSS_TEMPLATE = """
*{margin:0;padding:0;box-sizing:border-box}
:root{
--c-primary:__C_PRIMARY__;--c-secondary:__C_SECONDARY__;--c-accent:__C_ACCENT__;
--c-surface:__C_SURFACE__;--c-surface-alt:__C_SURFACE_ALT__;
--c-text:__C_TEXT__;--c-muted:__C_TEXT_MUTED__;--c-border:__C_BORDER__;
--f-display:__F_DISPLAY__;--f-body:__F_BODY__;--f-mono:__F_MONO__;
--lh:__LH__;--radius:14px;--pad:72px;
}
html,body{height:100%;background:#141311;font-family:var(--f-body);color:var(--c-text);line-height:var(--lh)}
#stage{position:fixed;inset:0;overflow:hidden}
.slide{position:absolute;inset:0;width:1280px;height:720px;background:var(--c-surface);display:none;transform-origin:top left}
.slide.active{display:block;animation:fadein .35s ease}
@keyframes fadein{from{opacity:.25}to{opacity:1}}
.slide-inner{position:relative;height:100%;display:flex;flex-direction:column;padding:calc(var(--pad)*.86) var(--pad);z-index:2}
.eyebrow{font-size:15px;letter-spacing:.16em;text-transform:uppercase;color:var(--c-accent);font-weight:700;margin-bottom:14px}
.title{font-family:var(--f-display);font-size:44px;line-height:1.14;font-weight:800;letter-spacing:-0.01em;margin-bottom:10px;max-width:1080px}
.subtitle{font-size:21px;color:var(--c-muted);margin-bottom:6px}
.content{flex:1;display:flex;flex-direction:column;justify-content:center;gap:22px;min-height:0}
.lead{font-size:24px;max-width:980px}
.bullets{list-style:none;display:flex;flex-direction:column;gap:14px;max-width:980px}
.bullets li{font-size:22px;padding-left:30px;position:relative}
.bullets li::before{content:"";position:absolute;left:2px;top:.62em;width:10px;height:10px;border-radius:3px;background:var(--c-accent)}
.steps{display:grid;gap:18px}
.steps[data-n="2"],.steps[data-n="4"]{grid-template-columns:1fr 1fr}
.steps[data-n="3"],.steps[data-n="5"],.steps[data-n="6"]{grid-template-columns:1fr 1fr 1fr}
.step{background:var(--c-surface-alt);border:1px solid var(--c-border);border-radius:var(--radius);padding:20px 22px;display:flex;flex-direction:column;gap:6px}
.step-head{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}
.step-label{font-family:var(--f-mono);font-size:13px;color:var(--c-accent);font-weight:700;letter-spacing:.08em}
.step-title{font-size:20px;font-weight:700}
.step-text{font-size:17px;color:var(--c-muted)}
.metrics{display:grid;gap:18px;grid-template-columns:repeat(auto-fit,minmax(180px,1fr))}
.metric{display:flex;flex-direction:column;gap:4px}
.metric-value{font-family:var(--f-display);font-size:56px;font-weight:800;color:var(--c-primary);line-height:1.05}
.metric-label{font-size:17px;color:var(--c-muted)}
.metric-delta{font-size:15px;color:var(--c-accent);font-weight:700}
.metric-src{font-size:12px;color:var(--c-muted)}
.metrics-sm .metric-value{font-size:34px}
.tbl{width:100%;border-collapse:collapse;font-size:19px}
.tbl th{text-align:left;font-size:14px;letter-spacing:.1em;text-transform:uppercase;color:var(--c-muted);padding:12px 16px;border-bottom:2px solid var(--c-text)}
.tbl td{padding:14px 16px;border-bottom:1px solid var(--c-border)}
.matrix{display:grid;grid-template-columns:34px 1fr;grid-template-rows:1fr 30px;gap:8px;height:100%}
.mx-axis{writing-mode:vertical-rl;transform:rotate(180deg);display:flex;justify-content:space-between;align-items:center;font-size:13px;color:var(--c-muted);text-transform:uppercase;letter-spacing:.08em}
.mx-grid{display:grid;grid-template-columns:1fr 1fr;grid-template-rows:1fr 1fr;gap:14px}
.mx-cell{background:var(--c-surface-alt);border:1px solid var(--c-border);border-radius:var(--radius);padding:18px 20px}
.mx-cell:nth-child(2){border-color:var(--c-accent)}
.mx-title{font-size:20px;font-weight:700;display:block;margin-bottom:4px}
.mx-cell p{font-size:16px;color:var(--c-muted)}
.mx-xaxis{grid-column:2;display:flex;justify-content:space-between;font-size:13px;color:var(--c-muted);text-transform:uppercase;letter-spacing:.08em}
.callout{border-left:4px solid var(--c-accent);background:var(--c-surface-alt);padding:16px 20px;border-radius:0 var(--radius) var(--radius) 0;font-size:19px}
.callout.tone-warning{border-color:#B03A2E}.callout.tone-positive{border-color:var(--c-primary)}
.chart-wrap{width:100%}.chart{width:100%;height:auto;max-height:430px}.chart-sm .chart{max-height:260px}
.q{max-width:960px}
.q p{font-family:var(--f-display);font-size:40px;line-height:1.3;font-weight:700}
.q footer{margin-top:18px;font-size:19px;color:var(--c-muted)}
.f-cover .slide-inner{justify-content:flex-end;padding-bottom:84px}
.f-cover .display,.f-divider .display{font-family:var(--f-display);font-size:76px;line-height:1.06;font-weight:800;letter-spacing:-0.015em;max-width:1000px}
.cover-sub{font-size:24px;color:var(--c-muted);margin-top:16px;max-width:760px}
.cover-foot{margin-top:26px;font-size:15px;letter-spacing:.14em;text-transform:uppercase;color:var(--c-muted)}
.f-cover .eyebrow{margin-bottom:18px}
.f-divider .slide-inner{justify-content:center}
.div-num{font-family:var(--f-display);font-size:120px;font-weight:800;color:transparent;-webkit-text-stroke:2px var(--c-accent);line-height:1;margin-bottom:8px}
.statement{font-family:var(--f-display);font-size:54px;line-height:1.18;font-weight:800;max-width:1060px;letter-spacing:-0.01em}
.statement-sub{font-size:23px;color:var(--c-muted);max-width:860px}
.bignum{display:flex;flex-direction:column;gap:8px}
.bignum-value{font-family:var(--f-display);font-size:150px;font-weight:800;color:var(--c-primary);line-height:1}
.bignum-label{font-size:26px;color:var(--c-muted);max-width:860px}
.split{position:relative;display:grid;grid-template-columns:1fr 1fr;gap:26px;align-items:stretch}
.panel{background:var(--c-surface-alt);border:1px solid var(--c-border);border-radius:var(--radius);padding:26px 28px}
.panel-accent{border-color:var(--c-accent)}
.panel-tag{font-size:13px;letter-spacing:.12em;text-transform:uppercase;color:var(--c-accent);font-weight:700;margin-bottom:10px}
.panel h3{font-size:26px;margin-bottom:10px}
.panel p{font-size:18px;color:var(--c-muted)}
.split-badge{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:52px;height:52px;border-radius:50%;background:var(--c-surface);border:1px solid var(--c-border);display:flex;align-items:center;justify-content:center;font-weight:800;font-size:19px;color:var(--c-accent)}
.case{display:grid;grid-template-columns:1.15fr .85fr;gap:34px;align-items:center}
.case-left{display:flex;flex-direction:column;gap:16px}
.case-right{background:var(--c-surface-alt);border:1px solid var(--c-border);border-radius:var(--radius);padding:28px;display:flex;flex-direction:column;gap:20px}
.checklist{list-style:none;display:flex;flex-direction:column;gap:16px;max-width:900px}
.checklist li{font-size:22px;padding-left:44px;position:relative}
.checklist li::before{content:"✓";position:absolute;left:0;top:0;width:30px;height:30px;border-radius:9px;background:var(--c-primary);color:var(--c-surface);display:flex;align-items:center;justify-content:center;font-size:16px;font-weight:800}
.f-process-flow .steps{grid-template-columns:repeat(auto-fit,minmax(150px,1fr))}
.f-process-flow .step::after{content:"→";position:absolute;right:-19px;top:50%;transform:translateY(-50%);color:var(--c-accent);font-weight:800;font-size:20px}
.f-process-flow .step{position:relative}
.f-process-flow .step:last-child::after{content:""}
.f-timeline .steps{grid-template-columns:repeat(auto-fit,minmax(140px,1fr));position:relative;padding-top:26px}
.f-timeline .steps::before{content:"";position:absolute;top:8px;left:4%;right:4%;height:3px;background:var(--c-border);border-radius:2px}
.f-timeline .step{background:none;border:none;padding:12px 8px 0}
.f-timeline .step::before{content:"";display:block;width:14px;height:14px;border-radius:50%;background:var(--c-accent);border:3px solid var(--c-surface);margin:-42px 0 14px;position:relative;z-index:1}
.f-roadmap .steps{grid-template-columns:1fr;gap:12px}
.f-roadmap .step{flex-direction:row;align-items:center;gap:18px;padding:14px 20px}
.f-roadmap .step-label{min-width:110px}
.f-cta .statement{font-size:60px}
.hero{position:absolute;right:0;top:0;height:100%;width:44%;object-fit:cover;z-index:1;mask-image:linear-gradient(90deg,transparent,var(--c-surface) 26%)}
.bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;z-index:0}
.scrim{position:absolute;inset:0;background:linear-gradient(100deg,rgba(20,19,17,.86) 30%,rgba(20,19,17,.45));z-index:1}
.f-cover .slide-inner,.f-cover .title,.f-cover .display,.f-cover .cover-sub,.f-cover .cover-foot,.f-cover .eyebrow{color:#F5F1EA}
.f-cover .sources{color:#CFC8BC}
.sources{position:absolute;bottom:22px;left:var(--pad);font-size:12.5px;color:var(--c-muted)}
.pagenum{position:absolute;bottom:22px;right:var(--pad);font-family:var(--f-mono);font-size:13px;color:var(--c-muted)}
#hud{position:fixed;left:0;right:0;bottom:0;z-index:50;display:flex;align-items:center;gap:16px;padding:10px 18px;color:#B9B2A6;font-family:var(--f-mono);font-size:13px}
#bar{flex:1;height:3px;background:rgba(255,255,255,.14);border-radius:2px;overflow:hidden}
#bar i{display:block;height:100%;background:var(--c-accent);width:0}
#hud button{background:none;border:1px solid rgba(255,255,255,.25);color:#B9B2A6;border-radius:8px;padding:4px 12px;cursor:pointer;font-family:inherit}
#notes{position:fixed;left:0;right:0;bottom:44px;background:rgba(20,19,17,.94);color:#E8E2D6;padding:14px 22px;font-size:16px;z-index:49;border-top:1px solid rgba(255,255,255,.14)}
@media (prefers-reduced-motion:reduce){.slide.active{animation:none}}
@media print{
@page{size:1280px 720px;margin:0}
html,body{background:#fff}
#stage{position:static;overflow:visible}
.slide{display:block!important;position:relative;transform:none!important;page-break-after:always;width:1280px;height:720px}
.slide.active{animation:none}
#hud,#notes{display:none!important}
}
"""

JS = """
(function(){
var slides=[].slice.call(document.querySelectorAll('.slide'));
var i=0;var notes=document.getElementById('notes');
function fit(){var s=Math.min(innerWidth/1280,innerHeight/720);slides.forEach(function(el){el.style.transform='scale('+s+')';});}
function show(n,push){
 i=Math.max(0,Math.min(slides.length-1,n));
 slides.forEach(function(el,idx){el.classList.toggle('active',idx===i);});
 document.getElementById('bar-i').style.width=((i+1)/slides.length*100)+'%';
 document.getElementById('cnt').textContent=(i+1)+' / '+slides.length;
 if(notes)notes.textContent=slides[i].getAttribute('data-notes')||'';
 if(push)history.replaceState(null,'','#'+(i+1));
}
addEventListener('keydown',function(e){
 if(e.key==='ArrowRight'||e.key===' '||e.key==='PageDown'){e.preventDefault();show(i+1,true);}
 else if(e.key==='ArrowLeft'||e.key==='PageUp'){e.preventDefault();show(i-1,true);}
 else if(e.key==='Home'){show(0,true);}else if(e.key==='End'){show(slides.length-1,true);}
 else if(e.key==='n'||e.key==='N'){notes.hidden=!notes.hidden;}
});
document.getElementById('prev').onclick=function(){show(i-1,true)};
document.getElementById('next').onclick=function(){show(i+1,true)};
addEventListener('resize',fit);fit();
var h=parseInt(location.hash.slice(1),10);show(isNaN(h)?0:h-1,false);
})();
"""


def build_css(theme: dict) -> str:
    c = {**DEFAULT_THEME["colors"], **theme.get("colors", {})}
    t = {**DEFAULT_THEME["typography"], **theme.get("typography", {})}
    lh = max(float(t.get("line_height_body", 1.55)), 1.25)  # Thai needs >= 1.25
    css = CSS_TEMPLATE
    for token, val in {
        "__C_PRIMARY__": c["primary"], "__C_SECONDARY__": c["secondary"], "__C_ACCENT__": c["accent"],
        "__C_SURFACE__": c["surface"], "__C_SURFACE_ALT__": c["surface_alt"],
        "__C_TEXT__": c["text"], "__C_TEXT_MUTED__": c["text_muted"], "__C_BORDER__": c["border"],
        "__F_DISPLAY__": t["display"], "__F_BODY__": t["body"], "__F_MONO__": t["mono"], "__LH__": str(lh),
    }.items():
        css = css.replace(token, val)
    return css


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("deck", type=Path)
    ap.add_argument("-o", "--out", type=Path, help="output deck.html (default: alongside deck.json)")
    ap.add_argument("--root", type=Path, help="workspace root for resolving assets/fonts (default: deck parent's parent)")
    args = ap.parse_args()

    deck = json.loads(args.deck.read_text(encoding="utf-8"))
    root = args.root or args.deck.parent.parent
    out = args.out or args.deck.with_name("deck.html")

    theme = deck.get("theme", {})
    if deck["metadata"].get("audience"):
        theme["_audience"] = deck["metadata"]["audience"]
    css = build_css(theme) + "\n" + font_css(theme, root)
    slides = deck["slides"]
    body = "\n".join(slide_html(s, i + 1, len(slides), theme, root) for i, s in enumerate(slides))
    aud = deck["metadata"].get("audience", "")
    title = deck["metadata"]["title"]

    doc = f"""<!doctype html>
<html lang="{h(deck['metadata'].get('language','en'))}">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>{h(title)}</title>
<style>{css}</style>
</head>
<body>
<div id="stage">
{body}
</div>
<div id="notes" hidden></div>
<div id="hud">
<button id="prev" aria-label="Previous">←</button>
<div id="bar"><i id="bar-i"></i></div>
<span id="cnt"></span>
<button id="next" aria-label="Next">→</button>
</div>
<script>{JS}</script>
</body>
</html>
"""
    out.write_text(doc, encoding="utf-8")
    print(f"Wrote {out} ({len(slides)} slides, {out.stat().st_size/1024:.0f} KB, self-contained)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
