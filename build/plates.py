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


(OUT / "plate-1-glyph.svg").write_text(plate_glyph())
(OUT / "plate-5-refusal.svg").write_text(plate_refusal())
for f in ("plate-1-glyph.svg", "plate-5-refusal.svg"):
    p = OUT / f
    print(f"{f}: {p.stat().st_size:,} bytes")
