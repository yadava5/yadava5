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
import { readFileSync, readdirSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const ASSETS = join(ROOT, 'assets');
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

// ── some claims are about the DEPLOYED artifact, not a committed one. "the
//    live page fetches /wasm/fast_mnist.wasm, 46,960 bytes" is checkable by
//    anyone with curl, and it SHOULD break if the deployment changes — that is
//    the claim. Not cached: a stale cache would defeat the point.
function live(url, header) {
  const out = execFileSync('curl', ['-fsSI', '--max-time', '60', url], { encoding: 'utf8' });
  const m = out.match(new RegExp(`^${header}:\\s*(.+)$`, 'im'));
  return m ? m[1].trim() : '';
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
    if (c.live) env.HEADER = live(c.live, c.header);
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
const fileText = new Map();
const textOf = (f) => {
  if (fileText.has(f)) return fileText.get(f);
  const raw = readFileSync(join(f.endsWith('.svg') ? ASSETS : ROOT, f), 'utf8');
  // Tags become a SPACE, not nothing. Deleting them butts adjacent <text> runs
  // together and invents numbers that nobody drew: "n=10,000" followed by
  // "299 wrong" read as the single token 10000299, and the coverage check below
  // then demanded evidence for it.
  const t = f.endsWith('.svg')
    ? raw.replace(/<style[\s\S]*?<\/style>/g, ' ')
         .replace(/<(?:title|desc)>[\s\S]*?<\/(?:title|desc)>/g, ' ')
         .replace(/<[^>]*>/g, ' ').replace(/,/g, '')
    : raw.replace(/,/g, '');
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
for (const c of [...spec.claims, ...spec.unpinnable, ...spec.external]) {
  for (const f of c.drawn_on || []) {
    if (!drawsToken(textOf(f), c.value))
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
    if (!knownIn.has(f)) knownIn.set(f, new Set());
    knownIn.get(f).add(String(c.value));
  }
const known = (f) => knownIn.get(f) || new Set();
// An exemption is either global ("880": the viewBox) or scoped to one plate
// ("plate-2-jetpack.svg:6"). Scoped is strongly preferred: exempting a bare "6"
// everywhere would let a future unsourced 6 onto any plate in the document.
const exempt = new Set(Object.keys(spec.exempt).filter(k => k !== '$comment'));
// README.md is swept alongside the plates. It was not, for a whole round: the
// coverage check read assets/ only, so roughly a dozen numbers that appear ONLY
// in the prose — a byte count, cited line numbers, a confidence interval — were
// never audited by the gate whose entire purpose is that no number goes
// unaudited. Link targets are stripped first; a URL is an address, not a claim.
const SWEPT = [...readdirSync(ASSETS).filter(f => /^(plate|m)-.*\.svg$/.test(f)).sort(), 'README.md'];
const numsOf = (f) => {
  // In README.md, three things are addresses rather than assertions: HTML
  // attributes (plate-0-thesis.svg, width="100%", the srcset), markdown link
  // targets, and bare URLs. Sweeping them demanded evidence for the "0" in a
  // filename. Alt text is not lost by stripping the tags — every alt is the
  // plate's own <desc>, and the plates are swept in the same pass.
  const t = f === 'README.md'
    ? textOf(f).replace(/<[^>]*>/g, ' ').replace(/\]\([^)]*\)/g, ' ').replace(/https?:\/\/\S+/g, ' ')
    : textOf(f);
  const out = new Set(t.match(/\d+\.\d+|\b\d+\b/g) || []);
  for (const [w, n] of Object.entries(WORDNUM))
    if (new RegExp(`\\b${w}\\b`, 'i').test(t)) out.add(String(n));
  return out;
};
for (const file of SWEPT) {
  for (const n of numsOf(file)) {
    if (known(file).has(n) || exempt.has(n) || exempt.has(`${file}:${n}`)) continue;
    fails.push(`${file}: draws "${n}", which claims.json neither derives nor exempts`);
  }
}
// An exemption nobody uses is a stale excuse. Fail on it, the same way an
// unreachable gate branch is a defect rather than a nicety.
const usedExempt = new Set();
for (const file of SWEPT) {
  for (const n of numsOf(file)) {
    if (exempt.has(`${file}:${n}`)) usedExempt.add(`${file}:${n}`);
    else if (exempt.has(n) && !known(file).has(n)) usedExempt.add(n);
  }
}
for (const k of exempt)
  if (!usedExempt.has(k)) fails.push(`claims.json exempts "${k}", which no plate draws — stale exemption`);

// ── report
for (const n of notes) console.log(`  note  ${n}`);
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
console.log(`\nCLAIMS GATE PASSED — ${derived} numbers re-derived from pinned commits; every number drawn is accounted for.`);
