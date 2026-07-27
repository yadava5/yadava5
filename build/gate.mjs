/**
 * The real gate.
 *
 * The previous one was char-count arithmetic. It could not see glyph collisions,
 * transforms, or containment, and it printed GATE PASSED over nine overlapping
 * text runs and two labels breaking out of their own boxes. On a document whose
 * thesis is that claims should be mechanically checkable, a check that cannot
 * fail is the worst possible defect.
 *
 * This one renders each plate in Chromium and measures:
 *   1. it renders at all (naturalWidth > 0 as image/svg+xml)
 *   2. no two text runs overlap
 *   3. every text run sits inside the canvas and the 150→730 type column
 *   4. labels stay inside the box they belong to
 *   5. frame zero is the finished frame — nothing essential is invisible at t=0
 *   6. no essential element is hidden for most of its loop
 */
import { chromium } from 'playwright';
import { readFileSync, readdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const ASSETS = join(ROOT, 'assets');
const LEFT = 150, RIGHT = 730;
const M_LEFT = 30, M_RIGHT = 412;   // the 440-wide mobile canvas
const fails = [];

const browser = await chromium.launch();
const page = await browser.newPage();

for (const file of readdirSync(ASSETS).filter(f => /^(plate|m)-.*\.svg$/.test(f)).sort()) {
  const svg = readFileSync(join(ASSETS, file), 'utf8');

  // 1 — does it render when embedded the way GitHub embeds it?
  await page.setContent(
    `<body style="margin:0"><img id="probe" src="data:image/svg+xml;base64,${Buffer.from(svg).toString('base64')}"></body>`);
  const natural = await page.evaluate(() => new Promise(res => {
    const i = document.getElementById('probe');
    const done = () => res(i.naturalWidth);
    i.complete ? done() : (i.onload = done, i.onerror = () => res(0));
  }));
  if (!natural) { fails.push(`${file}: does not render as image/svg+xml`); continue; }

  // measure inside the live document
  await page.setContent(`<body style="margin:0">${svg}</body>`);
  const mobile = /^m-/.test(file);
  const L = mobile ? M_LEFT : LEFT, R = mobile ? M_RIGHT : RIGHT;
  const r = await page.evaluate(({ LEFT, RIGHT }) => {
    const out = { texts: [], boxes: [], h: 0, faint: [], zero: [] };
    const svgEl = document.querySelector('svg');
    out.h = svgEl.viewBox.baseVal.height;

    const runs = [...svgEl.querySelectorAll('text')].filter(t => t.textContent.trim());
    for (const t of runs) {
      const b = t.getBBox();
      out.texts.push({ s: t.textContent.trim().slice(0, 34), x: b.x, y: b.y, w: b.width, h: b.height });
    }
    for (const rect of svgEl.querySelectorAll('rect')) {
      const b = rect.getBBox();
      if (b.width > 60 && b.width < 400 && rect.getAttribute('fill') === 'none')
        out.boxes.push({ x: b.x, y: b.y, w: b.width, h: b.height });
    }

    // frame zero + duty cycle: seek the shared clock and sample effective opacity
    const anims = document.getAnimations();
    const dur = anims.length ? Math.max(...anims.map(a => a.effect.getTiming().duration || 0)) : 0;
    const sample = (t) => {
      anims.forEach(a => { try { a.pause(); a.currentTime = t; } catch {} });
      return [...svgEl.querySelectorAll('[class]')].map(el => {
        let o = 1, n = el;
        while (n && n !== svgEl) { o *= parseFloat(getComputedStyle(n).opacity); n = n.parentElement; }
        return { cls: el.getAttribute('class'), o };
      });
    };
    if (dur) {
      out.zero = sample(0).filter(e => e.o < 0.5).map(e => e.cls);
      const steps = 12, seen = {};
      for (let i = 0; i < steps; i++)
        for (const e of sample(dur * i / steps)) {
          seen[e.cls] ??= 0; if (e.o >= 0.5) seen[e.cls]++;
        }
      out.faint = Object.entries(seen).filter(([, v]) => v / steps < 0.5).map(([k]) => k);
    }
    return out;
  }, { LEFT, RIGHT });

  // 2 — pairwise text collision
  for (let i = 0; i < r.texts.length; i++)
    for (let j = i + 1; j < r.texts.length; j++) {
      const a = r.texts[i], b = r.texts[j];
      const ox = Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x);
      const oy = Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y);
      if (ox > 1 && oy > 1)
        fails.push(`${file}: "${a.s}" collides with "${b.s}" (${ox.toFixed(0)}×${oy.toFixed(0)}u)`);
    }

  // 3 — canvas + type column
  for (const t of r.texts) {
    if (t.x < L - 2 || t.x + t.w > R + 2)
      fails.push(`${file}: "${t.s}" outside the ${L}–${R} column (${t.x.toFixed(0)}→${(t.x + t.w).toFixed(0)})`);
    if (t.y < 0 || t.y + t.h > r.h)
      fails.push(`${file}: "${t.s}" outside the canvas (y ${t.y.toFixed(0)}→${(t.y + t.h).toFixed(0)}, h=${r.h})`);
  }

  // 4 — a label that starts inside a box must finish inside it
  for (const t of r.texts)
    for (const box of r.boxes) {
      const startsIn = t.x >= box.x - 2 && t.x <= box.x + box.w && t.y >= box.y - 2 && t.y + t.h <= box.y + box.h + 2;
      if (startsIn && t.x + t.w > box.x + box.w + 2)
        fails.push(`${file}: "${t.s}" breaks out of its box by ${(t.x + t.w - box.x - box.w).toFixed(0)}u`);
    }

  // 5 / 6 — frame zero, and evidence that hides for most of the loop
  if (r.zero.length) fails.push(`${file}: invisible at frame zero — ${[...new Set(r.zero)].join(', ')}`);
  if (r.faint.length) fails.push(`${file}: visible <50% of the loop — ${[...new Set(r.faint)].join(', ')}`);

  // strip every tag so tspan-split values ("97.01<tspan>%") read as one string
  const drawn = svg.replace(/<style[\s\S]*?<\/style>/g, ' ')
                   .replace(/<(?:title|desc)>[\s\S]*?<\/(?:title|desc)>/g, ' ')
                   .replace(/<[^>]*>/g, '').replace(/,/g, '');
  const meta = [...svg.matchAll(/<(?:title|desc)>([^<]*)<\/(?:title|desc)>/g)].map(m => m[1]).join(' ').replace(/,/g, '');
  const nums = [...new Set((meta.match(/\d+\.\d+|\b\d{2,}\b/g) || []))];
  for (const n of nums)
    if (!drawn.includes(n) && !/^(10|20|25|30|32|64|96|100|500|880|440)$/.test(n))
      fails.push(`${file}: description says "${n}" but the plate never draws it`);

  console.log(`  measured ${file}`);
}

await browser.close();
if (fails.length) {
  console.log(`\nGATE FAILED — ${fails.length} defects:`);
  for (const f of fails) console.log(`  · ${f}`);
  process.exit(1);
}
console.log('\nGATE PASSED — rendered, measured, no collisions, no overflow, frame zero complete.');
