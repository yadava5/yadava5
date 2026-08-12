#!/usr/bin/env python3
"""
BOARD — figure builder.

The estate drawn as ONE continuous circuit board, sliced into transparent
plates. Three buses run the whole page at fixed x (BUS_X); each plate's bottom
edge hands them to the next plate's top edge, so the sections read as regions
of one artifact rather than instances of a template. The hero is a topology
whose edges are checkable claims about the estate — the one property this
page has that no other profile does.

Design rules encoded here (each one is a finding, not a preference):
  * TRANSPARENT, NOT UNGROUNDED. No plate paints a sheet — data-canvas
    declares the ground every ratio is graded against (#212830, Primer
    11.10.0 dark-dimmed, the lightest canvas GitHub serves dark; #ffffff
    light). The previous canvas constant #22272e is a colour GitHub no
    longer serves. Local ground comes from OBJECTS: the product marks are
    opaque near-black tiles, and gate.mjs check 10 grades ink inside a tile
    against the tile, because that is what a reader sees behind it.
  * THE CURRENT IS THE CARRIER. Every bus carries a comet — a colour-ramped
    dash train at constant 2u width — marching along the trace. Constant
    width because real traces do not bulge; the smoothness the client asked
    for ("very sharp, small lines" -> "evenly flowing") comes from LENGTH
    and FALLOFF: three abutting dash segments per comet, head brightest,
    tail landing on the track's own colour so the pulse melts into the line
    instead of ending. Every ramp step clears 3.0:1 on its canvas
    (measured, scratchpad/p1-palette.py, 2026-08-12) because translucent
    tails cannot: a 0.25-alpha tail is 1.2:1 on white.
  * UNEVEN BY DESIGN. The three buses run at different speeds (periods
    2100/2450/2750ms — near-coprime, so the page never beats into a pulse)
    and enter each plate at different phases. The client's words: "I like it
    uneven as the data is flowing in different ways" — evenness is the thing
    to avoid, sharpness was the complaint.
  * WIDTH IS THE LAW OF THE INK. Structural stroke is 2u everywhere —
    tracks, comets, mark hairlines. gate.mjs's hairline discriminator sits
    at 2u, and everything that travels must live under it: a moving stroke
    above 2u is heavy ink, and heavy ink crossing anything is a collision.
    Crossing TEXT is forbidden at any width — routes are laid so no bus
    passes through a label's box on any platform (+4% Linux advance skew
    included in the clearances).
  * LOOPS WRAP SEAMLESSLY, PHASE-INVARIANT. A repeating dash pattern is
    "finished" at every t, so any camo/cache phase a reader joins at is an
    authored frame. The ONE one-shot lives on the hero (the intro pulse,
    three staggered sends), because the hero is the only plate a reader
    reliably sees from t=0.
  * CSS IS THE ONLY MOTION LAYER. No SMIL: document.getAnimations() cannot
    see SMIL, so neither gate could seek it and reduced-motion could not
    park it. No animated filters — one animated blur costs more than 4000
    animated rects.
  * frame zero is the finished frame; keyframes only ever state `to`, so
    the authored attribute IS the start pose (gate checks 6/16).
  * viewBox 900 wide, every desktop plate. The board is one artifact and
    the buses must land on the same x across every seam; GitHub's profile
    column measures 846px at every desktop viewport (probed 2026-08-12), so
    every plate scales identically at 0.94 and registration holds exactly.
  * type: Syne 800 ('D') for the silkscreen voice — name, romans, claim
    figures; Commissioner 400/600 ('T') for text and labels, instanced at
    FLAR 40 (see subset-fonts.py). No mono anywhere: nothing on this page
    quotes a machine artifact whole, and mono that means nothing is the
    client's oldest complaint.
"""
from __future__ import annotations
import base64, json, pathlib, re
import xml.dom.minidom as _xml

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT.parent / "assets"
OUT.mkdir(exist_ok=True)

from charsets import DISPLAY_CHARS, TEXT_CHARS, LABEL_CHARS

FONT_D = base64.b64encode((ROOT / "syne-800.woff2").read_bytes()).decode()
FONT_T = base64.b64encode((ROOT / "comm-400.woff2").read_bytes()).decode()
FONT_TS = base64.b64encode((ROOT / "comm-600.woff2").read_bytes()).decode()

# ── the board's shared geometry. Every desktop plate is W wide; the three
# buses leave each plate's bottom edge at BUS_X and enter the next at the
# same x. The mobile page runs its own narrower bus at MBUS_X.
W = 900
BUS_X = {"verd": 63, "rust": 90, "zinc": 117}
MBUS_X = {"verd": 40, "rust": 54, "zinc": 68}

# every plate's description is authored ONCE here and flows to three places:
# the SVG <desc>, the SVG aria-label, and the README's <img alt>.
ALT: dict[str, str] = {}

# ── the two palettes. Oxidised metal on GitHub's own canvas: verdigris,
# rust, zinc — the colours of a board that has been powered a long time.
# Every value below was computed against its canvas before it was authored
# (scratchpad/p1-palette.py, 2026-08-12): text >= 4.5:1, structure >= 3.0:1,
# and the dark set re-checked on #010409 (dark-high-contrast), where light
# ink only gains. ramp = comet colours head->tail; the tail is deliberately
# near the track so the pulse decays into the line.
TILE = "#0A0A0B"   # the product marks' own ground, from their repos
DARK = dict(
    canvas="#212830", ink="#E4E9E9", mid="#C7D1D6", dim="#B0BAC0",
    verd="#4FB39A", rust="#E0703A", zinc="#8A9599",
    edge="#7A828A", pulse="#FFFFFF",
    ramp=dict(verd=("#A9EFD9", "#83D6BC", "#66C2A8"),
              rust=("#FFB287", "#F29260", "#E87E49"),
              zinc=("#C9D3D6", "#AEB9BD", "#9AA5A9")),
)
LIGHT = dict(
    canvas="#ffffff", ink="#1A2224", mid="#303B41", dim="#424D52",
    verd="#1F6D5C", rust="#9A3412", zinc="#5F6E73",
    edge="#6E7A80", pulse="#1A2224",
    ramp=dict(verd=("#0C4A3C", "#14584A", "#1A6253"),
              rust=("#6E2209", "#7F2A0D", "#8D2F10"),
              zinc=("#39464B", "#48565B", "#535F64")),
)
T = DARK


def set_theme(name: str) -> None:
    global T
    T = DARK if name == "dark" else LIGHT


# ── the product marks. Geometry lifted from each product's own logo source
# (cadence/public/cadence-mark.svg, glyph/web/public/glyph-mark.svg,
# applied/apps/web/app/icon.svg, jetpack-compress/web/public/favicon.svg);
# AutoML and VisualAssist have no mark of their own, so theirs are drawn HERE
# in the family language — near-black rounded tile, hairline, one accent, one
# geometric glyph. All emitters draw into a 48x48 box at (0,0).
#
# Three internals are nudged from their sources, because the tile is a
# contrast ground now and the gate measures it: structure grey #52525B reads
# 2.56:1 on the tile (floor 3.0) and becomes #6B6B76 (3.76:1); cadence's
# 0.28 ticks become 0.42 (2.33 -> 3.79:1); AutoML's 0.45 return arc becomes
# 0.65 (2.30 -> 3.58:1). Accents are untouched — the products keep their
# true colours, and all seven clear 7:1 on the tile.
STRUCT = "#6B6B76"


def _tile(r: int = 12) -> str:
    return (f'<rect x="0.75" y="0.75" width="46.5" height="46.5" rx="{r}" '
            f'fill="{TILE}" stroke="{T["edge"]}" stroke-width="1"/>')


# All six emitters are FLAT: presentation attributes ride on each element and
# scale corrections ride on the element's own transform, never on a nested
# <g>. gate.mjs composes by NEAREST enclosing group — a glyph in an inner
# styling group and its tile in the outer one read as strangers and every
# mark becomes forty collisions. mark() supplies the one group each needs.
def mark_cadence() -> str:
    return _tile() + '''
<path d="M10,33 H38" fill="none" stroke="#F7F8F8" stroke-opacity="0.82" stroke-width="2" stroke-linecap="round"/>
<path d="M15,30.5 V33 M22,30.5 V33 M36,30.5 V33" fill="none" stroke="#F7F8F8" stroke-opacity="0.42" stroke-width="1.5" stroke-linecap="round"/>
<path d="M25.6,15.2 L29,18.6 L32.4,15.2 M29,18.6 V33" fill="none" stroke="#34D399" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>'''


def mark_glyph() -> str:
    # source is a 40-unit box; scaled into 48. The ruled lines are ONE path,
    # not <line> elements: gate.mjs's drawables query reads text/rect/circle/
    # path, so a <line> is ink no check can see — the local-ground probe in
    # mutations.mjs keys on this path's stroke.
    return _tile() + f'''
<path transform="translate(4.8,4.8) scale(0.96)" d="M8,11 H32 M8,17 H32 M8,23 H32 M8,29 H32"
  fill="none" stroke="{STRUCT}" stroke-width="1.4"/>
<path transform="translate(4.8,4.8) scale(0.96)"
  d="M12.5 16 C12.5 10.5 27 9.5 27 15.5 C27 20 17 24 12 30 L29 30"
  fill="none" stroke="#F7F8F8" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'''


def mark_applied() -> str:
    return _tile() + '''
<path d="M17.2,30.2 L20.3,27.4 M27.7,20.7 L30.6,18.1" fill="none" stroke="#F7F8F8" stroke-opacity="0.65" stroke-width="2" stroke-linecap="round"/>
<circle cx="13.5" cy="33.5" r="3" fill="none" stroke="#06B6D4" stroke-width="2.4"/>
<circle cx="24" cy="24" r="3" fill="none" stroke="#06B6D4" stroke-width="2.4"/>
<circle cx="34.5" cy="14.5" r="4.1" fill="#10B981"/>'''


def mark_jetpack() -> str:
    # source is a 32-unit box; scaled into 48
    return _tile(r=10) + '''
<path transform="translate(2.4,2.4) scale(1.35)"
  d="M7 10 H14.5 M7 16 H19 M7 22 H14.5 M14.5 10 L20 16 L14.5 22 M20 16 H25"
  fill="none" stroke="#FF9E2C" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>'''


def mark_automl() -> str:
    # drawn here: a LangGraph state machine — three states on a cycle,
    # one transition arrowed. One accent (violet), geometry only.
    return _tile() + f'''
<path d="M24,12.5 A11.5,11.5 0 0 1 34.3,29.2 M31.5,33.8 A11.5,11.5 0 0 1 16.5,33.8"
  fill="none" stroke="#A78BFA" stroke-width="2.2" stroke-linecap="round"/>
<path d="M13.7,29.2 A11.5,11.5 0 0 1 24,12.5" fill="none" stroke="#A78BFA"
  stroke-opacity="0.65" stroke-width="2.2" stroke-linecap="round"/>
<path d="M34.3,25.6 L34.3,29.6 L30.6,28.4" fill="#A78BFA"/>
<circle cx="24" cy="12.5" r="3" fill="{TILE}" stroke="#A78BFA" stroke-width="2.2"/>
<circle cx="15.1" cy="31.5" r="3" fill="{TILE}" stroke="#A78BFA" stroke-width="2.2"/>
<circle cx="32.9" cy="31.5" r="3" fill="#A78BFA"/>'''


def mark_visualassist() -> str:
    # drawn here: the alert policy itself — near arc solid (interrupt),
    # mid arc a triple pulse, far arc drawn in structure grey: silence.
    return _tile() + f'''
<path d="M20.8,26.5 A9,9 0 0 1 26.5,20.8" fill="none" stroke="#FB7185" stroke-width="2.8" stroke-linecap="round"/>
<path d="M19.1,31.4 A16,16 0 0 1 31.4,19.1" fill="none" stroke="#FB7185" stroke-width="2.2"
  stroke-dasharray="4.5 4.8" stroke-linecap="round"/>
<path d="M17.6,36.2 A23,23 0 0 1 36.2,17.6" fill="none" stroke="{STRUCT}" stroke-width="1.4" stroke-linecap="round"/>
<circle cx="13.5" cy="34.5" r="3.2" fill="#FB7185"/>'''


MARKS = {"cadence": mark_cadence, "glyph": mark_glyph, "applied": mark_applied,
         "jetpack": mark_jetpack, "automl": mark_automl,
         "visualassist": mark_visualassist}


def mark(name: str, x: float, y: float, size: float) -> str:
    # One <g> per mark: gate.mjs treats same-group overlap as composed on
    # purpose, which is exactly what a glyph on its own tile is.
    s = size / 48.0
    return (f'<g transform="translate({x},{y}) scale({s:.4f})">'
            + MARKS[name]() + "</g>")


# ── the bus system.
#
# One comet = three abutting dash segments (COMET lengths, head first) on a
# shared period of PAT pattern-units, so a comet is 84u long with a soft
# decay. Each segment is its own <path> with its own generated @keyframes,
# because CSS dash animation is absolute: a shared keyframe would erase the
# per-segment offsets that keep the three aligned head-to-tail. Keyframes
# state only `to` — the `from` is the authored stroke-dashoffset attribute,
# which makes frame zero the finished frame by construction.
#
# Periods differ per bus ON PURPOSE (see the doctrine above); phase is the
# per-instance C argument, in pattern units, so two plates never open on the
# same frame and segments inside a plate can be staggered.
PAT = 210
COMET = (34, 28, 22)
BUS_MS = {"verd": 2100, "rust": 2450, "zinc": 2750}

_CSS: list[str] = []
_KN = 0


def _kf() -> str:
    global _KN
    _KN += 1
    return f"k{_KN}"


def comet(bus: str, d: str, C: float = 0.0) -> str:
    """The moving current for one trace segment (no track — see bus())."""
    out = ""
    end = C
    for L, col in zip(COMET, T["ramp"][bus]):
        o0 = round(L - end, 2)
        name = _kf()
        _CSS.append(f"@keyframes {name}{{to{{stroke-dashoffset:{o0 - PAT}}}}}")
        _CSS.append(f".{name}{{animation:{name} {BUS_MS[bus]}ms linear infinite}}")
        out += (f'<path class="cm {name}" stroke="{col}" '
                f'stroke-dasharray="{L} {PAT - L}" stroke-dashoffset="{o0}" '
                f'd="{d}"/>')
        end -= L
    return out


def bus(bus_key: str, d: str, C: float = 0.0, cd: str | None = None) -> str:
    """One trace: static track plus its comet, grouped as one object.

    `cd` is the comet's own path when it must differ from the track's — the
    track may end flush against a tile or the canvas edge, but a travelling
    dash wears round caps, and a cap protruding past the endpoint is ink
    leaving the canvas (check 4) or entering the tile. Callers inset comet
    endpoints ~4u for tiles, ~2.5u at canvas edges.
    """
    return (f'<g><path class="bus" stroke="{T[bus_key]}" d="{d}"/>'
            + comet(bus_key, cd or d, C) + "</g>")


def pulse(d: str, travel: float, delay_ms: int) -> str:
    """The hero's one-shot: a 70u send sweeping a whole trace, once.

    `travel` only needs to be an UPPER BOUND on the path length — the dash
    starts fully off-path (offset 70, nothing drawn at t=0) and the keyframe
    drives it `travel`+140 further, so it fully exits before the fade ends
    and no path-length arithmetic is load-bearing.
    """
    name = _kf()
    _CSS.append(
        f"@keyframes {name}{{78%{{opacity:.9}}"
        f"100%{{stroke-dashoffset:{-(travel + 70):.0f};opacity:0}}}}")
    _CSS.append(f".{name}{{animation:{name} 2300ms cubic-bezier(.45,0,.2,1) "
                f"{delay_ms}ms 1 forwards}}")
    return (f'<path class="pu {name}" stroke-dasharray="70 {travel + 140:.0f}" '
            f'stroke-dashoffset="70" d="{d}"/>')


# ── the plate opener.
def head(h: int, title: str, desc: str, key: str = "",
         col: tuple[int, int] = (44, 886),
         frame: tuple[float, float, float] | None = None,
         faces: str = "DT6", w: int = W) -> str:
    """Open a plate.

    `col` and `frame` are this plate's DECLARED geometry, written into the
    SVG root as data-col / data-frame and asserted by gate.mjs (checks 5 and
    12): no edge is ever an accident. data-canvas is unconditional — every
    plate on this page is transparent and names the worst canvas GitHub
    serves its theme on (#212830 dark / #ffffff light), so a pass there is a
    pass on all of them.

    `faces` names the faces this plate actually renders ('D' Syne 800,
    'T' Commissioner 400, '6' Commissioner 600). gate.mjs enforces both
    directions — a declared face nothing renders is dead payload shipped to
    every reader, and a rendered face nothing declares is a platform
    fallback — so a chip that speaks only in labels embeds only the 600.
    """
    if key:
        # The light pass re-authors the same key. A plate and its light twin
        # must carry byte-identical descriptions — asserted, not assumed.
        if key in ALT and ALT[key] != desc:
            raise SystemExit(f"{key}: description diverged between themes")
        ALT[key] = desc
    fr = f' data-frame="{frame[0]:g},{frame[1]:g},{frame[2]:g}"' if frame else ""
    fd = (f"@font-face{{font-family:'D';font-weight:800;"
          f"src:url(data:font/woff2;base64,{FONT_D}) format('woff2')}}\n") if "D" in faces else ""
    ft = (f"@font-face{{font-family:'T';font-weight:400;"
          f"src:url(data:font/woff2;base64,{FONT_T}) format('woff2')}}\n") if "T" in faces else ""
    f6 = (f"@font-face{{font-family:'T';font-weight:600;"
          f"src:url(data:font/woff2;base64,{FONT_TS}) format('woff2')}}\n") if "6" in faces else ""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{desc}" data-col="{col[0]},{col[1]}"{fr} data-canvas="{T['canvas']}">
<title>{title}</title><desc>{desc}</desc>
<style>
{fd}{ft}{f6}text{{font-family:'T',-apple-system,'Segoe UI',sans-serif;fill:{T['ink']}}}
.d{{font-family:'D',sans-serif;font-weight:800;fill:{T['ink']}}}
.ts{{font-weight:600}}
.mid{{fill:{T['mid']}}} .dim{{fill:{T['dim']}}}
.bus{{fill:none;stroke-width:2;stroke-linejoin:round}}
.cm{{fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}}
.pu{{fill:none;stroke:{T['pulse']};stroke-width:2;stroke-linecap:round;stroke-linejoin:round;opacity:.9}}
@media (prefers-reduced-motion: reduce){{*{{animation:none!important}}}}
"""


def css_close() -> str:
    """Drain the keyframes the plate's bus/pulse calls generated."""
    s = "\n".join(_CSS)
    _CSS.clear()
    return s + "\n</style>\n"


def lbl(x: float, y: float, text: str, cls: str = "ts dim", size: float = 11,
        ls: float = 1.4, anchor: str = "start") -> str:
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    return (f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}" '
            f'letter-spacing="{ls}"{a}>{text}</text>')


# ══════════════════════════════════════════════════════════ the hero
#
# Layout registry, in authored units. Clearances between every travelling
# trace and every text box hold >= 8u with the Linux +4% advance skew
# applied to each label's width — the constants below were chosen against
# that arithmetic, then verified in Chromium by gate.mjs, not by eye alone.
#   top row     cadence(620,52)  applied(784,52)          tiles 56u
#   mid-left    automl(520,140) — DELIBERATELY off both rows: the client's
#               brief is an uneven board, and flattening this cluster into a
#               grid was rejected in review. POSTGRES runs as a vertical
#               label beside the riser, the approved arrangement.
#   second row  glyph(620,188)   jetpack(784,188)
#   left        visualassist(48,300)
#   drops       verd x=766 (between label ends ~712 and applied 784)
#               rust x=744 (clear of the SIMD label by starting at y=216)
#               zinc x=612 (the postgres riser's own column; the riser sits
#                          at 612 rather than the old 606 so the label below
#                          the automl tile clears the comet by >= 4u with
#                          the +4% Linux advance applied — measured, not
#                          estimated, gate check 2 samples it 40x per loop)
#   collectors  y=400/415/430, exits at BUS_X 63/90/117
def plate_hero() -> str:
    d_verd = "M766,80 V388 Q766,400 754,400 H87 Q75,400 75,412 V470"
    d_rust = "M744,216 V403 Q744,415 732,415 H102 Q90,415 90,427 V470"
    d_zinc = "M612,130 V418 Q612,430 600,430 H129 Q117,430 117,442 V470"
    c_verd = "M766,84 V388 Q766,400 754,400 H87 Q75,400 75,412 V467.5"
    c_rust = "M744,220 V403 Q744,415 732,415 H102 Q90,415 90,427 V467.5"
    c_zinc = "M612,134 V418 Q612,430 600,430 H129 Q117,430 117,442 V467.5"
    body = (
        # the name block — anchored left, grown right and down. One <text>,
        # two lines: Syne's em box is ~1.29 of the size, so two separate
        # elements at this leading read to the gate as a permanent collision.
        f'<text x="48" y="84" class="d" font-size="58" letter-spacing="1">AYUSH'
        f'<tspan x="48" dy="64">YADAV</tspan></text>'
        f'<text x="48" y="190" font-size="16.5">Systems, from SIMD kernels to the browser they run in.</text>'
        f'<text x="48" y="216" class="dim" font-size="13">B.S. Computer Science, Miami University (May 2026) · Cincinnati, OH</text>'
        f'<text x="48" y="236" class="dim" font-size="13">open to full-time software engineering roles · aesh.03.23@gmail.com</text>'
        f'<rect x="48" y="258" width="9" height="9" fill="{T["verd"]}"/>'
        + lbl(66, 267, "EVERY EDGE ON THIS BOARD IS A CHECKABLE CLAIM", cls="ts mid", ls=1.6)
        # the two claim edges and the postgres feed
        + bus("verd", "M680,80 H780", C=30, cd="M684,80 H776")
        + bus("rust", "M680,216 H780", C=110, cd="M684,216 H776")
        # the postgres edge: out of AutoML's flank, up the riser, into
        # Cadence. The riser column doubles as the zinc drop below y=130 —
        # the junction where the feed splits, kept from the approved render.
        + bus("zinc", "M580,168 H612 V80 H616", C=64, cd="M584,168 H612 V84")
        # visualassist: deliberately unconnected — an open stub
        + f'<path class="bus" stroke="{T["zinc"]}" stroke-dasharray="3 6" d="M108,328 H150"/>'
        + f'<circle cx="157" cy="328" r="3.5" fill="none" stroke="{T["zinc"]}" stroke-width="2"/>'
        # the three main runs, converging bottom-left into the page bus
        + bus("verd", d_verd, C=0, cd=c_verd)
        + bus("rust", d_rust, C=87, cd=c_rust)
        + bus("zinc", d_zinc, C=41, cd=c_zinc)
        + pulse(c_verd, 1200, 400) + pulse(c_rust, 1050, 530) + pulse(c_zinc, 950, 680)
        # the marks
        + mark("automl", 480, 52, 56) + mark("cadence", 620, 52, 56)
        + mark("applied", 784, 52, 56)
        + mark("glyph", 620, 188, 56) + mark("jetpack", 784, 188, 56)
        + mark("visualassist", 48, 300, 56)
        # edge labels sit clear of every trace; drops were routed around them
        + lbl(578, 68, "POSTGRES", size=10, anchor="middle")
        + lbl(730, 68, "RLS · FORCED", size=10.5, anchor="middle")
        + lbl(730, 202, "SIMD", size=10.5, anchor="middle")
        + lbl(480, 44, "IV · AUTOML", size=10.5)
        + lbl(620, 124, "V · CADENCE", size=10.5) + lbl(784, 124, "VI · APPLIED", size=10.5)
        + lbl(620, 260, "III · GLYPH", size=10.5) + lbl(784, 260, "II · JETPACK", size=10.5)
        + lbl(48, 376, "VII · VISUALASSIST", size=10.5)
        + lbl(48, 391, "NO URL — IT NEEDS AN IPHONE WITH LIDAR, IN YOUR HAND", cls="ts dim", size=10, ls=1.1)
    )
    return head(
        470,
        "Ayush Yadav — the estate as one board; every edge is a checkable claim",
        "Ayush Yadav — the estate drawn as one circuit board. Six product marks "
        "sit on a shared bus and every printed edge is a checkable claim: "
        "Cadence and Applied share forced row-level security, Glyph and jetpack "
        "share SIMD, AutoML feeds Postgres. VisualAssist hangs on an open stub — "
        "no URL, it needs an iPhone with LiDAR in your hand. B.S. Computer "
        "Science, Miami University, May 2026; open to full-time software "
        "engineering roles; aesh at gmail.",
        key="plate-0-hero.svg",
        col=(44, 888), frame=HERO_FRAME,
    ) + css_close() + body + "</svg>"


# ══════════════════════════════════════════════════ the connector strip
#
# Four ports on the bus, each its own SVG so each is its own link in the
# README — the way out of "an SVG in an <img> cannot hold a link". The three
# lanes run edge-to-edge at the same y in all four chips; GitHub renders a
# 3.8px gap between adjacent linked images separated by one space (measured
# on the live profile page, 2026-08-12), so the lanes align across the gaps
# and the strip reads as one bus threading a row of edge connectors. Chips
# render at natural size (they never scale — total width ~550 fits the 590px
# column GitHub serves at 1024 viewports), which is also why the strip makes
# no claim of x-registration with the scaled plates above and below it: it
# is a crossing structure, not a continuation of their verticals.
#
# EACH CHIP IS AN OPAQUE MODULE, and that is forced by the medium, not
# chosen: GitHub's markdown pipeline SPLITS a <picture> inside a link — the
# <source> stays in the author's <a>, the <img> is extracted and auto-linked
# to the asset file itself (probed against the real /markdown API,
# 2026-08-12). So a chip cannot be both clickable and theme-switched. A
# component is a physical object that does not recolour with the room: the
# chip is a near-black module in the marks' own family language, self-
# grounded, ONE artwork legible on every canvas, linked as [<img>](url) —
# the nesting that survives. Only the module's hairline rides the canvas, in
# the one grey that clears 3:1 on all of them (#79848C: 3.89 on #212830,
# 3.82 on #ffffff, 5.37 on #010409 — measured). Everything inside grades
# against the module via check 10's local grounds, and the traces keep the
# dark palette on both themes because their ground never changes.
LANES = (44, 53, 62)          # connector pitch 9u — tighter than the board's 27
CHIP_H = 72
CHIP_EDGE = "#79848C"


def _port_glyphs(kind: str) -> str:
    """The port marks, drawn here in the family language. White ink only —
    colour on this page belongs to the products and the buses."""
    if kind == "www":       # a globe: equator and one meridian
        return ('<circle cx="24" cy="24" r="7.2" fill="none" stroke="#F7F8F8" stroke-width="1.7"/>'
                '<path d="M16.8,24 H31.2" fill="none" stroke="#F7F8F8" stroke-width="1.5"/>'
                '<path d="M24,16.8 C20.6,20.4 20.6,27.6 24,31.2 C27.4,27.6 27.4,20.4 24,16.8"'
                ' fill="none" stroke="#F7F8F8" stroke-width="1.5"/>')
    if kind == "doc":       # a sheet with three set lines
        return ('<rect x="18" y="16" width="12" height="16" rx="2" fill="none" stroke="#F7F8F8" stroke-width="1.7"/>'
                '<path d="M21,21.5 H27 M21,25 H27 M21,28.5 H25" fill="none" stroke="#F7F8F8" stroke-width="1.5" stroke-linecap="round"/>')
    if kind == "at":
        return ('<text x="24" y="29.5" class="ts" font-size="17" text-anchor="middle" style="fill:#F7F8F8">@</text>')
    if kind == "in":
        return ('<text x="24" y="29" class="ts" font-size="15.5" text-anchor="middle" style="fill:#F7F8F8">in</text>')
    raise SystemExit(f"unknown port glyph {kind}")


def chip(w: int, label: str, glyph: str, tap_bus: str, phases: tuple[float, float, float],
         title: str, desc: str, key: str, frame: tuple[float, float, float]) -> str:
    global T
    saved = T
    # the module carries the dark surface on every canvas: only data-canvas,
    # written by head() from the theme, differs between the two files.
    T = dict(saved, ink=DARK["ink"], mid=DARK["mid"], dim=DARK["dim"],
             verd=DARK["verd"], rust=DARK["rust"], zinc=DARK["zinc"],
             ramp=DARK["ramp"], edge=CHIP_EDGE)
    try:
        tap_y = LANES[{"verd": 0, "rust": 1, "zinc": 2}[tap_bus]]
        lanes = ""
        for (name, y), C in zip(zip(("verd", "rust", "zinc"), LANES), phases):
            lanes += bus(name, f"M0.5,{y} H{w - 0.5}", C=C, cd=f"M3,{y} H{w - 3}")
        module = (
            # the module and its fittings, one composed object; the rect is
            # FIRST in document order so it is the plate's contrast ground
            f'<g><rect x="0.5" y="4" width="{w - 1}" height="64" rx="3" fill="{TILE}" '
            f'stroke="{CHIP_EDGE}" stroke-width="1"/>'
            # connector fingers at both edges frame the 3.8px inter-image gap
            + "".join(f'<rect x="{fx}" y="{y - 2}" width="5" height="4" fill="{T[n]}"/>'
                      for n, y in zip(("verd", "rust", "zinc"), LANES)
                      for fx in (1.5, w - 6.5))
            # the tap: this port hangs off one lane, junction dot = connected
            + f'<path class="bus" stroke="{T[tap_bus]}" d="M24,38 V{tap_y}"/>'
            + f'<circle cx="24" cy="{tap_y}" r="2.6" fill="{T[tap_bus]}"/>'
            # the port badge, outlined in structure grey like the marks' rules
            + f'<rect x="10" y="10" width="28" height="28" rx="8" fill="none" '
            f'stroke="{STRUCT}" stroke-width="1.2"/>' + _port_glyphs(glyph)
            + lbl(46, 28.5, label, cls="ts", size=11.5, ls=1.3) + "</g>"
        )
        return head(CHIP_H, title, desc, key=key, col=(8, w - 4), frame=frame,
                    faces="6", w=w) + css_close() + module + lanes + "</svg>"
    finally:
        T = saved


CHIPS = {
    # filename fragment: (width, label, glyph, tap bus, comet phases)
    "portfolio": (190, "AYUSH-YADAV.COM", "www", "verd", (12, 96, 170),
                  "ayush-yadav.com — the portfolio",
                  "Port one of four on the link bus: ayush-yadav.com, the portfolio."),
    "resume":    (116, "RÉSUMÉ", "doc", "rust", (140, 58, 15),
                  "résumé — PDF",
                  "Port two of four on the link bus: the résumé, as a PDF."),
    "email":     (106, "EMAIL", "at", "zinc", (66, 190, 118),
                  "email — aesh at gmail",
                  "Port three of four on the link bus: email; opens a mail draft."),
    "linkedin":  (132, "LINKEDIN", "in", "rust", (200, 30, 84),
                  "linkedin — profile",
                  "Port four of four on the link bus: the LinkedIn profile."),
}


def make_chip(kind: str):
    w, label, glyph, tap, phases, title, desc = CHIPS[kind]
    fn = f"plate-link-{kind}.svg"
    return lambda: chip(w, label, glyph, tap, phases, title, desc, fn,
                        CHIP_FRAME[kind])


# ══════════════════════════════════════════════════ II · jetpack
def plate_jetpack() -> str:
    lanes = ""
    for i, (y, C) in enumerate(zip((150, 188, 226, 264), (0, 64, 128, 176))):
        lanes += (bus("rust", f"M228,{y} H300", C=C, cd=f"M230,{y} H296")
                  + f'<rect x="300" y="{y - 13}" width="170" height="26" rx="6" '
                  + f'fill="none" stroke="{T["zinc"]}" stroke-width="1.3"/>'
                  + lbl(312, y + 3.5, f"BLOCK {i} · DEFLATE", size=10.5, ls=1.2)
                  + bus("rust", f"M470,{y} H520", C=C + 30, cd=f"M474,{y} H516"))
    body = (
        # the three page buses, passing through
        bus("verd", "M63,0 V400", C=140, cd="M63,2.5 V397.5")
        + bus("rust", "M90,0 V400", C=55, cd="M90,2.5 V397.5")
        + bus("zinc", "M117,0 V400", C=190, cd="M117,2.5 V397.5")
        # the SIMD bus taps into the section: in, split, four lanes, stitch
        + bus("rust", "M90,120 H150", C=18, cd="M94,120 H146")
        + bus("rust", "M198,120 H228 V264", C=70, cd="M202,120 H228 V262")
        + lanes
        + f'<path class="bus" stroke="{T["rust"]}" d="M520,150 V282"/>'
        + bus("rust", "M520,225 H556", C=100, cd="M524,225 H552")
        + f'<rect x="556" y="204" width="160" height="42" rx="8" fill="none" '
        + f'stroke="{T["rust"]}" stroke-width="1.6"/>'
        + lbl(568, 229, "ONE GZIP MEMBER", cls="ts", size=11.5, ls=1.3)
        + lbl(556, 264, "STITCHED BYTE-ALIGNED · ONE CRC", size=10, ls=1.1)
        + lbl(300, 128, "DEFLATE · JDK 25 · VIRTUAL THREADS", size=10, ls=1.1)
        + mark("jetpack", 150, 96, 48)
        + f'<text x="150" y="54" class="d" font-size="30" letter-spacing="0.5">II — JETPACK</text>'
        + f'<text x="150" y="76" class="dim" font-size="14.5">is hand-vectorised code actually faster?</text>'
        + f'<text x="640" y="138" class="d" font-size="62">6.4×</text>'
        + f'<text x="640" y="176" class="dim" font-size="13">422 vs 66.2 MB/s, single thread —</text>'
        + f'<text x="640" y="194" class="dim" font-size="13">M1 Pro · 3-fork JMH, committed</text>'
        # the against-self admission, accent-barred: the page's differentiation
        + f'<rect x="150" y="318" width="4" height="16" fill="{T["rust"]}"/>'
        + f'<text x="164" y="331" class="mid" font-size="14">the JDK&#8217;s own Adler-32 intrinsic does 14.06 GB/s — not beaten.</text>'
        + f'<text x="164" y="351" class="dim" font-size="13">mine reaches 4.26 GB/s hand-vectorised, bit-identical to java.util.zip.</text>'
    )
    return head(
        400,
        "II · jetpack — parallel gzip on JDK 25: 6.4× over one thread; the JDK intrinsic stands",
        "II · jetpack — parallel gzip on JDK 25, drawn as the SIMD bus fanning "
        "into four deflate blocks stitched back to one gzip member: 422 against "
        "66.2 MB per second single-threaded, 6.4 times, on an M1 Pro from a "
        "3-fork JMH run. The against-self result is printed on the plate: the "
        "JDK's own Adler-32 intrinsic does 14.06 GB per second and is not "
        "beaten; the hand-vectorised checksum reaches 4.26, bit-identical to "
        "java.util.zip.",
        key="plate-2-jetpack.svg",
        col=(148, 880), frame=JET_FRAME,
    ) + css_close() + body + "</svg>"


# ══════════════════════════════════════════════════ the mobile hero
#
# 440u canvas, its own bus at MBUS_X. No email line here: the mobile set's
# gate direction is drawn-numbers ⊆ description, and "aesh.03.23" can never
# match a word-boundary number test — the address lives on the desktop hero
# and behind the email chip, which mobile readers get too.
def m_hero() -> str:
    # drops at 178/188: the only x-corridor that clears the RLS/SIMD labels
    # (centered on 140), the row labels (32.. and 200..) and the automl label
    # beside its tile (88..167 with the +4% skew) at every y they pass.
    d_verd = "M178,214 V548 Q178,560 166,560 H52 Q40,560 40,572 V620"
    c_verd = "M178,218 V548 Q178,560 166,560 H52 Q40,560 40,572 V617.5"
    d_rust = "M188,324 V564 Q188,576 176,576 H66 Q54,576 54,588 V620"
    c_rust = "M188,328 V564 Q188,576 176,576 H66 Q54,576 54,588 V617.5"
    d_zinc = "M68,458 V620"
    c_zinc = "M68,462 V617.5"
    body = (
        f'<text x="32" y="64" class="d" font-size="30" letter-spacing="0.5">AYUSH YADAV</text>'
        f'<text x="32" y="96" font-size="13.5">Systems, from SIMD kernels</text>'
        f'<text x="32" y="114" font-size="13.5">to the browser they run in.</text>'
        f'<text x="32" y="138" class="dim" font-size="12">open to full-time software engineering roles</text>'
        f'<rect x="32" y="152" width="8" height="8" fill="{T["verd"]}"/>'
        + lbl(48, 160, "EVERY EDGE IS A CHECKABLE CLAIM", cls="ts mid", size=10, ls=1.4)
        + bus("verd", "M84,214 H196", C=25, cd="M88,214 H192")
        + bus("rust", "M84,324 H196", C=150, cd="M88,324 H192")
        + f'<path class="bus" stroke="{T["zinc"]}" stroke-dasharray="3 6" d="M196,464 H172"/>'
        + f'<circle cx="166" cy="464" r="3" fill="none" stroke="{T["zinc"]}" stroke-width="2"/>'
        + bus("verd", d_verd, C=0, cd=c_verd)
        + bus("rust", d_rust, C=87, cd=c_rust)
        + bus("zinc", d_zinc, C=41, cd=c_zinc)
        + pulse(c_verd, 900, 400) + pulse(c_rust, 850, 530) + pulse(c_zinc, 350, 680)
        + mark("cadence", 32, 190, 48) + mark("applied", 200, 190, 48)
        + mark("glyph", 32, 300, 48) + mark("jetpack", 200, 300, 48)
        + mark("automl", 32, 410, 48) + mark("visualassist", 200, 440, 48)
        + lbl(140, 204, "RLS · FORCED", size=9.5, anchor="middle")
        + lbl(140, 314, "SIMD", size=9.5, anchor="middle")
        + lbl(32, 258, "V · CADENCE", size=9.5) + lbl(200, 258, "VI · APPLIED", size=9.5)
        + lbl(32, 368, "III · GLYPH", size=9.5) + lbl(200, 368, "II · JETPACK", size=9.5)
        + lbl(88, 436, "IV · AUTOML", size=9.5)
        + lbl(200, 508, "VII · VISUALASSIST", size=9.5)
        + lbl(200, 524, "NO URL — NEEDS AN IPHONE IN HAND", cls="ts dim", size=9, ls=0.5)
    )
    return head(
        620,
        "Ayush Yadav — the estate as one board",
        "Ayush Yadav — the estate drawn as one circuit board, phone cut. Six "
        "product marks on a shared bus; the printed edges are checkable claims "
        "— Cadence and Applied share forced row-level security, Glyph and "
        "jetpack share SIMD. VisualAssist hangs on an open stub: no URL, it "
        "needs an iPhone in hand. Open to full-time software engineering roles.",
        key="m-0-hero.svg",
        col=(28, 414), frame=MOB_FRAME, w=440,
    ) + css_close() + body + "</svg>"


# ── declared frames (top, rightGap, bottomGap), baked from gate.mjs
# measurement on this machine; tolerance 4 absorbs the CI ascent skew.
HERO_FRAME = (30, 37.7, 0)
JET_FRAME = (2.5, 55.9, 2.5)
MOB_FRAME = (36, 58, 0)
CHIP_FRAME = {
    "portfolio": (4, 0.5, 4), "resume": (4, 0.5, 4),
    "email": (4, 0.5, 4), "linkedin": (4, 0.5, 4),
}

PLATES = {
    "plate-0-hero.svg": plate_hero,
    "plate-link-portfolio.svg": make_chip("portfolio"),
    "plate-link-resume.svg": make_chip("resume"),
    "plate-link-email.svg": make_chip("email"),
    "plate-link-linkedin.svg": make_chip("linkedin"),
    "plate-2-jetpack.svg": plate_jetpack,
}
MOBILE = {"m-0-hero.svg": m_hero}

_re = re
_fail: list[str] = []


def _check_coverage(fn: str, svg: str) -> None:
    """Every character a plate draws must be in the charset of the face that
    will render it — a glyph outside its subset falls back to a platform font
    and NOTHING downstream can see it: the build succeeds, gate.mjs passes
    (the geometry is still legal), and the reader gets a platform sans mid-
    word. font-weight INHERITS, so the class stack is a union: a tspan inside
    a .ts run renders from the 600 face whatever its own classes say.
    """
    _ent = {'&amp;': '&', '&lt;': '<', '&gt;': '>', '&#39;': "'",
            '&quot;': '"', '&#8217;': '’'}
    for m in _re.finditer(r'<text([^>]*)>(.*?)</text>', svg, _re.S):
        stack = [set(_re.search(r'class="([^"]*)"', m.group(1)).group(1).split()
                     if _re.search(r'class="([^"]*)"', m.group(1)) else [])]
        for part in _re.split(r'(<tspan[^>]*>|</tspan>)', m.group(2)):
            if part.startswith('<tspan'):
                c = _re.search(r'class="([^"]*)"', part)
                stack.append(stack[-1] | set(c.group(1).split() if c else []))
                continue
            if part == '</tspan>':
                stack.pop()
                continue
            for k, v in _ent.items():
                part = part.replace(k, v)
            cls = stack[-1]
            face, chars = (('display', DISPLAY_CHARS) if 'd' in cls else
                           ('label', LABEL_CHARS) if 'ts' in cls else
                           ('text', TEXT_CHARS))
            for ch in part:
                if ch not in chars and ch != '\n':
                    _fail.append(f"{fn}: draws {ch!r} in the {face} face, which does not "
                                 f"carry it — it would render in a platform font "
                                 f"(charsets.py + build/subset-fonts.py)")


# One build, two documents. Dark keeps every path it has always had; light
# lands in assets/light/ under the SAME basenames (gate.mjs keys on that).
for _theme in ("dark", "light"):
    set_theme(_theme)
    _out = OUT if _theme == "dark" else OUT / "light"
    _out.mkdir(exist_ok=True)
    # a plate this build no longer authors must not survive on disk: the
    # gates sweep the DIRECTORY, so a stale file is a stale claim surface
    for _stale in _out.glob("*.svg"):
        if _stale.name not in PLATES and _stale.name not in MOBILE:
            _stale.unlink()
            print(f"{_theme:5s} {_stale.name}: removed (no longer authored)")
    for _fn, _gen in (PLATES | MOBILE).items():
        _path = _out / _fn
        _path.write_text(_gen())
        try:
            _xml.parseString(_path.read_text())
        except Exception as e:
            _fail.append(f"{_theme}/{_fn}: MALFORMED XML — {e}")
        if _theme == "dark":                    # text is theme-invariant
            _check_coverage(_fn, _path.read_text())
        print(f"{_theme:5s} {_fn}: {_path.stat().st_size:,} bytes")
set_theme("dark")

# ────────────────────────────────────────────────── alt/desc/README agreement
# Every description is authored once in ALT and must reach the README verbatim.
(OUT / "alt.json").write_text(json.dumps(ALT, indent=2, sort_keys=True))
_readme = ROOT.parent / "README.md"
# Fails CLOSED — a check allowed not to run is not one (the conditional form
# of this once skipped in silence on a case-insensitive filesystem).
if not _readme.exists():
    _fail.append(f"{_readme}: not found — the alt/desc agreement cannot be "
                 f"checked, and a check that cannot run must not pass")
else:
    _md = _readme.read_text()
    for _fn, _desc in ALT.items():
        _m = _re.search(rf'<img src="\./assets/{_re.escape(_fn)}"[^>]*?alt="([^"]*)"', _md)
        if not _m:
            _fail.append(f"{_fn}: no <img> with an alt in README.md")
        elif _m.group(1).strip() != _desc.strip():
            _fail.append(f"{_fn}: README alt has drifted from the plate's own description")
    # Both directions, over every published file. A plate authored and never
    # referenced is a file no reader can reach; a reference to a plate never
    # authored renders as a torn icon on the page itself. The trailing
    # lookahead is load-bearing: without it a typo'd reference matches
    # through `.svg` and reads as present.
    _want = {f"./assets/{_d}{_f}" for _f in set(PLATES) | set(MOBILE)
             for _d in ("", "light/")}
    _have = set(_re.findall(r'\./assets/(?:light/)?[\w.-]+\.svg(?![\w.-])', _md))
    for _p in sorted(_want - _have):
        _fail.append(f"{_p}: this build authors it and README.md references it nowhere")
    for _p in sorted(_have - _want):
        _fail.append(f"{_p}: README.md references it and no build authors it — broken image")

if _fail:
    print("\nGATE FAILED:")
    for f in _fail:
        print(f"  · {f}")
    raise SystemExit(1)
print("build clean: plates, coverage, XML, alt/README agreement")
