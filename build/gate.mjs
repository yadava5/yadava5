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
// screen-space bounds of the type column. The plates author at x=150..730 but
// the viewBox starts at 86, so the column lands 64..644 in rendered units.
const LEFT = 64, RIGHT = 644;
const M_LEFT = 30, M_RIGHT = 412;   // the 440-wide mobile canvas
const STEPS = 40;                   // samples across one loop
const TOL = 1.5;                    // antialiasing slack, in viewBox units
const fails = [];
const frame = [];   // desktop-only: first ink and right edge, for check 12 (carries its theme tag)

const browser = await chromium.launch();
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
    // A DESKTOP plate with no animations at all has dur === 0, and every motion
    // check below is guarded on `if (dur)` — so the worst possible case for
    // "does it move" was the one case nothing measured. Proven: stripping every
    // `animation:` from a plate passed gate.mjs clean, and motion.mjs globs
    // plate-* so it would have caught that one but never a mobile file.
    //
    // The mobile set is deliberately static: a 440 canvas carries the claim,
    // not the mechanism. So the exemption is named here rather than falling out
    // of an unguarded `if`, and it does not extend to the desktop plates.
    if (!dur && !isMobile)
      out.push(`has no animations at all — every motion check below is guarded on a loop existing, `
             + `so a static desktop plate passes them all by having nothing to measure`);
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

      // 17 — a total is not a distribution. A plate can clear the 35% floor and
      // still stand perfectly still for five consecutive seconds, which is what
      // a reader actually notices: measured, plate VII froze for 5.08s of a
      // 12.7s loop, plate II for 4.12s, plate 0 for 3.77s. Motion spread thinly
      // across the loop reads as alive; motion bunched at the start reads as a
      // still image that twitched once.
      let dead = 0, worst = 0;
      for (let i = 1; i < frames.length; i++) {
        const moved = frames[i].some((c, k) => {
          const q = frames[i - 1][k];
          return Math.abs(c.x - q.x) > 0.5 || Math.abs(c.y - q.y) > 0.5
              || Math.abs(c.w - q.w) > 0.5 || Math.abs(c.o - q.o) > 0.02
              || Math.abs(c.d - q.d) > 0.002;
        });
        dead = moved ? 0 : dead + 1;
        worst = Math.max(worst, dead);
      }
      const deadMs = worst * (dur / steps);
      // 2.4s, not the 1.2s the audit proposed. 1.2 on a 13.1s loop needs about
      // eleven events, and this document argues for calm rigour -- constant
      // motion would be the wrong register and would read as decoration. What
      // 2.4 forbids is a plate sitting dead for a QUARTER of its loop, which is
      // the actual complaint: plate VI was still for 3.60s and plate VII, whose
      // own label reads ANIMATED SVG, for 3.17s. Chosen deliberately, and I am
      // recording that I chose it rather than inheriting it.
      const CEILING_MS = 2400;
      if (deadMs > CEILING_MS)
        out.push(`stands completely still for ${(deadMs / 1000).toFixed(2)}s in a row `
               + `(ceiling ${(CEILING_MS/1000).toFixed(2)}s) — the loop has a hole in it, not a rhythm`);
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
    const SLABRGB = parse(getComputedStyle(svgEl.querySelector('rect')).fill);
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
      const REF = 448;
      const probe = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      probe.setAttribute('class', 'lbl'); probe.setAttribute('x', '0'); probe.setAttribute('y', '0');
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
    frame.push({ ...g, tag });
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

// 12 — THE DOCUMENT, not the plate.
//
// Everything above measures one plate at a time, and a multi-plate document
// lives in the relationship between them. Measured before this existed: first
// ink at 19, 23, 40 and 56; rightmost ink 150, 164, 164.8 and 166 short of the
// canvas — so the right edge visibly wandered as you scrolled and the top
// margin had three values. Neither gate could see it, because neither ever
// compared two plates.
// Run PER THEME. The light plates are geometrically identical to their dark
// twins, so pooling them would still pass — but a message interleaving twenty
// numbers from two sets would be unreadable the day it does fail, and "these
// two sets agree with each other" is not the property being asserted here.
const spread = (xs) => Math.max(...xs) - Math.min(...xs);
for (const { tag } of SETS) {
const themed = frame.filter(f => f.tag === tag);
if (!themed.length) continue;
const where = tag ? `the ${tag.replace('/', '')} plates` : 'the desktop plates';
const tops = themed.map(f => f.top), rights = themed.map(f => f.rightGap);
if (spread(tops) > 2)
  fails.push(`${where} start at ${tops.map(t => Math.round(t)).join('/')} — the first ink must sit on one line across the document`);
if (spread(rights) > 2)
  fails.push(`${where} end ${rights.map(r => Math.round(r)).join('/')} short of the canvas — the right edge wanders as you scroll`);
// three edges were enforced and the fourth wandered 12.8u
const bottoms = themed.map(f => f.bottomGap);
if (spread(bottoms) > 2)
  fails.push(`${where} leave ${bottoms.map(b => Math.round(b)).join('/')} below their last ink — the bottom edge is the one margin nothing was checking`);
}

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
