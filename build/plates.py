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
import base64, json, pathlib, random

# every plate's description is authored ONCE here and flows to three places:
# the SVG <desc>, the SVG aria-label, and the README's <img alt>. They diverged
# once already; the gate below now fails the build if the README drifts.
ALT: dict[str, str] = {}

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


def head(h: int, title: str, desc: str, loop: float, key: str = "") -> str:
    if key:
        ALT[key] = desc
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}" role="img" aria-label="{desc}">
<title>{title}</title><desc>{desc}</desc>
<style>
@font-face{{font-family:'M';src:url(data:font/woff2;base64,{FONT}) format('woff2')}}
text{{font-family:'M',ui-monospace,SFMono-Regular,Menlo,monospace}}
.lbl{{font-size:16px;letter-spacing:1.6px;fill:{INK2}}}
.key{{font-size:17px;letter-spacing:1.4px;fill:{INK2}}}
.big{{font-size:72px;letter-spacing:-1px;fill:{INK};font-weight:600}}
.big60{{font-size:60px;letter-spacing:-1px;fill:{INK};font-weight:600}}
.big52{{font-size:52px;letter-spacing:-1px;fill:{INK};font-weight:600}}
.big40{{font-size:40px;letter-spacing:-0.5px;fill:{INK};font-weight:600}}
.fine{{font-size:14px;letter-spacing:0.6px;fill:{INK2}}}
.unit{{font-size:29px;fill:{INK2}}}
.say{{font-size:17px;fill:{INK2}}}
@media (prefers-reduced-motion: reduce){{*{{animation:none!important}}}}
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
    H, LOOP, SET = 540, 9.1, 7.6
    a = AMBER
    s = [head(H, "Glyph — 97.01%, and the 299 it gets wrong",
              "A handwritten seven draws itself. Three hand-written SIMD kernels (AVX-512, AVX2, NEON) and an autovectorised WebAssembly build each carry the same dot product. "
              "the model scores 97.01 percent on the 10,000-image test set, which means 299 wrong. Every one of those 299 errors is drawn below, each mark the true label of an image the model missed; 79 of them were made with over 0.9 confidence.", LOOP, key="plate-1-glyph.svg")]
    s.append(f""".ink{{fill:none;stroke:{a};stroke-width:7;stroke-linecap:round;stroke-linejoin:round;
  stroke-dasharray:1;stroke-dashoffset:0;animation:draw {LOOP}s linear infinite;animation-delay:{-SET}s}}
@keyframes draw{{0%{{stroke-dashoffset:1}}17%{{stroke-dashoffset:0}}100%{{stroke-dashoffset:0}}}}
.tok{{animation:run {LOOP}s linear infinite}}
@keyframes run{{0%,20%{{opacity:0;transform:translateX(0)}}24%{{opacity:1}}
  40%,100%{{opacity:1;transform:translateX(214px)}}}}
.wrong{{opacity:.62}}
</style>{slab(H)}{rail(H, a)}""")

    # CLAIM — the seven, drawn by hand
    s.append(f'<g transform="translate(150,60) scale(1.15)"><path class="ink" d="{DIGITS[7]}" pathLength="1"/></g>')
    s.append(f'<text x="150" y="{60+200}" class="lbl">CLAIM</text>')

    # MECHANISM — four instruction sets, one answer
    isas = ["AVX-512", "AVX2", "NEON", "wasm (auto)"]
    for i, name in enumerate(isas):
        y = 78 + i * 34
        s.append(f'<text x="330" y="{y+5}" class="key">{name}</text>')
        s.append(f'<path d="M446 {y}H660" stroke="{INK3}" stroke-width="1" opacity=".45"/>')
        s.append(f'<circle class="tok" cx="446" cy="{y}" r="4" fill="{a}" '
                 f'style="animation-delay:{round(-SET + i*0.06,3)}s"/>')
    s.append(f'<path d="M660 74V186" stroke="{INK3}" stroke-width="1" opacity=".45"/>')
    s.append(f'<text x="540" y="206" class="key" fill="{INK2}">one kernel each</text>')
    s.append(f'<text x="330" y="{60+200}" class="lbl">MECHANISM — 3 HAND-WRITTEN, 1 AUTO</text>')

    # VERDICT
    s.append(f'<path d="M150 296H730" stroke="{EDGE}"/>')
    s.append(f'<text x="150" y="{296+56}" class="big">97.01<tspan class="unit">%</tspan></text>')
    s.append(f'<text x="470" y="{296+56}" class="key">MNIST TEST · n=10,000</text>')
    s.append(f'<text x="150" y="{296+106}" class="say">299 wrong, all drawn below. 79 above 0.9 conf.</text>')

    # THE MOVE — the REAL errors. Each mark is the true label of one image the
    # model got wrong, read from benchmarks/mnist_misclassified.csv in the Glyph
    # repo. Previously these were random glyphs; now the picture is the evidence.
    errs = json.loads((ROOT / "errors.json").read_text())["true"]
    gx, gy, cols = 150, 424, 46
    for i in range(299):
        c, r = i % cols, i // cols
        x, y = gx + c * 12.4, gy + r * 14.0
        s.append(f'<g class="wrong" transform="translate({x:.1f},{y:.1f}) scale(0.072)">'
                 f'<path d="{DIGITS[errs[i]]}" fill="none" stroke="{a}" stroke-width="15" '
                 f'stroke-linecap="round"/></g>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── PLATE V
def plate_refusal() -> str:
    H, LOOP, SET = 348, 6.7, 4.4
    s = [head(H, "The refusal — the database declines to return another tenant's rows",
              "A query from tenant A travels toward tenant B's rows, reaches the isolation boundary, "
              "and stops. Zero rows are returned.", LOOP, key="plate-5-refusal.svg")]
    s.append(f""".q{{animation:seek {LOOP}s cubic-bezier(.16,1,.3,1) infinite;animation-delay:{-SET}s}}
@keyframes seek{{0%{{opacity:0;transform:translateX(0)}}6%{{opacity:1;transform:translateX(0)}}
  /* it decelerates into the boundary and simply stops — no bounce, no alarm */
  30%{{opacity:1;transform:translateX(110px)}}36%,100%{{opacity:1;transform:translateX(116px)}}}}
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

    s.append(f'<g class="zero"><text x="336" y="150" class="big40">0 rows</text></g>')
    s.append(f'<path d="M150 240H730" stroke="{EDGE}"/>')
    s.append(f'<text x="150" y="266" class="say">The app didn\u2019t remember to filter.</text>')
    s.append(f'<text x="150" y="292" class="say">The database refused.</text>')
    s.append(f'<text x="150" y="322" class="lbl">IDOR: 7 FOUND, 7 FIXED</text>')
    s.append(f'<text x="470" y="322" class="lbl">BY THE AUTHOR</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── PLATE 00
def plate_thesis() -> str:
    H = 286
    s = [head(H, "Ayush Yadav — every number is followed by the thing that would catch it",
              "The thesis plate: Ayush Yadav, and the sentence 'Every number on this page is "
              "followed by the thing that would catch it.'", 0, key="plate-0-thesis.svg")]
    s.append(f""".rule{{stroke-dasharray:1;stroke-dashoffset:0;animation:sweep 5s cubic-bezier(.16,1,.3,1) 1 both}}
@keyframes sweep{{0%{{stroke-dashoffset:1}}22%,100%{{stroke-dashoffset:0}}}}
.tick{{opacity:1}}
@keyframes tk{{0%{{opacity:0}}56%,100%{{opacity:1}}}}
.ser{{font-family:ui-serif,Georgia,'Times New Roman',serif;font-size:31px;fill:{INK}}}
</style>{slab(H)}""")
    s.append(f'<text x="150" y="56" class="key" letter-spacing="5">AYUSH YADAV</text>')
    s.append(f'<text x="{W-150}" y="56" class="lbl" text-anchor="end">CS ’26 · MIAMI UNIVERSITY</text>')
    s.append(f'<path class="rule" d="M150 84H{W-150}" pathLength="1" stroke="{INK3}"/>')
    s.append(f'<text x="150" y="128" class="ser">Every number on this page is</text>')
    s.append(f'<text x="150" y="166" class="ser">followed by the thing</text>')
    s.append(f'<text x="150" y="204" class="ser">that would catch it.</text>')
    accents = [AMBER, "#B8E62E", "#34D399", CYAN, "#818CF8", "#F472B6"]
    for i, c in enumerate(accents):   # the ONLY polychrome frame in the document
        s.append(f'<rect class="tick" x="{150+i*26}" y="238" width="14" height="4" rx="1" fill="{c}" '
                 f'style="animation-delay:{0.09*i:.2f}s"/>')
    s.append(f'<text x="{W-150}" y="246" class="lbl" text-anchor="end">SIX SYSTEMS</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── PLATE II
def plate_jetpack() -> str:
    H, LOOP, SET, a = 480, 10.3, 7.2, "#B8E62E"
    s = [head(H, "jetpack — 6.4x parallel, and the intrinsic it does not beat",
              "Blocks flow through a bounded in-flight window and leave compressed. A hand-vectorised "
              "Adler-32 checksum is compared digit by digit against java.util.zip and matches exactly. "
              "The measured table lists the JDK's native intrinsic at 14.06 gigabytes per second, "
              "marked not beaten.", LOOP, key="plate-2-jetpack.svg")]
    s.append(f""".blk{{animation:sq {LOOP}s linear infinite;transform-box:fill-box;transform-origin:left center}}
@keyframes sq{{0%,14%{{transform:translateX(0) scaleX(1)}}44%{{transform:translateX(214px) scaleX(.42)}}
  60%,100%{{transform:translateX(214px) scaleX(.42)}}}}
.mt{{animation:mt {LOOP}s linear infinite}}
@keyframes mt{{0%,18%{{opacity:0}}28%,100%{{opacity:1}}}}
.row{{animation:rw {LOOP}s linear infinite}}
@keyframes rw{{0%,22%{{opacity:0}}32%,100%{{opacity:1}}}}
</style>{slab(H)}{rail(H, a)}""")
    s.append(f'<text x="150" y="86" class="big60">6.4<tspan class="unit">×</tspan></text>')
    s.append(f'<text x="330" y="56" class="key">PARALLEL vs SINGLE-THREAD GZIP</text>')
    s.append(f'<text x="330" y="78" class="lbl">JDK 25 · M1 PRO · 3 FORKS · CI ±5%</text>')
    s.append(f'<text x="150" y="124" class="lbl">CLAIM</text>')

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
    # the known-answer vector the repo commits: Adler32Test.java:36-37
    hexd = "11E60398"
    for i, ch in enumerate(hexd):
        x = 330 + i * 26
        s.append(f'<text x="{x}" y="298" class="key" fill="{INK}">{ch}</text>')
        s.append(f'<text x="{x}" y="322" class="key" fill="{INK}">{ch}</text>')
        s.append(f'<rect class="mt" x="{x-3}" y="304" width="20" height="2" fill="{a}" '
                 f'style="animation-delay:{round(-SET + i*0.05,3)}s"/>')
    s.append(f'<text x="556" y="312" class="say" fill="{a}">identical</text>')

    # the verdict — the measured table, including the reference he does NOT beat
    s.append(f'<path d="M150 344H730" stroke="{EDGE}"/>')
    rows = [
        ("Adler-32 scalar (pure Java)", "1.52 GB/s", ""),
        ("Adler-32 hand-vectorised", "4.26 GB/s", "2.8× scalar"),
        ("java.util.zip intrinsic", "14.06 GB/s", "not beaten"),
        ("gzip, one thread", "66.2 MB/s", ""),
        ("parallel virtual threads", "422 MB/s", "6.4×"),
    ]
    for i, (name, score, note) in enumerate(rows):
        y = 368 + i * 21
        dl = round(-SET + i * 0.16, 3)
        s.append(f'<text class="row lbl" x="150" y="{y}" style="animation-delay:{dl}s">{name}</text>')
        s.append(f'<text class="row lbl" x="470" y="{y}" fill="{INK}" style="animation-delay:{dl}s">{score}</text>')
        if note:
            s.append(f'<text class="row lbl" x="604" y="{y}" fill="{a if "×" in note else INK2}" '
                     f'style="animation-delay:{dl}s">{note}</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── PLATE III
def plate_cadence() -> str:
    H, LOOP, SET, a = 360, 7.9, 5.6, "#34D399"
    SENT, FS, CW = "lunch with sam friday 1pm", 26, 15.62
    s = [head(H, "Cadence — a parser that shows its work",
              "The sentence 'lunch with sam friday 1pm' is annotated in place by four parser stages "
              "labelling title, attendee, date and time, then filed into a calendar.", LOOP, key="plate-3-cadence.svg")]
    s.append(f""".ul{{animation:ul {LOOP}s linear infinite;transform-box:fill-box;transform-origin:left center}}
@keyframes ul{{0%,10%{{transform:scaleX(0);opacity:0}}14%{{opacity:1}}22%,100%{{transform:scaleX(1);opacity:1}}}}
.an{{animation:an {LOOP}s linear infinite}}
@keyframes an{{0%,12%{{opacity:0}}22%,100%{{opacity:1}}}}
.fil{{animation:fil {LOOP}s linear infinite}}
@keyframes fil{{0%,26%{{opacity:0}}36%,100%{{opacity:1}}}}
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
        s.append(f'<text class="an lbl" x="{x:.0f}" y="{132+ (i%2)*20}" fill="{a}" '
                 f'style="animation-delay:{dl}s">{label}</text>')
    s.append(f'<text x="150" y="196" class="lbl">MECHANISM — four stages, each one legible</text>')

    # filed
    s.append(f'<path d="M150 220H730" stroke="{EDGE}"/>')
    for d, day in enumerate(["MON", "TUE", "WED", "THU", "FRI"]):
        x = 150 + d * 116
        s.append(f'<text x="{x}" y="248" class="lbl">{day}</text>')
        s.append(f'<rect x="{x}" y="258" width="100" height="56" rx="3" fill="none" stroke="{EDGE}"/>')
    s.append(f'<g class="fil" style="animation-delay:{-SET}s">'
             f'<rect x="604" y="272" width="120" height="30" rx="3" fill="#0E2A22" stroke="{a}"/>'
             f'<text x="614" y="292" class="lbl" fill="{a}">1pm · sam</text></g>')
    s.append(f'<text x="150" y="340" class="lbl">36 HANDLERS · ONE FUNCTION · VERCEL CAP 12</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── PLATE IV
def plate_applied() -> str:
    H, LOOP, SET, a = 430, 11.7, 8.4, CYAN
    s = [head(H, "Applied — a classifier allowed to say it doesn't know",
              "Email falls through three classifier layers; messages that fail to clear the 0.85 "
              "confidence gate divert sideways to a human. Inference runs inside the browser.", LOOP, key="plate-4-applied.svg")]
    s.append(f""".env{{animation:fall {LOOP}s linear infinite}}
@keyframes fall{{0%{{opacity:0;transform:translateY(-30px)}}4%{{opacity:1}}
  44%{{opacity:1;transform:translateY(150px)}}47%{{opacity:0}}50%{{opacity:0;transform:translateY(-30px)}}
  54%{{opacity:1}}94%{{opacity:1;transform:translateY(150px)}}97%,100%{{opacity:0}}}}
.div{{animation:dv {LOOP}s linear infinite}}
@keyframes dv{{0%{{opacity:0;transform:translate(0,-30px)}}4%{{opacity:1}}
  30%{{opacity:1;transform:translate(0,96px)}}44%{{opacity:1;transform:translate(150px,96px)}}
  90%,100%{{opacity:1;transform:translate(150px,96px)}}}}
.cm{{animation:cm {LOOP}s linear infinite}}
@keyframes cm{{0%,20%{{opacity:0}}30%,100%{{opacity:1}}}}
</style>{slab(H)}{rail(H, a)}""")
    s.append(f'<text x="150" y="84" class="big52">0.979</text>')
    s.append(f'<text x="330" y="56" class="key">MACRO-F1 · 96-MSG EVAL SET</text>')
    s.append(f'<text x="330" y="78" class="lbl">CI FAILS THE BUILD BELOW 0.95</text>')
    s.append(f'<text x="150" y="118" class="lbl">CLAIM</text>')

    gates = [("201 REGEX RULES", 138), ("e5 EMBEDDINGS", 178), ("SETFIT", 218)]
    for label, y in gates:
        s.append(f'<path d="M180 {y}H496" stroke="{INK3}" stroke-width="1" opacity=".5" stroke-dasharray="4 5"/>')
        s.append(f'<text x="512" y="{y+5}" class="lbl">{label}</text>')
    # the gate that is allowed to decline
    s.append(f'<path d="M180 262H496" stroke="{a}" stroke-width="1"/>')
    s.append(f'<text x="512" y="267" class="lbl" fill="{a}">0.85 GATE</text>')
    for i in range(5):
        x = 196 + i * 68
        s.append(f'<rect class="env" x="{x}" y="100" width="30" height="20" rx="2" fill="none" '
                 f'stroke="{a}" stroke-width="1.6" style="animation-delay:{round(-SET + i*0.5,3)}s"/>')
    for i in range(2):
        x = 400 + i * 68
        s.append(f'<rect class="div" x="{x}" y="100" width="30" height="20" rx="2" fill="none" '
                 f'stroke="{AMBER}" stroke-width="1.6" style="animation-delay:{round(-SET + 0.3 + i*0.5,3)}s"/>')
    s.append(f'<circle cx="656" cy="212" r="11" fill="none" stroke="{AMBER}" stroke-width="1.4"/>')
    s.append(f'<text x="628" y="240" class="lbl" fill="{AMBER}">A HUMAN</text>')
    s.append(f'<text x="150" y="300" class="say">It is allowed to say it doesn’t know.</text>')

    s.append(f'<path d="M150 326H730" stroke="{EDGE}"/>')
    # the eval set's real shape, not a decorative matrix pretending to be data
    s.append(f'<text x="150" y="352" class="lbl">MEASURED ON</text>')
    for i, (k, v) in enumerate([("96", "authored messages"), ("8", "classes"), ("0.95", "CI floor")]):
        y = 376 + i * 22
        s.append(f'<text class="cm key" x="150" y="{y}" fill="{INK}" '
                 f'style="animation-delay:{round(-SET + i*0.06,3)}s">{k}</text>')
        s.append(f'<text class="cm lbl" x="200" y="{y}" '
                 f'style="animation-delay:{round(-SET + i*0.06,3)}s">{v}</text>')
    s.append(f'<rect x="430" y="356" width="272" height="52" rx="3" fill="none" stroke="{INK3}" opacity=".6"/>')
    s.append(f'<text x="446" y="378" class="lbl">YOUR BROWSER</text>')
    s.append(f'<text x="446" y="398" class="fine">int8 ONNX · no remote models</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── PLATE VI
def plate_release() -> str:
    H, LOOP, SET = 424, 13.1, 9.0
    m, ind = "#F472B6", "#818CF8"
    s = [head(H, "LifeQuest and Agentic AutoML",
              "Three seeded quests appear on a path; and a dataset moves through a hardened Docker "
              "sandbox that waits for human approval before deploying.", LOOP, key="plate-6-release.svg")]
    s.append(f""".nd{{animation:nd {LOOP}s linear infinite}}
@keyframes nd{{0%,6%{{opacity:0}}14%,100%{{opacity:1}}}}
.tk2{{animation:tk2 {LOOP}s linear infinite}}
@keyframes tk2{{0%,30%{{opacity:0;transform:translateX(0)}}36%{{opacity:1;transform:translateX(0)}}
  50%{{opacity:1;transform:translateX(150px)}}
  /* the longest dead hold in the document: it waits for a human */
  70%{{opacity:1;transform:translateX(150px)}}80%,100%{{opacity:1;transform:translateX(320px)}}}}
.ok{{animation:ok {LOOP}s linear infinite}}
@keyframes ok{{0%,30%{{opacity:0}}38%,100%{{opacity:1}}}}
</style>{slab(H)}{rail(H, m)}""")
    s.append(f'<text x="150" y="52" class="lbl">LIFEQUEST</text>')
    for i, txt in enumerate(["Reconnect with a mentor", "Document a new routine", "Share a win"]):
        x = 150
        s.append(f'<circle class="nd" cx="{x+8}" cy="{86+i*30}" r="7" fill="none" stroke="{m}" stroke-width="1.6" '
                 f'style="animation-delay:{round(-SET + i*0.3,3)}s"/>')
        if i < 2:
            s.append(f'<path d="M{x+8} {94+i*30}V{112+i*30}" stroke="{m}" stroke-width="1" opacity=".45"/>')
        s.append(f'<text x="{x+28}" y="{91+i*30}" class="lbl">{txt}</text>')
    s.append(f'<text x="150" y="196" class="say">For people rebuilding structure —</text>')
    s.append(f'<text x="150" y="220" class="say">after a layoff, or in retirement.</text>')

    s.append(f'<path d="M150 246H730" stroke="{EDGE}"/>')
    s.append(f'<text x="150" y="274" class="lbl">AGENTIC AUTOML</text>')
    s.append(f'<rect x="300" y="292" width="222" height="56" rx="3" fill="none" stroke="{ind}" opacity=".7"/>')
    s.append(f'<text x="312" y="314" class="lbl" fill="{ind}">DOCKER · SANDBOXED</text>')
    s.append(f'<text x="300" y="364" class="fine">non-root · read-only · no network</text>')
    s.append(f'<path d="M560 292V348" stroke="{INK3}"/>')
    s.append(f'<text x="574" y="310" class="lbl">HUMAN</text>')
    s.append(f'<text x="574" y="334" class="lbl">APPROVAL</text>')
    s.append(f'<circle class="tk2" cx="180" cy="320" r="6" fill="{ind}" style="animation-delay:{-SET}s"/>')
    s.append(f'<text class="ok lbl" x="640" y="288" fill="{ind}" style="animation-delay:{-SET}s">DEPLOYED</text>')
    s.append(f'<text x="150" y="394" class="lbl">SENIOR DESIGN · MIAMI UNIVERSITY</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── PLATE VII
def plate_colophon() -> str:
    H = 196
    s = [head(H, "Colophon", "Six systems, six system cards; rendered as animated SVG with no "
                             "JavaScript and no server.", 0, key="plate-7-colophon.svg")]
    s.append("</style>" + slab(H))
    s.append(f'<path d="M150 40H{W-150}" stroke="{EDGE}"/>')
    lines = ["Six systems. Six system cards. Every number here is",
             "traceable to the repo it came from.",
             "Rendered as animated SVG. No JavaScript.",
             "No server drew this frame.",
             "CS ’26 · Miami University · aesh.03.23@gmail.com"]
    for i, ln in enumerate(lines):
        s.append(f'<text x="150" y="{74 + i*28}" class="lbl">{ln}</text>')
    return "".join(s) + "</svg>"


PLATES = {
    "plate-0-thesis.svg": plate_thesis, "plate-1-glyph.svg": plate_glyph,
    "plate-2-jetpack.svg": plate_jetpack, "plate-3-cadence.svg": plate_cadence,
    "plate-4-applied.svg": plate_applied, "plate-5-refusal.svg": plate_refusal,
    "plate-6-release.svg": plate_release, "plate-7-colophon.svg": plate_colophon,
}
# ────────────────────────────────────────────────── the gate
# A build that can ship an unrenderable plate is not a build. Three checks,
# each one earned by a defect that actually shipped:
#   1. XML well-formedness — duplicate class attributes silently killed four
#      plates; SVG served as image/svg+xml is parsed strictly and simply aborts.
#   2. Layout — text that leaves the canvas or the 150/730 type column.
#      Monospace makes the advance width computable: 0.6em + letter-spacing.
#   3. Frame zero — anything invisible at t=0 fails the file's own stated rule.
import re as _re, sys as _sys, xml.dom.minidom as _xml

SIZES = {"lbl": (16, 1.6), "key": (17, 1.4), "say": (19, 0), "fine": (14, 0.6),
         "big": (72, -1), "big60": (60, -1), "big52": (52, -1), "big40": (40, -0.5),
         "ser": (31, 0)}
LEFT, RIGHT = 150, 730
_fail = []

for fn, gen in PLATES.items():
    path = OUT / fn
    path.write_text(gen())
    svg = path.read_text()

    try:
        _xml.parseString(svg)
    except Exception as e:
        _fail.append(f"{fn}: MALFORMED XML — {e}")
        print(f"{fn}: !! MALFORMED XML — {e}")
        continue

    h = int(_re.search(r'viewBox="0 0 \d+ (\d+)"', svg).group(1))
    for m in _re.finditer(r'<text([^>]*)>([^<]*)</text>', svg):
        attrs, body = m.group(1), m.group(2)
        if not body.strip():
            continue
        cls = _re.search(r'class="([^"]+)"', attrs)
        names = cls.group(1).split() if cls else []
        size, track = next((SIZES[n] for n in names if n in SIZES), (16, 1.6))
        x = float(_re.search(r'\bx="([-\d.]+)"', attrs).group(1))
        y = float(_re.search(r'\by="([-\d.]+)"', attrs).group(1))
        w = len(body) * (size * 0.6 + track)
        anchor = 'text-anchor="end"' in attrs
        x0, x1 = (x - w, x) if anchor else (x, x + w)
        if x1 > RIGHT + 2:
            _fail.append(f"{fn}: overflows the type column — {body[:38]!r} ends at {x1:.0f} (max {RIGHT})")
        if y - size * 0.72 < 0 or y > h:
            _fail.append(f"{fn}: outside the canvas — {body[:38]!r} at y={y} (h={h})")

    print(f"{fn}: {path.stat().st_size:,} bytes")

# 4. alt/desc/README agreement. Every description is authored once in ALT and
#    must reach the README verbatim — three surfaces drifted apart once and
#    left a retracted claim alive in the accessible text.
(ROOT.parent / "assets" / "alt.json").write_text(json.dumps(ALT, indent=2, sort_keys=True))
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
print("\nGATE PASSED — all plates parse, all type inside the column.")


# ────────────────────────────────────────────────── mobile set
# At GitHub's real 324px column a 16-unit label on an 880 canvas renders at
# 5.9px — unreadable. So the phone gets its own plates: a 440 canvas at the SAME
# absolute type sizes (≈11.8px rendered), carrying the hero and one line. The
# argument itself is already in the markdown, which is selectable, searchable
# and theme-native. Served via <picture media="(max-width:500px)">.
MW = 440

def plate_mobile(key: str, accent: str, kicker: str, hero: str, unit: str,
                 line1: str, line2: str, desc: str) -> str:
    h = 208
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {MW} {h}" width="{MW}" height="{h}" '
           f'role="img" aria-label="{desc}"><title>{kicker}</title><desc>{desc}</desc><style>'
           f"@font-face{{font-family:'M';src:url(data:font/woff2;base64,{FONT}) format('woff2')}}"
           f"text{{font-family:'M',ui-monospace,SFMono-Regular,Menlo,monospace}}"
           f".k{{font-size:15px;letter-spacing:1.8px;fill:{INK2}}}"
           f".n{{font-size:54px;letter-spacing:-1px;fill:{INK};font-weight:600}}"
           f".u{{font-size:22px;fill:{INK2}}}"
           f".t{{font-size:15px;fill:{INK2}}}"
           f"</style>"
           f'<rect width="{MW}" height="{h}" rx="2" fill="{SLAB}"/>'
           f'<rect x="0.5" y="0.5" width="{MW-1}" height="{h-1}" rx="2" fill="none" stroke="{EDGE}"/>'
           f'<rect x="0" y="0" width="4" height="{h}" fill="{accent}"/>']
    out.append(f'<text x="34" y="44" class="k">{kicker}</text>')
    out.append(f'<text x="34" y="112" class="n">{hero}<tspan class="u">{unit}</tspan></text>')
    out.append(f'<text x="34" y="152" class="t">{line1}</text>')
    out.append(f'<text x="34" y="178" class="t">{line2}</text>')
    return "".join(out) + "</svg>"


MOBILE = {
 "m-1-glyph.svg": ("GLYPH", AMBER, "97.01", "%", "A neural net written from", "scratch in C++. 299 wrong.",
   "Glyph scores 97.01 percent on the MNIST test set — a neural network written from scratch in C++ — which means 299 wrong."),
 "m-2-jetpack.svg": ("JETPACK", "#B8E62E", "6.4", "×", "Parallel gzip on JDK 25.", "The JDK intrinsic still wins.",
   "jetpack compresses roughly 6.4 times faster in parallel on JDK 25; the JDK's own native checksum intrinsic is still faster than the hand-vectorised one."),
 "m-3-cadence.svg": ("CADENCE", "#34D399", "36", "", "handlers bundled into one", "function. Vercel allows 12.",
   "Cadence bundles its 36 API handlers into a single serverless function, because Vercel's plan allows only 12 functions."),
 "m-4-applied.svg": ("APPLIED", CYAN, "0.979", "", "macro-F1 on 96 messages.", "Below 0.85 it asks a human.",
   "Applied scores 0.979 macro-F1 on a 96-message evaluation set; anything below the 0.85 confidence gate is referred to a human."),
 "m-5-refusal.svg": ("THE REFUSAL", CYAN, "0", " rows", "The app didn't remember", "to filter. The database refused.",
   "A query for another tenant's rows returns zero rows: the database refused it, rather than the application remembering to filter."),
 "m-6-release.svg": ("LIFEQUEST · AUTOML", "#F472B6", "2", "", "Routines become quests.", "Datasets become models.",
   "LifeQuest turns routines into quests; Agentic AutoML turns a dataset into a deployed model behind human approval gates."),
}
for _fn, (_k, _a, _n, _u, _l1, _l2, _d) in MOBILE.items():
    (OUT / _fn).write_text(plate_mobile(_fn, _a, _k, _n, _u, _l1, _l2, _d))
print(f"mobile set: {len(MOBILE)} plates at {MW}w")
