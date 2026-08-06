/**
 * Does the motion that EXISTS actually show?
 *
 * RE-AUTHORED, round 19, deliberately and in the same change as the design it
 * measures. The previous version of this file enforced the opposite doctrine:
 * every plate had to show pixel change in >=25% of sampled intervals and could
 * never hold still for more than 2.4s. That gate got what KPI-driven design
 * always gets — seven plates grew travelling hairlines whose own comments
 * admitted they existed "to carry the raster gate", and four of them spent
 * part of every loop striking through text (the colophon's crossed out the
 * author's email; the refusal's applied the plate's own strike-symbol to the
 * wrong nouns). Motion-as-quota produced decoration engineered for an
 * instrument, which is the definition of unrefined.
 *
 * The design doctrine is now STILL BY DEFAULT: a plate animates only where the
 * motion performs the claim beside it, and a plate with nothing to perform is
 * legally, deliberately still. So the floor and the ceiling are gone — but the
 * discovery that built this file stands: geometry cannot tell you whether
 * motion is VISIBLE, only pixels can. gate.mjs once reported a plate 70% alive
 * while a raster diff showed it never exceeded 0.2% pixel change. That failure
 * mode — an animation that exists for the instruments and not for the reader —
 * is precisely what a still-by-default page must not ship, because an
 * invisible animation is pure cost: it burns compositor time and carries no
 * meaning. So the check inverts:
 *
 *   · a plate with NO animations passes — stillness is a design decision
 *   · a plate WITH animations must show its gesture: at least MIN_LIVE
 *     sampled intervals must clear the perceptual floor, or the animation is
 *     invisible and should be deleted rather than shipped
 *
 * Both themes still measured separately: an opacity tuned on the dark canvas
 * can drop a gesture under the floor on the light one, and "should be
 * identical" is exactly the assumption this file exists to stop.
 *
 * The plates are transparent now, so each set is rastered over the canvas it
 * actually ships on — GitHub dark #0d1117, GitHub light #ffffff. Diffing
 * near-white ink over a default white test page would blind this gate
 * completely for the dark set.
 *
 * Usage: node build/motion.mjs [--step 100] [--floor 0.002] [--gate]
 */
import { chromium } from 'playwright';
import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

// Honour GATE_ASSETS like gate.mjs does, so build/mutations.mjs can point
// this file at a directory of deliberately-broken plates. Until it did, two
// of the three gates in `npm test` had never been shown able to fail.
const ASSETS = process.env.GATE_ASSETS || join(dirname(fileURLToPath(import.meta.url)), '..', 'assets');
const arg = (n, d) => { const i = process.argv.indexOf(n); return i > 0 ? Number(process.argv[i + 1]) : d; };
const STEP = arg('--step', 100);          // ms between samples
const FLOOR = arg('--floor', 0.002);      // fraction of pixels that must change
const MIN_LIVE = 3;                       // intervals a declared gesture must show
const GATE = process.argv.includes('--gate');

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

const SETS = [{ dir: ASSETS, tag: '', bg: '#0d1117' }];
const LIGHT_DIR = join(ASSETS, 'light');
if (existsSync(LIGHT_DIR)) SETS.push({ dir: LIGHT_DIR, tag: 'light/', bg: '#ffffff' });
const plates = SETS.flatMap(({ dir, tag, bg }) =>
  readdirSync(dir).filter(x => /^plate-.*\.svg$/.test(x)).sort().map(x => ({ dir, tag, bg, base: x })));

for (const { dir, tag, bg, base } of plates) {
  const f = tag + base;
  await page.setContent(`<body style="margin:0;background:${bg}">${readFileSync(join(dir, base), 'utf8')}</body>`);
  const dur = await page.evaluate(async () => {
    await document.fonts.ready;
    const a = document.getAnimations();
    a.forEach(x => x.pause());
    window.__prev = null;
    return a.length ? Math.max(...a.map(x => x.effect.getComputedTiming().duration || 0)) : 0;
  });
  if (!dur) { rows.push([f, { still: true }]); continue; }
  const n = Math.max(2, Math.round(dur / STEP));
  const svg = page.locator('svg');
  let live = 0;
  for (let i = 0; i <= n; i++) {
    await page.evaluate((t) => document.getAnimations().forEach(a => { try { a.currentTime = t; } catch {} }),
      dur * i / n);
    const frac = await decodeAndDiff((await svg.screenshot()).toString('base64'), i === 0);
    if (i === 0) continue;
    if (frac >= FLOOR) live++;
  }
  rows.push([f, { still: false, live, n }]);
}

console.log(`  raster diff · ${STEP}ms steps · a sample counts as motion when `
          + `>=${(FLOOR * 100).toFixed(1)}% of pixels change\n`);
const fail = [];
for (const [f, r] of rows) {
  if (r.still) { console.log(`  .. ${f.padEnd(24)} still by design`); continue; }
  const invisible = r.live < MIN_LIVE;
  if (invisible) fail.push(`${f}: declares animations but only ${r.live} of ${r.n} sampled intervals `
                         + `show visible change (needs ${MIN_LIVE}) — an invisible animation is `
                         + `instrument-food, not motion; make it visible or make the plate still`);
  console.log(`  ${invisible ? '!!' : '..'} ${f.padEnd(24)} gesture visible in ${String(r.live).padStart(3)}/${r.n} samples`);
}
await browser.close();

if (!GATE) {
  console.log(`\n  ${rows.length - new Set(fail.map(s => s.split(':')[0])).size}/${rows.length} plates pass.`);
} else if (fail.length) {
  console.error('\nMOTION GATE FAILED\n' + fail.map(s => '  ' + s).join('\n'));
  process.exit(1);
} else {
  console.log(`\nMOTION GATE PASSED — every declared gesture is visible; stillness is legal.`);
}
