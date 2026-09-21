# PitchCraft QA Report — geo-sme-thai (v2 demo)

- **Deck:** `examples/geo-sme-thai/output/deck.json` (10 สไลด์, 16:9, th)
- **Inspected:** rendered deck.html + Chromium captures 1280×720, 2026-09-22
- **Verdict: PASS — 0 FAIL, 0 WARNING** (หลังแก้ 1 รอบ)

## Pipeline findings

VALID: 0 fail(s), 0 warning(s), 10 slide(s) — validate_deck.py

## Font strategy (v2 feature)

`check_fonts.py` → `output/font-strategy.json`: Anuphan (variable, OFL)
base64-embedded in deck.html (330 KB) · PPTX maps to `Leelawadee UI` Thai
stack · export_strategy = pdf-canonical · Thai rules list emitted.

## Visual QA loop (iteration 1)

| Slide | Finding | Repair | Re-inspect |
| --- | --- | --- | --- |
| 6 | ป้ายการ์ดผสมไวยากรณ์ (84% / 21% / หลัก / +30-40%) — zoom ยืนยันว่าตำแหน่ง label ตรงกันหมดจริง แต่ grammar ไม่ลงตัว | "หลัก" → "Top 3" ให้ทุ้้นป้ายเป็น metric-style เหมือนกัน | PASS |
| (แก้ระหว่างทาง) | การแก้ป้ายพลาดไปโดนสไลด์ 5 (SEO/GEO) หนึ่งบรรทัด — จับได้จากการ re-read ก่อน render | คืนบรรทัด GEO เดิม แล้วแก้ที่บรรทัดที่ถูกต้อง (150) | PASS |

## Thai-specific checks (AC3)

- Thai glyphs: Anuphan แสดงผลถูกทุกสไลด์ — ไม่มี tofu, วรรณยุกต์บน-ล่างอยู่ตำแหน่ง (vision ยืนยัน 10/10)
- line-height 1.6: ไม่มีวรรณยุกต์โดนตัดในทุก layout (statement/การ์ด/แผง/เช็กลิสต์)
- กราฟ: label แกนไทย + ตัวเลขบนแท่งอ่านได้, source line ใต้กราฟทุกแผ่น (4, 7)

## Final per-slide status

| # | id | Layout | Status |
| --- | --- | --- | --- |
| 1 | cover | cover | PASS (dark cover, Thai light type) |
| 2 | ask-ai-first | statement | PASS |
| 3 | thirty-five | big-number | PASS |
| 4 | zero-click | chart | PASS |
| 5 | seo-vs-geo | comparison | PASS |
| 6 | what-ai-cites | framework-grid | PASS (หลังรวม label grammar) |
| 7 | stature-ladder | chart | PASS |
| 8 | start-where-you-are | problem-solution | PASS |
| 9 | week-one | checklist | PASS |
| 10 | cta | closing-cta | PASS |

## Deck-level QA

- Rhythm: cover→statement→big-number→chart→comparison→framework→chart→problem→checklist→cta; chart สองแผ่นคั่นด้วย 2 สไลด์
- Template library ใช้จริง 5/6 families (title, data, comparison, framework, closing) — ดู slide-plan.md
- ทุกตัวเลขมี URL ใน sources-map.json + ข้อจำกัดระบุใน speaker notes

## Exports

deck.html 330 KB (self-contained + Anuphan) · deck.pptx 10 สไลด์ (Leelawadee UI) · deck.json · font-strategy.json · preview/slide-01..10.png
