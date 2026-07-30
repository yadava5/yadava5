/**
 * Does it move enough to SEE?
 *
 * gate.mjs checks 13 and 17 count a sample interval "alive" when any element's
 * bounding box shifts 0.5 viewBox units or its opacity changes by 0.02. At a
 * 980px readme column 0.5u is 0.7 device pixels, and 0.02 opacity on a grey
 * label is nothing at all. Both thresholds sit below the threshold of vision,
 * so the gate reported plate VI 70% alive while a raster diff found it never
 * once exceeded 0.2% pixel change across its entire 13.1s loop.
 *
 * That is not a threshold that needs tightening — it is the wrong quantity.
 * Geometry cannot tell you whether something is visible; only pixels can. This
 * rasterises each plate every 100ms and reports the fraction of intervals in
 * which enough of the image actually changed.
 *
 * Deliberately a tool and not a check. Five plates fail it today, and wiring it
 * into CI before the motion is re-authored would just paint main red. It is
 * here so the next round can measure instead of guess — and so the claim "the
 * dead air is fixed", which I made from bounding-box deltas and which was
 * false, cannot be made again without evidence.
 *
 * Usage: node build/motion.mjs [--step 100] [--floor 0.002]
 */
import { chromium } from 'playwright';
import { readFileSync, readdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const ASSETS = join(dirname(fileURLToPath(import.meta.url)), '..', 'assets');
const arg = (n, d) => { const i = process.argv.indexOf(n); return i > 0 ? Number(process.argv[i + 1]) : d; };
const STEP = arg('--step', 100);          // ms between samples
const FLOOR = arg('--floor', 0.002);      // fraction of pixels that must change
const TARGET = 0.25;                      // of intervals

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 520, height: 760 } });
const rows = [];

// Diffing has to happen on the LIVE render. My first version serialised the
// animated SVG and re-rasterised it through an <img>, which restarts the CSS
// clock from zero — every frame came back identical and all eight plates
// reported 0% motion. Playwright screenshots the real compositor output; the
// bytes go back into the page only to be decoded into pixels.
const decodeAndDiff = async (b64, first) => page.evaluate(async ({ b64, first }) => {
  const img = new Image();
  img.src = 'data:image/png;base64,' + b64;
  await img.decode();
  const W = img.naturalWidth, H = img.naturalHeight;
  const cv = document.createElement('canvas'); cv.width = W; cv.height = H;
  const cx = cv.getContext('2d', { willReadFrequently: true });
  cx.drawImage(img, 0, 0);
  const cur = cx.getImageData(0, 0, W, H).data;
  const prev = window.__prev;
  window.__prev = cur;
  if (first || !prev) return 0;
  let changed = 0;
  for (let p = 0; p < cur.length; p += 4)
    if (Math.abs(cur[p] - prev[p]) + Math.abs(cur[p + 1] - prev[p + 1])
      + Math.abs(cur[p + 2] - prev[p + 2]) > 24) changed++;
  return changed / (W * H);
}, { b64, first });

for (const f of readdirSync(ASSETS).filter(x => /^plate-.*\.svg$/.test(x)).sort()) {
  await page.setContent(`<body style="margin:0">${readFileSync(join(ASSETS, f), 'utf8')}</body>`);
  const dur = await page.evaluate(async () => {
    await document.fonts.ready;
    const a = document.getAnimations();
    a.forEach(x => x.pause());
    window.__prev = null;
    return a.length ? Math.max(...a.map(x => x.effect.getComputedTiming().duration || 0)) : 0;
  });
  if (!dur) { rows.push([f, { live: 0, worst: Infinity }]); continue; }
  const n = Math.max(2, Math.round(dur / STEP));
  const svg = page.locator('svg');
  let live = 0, dead = 0, worst = 0;
  for (let i = 0; i <= n; i++) {
    await page.evaluate((t) => document.getAnimations().forEach(a => { try { a.currentTime = t; } catch {} }),
      dur * i / n);
    const frac = await decodeAndDiff((await svg.screenshot()).toString('base64'), i === 0);
    if (i === 0) continue;
    if (frac >= FLOOR) { live++; dead = 0; } else { dead++; worst = Math.max(worst, dead); }
  }
  rows.push([f, { live: live / n, worst: worst * (dur / n) / 1000 }]);
}

console.log(`  raster diff · ${STEP}ms steps · a sample counts as motion when `
          + `>=${(FLOOR * 100).toFixed(1)}% of pixels change\n`);
let bad = 0;
for (const [f, r] of rows) {
  const ok = r.live >= TARGET;
  if (!ok) bad++;
  console.log(`  ${ok ? '..' : '!!'} ${f.padEnd(24)} ${(r.live * 100).toFixed(0).padStart(3)}% of samples move`
            + `   longest still run ${r.worst.toFixed(1)}s`);
}
console.log(`\n  ${rows.length - bad}/${rows.length} plates clear ${TARGET * 100}% of samples.`);
await browser.close();
