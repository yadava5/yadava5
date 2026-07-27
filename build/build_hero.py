#!/usr/bin/env python3
"""
Build the profile hero.

Emits hero-dark.svg / hero-light.svg / hero-static.svg from one source of truth.
The art is GENERATED, not hand-placed: the digit is rasterised onto a real 28x28
grid the way MNIST input actually is, and the lit cells fall out of that.

Constraints this file encodes (all verified against GitHub's renderer):
  * fully self-contained — no external refs; the font is inlined as base64
  * every element has a meaningful STATIC state (a frozen first frame must read)
  * no animated filters (one animated blur costs more than 4000 animated rects)
  * `prefers-reduced-motion` does NOT reach inside an <img>-embedded SVG, so the
    reduced-motion variant is a separate file selected by <picture> in the README
  * theming is two files + <picture>, because prefers-color-scheme inside the SVG
    follows the OS, not the reader's GitHub theme
"""
from __future__ import annotations
import base64, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT.parent / "assets"
OUT.mkdir(exist_ok=True)

FONT_B64 = base64.b64encode((ROOT / "mono-subset.woff2").read_bytes()).decode()

# ── the digit, rasterised for real ──────────────────────────────────────────
N = 28                      # MNIST is 28x28; so is this
CELL = 6.0                  # px per cell
STROKES = [                 # a hand-drawn "7" in grid coordinates
    ((6.0, 6.0), (21.0, 6.0)),
    ((21.0, 6.0), (11.5, 22.5)),
    ((9.5, 14.5), (17.5, 14.5)),   # the European crossbar
]
RADIUS = 1.35               # stroke half-width, in cells


def rasterise() -> list[tuple[int, int, float]]:
    """Return (col, row, intensity) for every cell the pen darkens."""
    cells: dict[tuple[int, int], float] = {}
    for (x0, y0), (x1, y1) in STROKES:
        steps = int(max(abs(x1 - x0), abs(y1 - y0)) * 8) + 1
        for s in range(steps + 1):
            t = s / steps
            px, py = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            lo_c, hi_c = int(px - RADIUS) - 1, int(px + RADIUS) + 1
            lo_r, hi_r = int(py - RADIUS) - 1, int(py + RADIUS) + 1
            for c in range(lo_c, hi_c + 1):
                for r in range(lo_r, hi_r + 1):
                    if not (0 <= c < N and 0 <= r < N):
                        continue
                    d = (((c + 0.5) - px) ** 2 + ((r + 0.5) - py) ** 2) ** 0.5
                    if d <= RADIUS:
                        v = min(1.0, (1.0 - d / RADIUS) * 1.6 + 0.25)
                        if v > cells.get((c, r), 0.0):
                            cells[(c, r)] = v
    return [(c, r, round(v, 2)) for (c, r), v in sorted(cells.items(), key=lambda kv: (kv[0][1], kv[0][0]))]


CELLS = rasterise()

# order the lit cells along the pen's travel so they ignite in writing order
def pen_order(cell):
    c, r, _ = cell
    return (r * 0.55 + (c if r < 9 else -c) * 0.45)


LIT = sorted(CELLS, key=pen_order)

THEMES = {
    "dark":  dict(bg="#0b0d0e", ink="#e7ecef", dim="#5c6a73", grid="#161c21",
                  accent="#38bdf8", warm="#f5a524", ok="#34d399", panel="#11161a"),
    "light": dict(bg="#ffffff", ink="#0b0d0e", dim="#6b7780", grid="#eceff1",
                  accent="#0284c7", warm="#b45309", ok="#047857", panel="#f6f8f9"),
}

W, H = 1000, 340
LOOP = 14.0          # seconds — the master clock every element shares
SETTLE = 9.0         # the frozen first frame lands here: fully classified
GX, GY = 62, 92      # grid origin


def pct(sec: float) -> float:
    return round(sec / LOOP * 100, 3)


def build(theme_name: str, animated: bool) -> str:
    t = THEMES[theme_name]
    grid_px = N * CELL

    # ── the 28x28 input plate ──────────────────────────────────────────────
    plate = [f'<rect x="{GX-10}" y="{GY-10}" width="{grid_px+20}" height="{grid_px+20}" rx="8" '
             f'fill="{t["panel"]}" stroke="{t["grid"]}"/>']
    for i in range(N + 1):
        x = GX + i * CELL
        plate.append(f'<path d="M{x} {GY}V{GY+grid_px}" stroke="{t["grid"]}" stroke-width="0.5"/>')
        y = GY + i * CELL
        plate.append(f'<path d="M{GX} {y}H{GX+grid_px}" stroke="{t["grid"]}" stroke-width="0.5"/>')

    # ── lit cells (generated) ──────────────────────────────────────────────
    px_els = []
    n = len(LIT)
    for i, (c, r, v) in enumerate(LIT):
        x, y = GX + c * CELL, GY + r * CELL
        # SETTLE parks the frozen first frame at the scene's most complete
        # moment, so a renderer that only paints t=0 still shows the finished
        # classification rather than an empty plate.
        d = f' style="animation-delay:{round(-SETTLE + i * 0.024, 3)}s"' if animated else ''
        cls = ' class="px"' if animated else ''
        px_els.append(f'<rect{cls}{d} x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
                      f'fill="{t["accent"]}" opacity="{v:.2f}"/>')

    # ── the network: 784 -> 100 -> 10, drawn as three ranks ───────────────
    net = []
    NX = 300
    ranks = [(NX, 12, "784"), (NX + 96, 8, "100"), (NX + 192, 10, "10")]
    positions = []
    for ri, (rx, count, label) in enumerate(ranks):
        span = 150
        ys = [GY + 14 + (span / max(count - 1, 1)) * k for k in range(count)]
        positions.append([(rx, y) for y in ys])
        net.append(f'<text x="{rx}" y="{GY-6}" class="tiny" fill="{t["dim"]}" text-anchor="middle">{label}</text>')
    for ri in range(2):
        for a, (ax, ay) in enumerate(positions[ri]):
            for b, (bx, by) in enumerate(positions[ri + 1]):
                if (a + b) % 3:        # thin the mesh so it reads as structure
                    continue
                d = f' style="animation-delay:{round(-SETTLE + ((a+b) % 10) * 0.05, 3)}s"' if animated else ''
                cls = ' class="wire"' if animated else ''
                net.append(f'<path{cls}{d} d="M{ax} {ay}L{bx} {by}" stroke="{t["accent"]}" '
                           f'stroke-width="0.6" opacity="0.20" fill="none"/>')
    for ri, rank in enumerate(positions):
        for k, (x, y) in enumerate(rank):
            d = f' style="animation-delay:{round(-SETTLE + ri * 0.22 + k * 0.03, 3)}s"' if animated else ''
            cls = ' class="node"' if animated else ''
            net.append(f'<circle{cls}{d} cx="{x}" cy="{y}" r="2.6" fill="{t["ink"]}" opacity="0.55"/>')

    # ── the verdict: ten class bars, seven wins ───────────────────────────
    VX, VY = 620, GY + 6
    probs = [.01, .01, .02, .01, .02, .01, .01, .93, .01, .02]
    verdict = [f'<text x="{VX}" y="{GY-6}" class="tiny" fill="{t["dim"]}">OUTPUT</text>']
    for d, p in enumerate(probs):
        y = VY + d * 15
        win = d == 7
        col = t["accent"] if win else t["dim"]
        dl = f' style="animation-delay:{round(-SETTLE + d * 0.045, 3)}s"' if animated else ''
        cls = ' class="bar"' if animated else ''
        verdict.append(f'<text x="{VX}" y="{y+4}" class="tiny" fill="{col}">{d}</text>')
        verdict.append(f'<rect x="{VX+14}" y="{y-4}" width="120" height="7" rx="2" fill="{t["grid"]}"/>')
        verdict.append(f'<rect{cls}{dl} x="{VX+14}" y="{y-4}" width="{max(2, 120*p):.1f}" height="7" rx="2" '
                       f'fill="{col}" opacity="{1 if win else .55}"/>')
    verdict.append(f'<text x="{VX+150}" y="{VY+7*15+8}" class="num" fill="{t["ink"]}">97.01%</text>')
    verdict.append(f'<text x="{VX+150}" y="{VY+7*15+24}" class="tiny" fill="{t["dim"]}">held-out accuracy</text>')

    style = f"""
    @font-face {{ font-family:'M'; font-style:normal; font-weight:400;
      src:url(data:font/woff2;base64,{FONT_B64}) format('woff2'); }}
    text {{ font-family:'M', ui-monospace, SFMono-Regular, Menlo, monospace; }}
    .tiny {{ font-size:8.5px; letter-spacing:1.4px; }}
    .num  {{ font-size:20px; font-weight:600; letter-spacing:0.5px; }}
    .name {{ font-size:19px; font-weight:600; letter-spacing:6px; }}
    .tag  {{ font-size:10.5px; letter-spacing:1.2px; }}
    .lede {{ font-size:9px; letter-spacing:2.6px; }}
    """
    if animated:
        style += f"""
    .px, .wire, .node, .bar {{ animation:none {LOOP}s linear infinite; }}
    .px   {{ animation-name:ignite; }}
    .wire {{ animation-name:fire;   }}
    .node {{ animation-name:pulse;  }}
    .bar  {{ animation-name:grow; transform-box:fill-box; transform-origin:left center; }}
    @keyframes ignite {{
      0%,{pct(0.6)}% {{ opacity:0 }} {pct(1.6)}%,{pct(12.6)}% {{ opacity:1 }} {pct(13.4)}%,100% {{ opacity:0 }} }}
    @keyframes fire {{
      0%,{pct(3.4)}% {{ opacity:.06 }} {pct(4.4)}% {{ opacity:.55 }} {pct(6.0)}%,100% {{ opacity:.20 }} }}
    @keyframes pulse {{
      0%,{pct(4.0)}% {{ opacity:.35 }} {pct(5.0)}% {{ opacity:1 }} {pct(6.8)}%,100% {{ opacity:.55 }} }}
    @keyframes grow {{
      0%,{pct(6.2)}% {{ transform:scaleX(0) }} {pct(7.6)}%,100% {{ transform:scaleX(1) }} }}
    """
    # per-element delays are emitted inline on each element (exact, and it keeps
    # the stylesheet to four rules regardless of how many cells are generated)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img"
     aria-label="A handwritten seven is rasterised onto a 28 by 28 grid, fed through a 784-100-10 network, and classified with 97.01 percent held-out accuracy.">
  <title>Ayush Yadav — Glyph classifying a handwritten digit</title>
  <style>{style}</style>
  <rect width="{W}" height="{H}" fill="{t['bg']}"/>

  <text x="62" y="40" class="name" fill="{t['ink']}">AYUSH YADAV</text>
  <text x="62" y="60" class="tag"  fill="{t['dim']}">I build systems that prove themselves.</text>
  <text x="938" y="40" class="lede" fill="{t['dim']}" text-anchor="end">GLYPH — A NEURAL NET WRITTEN FROM SCRATCH IN C++</text>
  <path d="M62 72H938" stroke="{t['grid']}"/>

  <g>{''.join(plate)}</g>
  <g>{''.join(px_els)}</g>
  <text x="{GX}" y="{GY + N*CELL + 22}" class="tiny" fill="{t['dim']}">28 × 28 INPUT</text>
  <g>{''.join(net)}</g>
  <g>{''.join(verdict)}</g>

  <text x="62" y="{H-22}" class="tiny" fill="{t['dim']}">HAND-WRITTEN SIMD · AVX-512 / AVX2 / NEON / WASM128 · COMPILED TO WEBASSEMBLY</text>
  <text x="938" y="{H-22}" class="tiny" fill="{t['dim']}" text-anchor="end">getglyph.vercel.app</text>
</svg>
"""


for name in ("dark", "light"):
    (OUT / f"hero-{name}.svg").write_text(build(name, animated=True))
(OUT / "hero-static.svg").write_text(build("dark", animated=False))

for f in ("hero-dark.svg", "hero-light.svg", "hero-static.svg"):
    print(f"{f}: {(OUT / f).stat().st_size:,} bytes")
print(f"lit cells generated: {len(CELLS)}")
