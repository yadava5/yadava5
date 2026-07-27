#!/usr/bin/env python3
"""
FALSIFIABLE — plate builder.

Every claim is followed by the mechanism that would catch it if it were a lie.

Design rules encoded here (each one is a finding, not a preference):
  * viewBox 880 wide — 36% more legible at mobile than 1200
  * nothing below 16 viewBox units; body copy belongs in markdown, not in art
  * opaque slab on every plate — refuses the light/dark problem entirely
  * near-coprime loop lengths so plates never beat into a synchronised pulse
  * the finished frame is authored; animation supplies the START, never the end
    (share cards and static renderers capture frame zero)
  * no animated filters — one animated blur costs more than 4000 animated rects
  * the rail exits every plate at x=120 and enters the next at x=120
"""
from __future__ import annotations
import base64, pathlib, random

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT.parent / "assets"
OUT.mkdir(exist_ok=True)
FONT = base64.b64encode((ROOT / "mono-subset.woff2").read_bytes()).decode()

W = 880
SLAB, EDGE = "#0B0C0E", "rgba(255,255,255,0.07)"
INK, INK2, INK3 = "#F7F8F8", "#8A8F98", "#62666D"
AMBER, CYAN = "#F5A524", "#22D3EE"
RAIL_X = 120

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


def head(h: int, title: str, desc: str, loop: float) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}" role="img" aria-label="{desc}">
<title>{title}</title><desc>{desc}</desc>
<style>
@font-face{{font-family:'M';src:url(data:font/woff2;base64,{FONT}) format('woff2')}}
text{{font-family:'M',ui-monospace,SFMono-Regular,Menlo,monospace}}
.lbl{{font-size:16px;letter-spacing:1.6px;fill:{INK3}}}
.key{{font-size:17px;letter-spacing:1.4px;fill:{INK2}}}
.big{{font-size:72px;letter-spacing:-1px;fill:{INK};font-weight:600}}
.unit{{font-size:29px;fill:{INK2}}}
.say{{font-size:19px;fill:{INK2}}}
"""


def slab(h: int) -> str:
    return (f'<rect width="{W}" height="{h}" rx="2" fill="{SLAB}"/>'
            f'<rect x="0.5" y="0.5" width="{W-1}" height="{h-1}" rx="2" fill="none" stroke="{EDGE}"/>')


def rail(h: int, accent: str) -> str:
    """the continuity device — same x on every plate, so the eye stitches
    across the markdown gap between images"""
    return (f'<path d="M{RAIL_X} 0V26" stroke="{accent}" stroke-width="1" opacity=".5"/>'
            f'<path d="M{RAIL_X} {h-26}V{h}" stroke="{accent}" stroke-width="1" opacity=".5"/>')


# ────────────────────────────────────────────────────────────── PLATE I
def plate_glyph() -> str:
    # H fits 7 rows of the 299-grid; SET parks the frozen frame after the grid
    # has fully faded up, so the still shows the whole argument.
    H, LOOP, SET = 524, 9.1, 7.6
    a = AMBER
    s = [head(H, "Glyph — 97.01%, and the 299 it gets wrong",
              "A handwritten seven draws itself; four instruction sets each return the same answer; "
              "the model scores 97.01 percent, and all 299 misclassified digits are shown.", LOOP)]
    s.append(f""".ink{{fill:none;stroke:{a};stroke-width:7;stroke-linecap:round;stroke-linejoin:round;
  stroke-dasharray:1;stroke-dashoffset:0;animation:draw {LOOP}s linear infinite;animation-delay:{-SET}s}}
@keyframes draw{{0%{{stroke-dashoffset:1}}17%{{stroke-dashoffset:0}}100%{{stroke-dashoffset:0}}}}
.tok{{animation:run {LOOP}s linear infinite}}
@keyframes run{{0%,24%{{opacity:0;transform:translateX(0)}}26%{{opacity:1}}
  41%{{opacity:1;transform:translateX(214px)}}44%,100%{{opacity:0;transform:translateX(214px)}}}}
.wrong{{opacity:.42;animation:show {LOOP}s linear infinite;animation-delay:{-SET}s}}
@keyframes show{{0%,62%{{opacity:0}}72%,100%{{opacity:.42}}}}
</style>{slab(H)}{rail(H, a)}""")

    # CLAIM — the seven, drawn by hand
    s.append(f'<g transform="translate(150,60) scale(1.15)"><path class="ink" d="{DIGITS[7]}" pathLength="1"/></g>')
    s.append(f'<text x="150" y="{60+200}" class="lbl">CLAIM</text>')

    # MECHANISM — four instruction sets, one answer
    isas = ["AVX-512", "AVX2", "NEON", "wasm128"]
    for i, name in enumerate(isas):
        y = 78 + i * 34
        s.append(f'<text x="330" y="{y+5}" class="key">{name}</text>')
        s.append(f'<path d="M446 {y}H660" stroke="{INK3}" stroke-width="1" opacity=".45"/>')
        s.append(f'<circle class="tok" cx="446" cy="{y}" r="4" fill="{a}" '
                 f'style="animation-delay:{round(-SET + i*0.06,3)}s"/>')
    s.append(f'<path d="M660 74V186" stroke="{INK3}" stroke-width="1" opacity=".45"/>')
    s.append(f'<text x="678" y="135" class="key" fill="{INK2}">same answer</text>')
    s.append(f'<text x="330" y="{60+200}" class="lbl">MECHANISM — four paths, one result</text>')

    # VERDICT
    s.append(f'<path d="M150 296H730" stroke="{EDGE}"/>')
    s.append(f'<text x="150" y="{296+56}" class="big">97.01<tspan class="unit">%</tspan></text>')
    s.append(f'<text x="470" y="{296+56}" class="key">MNIST TEST · n=10,000</text>')
    s.append(f'<text x="150" y="{296+92}" class="say">These are the 299 it gets wrong.</text>')

    # THE MOVE — every single digit it gets wrong
    rnd = random.Random(7)
    gx, gy, cols = 150, 412, 46
    for i in range(299):
        c, r = i % cols, i // cols
        x, y = gx + c * 12.4, gy + r * 14.0
        s.append(f'<g class="wrong" transform="translate({x:.1f},{y:.1f}) scale(0.072)" '
                 f'style="animation-delay:{round(-SET + (i%46)*0.004,3)}s">'
                 f'<path d="{DIGITS[rnd.randrange(10)]}" fill="none" stroke="{a}" stroke-width="15" '
                 f'stroke-linecap="round"/></g>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── PLATE V
def plate_refusal() -> str:
    H, LOOP, SET = 300, 6.7, 4.4
    s = [head(H, "The refusal — the database declines to return another tenant's rows",
              "A query from tenant A travels toward tenant B's rows, reaches the isolation boundary, "
              "and stops. Zero rows are returned.", LOOP)]
    s.append(f""".q{{animation:seek {LOOP}s linear infinite;animation-delay:{-SET}s}}
@keyframes seek{{0%{{opacity:0;transform:translateX(0)}}6%{{opacity:1;transform:translateX(0)}}
  /* it decelerates into the boundary and simply stops — no bounce, no alarm */
  28%{{opacity:1;transform:translateX(214px)}}32%{{opacity:1;transform:translateX(222px)}}
  40%{{opacity:0;transform:translateX(222px)}}100%{{opacity:0;transform:translateX(222px)}}}}
.zero{{animation:land {LOOP}s linear infinite;animation-delay:{-SET}s}}
@keyframes land{{0%,34%{{opacity:0}}42%,100%{{opacity:1}}}}
</style>{slab(H)}{rail(H, CYAN)}""")

    s.append(f'<text x="150" y="52" class="lbl">TENANT A</text>')
    s.append(f'<text x="596" y="52" class="lbl">TENANT B</text>')
    for i in range(4):
        y = 74 + i * 28
        s.append(f'<rect x="150" y="{y}" width="180" height="18" rx="2" fill="#12171B"/>')
        s.append(f'<rect x="596" y="{y}" width="180" height="18" rx="2" fill="#12171B"/>')

    # the boundary: a plain hairline that never reacts
    s.append(f'<path d="M462 62V196" stroke="{INK3}" stroke-width="1" opacity=".55"/>')
    s.append(f'<text x="470" y="210" class="lbl">ROW-LEVEL SECURITY</text>')

    s.append(f'<circle class="q" cx="340" cy="88" r="5" fill="{CYAN}"/>')
    s.append(f'<text x="150" y="216" class="key">SELECT * FROM tasks;</text>')

    s.append(f'<g class="zero"><text x="500" y="96" class="big" font-size="46">0 rows</text></g>')
    s.append(f'<path d="M150 236H730" stroke="{EDGE}"/>')
    s.append(f'<text x="150" y="262" class="say">The app didn\'t remember to filter. The database refused.</text>')
    s.append(f'<text x="150" y="286" class="lbl">IDOR FOUND 7 · FIXED 7 · FOUND BY THE AUTHOR</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── PLATE 00
def plate_thesis() -> str:
    H = 250
    s = [head(H, "Ayush Yadav — every number is followed by the thing that would catch it",
              "The thesis plate: Ayush Yadav, and the sentence 'Every number on this page is "
              "followed by the thing that would catch it.'", 0)]
    s.append(f""".rule{{stroke-dasharray:1;stroke-dashoffset:0;animation:sweep 5s cubic-bezier(.16,1,.3,1) 1 both}}
@keyframes sweep{{0%{{stroke-dashoffset:1}}22%,100%{{stroke-dashoffset:0}}}}
.tick{{animation:tk 5s ease-out 1 both}}
@keyframes tk{{0%,42%{{opacity:0}}56%,100%{{opacity:1}}}}
.ser{{font-family:ui-serif,Georgia,'Times New Roman',serif;font-size:31px;fill:{INK}}}
</style>{slab(H)}""")
    s.append(f'<text x="150" y="56" class="key" letter-spacing="5">AYUSH YADAV</text>')
    s.append(f'<text x="{W-150}" y="56" class="lbl" text-anchor="end">CS ’26 · MIAMI UNIVERSITY</text>')
    s.append(f'<path class="rule" d="M150 84H{W-150}" pathLength="1" stroke="{INK3}"/>')
    s.append(f'<text x="150" y="134" class="ser">Every number on this page is followed</text>')
    s.append(f'<text x="150" y="172" class="ser">by the thing that would catch it.</text>')
    accents = [AMBER, "#B8E62E", "#34D399", CYAN, "#818CF8", "#F472B6"]
    for i, c in enumerate(accents):   # the ONLY polychrome frame in the document
        s.append(f'<rect class="tick" x="{150+i*26}" y="200" width="14" height="4" rx="1" fill="{c}" '
                 f'style="animation-delay:{0.09*i:.2f}s"/>')
    s.append(f'<text x="{W-150}" y="208" class="lbl" text-anchor="end">SIX SYSTEMS</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── PLATE II
def plate_jetpack() -> str:
    H, LOOP, SET, a = 430, 10.3, 7.2, "#B8E62E"
    s = [head(H, "jetpack — 6.5x, verified bit-identical against java.util.zip",
              "Blocks flow through a bounded in-flight window and leave compressed; a SIMD Adler-32 "
              "checksum is compared digit by digit against java.util.zip and matches; a table of "
              "speedups includes a row where the optimisation loses.", LOOP)]
    s.append(f""".blk{{animation:sq {LOOP}s linear infinite;transform-box:fill-box;transform-origin:left center}}
@keyframes sq{{0%,14%{{transform:translateX(0) scaleX(1)}}44%{{transform:translateX(214px) scaleX(.42)}}
  60%,100%{{transform:translateX(214px) scaleX(.42)}}}}
.mt{{animation:mt {LOOP}s linear infinite}}
@keyframes mt{{0%,46%{{opacity:0}}58%,100%{{opacity:1}}}}
.row{{animation:rw {LOOP}s linear infinite}}
@keyframes rw{{0%,60%{{opacity:0}}70%,100%{{opacity:1}}}}
</style>{slab(H)}{rail(H, a)}""")
    s.append(f'<text x="150" y="66" class="big" font-size="60">6.5<tspan class="unit">×</tspan></text>')
    s.append(f'<text x="330" y="60" class="key">THROUGHPUT vs java.util.zip</text>')
    s.append(f'<text x="330" y="82" class="lbl">JDK 25 · VIRTUAL THREADS</text>')
    s.append(f'<text x="150" y="{66+28}" class="lbl">CLAIM</text>')

    # the bounded in-flight window — the bracket never overflows; that IS the point
    s.append(f'<path d="M400 120V236M400 120H420M400 236H420" stroke="{INK3}" stroke-width="1"/>')
    s.append(f'<path d="M636 120V236M636 120H616M636 236H616" stroke="{INK3}" stroke-width="1"/>')
    s.append(f'<text x="400" y="112" class="lbl">BOUNDED IN-FLIGHT WINDOW</text>')
    for i in range(4):
        y = 138 + i * 26
        s.append(f'<rect class="blk" x="180" y="{y}" width="196" height="16" rx="2" fill="{a}" opacity=".85" '
                 f'style="animation-delay:{round(-SET + i*0.22,3)}s"/>')
    s.append(f'<text x="150" y="256" class="lbl">MECHANISM — peak memory independent of file size</text>')

    # checksum audit: the fast path checked against the reference
    s.append(f'<text x="150" y="298" class="lbl">SIMD ADLER-32</text>')
    s.append(f'<text x="150" y="322" class="lbl">java.util.zip</text>')
    hexd = "1F3A9C4E"
    for i, ch in enumerate(hexd):
        x = 330 + i * 26
        s.append(f'<text x="{x}" y="298" class="key" fill="{INK}">{ch}</text>')
        s.append(f'<text x="{x}" y="322" class="key" fill="{INK}">{ch}</text>')
        s.append(f'<rect class="mt" x="{x-3}" y="304" width="20" height="2" fill="{a}" '
                 f'style="animation-delay:{round(-SET + i*0.05,3)}s"/>')
    s.append(f'<text x="560" y="312" class="say" fill="{a}">bit-identical</text>')

    # the verdict table — and the row where it loses, set in the same ink
    s.append(f'<path d="M150 346H730" stroke="{EDGE}"/>')
    rows = [("64 KiB", "1.9×"), ("256 KiB", "3.4×"), ("1 MiB", "6.5×"), ("4 MiB", "6.1×"), ("4 KiB", "0.94×")]
    for i, (blk, sp) in enumerate(rows):
        x = 150 + i * 118
        s.append(f'<text class="row" x="{x}" y="372" class="lbl" style="animation-delay:{round(-SET + i*0.18,3)}s">{blk}</text>')
        s.append(f'<text class="row" x="{x}" y="398" class="key" fill="{INK}" style="animation-delay:{round(-SET + i*0.18,3)}s">{sp}</text>')
    s.append(f'<text x="{W-150}" y="398" class="lbl" text-anchor="end">gzip -t → OK</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── PLATE III
def plate_cadence() -> str:
    H, LOOP, SET, a = 360, 7.9, 5.6, "#34D399"
    SENT, FS, CW = "lunch with sam friday 1pm", 26, 15.62
    s = [head(H, "Cadence — a parser that shows its work",
              "The sentence 'lunch with sam friday 1pm' is annotated in place by four parser stages "
              "labelling title, attendee, date and time, then filed into a calendar.", LOOP)]
    s.append(f""".ul{{animation:ul {LOOP}s linear infinite;transform-box:fill-box;transform-origin:left center}}
@keyframes ul{{0%,10%{{transform:scaleX(0);opacity:0}}14%{{opacity:1}}22%,100%{{transform:scaleX(1);opacity:1}}}}
.an{{animation:an {LOOP}s linear infinite}}
@keyframes an{{0%,12%{{opacity:0}}22%,100%{{opacity:1}}}}
.fil{{animation:fil {LOOP}s linear infinite}}
@keyframes fil{{0%,56%{{opacity:0}}68%,100%{{opacity:1}}}}
</style>{slab(H)}{rail(H, a)}""")
    s.append(f'<text x="150" y="52" class="lbl">CLAIM — plain English in, calendar out</text>')
    s.append(f'<text x="150" y="100" font-size="{FS}" fill="{INK}" letter-spacing="0">{SENT}</text>')
    # four passes annotating the SAME sentence in place — a linguist's gloss
    toks = [(0, 5, "TITLE"), (11, 3, "ATTENDEE"), (15, 6, "DATE"), (22, 3, "TIME")]
    for i, (start, ln, label) in enumerate(toks):
        x, w = 150 + start * CW, ln * CW
        dl = round(-SET + i * 0.5, 3)
        s.append(f'<rect class="ul" x="{x:.0f}" y="110" width="{w:.0f}" height="2" fill="{a}" '
                 f'style="animation-delay:{dl}s"/>')
        s.append(f'<text class="an" x="{x:.0f}" y="{132+ (i%2)*20}" class="lbl" fill="{a}" '
                 f'style="animation-delay:{dl}s">{label}</text>')
    s.append(f'<text x="150" y="196" class="lbl">MECHANISM — four stages, each one legible</text>')

    # filed
    s.append(f'<path d="M150 220H730" stroke="{EDGE}"/>')
    for d, day in enumerate(["MON", "TUE", "WED", "THU", "FRI"]):
        x = 150 + d * 116
        s.append(f'<text x="{x}" y="248" class="lbl">{day}</text>')
        s.append(f'<rect x="{x}" y="258" width="100" height="56" rx="3" fill="none" stroke="{EDGE}"/>')
    s.append(f'<g class="fil" style="animation-delay:{-SET}s">'
             f'<rect x="614" y="272" width="100" height="30" rx="3" fill="#0E2A22" stroke="{a}"/>'
             f'<text x="626" y="292" class="lbl" fill="{a}">1pm · sam</text></g>')
    s.append(f'<text x="150" y="340" class="lbl">34 HANDLERS BUNDLED INTO ONE FUNCTION · VERCEL CAP 12</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── PLATE IV
def plate_applied() -> str:
    H, LOOP, SET, a = 430, 11.7, 8.4, CYAN
    s = [head(H, "Applied — a classifier allowed to say it doesn't know",
              "Email falls through three classifier layers; messages that fail to clear the 0.85 "
              "confidence gate divert sideways to a human. Inference runs inside the browser.", LOOP)]
    s.append(f""".env{{animation:fall {LOOP}s linear infinite}}
@keyframes fall{{0%{{opacity:0;transform:translateY(-30px)}}6%{{opacity:1}}
  40%{{opacity:1;transform:translateY(150px)}}48%,100%{{opacity:0;transform:translateY(150px)}}}}
.div{{animation:dv {LOOP}s linear infinite}}
@keyframes dv{{0%{{opacity:0;transform:translate(0,-30px)}}6%{{opacity:1}}
  34%{{opacity:1;transform:translate(0,96px)}}48%{{opacity:1;transform:translate(150px,96px)}}
  58%,100%{{opacity:0;transform:translate(150px,96px)}}}}
.cm{{animation:cm {LOOP}s linear infinite}}
@keyframes cm{{0%,54%{{opacity:0}}64%,100%{{opacity:1}}}}
</style>{slab(H)}{rail(H, a)}""")
    s.append(f'<text x="150" y="62" class="big" font-size="56">0.979</text>')
    s.append(f'<text x="330" y="56" class="key">MACRO-F1 · HELD-OUT</text>')
    s.append(f'<text x="330" y="78" class="lbl">CI FAILS THE BUILD BELOW 0.95</text>')
    s.append(f'<text x="150" y="90" class="lbl">CLAIM</text>')

    gates = [("201 REGEX RULES", 138), ("e5 EMBEDDINGS", 178), ("SETFIT", 218)]
    for label, y in gates:
        s.append(f'<path d="M180 {y}H560" stroke="{INK3}" stroke-width="1" opacity=".5" stroke-dasharray="4 5"/>')
        s.append(f'<text x="576" y="{y+5}" class="lbl">{label}</text>')
    # the gate that is allowed to decline
    s.append(f'<path d="M180 262H560" stroke="{a}" stroke-width="1"/>')
    s.append(f'<text x="576" y="267" class="lbl" fill="{a}">0.85 CONFIDENCE GATE</text>')
    for i in range(5):
        x = 196 + i * 68
        s.append(f'<rect class="env" x="{x}" y="100" width="30" height="20" rx="2" fill="none" '
                 f'stroke="{a}" stroke-width="1.6" style="animation-delay:{round(-SET + i*0.5,3)}s"/>')
    for i in range(2):
        x = 400 + i * 68
        s.append(f'<rect class="div" x="{x}" y="100" width="30" height="20" rx="2" fill="none" '
                 f'stroke="{AMBER}" stroke-width="1.6" style="animation-delay:{round(-SET + 0.3 + i*0.5,3)}s"/>')
    s.append(f'<circle cx="700" cy="212" r="11" fill="none" stroke="{AMBER}" stroke-width="1.4"/>')
    s.append(f'<text x="676" y="240" class="lbl" fill="{AMBER}">A HUMAN</text>')
    s.append(f'<text x="150" y="300" class="say">It is allowed to say it doesn’t know.</text>')

    s.append(f'<path d="M150 326H730" stroke="{EDGE}"/>')
    s.append(f'<text x="150" y="352" class="lbl">CONFUSION MATRIX — INCLUDING THE OFF-DIAGONAL</text>')
    for r in range(4):
        for c in range(4):
            on = r == c
            s.append(f'<rect class="cm" x="{150+c*17}" y="{362+r*17}" width="13" height="13" rx="1" '
                     f'fill="{a}" opacity="{0.9 if on else 0.22}" '
                     f'style="animation-delay:{round(-SET + (r*4+c)*0.02,3)}s"/>')
    s.append(f'<rect x="300" y="356" width="240" height="52" rx="3" fill="none" stroke="{INK3}" opacity=".6"/>')
    s.append(f'<text x="316" y="378" class="lbl">YOUR BROWSER</text>')
    s.append(f'<text x="316" y="398" class="lbl" fill="{INK2}">int8 ONNX · 0 server calls</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── PLATE VI
def plate_release() -> str:
    H, LOOP, SET = 360, 13.1, 9.0
    m, ind = "#F472B6", "#818CF8"
    s = [head(H, "LifeQuest and Agentic AutoML",
              "A daily routine becomes three mission nodes on a path; and a dataset moves through a "
              "sandboxed pipeline that waits for human approval before deploying.", LOOP)]
    s.append(f""".nd{{animation:nd {LOOP}s linear infinite}}
@keyframes nd{{0%,8%{{opacity:0}}18%,100%{{opacity:1}}}}
.tk2{{animation:tk2 {LOOP}s linear infinite}}
@keyframes tk2{{0%,30%{{opacity:0;transform:translateX(0)}}36%{{opacity:1;transform:translateX(0)}}
  50%{{opacity:1;transform:translateX(150px)}}
  /* the longest dead hold in the document: it waits for a human */
  70%{{opacity:1;transform:translateX(150px)}}80%,100%{{opacity:1;transform:translateX(320px)}}}}
.ok{{animation:ok {LOOP}s linear infinite}}
@keyframes ok{{0%,66%{{opacity:0}}72%,100%{{opacity:1}}}}
</style>{slab(H)}{rail(H, m)}""")
    s.append(f'<text x="150" y="52" class="lbl">LIFEQUEST</text>')
    for i, txt in enumerate(["walk 20 min", "apply to 2 roles", "meet-up"]):
        x = 150 + i * 196
        s.append(f'<circle class="nd" cx="{x+8}" cy="96" r="7" fill="none" stroke="{m}" stroke-width="1.6" '
                 f'style="animation-delay:{round(-SET + i*0.3,3)}s"/>')
        if i < 2:
            s.append(f'<path d="M{x+22} 96H{x+180}" stroke="{m}" stroke-width="1" opacity=".45"/>')
        s.append(f'<text x="{x}" y="126" class="lbl">{txt}</text>')
    s.append(f'<text x="150" y="160" class="say">For people rebuilding structure after a layoff.</text>')

    s.append(f'<path d="M150 190H730" stroke="{EDGE}"/>')
    s.append(f'<text x="150" y="218" class="lbl">AGENTIC AUTOML</text>')
    s.append(f'<rect x="300" y="238" width="170" height="56" rx="3" fill="none" stroke="{ind}" opacity=".7"/>')
    s.append(f'<text x="312" y="258" class="lbl" fill="{ind}">DOCKER · SANDBOXED</text>')
    s.append(f'<text x="312" y="284" class="lbl">it cannot leave this box</text>')
    s.append(f'<path d="M520 238V294" stroke="{INK3}"/>')
    s.append(f'<text x="534" y="262" class="lbl">HUMAN</text>')
    s.append(f'<text x="534" y="282" class="lbl">APPROVAL</text>')
    s.append(f'<circle class="tk2" cx="180" cy="266" r="6" fill="{ind}" style="animation-delay:{-SET}s"/>')
    s.append(f'<text class="ok" x="640" y="270" class="lbl" fill="{ind}" style="animation-delay:{-SET}s">DEPLOYED</text>')
    s.append(f'<text x="150" y="336" class="lbl">SENIOR DESIGN · MIAMI UNIVERSITY · CO-BUILT</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── PLATE VII
def plate_colophon() -> str:
    H = 150
    s = [head(H, "Colophon", "Six systems, six system cards; rendered as animated SVG with no "
                             "JavaScript and no server.", 0)]
    s.append("</style>" + slab(H))
    s.append(f'<path d="M150 40H{W-150}" stroke="{EDGE}"/>')
    lines = ["Six systems. Six system cards. Every number traces to a committed benchmark.",
             "Rendered as animated SVG. No JavaScript. No server drew this frame.",
             "CS ’26 · Miami University · aesh.03.23@gmail.com"]
    for i, ln in enumerate(lines):
        s.append(f'<text x="150" y="{74 + i*28}" class="lbl" fill="{INK3}">{ln}</text>')
    return "".join(s) + "</svg>"


PLATES = {
    "plate-0-thesis.svg": plate_thesis, "plate-1-glyph.svg": plate_glyph,
    "plate-2-jetpack.svg": plate_jetpack, "plate-3-cadence.svg": plate_cadence,
    "plate-4-applied.svg": plate_applied, "plate-5-refusal.svg": plate_refusal,
    "plate-6-release.svg": plate_release, "plate-7-colophon.svg": plate_colophon,
}
for fn, gen in PLATES.items():
    (OUT / fn).write_text(gen())
    print(f"{fn}: {(OUT / fn).stat().st_size:,} bytes")
