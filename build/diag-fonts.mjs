/**
 * TEMPORARY diagnostic — never merged to main.
 *
 * The gate fails on Linux CI and passes on macOS, in three shapes:
 *   a. serif plates' right edge lands 12-19u further left on CI
 *   b. anchored-end mono amounts overhang the column by ~3u on CI only
 *   c. two plates' first-ink top and bottom drift 3-4u
 *
 * Three candidate mechanisms, all platform fonts:
 *   1. .ser = ui-serif/Georgia/'Times New Roman' — none embedded
 *   2. .sub/.hero are font-weight:600 on an embedded 400 face — synthetic bold
 *   3. the mono subset has 70 glyphs and is missing , : @ ’ ( ) — those
 *      characters fall back to the platform mono
 *
 * This prints, for the failing plates: the actual platform font Chromium used
 * for each interesting glyph run (CDP CSS.getPlatformFontsForNode — measured,
 * not inferred), the probe metric, and the three rightmost elements exactly as
 * gate check 12 computes them. Run on both platforms, diff the output.
 */
import { chromium } from 'playwright';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const PLATES = ['plate-0-thesis.svg', 'plate-0b-work.svg', 'plate-4-applied.svg',
                'plate-6b-automl.svg', 'plate-7-colophon.svg', 'plate-8-visualassist.svg'];

// Theory to test: FreeType hinting rounds advances to whole pixels PER FONT
// SIZE, so a single 16px probe metric cannot normalise a document set in
// 13/21/34/55px. If true, this table is ~1.000 on macOS at every size and
// wanders per-size on Linux — and flattens back to ~1.000 under
// --font-render-hinting=none.
const sizeTable = async (page) => {
  const one = readFileSync(join(ROOT, 'assets', 'plate-0b-work.svg'), 'utf8');
  await page.setContent(`<body style="margin:0">${one}</body>`);
  await page.evaluate(() => document.fonts.ready);
  return page.evaluate(() => {
    const svgEl = document.querySelector('svg');
    const out = {};
    for (const fs of [13, 16, 21, 34, 55]) {
      const t = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      t.setAttribute('style', `font-size:${fs}px`);
      t.setAttribute('x', '0'); t.setAttribute('y', '0');
      t.textContent = 'M'.repeat(40);
      svgEl.appendChild(t);
      // JetBrains Mono advance is 0.6em, so the unhinted truth is 24*fs
      out[fs] = +(t.getBoundingClientRect().width / (24 * fs)).toFixed(4);
      t.remove();
    }
    // and the anchored-end amounts: how far does '%' ink overhang x=730?
    const amounts = [...svgEl.querySelectorAll('text[text-anchor="end"].sub, text.sub')]
      .filter(e => e.getAttribute('text-anchor') === 'end')
      .map(e => ({ txt: e.textContent,
                   overhang: +(e.getBoundingClientRect().right - 644).toFixed(2) }));
    return { out, amounts };
  });
};

console.log(`platform: ${process.platform}`);

for (const hinting of [null, 'none']) {
  const b = await chromium.launch(hinting ? { args: [`--font-render-hinting=${hinting}`] } : {});
  const p = await b.newPage();
  const { out, amounts } = await sizeTable(p);
  console.log(`advance ratio by font-size (hinting=${hinting ?? 'default'}):`,
    JSON.stringify(out), 'amount ink overhang past col:', JSON.stringify(amounts));
  await b.close();
}

const browser = await chromium.launch();
const page = await browser.newPage();
const cdp = await page.context().newCDPSession(page);
await cdp.send('DOM.enable');
await cdp.send('CSS.enable');

for (const base of PLATES) {
  const svg = readFileSync(join(ROOT, 'assets', base), 'utf8');
  await page.setContent(`<body style="margin:0">${svg}</body>`);
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(() => document.getAnimations().forEach(a => { try { a.pause(); a.currentTime = 0; } catch {} }));

  const info = await page.evaluate(() => {
    const svgEl = document.querySelector('svg');
    const W = svgEl.viewBox.baseVal.width, H = svgEl.viewBox.baseVal.height;
    const REF = 448;
    const probe = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    probe.setAttribute('style', 'font-size:16px;letter-spacing:1.6px');
    probe.setAttribute('x', '0'); probe.setAttribute('y', '0');
    probe.textContent = 'M'.repeat(40);
    svgEl.appendChild(probe);
    const metric = probe.getBoundingClientRect().width / REF || 1;
    probe.remove();

    // mirror check 12's element set and normalisation
    const els = [...svgEl.querySelectorAll('text,rect,circle,path')].filter(e => {
      const b = e.getBBox();
      return !(b.width >= W - 2 && b.height >= H - 2) && !(b.width <= 5 && b.height >= H - 2);
    });
    const rows = els.map((e, i) => {
      const c = e.getBoundingClientRect();
      const w = e.tagName === 'text' ? c.width / metric : c.width;
      return { i, tag: e.tagName, cls: e.getAttribute('class') || '',
               txt: e.tagName === 'text' ? e.textContent.slice(0, 34) : '',
               x: +c.x.toFixed(1), rawRight: +(c.x + c.width).toFixed(1),
               normRight: +(c.x + w).toFixed(1),
               top: +c.y.toFixed(1), bottom: +(c.y + c.height).toFixed(1) };
    }).filter(r => r.rawRight || r.bottom);
    const byRight = [...rows].sort((a, b) => b.normRight - a.normRight).slice(0, 3);
    const byTop = [...rows].sort((a, b) => a.top - b.top).slice(0, 2);
    const byBottom = [...rows].sort((a, b) => b.bottom - a.bottom).slice(0, 2);
    // mark the interesting text elements for CDP inspection
    const interesting = new Set([...byRight, ...byTop, ...byBottom].map(r => r.i));
    // plus: any anchored-end .sub amount, any .ser line, any text with a
    // glyph outside the embedded subset
    const SUBSET = new Set(" %+-./0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz·—");
    els.forEach((e, i) => {
      if (e.tagName !== 'text') return;
      const cls = e.getAttribute('class') || '';
      if (/\bsub\b|\bser\b|\bhero\b/.test(cls)) interesting.add(i);
      if ([...e.textContent].some(ch => !SUBSET.has(ch))) interesting.add(i);
    });
    els.forEach((e, i) => { if (interesting.has(i)) e.setAttribute('data-diag', String(i)); });
    return { metric: +metric.toFixed(4), byRight, byTop, byBottom,
             monoLoaded: document.fonts.check('16px M'),
             rows: rows.filter(r => interesting.has(r.i)) };
  });

  console.log(`\n=== ${base}  metric=${info.metric}  monoLoaded=${info.monoLoaded}`);
  const show = (label, rs) => rs.forEach(r =>
    console.log(`  ${label} [${r.i}] <${r.tag}.${r.cls}> "${r.txt}" x=${r.x} rawRight=${r.rawRight} normRight=${r.normRight} top=${r.top} bottom=${r.bottom}`));
  show('right', info.byRight); show('top  ', info.byTop); show('bottom', info.byBottom);

  // the actual fonts used, per glyph run, per interesting element
  const doc = await cdp.send('DOM.getDocument');
  const { nodeIds } = await cdp.send('DOM.querySelectorAll',
    { nodeId: doc.root.nodeId, selector: '[data-diag]' });
  for (const nodeId of nodeIds) {
    const { node } = await cdp.send('DOM.describeNode', { nodeId });
    const attrs = {};
    for (let i = 0; i < (node.attributes || []).length; i += 2) attrs[node.attributes[i]] = node.attributes[i + 1];
    const { fonts } = await cdp.send('CSS.getPlatformFontsForNode', { nodeId });
    const runs = fonts.map(f => `${f.familyName}${f.isCustomFont ? '(embedded)' : '(SYSTEM)'} x${f.glyphCount}`).join(', ');
    console.log(`  fonts [${attrs['data-diag']}] .${(attrs.class || '').split(' ')[0]}: ${runs}`);
  }
}
await browser.close();
