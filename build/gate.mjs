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
import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
// Overridable so build/mutations.mjs can point the whole gate at a directory
// of deliberately-broken plates. A check nobody has tried to break is a check
// nobody knows is connected.
const ASSETS = process.env.GATE_ASSETS || join(ROOT, 'assets');
// DEFAULT screen-space bounds of the type column (authored 150..730 minus the
// viewBox offset 86). RE-AUTHORED, round 20: the column is now a PER-PLATE
// DECLARATION — each desktop plate carries data-col="left,right" in authored
// units and check 5 holds its text to that. One fixed column for all ten
// figures was the frontispiece armature wearing a gate's uniform: the client
// rejected the sameness it enforced, and the redesign gives each section its
// own spatial system (a centered title page, a full-bleed copybook, a radial
// dial — none of which fit one column). The check itself survives untouched
// in spirit: text still may not drift past its plate's declared frame, and a
// declaration is a decision a reviewer can read in the file.
const LEFT = 64, RIGHT = 644;
const M_LEFT = 30, M_RIGHT = 412;   // the 440-wide mobile canvas
const STEPS = 40;                   // samples across one loop
const TOL = 1.5;                    // antialiasing slack, in viewBox units
const fails = [];

// FreeType rounds glyph advances to the pixel grid PER FONT SIZE: measured on
// the runner (diag/ci-fonts, run 31143030894), the same embedded mono advanced
// +2.6% at 13px, +4.2% at 16px, +3.2% at 21px and −2% at 34px — so no
// single-size probe metric can normalise a document set in 13/21/34/55px, and
// that skew was the whole of the data-frame drift. Hinting off, the ratios
// measured 1.0000–1.0001 at every size. This measures the TYPE, not the
// rasteriser's grid; no tolerance changes. macOS has no FreeType — inert there.
// (The probe-metric normalisation below stays: it is the belt to this brace,
// and it is what catches an environment where this flag stops working.)
const browser = await chromium.launch({ args: ['--font-render-hinting=none'] });
const page = await browser.newPage();
// A second page with motion switched off. This is the authored attributes with
// no animation applied, which is what every STATIC RASTERISER produces: resvg,
// librsvg, share-card pipelines, PDF export.
//
// It is NOT what a reduced-motion reader sees, and this comment claimed it was
// for four rounds. `prefers-reduced-motion` does not propagate into an SVG
// referenced by an <img>; the media query is evaluated against that document's
// own isolated environment. On GitHub — the only place this page is published —
// every plate animates regardless of the reader's preference. That is a
// property of the medium, not a bug in the plates, and the colophon says so.
const still = await browser.newPage({ reducedMotion: 'reduce' });

// Two themes, one document. `assets/light/` holds a light-slab twin of every
// plate, served by <picture media="(prefers-color-scheme: light)">. It is not
// a second-class asset: GitHub's light theme is the DEFAULT, so for roughly
// half of all readers those files ARE the page, and they are measured by every
// check here. The contrast checks adapt on their own — they read the slab
// colour off the plate's own first <rect> rather than assuming a dark ground.
const SETS = [{ dir: ASSETS, tag: '' }];
const LIGHT_DIR = join(ASSETS, 'light');
if (existsSync(LIGHT_DIR)) SETS.push({ dir: LIGHT_DIR, tag: 'light/' });
const sheet = (re) => SETS.flatMap(({ dir, tag }) =>
  readdirSync(dir).filter(f => re.test(f)).sort().map(f => ({ dir, tag, file: f })));

for (const { dir, tag, file: base } of sheet(/^(plate|m)-.*\.svg$/)) {
  const file = tag + base;
  const svg = readFileSync(join(dir, base), 'utf8');

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
  const mobile = /^m-/.test(base);
  const L = mobile ? M_LEFT : LEFT, R = mobile ? M_RIGHT : RIGHT;

  const found = await page.evaluate(async ({ L, R, STEPS, TOL, isMobile }) => {
    // The @font-face is a base64 data: URI, but it is still loaded
    // ASYNCHRONOUSLY. Measuring before it resolves measures the FALLBACK font —
    // which is how the same string came out 710u locally and 724u on Linux CI,
    // and why a platform-dependent gate result looked like a platform bug.
    await document.fonts.ready;
    const out = [];
    // And if it did not actually load, say so loudly. A silent fallback shifts
    // every measurement on the plate and makes the whole gate meaningless.
    //
    // This checked "16px M" and nothing else. 'M' is the mono, so the SERIF —
    // family 'S', which sets every hero numeral on the page, the 89px "B only",
    // 6.4x, 0.979, 15/44 — had no such assertion at all. A serif that failed to
    // load would render the emotional centre of all nine plates in a platform
    // fallback and measure it there, silently, which is the exact failure this
    // line was written to prevent and the exact half of it that was missing.
    //
    // Derived from the document rather than hardcoded, so it cannot go stale
    // the next time a face is added or renamed: every @font-face the plate
    // DECLARES must actually be available at the weight it declares. The
    // faces have already been swapped once wholesale (JetBrains + Gelasio ->
    // Fragment Mono + Fraunces, 2026-08-08), and a hardcoded list would have
    // survived that swap while measuring nothing.
    // Two different defects hide behind one symptom, and telling them apart
    // matters. `fonts.check` is false both when a face FAILED to load and when
    // nothing on the plate ever asked for it — a browser will not fetch a
    // data: URI face no glyph needs. Reporting the second as the first would be
    // a false alarm, and false alarms are how a red build stops meaning
    // anything. So resolve what the plate ACTUALLY renders first, and judge
    // each declared face against that.
    const css = [...document.querySelectorAll('style')].map(s => s.textContent).join('\n');
    const faces = [...css.matchAll(/@font-face\{font-family:'([^']+)';font-weight:(\d+)/g)];
    if (!faces.length) out.push('this plate declares no @font-face — every glyph on it is a platform font');
    const rendered = new Set();
    for (const t of document.querySelectorAll('text, tspan')) {
      const cs = getComputedStyle(t);
      const fam = (cs.fontFamily.split(',')[0] || '').replace(/['"]/g, '').trim();
      rendered.add(`${fam}|${cs.fontWeight}`);
    }
    for (const [, fam, w] of faces) {
      if (!rendered.has(`${fam}|${w}`)) {
        // Dead payload. Every plate base64s its faces inline — GitHub fetches
        // nothing external — so a declared-and-unused face is not a tidiness
        // issue, it is kilobytes shipped to every reader on every view.
        out.push(`declares an '${fam}' ${w} face that nothing on the plate renders `
               + `— the base64 payload ships to every reader and is never used`);
        continue;
      }
      if (!document.fonts.check(`${w} 16px ${fam}`))
        out.push(`the embedded '${fam}' ${w} webfont did not load — every measurement that uses it is the fallback font`);
    }
    // And the reverse, which is the half that makes dropping a face SAFE. The
    // loop above can only judge faces the plate declares, so "stop embedding
    // the face nothing renders" would silently become "render in a platform
    // fallback" the day a plate grows a hero again. getComputedStyle reports
    // what the CSS ASKS for, not what resolved, so rendered-minus-declared is
    // exactly the set of glyphs riding a fallback.
    const declared = new Set(faces.map(([, f, w]) => `${f}|${w}`));
    for (const r of rendered) {
      const [fam, w] = r.split('|');
      if (/^(ui-|serif|sans|monospace|Georgia|Menlo)/.test(fam)) continue;
      if (!declared.has(r))
        out.push(`renders '${fam}' at weight ${w}, which no @font-face on this plate embeds `
               + `— those glyphs are a platform font and differ per reader`);
    }

    const svgEl = document.querySelector('svg');
    const H = svgEl.viewBox.baseVal.height, W = svgEl.viewBox.baseVal.width;
    // the plate's own declared column, if it carries one (see the note at the
    // top of the file). Authored units; the viewBox offset converts to screen.
    const colDecl = (svgEl.getAttribute('data-col') || '').split(',').map(Number);
    if (colDecl.length === 2 && colDecl.every(Number.isFinite)) {
      L = colDecl[0] - svgEl.viewBox.baseVal.x;
      R = colDecl[1] - svgEl.viewBox.baseVal.x;
    }
    // Chromium on Linux advances ~4% wider than on macOS for this same embedded
    // woff2, and the error accumulates per character — so a label that fits the
    // column on one machine overruns it on the other, and a gate whose verdict
    // depends on who ran it is not a gate. Measure a reference run of 40 lbl
    // glyphs, compare against the authored baseline, and normalise every
    // column measurement by the ratio. Collisions are deliberately NOT
    // normalised: if type actually touches on a real platform, that is real.
    // 40 x "M" at font-size 16 with letter-spacing 1.6, in the embedded mono.
    // WRITTEN AS ITS DERIVATION, not as a number: 448 was JetBrains Mono's
    // 600/1000 advance and it shipped as a bare literal, so when the face
    // changed there was nothing in the file to say what it had been measured
    // from. Fragment Mono (the portfolio's mono, adopted 2026-08-08) advances
    // 618/1000 — read from its hmtx — so every column and edge would have
    // mis-normalised by 2.6% against the old constant, silently and in the
    // direction that HIDES overflow.
    const REF = 40 * (16 * 618 / 1000 + 1.6);   // = 459.52
    const probe = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    // styled EXPLICITLY, not via class="lbl": the mobile plates never define
    // .lbl, so the probe there rendered at letter-spacing 0, the metric came
    // out 0.857, and every mobile column width was inflated ~17% — a latent
    // gate bug that surfaced the first time a mobile line was centered.
    probe.setAttribute('style', 'font-size:16px;letter-spacing:1.6px');
    probe.setAttribute('x', '0'); probe.setAttribute('y', '0');
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
    // Paints nothing, so it cannot cross anything. The AutoML needle carries a
    // deliberate zero-ink path — `M-110 -110h0.01M110 110h0.01`, two 0.01u dots
    // that pin the rotating group's fill-box onto the dial axis — whose 220x220
    // bounding box otherwise "sweeps across" every label on the plate. A
    // bounding box is not ink.
    const isInkless = (el) => {
      const cs = getComputedStyle(el);
      const noStroke = cs.stroke === 'none' || parseFloat(cs.strokeWidth) === 0
                    || parseFloat(cs.strokeOpacity) === 0;
      const noFill = cs.fill === 'none' || parseFloat(cs.fillOpacity) === 0;
      return noStroke && noFill;
    };

    const meta = drawables.map((el, i) => ({
      el, i, tag: el.tagName, nm: name(el), grp: groupOf(el),
      hair: isHairline(el), frame: isFrame(el), inkless: isInkless(el),
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

    // ── Which hairlines TRAVEL. Check 3 exempts every hairline from crossing
    // type — "rules pass under type" — which is right for a table divider that
    // holds still behind a label, and wrong for a rule that sweeps ACROSS one.
    // A moving rule over a word renders as a strikethrough, and this gate
    // passed 40 samples a loop while `task-lists*` on plate V and "CODE
    // COMPLIANCE, 61 PROJECTS" on plate I were both drawn cancelled. A true
    // claim rendered struck out is the worst thing a plate can do, and it is
    // exactly the frame a reader is most likely to get: GitHub serves these
    // through camo as <img>, so the loop phase anyone sees is arbitrary.
    const travel = meta.map(() => ({ x0: Infinity, x1: -Infinity, y0: Infinity, y1: -Infinity }));
    for (let i = 0; i < steps; i++) {
      seek(dur ? dur * i / steps : 0);
      snap().forEach((e, k) => {
        const t = travel[k];
        t.x0 = Math.min(t.x0, e.x); t.x1 = Math.max(t.x1, e.x);
        t.y0 = Math.min(t.y0, e.y); t.y1 = Math.max(t.y1, e.y);
      });
    }
    // 1 viewBox unit — under the threshold of vision, and above the sub-pixel
    // jitter a static element picks up from getBoundingClientRect rounding.
    const travels = travel.map(t => (t.x1 - t.x0) > 1 || (t.y1 - t.y0) > 1);

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
            // A rule that HOLDS STILL passes under type; one that travels
            // across it is a strikethrough. See the travel pass above.
            if (G.hair && (!travels[G.i] || G.inkless)) continue;
            if (G.hair) {
              out.push(`${G.nm} sweeps across ${T.nm}${at} — a moving rule over type reads as a strikethrough`);
              continue;
            }
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
          // "Undrawn" only means something for a DRAW-ON: one dash as long as
          // the whole path, revealed by pulling its offset to zero. A two-value
          // dasharray is a repeating pattern -- a travelling pulse -- and it is
          // never "undrawn", it is just somewhere along the line. Reading
          // parseFloat of "18px 222px" as the dash length called a perfectly
          // healthy pulse a frame-zero defect.
          const pat = (st.strokeDasharray || '').split(',').map(v => parseFloat(v)).filter(Number.isFinite);
          const da = pat[0], dof = parseFloat(st.strokeDashoffset);
          if (pat.length === 1 && da > 0 && Math.abs(dof) / da > 0.5)
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

    // 15 — WHAT WAS AUTHORED IS WHAT RENDERS.
    //
    // `fill="#34D399"` on a <text class="an lbl"> is a PRESENTATION ATTRIBUTE,
    // and a presentation attribute loses to any CSS rule — including this
    // document's own `.lbl{fill:#8A8F98}`. Fifteen text elements asked for an
    // accent colour and rendered grey, for rounds. Plate III's four parser
    // labels were grey while the four underlines they gloss were emerald, on
    // the plate whose entire thesis is that every span carries its parser.
    //
    // Nothing could see it: the contrast check only asks whether what renders
    // is legible, never whether it is what the file asked for. A silently
    // discarded attribute is the quietest defect in the medium — the build
    // succeeds, the gate passes, and the picture argues something else.
    const norm = (v) => (v || '').trim().toLowerCase()
      .replace(/\s+/g, '').replace(/px$/, '');
    const asRGB = (v) => {
      const m = /^#([0-9a-f]{6})$/.exec(norm(v));
      if (!m) return norm(v);
      const n = parseInt(m[1], 16);
      return `rgb(${n >> 16 & 255},${n >> 8 & 255},${n & 255})`;
    };
    for (const m of meta) {
      for (const [attr, prop] of [['fill', 'fill'], ['stroke', 'stroke'],
                                  ['letter-spacing', 'letterSpacing']]) {
        if (!m.el.hasAttribute(attr)) continue;
        const want = attr === 'letter-spacing' ? norm(m.el.getAttribute(attr))
                                               : asRGB(m.el.getAttribute(attr));
        const got = attr === 'letter-spacing' ? norm(getComputedStyle(m.el)[prop])
                                              : norm(getComputedStyle(m.el)[prop]);
        // CSS reports a zero letter-spacing as the keyword `normal`
        // `currentColor` is a keyword whose whole purpose is to resolve to
        // something else. It is not a discarded attribute.
        if (want === 'none' || want === '' || want === 'currentcolor') continue;
        if (attr === 'letter-spacing' && (want === '0' || want === 'normal')
            && (got === 'normal' || got === '0')) continue;
        // a unitless letter-spacing attribute is in user units; CSS reports px
        if (want !== got && !(attr === 'letter-spacing' && want === got.replace('px', '')))
          out.push(`${m.nm} asks for ${attr}="${m.el.getAttribute(attr)}" and renders ${getComputedStyle(m.el)[prop]} — a CSS rule is overriding the attribute`);
      }
    }

    // 19 — A THING MUST NOT SPILL PAST THE EDGE THAT IS SUPPOSED TO HOLD IT.
    //
    // The gate could say where a token comes to REST (check 11) and nothing
    // about how far it strays in between. So plate II's blocks could sit 196u
    // wide inside a 120u bracket labelled BOUNDED IN-FLIGHT WINDOW, crossing
    // its far line by 82u for 45% of every loop — a window visibly failing to
    // bound, on the plate whose claim is that it bounds. Every other check
    // passed it, because overrunning a hairline is not a collision.
    //
    // Deliberately ONE-SIDED. My first version asserted containment on both
    // edges and fired on the fix as loudly as on the defect: a block that
    // travels INTO the window is legitimately outside it beforehand, and that
    // reads as arriving, not as spilling. The meaningful bound is the far one.
    // Authored in the plate's own coordinates and converted here, so the number
    // in plates.py is the number in the bracket's path.
    for (const m of meta) {
      const decl = m.el.getAttribute('data-max-x');
      if (!decl) continue;
      const hi = Number(decl) - svgEl.viewBox.baseVal.x;
      const k = meta.indexOf(m);
      let worst = 0, at = 0;
      frames.forEach((f, i) => {
        const e = f[k];
        if (e.o < 0.5) return;
        const over = (e.x + e.w) - hi;
        if (over > worst) { worst = over; at = i; }
      });
      if (worst > TOL)
        out.push(`${m.nm} spills ${Math.round(worst)}u past data-max-x="${decl}"`
               + `${dur ? ` at t=${(dur * at / steps / 1000).toFixed(2)}s` : ''}`);
    }

    // 13 — DECLARED MOTION MUST MOVE SOMETHING. RE-AUTHORED, round 19, in the
    //      same change as the design it measures.
    //
    // This check and check 17 used to enforce the opposite doctrine: a 35%
    // alive-floor across the loop, a 2.4s dead-run ceiling, and a failure for
    // any desktop plate with no animations at all. That regime is the
    // documented cause of the worst decoration in the set — seven travelling
    // hairlines whose own comments admitted they existed "to carry the raster
    // gate", four of them spending part of every loop striking through text,
    // including the author's own email on the colophon. A gate that demands
    // perpetual motion gets perpetual decoration; the failure was in the
    // doctrine, not the implementations.
    //
    // CAUTION — the paragraph above describes v2, a doctrine this page has
    // since abandoned, and reading it as current nearly cost a whole round.
    // "Still by default" was tried: eight of ten plates took the permission
    // and froze for 84-100% of their loops, and the verdict on the result was
    // "very static feel". build/motion.mjs is now on v3 and enforces the
    // OPPOSITE of what the text above implies — read its header before
    // trusting any motion claim in this file. Under v3 every plate carries a
    // continuous carrier plus its gesture, and a plate declaring no
    // animations at all fails there.
    //
    // What this check asserts is true under every one of the three doctrines,
    // which is why the code below never needed changing: a plate that
    // DECLARES animations none of which ever moves anything is not stillness,
    // it is dead code running on the reader's compositor — and it is exactly
    // how gate-food survives a redesign, the keyframes staying while the
    // travel gets zeroed and nothing notices.
    //
    // The division of labour: motion.mjs decides how much a plate must move,
    // in pixels. This decides that whatever it declares must be real.
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
      if (alive === 0)
        out.push(`declares animations that never move anything — not stillness, `
               + `dead code: delete the keyframes or give the gesture a visible travel`);
    }

    // 14 — A STAGGER IS A WAVE, NOT A QUEUE.
    //
    // This check used to enforce a 4% FLOOR, on the theory that plate I's
    // 0.66%-of-loop stagger was invisible. The floor was the wrong instrument
    // and it pushed the document the wrong way: raising every stagger to clear
    // it produced gaps of 300-900ms, and at 600ms between siblings a group
    // never reads as one gesture — plate 0's six swatches took 3.0s to finish a
    // ripple inside an 11.3s loop, six independent events rather than a wave.
    // Perception cares about the ABSOLUTE gap, not its fraction of the loop, so
    // the constraint is absolute: long enough to be a sequence, short enough to
    // be one gesture.
    const STAGGER_MIN = 40, STAGGER_MAX = 200;   // ms
    // Grouped by CLASS TOKEN until now, which one selector defeats. The colophon
    // writes `.ln,.ln2{animation:ln …}` — one gesture, three elements, relative
    // delays 0 / 150 / 1900ms. Split across two class names it became a `.ln`
    // group of two (gap 150, passes) and a `.ln2` group of one (size < 2,
    // skipped), so a 1750ms gap — 8.75x the stated ceiling — was invisible.
    // A stagger is a property of the GESTURE, so group by the keyframe name
    // that defines it.
    const byClass = new Map();
    for (const a of anims) {
      const el = a.effect?.target;
      if (!el || !el.getAttribute) continue;
      const k = a.animationName || (el.getAttribute('class') || '').split(/\s+/)[0];
      if (!k) continue;
      const d = Math.abs(a.effect.getComputedTiming().delay || 0);
      if (!byClass.has(k)) byClass.set(k, new Set());
      byClass.get(k).add(Math.round(d));
    }
    for (const [k, delays] of byClass) {
      if (delays.size < 2 || !dur) continue;
      const d = [...delays].sort((a, b) => a - b);
      // The MEAN step hides a hole. This computed (last - first)/(n-1), so
      // plate-4-applied's .env — real gaps 140 / 280 / 140ms, because the third
      // slot in the queue is deliberately empty — averaged 186.7ms and cleared
      // a 200ms ceiling it exceeded by 40%. A stagger is a wave; the thing a
      // reader notices is the widest gap in it, not its average.
      const gaps = d.slice(1).map((v, i) => v - d[i]);
      const lo = Math.min(...gaps), hi = Math.max(...gaps);
      if (lo < STAGGER_MIN)
        out.push(`.${k} has a ${Math.round(lo)}ms step across ${d.length} elements `
               + `(floor ${STAGGER_MIN}ms) — too tight to read as a sequence`);
      else if (hi > STAGGER_MAX)
        out.push(`.${k} has a ${Math.round(hi)}ms step across ${d.length} elements `
               + `(ceiling ${STAGGER_MAX}ms) — too slow to read as one gesture`);
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

    // 20 — THE GROUND MUST PAINT WHAT IT DECLARES.
    //
    //      Every ratio below is computed against the first <rect>'s fill. That
    //      makes the ground a DECLARATION, and until it is checked, a
    //      declaration is not a fact. The nine mobile plates carried
    //      `fill="#43372f" fill-opacity="0"` from the day they were written
    //      until 2026-08-08: the colour was right, the paint was missing, and
    //      the whole check below graded a phone's marks against paper the
    //      phone did not have. Nothing failed, because this line reads `fill`
    //      and `fill-opacity` is a different attribute — the same two-
    //      attributes-one-colour hole the loop below has its own note about.
    //
    //      It was survivable there only by luck: 19 of the 20 token/theme
    //      pairs measure HIGHER on GitHub's real canvas than on the paper, so
    //      the lie ran in the safe direction. The twentieth did not, and it
    //      was not even a magnitude error — night REDACT is lighter than
    //      #0d1117 and darker than #43372f, so a redaction rendered as a
    //      highlight. Luck is not a floor, and a ratio is unsigned, so
    //      neither this check nor any other could have caught the sign.
    //
    //      Three ways to make the ground a phantom, all three closed here:
    //      an alpha channel in the fill, a fill-opacity beside it, and an
    //      opacity on the rect or any ancestor of it.
    const slabEl = svgEl.querySelector('rect');
    if (!slabEl) out.push('no <rect> to take a contrast ground from — every ratio below would be meaningless');
    const slabStyle = slabEl ? getComputedStyle(slabEl) : null;
    if (slabStyle) {
      const fo = parseFloat(slabStyle.fillOpacity);
      const ao = opacityOf(slabEl);
      const chan = parse(slabStyle.fill);
      const alpha = (chan.length > 3 ? chan[3] : 1) * (Number.isFinite(fo) ? fo : 1) * ao;
      if (slabStyle.fill === 'none' || slabStyle.fill.startsWith('url') || !(alpha >= 1))
        out.push(`the ground rect declares ${slabStyle.fill} but paints it at alpha ${alpha.toFixed(3)} `
               + `(fill-opacity ${slabStyle.fillOpacity}, opacity ${ao}) — every contrast ratio on this `
               + `plate is measured against a colour the reader never sees`);
      // ...and it must be the SHEET, not merely the first thing that paints.
      // The line above grades the paint of whatever `querySelector` returns,
      // which is document order — the ordering plates.py's ground() docstring
      // calls load-bearing and which, until this line, nothing enforced. A
      // 30x10 rect emitted one position early is enough: it becomes the
      // contrast ground for the entire plate, and if its tone is near the
      // paper's, check 10 does not fire either. Demonstrated on a temp copy,
      // #4a3e35 ahead of #43372f — the gate passed while every ratio on the
      // plate was measured against the decoy. Same full-canvas bbox rule the
      // drawables filter uses to drop the slab, so the two agree by
      // construction.
      const sb = slabEl.getBBox();
      if (!(sb.width >= W - 2 && sb.height >= H - 2))
        out.push(`the first <rect> is ${Math.round(sb.width)}x${Math.round(sb.height)} on a ${W}x${H} `
               + `canvas — it is a mark, not the sheet, and every contrast ratio on this plate is `
               + `being measured against it`);
    }
    const SLABRGB = parse(slabStyle ? slabStyle.fill : 'rgb(0, 0, 0)');
    const ratio = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p); return (x + 0.05) / (y + 0.05); };

    for (const m of meta) {
      const st = getComputedStyle(m.el);
      // opacity is NOT inherited, so getComputedStyle(child).opacity reads 1
      // however dim the ancestor <g> is. This read parseFloat(st.opacity) and
      // therefore graded every grouped element at full strength: an audit
      // wrapped one 6.09:1 label in <g opacity="0.5">, dropping it to 2.32:1,
      // and the gate passed. Already live in the document — plate-1-glyph's
      // 220 .wrong glyphs sit inside a g at opacity .55 and were being graded
      // at 8.5:1 while rendering at 3.76:1. opacityOf() walks the ancestor
      // chain and has been sitting 377 lines up this file, used by four other
      // checks, since the day it was written.
      const alpha = opacityOf(m.el);
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
        // Three independent ways to make ink transparent in SVG, and this read
        // two of them. `opacity` (via opacityOf, ancestors included) and an
        // alpha channel inside rgba() were composited; `fill-opacity` and
        // `stroke-opacity` — sibling presentation attributes, the ones an
        // exported logo actually carries — were not read at all. A <text> at
        // fill-opacity="0.12" measured 1.4:1 and passed.
        //
        // Not hypothetical: build/logos.json bakes stroke-opacity into two of
        // the six product marks on the contact sheet, and this check graded
        // them at full strength while they rendered at 1.49:1 and 2.68:1 on
        // the light slab.
        const po = parseFloat(st[prop === 'fill' ? 'fillOpacity' : 'strokeOpacity']);
        const a = (rgb.length > 3 ? rgb[3] : 1) * alpha * (Number.isFinite(po) ? po : 1);
        if (a < 0.05) continue;
        const eff = over(rgb.slice(0, 3), SLABRGB, a);
        const r = ratio(eff, SLABRGB);
        // The 4.5:1 text floor was UNREACHABLE. `continue`-ing on r >= 3.0 before
        // computing `need` meant text between 3.0 and 4.5 was waved through, and
        // the 4.5 branch only ever ran where `r < 4.5` was already true. The
        // gate advertised AA on text and enforced the non-text floor. Compute
        // the floor first, then compare against it.
        const need = m.tag === 'text' ? 4.5 : 3.0;
        if (r >= need || Math.abs(r - 1) < 0.02) continue;          // 1:1 == it IS the slab
        if (r < need)
          out.push(`${m.nm} ${prop} is ${r.toFixed(2)}:1 on the slab (needs ${need}:1)`);
      }
    }

    return [...new Set(out)];
  }, { L, R, STEPS, TOL, isMobile: mobile });

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
      // Normalise TEXT width by the measured font metric, exactly as check 5
      // does. Chromium on Linux advances ~4% wider for this embedded woff2, so
      // a line that clears the column locally reports the document's right edge
      // 5u further out on CI — and check 12 was failing a plate that check 5
      // had already passed. Two checks measuring the same edge with different
      // rulers is worse than either ruler being wrong.
      const REF = 40 * (16 * 618 / 1000 + 1.6);   // = 459.52, see check 5
      const probe = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      // styled EXPLICITLY, not via class="lbl": the mobile plates never define
    // .lbl, so the probe there rendered at letter-spacing 0, the metric came
    // out 0.857, and every mobile column width was inflated ~17% — a latent
    // gate bug that surfaced the first time a mobile line was centered.
    probe.setAttribute('style', 'font-size:16px;letter-spacing:1.6px');
    probe.setAttribute('x', '0'); probe.setAttribute('y', '0');
      probe.textContent = 'M'.repeat(40);
      svg.appendChild(probe);
      const metric = probe.getBoundingClientRect().width / REF || 1;
      probe.remove();
      let top = 1e9, right = -1, bottom = -1;
      for (const e of els) {
        const c = e.getBoundingClientRect();
        if (!c.width && !c.height) continue;
        const w = e.tagName === 'text' ? c.width / metric : c.width;
        top = Math.min(top, c.y); right = Math.max(right, c.x + w);
        bottom = Math.max(bottom, c.y + c.height);
      }
      return { top, rightGap: W - right, bottomGap: H - bottom };
    });
    // 12 — EVERY EDGE IS A DECLARATION. RE-AUTHORED, round 20, in the same
    // change as the design it measures. This check used to assert first-ink /
    // right-edge / bottom-margin EQUALITY across the whole document — which
    // was the right instrument for round 18's finding (edges wandering by
    // accident) and the wrong doctrine once the client rejected the sameness:
    // a gate that fails any page whose sections differ is the frontispiece
    // armature, mechanised. What survives is the original virtue with the
    // uniformity removed: no edge may be an ACCIDENT. Each desktop plate now
    // declares its frame (data-frame="top,rightGap,bottomGap", viewBox
    // units), and the render must match the declaration within tolerance —
    // so a margin is still a decision with a machine behind it, it is just no
    // longer the same decision ten times. A plate with no declaration fails,
    // with the measured values printed so authoring is one round trip.
    // Tolerance 4: check 5's font-metric normalisation absorbs the Linux/mac
    // advance-width skew, but ascent rounding still moves first ink ~1-2u.
    const decl = (svg.match(/data-frame="([^"]+)"/) || [])[1];
    const measured = [g.top, g.rightGap, g.bottomGap].map(v => Math.round(v * 10) / 10);
    if (!decl) {
      fails.push(`${file}: declares no data-frame — measured top/right/bottom = ${measured.join('/')}`);
    } else {
      const want = decl.split(',').map(Number);
      const off = want.map((w, i) => Math.abs(w - measured[i]));
      if (want.length !== 3 || off.some(d => !(d <= 4)))
        fails.push(`${file}: data-frame says ${decl} but the render measures ${measured.join('/')} `
                 + `— the declared edge and the drawn edge disagree`);
    }
  }

  // 9 — every number the description claims must be drawn on the plate.
  //     (This only proves the two authored strings agree. It cannot prove
  //     either is TRUE — claims.json is what ties them to a repo.)
  // Tags strip to a SPACE, not to ''. claims.mjs:130-133 learned this the hard
  // way — collapsing `<text>n=10,000</text><text>299 wrong</text>` to nothing
  // between them makes "10000299" a single token — and this file went on
  // stripping to '' for another two rounds.
  const drawn = svg.replace(/<style[\s\S]*?<\/style>/g, ' ')
                   .replace(/<(?:title|desc)>[\s\S]*?<\/(?:title|desc)>/g, ' ')
                   .replace(/<[^>]*>/g, ' ').replace(/,/g, '');
  const meta = [...svg.matchAll(/<(?:title|desc)>([^<]*)<\/(?:title|desc)>/g)].map(m => m[1]).join(' ').replace(/,/g, '');
  // The desktop plate carries the whole argument, so its description must not
  // claim a number the plate does not draw. The mobile plate deliberately shows
  // a subset of the same shared description, so the check runs the other way:
  // every number it DOES draw must be one the description accounts for.
  const numsOf = s => [...new Set((s.match(/\d+\.\d+|\b\d+\b/g) || []))];
  // A SUBSTRING test, which is what this was, is vacuous for any number that is
  // a prefix of another on the same plate. claims.mjs documents this exactly
  // ("that is how 'IDOR: 7' could be falsified to 'IDOR: 79' and ship green")
  // and fixed it there; check 9 kept the bug, and check 9 is the only machine
  // comparing a plate's accessible description to the plate. Demonstrated: an
  // audit rewrote plate-1-glyph's desc to "29 wrong" and "97.0 percent",
  // touching no drawing, and the gate passed both. So claims.mjs's note that a
  // falsified alt is "caught twice upstream" was wrong — it was caught zero
  // times. Token match, on word boundaries, like the sweep next door.
  const has = (hay, n) =>
    new RegExp(`(?:^|[^\\d.])${n.replace(/\./g, '\\.')}(?![\\d.]*\\d)`).test(hay);
  if (mobile) {
    for (const n of numsOf(drawn))
      if (!has(meta, n))
        fails.push(`${file}: draws "${n}", which its description does not account for`);
  } else {
    for (const n of numsOf(meta))
      if (!has(drawn, n))
        fails.push(`${file}: description says "${n}" but the plate never draws it`);
  }

  console.log(`  measured ${file}`);
}

// (check 12 now runs per plate, inside the loop above — see its re-authoring
// note there. The cross-plate uniformity it used to assert was deliberately
// retired with the frontispiece: the document's coherence is carried by
// material, not by identical margins, and each plate's edges are asserted
// against its own declaration instead.)

// 16 — THE STILL FRAME MUST BE THE FINISHED FRAME.
//
// plates.py has claimed since round 6 that "the finished frame is authored;
// animation supplies the START". No plate did it. Every animated element was
// authored at its STARTING position and moved to its rest by a transform, so
// with motion off the document showed: four ISA tokens that never reached the
// collector (186u short), Applied's cascade with nothing fallen and nothing
// refused (246u), the RLS query 104u short of the wall it is named for, and
// AutoML's token 436u from its destination. Plate II drew four uncompressed
// bars OUTSIDE an empty "bounded in-flight window" — a diagram of memory that
// is not bounded.
//
// Check 11 could not see any of it: it measures the animated timeline, and
// every one of these plates is correct once it is allowed to move.
for (const { dir, tag, file: base } of sheet(/^plate-.*\.svg$/)) {
  const file = tag + base;
  await still.setContent(`<body style="margin:0">${readFileSync(join(dir, base), 'utf8')}</body>`);
  const bad = await still.evaluate(async () => {
    await document.fonts.ready;
    const svgEl = document.querySelector('svg');
    if (document.getAnimations().length) return ['reduced-motion did not stop the animations'];
    const out = [];
    for (const el of svgEl.querySelectorAll('[data-rest]')) {
      const want = el.getAttribute('data-rest');
      const within = parseFloat(el.getAttribute('data-rest-within') || '24');
      const t = svgEl.querySelector(`#${CSS.escape(want)}`);
      if (!t) { out.push(`declares data-rest="${want}", which is not on this plate`); continue; }
      const r = el.getBoundingClientRect(), T = t.getBoundingClientRect();
      const dx = Math.max(T.x - (r.x + r.width), r.x - (T.x + T.width), 0);
      const dy = Math.max(T.y - (r.y + r.height), r.y - (T.y + T.height), 0);
      const gap = Math.hypot(dx, dy);
      if (gap > within)
        out.push(`with motion off, <${el.tagName}.${(el.getAttribute('class') || '').split(/\s+/)[0]}> `
               + `sits ${Math.round(gap)}u from #${want} (allowed ${within}u) — the still frame is the START pose, not the finished one`);
    }
    return out;
  });
  for (const b of bad) fails.push(`${file}: ${b}`);
}

await browser.close();
if (fails.length) {
  console.log(`\nGATE FAILED — ${fails.length} defects:`);
  for (const f of fails) console.log(`  · ${f}`);
  process.exit(1);
}
console.log(`\nGATE PASSED — ${STEPS} samples across every loop: no collision, no overflow, frame zero complete.`);
