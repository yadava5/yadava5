// Rasterise every plate to PNG so a human (or a design agent) can look at what
// the generator actually draws. gate.mjs measures geometry and motion.mjs
// measures pixels-changed; neither produces an image anyone can SEE, which is
// how a plate can pass every gate and still look wrong.
//
//   node build/snapshot.mjs [outDir] [--t 0.0,0.35,0.7]
//
// Writes <outDir>/<plate>@<t>.png at the width the README column actually
// renders at (GitHub caps the content column near 880 CSS px).
import { chromium } from 'playwright';
import { readdirSync, mkdirSync, readFileSync } from 'node:fs';
import { join, resolve } from 'node:path';

const outDir = resolve(process.argv[2] && !process.argv[2].startsWith('--') ? process.argv[2] : 'snapshots');
const tArg = process.argv.indexOf('--t');
const TIMES = tArg > -1 ? process.argv[tArg + 1].split(',').map(Number) : [0.0];

const ASSETS = resolve('assets');
const COLUMN = 880;                     // GitHub's readme content column, CSS px

mkdirSync(outDir, { recursive: true });

// Light variants are half the audience and live in a subdirectory, so a plain
// readdir of assets/ silently reviews only the dark half of the page.
const files = [
  ...readdirSync(ASSETS).filter(f => f.endsWith('.svg')).sort(),
  ...readdirSync(join(ASSETS, 'light')).filter(f => f.endsWith('.svg')).sort()
    .map(f => join('light', f)),
];
const browser = await chromium.launch();

for (const f of files) {
  const svg = readFileSync(join(ASSETS, f), 'utf8');
  const vb = /viewBox="([\d.\-\s]+)"/.exec(svg);
  const [, , vw, vh] = vb ? vb[1].trim().split(/\s+/).map(Number) : [0, 0, 1000, 500];
  const isMobile = f.startsWith('m-');
  const width = isMobile ? 440 : COLUMN;
  const height = Math.round(width * (vh / vw));

  const page = await browser.newPage({
    viewport: { width, height },
    deviceScaleFactor: 2,
    // The plates are dark-first; light variants live in assets/light.
    colorScheme: 'dark',
  });
  // Load the SVG as a document but force it to fill the viewport the way the
  // README column does — a bare file:// load renders at the intrinsic size and
  // leaves you judging a plate at the wrong scale, with letterboxing.
  await page.goto('file://' + join(ASSETS, f));
  // (An SVG document has no <head>, so addStyleTag cannot be used — the root
  // element IS the <svg>, and sizing it is a matter of its own attributes.)
  await page.evaluate(() => {
    const svg = document.documentElement;
    svg.setAttribute('width', '100%');
    svg.setAttribute('height', '100%');
    svg.style.display = 'block';
  });
  await page.waitForTimeout(400);       // let webfonts decode

  for (const t of TIMES) {
    // Seek by ITERATION duration, not activeDuration. Every plate here loops
    // `infinite`, which makes activeDuration Infinity — so a Number.isFinite
    // guard silently skips every seek and each "sample" returns the identical
    // frame. That is a snapshot tool that cannot show motion, reporting success:
    // it made a rule parked across a row look like a scan line caught mid-sweep.
    await page.evaluate(t => {
      for (const a of document.getAnimations()) {
        a.pause();
        const d = a.effect?.getComputedTiming?.().duration;   // one iteration, ms
        if (Number.isFinite(d) && d > 0) a.currentTime = d * t;
      }
    }, t);
    await page.waitForTimeout(60);
    const tag = TIMES.length > 1 ? `@${t}` : '';
    await page.screenshot({ path: join(outDir, `${f.replace('.svg', '')}${tag}.png`) });
  }
  await page.close();
  process.stdout.write(`${f} ${width}x${height}\n`);
}

await browser.close();
console.log(`\n${files.length} plates -> ${outDir}`);
