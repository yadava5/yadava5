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
 * TWO families, because for a long time there was only one. The first mutates a
 * plate and invokes gate.mjs. The second copies the repository, falsifies
 * claims.json or README.md, and invokes claims.mjs — which until round 25 had
 * no probe at all, so the gate that leaves the repository and re-derives 56
 * numbers had never once been watched to fail. That is the same shape as the
 * four dead gates above, and it survived precisely because this file's own
 * name made it look like the negative test was covered.
 *
 * Usage: node build/mutations.mjs
 */
import { execFileSync } from 'node:child_process';
import { readFileSync, writeFileSync, mkdtempSync, readdirSync, cpSync, rmSync } from 'node:fs';
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
  ['text collides with text', /collides with/,
    (s) => s.replace(/<text x="150" y="(\d+)" class="(\w+)">/,
      (m, y, c) => `<text x="150" y="${y}" class="${c}">OVERLAP</text>${m}`)],
  ['ink leaves the canvas', /leaves the canvas/,
    (s) => s.replace(/<text x="150" y="56"/, '<text x="1500" y="56"')],
  // Glyph's first hand-drawn glyph carries its negative delay in an element
  // style; zeroing it puts the pen at 0% at t=0 — an undrawn stroke on the
  // authored frame, which check 6 must call out. Keys on the element style,
  // NOT the .ink class default: the same "-7.6s" appears there too, and
  // mutating the class is a no-op because every element overrides it.
  ['a draw-on is blank at frame zero', /undrawn at frame zero/,
    (s) => s.replace(/pathLength="1" style="animation-delay:-7\.6s"/, 'pathLength="1" style="animation-delay:0s"')],
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
    (s) => s.replace(/\.fine\{font-size:13px;letter-spacing:0\.4px;fill:#[0-9A-Fa-f]{6}\}/,
      '.fine{font-size:13px;letter-spacing:0.4px;fill:#8a8175}')],
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
  ['contrast is destroyed by an ancestor group opacity', /on the slab \(needs 4.5/,
    (s) => s.replace(/(<text x="150" y="82" class="lbl">[^<]*<\/text>)/, '<g opacity="0.5">$1</g>')],
  // Check 9 compared the accessible description to the plate with
  // String.includes, so any number that is a PREFIX of one the plate draws
  // passed: "29" is a substring of "299". The desc is the only thing a screen
  // reader gets, and it was the least guarded string in the repo.
  ['a description number is falsified to a prefix', /description says/,
    (s) => s.replace(/which means 299 wrong/g, 'which means 29 wrong')],
  // Three ways to make ink transparent in SVG and check 10 read only two.
  // fill-opacity and stroke-opacity are sibling presentation attributes, not
  // `opacity` and not an rgba alpha, and they are exactly what an exported
  // logo carries — two of the six product marks shipped at 1.49:1 and 2.68:1
  // because of it.
  // (Round 20 re-anchor: the refusal's SIX SERVICES say-line.)
  ['contrast is destroyed by fill-opacity', /on the slab \(needs 4.5/,
    (s) => s.replace(/(<text x="150" y="88" class="say")/, '$1 fill-opacity="0.12"')],
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
  ['a stagger step is too wide to read as one gesture', /too slow to read as one gesture/,
    (s) => s.replace(/animation-delay:-7\.45s/, 'animation-delay:-6.9s')],
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
for (const [name, expect, breakIt] of MUTATIONS) {
  const dir = mkdtempSync(join(tmpdir(), 'mut-'));
  cpSync(ASSETS, dir, { recursive: true });
  let touched = false;
  for (const f of readdirSync(dir).filter(x => /^plate-.*\.svg$/.test(x))) {
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
// ── The second family: can claims.mjs fail?
//
// Everything above mutates a PLATE and invokes gate.mjs. That was the WHOLE
// negative test, which means claims.mjs — the gate that leaves the repository
// and re-derives 56 numbers from pinned commits — had no probe at all, and the
// colophon's "fails if a check sleeps through it" was a sentence about one of
// two gates. A gate nobody has ever watched fail is this repo's signature
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
  ['an anchored sentence is quietly reworded',
    /anchor .* no longer appears in README\.md/,
    (root) => editReadme(root, (s) =>
      s.replace('on all **seven** tenant tables', 'on all **nineteen** tenant tables'))],
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

if (dead) { console.log(`\n${dead} mutation(s) went unnoticed — those checks are not connected.`); process.exit(1); }
console.log('\nevery mutation was caught: the checks are live.');
