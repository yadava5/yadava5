/**
 * The claims gate.
 *
 * gate.mjs check 9 compares the plate's <desc> against the plate's own drawn
 * text. That is worth having, but it only proves two strings the same author
 * wrote agree with each other. Both can be false, and three rounds of audits
 * found exactly that: a retracted figure lived on in the SVG after the prose
 * was corrected, and a "corrected" claim was itself wrong.
 *
 * This gate goes outside the repository. For every number the page draws it
 * fetches the pinned blob from raw.githubusercontent.com at a COMMIT SHA, runs
 * the row's extractor against it, and requires the output to equal the value.
 * A reader can run the same command. That is the difference between "every
 * number is traceable" as a slogan and as a mechanism.
 *
 * It fails in BOTH directions:
 *   · a registered claim whose extractor no longer reproduces its value
 *   · a number a plate draws that no row and no exemption accounts for
 *
 * The second one is the load-bearing half. A claims file that only checked the
 * numbers it happened to list is the same gate-that-cannot-fail this project
 * has already shipped twice (the char-count gate, and the duty cycle summed
 * per class). You cannot add a number to a plate without registering it here.
 */
import { readFileSync, readdirSync, writeFileSync, mkdirSync, existsSync, statSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
// See the note in motion.mjs: GATE_ASSETS makes this gate negative-testable.
const ASSETS = process.env.GATE_ASSETS || join(ROOT, 'assets');
const CACHE = join(ROOT, 'build', '.claims-cache');
const spec = JSON.parse(readFileSync(join(ROOT, 'build', 'claims.json'), 'utf8'));
const OFFLINE = process.argv.includes('--offline');

mkdirSync(CACHE, { recursive: true });
const fails = [];
const notes = [];

// ── fetch a blob, pinned. The SHA is in the path, so the cache can never go
//    stale: a different commit is a different file.
function blob(repoKey, path) {
  const r = repo(repoKey);
  const dest = join(CACHE, cacheKey(r, path));
  if (existsSync(dest)) return dest;
  if (OFFLINE) throw new Error(`--offline and ${path} is not cached`);
  const url = `https://raw.githubusercontent.com/${r.github}/${r.ref}/${path}`;
  const body = execFileSync('curl', ['-fsSL', '--max-time', '120', url], {
    maxBuffer: 1 << 30, encoding: 'buffer',
  });
  writeFileSync(dest, body);
  return dest;
}

const repo = (k) => {
  const r = spec.repos[k];
  if (!r) throw new Error(`claims.json: no repo entry "${k}"`);
  return r;
};
const cacheKey = (r, path) =>
  `${r.github.replace('/', '__')}__${r.ref.slice(0, 12)}__${path.replace(/[^\w.]/g, '_')}`;

// ── a claim about a file's SIZE does not need the file. The two ONNX weights
//    are 90 MB and 23 MB; downloading 113 MB on every CI run to type `wc -c` is
//    the kind of cost that eventually gets a gate switched off. The contents
//    API reports the byte length of the blob at that exact SHA.
function bytes(repoKey, path) {
  const r = repo(repoKey);
  const dest = join(CACHE, cacheKey(r, path) + '.size');
  if (existsSync(dest)) return readFileSync(dest, 'utf8').trim();
  if (OFFLINE) throw new Error(`--offline and the size of ${path} is not cached`);
  const url = `https://api.github.com/repos/${r.github}/contents/${path}?ref=${r.ref}`;
  const args = ['-fsSL', '--max-time', '60', '-H', 'Accept: application/vnd.github+json'];
  if (process.env.GITHUB_TOKEN) args.push('-H', `Authorization: Bearer ${process.env.GITHUB_TOKEN}`);
  const size = String(JSON.parse(execFileSync('curl', [...args, url], { encoding: 'utf8' })).size);
  writeFileSync(dest, size);
  return size;
}

// ── some claims are about a WHOLE REPOSITORY rather than one file, and those
//    are the claims a per-blob fetch structurally cannot make. "Nothing
//    constructs this class" is a statement about every file at once: check it
//    against three named blobs and you have proved nothing about the fourth.
//    The tarball endpoint serves the entire tree at an immutable SHA in one
//    request, so the claim stays pinned and a reader can reproduce it.
//
//    Rows using this MUST NOT be expected-zero. A `grep | wc -l` that must
//    print 0 also prints 0 when the pattern is typo'd, when the escaping is
//    wrong, or when the file extension filter excludes the very files that
//    would have matched — it passes hardest exactly when it is most broken.
//    That is the "check that cannot fail" defect wearing a new uniform, and
//    this repository has already shipped four of those. So an absence is
//    always stated as a positive count with an enumerated expectation, or
//    paired with a positive control in the same extractor: if the pattern
//    engine is working, the control is non-zero, and the row fails in BOTH
//    directions rather than only the flattering one.
function tree(repoKey) {
  const r = repo(repoKey);
  const dest = join(CACHE, `${r.github.replace('/', '__')}__${r.ref.slice(0, 12)}__tree`);
  if (existsSync(dest)) return dest;
  if (OFFLINE) throw new Error(`--offline and the tree for ${repoKey} is not cached`);
  const tar = `${dest}.tar.gz`;
  const args = ['-fsSL', '--max-time', '300'];
  if (process.env.GITHUB_TOKEN) args.push('-H', `Authorization: Bearer ${process.env.GITHUB_TOKEN}`);
  execFileSync('curl', [...args, `https://api.github.com/repos/${r.github}/tarball/${r.ref}`, '-o', tar]);
  mkdirSync(dest, { recursive: true });
  execFileSync('tar', ['-xzf', tar, '-C', dest, '--strip-components', '1']);
  return dest;
}

// ── some claims are about the DEPLOYED artifact, not a committed one. "the
//    live page fetches /wasm/fast_mnist.wasm, 46,960 bytes" is checkable by
//    anyone with curl, and it SHOULD break if the deployment changes — that is
//    the claim. Not cached: a stale cache would defeat the point.
function live(url, header, digest) {
  // ── WHY A ROW MAY NOW ASK FOR THE BODY, NOT A HEADER
  //
  // §III prints a sha256 and dares the reader to `curl … | shasum -a 256`. Until
  // now the gate could not run that dare: it hashed the REPO blob and separately
  // read the DEPLOYMENT's content-length, two different sources, so a
  // same-length different-bytes deploy passed both halves green. That is not
  // hypothetical — on 2026-08-08 the deployment rebuilt, content-length went red
  // and the hash stayed green against the repo. `digest` closes it by hashing
  // what the host actually serves, which is the only thing the sentence claims.
  // ── WHY THIS IS NOT A PLAIN curl ANY MORE
  //
  // This is the only claim on the page about a DEPLOYED artifact rather than a
  // committed one: README section II gives a sha256 and tells the reader to
  // curl it. That is worth keeping and worth keeping uncached in the place that
  // matters. But as written it had two faults that have nothing to do with the
  // claim being right.
  //
  // 1. It ran on EVERY local `npm test`. The suite gets run dozens of times in
  //    a working session, so a third party absorbed dozens of requests a day
  //    for a value that changes when a deployment changes — which is rarely.
  // 2. ONE transient response failed the build. That happened: getglyph
  //    answered 403 on three consecutive attempts and 200 twenty minutes later.
  //    Deployment protection was verified OFF and 40 rapid requests all
  //    returned 200, so it was not protection and not rate limiting; the only
  //    production deploy in three days landed in that window. Transient.
  //
  // So: retry before believing a failure, and cache LOCALLY ONLY. CI never
  // reads the cache, so the authority on drift is unchanged — the page is
  // still checked against the real deployment on every push and every PR. What
  // goes away is a laptop hammering someone else's host to re-learn a number
  // it already knows.
  const FRESH = !!process.env.CI || process.argv.includes('--fresh');
  const TTL = 12 * 60 * 60 * 1000;
  const key = join(CACHE, 'live__' + `${url}__${header}__${digest || ''}`.replace(/[^\w.]/g, '_'));

  if (!FRESH && existsSync(key) && Date.now() - statSync(key).mtimeMs < TTL)
    return readFileSync(key, 'utf8').trim();

  const attempt = () => {
    const status = execFileSync('curl', ['-sS', '-o', '/dev/null', '-w', '%{http_code}',
                                         '--max-time', '60', url], { encoding: 'utf8' }).trim();
    if (!/^2\d\d$/.test(status)) {
      const why = status === '403' ? 'access is being refused'
                : status === '404' ? 'the path is gone from the deployment'
                : `the host answered ${status}`;
      throw new Error(`${url} returns ${status} — ${why}`);
    }
    if (digest) {
      // The reader's own command, run verbatim. Piped in one shell so the body
      // is never written to disk and cannot be confused with a repo blob.
      return execFileSync('bash', ['-c',
        `curl -fsS --max-time 60 ${JSON.stringify(url)} | shasum -a ${digest === 'sha256' ? 256 : 1} | cut -d' ' -f1`],
        { encoding: 'utf8' }).trim();
    }
    const out = execFileSync('curl', ['-fsSI', '--max-time', '60', url], { encoding: 'utf8' });
    const m = out.match(new RegExp(`^${header}:\\s*(.+)$`, 'im'));
    return m ? m[1].trim() : '';
  };

  let last;
  for (let i = 0; i < 3; i++) {
    try {
      const v = attempt();
      try { writeFileSync(key, v); } catch { /* cache is an optimisation, never a requirement */ }
      return v;
    } catch (e) {
      last = e;
      if (i < 2) execFileSync('sleep', [String(2 ** i * 5)]);   // 5s, then 10s
    }
  }

  // MEASURED, not assumed: 40 rapid requests to this host all returned 200 and
  // then every subsequent request — including the site root — returned 403,
  // while a different Vercel project on the same account stayed 200. So Vercel
  // rate-limits per IP per project, the limit trips AFTER the burst, and the
  // cooldown outlasts any retry window worth having in a test suite.
  //
  // Which means a developer can put their own laptop in the penalty box by
  // running the suite too often, and then the gate reports a page defect that
  // is really a self-inflicted throttle. That is a false alarm, and false
  // alarms are how a red build stops meaning anything.
  //
  // So locally, a previously-verified value wins over an unreachable host: the
  // check says what it could not do and moves on. In CI it still fails, and CI
  // is the authority — it runs from a fresh address every time, so it cannot
  // trip the limit this way, and it never reads the cache.
  if (!FRESH && existsSync(key)) {
    const cached = readFileSync(key, 'utf8').trim();
    notes.push(`${url} could not be reached (${last.message.split(' — ')[1] || 'unknown'}); `
             + `used the value last verified ${Math.round((Date.now() - statSync(key).mtimeMs) / 6e4)} `
             + `minutes ago. CI checks this against the live deployment and does not use this cache.`);
    return cached;
  }
  throw new Error(`${last.message}, three times over ~15s. The page tells a reader to verify this `
                + `artifact with curl, so right now that instruction does not work for them either.`);
}

// ── 1. every registered claim must re-derive from its pinned blob
let derived = 0;
for (const c of spec.claims) {
  if (!c.extractor) { notes.push(`${c.id}: no extractor — ${c.unpinned || 'unexplained'}`); continue; }
  let out;
  try {
    // A row names one path, several paths (a count that lives across files), or
    // asks for a byte length. $BLOB / $BLOBS / $BYTES, whichever it declared.
    const env = { ...process.env };
    if (c.live) env.HEADER = live(c.live, c.header, c.digest);
    else if (c.tree) env.TREE = tree(c.repo);
    else if (c.bytes) env.BYTES = bytes(c.repo, c.path);
    else if (c.paths) env.BLOBS = c.paths.map(p => blob(c.repo, p)).join(' ');
    else env.BLOB = blob(c.repo, c.path);
    out = execFileSync('bash', ['-c', c.extractor], {
      env, encoding: 'utf8', maxBuffer: 1 << 28,
    }).trim();
  } catch (e) {
    fails.push(`${c.id}: extractor failed — ${String(e.message).split('\n')[0]}`);
    continue;
  }
  if (out !== String(c.value)) {
    if (c.live) { fails.push(`${c.id}: the page says "${c.value}", ${c.live} serves "${out}"`); continue; }
    const r = repo(c.repo), where = c.path || (c.paths || []).join(',');
    fails.push(`${c.id}: the page says "${c.value}", ${r.github}@${r.ref.slice(0, 7)}/${where} says "${out}"`);
    continue;
  }
  derived++;
  if (c.unpinned) notes.push(`${c.id}: ${c.unpinned}`);
}

// ── 2. drawn_on must be true. A row claiming the page shows a number the page
//       does not show is bookkeeping, not evidence.
// ── A CHARACTER REFERENCE IS TEXT, NOT A NUMBER.
//
// The plates write typographic punctuation as numeric references — the
// apostrophe in "the JDK&#8217;s own Adler-32" is `&#8217;`. Stripping tags
// leaves the reference intact, so the sweep below read 8217 as a number the
// page draws and demanded a derivation for an apostrophe. Six files carried
// that phantom. Decoding happens AFTER the tags are stripped, never before:
// `&lt;` would otherwise become a `<` and invent a tag boundary nobody wrote,
// and the strip would then eat real text on its way to the next `>`.
const NAMED = { amp: '&', lt: '<', gt: '>', quot: '"', apos: "'", nbsp: ' ' };
const cp = (n, raw) =>
  Number.isFinite(n) && n >= 0 && n <= 0x10ffff ? String.fromCodePoint(n) : raw;
const decodeRefs = (s) => s
  .replace(/&#x([0-9a-fA-F]+);/g, (m, h) => cp(parseInt(h, 16), m))
  .replace(/&#(\d+);/g, (m, d) => cp(Number(d), m))
  // Named last, so a double-encoded `&amp;#8217;` decodes exactly one level and
  // does not quietly become an apostrophe the author never wrote.
  .replace(/&([a-zA-Z][a-zA-Z0-9]*);/g, (m, n) => NAMED[n.toLowerCase()] ?? m);

const fileText = new Map();
// Returns null — not a throw — when the file is not on disk. A drawn_on target
// that does not exist is PRECISELY the condition this gate exists to report: a
// plate was retired and a row still points at it. readFileSync threw ENOENT out
// of the entire process from here, so one retired filename took all 225 defects
// with it and the caller got a stack trace instead of a report. Every caller
// below records the absence as a defect and carries on.
const textOf = (f) => {
  if (fileText.has(f)) return fileText.get(f);
  const p = join(f.endsWith('.svg') ? ASSETS : ROOT, f);
  if (!existsSync(p)) { fileText.set(f, null); return null; }
  const raw = readFileSync(p, 'utf8');
  // Tags become a SPACE, not nothing. Deleting them butts adjacent <text> runs
  // together and invents numbers that nobody drew: "n=10,000" followed by
  // "299 wrong" read as the single token 10000299, and the coverage check below
  // then demanded evidence for it.
  const stripped = f.endsWith('.svg')
    ? raw.replace(/<style[\s\S]*?<\/style>/g, ' ')
         .replace(/<(?:title|desc)>[\s\S]*?<\/(?:title|desc)>/g, ' ')
         .replace(/<[^>]*>/g, ' ')
    : raw;
  const t = decodeRefs(stripped).replace(/,/g, '');
  fileText.set(f, t);
  return t;
};
// A NUMBER must appear as a whole token. String.includes was vacuous for every
// single-digit value: "7".includes-test is satisfied by "97.01", so a row
// claiming the page draws 7 was validated by a 7 buried inside an unrelated
// number. That is how "IDOR: 7" could be falsified to "IDOR: 79" and ship
// green. Words stay on substring, case-insensitively, because a row whose
// value is "rules" is drawn as "RULES LAYER ONLY".
const isNum = (v) => /^\d+(\.\d+)?$/.test(String(v));
const WORDOF = {};   // digit -> the word a plate might draw it as
// The contentious counts on this page are SPELLED OUT -- seven tenant tables,
// four parsers, five system cards, a three-layer cascade -- and a sweep that
// only matches \d audited none of them. "all seven tenant tables" could be
// changed to "all nineteen" and ship green. one/two are deliberately excluded:
// in this prose they are far more often articles than counts.
const WORDNUM = { three: 3, four: 4, five: 5, six: 6, seven: 7, eight: 8, nine: 9,
  ten: 10, eleven: 11, twelve: 12, thirteen: 13, fourteen: 14, fifteen: 15,
  sixteen: 16, seventeen: 17, eighteen: 18, nineteen: 19, twenty: 20,
  thirty: 30, forty: 40, fifty: 50, sixty: 60, seventy: 70, eighty: 80,
  ninety: 90, hundred: 100, thousand: 1000, dozen: 12 };
for (const [w, n] of Object.entries(WORDNUM)) if (!(n in WORDOF)) WORDOF[String(n)] = w;
const drawsToken = (text, v) => {
  if (!isNum(v)) return text.toLowerCase().includes(String(v).toLowerCase());
  const asDigits = new RegExp(`(?<![\\d.])${String(v).replace('.', '\\.')}(?!\\d)(?!\\.\\d)`);
  if (asDigits.test(text)) return true;
  // a plate may draw the number as a word — "IDOR IN SIX SERVICES"
  const w = WORDOF[String(v)];
  return w ? new RegExp(`\\b${w}\\b`, 'i').test(text) : false;
};
for (const c of [...spec.claims, ...spec.unpinnable, ...spec.external, ...(spec.attested || [])]) {
  for (const f of c.drawn_on || []) {
    const text = textOf(f);
    if (text === null) {
      fails.push(`${c.id}: drawn_on lists ${f}, which is not on disk — a row cannot be evidence `
               + `that the page draws "${c.value}" somewhere that does not exist (a retired plate, `
               + `or a rename this row never followed)`);
      continue;
    }
    if (!drawsToken(text, c.value))
      fails.push(`${c.id}: drawn_on lists ${f}, but "${c.value}" does not appear there as a whole number`);
  }
}

// ── 3. coverage — the half that makes this a gate. Every number a plate draws
//       must be a registered claim or a named exemption.
// Scoped per file, via drawn_on. A GLOBAL set of known values is the very
// thing this file's own header warns against for exemptions -- it would "wave
// through an unsourced 6 anywhere in the document" -- and the coverage check
// was built on exactly that principle. Demonstrated: plate III's hosting cap
// could be changed from 12 to 10 and pass, validated by jetpack's laptop core
// count; plate V's IDOR figure could be changed to 79 and pass, validated by
// Glyph's confident-error count.
const knownIn = new Map();
for (const c of [...spec.claims, ...spec.unpinnable, ...spec.external])
  for (const f of c.drawn_on || []) {
    // A claim that ANCHORS its occurrences in a file does not also contribute
    // its value to that file's permitted-value pool. Otherwise anchoring would
    // be additive only: the phrase would be pinned and every OTHER occurrence
    // of the same number would still ride free on the row. Pinning an
    // occurrence means the row accounts for that occurrence and no other.
    if (c.anchors && c.anchors[f]) continue;
    if (!knownIn.has(f)) knownIn.set(f, new Set());
    knownIn.get(f).add(String(c.value));
  }
const known = (f) => knownIn.get(f) || knownIn.get(unthemed(f)) || new Set();
// Attested facts count for coverage but never for the derived total. They are
// the author's word; the page says so where it draws them.
for (const a of spec.attested || [])
  for (const f of a.drawn_on || []) {
    if (a.anchors && a.anchors[f]) continue;      // same rule as the derived rows
    if (!knownIn.has(f)) knownIn.set(f, new Set());
    knownIn.get(f).add(String(a.value));
  }
// An exemption is either global ("880": the viewBox) or scoped to one plate
// ("plate-2-jetpack.svg:6"). Scoped is strongly preferred: exempting a bare "6"
// everywhere would let a future unsourced 6 onto any plate in the document.
const exempt = new Set(Object.keys(spec.exempt).filter(k => k !== '$comment'));
// README.md is swept alongside the plates. It was not, for a whole round: the
// coverage check read assets/ only, so roughly a dozen numbers that appear ONLY
// in the prose — a byte count, cited line numbers, a confidence interval — were
// never audited by the gate whose entire purpose is that no number goes
// unaudited. Link targets are stripped first; a URL is an address, not a claim.
// GitHub's light theme is the DEFAULT, so assets/light/ is the set MOST readers
// see — and until now this sweep read the top level only. `grep -c 'light/'
// claims.json` returned 0: half the shipped document was uncovered. Changing 44
// to 88 in a light plate passed this gate.
//
// gate.mjs check 9 caught those two by accident, because both numbers also
// appear in the plate's <desc>. It cannot catch a light-plate number that is
// not in the desc — "1.52 GB/s", "3 JMH FORKS", "11E60398" — and those were
// audited in the dark set and by nothing at all in the light one.
//
// The light plate draws the same numbers as its dark twin by construction, so
// it inherits the twin's registrations rather than duplicating every row.
// REQUIRED, not conditional. The `: []` this replaced meant a missing directory
// dropped every light plate out of SWEPT in silence — so the coverage half of
// this gate, the one that rejects a number nothing accounts for, would have
// swept the dark set only and passed. The comment directly above says the light
// plates were "audited by nothing at all"; that was fixed by adding them to the
// sweep and then made conditional on a directory in the same breath.
const lightDir = join(ASSETS, 'light');
if (!existsSync(lightDir)) {
  console.log(`\nCLAIMS GATE FAILED — ${lightDir} does not exist, so half the published `
    + `plates are outside the sweep and no number drawn on them is accounted for.`);
  process.exit(1);
}
const LIGHT = readdirSync(lightDir).filter(f => /^(plate|m)-.*\.svg$/.test(f)).sort()
  .map(f => `light/${f}`);
const SWEPT = [...readdirSync(ASSETS).filter(f => /^(plate|m)-.*\.svg$/.test(f)).sort(), ...LIGHT, 'README.md'];
const unthemed = (f) => f.replace(/^light\//, '');
const numsOf = (f) => {
  // In README.md, three things are addresses rather than assertions: HTML
  // attributes (plate-0-thesis.svg, width="100%", the srcset), markdown link
  // targets, and bare URLs. Sweeping them demanded evidence for the "0" in a
  // filename.
  //
  // A previous version of this comment claimed alt text survives the strip
  // "because every alt is the plate's own <desc>, and the plates are swept in
  // the same pass". That was wrong about this file's own behaviour: the plate
  // sweep strips <title> and <desc> too, so NO alt-text number is audited here.
  // It is not a live hole — plates.py fails the build if a README alt drifts
  // from its plate's <desc>, and gate.mjs check 9 fails if a <desc> names a
  // number the plate does not draw, so a falsified alt is caught twice
  // upstream. But this gate advertises that no number goes unaudited, and the
  // honest statement is that it audits the drawn text and leans on two other
  // checks for the accessible copy.
  const src = sweepText(f) ?? textOf(f);
  if (src === null) return new Set();   // reported once, below, not per call
  const t = f === 'README.md'
    ? src.replace(/<[^>]*>/g, ' ').replace(/\]\([^)]*\)/g, ' ').replace(/https?:\/\/\S+/g, ' ')
    : src;
  const out = new Set(t.match(/\d+\.\d+|\b\d+\b/g) || []);
  for (const [w, n] of Object.entries(WORDNUM))
    if (new RegExp(`\\b${w}\\b`, 'i').test(t)) out.add(String(n));
  return out;
};
// ── ANCHORS. Coverage above is a per-file SET of permitted values, and for a
//    plate carrying five to ten numbers that is close to exact. For README.md
//    it is close to vacuous: ~79 values are permitted, and WORDNUM folds
//    three/seven/ten into the same tokens, so ANY registered value legitimises
//    EVERY other occurrence of that value anywhere in the file. An audit
//    demonstrated six live falsifications that shipped green, including the
//    headline claim of section VI:
//
//      "on all **seven** tenant tables"  ->  "ten"     licensed by jetpack.cores = 10
//      "a 3-fork JMH run"                ->  "10-fork" licensed by jetpack.cores = 10
//      "I led a three-person team"       ->  "twelve"  licensed by applied.eval_per_class = 12
//
//    A row may now pin its occurrence rather than its value: `anchors` lists
//    exact strings that must appear verbatim in a file. Each is verified and
//    then MASKED OUT before the value sweep, so the numbers inside it are
//    accounted for by that claim and by nothing else. Change a digit or a
//    numeral word inside an anchored phrase and the anchor stops matching.
const masked = new Map();
for (const c of [...spec.claims, ...(spec.attested || [])]) {
  for (const [file, list] of Object.entries(c.anchors || {})) {
    let text = masked.has(file) ? masked.get(file) : textOf(file);
    if (text === null) {
      fails.push(`${c.id}: anchors into ${file}, which is not on disk — the sentence this row `
               + `pins cannot be checked, so the occurrence it claims to account for is unaccounted`);
      continue;
    }
    for (const anchor of list) {
      if (!text.includes(anchor)) {
        fails.push(`${c.id}: anchor ${JSON.stringify(anchor)} no longer appears in ${file} `
                 + `— the sentence it pins was edited, so the value is no longer where the row says it is`);
        continue;
      }
      if (!drawsToken(anchor, c.value))
        fails.push(`${c.id}: anchor ${JSON.stringify(anchor)} does not contain the value "${c.value}"`);
      text = text.split(anchor).join(' '.repeat(anchor.length));
    }
    masked.set(file, text);
  }
}
const sweepText = (f) => masked.has(f) ? masked.get(f) : null;

// numsOf yields nothing for a file it cannot read, and SWEPT's plates come from
// readdirSync, so the only member that can go missing is the prose. Said once
// here rather than per call: a silently empty sweep of README.md is the
// coverage half of this gate passing because it read nothing.
if (textOf('README.md') === null)
  fails.push('README.md is not on disk, so every number in the prose is outside this sweep');
for (const file of SWEPT) {
  for (const n of numsOf(file)) {
    if (known(file).has(n) || exempt.has(n)
        || exempt.has(`${file}:${n}`) || exempt.has(`${unthemed(file)}:${n}`)) continue;
    fails.push(`${file}: draws "${n}", which claims.json neither derives nor exempts`);
  }
}
// An exemption nobody uses is a stale excuse. Fail on it, the same way an
// unreachable gate branch is a defect rather than a nicety.
const usedExempt = new Set();
for (const file of SWEPT) {
  for (const n of numsOf(file)) {
    if (exempt.has(`${file}:${n}`)) usedExempt.add(`${file}:${n}`);
    else if (exempt.has(`${unthemed(file)}:${n}`)) usedExempt.add(`${unthemed(file)}:${n}`);
    else if (exempt.has(n) && !known(file).has(n)) usedExempt.add(n);
  }
}
for (const k of exempt)
  if (!usedExempt.has(k)) fails.push(`claims.json exempts "${k}", which no plate draws — stale exemption`);

// ── how old is the evidence?
//
// A pin cannot drift — that is the point of pinning. But a pin that has fallen
// a long way behind its branch means the page is describing a state of the
// repository that no longer exists, and nothing here would ever say so. This
// does not fail the build: citing an older commit is legitimate, and a claim
// verified against a specific SHA stays verified. It just refuses to let the
// distance go unmentioned.
if (!OFFLINE && !process.env.CLAIMS_SKIP_FRESHNESS) {
  for (const [key, r] of Object.entries(spec.repos)) {
    try {
      const args = ['-fsSL', '--max-time', '20', '-H', 'Accept: application/vnd.github+json'];
      if (process.env.GITHUB_TOKEN) args.push('-H', `Authorization: Bearer ${process.env.GITHUB_TOKEN}`);
      // `per_page=1` bounds the commits array, which is most of the payload and
      // none of the answer — this reads two integers off the top of the object.
      // It does NOT bound `files`: GitHub returns those up to its own cap
      // regardless, which is why the buffer below is still needed.
      const url = `https://api.github.com/repos/${r.github}/compare/${r.ref}`
        + `...${encodeURIComponent(r.branch)}?per_page=1`;
      // execFileSync's default maxBuffer is 1 MiB, and applied's compare is
      // 1.59 MB of file patches — so this threw ENOBUFS, the catch below ate it,
      // and the freshness note for that repo had NEVER printed. It is pinned 65
      // commits behind main. The size scales with the diff, so every repo here
      // acquires this failure as it grows, silently, one at a time.
      const cmp = JSON.parse(execFileSync('curl', [...args, url],
        { encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 }));
      if (cmp.ahead_by > 0)
        notes.push(`${key} is pinned ${cmp.ahead_by} commit(s) behind ${r.branch} — still verified, but the page is citing an older ${r.github}`);
    } catch {
      // Freshness is a courtesy and still does not fail the build. But this
      // catch used to swallow the failure whole, so "up to date", "rate-limited"
      // and "the network is down" produced the same output — nothing — and a
      // courtesy that goes silent when it fails is indistinguishable from one
      // with good news. That is this repository's own definition of a check
      // that cannot fail, applied to something that was never meant to be a
      // check; the honest version says it could not answer.
      notes.push(`${key}: freshness UNKNOWN — the compare against ${r.branch} did not `
        + `answer (offline, rate-limited, or the ref has moved). No number is in doubt: `
        + `they are re-derived from ${r.ref}, which is pinned.`);
    }
  }
}

// ── report
for (const n of notes) console.log(`  note  ${n}`);
if ((spec.attested || []).length)
  console.log(`  attested  ${spec.attested.length} facts taken on the author's word `
            + `(${spec.attested[0].source}) — labelled ATTESTED where drawn, never counted as derived`);
for (const e of spec.external)
  console.log(`  external  ${e.id} = "${e.value}" — platform fact, cited to ${e.source}`);
// A row here would be a number the page draws and nobody can check. There are
// none, and the empty list is load-bearing: the one entry this list ever held
// turned out to be a FALSE number wearing an "unverifiable" excuse, so the
// gate fails rather than printing a note about it.
for (const u of spec.unpinnable)
  fails.push(`${u.id} = "${u.value}" is drawn but cannot be derived — remove it from the page or make its source public`);

if (fails.length) {
  console.log(`\nCLAIMS GATE FAILED — ${fails.length} defects:`);
  for (const f of fails) console.log(`  · ${f}`);
  process.exit(1);
}
// Two provenances, said apart. Reporting one total "re-derived from pinned
// commits" was the same overstatement the colophon used to draw: the rows that
// curl the LIVE deployment are not derived from frozen history, and they are
// the ones that would catch a deployment drifting from its pin.
const liveN = spec.claims.filter(c => "live" in c).length;
console.log(`\nCLAIMS GATE PASSED — ${derived} numbers accounted for: ${derived - liveN} re-derived from pinned commits, ${liveN} checked against the live deployment.`);
