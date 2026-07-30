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

W = 880
SLAB, EDGE = "#0B0C0E", "rgba(255,255,255,0.07)"
# Every structural line used to sit between 1.08:1 and 1.94:1 on the slab —
# WCAG 1.4.11 wants 3:1 for anything non-text that carries meaning. So the
# document was drawing its numbers at AAA and the mechanism behind them at
# roughly half the legibility floor, which is the exact inversion of its thesis.
RULE = "#5A606A"   # 3.06:1 — section rules
WIRE = "#6E737C"   # 4.05:1 — connectors, boundaries, brackets, box frames.
                   # Used at FULL opacity: a .45 alpha put it back under 2:1.
ROW = "#3A424B"    # tenant row fills, paired with a WIRE stroke
INK, INK2, INK3 = "#F7F8F8", "#8A8F98", "#62666D"
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


def head(h: int, title: str, desc: str, key: str = "") -> str:
    if key:
        ALT[key] = desc
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}" role="img" aria-label="{desc}">
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
@media (prefers-reduced-motion: reduce){{*{{animation:none!important}}}}
"""


def slab(h: int, accent: str | None = None) -> str:
    s = (f'<rect width="{W}" height="{h}" rx="2" fill="{SLAB}"/>'
         f'<rect x="0.5" y="0.5" width="{W-1}" height="{h-1}" rx="2" fill="none" stroke="{EDGE}"/>')
    if accent:
        s += f'<rect x="0" y="0" width="4" height="{h}" fill="{accent}"/>'
    return s


# ────────────────────────────────────────────────────────────── PLATE 0
def plate_thesis() -> str:
    H = 304
    s = [head(H, "Ayush Yadav — every number is followed by the thing that would catch it",
              "The thesis plate: Ayush Yadav, and the sentence 'Every number on this page is "
              "followed by the thing that would catch it.' Below it, the six colours the "
              "document uses, one per system: Glyph, jetpack, Cadence, Applied, LifeQuest, AutoML.",
              key="plate-0-thesis.svg")]
    # A one-shot with a negative delay equal to its duration starts finished and
    # never moves again — plate 0 was a static image wearing an animation. The
    # legend now carries a real loop, and frame zero still lands on full strength.
    LOOP, SET = 11.3, 9.0
    s.append(f""".rule{{stroke-dasharray:1;animation:sweep {LOOP}s {EASE} infinite;animation-delay:{-SET}s}}
@keyframes sweep{{0%{{stroke-dashoffset:1}}18%,100%{{stroke-dashoffset:0}}}}
.sw{{animation:sw {LOOP}s linear infinite}}
@keyframes sw{{0%,4%{{opacity:.45}}12%,100%{{opacity:1}}}}
.ser{{font-family:ui-serif,Georgia,'Times New Roman',serif;font-size:34px;fill:{INK}}}
</style>{slab(H, AMBER)}""")
    s.append(f'<text x="150" y="56" class="key" letter-spacing="5">AYUSH YADAV</text>')
    s.append(f'<text x="{R}" y="{TOP}" class="lbl" text-anchor="end">CS ’26 · MIAMI UNIVERSITY</text>')
    s.append(f'<path class="rule" d="M150 88H{W-150}" pathLength="1" stroke="{WIRE}"/>')
    for i, ln in enumerate(["Every number on this page is", "followed by the thing",
                            "that would catch it."]):
        s.append(f'<text x="150" y="{136 + i*40}" class="ser">{ln}</text>')
    # the ONLY polychrome frame in the document — and now it says what it means
    for i, (nm, c) in enumerate(LEGEND):
        x = 150 + i * 96
        s.append(f'<rect class="sw" x="{x}" y="248" width="14" height="4" rx="1" fill="{c}" '
                 f'style="animation-delay:{round(-SET + i*0.12,3)}s"/>')
        s.append(f'<text x="{x}" y="272" class="fine">{nm}</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── PLATE I
def plate_glyph() -> str:
    H, LOOP, SET, a = 584, 9.1, 7.6, AMBER
    s = [head(H, "Glyph — 97.01%, and the 299 it gets wrong",
              "Glyph: a neural network written from scratch in C++ with hand-written AVX-512, "
              "AVX2 and NEON kernels, plus an autovectorised WebAssembly build. It scores 97.01 "
              "percent on the 10,000-image MNIST test set, which means 299 wrong — every one of "
              "them drawn as a grid of the labels it missed. 79 of those errors were made with "
              "over 0.9 confidence.", key="plate-1-glyph.svg")]
    s.append(f""".ink{{fill:none;stroke:{a};stroke-width:7;stroke-linecap:round;stroke-linejoin:round;
  stroke-dasharray:1;stroke-dashoffset:0;animation:draw {LOOP}s linear infinite;animation-delay:{-SET}s}}
@keyframes draw{{0%{{stroke-dashoffset:1}}17%{{stroke-dashoffset:0}}100%{{stroke-dashoffset:0}}}}
.tok{{animation:run {LOOP}s {EASE} infinite}}
@keyframes run{{0%{{opacity:0;transform:translateX(0)}}5%{{opacity:1;transform:translateX(0)}}
  34%,96%{{opacity:1;transform:translateX(190px)}}100%{{opacity:0;transform:translateX(190px)}}}}
.wrong{{opacity:.78}}
</style>{slab(H, a)}""")

    # CLAIM — the seven, drawn by hand
    s.append(f'<text x="150" y="56" class="lbl">CLAIM</text>')
    s.append(f'<text x="330" y="80" class="lbl">MECHANISM — 3 BY HAND, 1 AUTO</text>')
    s.append(rail("I", "GLYPH"))
    s.append(f'<g {digit(DIGITS[7], 150, 104, 1.15)}><path class="ink" d="{DIGITS[7]}" pathLength="1"/></g>')

    # MECHANISM — four instruction sets, one answer
    for i, name in enumerate(["AVX-512", "AVX2", "NEON", "wasm (auto)"]):
        y = 120 + i * 34
        s.append(f'<text x="330" y="{y+5}" class="key">{name}</text>')
        s.append(f'<path d="M470 {y}H660" stroke="{WIRE}" stroke-width="1"/>')
        s.append(f'<circle class="tok" data-rest="one-answer" data-rest-within="2" '
                 f'cx="470" cy="{y}" r="4" fill="{a}" '
                 f'style="animation-delay:{round(-SET + i*0.06,3)}s"/>')
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
    for i in range(len(errs)):
        c, r = i % cols, i // cols
        x, y = gx + c * 11.4, gy + r * 14.0
        s.append(f'<g class="wrong" {digit(DIGITS[errs[i]], x, y, 0.068, centre=10.4)}>'
                 f'<path d="{DIGITS[errs[i]]}" fill="none" stroke="{a}" stroke-width="15" '
                 f'stroke-linecap="round"/></g>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── PLATE II
def plate_jetpack() -> str:
    H, LOOP, SET, a = 536, 10.3, 7.2, LIME
    s = [head(H, "jetpack — 6.4x parallel, and the intrinsic it does not beat",
              "jetpack: parallel gzip on JDK 25 reaches 422 megabytes per second against 66.2 "
              "single-threaded, a 6.4 times speedup, with blocks held in a bounded in-flight "
              "window. Its hand-vectorised Adler-32 checksum runs at 4.26 gigabytes per second "
              "and is verified bit-identical against java.util.zip — whose own native intrinsic "
              "is faster still, at 14.06, and is printed here as the reference it loses to.",
              key="plate-2-jetpack.svg")]
    s.append(f""".blk{{animation:sq {LOOP}s {EASE} infinite;transform-box:fill-box;transform-origin:left center}}
@keyframes sq{{0%{{opacity:0;transform:translateX(0) scaleX(1)}}
  5%,14%{{opacity:1;transform:translateX(0) scaleX(1)}}
  38%,96%{{opacity:1;transform:translateX(230px) scaleX(.55)}}
  100%{{opacity:0;transform:translateX(230px) scaleX(.55)}}}}
.mt{{transform-box:fill-box;transform-origin:left center;animation:mt {LOOP}s {EASE} infinite}}
@keyframes mt{{0%,6%{{transform:scaleX(0);opacity:0}}11%{{opacity:1}}24%,100%{{transform:scaleX(1);opacity:1}}}}
.row{{animation:rw {LOOP}s {EASE} infinite}}
@keyframes rw{{0%,8%{{opacity:.55}}20%,100%{{opacity:1}}}}
</style>{slab(H, a)}""")
    s.append(f'<text x="330" y="80" class="lbl">PARALLEL vs SINGLE-THREAD GZIP</text>')
    s.append(rail("II", "JETPACK"))
    # NOT "CI ±5%": the 3-fork run's 99.9% intervals span ±0.7% to ±6.9%, so a
    # single figure would be a claim the committed JSON contradicts.
    s.append(f'<text x="330" y="104" class="lbl">JDK 25 · M1 PRO · 3 JMH FORKS</text>')
    s.append(f'<text x="150" y="108" class="hero">6.4<tspan class="unit">×</tspan></text>')
    s.append(f'<text x="150" y="152" class="lbl">CLAIM</text>')

    # The bounded in-flight window. The bracket used to span 400→636 while the
    # compressed blocks came to rest at 410→518, leaving half the window
    # permanently void — it drew a window twice the size of the thing it bounds.
    s.append(f'<text x="400" y="136" class="lbl">BOUNDED IN-FLIGHT WINDOW</text>')
    # the window used to span 400..540 while the compressed blocks came to rest
    # at 410..517.8 — 32.2u of permanent void, split unevenly 10 left / 22 right.
    # 404..524 puts 6u of air on each side of the thing it bounds.
    s.append(f'<path d="M404 152V268M404 152H424M404 268H424" stroke="{WIRE}" stroke-width="1"/>')
    s.append(f'<path d="M524 152V268M524 152H504M524 268H504" stroke="{WIRE}" stroke-width="1"/>')
    for i in range(4):
        y = 168 + i * 26
        s.append(f'<rect class="blk" x="180" y="{y}" width="196" height="16" rx="2" fill="{a}" opacity=".85" '
                 f'style="animation-delay:{round(-SET + i*0.22,3)}s"/>')
    for j, ln in enumerate(["peak memory", "tracks the window,", "not the file"]):
        s.append(f'<text x="560" y="{194 + j*20}" class="fine">{ln}</text>')
    s.append(f'<text x="150" y="288" class="lbl">MECHANISM — one virtual thread per block</text>')

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
    s.append(f'<text x="556" y="344" class="lbl" fill="{a}">identical</text>')

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
        dl = round(-SET + i * 0.16, 3)
        s.append(f'<text class="row lbl" x="150" y="{y}" style="animation-delay:{dl}s">{name}</text>')
        s.append(f'<text class="row key" x="470" y="{y}" style="animation-delay:{dl}s">{score}</text>')
        if note:
            fill = INK if note == "not beaten" else a
            s.append(f'<text class="row lbl" x="604" y="{y}" fill="{fill}" '
                     f'style="animation-delay:{dl}s">{note}</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── PLATE III
def plate_cadence() -> str:
    H, LOOP, SET, a = 464, 7.9, 5.6, EMERALD
    SENT, FS, CW = "lunch with sam friday 1pm", 26, 15.62
    s = [head(H, "Cadence — a parser that shows its work",
              "Cadence: the sentence 'lunch with sam friday 1pm' is labelled in place — title, "
              "attendee, day and time — and filed into a Friday cell of the week grid. Its 36 "
              "API handlers are bundled into a single serverless function, because the hosting "
              "plan allows 12.", key="plate-3-cadence.svg")]
    s.append(f""".ul{{animation:ul {LOOP}s {EASE} infinite;transform-box:fill-box;transform-origin:left center}}
@keyframes ul{{0%,4%{{transform:scaleX(0);opacity:0}}8%{{opacity:1}}18%,100%{{transform:scaleX(1);opacity:1}}}}
.an{{animation:an {LOOP}s linear infinite}}
@keyframes an{{0%,6%{{opacity:0}}12%,100%{{opacity:1}}}}
.fil{{animation:fil {LOOP}s linear infinite}}
@keyframes fil{{0%,10%{{opacity:0}}16%,100%{{opacity:1}}}}
</style>{slab(H, a)}""")
    s.append(f'<text x="150" y="56" class="lbl">CLAIM — plain English in, calendar out</text>')
    s.append(rail("III", "CADENCE"))
    s.append(f'<text x="150" y="104" font-size="{FS}" fill="{INK}" letter-spacing="0">{SENT}</text>')
    # Four passes annotating the SAME sentence in place — a linguist's gloss.
    # The labels used to stagger onto two rows to dodge a collision, which made
    # a reader scan them TITLE→DATE→ATTENDEE→TIME. Short labels fit one row, so
    # the reading order is the sentence order again.
    toks = [(0, 5, "TITLE"), (11, 3, "WHO"), (15, 6, "DAY"), (22, 3, "TIME")]
    for i, (start, ln, label) in enumerate(toks):
        x, w = 150 + start * CW, ln * CW
        dl = round(-SET + i * 0.5, 3)
        s.append(f'<rect class="ul" x="{x:.0f}" y="114" width="{w:.0f}" height="2" fill="{a}" '
                 f'style="animation-delay:{dl}s"/>')
        s.append(f'<text class="an lbl" x="{x:.0f}" y="140" fill="{a}" '
                 f'style="animation-delay:{dl}s">{label}</text>')
    s.append(f'<text x="150" y="200" class="lbl">MECHANISM — four stages, each one legible</text>')

    # filed — a week grid with real hour rows, so it reads as a calendar
    s.append(f'<path d="M150 224H730" stroke="{RULE}"/>')
    for d, day in enumerate(["MON", "TUE", "WED", "THU", "FRI"]):
        x = 150 + d * 116
        s.append(f'<text x="{x}" y="252" class="lbl">{day}</text>')
        s.append(f'<rect x="{x}" y="262" width="100" height="72" rx="3" fill="none" stroke="{WIRE}"/>')
        for hr in (286, 310):
            s.append(f'<path d="M{x} {hr}H{x+100}" stroke="{RULE}" stroke-width="1"/>')
    s.append(f'<g class="fil" style="animation-delay:{-SET}s">'
             f'<rect x="616" y="288" width="96" height="20" rx="3" fill="#0E2A22" stroke="{a}"/>'
             f'<text x="624" y="302" class="fine" fill="{a}">1pm · sam</text></g>')
    s.append(f'<text x="150" y="410" class="hero">36</text>')
    s.append(f'<text x="232" y="394" class="lbl">HANDLERS IN ONE FUNCTION</text>')
    s.append(f'<text x="232" y="418" class="lbl">THE PLAN ALLOWS 12</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── PLATE IV
def plate_applied() -> str:
    H, LOOP, SET, a = 536, 11.7, 8.4, CYAN
    s = [head(H, "Applied — a classifier allowed to say it doesn't know",
              "Applied: a three-layer email classifier — 201 regex rules, then e5 embeddings, "
              "then a fine-tuned SetFit head, cheapest first. It scores 0.979 macro-F1 on a "
              "96-message evaluation set, measured with the rules layer alone; anything that "
              "fails to clear the 0.85 confidence gate is referred to a human rather than "
              "guessed at. Inference runs inside your browser.", key="plate-4-applied.svg")]
    s.append(f""".env{{animation:fall {LOOP}s {EASE} infinite}}
@keyframes fall{{0%{{opacity:0;transform:translateY(0)}}5%{{opacity:1;transform:translateY(0)}}
  46%,96%{{opacity:1;transform:translateY(184px)}}100%{{opacity:0;transform:translateY(184px)}}}}
/* The corner used to be at translateY(212px) — 52u BELOW the gate, so the one
   message that is supposed to be refused crossed the gate first and turned
   underneath it. Nothing on the plate was ever stopped by anything. 140px puts
   its bottom edge exactly on y=288, where it is held before being referred. */
.div{{animation:dv {LOOP}s {ARREST} infinite}}
@keyframes dv{{0%{{opacity:0;transform:translate(0,0)}}5%{{opacity:1;transform:translate(0,0)}}
  /* stopped ON the gate, and visibly held there — that pause is the refusal */
  30%,44%{{opacity:1;transform:translate(0,140px)}}
  /* then referred: down through the empty slot it left in the stack, and out
     to a person. It descends in its OWN column, so it never crosses a message
     still falling — routing it diagonally put it through slot 4 in flight. */
  56%{{opacity:1;transform:translate(0,212px)}}
  68%,96%{{opacity:1;transform:translate(146px,212px)}}100%{{opacity:0;transform:translate(146px,212px)}}}}
</style>{slab(H, a)}""")
    # 0.979 is the number with artifacts behind it: five committed files carry
    # it. 0.9583 — the full cascade — survives in exactly one line of prose,
    # because the run that produced it was overwritten by the deterministic
    # re-run. So the hero is the number I can hand you, labelled for what it
    # actually measures, and the gap is stated rather than papered over.
    s.append(f'<text x="150" y="104" class="hero">0.979</text>')
    s.append(rail("IV", "APPLIED"))
    s.append(f'<text x="400" y="80" class="lbl">MACRO-F1 · 96-MSG EVAL SET</text>')
    s.append(f'<text x="400" y="100" class="lbl" fill="{AMBER}">RULES LAYER ONLY</text>')
    s.append(f'<text x="400" y="118" class="fine">SetFit off, embeddings emptied</text>')

    for label, y in [("201 REGEX RULES", 160), ("e5 EMBEDDINGS", 200), ("SETFIT HEAD", 240)]:
        s.append(f'<text x="150" y="{y+5}" class="lbl">{label}</text>')
        s.append(f'<path d="M400 {y}H640" stroke="{WIRE}" stroke-width="1" stroke-dasharray="4 5"/>')
    # the gate that is allowed to decline
    s.append(f'<text x="150" y="293" class="lbl" fill="{a}">0.85 CONFIDENCE GATE</text>')
    s.append(f'<path d="M400 288H640" stroke="{a}" stroke-width="1"/>')
    s.append(f'<text x="150" y="316" class="fine">CI fails the build below 0.95</text>')

    for i in range(5):
        if i == 2:
            continue          # slot 2 belongs to the .div below — five messages, not six
        s.append(f'<rect class="env" x="{416 + i*44}" y="128" width="30" height="20" rx="2" fill="none" '
                 f'stroke="{a}" stroke-width="1.6" style="animation-delay:{round(-SET + i*0.4,3)}s"/>')
    # the one that does not clear the gate leaves the stack and goes sideways
    # the whole claim of this plate is that the one that fails the gate reaches
    # a PERSON. If it merely leaves the stack, the plate says nothing.
    s.append(f'<rect class="div" data-rest="the-human" data-rest-within="10" '
             f'x="504" y="128" width="30" height="20" rx="2" fill="none" '
             f'stroke="{AMBER}" stroke-width="1.6" style="animation-delay:{round(-SET + 0.2,3)}s"/>')
    s.append(f'<circle id="the-human" cx="700" cy="350" r="11" fill="none" stroke="{AMBER}" stroke-width="1.4"/>')
    s.append(f'<text x="{W-150}" y="318" class="lbl" fill="{AMBER}" text-anchor="end">A HUMAN</text>')
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
    H, LOOP, SET, a = 452, 6.7, 4.7, EMERALD
    s = [head(H, "The refusal — the database declines to return another tenant's rows",
              "A query from one tenant travels toward another tenant's rows, reaches the "
              "PostgreSQL row-level-security boundary, and stops. Only the querying tenant's own "
              "rows come back — because the database refused, not because the application "
              "remembered to filter.", key="plate-5-refusal.svg")]
    # The travel used to be 80px, which left the dot's right edge at 415 — five
    # units short of a boundary it is supposed to be stopped BY, for 66% of the
    # loop and at frame zero. A refusal that never touches the wall is a diagram
    # of a query losing interest. 104px lands the edge exactly on 439.
    s.append(f""".q{{animation:seek {LOOP}s {ARREST} infinite;animation-delay:{-SET}s}}
@keyframes seek{{0%{{opacity:0;transform:translateX(0)}}5%{{opacity:1;transform:translateX(0)}}
  /* contact at 28%, a 3u recoil, then it stays stopped. The recoil is the
     difference between "arrived here" and "was refused here". */
  28%{{opacity:1;transform:translateX(104px)}}30%{{transform:translateX(101px)}}
  32%,96%{{opacity:1;transform:translateX(104px)}}100%{{opacity:0;transform:translateX(104px)}}}}
/* The boundary reacts once, on contact. It cannot do this with opacity: an
   element that flashes is either dimmed at frame zero or below the 70% duty
   floor, and both are gate failures. So it flexes instead — always fully
   visible, at rest in the finished frame. */
.wall{{transform-box:fill-box;transform-origin:center;animation:wall {LOOP}s {EASE} infinite;animation-delay:{-SET}s}}
@keyframes wall{{0%,27%{{transform:scaleY(1)}}31%{{transform:scaleY(1.06)}}42%,100%{{transform:scaleY(1)}}}}
.zero{{animation:land {LOOP}s linear infinite;animation-delay:{-SET}s}}
@keyframes land{{0%,14%{{opacity:0}}22%,100%{{opacity:1}}}}
</style>{slab(H, a)}""")

    s.append(rail("V", "THE REFUSAL"))
    s.append(f'<text x="150" y="80" class="lbl">TENANT B — THE CALLER</text>')
    s.append(f'<text x="560" y="80" class="lbl">TENANT A</text>')
    for i in range(4):
        y = 104 + i * 28
        # Both stacks are 170 wide. They were 160 and 170 — two things that must
        # read as symmetric peers, differing by 10u for no reason.
        # And they are no longer the same grey: B's rows are the ones that come
        # back, so they carry the accent. The plate said "B only" in 32px type
        # and drew eight identical rectangles.
        s.append(f'<rect x="150" y="{y}" width="170" height="18" rx="2" fill="{ROW}" stroke="{a}"/>')
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
             f'cx="330" cy="113" r="5" fill="{a}"/>')

    # unfiltered on purpose: a predicate that names B and returns B proves nothing
    s.append(f'<text x="150" y="240" class="key">SELECT count(*) FROM tasks</text>')
    s.append(f'<text class="zero sub" x="150" y="280">B only</text>')
    s.append(f'<text x="440" y="272" class="lbl">ROW-LEVEL SECURITY</text>')

    s.append(f'<path d="M150 320H730" stroke="{RULE}"/>')
    s.append(f'<text x="150" y="352" class="say">The app didn’t remember to filter.</text>')
    s.append(f'<text x="150" y="380" class="say">The database refused.</text>')
    s.append(f'<text x="150" y="420" class="lbl">IDOR: 7 REGRESSION TESTS</text>')
    s.append(f'<text x="470" y="420" class="lbl">FOUND BY THE AUTHOR</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── PLATE VI
def plate_release() -> str:
    H, LOOP, SET = 568, 13.1, 9.8
    s = [head(H, "LifeQuest and Agentic AutoML",
              "LifeQuest turns real-world routines into tracked quests, for people rebuilding "
              "structure after a layoff or in retirement. Agentic AutoML moves a dataset through "
              "a hardened Docker sandbox and holds it for a human before a preprocessing step is "
              "committed and before a model is trained. This is the one section on the page a "
              "reader cannot check: the repository is private.",
              key="plate-6-release.svg")]
    s.append(f""".nd{{animation:nd {LOOP}s linear infinite}}
@keyframes nd{{0%,4%{{opacity:0}}10%,100%{{opacity:1}}}}
.tk2{{animation:tk2 {LOOP}s {EASE} infinite}}
@keyframes tk2{{0%{{opacity:0;transform:translateX(0)}}3%{{opacity:1;transform:translateX(0)}}
  18%,26%{{opacity:1;transform:translateX(348px)}}
  /* the longest dead hold in the document: it is waiting for a human, and it
     now waits AT the gate at x=530 rather than 110u short of it, inside a wall */
  32%,96%{{opacity:1;transform:translateX(424px)}}100%{{opacity:0;transform:translateX(424px)}}}}
.ok{{animation:ok {LOOP}s linear infinite}}
@keyframes ok{{0%,26%{{opacity:0}}30%,100%{{opacity:1}}}}
/* travel slow enough that a 0.33s sample never covers more than ~130u */
</style>{slab(H, PINK)}""")
    s.append(rail("VI", "LIFEQUEST · AUTOML"))
    s.append(f'<text x="150" y="56" class="lbl">LIFEQUEST</text>')
    for i, txt in enumerate(["Reconnect with a mentor", "Document a new routine", "Share a win"]):
        s.append(f'<circle class="nd" cx="158" cy="{83+i*30}" r="7" fill="none" stroke="{PINK}" stroke-width="1.6" '
                 f'style="animation-delay:{round(-SET + i*0.3,3)}s"/>')
        if i < 2:
            s.append(f'<path d="M158 {91+i*30}V{106+i*30}" stroke="{WIRE}" stroke-width="1"/>')
        s.append(f'<text x="178" y="{88+i*30}" class="lbl">{txt}</text>')
    s.append(f'<text x="150" y="196" class="say">For people rebuilding structure —</text>')
    s.append(f'<text x="150" y="224" class="say">after a layoff, or in retirement.</text>')

    s.append(f'<path d="M150 256H730" stroke="{RULE}"/>')
    s.append(f'<text x="150" y="288" class="lbl">AGENTIC AUTOML</text>')
    s.append(f'<text x="{W-150}" y="288" class="lbl" text-anchor="end">SENIOR DESIGN · MIAMI UNIVERSITY</text>')

    # the lane, y 320→400. Nothing crosses this band but lane furniture, so the
    # token cannot come to rest on a label — it did, on "APPROVAL", for 28% of
    # the loop, until the gate learned to measure position instead of opacity.
    # centred over the gate it names. It used to start at x=546 — 16u to the
    # right of the line at 530 and 3px below the university credit, so it read
    # as the second line of a right-aligned credit block instead of as a label.
    s.append(f'<text x="530" y="316" class="lbl" text-anchor="middle">HUMAN APPROVAL</text>')
    s.append(f'<rect x="150" y="320" width="300" height="80" rx="3" fill="none" stroke="{INDIGO}"/>')
    s.append(f'<text x="166" y="340" class="lbl">DOCKER · SANDBOXED</text>')
    # "internal net (dev)": the beta deploy defaults EXECUTION_NETWORK to bridge

    s.append(f'<path id="approval-gate" d="M530 320V400" stroke="{WIRE}"/>')
    # It ends the loop past the gate and beside DEPLOYED, which is the point:
    # the gate is passed by a human saying yes, not by the pipeline waiting it
    # out. The rest check anchors the final pose to the label that explains it.
    s.append(f'<circle class="tk2" data-rest="deployed" data-rest-within="14" '
             f'cx="176" cy="372" r="6" fill="{INDIGO}" style="animation-delay:{-SET}s"/>')
    s.append(f'<text x="150" y="418" class="fine">non-root · read-only rootfs · internal net (dev)</text>')
    # DEPLOYED now sits on the token's own row, so the rest check anchors to a
    # label beside it rather than one 28u down and to the right.
    s.append(f'<text id="deployed" class="ok lbl" x="618" y="378" fill="{INDIGO}" style="animation-delay:{-SET}s">DEPLOYED</text>')

    # This used to be a 64px "2". The number was wrong — the reproducible count
    # of human-gate stages is four (preprocessing await_approval, feature
    # engineering await_review, training propose_model and await_review) — and
    # it was also the only hero on the page that no reader could check, because
    # this repository is private. A hero nobody can verify, carrying a figure
    # that is not even right, is the exact thing the rest of this page refuses.
    # So the count is gone and the mechanism stays.
    s.append(f'<text x="150" y="486" class="sub">HUMAN IN THE LOOP</text>')
    s.append(f'<text x="150" y="514" class="fine">approval before a step commits, and before a model trains</text>')
    s.append(f'<text x="150" y="538" class="fine" fill="{INK3}">the only section here you cannot check — this repository is private</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── PLATE VII
def plate_colophon() -> str:
    H = 264
    s = [head(H, "Colophon", "Six systems, five system cards and one expo booklet. Every number "
                             "here is traceable to the repository it came from, except AutoML's, "
                             "whose repository is private — and the page itself is animated SVG "
                             "with no JavaScript and no server.", key="plate-7-colophon.svg")]
    # This plate asserts "ANIMATED SVG" and used to be the only one that wasn't.
    LOOP, SET = 12.7, 10.0
    s.append(f""".rule{{stroke-dasharray:1;animation:sweep {LOOP}s {EASE} infinite;animation-delay:{-SET}s}}
@keyframes sweep{{0%{{stroke-dashoffset:1}}20%,100%{{stroke-dashoffset:0}}}}
</style>{slab(H, INDIGO)}""")
    s.append(rail("VII", "COLOPHON"))
    s.append(f'<path class="rule" d="M150 80H{W-150}" pathLength="1" stroke="{RULE}"/>')
    s.append(f'<text x="150" y="120" class="say">Six systems. Five system cards, one booklet.</text>')
    s.append(f'<text x="150" y="148" class="say">Every number traces to its repo.</text>')
    s.append(f'<text x="150" y="172" class="fine" fill="{INK3}">except AutoML’s — that repository is private, and the plate says so</text>')
    s.append(f'<text x="150" y="204" class="lbl">ANIMATED SVG · NO JAVASCRIPT · NO SERVER</text>')
    s.append(f'<text x="150" y="236" class="lbl">CS ’26 · MIAMI UNIVERSITY</text>')
    s.append(f'<text x="{R}" y="236" class="lbl" text-anchor="end">aesh.03.23@gmail.com</text>')
    return "".join(s) + "</svg>"


PLATES = {
    "plate-0-thesis.svg": plate_thesis, "plate-1-glyph.svg": plate_glyph,
    "plate-2-jetpack.svg": plate_jetpack, "plate-3-cadence.svg": plate_cadence,
    "plate-4-applied.svg": plate_applied, "plate-5-refusal.svg": plate_refusal,
    "plate-6-release.svg": plate_release, "plate-7-colophon.svg": plate_colophon,
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
