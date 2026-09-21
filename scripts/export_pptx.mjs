#!/usr/bin/env node
/**
 * PitchCraft PPTX exporter — deck.json (Slide DSL) -> editable deck.pptx.
 *
 * Requires: npm i pptxgenjs   (node 18+)
 * Usage:    node scripts/export_pptx.mjs <workspace>/output/deck.json -o <workspace>/output/deck.pptx
 *
 * Keeps text, tables and charts as EDITABLE PowerPoint objects; rasterizes
 * nothing. Complex SVG-only families (funnel, matrix) fall back to clean
 * text layouts so a human can always edit the result.
 */
import fs from "node:fs";
import path from "node:path";
import PptxGenJS from "pptxgenjs";

const [deckPath, ...rest] = process.argv.slice(2);
if (!deckPath) {
  console.error("usage: export_pptx.mjs <deck.json> [-o out.pptx]");
  process.exit(1);
}
const outIdx = rest.indexOf("-o");
const outPath = outIdx >= 0 ? rest[outIdx + 1] : deckPath.replace(/deck\.json$/, "deck.pptx");

const deck = JSON.parse(fs.readFileSync(deckPath, "utf8"));
const root = path.resolve(path.dirname(deckPath), "..", "..");

const theme = { ...deck.theme };
const C = Object.assign(
  {
    primary: "254741", secondary: "7A8B99", accent: "C46A2F",
    surface: "FAF7F2", surface_alt: "F1ECE3", text: "201D1A",
    text_muted: "6B645B", border: "E3DCD0",
  },
  theme.colors && Object.fromEntries(Object.entries(theme.colors).map(([k, v]) => [k, String(v).replace("#", "")]))
);
// Font strategy (spec §10): PPTX cannot assume recipients own custom fonts.
// Thai decks map to a Thai-capable system stack; see scripts/check_fonts.py.
const THAI = String(deck.metadata.language || "en").toLowerCase().startsWith("th");
const FONT_D = THAI ? "Leelawadee UI" : "Verdana";
const FONT_B = THAI ? "Leelawadee UI" : "Verdana";

const pptx = new PptxGenJS();
pptx.defineLayout({ name: "W169", width: 13.333, height: 7.5 });
pptx.layout = "W169";
pptx.title = deck.metadata.title;
if (deck.metadata.audience) theme._audience = deck.metadata.audience;

const hex = (c) => String(c || "").replace("#", "").toUpperCase();
const IN = { x: 0.6, y: 0.55, w: 12.13 };
const esc = (s) => String(s ?? "");

function header(slide, s) {
  if (s.eyebrow) slide.addText(s.eyebrow.toUpperCase(), { x: IN.x, y: IN.y, w: IN.w, h: 0.3, fontSize: 11, bold: true, color: hex(C.accent), charSpacing: 2, fontFace: FONT_B });
  slide.addText(esc(s.title), { x: IN.x, y: IN.y + (s.eyebrow ? 0.34 : 0), w: IN.w, h: 0.75, fontSize: 30, bold: true, color: hex(C.text), fontFace: FONT_D });
  if (s.subtitle) slide.addText(esc(s.subtitle), { x: IN.x, y: IN.y + (s.eyebrow ? 1.06 : 0.72), w: IN.w, h: 0.35, fontSize: 14, color: hex(C.text_muted), fontFace: FONT_B });
}

function blockOf(content, ...kinds) {
  return (content || []).find((b) => kinds.includes(b.kind));
}

const chartTypes = { column: "bar", bar: "bar", "stacked-bar": "bar", line: "line", area: "line", donut: "doughnut" };

function addChart(slide, spec, y, h) {
  const t = spec.type;
  if (!(t in chartTypes)) return false;
  const opts = {
    x: IN.x, y, w: IN.w, h,
    barDir: t === "bar" ? "bar" : "col",
    chartColors: [hex(C.primary), hex(C.accent), hex(C.secondary), "A38B6A"].map(hex),
    showLegend: spec.data.series.length > 1,
    legendPos: "b",
    showValue: spec.data.series.length === 1,
    dataLabelFontSize: 10,
    catAxisLabelFontSize: 10,
    valAxisLabelFontSize: 10,
    title: spec.title || "",
    showTitle: Boolean(spec.title),
  };
  if (t === "stacked-bar") opts.barGrouping = "stacked";
  if (t === "area") opts.lineSmooth = true;
  const labels = spec.data.labels.map(String);
  if (t === "donut") {
    slide.addChart(pptx.ChartType.doughnut, [{ name: spec.data.series[0].name, labels, values: spec.data.series[0].values }], opts);
  } else if (chartTypes[t] === "bar" && spec.data.series.length > 1) {
    slide.addChart(pptx.ChartType.bar, spec.data.series.map((s) => ({ name: s.name, labels, values: s.values })), opts);
  } else if (chartTypes[t] === "bar") {
    slide.addChart(pptx.ChartType.bar, [{ name: spec.data.series[0].name, labels, values: spec.data.series[0].values }], opts);
  } else {
    slide.addChart(pptx.ChartType.line, spec.data.series.map((s) => ({ name: s.name, labels, values: s.values })), opts);
  }
  if (spec.source) slide.addText(`Source: ${spec.source}`, { x: IN.x, y: y + h + 0.02, w: IN.w, h: 0.25, fontSize: 9, italic: true, color: hex(C.text_muted), fontFace: FONT_B });
  return true;
}

let n = 0;
for (const s of deck.slides) {
  n += 1;
  const slide = pptx.addSlide();
  slide.background = { color: hex(C.surface) };
  const fam = s.layout_family;
  const steps = blockOf(s.content, "steps");
  const bullets = blockOf(s.content, "bullets");
  const text = blockOf(s.content, "text");
  const metrics = blockOf(s.content, "metrics");
  const table = blockOf(s.content, "table");
  const quote = blockOf(s.content, "quote");
  const callout = blockOf(s.content, "callout");
  let y = 1.5;

  if (fam === "cover") {
    slide.addText(esc(s.eyebrow || "").toUpperCase(), { x: IN.x, y: 2.1, w: IN.w, h: 0.4, fontSize: 13, bold: true, color: hex(C.accent), charSpacing: 3, fontFace: FONT_B });
    slide.addText(esc(s.title), { x: IN.x, y: 2.5, w: IN.w, h: 1.6, fontSize: 48, bold: true, color: hex(C.text), fontFace: FONT_D });
    if (s.subtitle) slide.addText(esc(s.subtitle), { x: IN.x, y: 4.1, w: 9, h: 0.5, fontSize: 18, color: hex(C.text_muted), fontFace: FONT_B });
    if (theme._audience) slide.addText(esc(theme._audience).toUpperCase(), { x: IN.x, y: 6.6, w: IN.w, h: 0.3, fontSize: 10, charSpacing: 2, color: hex(C.text_muted), fontFace: FONT_B });
  } else if (fam === "statement" || fam === "closing-cta") {
    slide.addText(esc(s.title), { x: IN.x, y: 2.3, w: IN.w, h: 2.4, fontSize: 36, bold: true, color: hex(C.text), fontFace: FONT_D });
    if (text) slide.addText(esc(text.text), { x: IN.x, y: 4.8, w: 10.5, h: 0.9, fontSize: 15, color: hex(C.text_muted), fontFace: FONT_B });
    if (steps) {
      steps.items.forEach((it, i) => {
        slide.addText([{ text: `${it.label ? it.label + "  " : ""}${it.title}`, options: { bold: true, color: hex(C.primary) } }, { text: it.text ? " — " + it.text : "", options: { color: hex(C.text_muted) } }], { x: IN.x + i * 4.1, y: 5.6, w: 3.9, h: 1.2, fontSize: 12, fontFace: FONT_B });
      });
    }
  } else if (fam === "quote") {
    const q = quote || { text: s.title, attribution: s.subtitle };
    slide.addText(`“${q.text}”`, { x: IN.x, y: 2.4, w: IN.w, h: 2.4, fontSize: 30, italic: true, color: hex(C.text), fontFace: FONT_D });
    if (q.attribution) slide.addText(`— ${q.attribution}`, { x: IN.x, y: 4.9, w: IN.w, h: 0.4, fontSize: 14, color: hex(C.text_muted), fontFace: FONT_B });
  } else if (fam === "big-number" && metrics) {
    slide.addText(esc(metrics.items[0].value), { x: IN.x, y: 2.2, w: IN.w, h: 2.0, fontSize: 96, bold: true, color: hex(C.primary), fontFace: FONT_D });
    slide.addText(esc(metrics.items[0].label), { x: IN.x, y: 4.3, w: 10, h: 0.6, fontSize: 20, color: hex(C.text_muted), fontFace: FONT_B });
  } else if (fam === "chart" || fam === "funnel" || fam === "kpi-dashboard") {
    header(slide, s);
    if (metrics) {
      metrics.items.forEach((m, i) => {
        const w = IN.w / metrics.items.length;
        slide.addText(esc(m.value), { x: IN.x + i * w, y: 1.55, w, h: 0.7, fontSize: 34, bold: true, color: hex(C.primary), fontFace: FONT_D });
        slide.addText(esc(m.label), { x: IN.x + i * w, y: 2.2, w, h: 0.4, fontSize: 12, color: hex(C.text_muted), fontFace: FONT_B });
      });
      y = 2.8;
    }
    if (s.chart_spec) {
      if (!addChart(slide, s.chart_spec, y, 3.6) && fam === "funnel") {
        const items = s.chart_spec.data.series[0].values.map((v, i) => `${s.chart_spec.data.labels[i]}: ${v}${s.chart_spec.data.unit || ""}`);
        slide.addText(items.map((t) => ({ text: t, options: { bullet: true } })), { x: IN.x, y, w: 8, h: 3.4, fontSize: 16, color: hex(C.text), fontFace: FONT_B });
      }
    }
    if (s.chart_spec && s.chart_spec.takeaway) slide.addText([{ text: "Takeaway. ", options: { bold: true, color: hex(C.accent) } }, { text: s.chart_spec.takeaway }], { x: IN.x, y: 6.5, w: IN.w, h: 0.4, fontSize: 12, fontFace: FONT_B });
  } else if (fam === "table" && table) {
    header(slide, s);
    slide.addTable(table.rows, {
      x: IN.x, y, w: IN.w,
      colW: Array(table.columns.length).fill(IN.w / table.columns.length),
      border: { type: "solid", color: hex(C.border), pt: 1 },
      fontSize: 13, fontFace: FONT_B, color: hex(C.text),
      fill: { color: hex(C.surface) },
    });
    slide.addText(table.columns.map((c) => ({ text: c, options: { bold: true, color: hex(C.text_muted), fill: { color: hex(C.surface_alt) } } })), { x: IN.x, y: y - 0.4, w: IN.w, h: 0.35, fontSize: 11, fontFace: FONT_B });
  } else if (steps && (fam === "comparison" || fam === "before-after" || fam === "problem-solution")) {
    header(slide, s);
    steps.items.slice(0, 2).forEach((p, i) => {
      const x = IN.x + i * 6.27;
      slide.addShape(pptx.ShapeType.roundRect, { x, y: 1.7, w: 5.9, h: 4.4, fill: { color: hex(C.surface_alt) }, line: { color: i === 1 ? hex(C.accent) : hex(C.border), width: 1 }, rectRadius: 0.08 });
      if (p.label) slide.addText(esc(p.label).toUpperCase(), { x: x + 0.25, y: 1.95, w: 5.4, h: 0.3, fontSize: 10, bold: true, charSpacing: 2, color: hex(C.accent), fontFace: FONT_B });
      slide.addText(esc(p.title), { x: x + 0.25, y: 2.3, w: 5.4, h: 0.5, fontSize: 20, bold: true, color: hex(C.text), fontFace: FONT_D });
      if (p.text) slide.addText(esc(p.text), { x: x + 0.25, y: 2.9, w: 5.4, h: 2.9, fontSize: 13, color: hex(C.text_muted), fontFace: FONT_B });
    });
  } else if (metrics && metrics.items.length >= 3) {
    header(slide, s);
    metrics.items.forEach((m, i) => {
      const w = IN.w / metrics.items.length;
      slide.addText(esc(m.value), { x: IN.x + i * w, y: 2.2, w, h: 0.9, fontSize: 44, bold: true, color: hex(C.primary), fontFace: FONT_D });
      slide.addText(esc(m.label), { x: IN.x + i * w, y: 3.1, w, h: 0.6, fontSize: 13, color: hex(C.text_muted), fontFace: FONT_B });
    });
  } else if (steps) {
    header(slide, s);
    const perRow = steps.items.length >= 4 ? 3 : steps.items.length;
    const w = (IN.w - 0.3 * (perRow - 1)) / perRow;
    steps.items.forEach((it, i) => {
      const x = IN.x + (i % perRow) * (w + 0.3);
      const yy = y + Math.floor(i / perRow) * 2.5;
      slide.addShape(pptx.ShapeType.roundRect, { x, y: yy, w, h: 2.2, fill: { color: hex(C.surface_alt) }, line: { color: hex(C.border), width: 1 }, rectRadius: 0.06 });
      if (it.label) slide.addText(esc(it.label), { x: x + 0.2, y: yy + 0.15, w: w - 0.4, h: 0.3, fontSize: 10, bold: true, charSpacing: 1, color: hex(C.accent), fontFace: FONT_B });
      slide.addText(esc(it.title), { x: x + 0.2, y: yy + 0.45, w: w - 0.4, h: 0.6, fontSize: 15, bold: true, color: hex(C.text), fontFace: FONT_D });
      if (it.text) slide.addText(esc(it.text), { x: x + 0.2, y: yy + 1.05, w: w - 0.4, h: 1.0, fontSize: 11, color: hex(C.text_muted), fontFace: FONT_B });
    });
  } else if (bullets || text) {
    header(slide, s);
    if (text) slide.addText(esc(text.text), { x: IN.x, y, w: IN.w, h: 0.8, fontSize: 16, color: hex(C.text), fontFace: FONT_B });
    if (bullets) slide.addText(bullets.items.map((t) => ({ text: t, options: { bullet: { characterCode: "2022" }, color: hex(C.text), breakLine: true } })), { x: IN.x + 0.1, y: y + 0.9, w: IN.w - 0.2, h: 4.0, fontSize: 16, fontFace: FONT_B });
  } else {
    header(slide, s);
    if (text) slide.addText(esc(text.text), { x: IN.x, y, w: IN.w, h: 1.0, fontSize: 16, color: hex(C.text), fontFace: FONT_B });
  }
  if (callout) slide.addText([{ text: (callout.title ? callout.title + ". " : ""), options: { bold: true, color: hex(C.accent) } }, { text: callout.text }], { x: IN.x, y: 6.85, w: IN.w, h: 0.45, fontSize: 11, fontFace: FONT_B, fill: { color: hex(C.surface_alt) } });
  if (s.sources && s.sources.length) slide.addText(`Sources: ${s.sources.join(", ")}`, { x: IN.x, y: 7.12, w: IN.w, h: 0.25, fontSize: 8, italic: true, color: hex(C.text_muted), fontFace: FONT_B });
  slide.addText(`${n} / ${deck.slides.length}`, { x: 12.35, y: 7.1, w: 0.6, h: 0.3, fontSize: 9, color: hex(C.text_muted), fontFace: FONT_B, align: "right" });
  if (s.speaker_notes) slide.addNotes(s.speaker_notes);
}

await pptx.writeFile({ fileName: outPath });
console.log(`Wrote ${outPath} (${deck.slides.length} slides)`);
