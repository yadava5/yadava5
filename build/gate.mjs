/**
 * The motion gate.
 *
 * Gate v1 was char-count arithmetic. It printed GATE PASSED over nine
 * overlapping text runs.
 *
 * Gate v2 rendered in Chromium and measured real geometry — but only at rest,
 * and it sampled only *opacity* across the loop. Every plate moves things with
 * `transform`. So a token that slides on top of a label, or comes to rest
 * across a word, was invisible to it. Two shipped that way.
 *
 * This one seeks the shared clock across the whole loop and measures POSITION
 * at every step, via getBoundingClientRect (which applies the transform;
 * getBBox does not). A collision that exists for one frame is a collision.
 *
 *   1. renders at all, as image/svg+xml
 *   2. text never overlaps text          — at any t
 *   3. text never overlaps a graphic     — at any t
 *   4. nothing leaves the canvas         — at any t
 *   5. text stays in the type column     — at any t
 *   6. frame zero is the finished frame  — opacity AND stroke-dashoffset
 *   7. nothing hides for most of its loop
 *   8. nothing teleports while visible
 *   9. every number in <desc> is drawn on the plate
 */
import { chromium } from 'playwright';
import { readFileSync, readdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const ASSETS = join(ROOT, 'assets');
const LEFT = 150, RIGHT = 730;
const M_LEFT = 30, M_RIGHT = 412;   // the 440-wide mobile canvas
const STEPS = 40;                   // samples across one loop
const TOL = 1.5;                    // antialiasing slack, in viewBox units
const fails = [];
const frame = [];   // desktop-only: first ink and right edge, for check 12

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

  // measure inside the live document, where the animations actually run
  await page.setContent(`<body style="margin:0">${svg}</body>`);
  const mobile = /^m-/.test(file);
  const L = mobile ? M_LEFT : LEFT, R = mobile ? M_RIGHT : RIGHT;

  const found = await page.evaluate(async ({ L, R, STEPS, TOL }) => {
    // The @font-face is a base64 data: URI, but it is still loaded
    // ASYNCHRONOUSLY. Measuring before it resolves measures the FALLBACK font —
    // which is how the same string came out 710u locally and 724u on Linux CI,
    // and why a platform-dependent gate result looked like a platform bug.
    await document.fonts.ready;
    const out = [];
    // And if it did not actually load, say so loudly. A silent fallback shifts
    // every measurement on the plate and makes the whole gate meaningless.
    if (!document.fonts.check("16px M")) out.push('the embedded mono webfont did not load — all geometry below is the fallback font');

    const svgEl = document.querySelector('svg');
    const H = svgEl.viewBox.baseVal.height, W = svgEl.viewBox.baseVal.width;
    // Chromium on Linux advances ~4% wider than on macOS for this same embedded
    // woff2, and the error accumulates per character — so a label that fits the
    // column on one machine overruns it on the other, and a gate whose verdict
    // depends on who ran it is not a gate. Measure a reference run of 40 lbl
    // glyphs, compare against the authored baseline, and normalise every
    // column measurement by the ratio. Collisions are deliberately NOT
    // normalised: if type actually touches on a real platform, that is real.
    const REF = 448;
    const probe = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    probe.setAttribute('class', 'lbl'); probe.setAttribute('x', '0'); probe.setAttribute('y', '0');
    probe.textContent = 'M'.repeat(40);
    svgEl.appendChild(probe);
    const metric = probe.getBoundingClientRect().width / REF || 1;
    probe.remove();


    // ── what counts as an element worth measuring
    const drawables = [...svgEl.querySelectorAll('text,rect,circle,path')].filter(el => {
      if (el.tagName === 'text') return el.textContent.trim().length > 0;
      // the slab and its border are the page, not content
      const r = el.getBBox();
      return !(r.width >= W - 2 && r.height >= H - 2);
    });

    const name = el => {
      if (el.tagName === 'text') return `"${el.textContent.trim().slice(0, 30)}"`;
      const c = el.getAttribute('class');
      return `<${el.tagName}${c ? '.' + c.split(/\s+/)[0] : ''} ${Math.round(el.getBBox().x)},${Math.round(el.getBBox().y)}>`;
    };
    // elements composed together on purpose (same <g>) may overlap
    const groupOf = el => { let n = el.parentElement; while (n && n !== svgEl) { if (n.tagName === 'g') return n; n = n.parentElement; } return null; };
    // a hairline rule/connector is allowed to pass under type; a drawn glyph or
    // a filled token is not. Stroke weight is the discriminator: the structural
    // rules are all 1u, the ink that carries meaning is 7u and 15u.
    const isHairline = el => {
      const b = el.getBBox();
      if (el.tagName === 'path') return parseFloat(getComputedStyle(el).strokeWidth) <= 2;
      if (el.tagName === 'rect') return (b.height <= 3 || b.width <= 3);
      return false;
    };
    const isFrame = el => el.tagName === 'rect' && el.getAttribute('fill') === 'none';

    const meta = drawables.map(el => ({
      el, tag: el.tagName, nm: name(el), grp: groupOf(el),
      hair: isHairline(el), frame: isFrame(el),
      cls: el.getAttribute('class') || '',
    }));

    const anims = document.getAnimations();
    anims.forEach(a => { try { a.pause(); } catch {} });
    const dur = anims.length
      ? Math.max(...anims.map(a => a.effect.getComputedTiming().duration || 0)) : 0;

    const seek = t => anims.forEach(a => { try { a.currentTime = t; } catch {} });
    const opacityOf = el => { let o = 1, n = el; while (n && n !== svgEl) { o *= parseFloat(getComputedStyle(n).opacity); n = n.parentElement; } return o; };
    const snap = () => meta.map(m => {
      const r = m.el.getBoundingClientRect();
      const dof = parseFloat(getComputedStyle(m.el).strokeDashoffset);
      return { ...m, x: r.x, y: r.y, w: r.width, h: r.height, o: opacityOf(m.el),
               d: Number.isFinite(dof) ? dof : 0 };
    });

    const hit = (a, b) => Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x) > TOL
                      && Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y) > TOL;

    const steps = dur ? STEPS : 1;
    const seenVis = [];                 // per-element count of samples visible
    const peak = [];                    // per-element max opacity over the loop
    const frames = [];                  // every sample, kept for the rest check
    let zero = [], prev = null;

    for (let i = 0; i < steps; i++) {
      const t = dur ? dur * i / steps : 0;
      seek(t);
      const s = snap();
      frames.push(s.map(e => ({ x: e.x, y: e.y, w: e.w, h: e.h, o: e.o, d: e.d })));
      const at = dur ? ` at t=${(t / 1000).toFixed(2)}s` : '';
      const vis = s.filter(e => e.o >= 0.5);

      for (let a = 0; a < vis.length; a++) {
        const A = vis[a];

        // 4 — the canvas
        if (A.x < -TOL || A.y < -TOL || A.x + A.w > W + TOL || A.y + A.h > H + TOL)
          out.push(`${A.nm} leaves the canvas${at} (${Math.round(A.x)},${Math.round(A.y)} ${Math.round(A.w)}x${Math.round(A.h)}, canvas ${W}x${H})`);

        // 5 — the type column. Left-anchored text must stop SAFE=6u short of
        //     the edge: the same string measured 730 on macOS and 733 on Linux
        //     CI, so anything flush against the column is a platform coin-flip.
        //     text-anchor="end" is exempt — its right edge is exact by
        //     construction, and it is the start that floats.
        if (A.tag === 'text') {
          const anchored = getComputedStyle(A.el).textAnchor === 'end';
          const w = anchored ? A.w : A.w / metric + 6;   // 6u of design margin
          if (A.x < L - TOL || A.x + w > R + TOL)
            out.push(`${A.nm} outside the ${L}-${R} column${at} (${Math.round(A.x)}->${Math.round(A.x + A.w)})`);
        }

        for (let b = a + 1; b < vis.length; b++) {
          const B = vis[b];
          if (A.grp && A.grp === B.grp) continue;         // composed on purpose
          if (!hit(A, B)) continue;
          const kinds = [A.tag, B.tag];

          // 2 — text on text is always wrong
          if (kinds[0] === 'text' && kinds[1] === 'text') {
            out.push(`${A.nm} collides with ${B.nm}${at}`);
            continue;
          }
          // 3 — text under a moving graphic
          if (kinds.includes('text')) {
            const T = A.tag === 'text' ? A : B, G = A.tag === 'text' ? B : A;
            if (G.hair) continue;                          // rules pass under type
            if (G.frame) {                                 // a box may CONTAIN a label
              const inside = T.x >= G.x - TOL && T.x + T.w <= G.x + G.w + TOL
                          && T.y >= G.y - TOL && T.y + T.h <= G.y + G.h + TOL;
              if (inside) continue;
              out.push(`${T.nm} straddles the edge of ${G.nm}${at} — neither inside nor out`);
              continue;
            }
            out.push(`${G.nm} sits on top of ${T.nm}${at}`);
            continue;
          }
          // Graphic on graphic. Proven blind: an opaque rect laid across three
          // tenant rows and the RLS boundary drew ZERO findings from this gate.
          // A frame legitimately contains its children; a hairline legitimately
          // passes under; everything else that overlaps is a collision.
          if (A.hair || B.hair) continue;
          const [F, C] = A.frame ? [A, B] : [B, A];
          if (F.frame && C.x >= F.x - TOL && C.x + C.w <= F.x + F.w + TOL
                      && C.y >= F.y - TOL && C.y + C.h <= F.y + F.h + TOL) continue;
          out.push(`${A.nm} overlaps ${B.nm}${at}`);
        }
      }

      // Per ELEMENT, not per class. Summing a 16-element class and dividing by
      // `steps` produced 16.0 against a 0.70 floor — a class of n elements could
      // only trip it if the average element were visible under 70/n percent.
      // The floor was live on 12 of 44 groups and unreachable on the rest.
      s.forEach((e, k) => { seenVis[k] = (seenVis[k] || 0) + (e.o >= 0.5 ? 1 : 0); });

      // 6 — frame zero must be the finished frame. An element authored faint on
      //     purpose (a 0.45 hairline) is not a defect; an element ANIMATED to
      //     invisible at t=0 is. So compare t=0 against each element's own peak,
      //     which needs the whole loop — evaluated after the sampling ends.
      s.forEach((e, k) => { peak[k] = Math.max(peak[k] ?? 0, e.o); });
      if (i === 0) {
        zero = s.map(e => e.o);
        for (const e of s) {
          const st = getComputedStyle(e.el);
          const da = parseFloat(st.strokeDasharray), dof = parseFloat(st.strokeDashoffset);
          if (da > 0 && Math.abs(dof) / da > 0.5)
            out.push(`${e.nm} is undrawn at frame zero (dashoffset ${dof}/${da})`);
        }
      }

      // 8 — a visible thing must not teleport
      if (prev) for (let k = 0; k < s.length; k++) {
        const p = prev[k], c = s[k];
        if (p.o >= 0.5 && c.o >= 0.5) {
          const d = Math.hypot(c.x - p.x, c.y - p.y);
          if (d > 160) out.push(`${c.nm} teleports ${Math.round(d)}u in one step${at}`);
        }
      }
      prev = s;
    }

    // 6 (concluded) — an element the loop brings to full strength must already
    //     be at full strength at t=0. Statically faint things are left alone.
    meta.forEach((m, k) => {
      if (peak[k] >= 0.5 && zero[k] < peak[k] - 0.01)
        out.push(`${m.nm} is dimmed at frame zero (${zero[k].toFixed(2)} of ${peak[k].toFixed(2)})`);
    });

    // 11 — WHERE A TOKEN COMES TO REST.
    //
    // Every other check here asks whether the plate is well-formed. None of
    // them can see the defect that has cost this document the most: a diagram
    // that is clean, legible, collision-free — and depicts the opposite of its
    // own caption. Plate V once showed tenant A asking and B receiving. Plate
    // VI's token waited for its human 110u short of the gate, inside a wall.
    // Both passed every check above.
    //
    // So the claim is authored next to the drawing: the moving element carries
    // data-rest="<id of what it should reach>", and this asserts it. Rest is
    // the longest run of consecutive samples where the element is visible and
    // its position is stable — the pose a reader actually sees, since these
    // timelines deliberately hold their final frame for most of the loop.
    const restOf = (k) => {
      let best = { len: 0 }, run = 0, start = 0;
      for (let i = 0; i < frames.length; i++) {
        const c = frames[i][k], p = i ? frames[i - 1][k] : null;
        const still = p && c.o >= 0.5 && Math.abs(c.x - p.x) < 1 && Math.abs(c.y - p.y) < 1;
        if (still) { if (!run) start = i - 1; run++; } else run = 0;
        if (run > best.len) best = { len: run, at: start, f: c };
      }
      return best.len ? best : null;
    };
    meta.forEach((m, k) => {
      const want = m.el.getAttribute('data-rest');
      if (!want) return;
      const within = parseFloat(m.el.getAttribute('data-rest-within') || '24');
      const target = svgEl.querySelector(`#${CSS.escape(want)}`);
      if (!target) {
        out.push(`${m.nm} declares data-rest="${want}", which is not an element on this plate`);
        return;
      }
      const rest = restOf(k);
      if (!rest) { out.push(`${m.nm} declares a rest position but never holds still`); return; }
      // gap between the two boxes, 0 when they touch or overlap.
      // getBoundingClientRect returns width/height, NOT w/h — reading T.w gave
      // undefined, so every gap computed as NaN and `NaN > within` is false.
      // The check silently passed everything, including a token resting 24u
      // short of the wall it is supposed to be stopped by. That is the third
      // gate in this repo that could not fail; it was caught only because the
      // negative test was run before the code was trusted. Run the negative
      // test. A green gate you have not tried to break is decoration.
      const T = target.getBoundingClientRect(), r = rest.f;
      const dx = Math.max(T.x - (r.x + r.w), r.x - (T.x + T.width), 0);
      const dy = Math.max(T.y - (r.y + r.h), r.y - (T.y + T.height), 0);
      const gap = Math.hypot(dx, dy);
      if (!Number.isFinite(gap)) {
        out.push(`${m.nm}: rest-position check computed a non-finite gap — the check is broken, not the plate`);
        return;
      }
      const held = Math.round((rest.len / steps) * 100);
      if (gap > within)
        out.push(`${m.nm} should come to rest at #${want} but stops ${Math.round(gap)}u away `
               + `(allowed ${within}u), and holds there for ${held}% of the loop`);
    });

    // 13 — DOES IT MOVE, AND HOW OFTEN.
    //
    // Nothing here ever asked whether a plate animates at all, or whether it
    // animates for more than a moment. Measured across the desktop set: every
    // plate was reveal-then-hold, and 55.8% of all loop-seconds showed nothing
    // moving — plate 0 was 77% frozen and plate VII 69%, on the plate that
    // asserts ANIMATED SVG. Both passed every check, because a frozen plate has
    // no collisions.
    //
    // Motion is measured between consecutive samples, on the frames already
    // collected: an interval counts as alive if any element's box or opacity
    // moved. That is cheaper than a pixel diff and it cannot be fooled by a
    // change too small to see, because sub-unit drift is excluded.
    if (dur) {
      let alive = 0;
      for (let i = 1; i < frames.length; i++) {
        const moved = frames[i].some((c, k) => {
          const p = frames[i - 1][k];
          return Math.abs(c.x - p.x) > 0.5 || Math.abs(c.y - p.y) > 0.5
              || Math.abs(c.w - p.w) > 0.5 || Math.abs(c.o - p.o) > 0.02
              || Math.abs(c.d - p.d) > 0.002;
        });
        if (moved) alive++;
      }
      const frac = alive / (frames.length - 1);
      if (frac < 0.35)
        out.push(`only ${Math.round(frac * 100)}% of this loop shows anything moving `
               + `(floor 35%) — it reveals once and then holds for the rest`);
    }

    // 14 — A STAGGER TOO SMALL TO SEE IS NOT A STAGGER.
    //
    // Plate I's four kernel tokens were 0.06s apart on a 9.1s loop — 0.66% —
    // and all four measured at the identical x at every sample. The plate's
    // whole point is three hand-written kernels and one autovectorised build,
    // and the distinction was carried by a string and by nothing visual.
    const byClass = new Map();
    for (const a of anims) {
      const el = a.effect?.target;
      if (!el || !el.getAttribute) continue;
      const c = el.getAttribute('class');
      if (!c) continue;
      const d = Math.abs(a.effect.getComputedTiming().delay || 0);
      for (const k of c.split(/\s+/)) {
        if (!byClass.has(k)) byClass.set(k, new Set());
        byClass.get(k).add(Math.round(d));
      }
    }
    for (const [k, delays] of byClass) {
      if (delays.size < 2 || !dur) continue;
      const d = [...delays].sort((a, b) => a - b);
      const step = (d[d.length - 1] - d[0]) / (d.length - 1);
      if (step / dur < 0.04)
        out.push(`.${k} staggers ${(step / dur * 100).toFixed(2)}% of its loop across `
               + `${d.length} elements (floor 4%) — too small to read as a sequence`);
    }

    // 7 — evidence that blinks. At 50% the page still looked broken: a reader
    //     scrolling past sees a different quarter of the argument missing every
    //     second, because the loops are deliberately near-coprime and never
    //     align. A reveal is allowed; a long absence is not.
    if (dur) meta.forEach((m, k) => {
      const f = (seenVis[k] || 0) / steps;
      if (f < 0.7) out.push(`${m.nm} is visible only ${Math.round(f * 100)}% of the loop`);
    });

    // 10 — contrast. WCAG 1.4.11 wants 3:1 for non-text that carries meaning,
    //      1.4.3 wants 4.5:1 for body text. Every structural line on this
    //      document once sat between 1.08:1 and 1.94:1 — the numbers were drawn
    //      at AAA and the mechanism behind them at half the floor, which is the
    //      precise inverse of what the page argues.
    seek(0);
    const lin = c => { c /= 255; return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); };
    const lum = ([r, g, b]) => 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b);
    const parse = s => (s.match(/[\d.]+/g) || []).map(Number);
    const over = (fg, bg, al) => fg.map((c, i) => c * al + bg[i] * (1 - al));
    const SLABRGB = parse(getComputedStyle(svgEl.querySelector('rect')).fill);
    const ratio = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p); return (x + 0.05) / (y + 0.05); };

    for (const m of meta) {
      const st = getComputedStyle(m.el);
      const alpha = parseFloat(st.opacity);
      if (alpha < 0.05) continue;
      // A shape outlined in something legible is legible: WCAG asks that the
      // component be perceivable, not that every channel of it clear 3:1.
      const strokeOK = (() => {
        const sv = st.stroke;
        if (!sv || sv === 'none') return false;
        const c = parse(sv); if (c.length < 3) return false;
        const e = over(c.slice(0, 3), SLABRGB, (c.length > 3 ? c[3] : 1) * alpha);
        return ratio(e, SLABRGB) >= 3.0;
      })();
      for (const prop of ['fill', 'stroke']) {
        if (prop === 'fill' && m.tag !== 'text' && strokeOK) continue;
        const raw = st[prop];
        if (!raw || raw === 'none' || raw.startsWith('url')) continue;
        // A stroke-only <path> still computes fill:black, which paints nothing.
        // Only judge a shape's fill when the file actually asked for one.
        if (prop === 'fill' && m.tag !== 'text' && !m.el.hasAttribute('fill')) continue;
        const rgb = parse(raw);
        if (rgb.length < 3) continue;
        const a = (rgb.length > 3 ? rgb[3] : 1) * alpha;
        if (a < 0.05) continue;
        const eff = over(rgb.slice(0, 3), SLABRGB, a);
        const r = ratio(eff, SLABRGB);
        if (r >= 3.0 || Math.abs(r - 1) < 0.02) continue;          // 1:1 == it IS the slab
        const need = m.tag === 'text' ? 4.5 : 3.0;
        if (r < need)
          out.push(`${m.nm} ${prop} is ${r.toFixed(2)}:1 on the slab (needs ${need}:1)`);
      }
    }

    return [...new Set(out)];
  }, { L, R, STEPS, TOL });

  for (const f of found) fails.push(`${file}: ${f}`);

  // desktop plates only — the mobile set is a different canvas and a different
  // column, so comparing their margins to the desktop set would be meaningless
  if (!mobile) {
    const g = await page.evaluate(() => {
      const svg = document.querySelector('svg');
      const H = svg.viewBox.baseVal.height, W = svg.viewBox.baseVal.width;
      const els = [...svg.querySelectorAll('text,rect,circle,path')].filter(e => {
        const b = e.getBBox();
        return !(b.width >= W - 2 && b.height >= H - 2) && !(b.width <= 5 && b.height >= H - 2);
      });
      let top = 1e9, right = -1;
      for (const e of els) {
        const c = e.getBoundingClientRect();
        if (!c.width && !c.height) continue;
        top = Math.min(top, c.y); right = Math.max(right, c.x + c.width);
      }
      return { top, rightGap: W - right };
    });
    frame.push(g);
  }

  // 9 — every number the description claims must be drawn on the plate.
  //     (This only proves the two authored strings agree. It cannot prove
  //     either is TRUE — claims.json is what ties them to a repo.)
  const drawn = svg.replace(/<style[\s\S]*?<\/style>/g, ' ')
                   .replace(/<(?:title|desc)>[\s\S]*?<\/(?:title|desc)>/g, ' ')
                   .replace(/<[^>]*>/g, '').replace(/,/g, '');
  const meta = [...svg.matchAll(/<(?:title|desc)>([^<]*)<\/(?:title|desc)>/g)].map(m => m[1]).join(' ').replace(/,/g, '');
  // The desktop plate carries the whole argument, so its description must not
  // claim a number the plate does not draw. The mobile plate deliberately shows
  // a subset of the same shared description, so the check runs the other way:
  // every number it DOES draw must be one the description accounts for.
  const numsOf = s => [...new Set((s.match(/\d+\.\d+|\b\d+\b/g) || []))];
  if (mobile) {
    for (const n of numsOf(drawn))
      if (!meta.includes(n) && !/^(440|208)$/.test(n))
        fails.push(`${file}: draws "${n}", which its description does not account for`);
  } else {
    for (const n of numsOf(meta))
      if (!drawn.includes(n) && !/^(880)$/.test(n))
        fails.push(`${file}: description says "${n}" but the plate never draws it`);
  }

  console.log(`  measured ${file}`);
}

// 12 — THE DOCUMENT, not the plate.
//
// Everything above measures one plate at a time, and a multi-plate document
// lives in the relationship between them. Measured before this existed: first
// ink at 19, 23, 40 and 56; rightmost ink 150, 164, 164.8 and 166 short of the
// canvas — so the right edge visibly wandered as you scrolled and the top
// margin had three values. Neither gate could see it, because neither ever
// compared two plates.
const spread = (xs) => Math.max(...xs) - Math.min(...xs);
const tops = frame.map(f => f.top), rights = frame.map(f => f.rightGap);
if (spread(tops) > 2)
  fails.push(`the desktop plates start at ${tops.map(t => Math.round(t)).join('/')} — the first ink must sit on one line across the document`);
if (spread(rights) > 2)
  fails.push(`the desktop plates end ${rights.map(r => Math.round(r)).join('/')} short of the canvas — the right edge wanders as you scroll`);

await browser.close();
if (fails.length) {
  console.log(`\nGATE FAILED — ${fails.length} defects:`);
  for (const f of fails) console.log(`  · ${f}`);
  process.exit(1);
}
console.log(`\nGATE PASSED — ${STEPS} samples across every loop: no collision, no overflow, frame zero complete.`);
