#!/usr/bin/env python3
"""PitchCraft font strategy check.

Implements the spec's font chain: preferred -> installed/embedded check ->
fallback -> PDF canonical. Scans the workspace fonts/ directory, reads the
deck's theme.typography, and emits output/font-strategy.json:

- embed: fonts that render_html.py will base64-embed into deck.html
- pptx:  safe font-family mapping per role (custom fonts are NOT assumed
  installed on the recipient's machine)
- export_strategy: "pdf-canonical" when custom fonts are used and PPTX
  cannot embed them; "pptx-safe" otherwise
- notes: warnings (missing files, unsupported formats, Thai language)

stdlib only.

Usage:
  python scripts/check_fonts.py <workspace>/output/deck.json [--root <workspace>]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SUPPORTED = {".woff2", ".woff", ".ttf", ".otf"}

# Thai-capable system fonts by platform, ordered by preference.
THAI_SAFE = "'Leelawadee UI', 'Noto Sans Thai', 'Sukhumvit Set', Tahoma, sans-serif"
LATIN_SAFE = "'Segoe UI', 'Helvetica Neue', Arial, sans-serif"
MONO_SAFE = "'Cascadia Code', Consolas, 'SF Mono', monospace"

# Known web-safe families we never need to embed (subset check).
WEB_SAFE = {"arial", "helvetica", "segoe ui", "tahoma", "verdana", "georgia",
            "times new roman", "consolas", "courier new", "leelawadee ui",
            "noto sans", "noto sans thai", "sans-serif", "serif", "monospace"}


def is_web_safe(stack: str) -> bool:
    first = stack.split(",")[0].strip("\"' ").lower()
    return first in WEB_SAFE


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("deck", type=Path)
    ap.add_argument("--root", type=Path, help="workspace root (default: deck parent's parent)")
    args = ap.parse_args()

    deck = json.loads(args.deck.read_text(encoding="utf-8"))
    root = args.root or args.deck.parent.parent
    lang = (deck.get("metadata", {}).get("language") or "en").lower()
    thai = lang.startswith("th")
    theme = deck.get("theme", {})
    typo = theme.get("typography", {})

    fonts_dir = root / "fonts"
    discovered = sorted(
        {"name": p.name, "size_kb": round(p.stat().st_size / 1024, 1)}
        for p in fonts_dir.glob("*") if p.suffix.lower() in SUPPORTED
    ) if fonts_dir.is_dir() else []

    custom = typo.get("custom_fonts", [])
    embed, notes = [], []
    for f in custom:
        p = (root / f["path"]).resolve()
        if p.suffix.lower() not in SUPPORTED:
            notes.append(f"unsupported font format: {f['path']} (use woff2/woff/ttf/otf)")
            continue
        if not p.is_file():
            notes.append(f"custom font file missing: {p}")
            continue
        embed.append({"family": f["family"], "path": f["path"],
                      "weight": f.get("weight", "normal"),
                      "variable": " " in str(f.get("weight", "")) or "-" in str(f.get("weight", ""))})
    for d in discovered:
        if not any(e["path"].endswith(d["name"]) for e in embed):
            notes.append(f"fonts/{d['name']} found but not referenced in theme.typography.custom_fonts")

    def pptx_stack(role_stack: str) -> str:
        if is_web_safe(role_stack):
            return role_stack
        if thai:
            return THAI_SAFE
        return LATIN_SAFE

    display = typo.get("display") or (THAI_SAFE if thai else LATIN_SAFE)
    body = typo.get("body") or (THAI_SAFE if thai else LATIN_SAFE)
    mono = typo.get("mono") or MONO_SAFE

    uses_custom = bool(embed)
    export_strategy = "pdf-canonical" if uses_custom else "pptx-safe"
    if uses_custom:
        notes.append("PPTX cannot assume recipients own the custom fonts: deck.html/PDF is the visual canonical version; PPTX uses a safe stack and stays editable")

    strategy = {
        "language": lang,
        "thai_rules_applied": thai,
        "discovered": discovered,
        "embed_into_html": embed,
        "pptx": {
            "display": pptx_stack(display),
            "body": pptx_stack(body),
            "mono": MONO_SAFE if not is_web_safe(mono) else mono,
        },
        "export_strategy": export_strategy,
        "fallback_chain": ["preferred (custom_fonts)", "embedded check (this report)",
                           "safe stack (pptx above)", "PDF canonical export"],
        "line_height_body": typo.get("line_height_body", 1.55),
        "notes": notes,
    }
    if thai:
        strategy["thai_rules"] = ["line-height >= 1.25 everywhere (renderer enforces)",
                                  "no negative letter-spacing on Thai text",
                                  "word-boundary wrapping; check tone marks are not clipped"]

    out = args.deck.parent / "font-strategy.json"
    out.write_text(json.dumps(strategy, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(strategy, ensure_ascii=False, indent=2))
    print(f"\nWritten to {out}")
    return 0 if not any("missing" in n or "unsupported" in n for n in notes) else 1


if __name__ == "__main__":
    raise SystemExit(main())
