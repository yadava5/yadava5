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
 * below breaks the plates in one specific way and names the check that must
 * notice. A check that stays silent under its own mutation is dead code wearing
 * a passing grade.
 *
 * Usage: node build/mutations.mjs
 */
import { execFileSync } from 'node:child_process';
import { readFileSync, writeFileSync, mkdtempSync, readdirSync, cpSync } from 'node:fs';
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
  // Glyph's ISA tokens are visible from 5% to 96% of their loop; flipping the
  // long hold to opacity:0 hides them for most of it. (Used to key on jetpack's
  // .row ripple, which was deleted as decoration.)
  ['an element hides for most of its loop', /visible only \d+%/,
    (s) => s.replace(/34%,96%\{opacity:1;/, '34%,96%{opacity:0;')],
  // Anchored on `class="lbl" style="fill:#F5A524"` until a round reclaimed that
  // amber for Glyph, and then it matched nothing. Third stale probe of the
  // week, all three from keying on a literal that design work is free to
  // change. Keys on the SHAPE now: any classed element that sets its fill
  // through `style` — which is the whole point of the check, since a `fill`
  // ATTRIBUTE loses to any CSS rule and paints nothing.
  ['a fill attribute is overridden by its class', /overriding the attribute/,
    (s) => s.replace(/class="([\w ]+)" style="fill:(#[0-9A-Fa-f]{6})"/,
      (m, c, col) => `class="${c}" fill="${col}"`)],
  ['text drops below 4.5:1 on the slab', /on the slab \(needs 4.5/,
    (s) => s.replace(/\.fine\{font-size:13px;letter-spacing:0\.6px;fill:#8A8F98\}/, '.fine{font-size:13px;letter-spacing:0.6px;fill:#3A3E44}')],
  // Keys on plate V's diverted message, which declares data-rest="the-human":
  // pulling its authored x back 90u strands it short of the person it must
  // reach, in both the animated and the still frame.
  ['a token rests short of its target', /should come to rest at|still frame is the START/,
    (s) => s.replace(/data-rest-within="10" x="656"/, 'data-rest-within="10" x="566"')],
  // Both of the following were dead until an audit ran them by hand. They are
  // probes now so that cannot happen twice.
  //
  // Check 10 read the element's OWN opacity, which is never inherited, so
  // anything inside a dimmed <g> was graded at full strength. Wrapping one
  // 6.09:1 label in <g opacity="0.5"> takes it to 2.32:1 and the gate passed.
  // (Keys on jetpack's first benchmark-table row — the old "row lbl" class
  // token went with the table's decorative ripple.)
  ['contrast is destroyed by an ancestor group opacity', /on the slab \(needs 4.5/,
    (s) => s.replace(/(<text class="lbl" x="150" y="416">[^<]*<\/text>)/, '<g opacity="0.5">$1</g>')],
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
  ['contrast is destroyed by fill-opacity', /on the slab \(needs 4.5/,
    (s) => s.replace(/(<text class="lbl" x="150" y="440")/, '$1 fill-opacity="0.12"')],
  // RE-AUTHORED with checks 13/17: stillness is legal now, so "no animations
  // at all" stopped being a defect and its probe retired with it. The defect
  // that replaced it is an animation that MOVES NOTHING — dead code on the
  // reader's compositor wearing the name of a gesture. Applied's refusal
  // journey is the only animation on its plate; freezing its keyframes into a
  // constant leaves a declared animation with zero geometric change across
  // the whole loop, which the re-authored check 13 must call out. ('a plate
  // freezes for too long' retired with the 2.4s ceiling it tested — the
  // ceiling was the doctrine that grew the sweeps.)
  ['a declared animation never moves anything', /never move anything/,
    (s) => s.replace(/@keyframes dv\{[^]*?\}\}/,
      '@keyframes dv{0%,100%{opacity:1;transform:translate(0,0)}}')],
  // Check 14 is the surviving motion-quality check (a stagger is a wave, not a
  // queue), so it keeps a probe: stretching the middle pen stroke's delay on
  // Glyph opens a 400ms hole in a 150ms wave.
  ['a stagger step is too wide to read as one gesture', /too slow to read as one gesture/,
    (s) => s.replace(/animation-delay:-7\.45s/, 'animation-delay:-6.9s')],
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
  if (!touched) { console.log(`  ?? ${name} — mutation matched nothing; the probe is stale`); dead++; continue; }
  const out = gate(dir);
  const caught = expect.test(out);
  console.log(`  ${caught ? '..' : '!!'} ${name}${caught ? '' : '  — NOT CAUGHT'}`);
  if (!caught) dead++;
}
if (dead) { console.log(`\n${dead} mutation(s) went unnoticed — those checks are not connected.`); process.exit(1); }
console.log('\nevery mutation was caught: the checks are live.');
