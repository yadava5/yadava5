#!/usr/bin/env python3
"""
FALSIFIABLE — plate builder.

Every claim is followed by the mechanism that would catch it if it were a lie.

Design rules encoded here (each one is a finding, not a preference):
  * viewBox 880 wide, type column 150→730 — symmetric, 36% more legible at
    mobile than 1200
  * type scale 64 / 32 / 20 / 16 / 13, plus three named exceptions: the 34px
    serif on the thesis plate (the only serif, and the only voice that is not
    the machine's), the 26px .unit suffix that hangs off a hero, and plate
    III's 26px sentence specimen, which is set at the size a user would type.
    Ten sizes shipped while this comment claimed five; the mobile set is now
    on the same scale rather than 15/22/54.
  * everything sits on a 4u grid. NOT a uniform first baseline or bottom
    margin — an earlier version of this comment claimed 56 and 32 and the
    measured values were 19..56 and 27..36. Two 64px heroes set their own top
    margin, because a 84u-tall glyph box cannot start where a 21u label does.
  * opaque slab on every plate — refuses the light/dark problem entirely
  * a 4u accent bar at x=0, the same device the mobile plates already used;
    the old "rail" was two 26u stubs outside the type column, absent from two
    of eight plates, and legible on none
  * near-coprime loop lengths so plates never beat into a synchronised pulse
  * the finished frame is authored; animation supplies the START, never the end
    (share cards and static renderers capture frame zero)
  * nothing comes to rest on top of a label. The gate now samples 40 points
    across every loop and measures getBoundingClientRect, so this is enforced
    rather than hoped for.
  * long travels use cubic-bezier(.4,0,.2,1). The old expo-out covered 221u in
    a single 0.33s step — it read as a teleport, not as motion.
  * an element that MOVES fades out before its position resets, so the loop
    wrap is never a visible snap-back. Elements that only fade still reset in
    one frame; that is a blink, not a jump, and it is the cheaper trade.
  * no animated filters — one animated blur costs more than 4000 animated rects
"""
from __future__ import annotations
import base64, json, pathlib, re

# ── the grid, as constants rather than as eight independent judgement calls.
# Measured across the desktop set before this existed: first ink at 19, 23, 40
# and 56; rightmost ink 150, 164, 164.8 and 166 short of the canvas. So the
# document's right edge visibly wandered as you scrolled it, and its top margin
# had three values. L/R are the type column; TOP is the first baseline for a
# label row; HERO_GAP is the space between a 64px numeral and the label that
# explains it, which had been eyeballed at 8.2 on one plate and 23.1 on another.
L, R = 150, 730
TOP = 56
HERO_GAP = 16

# ── the canvas window.
# The type column is L..R = 580 units wide on an 880-unit canvas, so 34.1% of
# every plate was margin and ink covered 7.1% of the document. That 150 was
# chosen for one reason — legibility of a 16u label on a phone — and the phone
# is out of scope now, so the reason is gone and the emptiness is not.
#
# Rather than move several hundred coordinates, tighten the WINDOW: the viewBox
# starts at VB_X and is VB_W wide, so authored x=150 lands 64 from the left edge
# and authored x=730 lands 64 from the right. Every relative position, every
# travel distance and every collision is untouched.
#
# The second effect is the one that matters more. The plate scales to the width
# of GitHub's readme column either way, so a narrower canvas renders everything
# LARGER: a 16px label goes from ~17.8px to ~22px at a 980px column. The plates
# were not only empty, they were small.
VB_X, VB_W = 86, 708

# every plate's description is authored ONCE here and flows to three places:
# the SVG <desc>, the SVG aria-label, and the README's <img alt>. They diverged
# once already; the gate below now fails the build if the README drifts.
#
# Since <picture> allows exactly ONE alt for both the desktop and the mobile
# source, these strings describe the CLAIM rather than the picture — so the same
# sentence is true whichever image the browser actually chose.
ALT: dict[str, str] = {}

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT.parent / "assets"
OUT.mkdir(exist_ok=True)
FONT = base64.b64encode((ROOT / "mono-subset.woff2").read_bytes()).decode()

# The real product marks, extracted from each app's own logo and stripped to the
# mark alone — the card already sets the name in type, so the wordmark would say
# it twice, and the background tile would sit on a slab that is already the same
# near-black. Every stroke and fill is currentColor, so the card supplies the
# system's legend colour and the six marks read as one family rather than six
# pasted assets. Inlined, not linked: nothing external can load in this medium.
LOGOS = json.loads((ROOT / "logos.json").read_text())


def logo(name: str, x: float, y: float, size: float, colour: str) -> str:
    m = LOGOS[name]
    k = size / m["size"]
    return (f'<g transform="translate({x},{y}) scale({k:.4f})" '
            f'style="color:{colour}">{m["body"]}</g>')

W = 880
SLAB, EDGE = "#0A0A0B", "rgba(255,255,255,0.14)"
# Every structural line used to sit between 1.08:1 and 1.94:1 on the slab —
# WCAG 1.4.11 wants 3:1 for anything non-text that carries meaning. So the
# document was drawing its numbers at AAA and the mechanism behind them at
# roughly half the legibility floor, which is the exact inversion of its thesis.
RULE = "#5A606A"   # 3.06:1 — section rules
WIRE = "#6E737C"   # 4.05:1 — connectors, boundaries, brackets, box frames.
                   # Used at FULL opacity: a .45 alpha put it back under 2:1.
ROW = "#5A606A"    # 3.09:1 — tenant row fills. Was #3A424B at 1.92:1: eight
                   # near-invisible rectangles carrying the whole of plate V.
INK, INK2, INK3 = "#F7F8F8", "#8A8F98", "#767B84"   # 18.39:1 / 6.02:1 / 4.60:1
AMBER, LIME, EMERALD = "#F5A524", "#B8E62E", "#34D399"
CYAN, PINK, INDIGO = "#22D3EE", "#F472B6", "#818CF8"

# one colour per system, in the order the README presents them
LEGEND = [("GLYPH", AMBER), ("JETPACK", LIME), ("CADENCE", EMERALD),
          ("APPLIED", CYAN), ("LIFEQUEST", PINK), ("AUTOML", INDIGO)]

# single-stroke digits in a 120x160 box — the same pen Glyph's landing uses
DIGITS = [
    "M60 26C32 26 26 62 26 92C26 128 38 150 60 150C82 150 94 120 94 90C94 58 86 26 60 26Z",
    "M38 48L64 28L64 150", "M32 50C30 22 94 18 90 56C87 84 40 98 28 140L98 140",
    "M34 42C42 20 92 22 86 54C82 74 58 78 58 78C58 78 94 76 94 110C94 150 40 150 30 120",
    "M82 28L28 108L100 108M82 64L82 150",
    "M88 28L46 28L42 76C72 64 96 76 96 108C96 144 58 152 32 134",
    "M86 32C62 20 34 44 32 92C30 134 54 152 62 150C92 146 96 100 66 96C44 94 32 112 34 120",
    "M30 30L98 30L56 150",
    "M60 84C32 80 34 30 60 30C86 30 88 80 60 84C26 88 24 150 60 150C96 150 94 88 60 84Z",
    "M88 74C86 40 54 26 40 50C26 74 44 100 66 96C80 94 88 82 88 74C88 118 78 146 44 150",
]

# ── the pen, normalised.
# Every DIGITS path is authored inside a nominal 120x160 box, but the INK inside
# that box is a different width for every glyph: "1" spans x 38..64 and "4"
# spans 28..100. Drawing them all at translate(x,y) therefore left the 299-error
# grid with mark widths from 1.77u to 4.90u and gaps from 6.40u to 9.23u in a
# nominal 11.4u cell — a 44% jitter, which is the visible raggedness — and hung
# the hero "7" 34.5u to the right of the 150 column it was supposed to sit on.
#
# The fix is NOT to equalise widths: stretching "1" to the width of "0" would
# distort the letterforms. It is to measure each glyph's ink and place it
# deliberately — flush left for the hero, centred in its cell for the grid.
# Every command in DIGITS takes coordinate PAIRS (M, L, C, Z), so the even-index
# numbers are the x values.
def ink(d: str) -> tuple[float, float]:
    n = [float(v) for v in re.findall(r'-?\d+\.?\d*', d)]
    xs = n[0::2]
    return min(xs), max(xs)


def digit(d: str, x: float, y: float, scale: float, *, centre: float | None = None) -> str:
    """Place a glyph so its INK lands where you asked, not its bounding box."""
    x0, x1 = ink(d)
    dx = x - x0 * scale if centre is None else x + (centre - (x1 - x0) * scale) / 2 - x0 * scale
    return f'transform="translate({dx:.2f},{y:.2f}) scale({scale})"'


def rail(numeral: str, name: str) -> str:
    """The chapter rail: every plate names itself at the same right edge.

    This does two jobs. It pins the rightmost ink to R on all eight plates, and
    it makes the top-to-bottom sequence read as one numbered document rather
    than eight cards that happen to share a slab — the plates had no shared
    marker of where you were in the argument.
    """
    return (f'<text x="{R}" y="{TOP}" class="lbl" text-anchor="end">'
            f'<tspan fill="{INK}">{numeral}</tspan>  {name}</text>')


EASE = "cubic-bezier(.4,0,.2,1)"
# EASE is ease-IN-out: it accelerates first, then settles. That is right for a
# thing travelling somewhere, and wrong for a thing being STOPPED — plate V's
# comment claimed its query "decelerates into the boundary" while easing into it
# like a lift arriving. A refusal needs an arrest: nearly all the deceleration
# in the last fifth of the travel.
ARREST = "cubic-bezier(.05,.75,.1,1)"

# One curve did every job. A census of the 21 animation classes found
# cubic-bezier(.4,0,.2,1) on 16 of them — arrivals, impacts and ambient pulses
# all on the same symmetric ease-in-out — which is why the document had one
# gesture performed eight times. Motion carries meaning here or it is
# decoration, and three verbs need three curves.
ARRIVE  = "cubic-bezier(.16,1,.3,1)"      # expo-out: fast away, long settle
IMPACT  = "cubic-bezier(.34,1.56,.64,1)"  # overshoots slightly, then sets
BREATHE = "cubic-bezier(.37,0,.63,1)"     # symmetric sine, for ambient loops


def head(h: int, title: str, desc: str, key: str = "") -> str:
    if key:
        ALT[key] = desc
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="{VB_X} 0 {VB_W} {h}" width="{VB_W}" height="{h}" role="img" aria-label="{desc}">
<title>{title}</title><desc>{desc}</desc>
<style>
@font-face{{font-family:'M';src:url(data:font/woff2;base64,{FONT}) format('woff2')}}
text{{font-family:'M',ui-monospace,SFMono-Regular,Menlo,monospace}}
.hero{{font-size:64px;letter-spacing:-1.5px;fill:{INK};font-weight:600}}
.sub{{font-size:32px;letter-spacing:-0.5px;fill:{INK};font-weight:600}}
.unit{{font-size:26px;fill:{INK2}}}
.say{{font-size:20px;fill:{INK2}}}
.lbl{{font-size:16px;letter-spacing:1.6px;fill:{INK2}}}
.key{{font-size:16px;letter-spacing:1.6px;fill:{INK}}}
.fine{{font-size:13px;letter-spacing:0.6px;fill:{INK2}}}
.kick{{font-size:11px;letter-spacing:2.6px;fill:{INK3}}}
@media (prefers-reduced-motion: reduce){{*{{animation:none!important}}}}
"""


def slab(h: int, accent: str | None = None) -> str:
    # drawn at the viewBox origin, not the authoring origin, so the slab, its
    # border and the accent bar all sit on the visible edge
    s = (f'<rect x="{VB_X}" width="{VB_W}" height="{h}" rx="2" fill="{SLAB}"/>'
         f'<rect x="{VB_X+0.5}" y="0.5" width="{VB_W-1}" height="{h-1}" rx="2" fill="none" stroke="{EDGE}"/>')
    if accent:
        s += f'<rect x="{VB_X}" y="0" width="4" height="{h}" fill="{accent}"/>'
    return s


# ────────────────────────────────────────────────────────────── PLATE 0
def plate_thesis() -> str:
    """Identity and contact sheet.

    This plate used to open with a thesis about falsifiability and a colour
    legend. It was the most distinctive thing on the page and the wrong thing to
    lead with: a reader met a sentence about numbers catching lies before
    learning what any of this is. The proof is the payoff, not the premise, so
    it moved to the colophon and this became the answer to "who is this and what
    have they built" — legible in about eight seconds, after which everything
    below is optional depth.
    """
    H, LOOP, SET = 614, 11.3, 9.0
    s = [head(H, "Ayush Yadav — computer science graduate, Cincinnati OH",
              "Ayush Yadav, a computer science graduate in Cincinnati, Ohio, open to full-time "
              "engineering roles. Languages C++, TypeScript, Python, Java, Swift, Rust and "
              "SQL; systems work in SIMD, the Java Vector API, WebAssembly and OpenMP; "
              "machine learning with LangGraph, MCP, in-browser ONNX and SetFit; web and "
              "backend in React, Next.js, Tauri, SwiftUI, FastAPI and NestJS; infrastructure "
              "on GitHub Actions, Docker, Postgres, CodeQL and fuzzing. Below, the six "
              "systems this page documents: Glyph, jetpack, Cadence, Applied, LifeQuest and "
              "Agentic AutoML.", key="plate-0-thesis.svg")]
    s.append(f""".rule{{stroke-dasharray:1;animation:sweep {LOOP}s {EASE} infinite;animation-delay:{-SET}s}}
@keyframes sweep{{0%{{stroke-dashoffset:1}}18%,100%{{stroke-dashoffset:0}}}}
.sw{{transform-box:fill-box;transform-origin:center;animation:sw {LOOP}s {BREATHE} infinite}}
@keyframes sw{{0%{{transform:translateY(0) scale(1)}}10%{{transform:translateY(-7px) scale(1.06)}}
  24%{{transform:translateY(0) scale(1)}}
  40%{{transform:translateY(0) scale(1)}}50%{{transform:translateY(-7px) scale(1.06)}}
  64%{{transform:translateY(0) scale(1)}}
  76%{{transform:translateY(0) scale(1)}}86%{{transform:translateY(-7px) scale(1.06)}}
  98%,100%{{transform:translateY(0) scale(1)}}}}
.ser{{font-family:ui-serif,Georgia,'Times New Roman',serif;font-size:34px;fill:{INK}}}
</style>{slab(H, INK2)}""")

    s.append(f'<text x="{L}" y="{TOP}" class="key" style="letter-spacing:5px">AYUSH YADAV</text>')
    s.append(f'<text x="{R}" y="{TOP}" class="lbl" text-anchor="end">CS GRADUATE · CINCINNATI, OH</text>')
    s.append(f'<path class="rule" d="M{L} 88H{R}" pathLength="1" stroke="{WIRE}"/>')

    # the one serif voice in the document, saying what the work IS
    for i, ln in enumerate(["Systems, from SIMD kernels", "to the browser they run in."]):
        s.append(f'<text x="{L}" y="{132 + i*40}" class="ser">{ln}</text>')
    s.append(f'<text x="{L}" y="200" class="fine">Open to full-time software engineering roles · aesh.03.23@gmail.com</text>')

    # what he actually works in, grouped so it can be scanned rather than read
    SKILLS = [
        ("LANGUAGES", "C++ · TypeScript · Python · Java · Swift · Rust"),
        ("SYSTEMS",   "SIMD AVX-512 · Vector API · WebAssembly · OpenMP"),
        ("ML",        "LangGraph · MCP · in-browser ONNX · SetFit"),
        ("WEB",       "React · Next.js · Tauri · SwiftUI · FastAPI · NestJS"),
        ("INFRA",     "GitHub Actions · Docker · Postgres · CodeQL"),
    ]
    for i, (dom, items) in enumerate(SKILLS):
        y = 240 + i * 22
        s.append(f'<text x="{L}" y="{y}" class="kick">{dom}</text>')
        s.append(f'<text x="262" y="{y}" class="fine">{items}</text>')

    # the contact sheet: every system on the page, at a glance
    s.append(f'<path d="M{L} 366H{R}" stroke="{RULE}"/>')
    CARDS = [
        ("GLYPH",     "A neural net in C++",   "C++ · SIMD · WASM"),
        ("JETPACK",   "Parallel gzip",         "Java · Vector API"),
        ("CADENCE",   "NL calendar + tasks",   "TS · Postgres"),
        ("APPLIED",   "Inbox → job pipeline",  "Python · ONNX"),
        ("LIFEQUEST", "Routines as quests",    "Tauri · NestJS"),
        ("AUTOML",    "Dataset → model",       "LangGraph · Docker"),
    ]
    for i, (nm, what, stack) in enumerate(CARDS):
        col, row = i % 3, i // 3
        x, y = L + col * 197, 394 + row * 104
        c = LEGEND[i][1]
        s.append(f'<g class="sw" style="animation-delay:{round(-SET + i*0.12,3)}s">'
                 + logo(nm, x, y, 28, c) + '</g>')
        s.append(f'<text x="{x}" y="{y+50}" class="key">{nm}</text>')
        s.append(f'<text x="{x}" y="{y+68}" class="fine">{what}</text>')
        s.append(f'<text x="{x}" y="{y+84}" class="fine" style="fill:{INK3}">{stack}</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────── PLATE I — WORK
def plate_work() -> str:
    """A year of paid engineering, and a national competition.

    Neither appears in any repository a reader can clone — the Oracle logs, the
    Tableau inventory and the compliance dashboard belong to Miami University,
    and the DataFest data is a competition set. Every other number on this page
    is re-derived in CI from a pinned commit; these are the author's word, and
    the plate says so on its face rather than borrowing the warrant of the ones
    that are checked.
    """
    H, LOOP, SET, a = 566, 9.7, 6.8, INK2
    LOOP3 = round(LOOP / 3, 2)
    s = [head(H, "Experience: a year as ITSM Data Integration Intern at Miami University, and "
                 "team lead at DataFest 2026",
              "Experience. As ITSM Data Integration Intern at Miami University from June 2025 "
              "to May 2026: a Python pipeline turning 1.6 million Oracle Analytics query logs "
              "into a 57.8 million-row field-usage table; code compliance lifted from 0 to "
              "96.72 percent across a 61-project portfolio; and a 10,453-row master asset "
              "inventory consolidated from Tableau and Workday. At DataFest 2026, team lead "
              "of three: 90-day care utilisation modelled for 349 thousand patients at 0.90 "
              "holdout AUC, over 7.7 million encounters processed with DuckDB and Polars, "
              "preserving 99.6 percent of social-determinant linkage against 32 percent under "
              "a naive join. These figures are attested by the author rather than derived "
              "from a public repository.", key="plate-0b-work.svg")]
    s.append(f""".fill{{transform-box:fill-box;transform-origin:left center;animation:fill {LOOP3}s {BREATHE} infinite}}
@keyframes fill{{0%,6%{{transform:scaleX(.02)}}26%{{transform:scaleX(1)}}
  38%{{transform:scaleX(1)}}46%{{transform:scaleX(.86)}}56%{{transform:scaleX(1)}}
  68%{{transform:scaleX(1)}}76%{{transform:scaleX(.86)}}86%,100%{{transform:scaleX(1)}}}}
</style>{slab(H, a)}""")

    s.append(rail("I", "WORK"))
    s.append(f'<text x="{L}" y="{TOP}" class="kick">ITSM DATA INTEGRATION INTERN · MIAMI UNIVERSITY</text>')
    s.append(f'<text x="{L}" y="78" class="fine">Jun 2025 – May 2026</text>')

    ROWS = [
        ("57.8M",  "ROW FIELD-USAGE TABLE",     "from 1.6M Oracle Analytics query logs, 5 years"),
        ("96.72%", "CODE COMPLIANCE ACROSS 61 PROJECTS", "from 0 — a legacy Laravel reporter, refactored"),
        ("10,453", "ROW MASTER ASSET INVENTORY","Tableau and Workday consolidated, hash-deduped"),
    ]
    for i, (num, lab, det) in enumerate(ROWS):
        y = [128, 184, 264][i]
        s.append(f'<text x="{L}" y="{y}" class="sub">{num}</text>')
        s.append(f'<text x="330" y="{y-8}" class="lbl">{lab}</text>')
        s.append(f'<text x="330" y="{y+12}" class="fine">{det}</text>')
    # the compliance number is a fill, so draw it as one
    # track and fill are one composed object, so they live in a <g> — that also
    # lets the bar be thick enough to see. At 3u it was a hairline the eye
    # never caught: the plate measured 2% of samples showing real motion.
    s.append(f'<g><rect x="330" y="204" width="300" height="26" rx="3" fill="{RULE}"/>'
             f'<rect class="fill" x="330" y="204" width="300" height="26" rx="3" fill="{LIME}" '
             f'style="animation-delay:{-SET}s"/></g>')

    s.append(f'<path d="M{L} 330H{R}" stroke="{RULE}"/>')
    s.append(f'<text x="{L}" y="362" class="kick">DATAFEST 2026 · TEAM LEAD, 3-PERSON, NATIONAL ASA COMPETITION</text>')
    s.append(f'<text x="{L}" y="406" class="sub">0.90</text>')
    s.append(f'<text x="330" y="398" class="lbl">HOLDOUT AUC</text>')
    s.append(f'<text x="330" y="418" class="fine">90-day care utilisation for 349K patients</text>')
    # the linkage claim is a comparison, so draw the comparison
    s.append(f'<text x="{L}" y="470" class="sub">99.6%</text>')
    s.append(f'<text x="330" y="452" class="lbl">OF LINKAGE PRESERVED</text>')
    s.append(f'<text x="330" y="{"%d" % 508}" class="fine">7.7M encounters · DuckDB + Polars star schema</text>')
    for j, (frac, col, tag) in enumerate([(1.0, LIME, "star"), (0.321, AMBER, "32% naive")]):
        yy = 462 + j * 18
        s.append(f'<g><rect x="330" y="{yy}" width="300" height="12" rx="2" fill="{RULE}"/>'
                 f'<rect class="fill" x="330" y="{yy}" width="{300*frac:.0f}" height="12" rx="2" '
                 f'fill="{col}" style="animation-delay:{round(-SET + j*0.14,3)}s"/></g>')
        s.append(f'<text x="640" y="{yy+11}" class="fine">{tag}</text>')

    s.append(f'<text x="{L}" y="534" class="fine" style="fill:{INK3}">ATTESTED — not derivable from a public repo</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── PLATE I
def plate_glyph() -> str:
    H, LOOP, SET, a = 576, 9.1, 7.6, AMBER
    s = [head(H, "Glyph — 97.01%, and the 299 it gets wrong",
              "Glyph: a neural network written from scratch in C++ with hand-written AVX-512, "
              "AVX2 and NEON kernels, plus an autovectorised WebAssembly build. It scores 97.01 "
              "percent on the 10,000-image MNIST test set, which means 299 wrong — every one of "
              "them drawn as a grid of the labels it missed. 79 of those errors were made with "
              "over 0.9 confidence.", key="plate-1-glyph.svg")]
    s.append(f""".ink{{fill:none;stroke:{a};stroke-width:7;stroke-linecap:round;stroke-linejoin:round;
  stroke-dasharray:1;stroke-dashoffset:0;animation:draw {LOOP}s linear infinite;animation-delay:{-SET}s}}
@keyframes draw{{0%{{stroke-dashoffset:1}}17%{{stroke-dashoffset:0}}100%{{stroke-dashoffset:0}}}}
.tok{{animation:run {LOOP}s {ARRIVE} infinite}}
@keyframes run{{0%{{opacity:0;transform:translateX(-190px)}}5%{{opacity:1;transform:translateX(-190px)}}
  34%,96%{{opacity:1;transform:translateX(0)}}100%{{opacity:0;transform:translateX(0)}}}}
.wrong{{opacity:.78}}
.gr{{transform-box:fill-box;transform-origin:left center;animation:gr {LOOP}s {BREATHE} infinite}}
@keyframes gr{{0%,30%{{transform:translateY(0)}}38%{{transform:translateY(-5px)}}
  50%,100%{{transform:translateY(0)}}}}
</style>{slab(H, a)}""")

    # CLAIM — the seven, drawn by hand
    s.append(f'<text x="150" y="56" class="kick">THE 299 IT GETS WRONG</text>')
    s.append(f'<text x="330" y="80" class="kick">MECHANISM — 3 BY HAND, 1 AUTO</text>')
    s.append(rail("II", "GLYPH"))
    # 0.68 keeps the three glyphs clear of the mechanism column at x=330;
    # they end at 306. Each is placed by its own ink, not its nominal box.
    hx = 150
    for j, d in enumerate([DIGITS[2], DIGITS[9], DIGITS[9]]):
        s.append(f'<g {digit(d, hx, 104, 0.68)}>'
                 f'<path class="ink" d="{d}" pathLength="1" '
                 f'style="animation-delay:{round(-SET + j*0.15,3)}s"/></g>')
        x0, x1 = ink(d)
        hx += (x1 - x0) * 0.68 + 12

    # MECHANISM — four instruction sets, one answer
    for i, name in enumerate(["AVX-512", "AVX2", "NEON", "wasm (auto)"]):
        y = 120 + i * 34
        s.append(f'<text x="330" y="{y+5}" class="key">{name}</text>')
        s.append(f'<path d="M470 {y}H660" stroke="{WIRE}" stroke-width="1"/>')
        # A 4u ring with a 2.2/2 dash renders as roughly six disconnected dots
        # at 1:1 — it read as a broken glyph, not as "autovectorised". Hollow
        # against three filled is the same distinction and survives the scale.
        hand = i < 3
        s.append(f'<circle class="tok" data-rest="one-answer" data-rest-within="2" '
                 f'cx="660" cy="{y}" r="4" '
                 + (f'fill="{a}" ' if hand else f'fill="none" stroke="{a}" stroke-width="1.8" ')
                 + f'style="animation-delay:{round(-SET + i*0.12,3)}s"/>')
    # four instruction sets, one answer — so all four tokens must actually
    # arrive at the collector, not merely set off in its direction
    s.append(f'<path id="one-answer" d="M660 116V226" stroke="{WIRE}" stroke-width="1"/>')
    # It used to say "1 ANSWER", which asserts the four builds agree — and
    # nothing tests that. There is no cross-ISA equivalence test in the repo;
    # the prose two paragraphs down says so itself ("nothing cross-checks
    # them"). The plate was making the stronger claim the README declines to.
    s.append(f'<text x="330" y="256" class="lbl">4 BUILDS · 1 PATH COMPILED</text>')

    # VERDICT — the hero clears the rule by 16u; at 64px its box runs from
    # baseline-64 to baseline+19, which is 84u tall, not the 60 I first assumed.
    s.append(f'<path d="M150 312H730" stroke="{RULE}"/>')
    s.append(f'<text x="150" y="392" class="hero">97.01<tspan class="unit">%</tspan></text>')
    s.append(f'<text x="470" y="392" class="lbl">MNIST TEST · n=10,000</text>')
    s.append(f'<text x="150" y="436" class="say">299 wrong, drawn below. 79 above 0.9 conf.</text>')

    # THE MOVE — the REAL errors. Each mark is the true label of one image the
    # model got wrong, read from benchmarks/mnist_misclassified.csv in the Glyph
    # repo. Previously these were random glyphs; now the picture is the evidence.
    # 50 per row leaves 49 in the last of six rows. 46 per row left exactly half
    # a row hanging, which reads as a mistake rather than as the end of a list.
    errs = json.loads((ROOT / "errors.json").read_text())["true"]
    gx, gy, cols = 150, 468, 50
    for r in range((len(errs) + cols - 1) // cols):
        s.append(f'<g class="gr" style="animation-delay:{round(-SET + r*0.12,3)}s">')
        for i in range(r * cols, min((r + 1) * cols, len(errs))):
            x, y = gx + (i % cols) * 11.4, gy + r * 14.0
            s.append(f'<g class="wrong" {digit(DIGITS[errs[i]], x, y, 0.068, centre=10.4)}>'
                     f'<path d="{DIGITS[errs[i]]}" fill="none" stroke="{a}" stroke-width="15" '
                     f'stroke-linecap="round"/></g>')
        s.append('</g>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── PLATE II
def plate_jetpack() -> str:
    H, LOOP, SET, a = 537, 10.3, 7.2, LIME
    LOOP2 = round(LOOP / 2, 2)
    s = [head(H, "jetpack — 6.4x parallel, and the intrinsic it does not beat",
              "jetpack: parallel gzip on JDK 25 reaches 422 megabytes per second against 66.2 "
              "single-threaded, a 6.4 times speedup, with blocks held in a bounded in-flight "
              "window. Its hand-vectorised Adler-32 checksum runs at 4.26 gigabytes per second "
              "and is verified bit-identical against java.util.zip — whose own native intrinsic "
              "is faster still, at 14.06, and is printed here as the reference it loses to.",
              key="plate-2-jetpack.svg")]
    s.append(f""".blk{{animation:sq {LOOP}s {ARRIVE} infinite;transform-box:fill-box;transform-origin:left center}}
@keyframes sq{{0%{{opacity:0;transform:translateX(-88px) scaleX(1)}}
  5%,14%{{opacity:1;transform:translateX(-88px) scaleX(1)}}
  38%,60%{{opacity:1;transform:translateX(0) scaleX(1)}}
  /* the window breathes once the blocks are inside it: peak memory tracking
     the window is a continuous property, not a one-off arrival */
  52%{{opacity:1;transform:translateX(0) scaleX(.94)}}
  66%,78%{{opacity:1;transform:translateX(0) scaleX(1)}}
  86%{{opacity:1;transform:translateX(0) scaleX(.97)}}
  94%,96%{{opacity:1;transform:translateX(0) scaleX(1)}}
  100%{{opacity:0;transform:translateX(0) scaleX(1)}}}}
.wscan{{animation:wscan {LOOP2}s linear infinite}}
@keyframes wscan{{0%{{transform:translateY(0)}}100%{{transform:translateY(112px)}}}}
.mt{{transform-box:fill-box;transform-origin:left center;animation:mt {LOOP}s {ARRIVE} infinite}}
@keyframes mt{{0%,6%{{transform:scaleX(0);opacity:0}}11%{{opacity:1}}24%,100%{{transform:scaleX(1);opacity:1}}}}
.row{{animation:rw {LOOP}s {EASE} infinite}}
@keyframes rw{{0%,8%{{opacity:.86}}20%,100%{{opacity:1}}}}
</style>{slab(H, a)}""")
    s.append(f'<text x="330" y="80" class="lbl">PARALLEL vs SINGLE-THREAD GZIP</text>')
    s.append(rail("III", "JETPACK"))
    # NOT "CI ±5%": the 3-fork run's 99.9% intervals span ±0.7% to ±6.9%, so a
    # single figure would be a claim the committed JSON contradicts.
    s.append(f'<text x="330" y="104" class="lbl">JDK 25 · M1 PRO · 3 JMH FORKS</text>')
    s.append(f'<text x="150" y="108" class="hero">6.4<tspan class="unit">×</tspan></text>')
    s.append(f'<text x="150" y="152" class="kick">CLAIM</text>')

    # The bounded in-flight window. The bracket used to span 400→636 while the
    # compressed blocks came to rest at 410→518, leaving half the window
    # permanently void — it drew a window twice the size of the thing it bounds.
    s.append(f'<text x="400" y="160" class="kick">BOUNDED IN-FLIGHT WINDOW</text>')
    # the window used to span 400..540 while the compressed blocks came to rest
    # at 410..517.8 — 32.2u of permanent void, split unevenly 10 left / 22 right.
    # 404..524 puts 6u of air on each side of the thing it bounds.
    s.append(f'<path d="M174 152V268M174 152H194M174 268H194" stroke="{WIRE}" stroke-width="1"/>')
    s.append(f'<path d="M294 152V268M294 152H274M294 268H274" stroke="{WIRE}" stroke-width="1"/>')
    s.append(f'<rect class="wscan" x="176" y="153" width="116" height="2" fill="{a}" opacity=".55"/>')
    for i in range(4):
        y = 168 + i * 26
        s.append(f'<rect class="blk" data-max-x="294" x="180" y="{y}" width="107.8" height="16" rx="2" fill="{a}" '
                 f'style="animation-delay:{round(-SET + i*0.12,3)}s"/>')
    for j, ln in enumerate(["peak memory", "tracks the window,", "not the file"]):
        s.append(f'<text x="400" y="{194 + j*20}" class="fine">{ln}</text>')
    s.append(f'<text x="150" y="288" class="kick">MECHANISM — one virtual thread per block</text>')

    # checksum audit: the fast path checked against the reference
    s.append(f'<text x="150" y="328" class="lbl">SIMD ADLER-32</text>')
    s.append(f'<text x="150" y="352" class="lbl">java.util.zip</text>')
    # the known-answer vector the repo commits: Adler32Test.java:36-37
    # One string per row, not eight <text> elements at a 26u pitch against an
    # 11.2u advance — 132% tracking, which read as eight loose characters rather
    # than as a hex value. The match is now drawn as a rule that sweeps the
    # width of the two rows it is comparing.
    s.append(f'<text x="330" y="328" class="key">11E60398</text>')
    s.append(f'<text x="330" y="352" class="key">11E60398</text>')
    s.append(f'<rect class="mt" x="330" y="334" width="90" height="2" fill="{a}" style="animation-delay:{-SET}s"/>')
    s.append(f'<text x="556" y="344" class="lbl" style="fill:{a}">identical</text>')

    # the verdict — the measured table, including the reference he does NOT beat
    s.append(f'<path d="M150 376H730" stroke="{RULE}"/>')
    rows = [
        ("Adler-32 scalar (pure Java)", "1.52 GB/s", ""),
        ("Adler-32 hand-vectorised", "4.26 GB/s", "2.80×"),
        ("java.util.zip intrinsic", "14.06 GB/s", "not beaten"),
        ("gzip, one thread", "66.2 MB/s", ""),
        ("parallel virtual threads", "422 MB/s", "6.4×"),
    ]
    for i, (name, score, note) in enumerate(rows):
        y = 408 + i * 24
        dl = round(-SET + i * 0.12, 3)
        s.append(f'<text class="row lbl" x="150" y="{y}" style="animation-delay:{dl}s">{name}</text>')
        s.append(f'<text class="row key" x="470" y="{y}" style="animation-delay:{dl}s">{score}</text>')
        if note:
            fill = INK if note == "not beaten" else a
            s.append(f'<text class="row lbl" x="604" y="{y}" '
                     f'style="fill:{fill};animation-delay:{dl}s">{note}</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── PLATE III
def plate_cadence() -> str:
    H, LOOP, SET, a = 457, 7.9, 5.6, EMERALD
    SENT, FS, CW = "lunch with sam friday 1pm", 26, 15.62
    s = [head(H, "Cadence — a parser that shows its work",
              "Cadence: the sentence 'lunch with sam friday 1pm' is labelled in place — title, "
              "attendee, day and time — and filed into the Friday 1pm slot of a week grid that "
              "names its hours. Its 36 API handlers are bundled into a single serverless "
              "function, because the hosting plan allows 12.", key="plate-3-cadence.svg")]
    s.append(f""".ul{{animation:ul {LOOP}s {EASE} infinite;transform-box:fill-box;transform-origin:left center}}
@keyframes ul{{0%,4%{{transform:scaleX(0);opacity:0}}8%{{opacity:1}}18%,100%{{transform:scaleX(1);opacity:1}}}}
.an{{animation:an {LOOP}s linear infinite}}
@keyframes an{{0%,6%{{opacity:0}}12%,100%{{opacity:1}}}}
.now{{animation:now {LOOP}s linear infinite}}
@keyframes now{{0%{{transform:translateY(0)}}100%{{transform:translateY(70px)}}}}
.fil{{transform-box:fill-box;transform-origin:center;animation:fil {LOOP}s {BREATHE} infinite}}
@keyframes fil{{0%,10%{{opacity:0;transform:scale(.94)}}16%{{opacity:1;transform:scale(1)}}
  40%{{transform:scale(1)}}48%{{transform:scale(1.05)}}58%,100%{{transform:scale(1);opacity:1}}}}
</style>{slab(H, a)}""")
    s.append(f'<text x="150" y="56" class="kick">CLAIM — plain English in, calendar out</text>')
    s.append(rail("IV", "CADENCE"))
    s.append(f'<text x="150" y="78" class="kick">MECHANISM — every span carries its parser</text>')
    s.append(f'<text x="150" y="116" font-size="{FS}" fill="{INK}" letter-spacing="0">{SENT}</text>')
    # Four passes annotating the SAME sentence in place — a linguist's gloss.
    # The labels used to stagger onto two rows to dodge a collision, which made
    # a reader scan them TITLE→DATE→ATTENDEE→TIME. Short labels fit one row, so
    # the reading order is the sentence order again.
    toks = [(0, 5, "TITLE"), (11, 3, "WHO"), (15, 6, "DAY"), (22, 3, "TIME")]
    for i, (start, ln, label) in enumerate(toks):
        x, w = 150 + start * CW, ln * CW
        dl = round(-SET + i * 0.12, 3)
        s.append(f'<rect class="ul" x="{x:.0f}" y="126" width="{w:.0f}" height="2" fill="{a}" '
                 f'style="animation-delay:{dl}s"/>')
        s.append(f'<text class="an lbl" x="{x:.0f}" y="152" '
                 f'style="fill:{a};animation-delay:{dl}s">{label}</text>')
    s.append(f'<text x="150" y="200" class="kick">FILED — into the hour it names</text>')

    # filed — a week grid with real hour rows, so it reads as a calendar
    s.append(f'<path d="M150 224H730" stroke="{RULE}"/>')
    # the hour gutter — right-aligned so it cannot drift into the type column
    for hy, hl in ((266, "12"), (290, "1pm"), (314, "2pm")):
        s.append(f'<text x="182" y="{hy}" class="fine" text-anchor="end">{hl}</text>')
    for d, day in enumerate(["MON", "TUE", "WED", "THU", "FRI"]):
        x = 196 + d * 108
        s.append(f'<text x="{x}" y="252" class="lbl">{day}</text>')
        s.append(f'<rect x="{x}" y="262" width="96" height="72" rx="3" fill="none" stroke="{WIRE}"/>')
        for hr in (286, 310):
            s.append(f'<path d="M{x} {hr}H{x+96}" stroke="{RULE}" stroke-width="1"/>')
    s.append(f'<rect class="now" x="110" y="263" width="528" height="2" fill="{a}" opacity=".62"/>')
    s.append(f'<g class="fil" style="animation-delay:{-SET}s">'
             f'<rect x="632" y="288" width="80" height="20" rx="3" fill="#0E2A22" stroke="{a}"/>'
             f'<text x="640" y="302" class="fine" style="fill:{a}">lunch</text></g>')
    s.append(f'<text x="150" y="410" class="hero">36</text>')
    s.append(f'<text x="232" y="394" class="lbl">HANDLERS IN ONE FUNCTION</text>')
    s.append(f'<text x="232" y="418" class="lbl">THE PLAN ALLOWS 12</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── PLATE IV
def plate_applied() -> str:
    H, LOOP, SET, a = 532, 11.7, 8.4, CYAN
    s = [head(H, "Applied — a classifier allowed to say it doesn't know",
              "Applied: a three-layer email classifier — 201 regex rules, then e5 embeddings, "
              "then a fine-tuned SetFit head, cheapest first. It scores 0.979 macro-F1 on a "
              "96-message evaluation set, measured with the rules layer alone; anything that "
              "fails to clear the 0.85 confidence gate is referred to a human rather than "
              "guessed at. Inference runs inside your browser.", key="plate-4-applied.svg")]
    s.append(f""".env{{animation:fall {LOOP}s {ARRIVE} infinite}}
@keyframes fall{{0%{{opacity:0;transform:translateY(-184px)}}5%{{opacity:1;transform:translateY(-184px)}}
  46%,96%{{opacity:1;transform:translateY(0)}}100%{{opacity:0;transform:translateY(0)}}}}
/* The corner used to be at translateY(212px) — 52u BELOW the gate, so the one
   message that is supposed to be refused crossed the gate first and turned
   underneath it. Nothing on the plate was ever stopped by anything. 140px puts
   its bottom edge exactly on y=288, where it is held before being referred. */
.ly{{stroke-dasharray:18 222;animation:ly {LOOP}s linear infinite}}
@keyframes ly{{0%{{stroke-dashoffset:240}}100%{{stroke-dashoffset:0}}}}
.div{{animation:dv {LOOP}s {ARRIVE} infinite}}
@keyframes dv{{0%{{opacity:0;transform:translate(-146px,-212px)}}5%{{opacity:1;transform:translate(-146px,-212px)}}
  /* stopped ON the gate, and visibly held there — that pause is the refusal */
  30%,44%{{opacity:1;transform:translate(-146px,-72px)}}
  /* then referred: down through the empty slot it left in the stack, and out
     to a person. It descends in its OWN column, so it never crosses a message
     still falling — routing it diagonally put it through slot 4 in flight. */
  56%{{opacity:1;transform:translate(-146px,0)}}
  68%,96%{{opacity:1;transform:translate(0,0)}}100%{{opacity:0;transform:translate(0,0)}}}}
</style>{slab(H, a)}""")
    # 0.979 is the number with artifacts behind it: five committed files carry
    # it. 0.9583 — the full cascade — survives in exactly one line of prose,
    # because the run that produced it was overwritten by the deterministic
    # re-run. So the hero is the number I can hand you, labelled for what it
    # actually measures, and the gap is stated rather than papered over.
    s.append(f'<text x="150" y="104" class="hero">0.979</text>')
    s.append(rail("V", "APPLIED"))
    s.append(f'<text x="400" y="80" class="lbl">MACRO-F1 · 96-MSG EVAL SET</text>')
    s.append(f'<text x="400" y="100" class="lbl" style="fill:{AMBER}">RULES LAYER ONLY</text>')
    s.append(f'<text x="400" y="118" class="fine">SetFit off, embeddings emptied</text>')

    for i, (label, y) in enumerate([("201 REGEX RULES", 160), ("e5 EMBEDDINGS", 200), ("SETFIT HEAD", 240)]):
        s.append(f'<text x="150" y="{y+5}" class="lbl">{label}</text>')
        s.append(f'<path d="M400 {y}H640" stroke="{WIRE}" stroke-width="1" stroke-dasharray="4 5"/>')
        # the lit layer, drawn over the dashed one as the messages arrive
        s.append(f'<path class="ly" d="M400 {y}H640" stroke="{a}" stroke-width="1.4" '
                 f'style="animation-delay:{round(-SET + i*0.18,3)}s"/>')
    # the gate that is allowed to decline
    s.append(f'<text x="150" y="293" class="lbl" style="fill:{a}">0.85 CONFIDENCE GATE</text>')
    s.append(f'<path d="M400 288H640" stroke="{a}" stroke-width="1"/>')
    s.append(f'<text x="150" y="316" class="fine">CI fails the build below 0.95</text>')

    for i in range(5):
        if i == 2:
            continue          # slot 2 belongs to the .div below — five messages, not six
        s.append(f'<rect class="env" x="{416 + i*44}" y="312" width="30" height="20" rx="2" fill="none" '
                 f'stroke="{a}" stroke-width="1.6" style="animation-delay:{round(-SET + i*0.14,3)}s"/>')
    # the one that does not clear the gate leaves the stack and goes sideways
    # the whole claim of this plate is that the one that fails the gate reaches
    # a PERSON. If it merely leaves the stack, the plate says nothing.
    s.append(f'<rect class="div" data-rest="the-human" data-rest-within="10" '
             f'x="650" y="340" width="30" height="20" rx="2" fill="none" '
             f'stroke="{AMBER}" stroke-width="1.6" style="animation-delay:{round(-SET + 0.2,3)}s"/>')
    s.append(f'<circle id="the-human" cx="700" cy="350" r="11" fill="none" stroke="{AMBER}" stroke-width="1.4"/>')
    s.append(f'<text x="{W-150}" y="318" class="lbl" style="fill:{AMBER}" text-anchor="end">A HUMAN</text>')
    # and the ones that DO clear the gate land on a name rather than in blank space
    s.append(f'<text x="150" y="356" class="lbl">CLASSIFIED</text>')
    s.append(f'<text x="150" y="400" class="say">It is allowed to say it doesn’t know.</text>')

    s.append(f'<path d="M150 424H730" stroke="{RULE}"/>')
    s.append(f'<rect x="150" y="436" width="580" height="68" rx="3" fill="none" stroke="{WIRE}"/>')
    s.append(f'<text x="166" y="460" class="lbl">YOUR BROWSER</text>')
    s.append(f'<text x="166" y="484" class="fine">int8 ONNX · 90.4 MB → 22.8 MB · nothing you paste leaves the tab</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── PLATE V
def plate_refusal() -> str:
    H, LOOP, SET, a = 453, 6.7, 4.7, EMERALD
    s = [head(H, "The refusal — the database declines to return another tenant's rows",
              "A query from one tenant travels toward another tenant's rows, reaches the "
              "PostgreSQL row-level-security boundary, and stops. Only the querying tenant's own "
              "rows come back — because the database refused, not because the application "
              "remembered to filter.", key="plate-5-refusal.svg")]
    # The travel used to be 80px, which left the dot's right edge at 415 — five
    # units short of a boundary it is supposed to be stopped BY, for 66% of the
    # loop and at frame zero. A refusal that never touches the wall is a diagram
    # of a query losing interest. 104px lands the edge exactly on 439.
    s.append(f""".q{{animation:seek {LOOP}s {IMPACT} infinite;animation-delay:{-SET}s}}
@keyframes seek{{0%{{opacity:0;transform:translateX(-104px)}}5%{{opacity:1;transform:translateX(-104px)}}
  /* contact at 28%, a 3u recoil, then it stays stopped. The recoil is the
     difference between "arrived here" and "was refused here". */
  28%{{opacity:1;transform:translateX(0)}}30%{{transform:translateX(-3px)}}
  32%,96%{{opacity:1;transform:translateX(0)}}100%{{opacity:0;transform:translateX(0)}}}}
/* The boundary reacts once, on contact. It cannot do this with opacity: an
   element that flashes is either dimmed at frame zero or below the 70% duty
   floor, and both are gate failures. So it flexes instead — always fully
   visible, at rest in the finished frame. */
.wall{{transform-box:fill-box;transform-origin:center;animation:wall {LOOP}s {IMPACT} infinite;animation-delay:{-SET}s}}
@keyframes wall{{0%,27%{{transform:scaleY(1)}}31%{{transform:scaleY(1.06)}}42%,100%{{transform:scaleY(1)}}}}
.zero{{animation:land {LOOP}s linear infinite;animation-delay:{-SET}s}}
@keyframes land{{0%,14%{{opacity:0}}22%,100%{{opacity:1}}}}
.ret{{transform-box:fill-box;transform-origin:left center;animation:ret {LOOP}s {EASE} infinite}}
@keyframes ret{{0%,34%{{transform:translateY(0)}}42%{{transform:translateY(-4px)}}
  56%,100%{{transform:translateY(0)}}}}
</style>{slab(H, a)}""")

    s.append(rail("VI", "THE REFUSAL"))
    s.append(f'<text x="150" y="80" class="lbl">TENANT B — THE CALLER</text>')
    s.append(f'<text x="560" y="80" class="lbl">TENANT A</text>')
    for i in range(4):
        y = 104 + i * 28
        # Both stacks are 170 wide. They were 160 and 170 — two things that must
        # read as symmetric peers, differing by 10u for no reason.
        # And they are no longer the same grey: B's rows are the ones that come
        # back, so they carry the accent. The plate said "B only" in 32px type
        # and drew eight identical rectangles.
        s.append(f'<rect class="ret" x="150" y="{y}" width="170" height="18" rx="2" fill="{ROW}" '
                 f'stroke="{a}" style="animation-delay:{round(-SET + i*0.18,3)}s"/>')
        s.append(f'<rect x="560" y="{y}" width="170" height="18" rx="2" fill="{ROW}" stroke="{WIRE}"/>')

    # The boundary now sits on the midpoint between the two stacks (320→560) and
    # is a 2u wall rather than a 1u hairline the reader cannot find.
    s.append(f'<rect class="wall" id="rls-boundary" x="439" y="92" width="2" height="132" fill="{WIRE}"/>')
    # data-rest is the caption, made checkable, and 2u means CONTACT. This plate
    # has already shipped inverted once — tenant A asking and B receiving — and
    # every geometric check passed it, because an inverted diagram is still a
    # well-formed diagram. A loose tolerance here would repeat that: the round-9
    # geometry stopped 5u short, so any allowance above 4 would have called the
    # defect this check exists to catch a pass.
    s.append(f'<circle class="q" data-rest="rls-boundary" data-rest-within="2" '
             f'cx="434" cy="113" r="5" fill="{a}"/>')

    # unfiltered on purpose: a predicate that names B and returns B proves nothing
    s.append(f'<text x="150" y="240" class="key">SELECT count(*) FROM tasks</text>')
    s.append(f'<text class="zero sub" x="150" y="280">B only</text>')
    s.append(f'<text x="440" y="272" class="lbl">ROW-LEVEL SECURITY</text>')

    s.append(f'<path d="M150 320H730" stroke="{RULE}"/>')
    s.append(f'<text x="150" y="352" class="say">The app didn’t remember to filter.</text>')
    s.append(f'<text x="150" y="380" class="say">The database refused.</text>')
    s.append(f'<text x="150" y="420" class="lbl">IDOR IN SIX SERVICES</text>')
    s.append(f'<text x="470" y="420" class="lbl">FOUND BY THE AUTHOR</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── PLATE VI
def plate_release() -> str:
    H, LOOP, SET = 660, 13.1, 9.8
    BEAT = round(LOOP / 4, 2)
    s = [head(H, "LifeQuest",
              "LifeQuest turns real-world routines into tracked quests, for people rebuilding "
              "structure after a layoff or in retirement. One source tree in apps/desktop is "
              "built twice — as a Tauri 2 native binary and as a web app — with a shared Zod "
              "schema package holding both of them to the same contract as the API. Behind it: "
              "10 Prisma models and 14 REST endpoints across 6 NestJS controllers. When it "
              "generates a quest it asks OpenAI, falls back to Hugging Face, and if neither is "
              "configured it returns nothing rather than inventing one.",
              key="plate-6-release.svg")]
    s.append(f""".nd{{transform-box:fill-box;transform-origin:center;animation:nd {LOOP}s {BREATHE} infinite}}
@keyframes nd{{0%,4%{{opacity:0;transform:scale(.9)}}10%{{opacity:1;transform:scale(1)}}
  40%{{transform:scale(1)}}48%{{transform:scale(1.22)}}
  58%{{transform:scale(1)}}
  /* a second, smaller pulse late in the loop, so the plate does not look
     switched off between its two halves */
  82%{{transform:scale(1.1)}}92%,100%{{transform:scale(1);opacity:1}}}}
/* The fallback chain lights left to right and the last link stays dim: it is
   the one that declines. Late in the loop, so the lower half of the plate is
   not dead while the upper half breathes. */
.lnk{{animation:lnk {LOOP}s {ARRIVE} infinite}}
@keyframes lnk{{0%,18%{{opacity:0;transform:translateX(-10px)}}
  28%,100%{{opacity:1;transform:translateX(0)}}}}
/* One build leaves the shared tree down each branch, four times a loop. This
   is the plate's only continuous motion and the reason it no longer sits dead
   for 3.6s in the middle: everything else here arrives once and then holds. */
.bd{{animation:bd {BEAT}s {EASE} infinite}}
@keyframes bd{{0%{{opacity:0;transform:translateX(-72px)}}
  16%{{opacity:1}}84%{{opacity:1}}
  100%{{opacity:0;transform:translateX(0)}}}}
</style>{slab(H, PINK)}""")
    s.append(rail("VII", "LIFEQUEST"))
    s.append(f'<text x="150" y="56" class="kick">CLAIM — WHAT YOU MEANT TO DO, AS QUESTS</text>')
    for i, txt in enumerate(["Reconnect with a mentor", "Document a new routine", "Share a win"]):
        s.append(f'<circle class="nd" cx="158" cy="{83+i*30}" r="7" fill="none" stroke="{PINK}" stroke-width="1.6" '
                 f'style="animation-delay:{round(-SET + i*0.14,3)}s"/>')
        if i < 2:
            s.append(f'<path d="M158 {91+i*30}V{106+i*30}" stroke="{WIRE}" stroke-width="1"/>')
        s.append(f'<text x="178" y="{88+i*30}" class="lbl">{txt}</text>')
    s.append(f'<text x="150" y="196" class="say">For people rebuilding structure —</text>')
    s.append(f'<text x="150" y="224" class="say">after a layoff, or in retirement.</text>')

    s.append(f'<path d="M150 256H730" stroke="{RULE}"/>')
    s.append(f'<text x="150" y="286" class="kick">MECHANISM — ONE SOURCE TREE, BUILT TWICE</text>')

    # the fork: the same apps/desktop tree is a Vite web build and a Tauri
    # native binary, and packages/schemas is the Zod contract that keeps both
    # of them honest against the NestJS API.
    s.append(f'<rect x="150" y="304" width="196" height="46" rx="3" fill="none" stroke="{WIRE}"/>')
    s.append(f'<text x="166" y="323" class="fine" style="fill:{INK}">apps/desktop</text>')
    s.append(f'<text x="166" y="341" class="fine">React · Vite</text>')
    s.append(f'<path d="M346 327H380M380 309V345" fill="none" stroke="{WIRE}"/>')
    for i, (dy, txt) in enumerate([(-18, "TAURI 2 · NATIVE BINARY"), (18, "VITE BUILD · WEB APP")]):
        s.append(f'<path d="M380 {327+dy}H452" fill="none" stroke="{WIRE}"/>')
        # a build leaving down each branch, four times a loop, so the lower half
        # of the plate is never still — and so the fork is shown, not asserted
        s.append(f'<circle class="bd" cx="452" cy="{327+dy}" r="3.5" fill="{PINK}" '
                 f'style="animation-delay:{round(-BEAT*0.5 + i*0.12, 3)}s"/>')
        s.append(f'<text x="{R}" y="{332+dy}" class="lbl" text-anchor="end" style="fill:{PINK}">{txt}</text>')
    s.append(f'<text x="150" y="378" class="fine">packages/schemas — one Zod contract for both builds</text>')

    s.append(f'<path d="M150 402H730" stroke="{RULE}"/>')
    for i, (n, lab, sub) in enumerate([("10", "PRISMA MODELS", "quests, rewards, meetups, rituals"),
                                       ("14", "REST ENDPOINTS", "across 6 NestJS controllers")]):
        y = 442 + i * 62
        s.append(f'<text x="150" y="{y}" class="sub">{n}</text>')
        s.append(f'<text x="230" y="{y}" class="lbl">{lab}</text>')
        s.append(f'<text x="230" y="{y+22}" class="fine">{sub}</text>')

    # The quest generator asks OpenAI, then Hugging Face, and if neither is
    # configured it returns null rather than inventing a quest. Drawn as a
    # chain because that is the shape of the code (ai-content.service.ts:49-56)
    # and because the last link is the honest one.
    s.append(f'<text x="150" y="{442+62+50}" class="kick">QUEST GENERATION — ASKS, THEN FALLS BACK, THEN DECLINES</text>')
    for i, (txt, col) in enumerate([("OPENAI", PINK), ("HUGGING FACE", PINK), ("RETURNS NOTHING", INK3)]):
        x = 150 + i * 200
        s.append(f'<rect class="lnk" x="{x}" y="{442+62+64}" width="168" height="30" rx="3" fill="none" '
                 f'stroke="{WIRE}" style="animation-delay:{round(-SET + i*0.11,3)}s"/>')
        s.append(f'<text x="{x+14}" y="{442+62+84}" class="fine" style="fill:{col}">{txt}</text>')
        if i < 2:
            s.append(f'<path d="M{x+168} {442+62+79}H{x+200}" stroke="{WIRE}"/>')
    s.append(f'<text x="150" y="{442+62+124}" class="fine" style="fill:{INK3}">source-available · noncommercial</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── PLATE VII
def plate_automl() -> str:
    """AutoML's own plate.

    It shared plate VII with LifeQuest until now — a quest tracker and a
    multi-agent ML pipeline on one slab, which the audit called two plates in
    one and measured as the least dense in the set. It also carried the line
    "the one section you cannot check", because the repository was private.
    That stopped being true on 2026-07-30, so every figure here is DERIVED from
    a pinned commit like the other five systems, and the plate is built around
    the one mechanism that is genuinely unusual: the model is never handed the
    whole tool registry.
    """
    H, LOOP, SET = 624, 13.3, 9.9
    TICKS, GEN = 44, 15
    PITCH = (R - L) / TICKS                 # 44 ticks across the type column
    BARS, BX = 7, L + GEN * PITCH           # the seven sets sit under the routed 29
    BPITCH = (R - BX) / BARS
    s = [head(H, "Agentic AutoML",
              "Agentic AutoML takes a dataset and a sentence and returns a trained model. "
              "Its tool registry holds 44 definitions, but the model never carries all of "
              "them: 15 travel with it in every phase and the remaining 29 arrive with the "
              "phase that needs them, routed by seven named tool sets — onboarding, "
              "preprocessing, feature proposal, feature continue, feature engineering, "
              "feature lifecycle and training lifecycle. The Python it writes executes in a "
              "container with no network, a read-only root filesystem, a non-root user and "
              "the dataset mounted read-only, leaving 5 tmpfs mounts as the only writable "
              "surface. Behind it sits a 29-table Postgres schema with pgvector. Written "
              "with Shree Chaturvedi; the repository is public and noncommercially licensed.",
              key="plate-6b-automl.svg")]
    s.append(f""".tk{{animation:tk {LOOP}s {ARRIVE} infinite}}
@keyframes tk{{0%{{opacity:0;transform:translateY(9px)}}
  9%,100%{{opacity:1;transform:translateY(0)}}}}
/* The marker is the claim: it steps through the seven sets one at a time and
   is never over more than one, because that is what phase-aware routing does.
   Seven holds of ~1.6s each — under the 2.4s ceiling on a dead run, and the
   sandbox scan runs underneath it the whole time so the plate is never still. */
/* The wrap from the seventh set back to the first is a 328u jump, which the
   gate calls a teleport and is right to. So it happens with the marker faded
   out, the same way plate VII's token resets — a cycle that visibly snaps
   backwards reads as a glitch, not as a new run starting. */
.mk{{animation:mk {LOOP}s steps(1,end) infinite;animation-delay:{-SET}s}}
@keyframes mk{{0%{{opacity:0;transform:translateX({-6*BPITCH:.1f}px)}}
  2%,12%{{opacity:1;transform:translateX({-6*BPITCH:.1f}px)}}
  14.3%,26%{{transform:translateX({-5*BPITCH:.1f}px)}}
  28.6%,40%{{transform:translateX({-4*BPITCH:.1f}px)}}
  42.9%,55%{{transform:translateX({-3*BPITCH:.1f}px)}}
  57.1%,69%{{transform:translateX({-2*BPITCH:.1f}px)}}
  71.4%,83%{{transform:translateX({-1*BPITCH:.1f}px)}}
  85.7%,97%{{opacity:1;transform:translateX(0)}}
  100%{{opacity:0;transform:translateX(0)}}}}
.sc{{animation:sc {round(LOOP/2,2)}s linear infinite}}
@keyframes sc{{0%{{transform:translateY(0)}}100%{{transform:translateY(118px)}}}}
.mn{{transform-box:fill-box;transform-origin:center;animation:mn {LOOP}s {BREATHE} infinite}}
@keyframes mn{{0%,6%{{opacity:.35;transform:scaleY(.6)}}
  14%{{opacity:1;transform:scaleY(1)}}
  34%{{opacity:1;transform:scaleY(1)}}
  46%,100%{{opacity:1;transform:scaleY(1)}}}}
</style>{slab(H, INDIGO)}""")
    s.append(rail("VIII", "AGENTIC AUTOML"))
    s.append(f'<text x="{L}" y="56" class="kick">CLAIM — DATASET IN, TRAINED MODEL OUT</text>')
    s.append(f'<text x="{L}" y="78" class="kick">MECHANISM — ONE PHASE, ONE TOOL SET</text>')

    # ── the registry, drawn at its real size
    s.append(f'<text x="{L}" y="160" class="hero">{TICKS}</text>')
    s.append(f'<text x="270" y="136" class="key">TOOL DEFINITIONS</text>')
    s.append(f'<text x="270" y="160" class="fine">one MCP server over a LangGraph state machine</text>')
    for i in range(TICKS):
        x = L + i * PITCH
        col = INDIGO if i < GEN else WIRE
        s.append(f'<rect class="tk" x="{x:.1f}" y="190" width="5" height="22" fill="{col}" '
                 f'style="animation-delay:{round(-SET + i*0.045,3)}s"/>')
    # brackets naming the two halves. The labels sit at the two OUTER edges —
    # left under the 15, right-anchored under the far end of the 29 — because
    # putting both flush-left made them collide, and the gate said so.
    s.append(f'<path d="M{L} 220V226H{L+(GEN-1)*PITCH+5:.1f}V220" fill="none" stroke="{WIRE}"/>')
    s.append(f'<text x="{L}" y="244" class="kick" style="fill:{INDIGO}">{GEN} TRAVEL WITH THE MODEL</text>')
    s.append(f'<path d="M{BX:.1f} 220V226H{L+(TICKS-1)*PITCH+5:.1f}V220" fill="none" stroke="{WIRE}"/>')
    s.append(f'<text x="{R}" y="244" class="kick" text-anchor="end">{TICKS-GEN} ARRIVE WITH THE PHASE</text>')

    # ── the seven sets, and the marker that is only ever under one of them.
    # The marker underlines rather than overlays: an indigo rect ON the bar is
    # a collision as far as the gate is concerned, and it was right to say so —
    # two filled rects at the same coordinates is exactly what a bug looks like.
    for i in range(BARS):
        x = BX + i * BPITCH
        last = ' id="set-last"' if i == BARS - 1 else ''
        s.append(f'<rect{last} x="{x:.1f}" y="264" width="{BPITCH-8:.1f}" height="8" rx="1" fill="{ROW}"/>')
    s.append(f'<rect class="mk" data-rest="set-last" data-rest-within="14" '
             f'x="{BX + (BARS-1)*BPITCH:.1f}" y="278" width="{BPITCH-8:.1f}" height="3" rx="1" fill="{INDIGO}"/>')
    s.append(f'<text x="{L}" y="276" class="lbl">SEVEN PHASE SETS</text>')

    s.append(f'<path d="M{L} 300H{R}" stroke="{RULE}"/>')

    # ── the sandbox, quoted from the docker run it actually builds
    s.append(f'<text x="{L}" y="330" class="kick">WHERE THE GENERATED PYTHON RUNS</text>')
    s.append(f'<rect x="{L}" y="344" width="330" height="124" rx="3" fill="none" stroke="{INDIGO}"/>')
    s.append(f'<rect class="sc" x="{L+2}" y="347" width="326" height="3" fill="{INDIGO}" opacity=".6"/>')
    for i, (flag, why) in enumerate([("--network none", "no egress"),
                                     ("--read-only", "immutable rootfs"),
                                     ("--user sandbox", "never root"),
                                     ("/datasets:ro", "read-only mount")]):
        s.append(f'<text x="{L+16}" y="{374+i*26}" class="fine" style="fill:{INK}">{flag}</text>')
        s.append(f'<text x="{L+170}" y="{374+i*26}" class="fine">{why}</text>')
    # the five writable mounts, drawn because their count IS the blast radius
    s.append(f'<text x="520" y="366" class="key">5 TMPFS MOUNTS</text>')
    s.append(f'<text x="520" y="388" class="fine">the only surface it can</text>')
    s.append(f'<text x="520" y="406" class="fine">write to, and none of it</text>')
    s.append(f'<text x="520" y="424" class="fine">survives the container</text>')
    for i in range(5):
        s.append(f'<rect class="mn" x="{520+i*30}" y="440" width="20" height="14" rx="1" '
                 f'fill="none" stroke="{INDIGO}" style="animation-delay:{round(-SET + i*0.09,3)}s"/>')

    s.append(f'<path d="M{L} 500H{R}" stroke="{RULE}"/>')
    s.append(f'<text x="{L}" y="540" class="sub">29</text>')
    s.append(f'<text x="200" y="540" class="lbl">TABLES · POSTGRES + PGVECTOR</text>')
    s.append(f'<text x="200" y="562" class="fine">a Jupyter kernel per project, kept alive between cells</text>')
    s.append(f'<text x="{L}" y="592" class="fine" style="fill:{INK3}">public · noncommercial · written with Shree Chaturvedi</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── PLATE IX
def plate_colophon() -> str:
    H = 269
    s = [head(H, "Colophon", "Six systems, five system cards and one expo booklet. Every number "
                             "here is traceable to the repository it came from, and the page "
                             "itself is animated SVG "
                             "with no JavaScript and no server.", key="plate-7-colophon.svg")]
    # This plate asserts "ANIMATED SVG" and used to be the only one that wasn't.
    LOOP, SET = 12.7, 10.0
    s.append(f""".rule{{stroke-dasharray:1;animation:sweep {LOOP}s {EASE} infinite;animation-delay:{-SET}s}}
@keyframes sweep{{0%{{stroke-dashoffset:1}}20%,100%{{stroke-dashoffset:0}}}}
.ln,.ln2{{animation:ln {LOOP}s {BREATHE} infinite}}
@keyframes ln{{0%,24%{{transform:translateX(0)}}32%{{transform:translateX(6px)}}
  46%{{transform:translateX(0)}}
  68%{{transform:translateX(0)}}76%{{transform:translateX(3px)}}
  88%,100%{{transform:translateX(0)}}}}
/* The colophon's accent used to be INDIGO, which the legend on plate 0 assigns
   to AutoML. Now that AutoML has a plate of its own that reads as its colour,
   the closing plate takes the neutral rule grey: it is not a system, so it
   should not wear a system's colour. */
</style>{slab(H, RULE)}""")
    s.append(rail("IX", "COLOPHON"))
    s.append(f'<path class="rule" d="M150 80H{W-150}" pathLength="1" stroke="{RULE}"/>')
    for i, ln in enumerate(["Six systems. Five system cards, one booklet.",
                            "Every number traces to its repo."]):
        s.append(f'<text class="ln say" x="150" y="{120 + i*28}" '
                 f'style="animation-delay:{round(-SET + i*0.15,3)}s">{ln}</text>')
    s.append(f'<text x="150" y="172" class="fine" style="fill:{INK3}">all six repositories are open — the work numbers come from my CV</text>')
    s.append(f'<text class="ln2 lbl" x="150" y="204" '
             f'style="animation-delay:{round(-SET + 1.9,3)}s">ANIMATED SVG · NO JAVASCRIPT · NO SERVER</text>')
    s.append(f'<text x="150" y="236" class="lbl">B.S. CS · MIAMI UNIVERSITY ’26</text>')
    s.append(f'<text x="{R}" y="236" class="lbl" text-anchor="end">aesh.03.23@gmail.com</text>')
    return "".join(s) + "</svg>"


PLATES = {
    "plate-0-thesis.svg": plate_thesis, "plate-0b-work.svg": plate_work,
    "plate-1-glyph.svg": plate_glyph,
    "plate-2-jetpack.svg": plate_jetpack, "plate-3-cadence.svg": plate_cadence,
    "plate-4-applied.svg": plate_applied, "plate-5-refusal.svg": plate_refusal,
    "plate-6-release.svg": plate_release, "plate-6b-automl.svg": plate_automl,
    "plate-7-colophon.svg": plate_colophon,
}

# ────────────────────────────────────────────────── the build-time gate
# Cheap structural checks only. The REAL layout gate is build/gate.mjs, which
# renders every plate in Chromium and measures 40 samples across each loop —
# arithmetic here cannot see a transform, and pretending otherwise is how nine
# collisions once shipped under a PASS.
import re as _re, sys as _sys, xml.dom.minidom as _xml

_fail = []
for fn, gen in PLATES.items():
    path = OUT / fn
    path.write_text(gen())
    try:
        _xml.parseString(path.read_text())
    except Exception as e:
        _fail.append(f"{fn}: MALFORMED XML — {e}")
    print(f"{fn}: {path.stat().st_size:,} bytes")

# ────────────────────────────────────────────────── mobile set
# At GitHub's real 324px column a 16-unit label on an 880 canvas renders at
# 5.9px — unreadable. So the phone gets its own plates: a 440 canvas at the SAME
# absolute type sizes (≈11.8px rendered), carrying the hero and one line. The
# argument itself is already in the markdown, which is selectable, searchable
# and theme-native. Served via <picture media="(max-width:500px)">.
#
# The <desc> here is the SAME string as the desktop plate's, because <picture>
# permits one alt for both sources — so the alt has to be true of whichever
# image the browser picked. gate.mjs enforces the direction that matters: every
# number the mobile plate DRAWS must appear in that shared description.
MW = 440


def plate_mobile(accent: str, kicker: str, hero: str, unit: str,
                 line1: str, line2: str, desc: str) -> str:
    h = 224   # a 64px hero's glyph box is 84u tall; 208 could not hold it
    return "".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {MW} {h}" width="{MW}" height="{h}" '
        f'role="img" aria-label="{desc}"><title>{kicker}</title><desc>{desc}</desc><style>'
        f"@font-face{{font-family:'M';src:url(data:font/woff2;base64,{FONT}) format('woff2')}}"
        f"text{{font-family:'M',ui-monospace,SFMono-Regular,Menlo,monospace}}"
        f".k{{font-size:16px;letter-spacing:1.8px;fill:{INK2}}}"
        f".n{{font-size:64px;letter-spacing:-1.5px;fill:{INK};font-weight:600}}"
        f".u{{font-size:26px;fill:{INK2}}}"
        f".t{{font-size:16px;fill:{INK2}}}"
        f"</style>"
        f'<rect width="{MW}" height="{h}" rx="2" fill="{SLAB}"/>'
        f'<rect x="0.5" y="0.5" width="{MW-1}" height="{h-1}" rx="2" fill="none" stroke="{EDGE}"/>'
        f'<rect x="0" y="0" width="4" height="{h}" fill="{accent}"/>',
        f'<text x="34" y="40" class="k">{kicker}</text>',
        f'<text x="34" y="124" class="n">{hero}<tspan class="u">{unit}</tspan></text>',
        f'<text x="34" y="168" class="t">{line1}</text>',
        f'<text x="34" y="194" class="t">{line2}</text>',
        "</svg>"])


MOBILE = {
 "m-1-glyph.svg": ("GLYPH", AMBER, "97.01", "%", "A neural net written from", "scratch in C++. 299 wrong.", "plate-1-glyph.svg"),
 "m-2-jetpack.svg": ("JETPACK", LIME, "6.4", "×", "Parallel gzip on JDK 25.", "The JDK intrinsic still wins.", "plate-2-jetpack.svg"),
 "m-3-cadence.svg": ("CADENCE", EMERALD, "36", "", "handlers bundled into one", "function. The plan allows 12.", "plate-3-cadence.svg"),
 "m-4-applied.svg": ("APPLIED", CYAN, "0.979", "", "macro-F1, rules layer only.", "Below 0.85 it asks a human.", "plate-4-applied.svg"),
 "m-5-refusal.svg": ("THE REFUSAL", EMERALD, "B", " only", "The app didn't remember", "to filter. The database refused.", "plate-5-refusal.svg"),
 "m-6-release.svg": ("LIFEQUEST · AUTOML", PINK, "HUMAN", "", "in the loop before a step commits", "or a model trains. Not public.", "plate-6-release.svg"),
}
for _fn, (_k, _a, _n, _u, _l1, _l2, _src) in MOBILE.items():
    (OUT / _fn).write_text(plate_mobile(_a, _k, _n, _u, _l1, _l2, ALT[_src]))
print(f"mobile set: {len(MOBILE)} plates at {MW}w")

# ────────────────────────────────────────────────── alt/desc/README agreement
# Every description is authored once in ALT and must reach the README verbatim —
# three surfaces drifted apart once and left a retracted claim alive in the
# accessible text.
(OUT / "alt.json").write_text(json.dumps(ALT, indent=2, sort_keys=True))
_readme = ROOT.parent / "README.md"
if _readme.exists():
    _md = _readme.read_text()
    for _fn, _desc in ALT.items():
        _m = _re.search(rf'<img src="\./assets/{_re.escape(_fn)}"[^>]*?alt="([^"]*)"', _md)
        if not _m:
            _fail.append(f"{_fn}: no <img> with an alt in README.md")
        elif _m.group(1).strip() != _desc.strip():
            _fail.append(f"{_fn}: README alt has drifted from the plate's own description")

if _fail:
    print("\nGATE FAILED:")
    for f in _fail:
        print(f"  · {f}")
    _sys.exit(1)
print("\nBUILD OK — all plates parse, alts agree. Run `node build/gate.mjs` to measure them.")
