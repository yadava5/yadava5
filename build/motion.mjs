/**
 * Does the page actually MOVE — all of it, all the time?
 *
 * RE-AUTHORED, round 21, deliberately and in the same change as the design it
 * measures. This file has now enforced three doctrines, and the history is
 * the argument for the current one:
 *
 *   v1 (rounds ~14-18): ">=25% of intervals must move, never hold >2.4s."
 *      A quota. It got what quotas get — seven travelling hairlines whose
 *      own comments admitted they existed to feed this gate, four of them
 *      striking through text. Decoration engineered for an instrument.
 *   v2 (rounds 19-20): "stillness is legal; a declared gesture must merely
 *      be visible." A sound correction of v1's failure — and eight of ten
 *      plates took the permission and froze for 84-100% of their loops
 *      (raster-measured, 100ms steps). The client's verdict on the result
 *      was "very static feel", and the one plate he did not criticise was
 *      the only one at 100% liveness: the rider in continuous travel.
 *   v3 (now): the rider is the floor. Every plate carries a continuous
 *      carrier plus its gesture, so the gate demands BOTH:
 *
 *      · a plate with NO animations fails — stillness is no longer a legal
 *        design on this page, because the page's brief is to be alive
 *      · SUSTAINED: >=95% of a desktop plate's sampled intervals must clear
 *        FLOOR/10. The divisor is measured, not soft: the round-20 rider ran
 *        0.028-0.035% per 100ms in EVERY interval and was unmissable,
 *        because the eye tracks coherent displacement (smooth pursuit);
 *        per-interval repaint area is the wrong model for it. FLOOR/10
 *        still demands ~50+ real pixels changing every 100ms, which no
 *        dead-code animation produces.
 *      · GESTURE: >=3 intervals must clear the full FLOOR — some moment of
 *        each loop must read at a glance, not only under pursuit. A plate
 *        may also satisfy this clause with a carrier strong enough to BE
 *        the glance: >=90% of intervals at FLOOR/4. Measured, not assumed:
 *        the title page's drifting leader field clears FLOOR/4 in 270 of
 *        270 samples — ten times the old page's median liveness — and
 *        demanding it ALSO fire a repaint burst is exactly the quota
 *        thinking that grew v1's travelling hairlines.
 *
 *      The v1 failure mode cannot return through this door: v1 punished
 *      stillness ANYWHERE (so plates grew roving junk to keep every second
 *      busy), while v3 asks for one honest carrier — and the carrier is a
 *      design element chosen per section (a scan, a stream, a conveyor, a
 *      nib, a needle, a sweep, a ring), asserted here only in pixels.
 *
 *   The mobile set enters the gate for the first time this round (it was
 *   never measured before — scope-widening, not loosening). Its plates are
 *   hero cards with one gliding highlight, so they are held to the carrier
 *   clause at a gentler 70% and excused the gesture clause: a 440u card has
 *   no room for a second system of motion, and demanding one is how v1
 *   grew hairlines.
 *
 * Both themes still measured separately: an opacity tuned on the dark canvas
 * can drop a carrier under the floor on the light one. The plates are
 * transparent, so each set is rastered over the canvas it ships on.
 *
 * Usage: node build/motion.mjs [--step 100] [--floor 0.002] [--gate]
 */
import { chromium } from 'playwright';
import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

// Honour GATE_ASSETS like gate.mjs does, so build/mutations.mjs can point
// this file at a directory of deliberately-broken plates.
const ASSETS = process.env.GATE_ASSETS || join(dirname(fileURLToPath(import.meta.url)), '..', 'assets');
const arg = (n, d) => { const i = process.argv.indexOf(n); return i > 0 ? Number(process.argv[i + 1]) : d; };
const STEP = arg('--step', 100);          // ms between samples
const FLOOR = arg('--floor', 0.002);      // fraction of pixels that must change
const SUS_DESKTOP = 0.95;                 // carrier floor, desktop
const SUS_MOBILE = 0.70;                  // carrier floor, mobile hero cards
const MIN_LIVE = 3;                       // intervals the gesture must clear
const GATE = process.argv.includes('--gate');

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 520, height: 760 } });
const rows = [];

// Diffing has to happen on the LIVE render. Serialising the animated SVG and
// re-rasterising it through an <img> restarts the CSS clock from zero — every
// frame comes back identical. Playwright screenshots the real compositor
// output; the bytes go back into the page only to be decoded into pixels.
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

// The light set is REQUIRED here for the same reason it is in gate.mjs: it was
// conditional, so a missing directory halved what this gate measured and still
// printed MOTION GATE PASSED. Guarded in place rather than through a shared
// helper on purpose — a shared throw only fires where it is called, so probing
// it through one entry point would prove nothing about this one and would make
// a single probe look like it covered three gates.
//
// SCOPE: this particular guard has no probe in mutations.mjs, and that is a
// decision rather than an oversight. A motion family would cost a full
// Playwright frame-diff of every plate per probe, which is the slowest thing in
// the repository. gate.mjs's twin of this guard and claims.mjs's are both
// probed there. This one was falsified by hand on 2026-08-11 — run against a
// copied assets/ with light/ removed, it exits 1 — and it is not falsified
// again on every push. Stated so the gap is a boundary and not a silence.
const SETS = [{ dir: ASSETS, tag: '', bg: '#0d1117' }];
const LIGHT_DIR = join(ASSETS, 'light');
if (!existsSync(LIGHT_DIR)) {
  console.error(`\nMOTION GATE FAILED — ${LIGHT_DIR} does not exist. It holds the light `
    + `twin of every plate, and half a published set cannot pass a gate about what `
    + `readers see.`);
  process.exit(1);
}
SETS.push({ dir: LIGHT_DIR, tag: 'light/', bg: '#ffffff' });
const plates = SETS.flatMap(({ dir, tag, bg }) =>
  readdirSync(dir).filter(x => /^(plate|m)-.*\.svg$/.test(x)).sort().map(x => ({ dir, tag, bg, base: x })));

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
  if (!dur) { rows.push([f, { still: true, mobile: /^m-/.test(base) }]); continue; }
  const n = Math.max(2, Math.round(dur / STEP));
  const svg = page.locator('svg');
  let live = 0, sus = 0, strong = 0;   // gesture / carrier / strong-carrier
  for (let i = 0; i <= n; i++) {
    await page.evaluate((t) => document.getAnimations().forEach(a => { try { a.currentTime = t; } catch {} }),
      dur * i / n);
    const frac = await decodeAndDiff((await svg.screenshot()).toString('base64'), i === 0);
    if (i === 0) continue;
    if (frac >= FLOOR) live++;
    if (frac >= FLOOR / 4) strong++;
    if (frac >= FLOOR / 10) sus++;
  }
  rows.push([f, { still: false, mobile: /^m-/.test(base), live, sus, strong, n }]);
}

console.log(`  raster diff · ${STEP}ms steps · gesture floor ${(FLOOR * 100).toFixed(1)}% · carrier floor ${(FLOOR * 10).toFixed(2)}%\n`);
const fail = [];
for (const [f, r] of rows) {
  if (r.still) {
    fail.push(`${f}: declares no animations — stillness is no longer a legal design on this page`);
    console.log(`  !! ${f.padEnd(30)} STILL`);
    continue;
  }
  const susFloor = r.mobile ? SUS_MOBILE : SUS_DESKTOP;
  const pct = r.sus / r.n;
  const glance = r.live >= MIN_LIVE || r.strong / r.n >= 0.9;   // burst OR strong carrier
  const bad = pct < susFloor || (!r.mobile && !glance);
  if (pct < susFloor)
    fail.push(`${f}: carrier alive in only ${Math.round(pct * 100)}% of intervals (floor ${susFloor * 100}%) — the plate is holding a frozen frame`);
  if (!r.mobile && !glance)
    fail.push(`${f}: no moment of the loop reads at a glance (${r.live} gesture samples, `
            + `strong carrier in ${Math.round(r.strong / r.n * 100)}% — needs ${MIN_LIVE} bursts or 90%)`);
  console.log(`  ${bad ? '!!' : '..'} ${f.padEnd(30)} alive ${String(Math.round(pct * 100)).padStart(3)}% of loop · gesture in ${String(r.live).padStart(3)}/${r.n}`);
}
await browser.close();

if (!GATE) {
  console.log(`\n  ${rows.length - new Set(fail.map(s => s.split(':')[0])).size}/${rows.length} plates pass.`);
} else if (fail.length) {
  console.error('\nMOTION GATE FAILED\n' + fail.map(s => '  ' + s).join('\n'));
  process.exit(1);
} else {
  // THIRD correction of this one sentence, so the history is the warning.
  //   v1 "every plate sustains its carrier and lands its gesture" — false of
  //      the mobile set, which the gesture clause deliberately excuses.
  //   v2 "N are held to the gesture clause and land one" — read as though
  //      every desktop plate fires a burst.
  //   v3 "12 land a burst, 16 clear it as a carrier" — read as a PARTITION by
  //      route, which measurement refuted: the routes overlap completely.
  //
  // Measured on this design, and the reason v3 was still wrong: the clause has
  // two satisfying routes (`r.live >= MIN_LIVE || r.strong / r.n >= 0.9`), and
  // ALL held plates clear the second at 100% of intervals. `burst-only` is
  // ZERO — delete burst detection entirely and every plate still passes. So
  // the burst clause currently has no grip on anything, and any sentence
  // implying it carries some plates overstates the gate's hold. The burst
  // count is still worth printing, as the thing that would notice the carrier
  // weakening, but it is a subset and must read as one.
  //
  // Everything here is counted from the rows rather than written down. Every
  // stale number this comment has carried — "four of them report gesture in
  // 0/N" was three by the next run — was a literal somebody typed.
  const exempt = rows.filter(([, r]) => r.mobile).length;
  const held = rows.filter(([, r]) => !r.mobile);
  const strong = held.filter(([, r]) => r.strong / r.n >= 0.9).length;
  const burst = held.filter(([, r]) => r.live >= MIN_LIVE).length;
  const carrierOnly = strong === held.length;
  console.log(`\nMOTION GATE PASSED — all ${rows.length} plates sustain a carrier. `
    + (carrierOnly
        ? `All ${held.length} desktop plates clear the gesture clause as a carrier `
          + `strong enough to be the glance; ${burst} of them also land a burst. `
        : `${held.length} are held to the gesture clause: ${strong} clear it on the `
          + `carrier, ${held.length - strong} only on a burst. `)
    + `${exempt} mobile cards are excused it by design, not by accident.`);
}
