/**
 * Ink coverage, per plate and for the document.
 *
 * The round-11 visual audit's most structural finding was not a defect in any
 * one plate — it was that ink covers 7.1% of the page. L=150/R=730 on an 880
 * canvas puts 34.1% of every plate's width into margin, and that margin existed
 * for one reason: legibility on a phone. Mobile is out of scope, so the reason
 * is gone and the emptiness is not.
 *
 * This measures it the way a reader sees it: rasterise the plate and count the
 * pixels that are not the slab. Geometry-based counting does not work — nested
 * <g> and <path> double-count, and plate I's 299 error marks took a bbox sum
 * to 846% of the canvas.
 *
 * It is a measurement, not a gate. Density is not automatically good; a plate
 * can be dense and unreadable. But you cannot argue about whether the document
 * feels empty without a number, and this is the number.
 */
import { chromium } from 'playwright';
import { readFileSync, readdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const ASSETS = join(dirname(fileURLToPath(import.meta.url)), '..', 'assets');
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 900, height: 800 } });
let inkTotal = 0, areaTotal = 0;

for (const f of readdirSync(ASSETS).filter(x => /^plate-.*\.svg$/.test(x)).sort()) {
  const svg = readFileSync(join(ASSETS, f), 'utf8');
  const r = await page.evaluate(async (s) => {
    document.body.innerHTML =
      `<img id="i" src="data:image/svg+xml;base64,${btoa(unescape(encodeURIComponent(s)))}">`;
    const img = document.getElementById('i');
    await new Promise(res => img.complete ? res() : (img.onload = res));
    await document.fonts.ready;
    const W = img.naturalWidth, H = img.naturalHeight;
    const c = document.createElement('canvas'); c.width = W; c.height = H;
    const x = c.getContext('2d'); x.drawImage(img, 0, 0);
    const d = x.getImageData(0, 0, W, H).data;
    // Derive the slab from the plate itself. This constant used to be a
    // hardcoded #0B0C0E and the slab moved to #0A0A0B without it — the number
    // stayed right only because the delta (6) was under the threshold (24).
    // A measurement tool carrying its own copy of the thing it measures will
    // eventually lie, quietly.
    const mid = ((H >> 1) * W + 4) * 4;
    const [sr, sg, sb] = [d[mid], d[mid + 1], d[mid + 2]];
    let ink = 0;
    for (let i = 0; i < d.length; i += 4)
      if (Math.abs(d[i] - sr) + Math.abs(d[i + 1] - sg) + Math.abs(d[i + 2] - sb) > 24) ink++;
    return { W, H, ink };
  }, svg);
  inkTotal += r.ink; areaTotal += r.W * r.H;
  console.log(`  ${f.padEnd(24)} ${(r.ink / (r.W * r.H) * 100).toFixed(2)}%`);
}
console.log(`\n  DOCUMENT INK COVERAGE: ${(inkTotal / areaTotal * 100).toFixed(2)}%`);
await browser.close();
