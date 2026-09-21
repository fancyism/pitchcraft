#!/usr/bin/env node
/**
 * PitchCraft CLI — BMad-style workspace scaffolder.
 *
 * Install skill (agent side):  npx skills add fancyism/pitchcraft
 * Scaffold workspace (project side):
 *   npx github:fancyism/pitchcraft init            (interactive)
 *   npx github:fancyism/pitchcraft init decks/q3   (target dir)
 *   npx github:fancyism/pitchcraft init --yes      (defaults, no prompts)
 *   npx github:fancyism/pitchcraft check           (workspace readiness)
 *
 * Zero dependencies: Node >= 18 built-ins only.
 */
import { promises as fs } from "node:fs";
import path from "node:path";

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, "$1")), "..");
const TPL = path.join(ROOT, "templates", "workspace");

const PRESETS = ["editorial", "consulting", "data", "pitch", "educational"];
const banner = () => {
  console.log(`
  ╭──────────────────────────────────────────╮
  │   PitchCraft — Marketing Presentation    │
  │   Engine · workspace scaffolder          │
  ╰──────────────────────────────────────────╯`);
};

async function exists(p) { try { await fs.access(p); return true; } catch { return false; } }

function makeAsker() {
  // TTY: real readline interview. Piped/CI stdin: buffered answers, then defaults.
  if (process.stdin.isTTY) {
    return async (rl, label, def) => {
      const suffix = def ? ` (${def})` : "";
      const a = (await rl.question(`${label}${suffix}: `)).trim();
      return a || def || "";
  };
  }
  const lines = [];
  let resolveDrained;
  const drained = new Promise((r) => (resolveDrained = r));
  process.stdin.setEncoding("utf8");
  process.stdin.on("data", (c) => lines.push(...String(c).split(/\r?\n/)));
  process.stdin.on("end", resolveDrained);
  process.stdin.on("close", resolveDrained);
  return async (rl, label, def) => {
    await drained;
    const suffix = def ? ` (${def})` : "";
    while (lines.length && !lines[0] && lines.shift());
    const a = (lines.length ? lines.shift() : "").trim();
    console.log(`${label}${suffix}: ${a || def || ""}`);
    return a || def || "";
  };
}
const ask = makeAsker();

async function* walk(dir) {
  for (const e of await fs.readdir(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) yield* await walk(p);
    else yield p;
  }
}

function fillDeckConfig(a) {
  return `# PitchCraft workspace configuration — created by pitchcraft init ${new Date().toISOString().slice(0, 10)}
deck:
  title: ${JSON.stringify(a.title)}
  audience: ${JSON.stringify(a.audience)}
  objective: ${JSON.stringify(a.objective)}
  desired_action: ${JSON.stringify(a.action)}
  style_preset: ${a.style}
  language: ${a.lang}
  aspect_ratio: "16:9"
  length: ${a.slides}

outputs: [html, pptx, pdf, previews]

fonts:
  directory: "fonts"
  strategy: auto

brand:
  file: "config/brand.yaml"

design_rules: "config/design-rules.md"
templates: "templates"

qa:
  visual: true
  content: true
  ai_judgments: false

sourcing:
  web_verify: true
`;
}

function fillBrandYaml(a) {
  return `# Brand definition — created by pitchcraft init
# Compiles to theme tokens in Phase 6 (preset "${a.style}" is the base)

identity:
  name: ${JSON.stringify(a.brand || "")}
  tagline: ""

colors: {}   # empty = use the ${a.style} preset; add hex values to override

typography:
  # Put font files in fonts/ then list them here, e.g.:
  # custom_fonts:
  #   - family: "Anuphan"
  #     path: "fonts/Anuphan.ttf"
  #     weight: "100 900"
  line_height_body: ${a.lang === "th" ? 1.6 : 1.55}

logo:
  file: ""            # e.g. brand/logo.svg
  placement: [cover, closing]

icons:
  directory: "brand/icons"
  style: "outline 1.5px, single accent color"

photography: "one idea per image, natural light, consistent warmth; credit required"
`;
}

function startMd(a) {
  const dir = a.dir;
  return `# PitchCraft workspace — เริ่มตรงนี้ / Start here

## 1 · ติดตั้ง skill ฝั่ง agent (ครั้งเดียวต่อเครื่อง)

\`\`\`bash
npx skills add fancyism/pitchcraft
\`\`\`

ใช้ได้กับ agent ใดก็ตามที่อ่าน skills ได้ (Claude Code, Codex, OpenCode, OMP, Cursor, ...)

## 2 · ใส่วัตถุดิบของคุณ

| โฟลเดอร์ | ใส่อะไร |
| --- | --- |
| \`sources/\` | PDF, DOCX, XLSX/CSV, Markdown, เด็คเก่า — ทุกอย่างที่เป็น "ความจริง" ของเด็ค |
| \`fonts/\` | ไฟล์ .woff2/.ttf ของแบรนด์ (ไม่มีก็ได้ — ใช้ preset) |
| \`brand/\` | logo.svg, palette.json, แบรนด์ไกด์ (ไม่มีก็ได้) |
| \`references/\` | ภาพสไลด์ตัวอย่างที่ชอบสไตล์ (วิเคราะห์เป็นหลักการ ไม่ก็เลียน) |
| \`data/\` | ข้อมูลตัวเลขสำหรับกราฟ |

## 3 · สั่ง agent ทำเด็ค (คัดลอกไปใช้ได้เลย)

> สร้าง presentation จาก workspace นี้ (${dir}/) ด้วย PitchCraft
> ผู้ฟัง: ${a.audience || "(ระบุผู้ฟัง)"}
> เป้าหมาย: ${a.objective || "(ระบุเป้าหมาย)"}
> ${a.slides} สไลด์ · style: ${a.style} · ภาษา${a.lang === "th" ? "ไทย" : a.lang}
> ใช้ brand ใน brand/ และ font ใน fonts/ ถ้ามี
> Export: HTML, PPTX, PDF + previews

agent จะรัน pipeline: ingest (พร้อม provenance) → story → slide plan →
deck.json (validated) → render → QA loop → export ลง \`output/\`

## คำสั่งที่เป็นประโยชน์

\`\`\`bash
npx github:fancyism/pitchcraft check ${dir}   # เช็กความพร้อมของ workspace
python scripts/validate_deck.py ${dir}/output/deck.json   # (ใน repo pitchcraft)
\`\`\`

config ทั้งหมดอยู่ที่ \`config/\` — แก้ style preset / brand / กฎการออกแบบได้ตลอด
สไลด์ทุกใบจะอ้างอิง claim กลับไปที่ sources ผ่าน \`output/sources-map.json\`
`;
}

async function init(args) {
  const flags = Object.fromEntries(args.filter((a) => a.startsWith("--")).map((a) => [a.split("=")[0].slice(2), a.includes("=") ? a.split("=").slice(1).join("=") : true]));
  const pos = args.filter((a) => !a.startsWith("--"));
  const dir = pos[0] || "pitchcraft";
  banner();
  const { createInterface } = await import("node:readline/promises");
  let a = { dir, style: flags.style || "editorial", lang: flags.lang || "th", slides: flags.slides || 12, title: flags.title || "", audience: flags.audience || "", objective: flags.objective || "", action: "", brand: "" };
  if (!flags.yes) {
    const rl = process.stdin.isTTY ? (await import("node:readline/promises")).createInterface({ input: process.stdin, output: process.stdout }) : null;
    console.log("ตอบสั้น ๆ ได้เลย — Enter = ใช้ค่าในวงเล็บ\n");
    a.lang = (await ask(rl, "ภาษาของเด็ค (th/en)", a.lang)).toLowerCase();
    a.title = await ask(rl, "ชื่อเด็ค (working title)", a.title || "ให้ agent เสนอชื่อให้");
    a.audience = await ask(rl, "ผู้ฟัง", a.audience || "ทีมขายและผู้บริหาร");
    a.objective = await ask(rl, "เป้าหมายของเด็ค", a.objective || "อธิบายข้อเสนอและปิดการตัดสินใจ");
    a.action = await ask(rl, "สิ่งที่อยากให้ผู้ฟังทำต่อ", a.action || "อนุมัติแผน");
    a.brand = await ask(rl, "ชื่อแบรนด์/ร้าน (ถ้ามี)", a.brand);
    console.log(`\nStyle presets: ${PRESETS.join(" · ")}`);
    const s = await ask(rl, "เลือก style preset", a.style);
    if (PRESETS.includes(s)) a.style = s; else console.log(`(ไม่รู้จัก "${s}" — ใช้ ${a.style})`);
    a.slides = Number(await ask(rl, "จำนวนสไลด์", String(a.slides))) || 12;
    if (rl) rl.close();
  }

  const out = path.resolve(dir);
  if (await exists(path.join(out, "config", "deck.config.yaml"))) {
    console.error(`\n✗ ${out} มี workspace อยู่แล้ว — ใช้ชื่อโฟลเดอร์อื่น หรือลบ config/deck.config.yaml ก่อน`);
    process.exit(1);
  }
  await fs.mkdir(out, { recursive: true });
  for (const d of ["sources", "fonts", "brand", "brand/icons", "references", "assets", "assets/generated", "data", "output", "config", "templates"]) {
    await fs.mkdir(path.join(out, d), { recursive: true });
  }
  // templates + presets + design rules straight from the skill repo
  for await (const f of walk(TPL)) {
    const rel = path.relative(TPL, f);
    const dest = path.join(out, rel);
    await fs.mkdir(path.dirname(dest), { recursive: true });
    await fs.copyFile(f, dest);
  }
  await fs.writeFile(path.join(out, "config", "deck.config.yaml"), fillDeckConfig(a), "utf8");
  await fs.writeFile(path.join(out, "config", "brand.yaml"), fillBrandYaml(a), "utf8");
  await fs.writeFile(path.join(out, "START.md"), startMd(a), "utf8");
  await fs.writeFile(path.join(out, "sources", ".gitkeep"), "", "utf8");
  await fs.writeFile(path.join(out, "data", ".gitkeep"), "", "utf8");

  console.log(`
✓ Workspace พร้อมที่ ${out}/

  ขั้นต่อไป (3 ขั้น):
  1. ติดตั้ง skill ให้ agent:  npx skills add fancyism/pitchcraft
  2. ใส่ไฟล์ของคุณใน sources/ (+ fonts/ brand/ data/ ถ้ามี)
  3. เปิด ${out}/START.md — มีพร้อมต์สั่งเด็คที่คัดลอกได้เลย

  ตรวจความพร้อม:  npx github:fancyism/pitchcraft check ${dir}`);
}

async function check(args) {
  const dir = path.resolve(args[0] || "pitchcraft");
  banner();
  console.log(`Workspace: ${dir}\n`);
  const need = [
    ["config/deck.config.yaml", "deck config"], ["config/brand.yaml", "brand"], ["config/design-rules.md", "design rules"],
    ["templates", "DSL templates"], ["sources", "sources"], ["output", "output"],
  ];
  let ok = true;
  for (const [rel, label] of need) {
    const e = await exists(path.join(dir, rel));
    if (!e) ok = false;
    console.log(`  ${e ? "✓" : "✗ missing"}  ${label} (${rel})`);
  }
  const fontsDir = path.join(dir, "fonts");
  const fonts = (await exists(fontsDir)) ? (await fs.readdir(fontsDir)).filter((f) => /\.(woff2?|ttf|otf)$/i.test(f)) : [];
  console.log(`  ${fonts.length ? "✓" : "-"}     fonts: ${fonts.length ? fonts.join(", ") : "none (preset stacks will be used)"}`);
  const sources = (await exists(path.join(dir, "sources"))) ? (await fs.readdir(path.join(dir, "sources"))).filter((f) => !f.startsWith(".")) : [];
  console.log(`  ${sources.length ? "✓" : "!"}     sources: ${sources.length} file(s)${sources.length ? "" : " — ใส่ไฟล์ก่อนสั่งเด็ค"}`);
  console.log(`\n  ${ok ? "✓ Workspace พร้อม — สั่ง agent ได้เลย (ดู START.md)" : "✗ ยังไม่ครบ — รัน init ใหม่ หรือเพิ่มไฟล์ที่ขาด"}`);
  process.exit(ok ? 0 : 1);
}

const [cmd, ...rest] = process.argv.slice(2);
if (cmd === "init") await init(rest);
else if (cmd === "check") await check(rest);
else {
  banner();
  console.log(`  คำสั่ง:
    init [dir]   สร้าง workspace (--yes ข้ามคำถาม, --style= --lang= --title= --audience= --slides=)
    check [dir]  ตรวจความพร้อมของ workspace

  ตัวอย่าง:
    npx github:fancyism/pitchcraft init decks/q3
    npx github:fancyism/pitchcraft init --yes --lang=en --style=pitch
    npx github:fancyism/pitchcraft check decks/q3`);
}
