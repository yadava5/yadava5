/**
 * Does every check actually fire?
 *
 * This repository has shipped FOUR gates that could not fail: the char-count
 * gate, the duty cycle summed per class, the rest-position check that compared
 * against `undefined` and computed NaN, and check 10's 4.5:1 text branch, which
 * sat behind a `continue` that made it unreachable. Three of those passed
 * review. Two were written by me, in this session, and were caught only because
 * someone ran the negative test before trusting the green.
 *
 * So the negative test stops being something you remember to do. Each entry
 * below breaks the page in one specific way and names the check that must
 * notice. A check that stays silent under its own mutation is dead code wearing
 * a passing grade.
 *
 * THREE families, and each was added after noticing that a whole gate had no
 * probe pointed at it. The first mutates a plate and invokes gate.mjs. The
 * second copies the repository, falsifies claims.json or README.md, and invokes
 * claims.mjs — the gate that leaves the repository and re-derives every drawn
 * number from pinned commits, which had never once been watched to fail. The
 * third copies the repository, breaks one of the generator's inputs, and runs
 * the COPY's plates.py, whose build-time gate holds the charset coverage, the
 * XML check, the sweep, and the alt/desc agreement that is the page's entire
 * accessibility contract.
 *
 * The pattern is worth naming, because it has now repeated three times: the gap
 * is never in the check you are looking at, it is in the gate this file does
 * not mention. This file's own NAME is what made each of them look covered.
 *
 * Usage: node build/mutations.mjs
 */
import { execFileSync } from 'node:child_process';
import { readFileSync, writeFileSync, mkdtempSync, readdirSync, cpSync, rmSync, existsSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const ROOT = new URL('..', import.meta.url).pathname;
const ASSETS = join(ROOT, 'assets');

// ── FINDING A SUBJECT WITHOUT NAMING ONE
//
// Round 28 (BOARD) rebuilt every plate: new filenames, new compositions, new
// class names, new faces. Fifteen of the twenty probes below reported "??
// stale" against the result, and all fifteen for one reason — each named a
// literal that design work is free to change and duly did: class="lbl",
// class="say", class="kick", font-family:'S', x="150", a y-coordinate. That
// makes seventeen stale probes from this cause in this file's history, which
// is no longer a run of bad luck; it is the wrong way to write a probe.
//
// So the probes take their subject from the page's SHAPE. `topText` answers
// "which <text> elements are direct children of <svg>, and where are they" —
// direct children because checks 2 and 3 both exempt elements that share a <g>
// ("composed on purpose", gate.mjs:353), so a probe injected beside a grouped
// target is waved through and reports a false pass; and because a <g> may
// carry a transform, so a copy of a grouped element's authored x/y placed at
// the top level lands somewhere else entirely.
//
// A regex cannot answer "is this inside a <g>", so this walks the tags once
// and tracks depth. Not a parser: the plates are machine-written and plates.py
// asserts they are well-formed XML at build time, and giving the negative test
// an XML dependency the gate itself does not have would be its own liability.
const topText = (s) => {
  const out = [];
  let depth = 0;
  const re = /<(\/?)([\w-]+)((?:[^>"]|"[^"]*")*?)(\/?)>/g;
  let m;
  while ((m = re.exec(s))) {
    const [, close, name, attrs] = m;
    if (name === 'g') { depth += close ? -1 : 1; continue; }
    if (close || name !== 'text' || depth !== 0) continue;
    const end = s.indexOf('</text>', re.lastIndex);
    if (end < 0) continue;
    const x = /\bx="(-?[\d.]+)"/.exec(attrs), y = /\by="(-?[\d.]+)"/.exec(attrs);
    if (!x || !y) continue;
    out.push({ attrs, x: Number(x[1]), y: Number(y[1]), body: s.slice(re.lastIndex, end) });
  }
  return out;
};
// The one a coordinate-borrowing probe wants: long enough that an overlap is
// wider than the 1.5u antialiasing slack, and START-anchored, because an
// end-anchored run extends LEFT of its x and a rule drawn rightwards from
// there would miss it entirely — a probe that lands in empty space and proves
// nothing, which is the mistake the collision probe made in round 17.
const anchorText = (s) => topText(s).find(t =>
  !/text-anchor="(?:end|middle)"/.test(t.attrs)
  && t.body.replace(/<[^>]*>/g, '').trim().length >= 4);
// Authored canvas, read per file rather than assumed. The retired design was
// 794 wide with an 86u viewBox offset; this one is 900x534 and 440x… on the
// phone, and the next one will be something else again.
const canvasOf = (s) => {
  const m = /viewBox="[\d.-]+ [\d.-]+ ([\d.]+) ([\d.]+)"/.exec(s);
  return m ? { w: Number(m[1]), h: Number(m[2]) } : null;
};

// [name, check it must trip, how to break one plate]
const MUTATIONS = [
  // inject a second run of type at coordinates already occupied. Moving an
  // existing label was a bad probe: it landed in empty space and proved nothing
  // except that the probe was wrong.
  // Anchored on class="lbl" at y=56 until round 17, when that element became a
  // class="kick" and the probe silently stopped matching anything. A stale
  // probe reports "?? matched nothing" rather than a false pass, which is the
  // right failure mode — but a probe that only works until someone edits a
  // class is not much of a probe. This one keys on the SHAPE of any left-column
  // label and injects a second run of type at the same coordinates.
  // Round 27: the expectation was a bare /collides with/, and the redesign
  // proved why that is not a probe. plate-4-applied shipped a real collision,
  // so every temp copy printed "collides with" before this mutation touched
  // anything — and this line reported a pass while its injection was never
  // read. The injected run is the only thing on the page that says OVERLAP, so
  // the expectation names it. Either side of the pair may print first.
  // Round 28: x="150" was the retired design's type column and matches nothing
  // on the board. The injected run now COPIES the attribute list of the first
  // top-level text on the plate, so it lands at exactly that element's
  // position, in exactly its face and size, whatever those turn out to be —
  // there is no coordinate, class or size left here for a redesign to move.
  ['text collides with text', /"OVERLAP" collides with|collides with "OVERLAP"/,
    (s) => {
      const t = topText(s)[0];
      if (!t) return s;
      return s.replace('</svg>', `<text${t.attrs}>OVERLAP</text></svg>`);
    }],
  // Same treatment, one axis over: the same attribute list, pushed past the
  // plate's own right edge. The old form moved a literal x="150" y="56" that
  // no plate has had for two rounds. The expectation names the injected run
  // because check 4's message identifies a <text> by its content, and a bare
  // /leaves the canvas/ would be satisfied by any real overflow — a probe that
  // passes because the tree is already broken is the defect this file exists
  // to prevent.
  ['ink leaves the canvas', /"OFFCANVAS" leaves the canvas[^\n]*canvas \d+x\d+\)/,
    (s) => {
      const t = topText(s)[0], c = canvasOf(s);
      if (!t || !c) return s;
      return s.replace('</svg>',
        `<text${t.attrs.replace(/\bx="-?[\d.]+"/, `x="${c.w + 40}"`)}>OFFCANVAS</text></svg>`);
    }],
  // Glyph's first hand-drawn glyph carries its negative delay in an element
  // style; zeroing it puts the pen at 0% at t=0 — an undrawn stroke on the
  // authored frame, which check 6 must call out. Keys on the element style,
  // NOT the .ink class default: the same "-7.6s" appears there too, and
  // mutating the class is a no-op because every element overrides it.
  // Round 27: this probe went stale in a way re-anchoring cannot fix — the
  // redesign removed the hand-drawn strokes, and `pathLength` now appears in
  // ZERO of the 36 files. Check 6 has no subject left on the page. That does
  // not make the check worthless (it guards the next draw-on someone adds), but
  // a probe cannot borrow a subject that does not exist, so it SYNTHESISES one:
  // a single-value dasharray whose offset is still pulled fully back at t=0,
  // which is the exact condition check 6 reads. Injected before </svg> as a
  // top-level sibling, 1u stroke so it counts as a hairline and does not also
  // trip check 3 with noise. Keyed to nothing in the page, so no future edit
  // can silence it.
  ['a draw-on is blank at frame zero', /<path\.probe6 [^>]*> is undrawn at frame zero/,
    (s) => s.replace('</svg>',
      '<path class="probe6" d="M160 24 L 260 24" fill="none" stroke="#f6efe2" '
      + 'stroke-width="1" style="stroke-dasharray:100;stroke-dashoffset:100"/></svg>')],
  // Check 7 held a probe pointed at one keyframe percentage on one plate
  // (`0%,30%{opacity:1;`), and the rebuild deleted the plate. There is no
  // element on the board that hides for part of its loop — every gesture here
  // is a dash travelling along a bus — so, like the draw-on probe above, this
  // SYNTHESISES the subject rather than borrowing one that does not exist:
  // a rect that spends 84% of a one-second cycle at opacity 0. 1000ms is
  // deliberately shorter than any authored loop, so `dur` (gate.mjs:280, the
  // longest animation on the plate) does not move and the sampling phase of
  // every real element is left exactly where the gate found it.
  ['an element hides for most of its loop',
    /<rect\.probe7 [\d.,-]+> is visible only \d+% of the loop/,
    (s) => s.replace('</svg>',
      '<style>@keyframes probe7{0%,84%{opacity:0}85%,100%{opacity:1}}'
      + '.probe7{animation:probe7 1000ms linear infinite}</style>'
      + '<rect class="probe7" x="4" y="4" width="24" height="8" fill="#E4E9E9"/></svg>')],
  // Anchored on `class="lbl" style="fill:#F5A524"` until a round reclaimed that
  // amber for Glyph, then on the SHAPE of any classed element setting its fill
  // through `style` — and BOARD emits no element style at all, so that shape
  // matched nothing either. Both versions were looking for a defect already
  // present; what the check actually needs is an attribute a rule can beat.
  // So the mutation reads the plate's OWN stylesheet, takes the first class
  // rule that sets a fill, finds an element carrying that class and no fill
  // attribute, and gives it one. Whatever the classes are called, a plate that
  // styles fill by class has a subject for this check.
  ['a fill attribute is overridden by its class',
    /asks for fill="#FF00FF" and renders rgb\([\d, ]+\) — a CSS rule is overriding the attribute/,
    (s) => {
      const css = [...s.matchAll(/<style>([\s\S]*?)<\/style>/g)].map(m => m[1]).join('\n');
      for (const [, cls] of css.matchAll(/\.([\w-]+)\{[^}]*\bfill:#[0-9A-Fa-f]{6}/g)) {
        const held = new RegExp(`class="[^"]*\\b${cls}\\b[^"]*"`);
        for (const m of s.matchAll(/<(text|rect|circle|path)\s((?:[^>"]|"[^"]*")*?)>/g)) {
          if (!held.test(m[2]) || /\bfill="/.test(m[2])) continue;
          return s.replace(m[0], `<${m[1]} fill="#FF00FF" ${m[2]}>`);
        }
      }
      return s;
    }],
  // Re-anchored 2026-08-08 with the paper palette: this keyed on the literal
  // dark INK2 #8A8F98, which the Daylight Study replaced with #D9D0C3. The
  // probe went stale in the same commit that changed the colour — which is
  // the design, but a probe pinned to ONE hex rots on every palette move. So
  // it now keys on the .fine rule's SHAPE and rewrites whatever fill it finds
  // to #8a8175 — a warm mid tone that fails the 4.5:1 text floor against
  // BOTH papers (3.00:1 on night #43372f, 3.05:1 on day #f2e4c9, measured).
  // The loop only ever reads the dark set, so failing night alone would be
  // enough today; failing both means the probe still fires the day someone
  // points it at assets/light, which is the cheaper thing to be right about.
  // The rule's geometry — 13px / 0.4px — stays pinned: that is authored
  // typography, not palette, and it should rot loudly if a redesign moves it.
  // Round 28: `.fine` went with the paper design, and pinning a rule's authored
  // geometry — the thing the note above defended — turned out to buy nothing
  // except a probe that dies on schedule. The check has nothing to do with any
  // particular rule: it grades the ink a plate actually paints against the
  // ground it declares. So the mutation adds ink of its own, at the position
  // of the plate's first top-level run so it is certainly on the SHEET rather
  // than inside one of the product tiles (which have their own local ground —
  // see the mark probe further down, which is the other half of this pair).
  // #3a4048 is a near-black that fails 4.5:1 against the dark canvas by a wide
  // margin, and the expectation names both the injected run and the ground it
  // must be graded against.
  ['text drops below 4.5:1 on the slab',
    /"FAINT" fill is \d\.\d+:1 on the slab \(needs 4\.5:1\)/,
    (s) => {
      const t = anchorText(s);
      if (!t) return s;
      return s.replace('</svg>',
        `<text x="${t.x}" y="${t.y}" font-size="13" style="fill:#3a4048">FAINT</text></svg>`);
    }],
  // Keys on Applied's refused message, which declares data-rest="the-human":
  // pulling its authored x back 100u strands it short of the person it must
  // reach, in both the animated and the still frame.
  //
  // Re-anchored twice, then a third time, each because a redesign moved the
  // message by a couple of units and the literal x stopped matching. A probe
  // that matches nothing is worse than no probe: it reports a check as
  // exercised when the check was never run. The pass-3 note said that if it
  // happened again the probe should key on the attribute alone and compute
  // the shift — it happened again (round 22 resized the token 14u -> 18u,
  // moving 632 -> 630), so this now does exactly that: any element that
  // declares a rest is dragged 100u left of wherever it was authored.
  // Round 28: the board draws no token that travels to a destination, so
  // `data-rest` appears on nothing and no element carries an `id` for one to
  // point at. Both ends are synthesised, at the plate's own scale: a target
  // near the right edge and a marker that stops on the far left and stays
  // there. That is enough to ask both halves of the claim — check 11 reads the
  // longest still run in the animated timeline, check 16 reads the authored
  // frame with motion off — and a static pair fails both, which is why the
  // expectation accepts either sentence. If a plate ever declares a real rest
  // again, this probe keeps working beside it and stops being the only subject.
  ['a token rests short of its target',
    /<rect\.probe11 [\d.,-]+> should come to rest at #probe11target but stops \d+u away|with motion off, <rect\.probe11> sits \d+u from #probe11target/,
    (s) => {
      const c = canvasOf(s);
      if (!c) return s;
      const y = Math.round(c.h / 2);
      return s.replace('</svg>',
        `<rect id="probe11target" x="${c.w - 80}" y="${y}" width="20" height="20" fill="#E4E9E9"/>`
        + `<rect class="probe11" data-rest="probe11target" data-rest-within="12" `
        + `x="40" y="${y}" width="20" height="20" fill="#E4E9E9"/></svg>`);
    }],
  // Both of the following were dead until an audit ran them by hand. They are
  // probes now so that cannot happen twice.
  //
  // Check 10 read the element's OWN opacity, which is never inherited, so
  // anything inside a dimmed <g> was graded at full strength. Wrapping one
  // 6.09:1 label in <g opacity="0.5"> takes it to 2.32:1 and the gate passed.
  // (Keys on jetpack's first benchmark-table row — the old "row lbl" class
  // token went with the table's decorative ripple.)
  // (Round 20 re-anchor: jetpack's bench sub-header — the old benchmark-table
  // row went with the table when the lanes became bars.)
  // (Round 27: the y="82" literal died with the plate that carried it. Round
  // 28: so did class="lbl" and x="150", and the whole selector matched nothing
  // — which is the third form of the same mistake on one line.)
  //
  // The ink is injected at FULL strength — #E4E9E9 is roughly 13:1 on the dark
  // canvas — inside a <g opacity="0.35">. Nothing about the element itself is
  // wrong; only the ancestor makes it illegible, so the check can only catch it
  // by walking the chain, which is precisely the hole that was live here.
  ['contrast is destroyed by an ancestor group opacity',
    /"DIMMED" fill is \d\.\d+:1 on the slab \(needs 4\.5:1\)/,
    (s) => {
      const t = anchorText(s);
      if (!t) return s;
      return s.replace('</svg>',
        `<g opacity="0.35"><text x="${t.x}" y="${t.y}" font-size="13" `
        + `style="fill:#E4E9E9">DIMMED</text></g></svg>`);
    }],
  // Check 9 compared the accessible description to the plate with
  // String.includes, so any number that is a PREFIX of one the plate draws
  // passed: "29" is a substring of "299". The desc is the only thing a screen
  // reader gets, and it was the least guarded string in the repo.
  // (Round 27: keyed on the sentence "which means 299 wrong", which the rewrite
  // rephrased. The DEFECT is the shape — a desc number truncated to a prefix of
  // one the plate draws — so the mutation now takes the first three-digit number
  // in the description and drops its last digit, whatever that number happens
  // to be. There is nothing left here for a copy edit to break.)
  ['a description number is falsified to a prefix', /description says/,
    // [\s\S]*? did not stop at </desc>: on a plate whose description holds no
    // three-digit number the lazy match ran on into <style> and truncated
    // font-weight:400 to 40. The gate caught THAT — as a missing-face defect —
    // so the probe reported "not caught" while the corruption was in fact
    // noticed, for a reason that had nothing to do with check 9. [^<]*? keeps
    // the match inside the text node, so a plate without one simply declines.
    (s) => s.replace(/(<desc>[^<]*?)\b(\d\d)\d\b/, '$1$2')],
  // Three ways to make ink transparent in SVG and check 10 read only two.
  // fill-opacity and stroke-opacity are sibling presentation attributes, not
  // `opacity` and not an rgba alpha, and they are exactly what an exported
  // logo carries — two of the six product marks shipped at 1.49:1 and 2.68:1
  // because of it.
  // (Round 20 re-anchor: the refusal's SIX SERVICES say-line. Round 27: the
  // first left-column .say in the sorted set. Round 28: no plate has a .say and
  // no plate has an x="150". Same injected-ink treatment as its two siblings
  // above, and the same reason it is a separate probe from them: fill-opacity
  // is a sibling PRESENTATION ATTRIBUTE, neither `opacity` nor an rgba alpha,
  // and reading the other two is what let two product marks ship at 1.49:1.)
  ['contrast is destroyed by fill-opacity',
    /"SHEER" fill is \d\.\d+:1 on the slab \(needs 4\.5:1\)/,
    (s) => {
      const t = anchorText(s);
      if (!t) return s;
      return s.replace('</svg>',
        `<text x="${t.x}" y="${t.y}" font-size="13" style="fill:#E4E9E9" `
        + `fill-opacity="0.12">SHEER</text></svg>`);
    }],
  // Check 21 (data-canvas) got its probe in round 27, in the same change as the
  // check — and the probe could not produce the violation. It painted a rect
  // 708 units wide, which was the paper design's sheet inside an 86u viewBox
  // offset; BOARD's canvas is 900x534, and check 21 fires only when the first
  // <rect> covers the whole of it (gate.mjs:729). So the condition was
  // unsatisfiable, the probe reported `!!` — "the gate said nothing" — and
  // check 21 has in fact never once been watched to fail, in the round that
  // was written to make sure it could be. A probe built against a retired
  // geometry is not a weaker probe than one built against a literal; it is the
  // same probe.
  //
  // The sheet is now cut from the plate's OWN viewBox, and injected ahead of
  // <title> so it is what querySelector('rect') returns. Two things make it
  // clean rather than noisy: the drawables filter (gate.mjs:239) drops any
  // element with a full-canvas bbox, so it adds no collision or edge findings;
  // and SLABRGB comes from the declared canvas, not from this rect, so no
  // contrast ratio on the plate moves either. The only thing it changes is the
  // one thing check 21 asserts.
  ['a transparent frontispiece paints a sheet anyway',
    /declares data-canvas="#[0-9A-Fa-f]{6}" and also paints a full-canvas sheet — it cannot be both paper and transparency/,
    (s) => {
      const c = canvasOf(s);
      if (!c || !/\bdata-canvas="/.test(s)) return s;
      return s.replace(/(<title>)/,
        `<rect x="0" y="0" width="${c.w}" height="${c.h}" fill="#43372f"/>$1`);
    }],
  // Check 20 was RE-AIMED in the same change as this probe, and this probe is
  // what connects the two. The ground on this page is a DECLARATION —
  // data-canvas, the worst canvas GitHub serves that theme on — not a painted
  // sheet, so the check's two ground-rect assertions had no subject left: both
  // were guarded on `!declaredCanvas` and all 48 published plates declare one,
  // which made them dead code wearing a passing grade. They are deleted; what
  // the check asserts now is that a plate MUST declare a canvas.
  //
  // That is not something check 21 was ever doing. 21 fires only when a canvas
  // IS declared and a full-canvas sheet is painted as well, so a plate
  // declaring nothing at all fell through both checks and had every ratio on it
  // graded against whatever the fallback happened to be. Strip the attribute
  // and the gate must say so.
  //
  // Keyed on the attribute, which head() writes for every plate in the set,
  // rather than on any one plate's art. The mutation runs against the DARK set,
  // where the fallback ground is black and every ink on the canvas therefore
  // measures HIGHER rather than lower — so the only finding it can produce is
  // the one it names, which was confirmed by reading the whole mutated gate
  // output and not just the regex verdict.
  ['a plate stops declaring the canvas it is graded against',
    /declares no data-canvas — every contrast ratio below would be graded against a ground/,
    (s) => s.replace(/ data-canvas="[^"]*"/, '')],
  // Check 13 fires when a plate declares animations NONE of which moves
  // anything — dead code on the reader's compositor wearing the name of a
  // gesture. Round 21 anchored this on the title page's two carriers; round
  // 22 gave the title page the index-read chase, so freezing those two no
  // longer silences it and the probe moved to the colophon — the plate with
  // the fewest declared animations — freezing all three (the turning device,
  // the counter-rotation that keeps its marks upright, the drifting halo).
  // Round 28: naming three keyframe bodies was the same mistake made three
  // times over — the turning device, its counter-rotation and the drifting halo
  // all went with the colophon's redraw, and the probe froze nothing.
  //
  // The check fires only when NO element moves at any sample, so a probe cannot
  // freeze one gesture; it has to neutralise every keyframe on the plate and
  // leave the ANIMATIONS THEMSELVES declared, because gate.mjs:602 guards the
  // whole check on `dur` and a plate with no animations at all is a different
  // (and legal) thing. Every keyframe body becomes `to{stroke-opacity:1}`:
  // still a real animation with a real duration, on the one animatable
  // property the alive test (gate.mjs:605-610, which reads x/y/w/h, composited
  // opacity and stroke-dashoffset) does not look at. Keyed to the @keyframes
  // syntax rather than to any gesture, so a redesign can invent whatever
  // motion it likes and this still empties it.
  ['a declared animation never moves anything', /declares animations that never move anything/,
    (s) => s.replace(/^@keyframes ([\w-]+)\{.*$/gm, '@keyframes $1{to{stroke-opacity:1}}')],
  // Check 14 is the surviving motion-quality check (a stagger is a wave, not a
  // queue), so it keeps a probe. Its history is a list of subjects that walked
  // away: Glyph's pen stagger went with the pen in round 27, the refusal's
  // redaction rows went with the refusal in round 28.
  //
  // Round 28 found something worse than a stale probe, and the finding was
  // about the CHECK. It grouped delays by animation NAME, and BOARD gives every
  // animated element its OWN generated name (k115, k116, k117 …) because dash
  // animation is absolute and a shared keyframe would erase the per-segment
  // offsets. So every group had exactly one member, every group was skipped at
  // `delays.size < 2`, and the check had jurisdiction over nothing at all while
  // printing nothing at all.
  //
  // Fixed where the fault was. Check 14 now groups by the connected component
  // over keyframe name AND class token, which is the only identity that
  // survives both ways a gesture has been split here — one selector over two
  // class names (the colophon's `.ln,.ln2`), and one class over many generated
  // names (this page's `pu`). The hero's three one-shots are a wave again:
  // class `pu`, delays 400 / 530 / 680, gaps 130 and 150 inside the 40-200ms
  // band. Measured, not assumed.
  //
  // So this probe stops bringing its own subject. It brought one for exactly
  // one round — three injected rects on one keyframe name — and a synthetic
  // subject is the wrong instrument for this check: it passes whether or not
  // the check can reach anything the page actually draws, which is the state it
  // was written to expose. It mutates the real wave now, and the day a redesign
  // leaves the page with no stagger at all it reports `??` stale, which is the
  // finding rather than the failure.
  //
  // It PULLS the widest delay down to (smallest + 5ms) rather than pushing it
  // out. Both directions fire the check — this one on the 40ms floor branch,
  // widening on the 200ms ceiling — but widening a one-shot's delay shortens
  // the window it is visible in and would trip check 7 as a side effect, and a
  // mutation that causes two unrelated findings is harder to read than one that
  // causes exactly the finding it names. Every delay only ever decreases here,
  // which moves visibility in the safe direction.
  //
  // Keyed on the SHAPE of the message and on the mutation's own 5ms, never on
  // `pu` — a class name is a literal design work is free to change, and naming
  // one is how seventeen probes in this file went stale.
  ['a stagger step is too tight to read as a sequence',
    /has a 5ms step across \d+ elements \(floor 40ms\) — too tight to read as a sequence/,
    (s) => {
      // The delay is the SECOND time in the `animation` shorthand. A comet
      // declares a duration and no delay — its phase lives in the dasharray —
      // so the comets are skipped here by construction, exactly as check 14
      // skips them for having one distinct delay between them.
      const d = [...s.matchAll(/animation:[\w-]+ [\d.]+m?s [^;}"]*/g)].map(m => {
        const t = [...m[0].matchAll(/([\d.]+)ms\b/g)];
        return t.length >= 2
          ? { at: m.index + t[1].index, len: t[1][0].length, delay: Number(t[1][1]) } : null;
      }).filter(Boolean);
      if (d.length < 2) return s;
      const lo = Math.min(...d.map(x => x.delay));
      const hi = d.reduce((a, b) => (b.delay > a.delay ? b : a));
      if (hi.delay <= lo + 5) return s;
      return s.slice(0, hi.at) + `${lo + 5}ms` + s.slice(hi.at + hi.len);
    }],
  // Check 3 exempted every hairline from crossing type — "rules pass under
  // type" — so a rule that TRAVELLED across a word passed 40 samples a loop
  // while rendering it struck out. Two plates were shipping exactly that. The
  // exemption is now narrowed to hairlines that hold still, and this is the
  // probe that the narrowing is connected to anything.
  //
  // Injected at the end of the document rather than beside the text it
  // crosses, deliberately: elements sharing a <g> are "composed on purpose"
  // and skipped, so a probe nested next to its target would be waved through
  // and report a false pass — the exact shape of the three stale probes above.
  // The expectation is keyed to the INJECTED element's own name, not to the
  // bare phrase. While a real plate is failing this check, a probe matching
  // /sweeps across/ would be satisfied by the pre-existing failure and report
  // "caught" without the mutation contributing anything — a probe that passes
  // because the tree is already broken is the precise defect this file exists
  // to prevent, and it would have been one more entry in its own history.
  // The font-load assertion covered family 'M' and nothing else, so the serif —
  // every hero numeral on the paper design — could have fallen back to a
  // platform face and been measured there. The fix in gate.mjs was to derive
  // the faces from the document so a swap could not outrun it, and the swap
  // duly came: BOARD is Syne 800 ('D') and Commissioner 400/600 ('T'), and
  // there is no 'S' and no 'M' anywhere. These two probes named the family and
  // the weight, so both went stale in the change that proved the gate right.
  //
  // Neither names a face now. The payload of every declared face is corrupted,
  // which guarantees the probe hits whichever ones the plate actually renders
  // — the message the expectation reads is emitted only for a face that IS
  // rendered (gate.mjs:178), so a plate carrying an unused face cannot satisfy
  // it by accident.
  ['an embedded webfont fails to load',
    /the embedded '\w+' \d+ webfont did not load — every measurement that uses it is the fallback font/,
    (s) => s.replace(/(font-family:'[^']+';font-weight:\d+;src:url\(data:font\/woff2;base64,)([A-Za-z0-9+/=]{240})/g,
      (m, head) => head + 'A'.repeat(240))],
  // The other direction, and the half that makes DROPPING a face safe: plates
  // stop embedding a face nothing renders (~7.5 KB apiece), which is only safe
  // while a plate that DOES render one cannot quietly lose it. Strips the first
  // declared face and expects the fallback to be named — the expectation is
  // keyed to the reverse message (rendered-minus-declared, gate.mjs:192) so it
  // cannot be satisfied by the declared-but-unused warning next to it.
  ['a rendered face is not embedded',
    /renders '\w+' at weight \d+, which no @font-face on this plate embeds/,
    (s) => s.replace(/@font-face\{font-family:'[^']+';font-weight:\d+;src:url\(data:font\/woff2;base64,[A-Za-z0-9+/=]+\) format\('woff2'\)\}\n?/, '')],
  // (Round 28: the class alternation `kick|lbl|fine|key` and the x="150" both
  // stopped matching. The rule is laid over whatever the plate's first
  // start-anchored run turns out to be, at that run's own coordinates.)
  ['a moving rule is drawn through type', /<rect\.mutsweep [\d.,-]+> sweeps across/,
    (s) => {
      const t = anchorText(s);
      if (!t) return s;
      return s.replace('</svg>',
        '<style>@keyframes mutsweep{from{transform:translateY(-30px)}'
        + 'to{transform:translateY(30px)}}</style>'
        + `<rect class="mutsweep" x="${t.x}" y="${t.y - 8}" width="120" height="2" `
        + 'fill="#ffffff" style="animation:mutsweep 1000ms linear infinite"/></svg>');
    }],
  // The OTHER half of check 3, which had no probe at all until 2026-08-11.
  // The rule above exercises the hairline branch — a thin thing travelling
  // across type. A solid graphic simply lying on type takes a different branch
  // (`sits on top of`), and that is the branch a mark like plate-1's index
  // triangle would trip, so the round that added the triangle was leaning on an
  // unfalsified check to say the triangle was fine. Found by asking what the
  // check would have caught rather than by reading that it passed.
  //
  // Appended before </svg> so the rect is a top-level sibling: check 3 exempts
  // pairs inside the same group, and injecting next to the text would have put
  // the probe inside whatever <g> holds it and proved nothing. 80x16 because a
  // rect is a HAIRLINE to this gate at 3u or under on either side, and a FRAME
  // if its fill is none — a probe that is either is a probe of a different
  // branch.
  // (Round 28: same class alternation, same death. It also carries a class now,
  // so the expectation names the injected rect instead of matching any bare
  // <rect> — while a real graphic is sitting on real type, the old form would
  // have reported "caught" with the mutation contributing nothing.)
  ['a solid graphic is laid over type', /<rect\.mutover [\d.,-]+> sits on top of/,
    (s) => {
      const t = anchorText(s);
      if (!t) return s;
      return s.replace('</svg>',
        `<rect class="mutover" x="${t.x + 2}" y="${t.y - 12}" width="80" height="16" `
        + 'fill="#8a8a8a"/></svg>');
    }],
  // ── The mobile canvas, for the first time.
  //
  // Check 12 was guarded `if (!mobile)` from round 11 (89c69e4) to round 21 —
  // ten rounds, not the three an earlier draft of this comment claimed — so 18
  // of the 36 published files had no edge assertion at all.
  // These two probes exist because a new coverage nobody has watched fail is
  // the very defect that guard turned out to be — and this file's own history
  // is four gates that were trusted before they were falsified.
  //
  // Both expectations are keyed to an `m-` filename ON PURPOSE. Every other
  // probe here mutates a desktop plate, so an expectation matching the bare
  // phrase would be satisfied by a desktop plate that is already failing check
  // 12 and would report "caught" without the mutation contributing anything —
  // the stale-probe shape documented above, which this file has shipped three
  // times.
  // Check 10's local-ground retune (BOARD, 2026-08-12): ink wholly inside an
  // opaque rect is graded against that rect, not the canvas. This is the
  // probe that ships with it: dim the glyph mark's structure rules to a grey
  // that is LEGIBLE on the canvas of both themes but near-invisible on the
  // #0A0A0B tile they actually sit on (#26262B is 1.34:1 there). The old
  // canvas-graded check cannot see this defect; only the retuned one can, so
  // a pass here proves the local ground is really being consulted. Keyed to
  // the hero by name — every plate with a mark would do, but an expectation
  // that floats across files is the stale-probe shape this file documents.
  ['mark ink goes dim against its own tile', /is 1\.\d+:1 on its local ground/,
    (s) => s.replace(/stroke="#6B6B76" stroke-width="1.4"/,
      'stroke="#26262B" stroke-width="1.4"'), /^plate-0-hero\.svg$/],
  ['a mobile plate stops declaring its frame', /\bm-[\w-]+\.svg: declares no data-frame/,
    (s) => s.replace(/ data-frame="[^"]*"/, ''), /^m-.*\.svg$/],
  // The other direction: a declaration that survives but stops being true.
  // +40 rather than +5 because tolerance is 4 and the point is to prove the
  // comparison happens at all, not to probe where its edge sits.
  ['a mobile frame declares an edge it does not draw',
    /\bm-[\w-]+\.svg: data-frame says [^\n]*the declared edge and the drawn edge disagree/,
    (s) => s.replace(/(data-frame="[\d.]+,[\d.]+,)([\d.]+)"/,
      (_m, head, bottom) => `${head}${Number(bottom) + 40}"`), /^m-.*\.svg$/],
];

const gate = (dir) => {
  try {
    execFileSync('node', [join(ROOT, 'build', 'gate.mjs')],
      { env: { ...process.env, GATE_ASSETS: dir }, encoding: 'utf8', stdio: 'pipe' });
    return '';
  } catch (e) { return (e.stdout || '') + (e.stderr || ''); }
};

console.log('baseline:', gate(ASSETS) ? 'FAILS (fix the plates first)' : 'passes');
// TWO counters, because these are two different findings and summing them hid
// the one that matters. `??` means the mutation never landed — the check behind
// it was never asked the question, so the probe proves nothing in either
// direction. `!!` means the page WAS broken, the gate read it, and the gate
// said nothing: a hole. One combined "N mutation(s) went unnoticed" read as N
// dead checks when most of N was stale probes, in the one file whose whole
// purpose is telling those two states apart.
let stale = 0, asleep = 0;
for (const [name, expect, breakIt, only] of MUTATIONS) {
  const dir = mkdtempSync(join(tmpdir(), 'mut-'));
  cpSync(ASSETS, dir, { recursive: true });
  let touched = false;
  // Scope defaults to the desktop set: every probe above this line was written
  // against a desktop plate, so widening the default would silently re-point
  // them. A probe that needs the mobile canvas asks for it by name. Sorted
  // because readdirSync order is not stable across platforms and "the first
  // file the mutation matches" is otherwise a different file on CI than here —
  // which would make a probe's target, and so its failure text, unreproducible.
  for (const f of readdirSync(dir).sort().filter(x => (only || /^plate-.*\.svg$/).test(x))) {
    const before = readFileSync(join(dir, f), 'utf8');
    const after = breakIt(before);
    if (after !== before) { writeFileSync(join(dir, f), after); touched = true; break; }
  }
  if (!touched) {
    console.log(`  ?? ${name} — mutation matched nothing; the probe is stale`);
    stale++; rmSync(dir, { recursive: true, force: true }); continue;
  }
  const out = gate(dir);
  // Each probe copies assets/ into a fresh tmpdir and nothing ever removed
  // them: 13 per run, and an audit found 1,010 orphaned `mut-*` directories
  // holding 326 MB. Harmless to correctness, but this file now runs on every
  // `npm test` rather than only in CI, so the leak rate went up by the
  // frequency of the suite. Cleaned in a finally-ish position: after the gate
  // has read the directory, before the next iteration allocates another.
  rmSync(dir, { recursive: true, force: true });
  const caught = expect.test(out);
  console.log(`  ${caught ? '..' : '!!'} ${name}${caught ? '' : '  — NOT CAUGHT'}`);
  if (!caught) asleep++;
}
// ── Still gate.mjs, but breaking the SET rather than a file in it.
//
// Family 1 mutates the text of one plate, so there is no way to say "the light
// twins are not there" in its vocabulary — and that turned out to be the guard
// worth saying it about. gate.mjs pushed the light set only `if (existsSync)`,
// three lines under a comment asserting those files "are measured by every
// check here", so an absent directory left the gate measuring the dark half and
// printing GATE PASSED. Same runner, a mutator that takes the copied directory.
// Each mutator returns whether it CHANGED anything, exactly as the file-level
// family above does. It did not: both returned a hardcoded `true`, and the
// second one named a plate the redesign retired, so `rmSync` threw ENOENT out
// of the whole process — the run died after 21 of 36 probes and two of the
// three baselines never printed. A probe that cannot report itself stale is
// the check-that-cannot-fail shape this file exists to find, sitting inside
// this file. Absence is a finding here, the same as everywhere else.
const SET_MUTATIONS = [
  ['the light twin of every plate is missing', /does not exist\. It holds the light twin/,
    (dir) => {
      const p = join(dir, 'light');
      if (!existsSync(p)) return false;
      rmSync(p, { recursive: true, force: true });
      return true;
    }],
  // and the partial case, which the existsSync form could never have seen even
  // when the directory was present: one theme holding one fewer plate than the
  // other means a <picture> whose light <source> resolves to nothing.
  //
  // Named plate-1-glyph.svg until the redraw renumbered the set, and then it
  // deleted nothing and reported "?? stale". It takes whichever plate sorts
  // first in the light directory now — the assertion is that ANY hole in the
  // twinning is refused, and naming one file was never part of it. The
  // expectation still pins the COUNT, because "1 plate(s)" is what makes it a
  // hole rather than the missing-directory case the probe above covers.
  ['one plate loses its light twin', /1 plate\(s\) have no light twin: plate-[\w-]+\.svg\./,
    (dir) => {
      const light = join(dir, 'light');
      if (!existsSync(light)) return false;
      const victim = readdirSync(light).sort().find(f => /^plate-.*\.svg$/.test(f));
      if (!victim) return false;
      rmSync(join(light, victim));
      return true;
    }],
];
for (const [name, expect, breakIt] of SET_MUTATIONS) {
  const dir = mkdtempSync(join(tmpdir(), 'mut-'));
  cpSync(ASSETS, dir, { recursive: true });
  const touched = breakIt(dir);
  if (!touched) {
    console.log(`  ?? ${name} — mutation matched nothing; the probe is stale`);
    stale++; rmSync(dir, { recursive: true, force: true }); continue;
  }
  const out = gate(dir);
  rmSync(dir, { recursive: true, force: true });
  const caught = expect.test(out);
  console.log(`  ${caught ? '..' : '!!'} ${name}${caught ? '' : '  — NOT CAUGHT'}`);
  if (!caught) asleep++;
}

// ── The second family: can claims.mjs fail?
//
// Everything above mutates a PLATE and invokes gate.mjs. That was the WHOLE
// negative test, which means claims.mjs — the gate that leaves the repository
// and re-derives every drawn number from pinned commits — had no probe at all,
// and the colophon's "fails if a check sleeps through it" was a sentence about
// one of two gates. A gate nobody has ever watched fail is this repo's signature
// defect; it has shipped four of them, and the fix has never been to trust the
// newest one harder.
//
// These copy build/, assets/ and README.md into a tmpdir and run the COPY, so
// claims.mjs's ROOT resolves to the temporary tree and claims.json or README.md
// can be falsified without touching the working tree. --offline reads the warm
// build/.claims-cache (copied along), so the negative test costs no network —
// and in CI the cache is warm because gate.yml runs claims.mjs immediately
// before this file. CI is unset in the child so `live()` reads the value the
// real run just cached rather than re-fetching a third party four more times.
const claimsGate = (root) => {
  try {
    execFileSync('node', [join(root, 'build', 'claims.mjs'), '--offline'], {
      env: { ...process.env, CI: '', CLAIMS_SKIP_FRESHNESS: '1' },
      encoding: 'utf8', stdio: 'pipe',
    });
    return '';
  } catch (e) { return (e.stdout || '') + (e.stderr || ''); }
};
const editJson = (root, fn) => {
  const p = join(root, 'build', 'claims.json');
  const s = JSON.parse(readFileSync(p, 'utf8'));
  if (fn(s) === false) return false;
  writeFileSync(p, JSON.stringify(s, null, 2));
  return true;
};
const editReadme = (root, fn) => {
  const p = join(root, 'README.md');
  const before = readFileSync(p, 'utf8');
  const after = fn(before);
  if (after === before) return false;
  writeFileSync(p, after);
  return true;
};

// claims.mjs answers "does this file draw this value?" with drawsToken()
// (claims.mjs:310-317): a digit match on token boundaries, OR the number
// SPELLED — "IDOR IN SIX SERVICES" satisfies a value of 6. A probe that picks
// its victim row with String.includes can therefore select a row the gate goes
// on to find anyway, and then report the check asleep for a reason that has
// nothing to do with the check. So the predicate is mirrored here, and a
// mutator that cannot find a qualifying row DECLINES — "?? stale" is an honest
// answer and a green line from a mutation that could never fire is not.
const WORDOF = { 3: 'three', 4: 'four', 5: 'five', 6: 'six', 7: 'seven',
  8: 'eight', 9: 'nine', 10: 'ten', 11: 'eleven', 12: 'twelve', 13: 'thirteen',
  14: 'fourteen', 15: 'fifteen', 16: 'sixteen', 17: 'seventeen', 18: 'eighteen',
  19: 'nineteen', 20: 'twenty', 30: 'thirty', 40: 'forty', 50: 'fifty',
  60: 'sixty', 70: 'seventy', 80: 'eighty', 90: 'ninety', 100: 'hundred',
  1000: 'thousand' };
// The same strip claims.mjs:282-287 performs, for the same reason: tags become
// a SPACE so two adjacent <text> runs cannot fuse into a number nobody drew.
const plateText = (p) => readFileSync(p, 'utf8')
  .replace(/<style[\s\S]*?<\/style>/g, ' ')
  .replace(/<(?:title|desc)>[\s\S]*?<\/(?:title|desc)>/g, ' ')
  .replace(/<[^>]*>/g, ' ').replace(/,/g, '');
const drawsToken = (text, v) => {
  const s = String(v);
  if (!/^\d+(\.\d+)?$/.test(s)) return text.toLowerCase().includes(s.toLowerCase());
  if (new RegExp(`(?<![\\d.])${s.replace('.', '\\.')}(?!\\d)(?!\\.\\d)`).test(text)) return true;
  const w = WORDOF[s];
  return w ? new RegExp(`\\b${w}\\b`, 'i').test(text) : false;
};

// Each entry names ONE of claims.mjs's four independent failure modes.
//
// Round 28 (BOARD) re-aimed four of the five. Every one of them had been keyed
// to a literal the rebuild was free to change and duly did: an id whose value
// moved (cadence.handlers 36 -> 37 -> 38), a filename the redraw retired
// (plate-1-glyph.svg), a markdown heading the README no longer has (`## I ·
// Work` — the file has no `#` heading at all now), and an anchored sentence
// about seven tenant tables that was cut with the prose. Three of the four
// reported "?? stale", which is the right failure mode and still means the
// check behind them went unasked for a whole redesign.
//
// What replaces them is a SELECTOR over the spec rather than a name out of it:
// the first row that has an extractor, the first plate on disk, the first row
// carrying an anchor. The expectations keep their shape — id, message, file —
// but stop naming a value, an id or a plate, because while a real claim is
// failing a loose /the page says/ would be satisfied by the pre-existing
// failure and report "caught" with the mutation contributing nothing.
const CLAIM_MUTATIONS = [
  // 1. the extractor half — a registered value that no longer re-derives.
  //    Any row with an extractor and a numeric value will do, so it takes the
  //    first; `live` rows are skipped because they print a different sentence
  //    (claims.mjs:236) and this probe is pointed at the pinned-blob half.
  ['a registered number stops matching its pinned commit',
    /: the page says "[\d.]+", [\w.-]+\/[\w.-]+@[0-9a-f]{7}\/\S+ says "[^"]*"/,
    (root) => editJson(root, (s) => {
      const c = s.claims.find(x => x.extractor && !x.live && x.repo
        && /^\d+(\.\d+)?$/.test(String(x.value)));
      if (!c) return false;
      c.value = String(Number(c.value) + 1);
    })],
  // 2. the drawn_on half — a row asserting the page shows what it does not.
  //    Named plate-1-glyph.svg and plate-2-jetpack.svg until the redraw took
  //    the first of them; before that it named glyph.accuracy, which was never
  //    a row at all (it is glyph.accuracy_pct). Two stale anchors in one entry.
  //    So: the target is whatever plate sorts first on disk, and the row is the
  //    first whose value that plate provably does NOT draw — checked with the
  //    gate's own predicate, so the mutation cannot be a value the gate would
  //    have found anyway.
  ['a row claims a plate draws a number it never draws',
    /drawn_on lists plate-[\w-]+\.svg, but "[^"]*" does not appear there as a whole number/,
    (root) => {
      const dir = join(root, 'assets');
      const target = readdirSync(dir).sort().find(f => /^plate-.*\.svg$/.test(f));
      if (!target) return false;
      const text = plateText(join(dir, target));
      return editJson(root, (s) => {
        const c = s.claims.find(x => (x.drawn_on || []).length
          && !x.drawn_on.includes(target) && !drawsToken(text, x.value));
        if (!c) return false;
        c.drawn_on = [...c.drawn_on, target];
      });
    }],
  // 3. the coverage half — the load-bearing one. A number on the page that no
  //    row derives and no exemption names must be rejected. Appended rather
  //    than spliced into a heading: an append lands on any README that exists,
  //    and the sentence carries no numeral word, so the only number it adds to
  //    the sweep is the one the expectation names.
  ['the page grows a number nothing accounts for',
    /README\.md: draws "8675309", which claims\.json neither derives nor exempts/,
    (root) => editReadme(root, (s) =>
      `${s}\nA number no row derives and no exemption names: 8675309.\n`)],
  // 4. the anchor half — anchors exist because README.md's permitted-value pool
  //    is nearly vacuous, so an anchored sentence must fail closed when edited.
  //    The edit is the one anchors are FOR: change the count inside the pinned
  //    phrase and leave the rest of the sentence alone. Read out of the spec in
  //    the copy, so it follows the anchor wherever the prose moves it.
  ['an anchored sentence is quietly reworded',
    /: anchor "[^"]*" no longer appears in README\.md/,
    (root) => {
      const spec = JSON.parse(readFileSync(join(root, 'build', 'claims.json'), 'utf8'));
      const row = [...spec.claims, ...(spec.attested || [])]
        .find(c => (c.anchors || {})['README.md']?.length);
      if (!row) return false;
      const anchor = row.anchors['README.md'][0];
      const NUM = /\b(three|four|five|six|seven|eight|nine|ten|eleven|twelve|\d+)\b/i;
      if (!NUM.test(anchor)) return false;
      const reworded = anchor.replace(NUM, (m) => /^nineteen$/i.test(m) ? 'twelve' : 'nineteen');
      return editReadme(root, (s) => s.includes(anchor) ? s.replace(anchor, reworded) : s);
    }],
  // 5. the SCOPE of the sweep, rather than anything inside it. The light plates
  //    were added to SWEPT and made conditional on their directory in the same
  //    breath, so a missing half of the published set dropped out in silence and
  //    the coverage half of this gate — the one that rejects a number nothing
  //    accounts for — passed having swept the dark set only.
  ['half the published plates fall out of the sweep',
    /does not exist, so half the published/,
    (root) => { rmSync(join(root, 'assets', 'light'), { recursive: true, force: true }); return true; }],
];

const REPO_COPY = (dir) => cpSync(ROOT, dir, {
  recursive: true,
  // node_modules is ~200 MB of playwright and irrelevant to this gate; .git
  // likewise. snapshots/ is generated art, not input.
  filter: (src) => !/[\\/](node_modules|\.git|snapshots)([\\/]|$)/.test(src),
});

console.log('\nclaims baseline:', (() => {
  const d = mkdtempSync(join(tmpdir(), 'mutc-'));
  REPO_COPY(d);
  const out = claimsGate(d);
  rmSync(d, { recursive: true, force: true });
  return out ? 'FAILS (fix the claims first)' : 'passes';
})());

for (const [name, expect, breakIt] of CLAIM_MUTATIONS) {
  const dir = mkdtempSync(join(tmpdir(), 'mutc-'));
  REPO_COPY(dir);
  const touched = breakIt(dir);
  if (!touched) {
    console.log(`  ?? ${name} — mutation matched nothing; the probe is stale`);
    stale++; rmSync(dir, { recursive: true, force: true }); continue;
  }
  const out = claimsGate(dir);
  rmSync(dir, { recursive: true, force: true });
  const caught = expect.test(out);
  console.log(`  ${caught ? '..' : '!!'} ${name}${caught ? '' : '  — NOT CAUGHT'}`);
  if (!caught) asleep++;
}

// ── The third family: can plates.py fail?
//
// The two families above mutate a plate and invoke gate.mjs, or falsify a
// number and invoke claims.mjs. Nothing in this file has ever pointed at the
// GENERATOR, which carries a build-time gate of its own: charset coverage, XML
// well-formedness, the MFRAME/MOBILE pairing, the sweep that deletes plates the
// build no longer authors, and the alt/desc agreement — the only assertion
// anywhere that the sentence a screen reader is given is the sentence the plate
// wrote. Five checks, on the accessibility contract and on the published file
// set, and not one of them had ever been watched to fail.
//
// Writing these found two. The alt/desc block was `if _readme.exists():`, so a
// README that did not resolve skipped the whole agreement in silence and exited
// 0 — and the case is not hypothetical, because macOS matches `Readme.md`
// case-insensitively and the Linux runner that publishes does not. And the
// other 27 of the 36 published files, every light twin and the entire mobile
// set, reach the page through <source srcset>, which the alt loop never reads:
// a plate could be authored and referenced nowhere, or referenced and authored
// by nothing, with every gate green. Both are checks now, and both directions
// are probed below.
//
// Same shape as the claims family: copy the repository, break one input, run
// the COPY's build. platesGate returns output on success as well as failure,
// because one of these probes asserts that a run SUCCEEDS and says something.
const platesGate = (root) => {
  try {
    return execFileSync('python3', [join(root, 'build', 'plates.py')],
      { cwd: root, encoding: 'utf8', stdio: 'pipe' });
  } catch (e) { return (e.stdout || '') + (e.stderr || ''); }
};
const editFile = (root, rel, fn) => {
  const p = join(root, rel);
  if (!existsSync(p)) return false;
  const before = readFileSync(p, 'utf8');
  const after = fn(before);
  if (after === undefined || after === before) return false;
  writeFileSync(p, after);
  return true;
};

// Round 28 (BOARD): six of the nine named a file, a name or a line of Python
// that the rebuild replaced, and every one of them reported "?? stale". They
// are re-aimed at the SHAPE of what plates.py checks — the first <img> alt in
// the README, the first light mobile reference, the character sets by name
// rather than by member, the </svg> the writer appends — so a rename cannot
// silence them again. The seventh is DELETED rather than re-aimed: see below.
const PLATE_MUTATIONS = [
  // 1-2. the accessibility contract, in its two failure modes. Drift is the one
  //      that was already checked; absence is the one that used to pass.
  //      Anchored on plate-0-thesis.svg until the redraw renamed it
  //      plate-0-hero.svg; it takes whichever desktop plate the README serves
  //      first now, which is the same assertion with nothing to rot.
  ['an alt drifts from the description its plate authored',
    /plate-[\w-]+\.svg: README alt has drifted from the plate's own description/,
    (root) => editFile(root, 'README.md', (s) => s.replace(
      /(<img src="\.\/assets\/plate-[\w-]+\.svg"[^>]*?alt=")/, '$1Not what the plate says. '))],
  ['README.md is not there at all',
    /README\.md: not found/,
    (root) => { rmSync(join(root, 'README.md')); return true; }],
  // 3-4. the published set, both directions. Probe 3 appends a character to a
  //      filename rather than deleting the line, because that is the mistake a
  //      person actually makes — and because the first draft of the check used
  //      an unanchored regex that still matched `…svgX` through its `.svg` and
  //      called the reference present. It takes the first light-theme mobile
  //      reference in the file rather than naming m-4-applied.svg, which the
  //      redraw retired.
  ['a published plate is referenced nowhere in the README',
    /\.\/assets\/light\/m-[\w-]+\.svg: this build authors it and README\.md references it nowhere/,
    (root) => editFile(root, 'README.md', (s) =>
      s.replace(/(\.\/assets\/light\/m-[\w-]+\.svg)(?=")/, '$1X'))],
  // Probe 4 used to rename a real reference, which trips three checks at once
  // and named a plate (m-5-refusal.svg) that no longer exists. It ADDS a
  // reference now: the only defect is the one the expectation names, and the
  // filename is this probe's own invention, so no redraw can retire it.
  ['the README reaches for a plate no build authors',
    /\.\/assets\/plate-zz-unauthored\.svg: README\.md references it and no build authors it/,
    (root) => editFile(root, 'README.md', (s) =>
      `${s}\n<img src="./assets/plate-zz-unauthored.svg" alt="a reference no build answers">\n`)],
  // 5-6. charset coverage: a glyph the subset does not carry falls back to a
  //      platform font, and nothing downstream can see it — gate.mjs measures
  //      the geometry of the FALLBACK and passes.
  //
  //      BOARD retired the mono and the serif; the faces are Syne 800
  //      (DISPLAY_CHARS) and Commissioner 400/600 (TEXT_CHARS). The old probes
  //      named BOLD_CHARS and SERIF_CHARS, neither of which exists, so both
  //      arms of the only check standing between this page and a platform font
  //      mid-word were unexercised. LABEL_CHARS is still TEXT_CHARS — the same
  //      object, charsets.py:32 — so a probe of the label-vs-text arm would be
  //      asserting nothing; the expectation below accepts whichever of the two
  //      names the check happens to print, and there is no third probe for a
  //      distinction the source does not make.
  //
  //      Probe 5 strips EVERY digit rather than one: which digits the display
  //      face draws is a design decision (the section romans carry none), and a
  //      probe that pins one is the stale-probe shape this file documents.
  ['a digit leaves the display face and falls back to a platform font',
    /draws '\d' in the display face, which does not carry it/,
    (root) => editFile(root, 'build/charsets.py', (s) =>
      s.replace(/^(DISPLAY_CHARS = \(?")([^"]*)"/m,
        (_m, head, set) => `${head}${set.replace(/\d/g, '')}"`))],
  ['a letter leaves the text face',
    /draws 't' in the (?:text|label) face, which does not carry it/,
    (root) => editFile(root, 'build/charsets.py', (s) =>
      s.replace(/^(TEXT_CHARS = \(?")([^"]*)"/m,
        (_m, head, set) => `${head}${set.replace('t', '')}"`))],
  // 7. DELETED, 2026-08-12, and the deletion is the finding.
  //
  //    The probe here asserted `MFRAME/MOBILE disagree` — the pairing that kept
  //    check 12 honest on the phone canvas by requiring every mobile plate to
  //    declare a frame. There is no MFRAME in plates.py any more and no such
  //    assertion: the rebuilt mobile plates all take one MOB_FRAME
  //    (plates.py:1698, 1174), so there is no per-file table left to disagree
  //    with. A probe cannot be re-aimed at a check that is gone, and leaving it
  //    printing "?? stale" would have gone on implying a build-time guard that
  //    does not exist. gate.mjs check 12 still asserts the DRAWN edge against
  //    the declaration on every mobile file, in both themes, and the two mobile
  //    probes in the first family above are pointed at it.
  //
  //    Two plates.py checks arrived where this one stood and have no probe:
  //    the `<source media="(max-width: 500px)">` service check (plates.py:1829)
  //    and its light-twin counterpart (1831). Naming them here rather than
  //    quietly leaving the count at nine, because an unprobed check that nobody
  //    has written down is exactly how this file's four dead gates happened.
  // 8. well-formedness. A plate that is not parseable XML is not a plate;
  //    GitHub serves it as a torn image and every other gate here reads the
  //    file as text and never notices. Keyed to the closing tag every writer
  //    appends rather than to one `return` line, which the rebuild split
  //    fourteen ways.
  ['a plate emits markup that is not well-formed',
    /plate-[\w-]+\.svg: MALFORMED XML/,
    (root) => editFile(root, 'build/plates.py', (s) =>
      s.replace(/\+ "<\/svg>"/g, '+ "</svgg>"'))],
  // 9. the sweep, and the only probe here that requires the build to SUCCEED.
  //    A plate dropped from PLATES survives in assets/ unless something deletes
  //    it, and a stale file on disk is a stale claim surface: the gates sweep
  //    the directory, so it would go on being measured and go on being served
  //    by any README that still points at it.
  ['a plate this build no longer authors is left on disk',
    /plate-zz-stale\.svg: removed \(no longer authored\)/,
    (root) => {
      writeFileSync(join(root, 'assets', 'plate-zz-stale.svg'),
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1 1"/>');
      return true;
    }],
];

console.log('\nplates baseline:', (() => {
  const d = mkdtempSync(join(tmpdir(), 'mutp-'));
  REPO_COPY(d);
  const out = platesGate(d);
  rmSync(d, { recursive: true, force: true });
  return /GATE FAILED/.test(out) ? 'FAILS (fix the build first)' : 'passes';
})());

for (const [name, expect, breakIt] of PLATE_MUTATIONS) {
  const dir = mkdtempSync(join(tmpdir(), 'mutp-'));
  REPO_COPY(dir);
  const touched = breakIt(dir);
  if (!touched) {
    console.log(`  ?? ${name} — mutation matched nothing; the probe is stale`);
    stale++; rmSync(dir, { recursive: true, force: true }); continue;
  }
  const out = platesGate(dir);
  rmSync(dir, { recursive: true, force: true });
  const caught = expect.test(out);
  console.log(`  ${caught ? '..' : '!!'} ${name}${caught ? '' : '  — NOT CAUGHT'}`);
  if (!caught) asleep++;
}

if (stale || asleep) {
  if (asleep) console.log(`\n${asleep} mutation(s) went unnoticed — the page was broken, the gate `
    + `read it, and said nothing. Those checks are asleep.`);
  if (stale) console.log(`\n${stale} probe(s) matched nothing — the mutation never landed, so the `
    + `check behind it was never asked. Those probes are stale: they prove nothing in either `
    + `direction, and a green line from one would have been a lie.`);
  process.exit(1);
}
console.log('\nevery mutation landed and every mutation was caught: the checks are live.');
