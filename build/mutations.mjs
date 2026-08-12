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
  ['text collides with text', /"OVERLAP" collides with|collides with "OVERLAP"/,
    (s) => s.replace(/<text x="150" y="(\d+)" class="(\w+)">/,
      (m, y, c) => `<text x="150" y="${y}" class="${c}">OVERLAP</text>${m}`)],
  ['ink leaves the canvas', /leaves the canvas/,
    (s) => s.replace(/<text x="150" y="56"/, '<text x="1500" y="56"')],
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
  // Applied's refused message rests beside the human for the first 30% of
  // its loop; flipping that hold to opacity:0 hides it for most of the cycle.
  // (Round 21 re-anchor: the sieve became the sifting channel and the hold
  // moved from 52% to 30%.)
  ['an element hides for most of its loop', /visible only \d+%/,
    (s) => s.replace(/0%,30%\{opacity:1;/, '0%,30%{opacity:0;')],
  // Anchored on `class="lbl" style="fill:#F5A524"` until a round reclaimed that
  // amber for Glyph, and then it matched nothing. Third stale probe of the
  // week, all three from keying on a literal that design work is free to
  // change. Keys on the SHAPE now: any classed element that sets its fill
  // through `style` — which is the whole point of the check, since a `fill`
  // ATTRIBUTE loses to any CSS rule and paints nothing.
  ['a fill attribute is overridden by its class', /overriding the attribute/,
    (s) => s.replace(/class="([\w ]+)" style="fill:(#[0-9A-Fa-f]{6})"/,
      (m, c, col) => `class="${c}" fill="${col}"`)],
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
  ['text drops below 4.5:1 on the slab', /on the slab \(needs 4.5/,
    // Round 25 moved .fine's tracking 0.4px -> 0px when the text face became
    // Newsreader (a serif's lowercase wants no extra air; the mono's did).
    // The probe went stale and SAID SO, which is what the note above asks for:
    // pinning the authored typography means a redesign trips this on purpose
    // rather than silently carrying a probe that matches nothing.
    (s) => s.replace(/\.fine\{font-size:13px;letter-spacing:0px;fill:#[0-9A-Fa-f]{6}\}/,
      '.fine{font-size:13px;letter-spacing:0px;fill:#8a8175}')],
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
  ['a token rests short of its target', /should come to rest at|still frame is the START/,
    (s) => s.replace(/data-rest-within="12" x="(\d+)"/,
      (m, x) => `data-rest-within="12" x="${Number(x) - 100}"`)],
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
  // (Round 27: the y="82" literal died with the plate that carried it — the
  // SAME y-literal trap already fixed on the fill-opacity probe below, one
  // instance missed. Keys on the shape of any left-column label now.)
  ['contrast is destroyed by an ancestor group opacity', /on the slab \(needs 4.5/,
    (s) => s.replace(/(<text x="150" y="\d+" class="lbl">[^<]*<\/text>)/, '<g opacity="0.5">$1</g>')],
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
  // (Round 20 re-anchor: the refusal's SIX SERVICES say-line. Round 27: that
  // line went with the audit table it headed, so this keys on the SHAPE — the
  // first left-column .say in the sorted set, which is jetpack's bench
  // header. A y-literal was the third stale-probe pattern in one week.)
  ['contrast is destroyed by fill-opacity', /on the slab \(needs 4.5/,
    (s) => s.replace(/(<text x="150" y="\d+" class="say")/, '$1 fill-opacity="0.12"')],
  // Check 21 (data-canvas) is new in round 27 and gets its probe in the same
  // change — this file's whole history is checks trusted before they were
  // watched to fail. Paints a full-canvas sheet onto a plate that declares
  // itself transparent; keyed to the attribute rather than a filename, so it
  // follows the frontispieces wherever they move.
  ['a transparent frontispiece paints a sheet anyway', /cannot be both paper and transparency/,
    (s) => s.includes('data-canvas') ? s.replace(/(<desc>)/,
      '<rect x="86" y="0" width="708" height="100%" fill="#43372f"/>$1') : s],
  // Check 13 fires when a plate declares animations NONE of which moves
  // anything — dead code on the reader's compositor wearing the name of a
  // gesture. Round 21 anchored this on the title page's two carriers; round
  // 22 gave the title page the index-read chase, so freezing those two no
  // longer silences it and the probe moved to the colophon — the plate with
  // the fewest declared animations — freezing all three (the turning device,
  // the counter-rotation that keeps its marks upright, the drifting halo).
  ['a declared animation never moves anything', /never move anything/,
    (s) => s
      .replace('to{transform:rotate(360deg)}', 'to{transform:rotate(0deg)}')
      .replace('to{transform:rotate(-360deg)}', 'to{transform:rotate(0deg)}')
      .replace('to{stroke-dashoffset:-44}', 'to{stroke-dashoffset:0}')],
  // Check 14 is the surviving motion-quality check (a stagger is a wave, not a
  // queue), so it keeps a probe: stretching the middle pen stroke's delay on
  // Glyph opens a 400ms hole in a 150ms wave.
  // (Round 27: Glyph's pen stagger went with the pen. The wave now lives on the
  // refusal's redaction rows. Rather than name that plate — the mistake this
  // probe has made twice — the mutation asks each file in turn whether it holds
  // a stagger at all: fewer than three distinct delays and it declines, so the
  // runner moves on. Then it pushes the LAST step 600ms past the others, which
  // is a hole no averaging can hide, against a 200ms ceiling.)
  ['a stagger step is too wide to read as one gesture',
    /has a \d+ms step across \d+ elements \(ceiling 200ms\) — too slow/,
    (s) => {
      // Counting delays FILE-WIDE was wrong and the first run caught it: check 5
      // groups by animation NAME (gate.mjs:641), and plate-4-applied's four
      // delays sit on four different names — four groups of one, which the check
      // skips at `delays.size < 2`. The mutation landed on a plate the check has
      // no jurisdiction over and the corrupted file passed clean. So group the
      // same way the check does: by animation name when the element declares
      // one, by first class token otherwise.
      const groups = new Map();
      for (const tag of s.match(/<[^>]*animation-delay:[^>]*>/g) || []) {
        const d = /animation-delay:(-?[\d.]+)s/.exec(tag)?.[1];
        const key = /animation:\s*([\w-]+)/.exec(tag)?.[1]
                 ?? /class="([\w-]+)/.exec(tag)?.[1];
        if (d === undefined || !key) continue;
        if (!groups.has(key)) groups.set(key, new Set());
        groups.get(key).add(d);
      }
      const wave = [...groups.values()].find(v => v.size >= 3);
      if (!wave) return s;                       // no stagger here — try the next plate
      // gate.mjs:643 reads Math.abs(delay), so widen the MAGNITUDE. Adding 0.6
      // to the largest of a negative set (-3.1 -> -2.5) narrows the step instead.
      const far = [...wave].reduce((a, b) =>
        (Math.abs(parseFloat(b)) > Math.abs(parseFloat(a)) ? b : a));
      const v = parseFloat(far);
      return s.replace(`animation-delay:${far}s`,
        `animation-delay:${(v < 0 ? v - 0.6 : v + 0.6).toFixed(2)}s`);
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
  // The font-load assertion covered family 'M' and nothing else, so the SERIF
  // — every hero numeral on the page — could have fallen back to a platform
  // face and been measured there. This corrupts the SERIF's base64 payload
  // specifically, so the probe exercises the half that was missing rather than
  // the half that already worked.
  ['an embedded webfont fails to load', /the embedded 'S' 600 webfont did not load/,
    (s) => s.replace(/(font-family:'S';font-weight:600;src:url\(data:font\/woff2;base64,)([A-Za-z0-9+/=]{240})/,
      (m, head) => head + 'A'.repeat(240))],
  // The other direction. Two plates stopped embedding the serif-600 face
  // because nothing on them renders it (~7.5 KB each, four files); that is only
  // safe while a plate which DOES render it cannot quietly lose it. Strips the
  // face from a plate that uses a hero and expects the fallback to be named.
  ['a rendered face is not embedded', /renders 'S' at weight 600, which no @font-face/,
    (s) => s.replace(/@font-face\{font-family:'S';font-weight:600;src:url\(data:font\/woff2;base64,[A-Za-z0-9+/=]+\) format\('woff2'\)\}\n?/, '')],
  ['a moving rule is drawn through type', /rect\.mutsweep[^\n]*sweeps across/,
    (s) => {
      const m = /<text x="150" y="(\d+)" class="(?:kick|lbl|fine|key)"/.exec(s);
      if (!m) return s;
      return s.replace('</svg>',
        '<style>@keyframes mutsweep{from{transform:translateY(-30px)}'
        + 'to{transform:translateY(30px)}}</style>'
        + `<rect class="mutsweep" x="150" y="${Number(m[1]) - 8}" width="360" height="2" `
        + 'fill="#ffffff" style="animation:mutsweep 4s linear infinite"/></svg>');
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
  ['a solid graphic is laid over type', /<rect [\d.,]+> sits on top of/,
    (s) => {
      const m = /<text x="([\d.]+)" y="([\d.]+)" class="(?:lbl|kick|fine)\b[^"]*"/.exec(s);
      if (!m) return s;
      return s.replace('</svg>',
        `<rect x="${Number(m[1]) + 2}" y="${Number(m[2]) - 12}" width="80" height="16" `
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
let dead = 0;
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
    dead++; rmSync(dir, { recursive: true, force: true }); continue;
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
  if (!caught) dead++;
}
// ── Still gate.mjs, but breaking the SET rather than a file in it.
//
// Family 1 mutates the text of one plate, so there is no way to say "the light
// twins are not there" in its vocabulary — and that turned out to be the guard
// worth saying it about. gate.mjs pushed the light set only `if (existsSync)`,
// three lines under a comment asserting those files "are measured by every
// check here", so an absent directory left the gate measuring the dark half and
// printing GATE PASSED. Same runner, a mutator that takes the copied directory.
const SET_MUTATIONS = [
  ['the light twin of every plate is missing', /does not exist\. It holds the light twin/,
    (dir) => { rmSync(join(dir, 'light'), { recursive: true, force: true }); return true; }],
  // and the partial case, which the existsSync form could never have seen even
  // when the directory was present: one theme holding one fewer plate than the
  // other means a <picture> whose light <source> resolves to nothing.
  ['one plate loses its light twin', /have no light twin: plate-1-glyph\.svg/,
    (dir) => { rmSync(join(dir, 'light', 'plate-1-glyph.svg')); return true; }],
];
for (const [name, expect, breakIt] of SET_MUTATIONS) {
  const dir = mkdtempSync(join(tmpdir(), 'mut-'));
  cpSync(ASSETS, dir, { recursive: true });
  breakIt(dir);
  const out = gate(dir);
  rmSync(dir, { recursive: true, force: true });
  const caught = expect.test(out);
  console.log(`  ${caught ? '..' : '!!'} ${name}${caught ? '' : '  — NOT CAUGHT'}`);
  if (!caught) dead++;
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

// Each entry names ONE of claims.mjs's four independent failure modes. They are
// keyed to the mutated row by id, not to a bare phrase: while any real claim is
// failing, a loose /the page says/ would be satisfied by the pre-existing
// failure and report "caught" with the mutation contributing nothing.
const CLAIM_MUTATIONS = [
  // 1. the extractor half — a registered value that no longer re-derives
  ['a registered number stops matching its pinned commit',
    /cadence\.handlers: the page says "38"/,
    (root) => editJson(root, (s) => {
      const c = s.claims.find(x => x.id === 'cadence.handlers');
      if (!c) return false;
      c.value = String(Number(c.value) + 1);
    })],
  // 2. the drawn_on half — a row asserting the page shows what it does not.
  //    Keyed on SHAPE, not on an id: three plate probes above went stale in one
  //    week from pinning a literal, and `glyph.accuracy` was already the wrong
  //    guess here (the row is `glyph.accuracy_pct`). This picks any Glyph row
  //    whose value provably does NOT occur in the jetpack plate, so the
  //    expectation below cannot be satisfied by coincidence.
  ['a row claims a plate draws a number it never draws',
    /drawn_on lists plate-2-jetpack\.svg, but "[^"]*" does not appear there/,
    (root) => editJson(root, (s) => {
      const other = readFileSync(join(ASSETS, 'plate-2-jetpack.svg'), 'utf8');
      const c = s.claims.find(x => (x.drawn_on || []).includes('plate-1-glyph.svg')
        && !other.includes(String(x.value)));
      if (!c) return false;
      c.drawn_on = [...c.drawn_on, 'plate-2-jetpack.svg'];
    })],
  // 3. the coverage half — the load-bearing one. A number on the page that no
  //    row derives and no exemption names must be rejected.
  ['the page grows a number nothing accounts for',
    /README\.md: draws "8675309"/,
    (root) => editReadme(root, (s) =>
      s.replace('## I · Work', '## I · Work 8675309'))],
  // 4. the anchor half — anchors exist because README.md's permitted-value pool
  //    is nearly vacuous, so an anchored sentence must fail closed when edited.
  // Round 27: same defect as the collision probe above. The expectation named
  // no row, so while automl.tool_sets held an anchor into alt text that a plate
  // rewrite had deleted, the claims baseline printed this exact sentence for a
  // row this mutation never touches — and the probe passed without discriminating.
  // Keyed to the sentence it actually rewords now.
  ['an anchored sentence is quietly reworded',
    /anchor "[^"]*seven\*\* tenant tables" no longer appears in README\.md/,
    (root) => editReadme(root, (s) =>
      s.replace('on all **seven** tenant tables', 'on all **nineteen** tenant tables'))],
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
    dead++; rmSync(dir, { recursive: true, force: true }); continue;
  }
  const out = claimsGate(dir);
  rmSync(dir, { recursive: true, force: true });
  const caught = expect.test(out);
  console.log(`  ${caught ? '..' : '!!'} ${name}${caught ? '' : '  — NOT CAUGHT'}`);
  if (!caught) dead++;
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

const PLATE_MUTATIONS = [
  // 1-2. the accessibility contract, in its two failure modes. Drift is the one
  //      that was already checked; absence is the one that used to pass.
  ['an alt drifts from the description its plate authored',
    /plate-0-thesis\.svg: README alt has drifted/,
    (root) => editFile(root, 'README.md', (s) => s.replace(
      /(<img src="\.\/assets\/plate-0-thesis\.svg"[^>]*?alt=")/, '$1Not what the plate says. '))],
  ['README.md is not there at all',
    /README\.md: not found/,
    (root) => { rmSync(join(root, 'README.md')); return true; }],
  // 3-4. the published set, both directions. Probe 3 appends a character to a
  //      filename rather than deleting the line, because that is the mistake a
  //      person actually makes — and because the first draft of the check used
  //      an unanchored regex that still matched `…svgX` through its `.svg` and
  //      called the reference present.
  ['a published plate is referenced nowhere in the README',
    /m-4-applied\.svg: this build authors it and README\.md references it nowhere/,
    (root) => editFile(root, 'README.md', (s) =>
      s.replace('./assets/light/m-4-applied.svg', './assets/light/m-4-applied.svgX'))],
  ['the README reaches for a plate no build authors',
    /m-5-refusalZZ\.svg: README\.md references it and no build authors it/,
    (root) => editFile(root, 'README.md', (s) =>
      s.replace('./assets/m-5-refusal.svg"', './assets/m-5-refusalZZ.svg"'))],
  // 5-6. charset coverage: a glyph the subset does not carry falls back to a
  //      platform font, and nothing downstream can see it — gate.mjs measures
  //      the geometry of the FALLBACK and passes. Only the 600 and the serif are
  //      probed: TEXT_CHARS is MONO_CHARS, the same object, so a probe of the
  //      mach-vs-text arm would be asserting nothing. That is a true statement
  //      about the check, not a working probe, and it is not scored as one.
  ['a digit leaves the display face and falls back to a platform font',
    /draws '4' in the 600 face/,
    (root) => editFile(root, 'build/charsets.py', (s) =>
      s.replace(/^(BOLD_CHARS = ")([^"]*)"/m, (_m, head, set) => `${head}${set.replace('4', '')}"`))],
  ['a letter leaves the serif face',
    /draws 't' in the serif face/,
    (root) => editFile(root, 'build/charsets.py', (s) =>
      s.replace(/^(SERIF_CHARS = ")([^"]*)"/m, (_m, head, set) => `${head}${set.replace('t', '')}"`))],
  // 7. the pairing that keeps check 12 honest on the phone canvas. Sliced from
  //    MFRAME's own text rather than searched for globally: MOBILE is declared
  //    first and holds a tuple under the same key, so an unscoped match would
  //    delete the plate instead of its frame and trip the guard for the wrong
  //    reason.
  ['a mobile plate loses the frame declaration check 12 measures it against',
    /MFRAME\/MOBILE disagree/,
    (root) => editFile(root, 'build/plates.py', (s) => {
      const i = s.indexOf('MFRAME = {');
      if (i < 0) return undefined;
      const head = s.slice(0, i), tail = s.slice(i);
      const cut = tail.replace(/"m-1-glyph\.svg":\s*\([^)]*\),\s*/, '');
      return cut === tail ? undefined : head + cut;
    })],
  // 8. well-formedness. A plate that is not parseable XML is not a plate;
  //    GitHub serves it as a torn image and every other gate here reads the
  //    file as text and never notices.
  ['a plate emits markup that is not well-formed',
    /plate-[\w-]+\.svg: MALFORMED XML/,
    (root) => editFile(root, 'build/plates.py', (s) =>
      s.replace('return "".join(s) + "</svg>"', 'return "".join(s) + "</svgg>"'))],
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
    dead++; rmSync(dir, { recursive: true, force: true }); continue;
  }
  const out = platesGate(dir);
  rmSync(dir, { recursive: true, force: true });
  const caught = expect.test(out);
  console.log(`  ${caught ? '..' : '!!'} ${name}${caught ? '' : '  — NOT CAUGHT'}`);
  if (!caught) dead++;
}

if (dead) { console.log(`\n${dead} mutation(s) went unnoticed — those checks are not connected.`); process.exit(1); }
console.log('\nevery mutation was caught: the checks are live.');
