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


def comet(bus: str, d: str, C: float = 0.0,
          lens: tuple[float, ...] = COMET) -> str:
    """The moving current for one trace segment (no track — see bus()).

    `lens` is the ramp's segment lengths, a parameter because a comet only
    reads as one on a run LONGER than its own segments: where a segment is
    wider than the window it crosses, it fills that window edge to edge and
    the frame stops changing for as long as it takes to cross. Long traces
    never meet this; the link row's 22u run does, and passes a scaled set —
    see the carrier note in chip().
    """
    out = ""
    end = C
    for L, col in zip(lens, T["ramp"][bus]):
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
         col: tuple[float, float] = (44, 886),
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
#   collectors  y=400/415/430
#   fan band    y=470-534: the collectors do NOT stop at the old bottom edge
#               — each continues into a drop aimed at a link-row lead (see
#               the link row's calibration block). verd's collector column at
#               x=75 IS the portfolio drop, dead straight; rust tees at y498
#               (resume branch + linkedin corner); zinc turns at y486 above
#               rust's tier, so the two trees nest and nothing crosses.
def plate_hero() -> str:
    pr, pl, pe = DROP["resume"], DROP["linkedin"], DROP["email"]
    d_verd = "M766,80 V388 Q766,400 754,400 H87 Q75,400 75,412 V534"
    d_rust = ("M744,216 V403 Q744,415 732,415 H102 Q90,415 90,427 V486 "
              f"Q90,498 102,498 H{pl - 12} Q{pl},498 {pl},510 V534")
    d_zinc = ("M612,130 V418 Q612,430 600,430 H129 Q117,430 117,442 V474 "
              f"Q117,486 129,486 H{pe - 12} Q{pe},486 {pe},498 V534")
    c_verd = "M766,84 V388 Q766,400 754,400 H87 Q75,400 75,412 V531.5"
    c_rust = ("M744,220 V403 Q744,415 732,415 H102 Q90,415 90,427 V486 "
              f"Q90,498 102,498 H{pl - 12} Q{pl},498 {pl},510 V531.5")
    c_zinc = ("M612,134 V418 Q612,430 600,430 H129 Q117,430 117,442 V474 "
              f"Q117,486 129,486 H{pe - 12} Q{pe},486 {pe},498 V531.5")
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
        # the resume branch tees off rust's fan tier; junction dot = connected
        + bus("rust", f"M{pr},498 V534", C=55, cd=f"M{pr},500.5 V531.5")
        + f'<circle cx="{pr}" cy="498" r="2.6" fill="{T["rust"]}"/>'
        + pulse(c_verd, 1200, 400) + pulse(c_rust, 1200, 530) + pulse(c_zinc, 1400, 680)
        # the marks — automl deliberately BETWEEN the rows (see the registry
        # above): its tile at (520,140) is what makes the board uneven, and
        # the zinc feed out of its right flank at y=168 is only connected
        # while the tile is here.
        + mark("automl", 520, 140, 56) + mark("cadence", 620, 52, 56)
        + mark("applied", 784, 52, 56)
        + mark("glyph", 620, 188, 56) + mark("jetpack", 784, 188, 56)
        + mark("visualassist", 48, 300, 56)
        # edge labels sit clear of every trace; drops were routed around them.
        # POSTGRES is VERTICAL, reading up the riser it names: baseline at
        # x=600 puts the rotated em box at x 590-603, 8u clear of the riser
        # comet's left edge at 611; rotation puts the +4% Linux advance skew
        # on the label's HEIGHT (y 92-158 with skew), which nothing crosses.
        + '<text x="600" y="124" class="ts dim" font-size="10" letter-spacing="1.4" '
          'text-anchor="middle" transform="rotate(-90 600 124)">POSTGRES</text>'
        + lbl(730, 68, "RLS · FORCED", size=10.5, anchor="middle")
        + lbl(730, 202, "SIMD", size=10.5, anchor="middle")
        + lbl(520, 212, "IV · AUTOML", size=10.5)
        + lbl(620, 124, "V · CADENCE", size=10.5) + lbl(784, 124, "VI · APPLIED", size=10.5)
        + lbl(620, 260, "III · GLYPH", size=10.5) + lbl(784, 260, "II · JETPACK", size=10.5)
        + lbl(48, 376, "VII · VISUALASSIST", size=10.5)
        + lbl(48, 391, "NO URL — IT NEEDS AN IPHONE WITH LIDAR, IN YOUR HAND", cls="ts dim", size=10, ls=1.1)
    )
    return head(
        534,
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


# ══════════════════════════════════════════════════ the link row
#
# Four ports on the bus, each its own SVG so each is its own link in the
# README — the way out of "an SVG in an <img> cannot hold a link". EACH CHIP
# IS AN OPAQUE MODULE, and that is forced by the medium, not chosen: GitHub's
# markdown pipeline SPLITS a <picture> inside a link — the <source> stays in
# the author's <a>, the <img> is extracted and auto-linked to the asset file
# itself (probed against the real /markdown API, 2026-08-12). So a chip
# cannot be both clickable and theme-switched. A component is a physical
# object that does not recolour with the room: the chip is a near-black
# module in the marks' own family language, self-grounded, ONE artwork
# legible on every canvas, linked as [<img>](url) — the nesting that
# survives. Everything inside grades against the module via check 10's local
# grounds; only ink that rides the changing canvas (the module hairline, the
# leads) uses tones measured on BOTH grounds.
#
# HOW THE ROW SITS ON THE BOARD — re-authored 2026-08-13. The previous strip
# ran three self-contained horizontal lanes edge-to-edge through the chips;
# they continued nothing above or below, so the row read as a foreign object
# breaking the page bus. Now each chip is a COMPONENT ON A TRACE: the hero's
# fan band (its bottom 64u) drops one lane per port; the lead enters the
# chip's top edge at the badge column, dives under the opaque package,
# re-emerges below the badge carrying the comet, and exits the bottom edge;
# plate-link-return.svg merges the four drops back to BUS_X and lands the
# page bus on plate II at the x it left the hero. The README contract is one
# line of adjacent links, IN ROUTING ORDER:
#
#   [portfolio][resume][linkedin][email]     GAP = 3.8px between adjacent
#                                            linked images (measured on the
#                                            live profile, 2026-08-12)
#
# CALIBRATION. Chips render at natural size; every 900-wide plate scales to
# the profile column. Registration between a fixed-px image and a scaled one
# is exact at ONE width, so the row is calibrated to the canonical 846px
# column (900 × PAGE, the wide-desktop measurement; the demo renders at it).
# At narrower columns the two seams drift by the scale difference — a small
# jog, never a collision — and the 580.4px row still clears the 590px column
# GitHub serves at 1024 viewports without wrapping. The row's left edge is
# the portfolio module at x=45.5 ≈ the hero's content margin (48 × PAGE).
#
# The LEAD tones are the buses' component-land register: one artwork means a
# lead crosses both canvases, so each is measured on #ffffff / #212830 / the
# tile (scratchpad, 2026-08-13): verd #3E8E76 3.94/3.78/5.03, rust #C1663A
# 4.02/3.71/4.93, zinc #79848C 3.82/3.89/5.18. Comets keep the dark ramps
# but run ONLY on the module, below the badge: a ramp head is ~1.3:1 on
# white canvas, and a travelling dash may never cross the '@' badge text
# (gate check 3 reads that as a strikethrough) — which is also why the badge
# is opaque tile now: it occludes the static lead instead of wearing it.
PAGE = 846 / 900              # canonical profile column / authored width
GAP = 3.8                     # measured inter-image gap, adjacent links
CHIP_H = 88
CHIP_EDGE = "#79848C"         # 3.89:1 on #212830, 3.82 on #fff, 5.37 on #010409
LEAD = {"verd": "#3E8E76", "rust": "#C1663A", "zinc": "#79848C"}
CHIP_RUN = 22                 # the comet's visible run, y58->y80 (see chip())
CHIP_COMET = (17, 14, 11)     # COMET halved — every segment inside CHIP_RUN
CHIP_SPAN = 52.5              # four of them per PAT, so every gap is 10.5u

# the row layout, in page px: (module width, left inset). Portfolio's inset
# puts its module edge on the content margin, and its lead at 70.5 = board
# 75 × PAGE — the hero's verd collector column runs dead straight through it.
ROW = {"portfolio": (190, 45), "resume": (108, 0),
       "linkedin": (124, 0), "email": (102, 0)}
_rx, CHIP_LEAD = 0.0, {}
for _k, (_w, _pad) in ROW.items():
    CHIP_LEAD[_k] = _rx + (_pad + 25.5 if _pad else 24)
    _rx += _pad + _w + GAP
# where the hero's fan band drops each lead, in board units
DROP = {k: round(v / PAGE, 1) for k, v in CHIP_LEAD.items()}


def _port_glyphs(kind: str, dx: float, dy: float) -> str:
    """The port marks, drawn here in the family language. White ink only —
    colour on this page belongs to the products and the buses. The offset
    rides EVERY element's own transform, never a wrapping <g>: gate.mjs
    composes by nearest enclosing group, and these must stay in the module's.
    """
    tr = f' transform="translate({dx},{dy})"'
    if kind == "www":       # a globe: equator and one meridian
        return (f'<circle{tr} cx="24" cy="24" r="7.2" fill="none" stroke="#F7F8F8" stroke-width="1.7"/>'
                f'<path{tr} d="M16.8,24 H31.2" fill="none" stroke="#F7F8F8" stroke-width="1.5"/>'
                f'<path{tr} d="M24,16.8 C20.6,20.4 20.6,27.6 24,31.2 C27.4,27.6 27.4,20.4 24,16.8"'
                ' fill="none" stroke="#F7F8F8" stroke-width="1.5"/>')
    if kind == "doc":       # a sheet with three set lines
        return (f'<rect{tr} x="18" y="16" width="12" height="16" rx="2" fill="none" stroke="#F7F8F8" stroke-width="1.7"/>'
                f'<path{tr} d="M21,21.5 H27 M21,25 H27 M21,28.5 H25" fill="none" stroke="#F7F8F8" stroke-width="1.5" stroke-linecap="round"/>')
    if kind == "at":
        return (f'<text{tr} x="24" y="29.5" class="ts" font-size="17" text-anchor="middle" style="fill:#F7F8F8">@</text>')
    if kind == "in":
        return (f'<text{tr} x="24" y="29" class="ts" font-size="15.5" text-anchor="middle" style="fill:#F7F8F8">in</text>')
    raise SystemExit(f"unknown port glyph {kind}")


def chip(kind: str, label: str, glyph: str, tap_bus: str,
         phase: float, title: str, desc: str, key: str,
         frame: tuple[float, float, float]) -> str:
    global T
    saved = T
    # the module carries the dark surface on every canvas: only data-canvas,
    # written by head() from the theme, differs between the two files.
    T = dict(saved, ink=DARK["ink"], mid=DARK["mid"], dim=DARK["dim"],
             verd=DARK["verd"], rust=DARK["rust"], zinc=DARK["zinc"],
             ramp=DARK["ramp"], edge=CHIP_EDGE)
    try:
        w_mod, pad = ROW[kind]
        w = pad + w_mod
        sx = pad + 25.5 if pad else 24          # the lead = the badge column
        lead = LEAD[tap_bus]
        # the through-lead: the trace this component sits on, canvas-to-canvas
        track = f'<path class="bus" stroke="{lead}" d="M{sx},0 V{CHIP_H}"/>'
        module = (
            # the module and its fittings, one composed object; the rect is
            # FIRST in document order so it is the plate's contrast ground
            f'<g><rect x="{pad + 0.5}" y="20" width="{w_mod - 1}" height="64" rx="3" '
            f'fill="{TILE}" stroke="{CHIP_EDGE}" stroke-width="1"/>'
            # entry and exit pads, just inside the edges the lead pierces —
            # vivid on the tile, where the true bus colours are legal
            + "".join(f'<rect x="{sx - 2.5}" y="{py}" width="5" height="4" fill="{T[tap_bus]}"/>'
                      for py in (20.5, 79.5))
            # the trace where it is VISIBLE on the package: a stub above the
            # badge, and the run below it that carries the comet
            + f'<path class="bus" stroke="{lead}" d="M{sx},20 V26 M{sx},54 V84"/>'
            # the port badge: OPAQUE tile, occluding the lead (see the note
            # above on the '@' strikethrough), ruled like the marks
            + f'<rect x="{sx - 14}" y="26" width="28" height="28" rx="8" fill="{TILE}" '
            f'stroke="{STRUCT}" stroke-width="1.2"/>' + _port_glyphs(glyph, sx - 24, 16)
            + lbl(pad + 46, 44.5, label, cls="ts", size=11.5, ls=1.3) + "</g>"
        )
        # THE CARRIER, SIZED TO THE RUN IT RIDES. This was two page-sized
        # comets 105 pattern-units apart, and the note here read "one of them
        # is always on-path, so the carrier never blinks". Never blank was the
        # wrong property to check for. The page's comet is 84u long and its
        # three segments are 34/28/22 (COMET); this visible run is 22u, so
        # every segment is at least as wide as the window it crosses, and
        # while one covers the run the chip draws a flat uniform bar — a still
        # image, not a slow one. Measured per interval with motion.mjs's own
        # sampler (2026-08-13): the head holds the run frozen for 34-22 = 12u
        # of travel and the second segment for 28-22 = 6u, once each per comet
        # per pattern. 36 of every 210u, 17% of the loop, in stalls of
        # 120-157ms; any two samples landing inside one stall diff to EXACTLY
        # zero pixels. That is what pinned three of these four chips one
        # interval above the 95% carrier floor with nothing left to give —
        # email cleared it only because its phase happened to put a single
        # sample inside the band, which is luck, not margin.
        #
        # So the comet is halved and run four to the pattern instead of two:
        # same PAT, same period, same speed, and the same ink duty cycle
        # (4x42 = 2x84 of 210). The longest uniform region is now 17u and the
        # longest gap 10.5u, both inside the 22u window, so every frame
        # carries a moving boundary and the run never drains below 11.5u
        # either — where it used to fall to a 1u sliver. THE CONSTRAINT, for
        # anyone retuning this: segment < CHIP_RUN and gap < CHIP_RUN. Both,
        # or the frame goes flat again — flat-full or flat-empty, the gate and
        # the eye cannot tell those apart and neither should they.
        current = "".join(
            comet(tap_bus, f"M{sx},58 V80", C=phase + i * CHIP_SPAN, lens=CHIP_COMET)
            for i in range(4))
        # THE TYPE COLUMN this chip declares (gate check 5, which holds a
        # left-anchored label 6u short of the declared edge). Default: 8u in
        # from the canvas left, 4u short of its right.
        #
        # RÉSUMÉ is the one label that nearly fills its module — drawn 46->102
        # in a 108-wide chip, identical at all 40 samples — so the 6u margin
        # needs 105.85 and the blanket `w - 4` (= 104) declared an edge 2u
        # inside what the plate DRAWS. The module's own ink edge is this
        # chip's column: type may not leave the package, which is a decision
        # a reviewer can read, and the label clears it with 1.65u. Written as
        # its derivation, not as 107.5, so it follows the module width.
        col = (pad + 8, pad + w_mod - 0.5 if kind == "resume" else w - 4)
        return head(CHIP_H, title, desc, key=key, col=col, frame=frame,
                    faces="6", w=w) + css_close() + track + module + current + "</svg>"
    finally:
        T = saved


CHIPS = {
    # filename fragment: (label, glyph, tap bus, carrier phase — the chip's
    # four comets sit at phase + 0/1/2/3 x CHIP_SPAN, so no two ports open on
    # the same frame: mod 52.5 these are 12, 35, 42.5, 13.5.
    "portfolio": ("AYUSH-YADAV.COM", "www", "verd", 12,
                  "ayush-yadav.com — the portfolio",
                  "Port one of four on the link bus: ayush-yadav.com, the portfolio."),
    "resume":    ("RÉSUMÉ", "doc", "rust", 140,
                  "résumé — PDF",
                  "Port two of four on the link bus: the résumé, as a PDF."),
    "linkedin":  ("LINKEDIN", "in", "rust", 200,
                  "linkedin — profile",
                  "Port three of four on the link bus: the LinkedIn profile."),
    "email":     ("EMAIL", "at", "zinc", 66,
                  "email — aesh at gmail",
                  "Port four of four on the link bus: email; opens a mail draft."),
}


def make_chip(kind: str):
    label, glyph, tap, phase, title, desc = CHIPS[kind]
    fn = f"plate-link-{kind}.svg"
    return lambda: chip(kind, label, glyph, tap, phase, title, desc, fn,
                        CHIP_FRAME[kind])


# ══════════════════════════════════════════════════ the return plate
#
# Below the link row the four drops merge back into the page bus and land on
# plate II at BUS_X — the other half of "the buses visibly survive the row".
# Tier order mirrors the hero's fan band (verd y=14, rust y=32, zinc y=50):
# with the ports in routing order the three trees nest and nothing crosses.
# The one line of silkscreen is wayfinding, not decoration — it names what
# the bus runs into next, and it is the only text between the ports and
# section II.
def plate_return() -> str:
    pv, pr, pl, pe = (DROP[k] for k in ("portfolio", "resume", "linkedin", "email"))
    body = (
        bus("verd", f"M{pv},0 V9 Q{pv},14 {pv - 5},14 H68 Q63,14 63,19 V64",
            C=30, cd=f"M{pv},2.5 V9 Q{pv},14 {pv - 5},14 H68 Q63,14 63,19 V61.5")
        + bus("rust", f"M{pl},0 V20 Q{pl},32 {pl - 12},32 H102 Q90,32 90,44 V64",
              C=150, cd=f"M{pl},2.5 V20 Q{pl},32 {pl - 12},32 H102 Q90,32 90,44 V61.5")
        # the resume drop joins rust's tier; junction dot = connected
        + bus("rust", f"M{pr},0 V32", C=64, cd=f"M{pr},2.5 V29.5")
        + f'<circle cx="{pr}" cy="32" r="2.6" fill="{T["rust"]}"/>'
        + bus("zinc", f"M{pe},0 V38 Q{pe},50 {pe - 12},50 H129 Q117,50 117,62 V64",
              C=100, cd=f"M{pe},2.5 V38 Q{pe},50 {pe - 12},50 H129 Q117,50 117,62 V61.5")
        + lbl(640, 58, "THE EVIDENCE · SECTIONS II — VII", size=10.5)
    )
    return head(
        64,
        "the link ports rejoin the page bus",
        "The four link ports hand back to the page bus — the three lanes "
        "merge and continue into the evidence, sections two to seven.",
        key="plate-link-return.svg",
        col=(44, 886), frame=RET_FRAME,
        # This plate speaks in ONE line of silkscreen, class "ts" — Commissioner
        # 600 and nothing else. It was shipping the display 800 and the text 400
        # as well: ~37KB of base64 no glyph on it ever asks for, sent to every
        # reader of the profile, in both themes. Same declaration a chip makes.
        faces="6",
    ) + css_close() + body + "</svg>"


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


# ══════════════════════════════════════════════════ I · work
#
# The one section with no product mark, drawn as the thing a board does when
# the part exists but is not fitted: an UNPOPULATED FOOTPRINT. The dashed
# outline sits in the exact slot every other section's mark occupies, the
# zinc tap runs to its entry pad and stops — a year of paid work, and the
# component is off-board. Drawing a sigil for it was rejected in the brief:
# the absence is the claim. The eyebrow at top right answers the return
# plate's "SECTIONS II — VII" wayfinding: I is the exception, and says so.
def plate_work() -> str:
    body = (
        bus("verd", "M63,0 V320", C=95, cd="M63,2.5 V317.5")
        + bus("rust", "M90,0 V320", C=10, cd="M90,2.5 V317.5")
        + bus("zinc", "M117,0 V320", C=160, cd="M117,2.5 V317.5")
        # the tap: onto the pad, and no further. The comet dies here every
        # 2750ms, which is the drawing doing the section's arguing.
        + bus("zinc", "M117,120 H148.5", C=48, cd="M121,120 H144")
        # one <g>, like the chips' modules: the pad pierces the outline it
        # serves, which is composition, not collision
        + f'<g><rect x="150.75" y="96.75" width="46.5" height="46.5" rx="12" '
          f'fill="none" stroke="{T["zinc"]}" stroke-width="1.4" stroke-dasharray="5 4"/>'
          f'<rect x="148.25" y="118" width="5" height="4" fill="{T["zinc"]}"/></g>'
        + lbl(150, 163, "NO PRODUCT MARK — THE WORK IS OFF-REPO", size=10, ls=1.1)
        + f'<text x="150" y="54" class="d" font-size="30" letter-spacing="0.5">I — WORK</text>'
        + f'<text x="150" y="76" class="dim" font-size="14.5">twelve months of production data work — none of it public.</text>'
        + lbl(852, 30, "FIRST, THE EXCEPTION — ATTESTED, NOT DERIVED", size=10.5, anchor="end")
        + f'<text x="584" y="150" class="d" font-size="56">57.8M</text>'
        + f'<text x="584" y="186" class="dim" font-size="13">rows in one field-usage table,</text>'
        + f'<text x="584" y="204" class="dim" font-size="13">from 1.6M Oracle Analytics query logs.</text>'
        + f'<rect x="150" y="248" width="4" height="16" fill="{T["zinc"]}"/>'
        + f'<text x="164" y="261" class="mid" font-size="14">none of these numbers can be re-derived by you.</text>'
        + f'<text x="164" y="281" class="dim" font-size="13">the data belongs to Miami University and to a competition — this section is my word.</text>'
    )
    return head(
        320,
        "I · Work — a year of paid data work; the part is off-board",
        "I · Work — the one section drawn as an empty footprint: a component "
        "the board expects that is not fitted, because the year of paid work "
        "is off-repo. A 57.8M-row field-usage table, distilled from 1.6M "
        "Oracle Analytics query logs at Miami University. None of these "
        "numbers can be re-derived by a reader — the data belongs to Miami "
        "University and to a competition; this section is attested, not "
        "derived.",
        key="plate-1-work.svg",
        col=(148, 880), frame=WORK_FRAME,
    ) + css_close() + body + "</svg>"


# ══════════════════════════════════════════════════ III · glyph
#
# The section drawn as its own part: three register-lane bundles — NEON,
# AVX2, AVX-512, the ISAs the kernels were written for — fed off the SIMD
# bus and converging on the one benchmark chip, then dropping to the package
# that actually ships: the wasm_simd128 build, byte-counted and checked
# daily. The admission block runs three lines, the longest on the page,
# because this section owes two of them: the size-floor slowdown and the
# checkpoint the test set picked.
def plate_glyph() -> str:
    # lane counts are the ISAs' own: 128/256/512-bit registers hold 2/4/8
    # 64-bit lanes, and the 1:2:4 ratio holds for any element width — the
    # bundle heights ARE the claim the section makes about register width.
    lanes = ""
    for label, n, yc in (("NEON", 2, 175), ("AVX2", 4, 235), ("AVX-512", 8, 295)):
        y0 = yc - 3 * (n - 1)
        rules = " ".join(f"M300,{y0 + i * 6} H420" for i in range(n))
        lanes += (lbl(300, y0 - 10, label, size=10, ls=1.2)
                  + f'<path fill="none" stroke="{T["zinc"]}" stroke-width="1.4" d="{rules}"/>')
    body = (
        bus("verd", "M63,0 V448", C=40, cd="M63,2.5 V445.5")
        + bus("rust", "M90,0 V448", C=130, cd="M90,2.5 V445.5")
        + bus("zinc", "M117,0 V448", C=8, cd="M117,2.5 V445.5")
        # SIMD tap into the mark, then the feeder down the bundle column
        + bus("rust", "M90,120 H150", C=88, cd="M94,120 H145")
        + bus("rust", "M198,120 H264 V295", C=30, cd="M202,120 H264 V292")
        + f'<circle cx="264" cy="175" r="2.6" fill="{T["rust"]}"/>'
        + f'<circle cx="264" cy="235" r="2.6" fill="{T["rust"]}"/>'
        + bus("rust", "M264,175 H300", C=60, cd="M266.5,175 H297")
        + bus("rust", "M264,235 H300", C=115, cd="M266.5,235 H297")
        + bus("rust", "M264,295 H300", C=170, cd="M266.5,295 H297")
        + lanes
        # the collector gathers the three bundles into the benchmark chip
        + f'<path class="bus" stroke="{T["rust"]}" d="M420,175 H456 V295 H420 M420,235 H456"/>'
        + bus("rust", "M456,235 H492", C=142, cd="M422,175 H456 V235 H489")
        + f'<rect x="492" y="214" width="170" height="42" rx="8" fill="none" '
          f'stroke="{T["rust"]}" stroke-width="1.6"/>'
        + lbl(504, 240, "BENCHDOT/256", cls="ts", size=11.5, ls=1.3)
        # and drops to the package that ships
        + bus("rust", "M577,256 V300", C=55, cd="M577,258.5 V296")
        + f'<rect x="492" y="300" width="208" height="42" rx="8" fill="none" '
          f'stroke="{T["zinc"]}" stroke-width="1.6"/>'
        + lbl(504, 326, "WASM_SIMD128 · 43,751 B", cls="ts", size=11.5, ls=1.3)
        + lbl(492, 360, "BYTE-IDENTICAL TO MAIN · CHECKED DAILY IN CI", size=10, ls=1.1)
        + mark("glyph", 150, 96, 48)
        + f'<text x="150" y="54" class="d" font-size="30" letter-spacing="0.5">III — GLYPH</text>'
        + f'<text x="150" y="76" class="dim" font-size="14.5">SIMD kernels over a net the course provided.</text>'
        + f'<text x="660" y="150" class="d" font-size="62">3.5×</text>'
        + f'<text x="660" y="188" class="dim" font-size="13">benchDot/256 — course baseline,</text>'
        + f'<text x="660" y="206" class="dim" font-size="13">reference machine, committed run.</text>'
        + f'<rect x="150" y="382" width="4" height="16" fill="{T["rust"]}"/>'
        + f'<text x="164" y="395" class="mid" font-size="14">the same flags run 10.7× slower on benchAxpy/128 — below the size floor,</text>'
        + f'<text x="164" y="415" class="dim" font-size="13">where threading costs more than it pays. and 97.01% is a training-time</text>'
        + f'<text x="164" y="433" class="dim" font-size="13">number: the test set that graded the net also picked its checkpoint.</text>'
    )
    return head(
        448,
        "III · Glyph — SIMD kernels over a course-provided net: 3.5× where the size is right, 10.7× slower where it is not",
        "III · Glyph — SIMD kernels over a course-provided MNIST net, drawn "
        "as three register-lane bundles — NEON, AVX2, AVX-512 — converging "
        "on benchDot/256: 3.5× over the course baseline on the reference "
        "machine. The package that ships is WASM_SIMD128, 43,751 bytes, "
        "byte-identical to main and checked daily in CI. The against-self "
        "results are printed: the same flags run 10.7× slower on "
        "benchAxpy/128, below the size floor, and 97.01% is a training-time "
        "number — the test set that graded the net also picked its "
        "checkpoint.",
        key="plate-3-glyph.svg",
        col=(148, 880), frame=GLYPH_FRAME,
    ) + css_close() + body + "</svg>"


# ══════════════════════════════════════════════════ IV · automl
#
# The dispatcher drawn as its registry: a 44-pin strip — one pin per tool
# the graph defines, emitted by loop so the count is true by construction —
# with seven tool-set taps hanging below it. No tap spans the strip, which
# is the claim: no phase is handed all 44. The per-phase counts (15/7/29)
# were cut by the prose inventory and are deliberately NOT drawn, so no
# bracket on this plate is countable into a number the page no longer backs.
def plate_automl() -> str:
    pins = " ".join(f"M{276 + i * (604 - 276) / 43:.1f},150 V170" for i in range(44))
    drops = " ".join(f"M{300 + i * 45},182 V218" for i in range(7))
    sets = "".join(f'<circle cx="{300 + i * 45}" cy="224" r="5" fill="none" '
                   f'stroke="{T["zinc"]}" stroke-width="2"/>' for i in range(7))
    body = (
        bus("verd", "M63,0 V380", C=170, cd="M63,2.5 V377.5")
        + bus("rust", "M90,0 V380", C=85, cd="M90,2.5 V377.5")
        + bus("zinc", "M117,0 V380", C=25, cd="M117,2.5 V377.5")
        + bus("zinc", "M117,120 H150", C=55, cd="M121,120 H145")
        + bus("zinc", "M198,120 H240 V160 H262", C=96, cd="M202,120 H240 V160 H258")
        + f'<rect x="262" y="138" width="356" height="44" rx="4" fill="none" '
          f'stroke="{T["zinc"]}" stroke-width="1.3"/>'
        + f'<path fill="none" stroke="{T["zinc"]}" stroke-width="2" d="{pins}"/>'
        + lbl(262, 130, "THE REGISTRY · 44 TOOLS DEFINED", size=10, ls=1.1)
        + f'<path fill="none" stroke="{T["zinc"]}" stroke-width="1.4" d="{drops}"/>'
        + sets
        + lbl(300, 256, "SEVEN TOOL SETS — NO PHASE IS HANDED ALL 44", size=10, ls=1.1)
        + mark("automl", 150, 96, 48)
        + f'<text x="150" y="54" class="d" font-size="30" letter-spacing="0.5">IV — AUTOML</text>'
        + f'<text x="150" y="76" class="dim" font-size="14.5">a LangGraph agent, dealt its tools phase by phase.</text>'
        + f'<text x="660" y="160" class="d" font-size="62">44</text>'
        + f'<text x="660" y="198" class="dim" font-size="13">defined across the dispatcher;</text>'
        + f'<text x="660" y="216" class="dim" font-size="13">no phase&#8217;s hand holds them all.</text>'
        + f'<rect x="150" y="308" width="4" height="16" fill="{T["zinc"]}"/>'
        + f'<text x="164" y="321" class="mid" font-size="14">the sandbox guards against accidents, not adversaries.</text>'
        + f'<text x="164" y="341" class="dim" font-size="13">the network is an env var — the beta template renders it bridge; no cap-drop, no pids-limit, no seccomp.</text>'
    )
    return head(
        380,
        "IV · AutoML — 44 tools defined; no phase is handed all of them",
        "IV · AutoML — the dispatcher drawn as its registry: a 44-pin strip, "
        "one pin per tool the graph defines, with seven tool-set taps below "
        "it — no phase is handed all 44. The against-self line is the "
        "sandbox: it guards against accidents, not adversaries — the network "
        "is an env var the beta template renders as bridge, with no "
        "cap-drop, no pids-limit, no seccomp.",
        key="plate-4-automl.svg",
        col=(148, 880), frame=AUTOML_FRAME,
    ) + css_close() + body + "</svg>"


# ══════════════════════════════════════════════════ V · cadence
#
# The whole API drawn as the one part it actually is: 37 entry stubs — one
# per route handler, range(150,331,5), count true by construction — into a
# single serverless package, whose single output crosses a doored wall
# before the 7 table frames behind it. The wall is the section's claim: the
# door is the only way through, because RLS is FORCEd. The app-side guards
# being conditional is the admission, and the drawing agrees — nothing else
# crosses the wall.
def plate_cadence() -> str:
    stubs = " ".join(f"M252,{y} H300" for y in range(150, 331, 5))
    fan = " ".join(f"M600,{y} H628" for y in range(165, 316, 25))
    tables = "".join(f'<rect x="628" y="{y - 9}" width="120" height="18" rx="3" '
                     f'fill="none" stroke="{T["zinc"]}" stroke-width="1.3"/>'
                     for y in range(165, 316, 25))
    body = (
        bus("verd", "M63,0 V440", C=12, cd="M63,2.5 V437.5")
        + bus("rust", "M90,0 V440", C=175, cd="M90,2.5 V437.5")
        + bus("zinc", "M117,0 V440", C=90, cd="M117,2.5 V437.5")
        + bus("verd", "M63,120 H150", C=30, cd="M67,120 H145")
        + bus("verd", "M198,120 H252 V330", C=132, cd="M202,120 H252 V326")
        + f'<path fill="none" stroke="{T["verd"]}" stroke-width="1.4" d="{stubs}"/>'
        + f'<rect x="300" y="140" width="170" height="200" rx="8" fill="none" '
          f'stroke="{T["verd"]}" stroke-width="1.6"/>'
        + lbl(312, 222, "ONE SERVERLESS", cls="ts", size=10, ls=1.1)
        + lbl(312, 238, "FUNCTION", cls="ts", size=10, ls=1.1)
        + lbl(312, 258, "37 ROUTE HANDLERS", cls="ts dim", size=10, ls=1.1)
        + bus("verd", "M496,235 H600", C=66, cd="M500,235 H596")
        # the wall, doored only where the output passes
        + f'<path class="bus" stroke="{T["verd"]}" d="M560,150 V223 M560,247 V330"/>'
        + f'<path class="bus" stroke="{T["verd"]}" d="M566,150 V223 M566,247 V330"/>'
        + lbl(563, 140, "RLS · FORCED", size=10.5, anchor="middle")
        + bus("verd", "M600,165 V315", C=190, cd="M600,168 V312")
        + f'<path fill="none" stroke="{T["verd"]}" stroke-width="1.4" d="{fan}"/>'
        + tables
        + mark("cadence", 150, 96, 48)
        + f'<text x="150" y="54" class="d" font-size="30" letter-spacing="0.5">V — CADENCE</text>'
        + f'<text x="150" y="76" class="dim" font-size="14.5">every route into one function; every row behind RLS.</text>'
        + f'<text x="680" y="70" class="d" font-size="62">37</text>'
        + f'<text x="680" y="108" class="dim" font-size="13">route handlers, one function;</text>'
        + f'<text x="680" y="126" class="dim" font-size="13">RLS FORCEd on all 7 tables.</text>'
        + f'<rect x="150" y="374" width="4" height="16" fill="{T["verd"]}"/>'
        + f'<text x="164" y="387" class="mid" font-size="14">every one of the six services carries a conditional owner guard.</text>'
        + f'<text x="164" y="407" class="dim" font-size="13">a caller that forgets the identity still sends the query; the database&#8217;s refusal cannot be forgotten.</text>'
    )
    return head(
        440,
        "V · Cadence — 37 route handlers, one function, and a wall with one door",
        "V · Cadence — the whole API drawn as one part: 37 route handlers "
        "enter one serverless function, and its single output passes through "
        "the one door in a wall — row-level security, FORCEd — before "
        "reaching the 7 tables behind it. The against-self line: every one of "
        "the six services carries a conditional owner guard; a caller that "
        "forgets the identity still sends the query, and the database's "
        "refusal is the one that cannot be forgotten.",
        key="plate-5-cadence.svg",
        col=(148, 880), frame=CADENCE_FRAME,
    ) + css_close() + body + "</svg>"


# ══════════════════════════════════════════════════ VI · applied
#
# The part that ships and the part that doesn't, on one plate. The rules
# layer grades a strip of 96 ticks — two of them rust, the two it called
# wrong — and below it the cascade is drawn in the board's absence
# vocabulary: a dashed outline, its lead ending in an open circle, because
# its 0.9583 has no surviving artifact. The wrong ticks are placed by hand;
# their COUNT is the claim, their positions are not.
def plate_applied() -> str:
    def row(y0: int, wrong: int) -> str:
        ticks = " ".join(f"M{462 + i * 6.4:.1f},{y0} V{y0 + 24}"
                         for i in range(48) if i != wrong)
        wx = 462 + wrong * 6.4
        return (f'<path fill="none" stroke="{T["verd"]}" stroke-width="2" d="{ticks}"/>'
                f'<path fill="none" stroke="{T["rust"]}" stroke-width="2" '
                f'd="M{wx:.1f},{y0 - 3} V{y0 + 27}"/>')
    body = (
        bus("verd", "M63,0 V430", C=200, cd="M63,2.5 V427.5")
        + bus("rust", "M90,0 V430", C=45, cd="M90,2.5 V427.5")
        + bus("zinc", "M117,0 V430", C=130, cd="M117,2.5 V427.5")
        + bus("verd", "M63,120 H150", C=88, cd="M67,120 H145")
        + bus("verd", "M198,120 H240", C=140, cd="M202,120 H236")
        + f'<rect x="240" y="99" width="160" height="42" rx="8" fill="none" '
          f'stroke="{T["verd"]}" stroke-width="1.6"/>'
        + lbl(252, 124, "THE RULES LAYER", cls="ts", size=11.5, ls=1.3)
        + bus("verd", "M400,120 H452", C=20, cd="M404,120 H448")
        + f'<rect x="452" y="88" width="324" height="80" rx="6" fill="none" '
          f'stroke="{T["zinc"]}" stroke-width="1.3"/>'
        + row(100, 16) + row(132, 40)
        + lbl(452, 80, "96 LABELLED MESSAGES · 2 CALLED WRONG", size=10, ls=1.1)
        # the cascade, in the board's absence vocabulary: dashed, lead open
        + f'<path fill="none" stroke="{T["verd"]}" stroke-width="1.4" d="M320,141 V196"/>'
        + f'<circle cx="320" cy="202.5" r="3.5" fill="none" stroke="{T["verd"]}" stroke-width="2"/>'
        + f'<rect x="240" y="220" width="160" height="42" rx="8" fill="none" '
          f'stroke="{T["zinc"]}" stroke-width="1.4" stroke-dasharray="5 4"/>'
        + lbl(252, 245, "THE CASCADE", cls="ts dim", size=10, ls=1.1)
        + lbl(240, 286, "LAYER TWO — NO EVALUATION ARTIFACT SURVIVES", size=10, ls=1.1)
        + mark("applied", 150, 96, 48)
        + f'<text x="150" y="54" class="d" font-size="30" letter-spacing="0.5">VI — APPLIED</text>'
        + f'<text x="150" y="76" class="dim" font-size="14.5">an inbox read by rules that keep score.</text>'
        + f'<text x="560" y="240" class="d" font-size="62">0.979</text>'
        + f'<text x="560" y="278" class="dim" font-size="13">macro-F1 — the rules layer alone,</text>'
        + f'<text x="560" y="296" class="dim" font-size="13">graded on the strip above.</text>'
        + f'<rect x="150" y="362" width="4" height="16" fill="{T["verd"]}"/>'
        + f'<text x="164" y="375" class="mid" font-size="14">the full cascade scored 0.9583 — and the artifact is gone; the run was overwritten.</text>'
        + f'<text x="164" y="395" class="dim" font-size="13">what is deployed runs only that first layer.</text>'
    )
    return head(
        430,
        "VI · Applied — 0.979 macro-F1, rules layer alone; the cascade has no artifact",
        "VI · Applied — the mail triage drawn as the part that ships: the "
        "rules layer grades a labelled strip of 96 messages and gets 2 wrong "
        "— 0.979 macro-F1, rules layer alone. Below it, drawn dashed with "
        "its lead left open, is the cascade: layer two, whose 0.9583 has no "
        "evaluation artifact — the run was overwritten. What is deployed "
        "runs only that first layer.",
        key="plate-6-applied.svg",
        col=(148, 880), frame=APPLIED_FRAME,
    ) + css_close() + body + "</svg>"


# ══════════════════════════════════════════════════ VII · visualassist
#
# The alert policy drawn to scale from the phone in the reader's hand:
# three arcs at 0.5 / 1.0 / 2.0 m along a measured ruler, their styles
# keyed to a swatch legend — solid rust interrupts, dashed rust pulses,
# zinc stays silent, the mark's own encoding at board scale. The behaviour
# words live in the legend rather than on the arcs because a label laid
# across a curve reads as ink through type at exactly the radii that
# matter. Below: the settings slider the app actually shows, drawn with
# its lead severed — an open circle short of LIDARSERVICE — which is the
# section's admission made geometry. The plate taps no page bus: like the
# hero says, no URL. Its only current runs mark-to-phone.
def plate_visualassist() -> str:
    body = (
        bus("verd", "M63,0 V524", C=60, cd="M63,2.5 V521.5")
        + bus("rust", "M90,0 V524", C=145, cd="M90,2.5 V521.5")
        + bus("zinc", "M117,0 V524", C=205, cd="M117,2.5 V521.5")
        # the open stub: reaching for the zinc bus, not landing
        + f'<path class="bus" stroke="{T["zinc"]}" stroke-dasharray="3 6" d="M132,120 H146"/>'
        + f'<circle cx="125.5" cy="120" r="3.5" fill="none" stroke="{T["zinc"]}" stroke-width="2"/>'
        # the one live current: mark to phone
        + bus("rust", "M198,120 H226 V213 H252", C=100, cd="M202,120 H226 V213 H247")
        + f'<g><rect x="252" y="198" width="18" height="30" rx="4" fill="{TILE}" '
          f'stroke="{T["edge"]}" stroke-width="1.2"/>'
          f'<circle cx="261" cy="206" r="1.5" fill="#F7F8F8"/></g>'
        # the policy, to scale: 120u per metre along a measured ruler
        + f'<path fill="none" stroke="{T["zinc"]}" stroke-width="1.4" '
          f'd="M272,213 H524 M332,209 V217 M392,209 V217 M512,209 V217"/>'
        + f'<path fill="none" stroke="{T["rust"]}" stroke-width="2" d="M324,183 A60,60 0 0 1 324,243"/>'
        + f'<path fill="none" stroke="{T["rust"]}" stroke-width="2" stroke-dasharray="4.5 4.8" '
          f'd="M375.9,153 A120,120 0 0 1 375.9,273"/>'
        + f'<path fill="none" stroke="{T["zinc"]}" stroke-width="2" d="M479.8,93 A240,240 0 0 1 479.8,333"/>'
        # the legend, keyed by the arcs' own strokes
        + f'<path fill="none" stroke="{T["rust"]}" stroke-width="2" d="M522,176 H534"/>'
        + lbl(540, 180, "0.5 M — INTERRUPT", cls="ts", size=11, ls=1.3)
        + f'<path fill="none" stroke="{T["rust"]}" stroke-width="2" stroke-dasharray="4.5 4.8" d="M522,201 H534"/>'
        + lbl(540, 205, "1.0 M — PULSE", cls="ts", size=11, ls=1.3)
        + f'<path fill="none" stroke="{T["zinc"]}" stroke-width="2" d="M522,226 H534"/>'
        + lbl(540, 230, "2.0 M — STAY SILENT", cls="ts", size=11, ls=1.3)
        # the settings slider, lead severed before the service that ignores it
        + lbl(150, 372, "SETTINGS · ALERT DISTANCE — METRES, READ ALOUD", size=10, ls=1.1)
        + f'<path fill="none" stroke="{T["zinc"]}" stroke-width="2" '
          f'd="M150,398 H458 M211.6,392 V404 M273.2,392 V404 M396.4,392 V404"/>'
        + f'<circle cx="273.2" cy="398" r="7" fill="{T["rust"]}"/>'
        + lbl(211.6, 422, "0.5", cls="dim", size=10, ls=0.5, anchor="middle")
        + lbl(273.2, 422, "1.0", cls="dim", size=10, ls=0.5, anchor="middle")
        + lbl(396.4, 422, "2.0", cls="dim", size=10, ls=0.5, anchor="middle")
        + f'<path fill="none" stroke="{T["rust"]}" stroke-width="1.4" d="M273.2,405 V436 H544"/>'
        + f'<circle cx="551" cy="436" r="3.5" fill="none" stroke="{T["rust"]}" stroke-width="2"/>'
        + f'<rect x="590" y="415" width="160" height="42" rx="8" fill="none" '
          f'stroke="{T["rust"]}" stroke-width="1.6"/>'
        + lbl(602, 440, "LIDARSERVICE", cls="ts", size=11.5, ls=1.3)
        + f'<text x="150" y="54" class="d" font-size="30" letter-spacing="0.5">VII — VISUALASSIST</text>'
        + f'<text x="150" y="76" class="dim" font-size="14.5">it decides by distance when to speak — and when not to.</text>'
        + mark("visualassist", 150, 96, 48)
        + f'<rect x="150" y="470" width="4" height="16" fill="{T["rust"]}"/>'
        + f'<text x="164" y="483" class="dim" font-size="13">a slider labelled in metres, its value read aloud — bound to a threshold LiDARService never consults.</text>'
        + f'<text x="164" y="505" font-size="14.5">a live control that does nothing lies to the person the app is for.</text>'
    )
    return head(
        524,
        "VII · VisualAssist — 0.5 / 1.0 / 2.0 m: interrupt, pulse, stay silent; the slider is bound to nothing",
        "VII · VisualAssist — the alert policy drawn to scale from the phone "
        "in your hand: interrupt inside 0.5 m, pulse at 1.0, stay silent "
        "past 2.0. Below it, the settings slider the app actually shows — "
        "labelled in metres, its value read aloud — drawn with its lead "
        "ending open before LiDARService, the threshold it never consults. "
        "A live control that does nothing lies to the person the app is "
        "for.",
        key="plate-7-visualassist.svg",
        col=(148, 880), frame=VA_FRAME,
    ) + css_close() + body + "</svg>"


# ══════════════════════════════════════════════════ the colophon
#
# The board's edge. The three buses land on their pads and leave the page —
# an edge connector, because the page plugs into CI, not a footer. The one
# line of silkscreen is DERIVED, not asserted: the claim count is read out
# of build/claims.json in this very build, so the page's warrant for itself
# ("N claims, each a command") is true by construction and cannot drift
# from the file that makes it true. No derivation date is printed: the
# honest date lives in CI's own logs, and a baked one would be stale by
# the first morning.
CLAIMS_N = len(json.loads((ROOT / "claims.json").read_text())["claims"])


def plate_colophon() -> str:
    body = (
        bus("verd", "M63,0 V140", C=150, cd="M63,2.5 V136")
        + bus("rust", "M90,0 V140", C=30, cd="M90,2.5 V136")
        + bus("zinc", "M117,0 V140", C=100, cd="M117,2.5 V136")
        + f'<rect x="58" y="140" width="10" height="22" fill="{T["verd"]}"/>'
        + f'<rect x="85" y="140" width="10" height="22" fill="{T["rust"]}"/>'
        + f'<rect x="112" y="140" width="10" height="22" fill="{T["zinc"]}"/>'
        + f'<path class="bus" stroke="{T["zinc"]}" d="M48,166 L56,166 M48,166 L44,160 M852,166 L844,166 M852,166 L856,160 M56,166 H844"/>'
        + lbl(852, 120, f"{CLAIMS_N} CLAIMS · {CLAIMS_N} COMMANDS · RE-RUN IN CI FROM PINNED COMMITS",
              cls="ts mid", size=10.5, anchor="end")
        + lbl(852, 140, "what is my word rather than a derivation says so where it stands",
              cls="dim", size=10, ls=0.2, anchor="end")
    )
    return head(
        170,
        "colophon — the board's edge; every claim is a command",
        f"Colophon — the board's edge connector: the three buses land on "
        f"their pads and leave the page. {CLAIMS_N} claims, {CLAIMS_N} "
        f"commands, re-run in CI from pinned commits; what is my word "
        f"rather than a derivation says so where it stands.",
        key="plate-colophon.svg",
        col=(44, 886), frame=COLO_FRAME,
        faces="T6",
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


# ══════════════════════════════════════════════════ the mobile sections
#
# One 440u twin per published surface — a REDESIGN for the width, not the
# desktop composition shrunk. On a phone the desktop plate would render at
# ~0.43 and its 13px captions at 5.6px; the client's rule is that nothing is
# downscaled, so every section is recomposed: the same vocabulary (three
# buses, a tap, the mark, the diagram, the claim figure, the accent-barred
# admission) rotated into one column. Every sentence is reflowed against
# MEASURED widths (scratchpad/measure.mjs, 2026-08-12) — the 440 canvas is
# where "about right" line lengths go to overrun.
#   * THE BUSES SURVIVE WHOLE. All three run every plate at MBUS_X, same
#     speeds, same comets, phases varied per plate — the phone page is the
#     same board, not a reduced print of it. 28u of bus corridor on a 440
#     canvas is the desktop's own proportion (54/900).
#   * content column: x 92..~404 (the 8u doctrine clearance off the zinc
#     comet at 69, in the direction platform advance-skew cannot close,
#     because left-anchored text grows rightward).
#   * type: titles Syne 24 (the phone hero's name is 30 and stays the
#     largest voice), figures 44, text 13/12, silkscreen 10-11.5. Rendered
#     at the phone column's ~0.89 these sit near desktop's own rendered
#     sizes — larger, not smaller, than the desktop plate would give a
#     phone reader.
#   * the FOUR LINK CHIPS have no mobile twin BY DESIGN: a chip is a
#     fixed-px component (natural size, no <picture> possible inside a
#     link — see the link-row doctrine above), so at 440 the row wraps to
#     two rows of ports and every chip keeps its size. m-link-return
#     resumes the lanes below the wrapped row.
def m_sec(h: int, C: tuple[float, float, float],
          tap: tuple[str, float] | None = None) -> str:
    """The three page buses crossing a mobile plate, plus the section's tap.
    The tap runs bus -> tile edge at y=120, crossing its sibling buses the
    way every desktop tap does: hairline over hairline is board routing."""
    out = (bus("verd", f"M40,0 V{h}", C=C[0], cd=f"M40,2.5 V{h - 2.5}")
           + bus("rust", f"M54,0 V{h}", C=C[1], cd=f"M54,2.5 V{h - 2.5}")
           + bus("zinc", f"M68,0 V{h}", C=C[2], cd=f"M68,2.5 V{h - 2.5}"))
    if tap:
        bk, tc = tap
        out += bus(bk, f"M{MBUS_X[bk]},120 H92.5", C=tc,
                   cd=f"M{MBUS_X[bk] + 4},120 H88")
    return out


def m_fig(fig: str, c1: str, c2: str) -> str:
    """The claim figure block, right of the mark: Syne 44 over two measured
    12px caption lines. 172 leaves 12u to the x=160 feeder spine the denser
    plates run — above the 8u floor, in the safe direction (see above).
    Caption leading is set by Syne's em box, not its ink: the 44px figure's
    box reaches ~13u below the baseline, so the first caption sits 32 down.
    Mobile prose never uses &#8217; — the entity's own digits would enter
    the drawn ⊆ description check — the literal ’ is in TEXT_CHARS."""
    return (f'<text x="172" y="140" class="d" font-size="44">{fig}</text>'
            f'<text x="172" y="172" class="dim" font-size="12">{c1}</text>'
            f'<text x="172" y="189" class="dim" font-size="12">{c2}</text>')


def m_adm(y: float, accent: str, mids: list[str], dims: list[str]) -> str:
    """The against-self admission, reflowed for 306u of measure."""
    out = f'<rect x="92" y="{y:g}" width="4" height="16" fill="{T[accent]}"/>'
    b = y + 13
    for s in mids:
        out += f'<text x="106" y="{b:g}" class="mid" font-size="13">{s}</text>'
        b += 19
    b += 1
    for s in dims:
        out += f'<text x="106" y="{b:g}" class="dim" font-size="12">{s}</text>'
        b += 17
    return out


# ── I · work, phone cut. The footprint keeps its desktop reading whole:
# tap to the pad and no further, the slot empty. The eyebrow loses only
# "FIRST," — at 10.5 the full line's start would land 4u off the zinc comet
# once Linux's +4% advance grows an end-anchored label leftward.
def m_work() -> str:
    body = (
        m_sec(380, (95, 10, 160))
        + bus("zinc", "M68,120 H90.5", C=48, cd="M72,120 H86")
        + f'<g><rect x="92.75" y="96.75" width="46.5" height="46.5" rx="12" '
          f'fill="none" stroke="{T["zinc"]}" stroke-width="1.4" stroke-dasharray="5 4"/>'
          f'<rect x="90.25" y="118" width="5" height="4" fill="{T["zinc"]}"/></g>'
        + lbl(92, 163, "NO PRODUCT MARK — THE WORK IS OFF-REPO", size=10, ls=1.1)
        + f'<text x="92" y="54" class="d" font-size="24" letter-spacing="0.5">I — WORK</text>'
        + f'<text x="92" y="74" class="dim" font-size="13">twelve months of production data work —</text>'
        + f'<text x="92" y="90" class="dim" font-size="13">none of it public.</text>'
        + lbl(404, 30, "THE EXCEPTION — ATTESTED, NOT DERIVED", size=10.5, anchor="end")
        + f'<text x="92" y="224" class="d" font-size="44">57.8M</text>'
        + f'<text x="92" y="256" class="dim" font-size="12">rows in one field-usage table,</text>'
        + f'<text x="92" y="273" class="dim" font-size="12">from 1.6M Oracle Analytics query logs.</text>'
        + m_adm(300, "zinc",
                ["none of these numbers can be re-derived by you."],
                ["the data belongs to Miami University",
                 "and to a competition — this section is my word."])
    )
    return head(
        380,
        "I · Work — the empty footprint, phone cut",
        "I · Work, phone cut — the empty footprint: the slot for a component "
        "the board expects but does not fit, because the year of paid work is "
        "off-repo. A 57.8M-row field-usage table, distilled from 1.6M Oracle "
        "Analytics query logs at Miami University. None of it can be "
        "re-derived by a reader — the data belongs to Miami University and to "
        "a competition; this section is attested, not derived.",
        key="m-1-work.svg",
        col=(88, 412), frame=(2.5, 36, 2.5), w=440,
    ) + css_close() + body + "</svg>"


# ── II · jetpack, phone cut. The fan turns vertical: spine down from the
# mark, four deflate blocks stacked (unlabelled — four frames ARE the count,
# and four repeated captions at 440u are noise), collector down the right
# edge, and the gzip member back at the content margin. The block digits are
# deliberately not drawn: the mobile gate direction is drawn ⊆ description,
# and numbering the blocks would oblige the desc to recite 0 1 2 3.
def m_jetpack() -> str:
    lanes = ""
    for y, C in zip((246, 284, 322, 360), (0, 64, 128, 176)):
        lanes += (bus("rust", f"M160,{y} H196", C=C, cd=f"M164,{y} H192")
                  + f'<rect x="196" y="{y - 13}" width="140" height="26" rx="6" '
                  + f'fill="none" stroke="{T["zinc"]}" stroke-width="1.3"/>'
                  + bus("rust", f"M336,{y} H372", C=C + 30, cd=f"M340,{y} H368"))
    body = (
        m_sec(600, (140, 55, 190), tap=("rust", 18))
        + mark("jetpack", 92, 96, 48)
        + f'<text x="92" y="54" class="d" font-size="24" letter-spacing="0.5">II — JETPACK</text>'
        + f'<text x="92" y="76" class="dim" font-size="13">is hand-vectorised code actually faster?</text>'
        + m_fig("6.4×", "422 vs 66.2 MB/s, single thread",
                "M1 Pro · 3-fork JMH, committed")
        + bus("rust", "M140,120 H160 V360", C=70, cd="M144,120 H160 V357")
        + lanes
        + lbl(196, 208, "DEFLATE · JDK 25", size=10, ls=1.1)
        + lbl(196, 224, "VIRTUAL THREADS", size=10, ls=1.1)
        + bus("rust", "M372,246 V445 H252", C=100, cd="M372,248.5 V445 H256.5")
        + f'<rect x="92" y="424" width="160" height="42" rx="8" fill="none" '
          f'stroke="{T["rust"]}" stroke-width="1.6"/>'
        + lbl(104, 449, "ONE GZIP MEMBER", cls="ts", size=11.5, ls=1.3)
        + lbl(92, 484, "STITCHED BYTE-ALIGNED · ONE CRC", size=10, ls=1.1)
        + m_adm(506, "rust",
                ["the JDK’s own Adler-32 intrinsic",
                 "does 14.06 GB/s — not beaten."],
                ["mine reaches 4.26 GB/s hand-vectorised,",
                 "bit-identical to java.util.zip."])
    )
    return head(
        600,
        "II · jetpack — the SIMD fan, phone cut: 6.4× over one thread",
        "II · jetpack, phone cut — parallel gzip on JDK 25: the SIMD bus fans "
        "into four deflate blocks collected back to one gzip member, stitched "
        "byte-aligned under one CRC. 422 against 66.2 MB per second "
        "single-threaded — 6.4 times, on an M1 Pro, from a committed 3-fork "
        "JMH run. The against-self result is printed: the JDK's own Adler-32 "
        "intrinsic does 14.06 GB per second and is not beaten; the "
        "hand-vectorised checksum reaches 4.26, bit-identical to "
        "java.util.zip.",
        key="m-2-jetpack.svg",
        col=(88, 412), frame=(2.5, 67, 2.5), w=440,
    ) + css_close() + body + "</svg>"


# ── III · glyph, phone cut. The bundles keep their one load-bearing ratio —
# 2/4/8 rules for 128/256/512-bit registers — stacked down the column, the
# collector gathering them into the benchmark chip and the chip dropping to
# the package that ships. The admission still runs longest: this section
# owes the same two sentences at every width.
def m_glyph() -> str:
    lanes = ""
    for label, n, yc in (("NEON", 2, 240), ("AVX2", 4, 300), ("AVX-512", 8, 368)):
        y0 = yc - 3 * (n - 1)
        rules = " ".join(f"M200,{y0 + i * 6} H320" for i in range(n))
        lanes += (lbl(200, y0 - 10, label, size=10, ls=1.2)
                  + f'<path fill="none" stroke="{T["zinc"]}" stroke-width="1.4" d="{rules}"/>')
    body = (
        m_sec(690, (40, 130, 8), tap=("rust", 88))
        + mark("glyph", 92, 96, 48)
        + f'<text x="92" y="54" class="d" font-size="24" letter-spacing="0.5">III — GLYPH</text>'
        + f'<text x="92" y="76" class="dim" font-size="13">SIMD kernels over a net the course provided.</text>'
        + m_fig("3.5×", "benchDot/256 — course baseline,",
                "reference machine, committed run.")
        + bus("rust", "M140,120 H160 V368", C=30, cd="M144,120 H160 V365")
        + f'<circle cx="160" cy="240" r="2.6" fill="{T["rust"]}"/>'
        + f'<circle cx="160" cy="300" r="2.6" fill="{T["rust"]}"/>'
        + bus("rust", "M160,240 H200", C=60, cd="M162.5,240 H197")
        + bus("rust", "M160,300 H200", C=115, cd="M162.5,300 H197")
        + bus("rust", "M160,368 H200", C=170, cd="M162.5,368 H197")
        + lanes
        + f'<path class="bus" stroke="{T["rust"]}" d="M320,240 H344 V368 H320 M320,300 H344"/>'
        + bus("rust", "M344,368 V404", C=142, cd="M322,240 H344 V400")
        + f'<rect x="200" y="404" width="160" height="36" rx="8" fill="none" '
          f'stroke="{T["rust"]}" stroke-width="1.6"/>'
        + lbl(212, 426, "BENCHDOT/256", cls="ts", size=11.5, ls=1.3)
        + bus("rust", "M280,440 V464", C=55, cd="M280,442.5 V459.5")
        + f'<rect x="200" y="464" width="196" height="36" rx="8" fill="none" '
          f'stroke="{T["zinc"]}" stroke-width="1.6"/>'
        + lbl(212, 486, "WASM_SIMD128 · 43,751 B", cls="ts", size=11.5, ls=1.3)
        + lbl(200, 522, "BYTE-IDENTICAL TO MAIN", size=10, ls=1.1)
        + lbl(200, 537, "CHECKED DAILY IN CI", size=10, ls=1.1)
        + m_adm(556, "rust",
                ["the same flags run 10.7× slower on",
                 "benchAxpy/128 — below the size floor,"],
                ["where threading costs more than it pays.",
                 "and 97.01% is a training-time number:",
                 "the test set that graded the net",
                 "also picked its checkpoint."])
    )
    return head(
        690,
        "III · Glyph — register lanes to one benchmark, phone cut",
        "III · Glyph, phone cut — SIMD kernels over a course-provided MNIST "
        "net: three register-lane bundles — NEON, AVX2, AVX-512 — converge on "
        "benchDot/256, 3.5× over the course baseline on the reference "
        "machine, and drop to the package that ships: WASM_SIMD128, 43,751 "
        "bytes, byte-identical to main, checked daily in CI. The against-self "
        "results are printed: the same flags run 10.7× slower on "
        "benchAxpy/128, below the size floor, and 97.01% is a training-time "
        "number — the test set that graded the net also picked its "
        "checkpoint.",
        key="m-3-glyph.svg",
        col=(88, 412), frame=(2.5, 43, 2.5), w=440,
    ) + css_close() + body + "</svg>"


# ── IV · automl, phone cut. The registry keeps its one un-negotiable
# property: 44 pins in ONE strip, emitted by loop so the count stays true by
# construction. The pitch tightens to 5.9u — a denser comb, not a shorter
# one — because splitting the strip would redraw "one part, 44 pins" as two
# parts. Seven set-taps below, exactly as wide as the strip they tap.
def m_automl() -> str:
    pins = " ".join(f"M{140 + i * (392 - 140) / 43:.1f},222 V242" for i in range(44))
    drops = " ".join(f"M{152 + i * 40},258 V294" for i in range(7))
    sets = "".join(f'<circle cx="{152 + i * 40}" cy="300" r="5" fill="none" '
                   f'stroke="{T["zinc"]}" stroke-width="2"/>' for i in range(7))
    body = (
        m_sec(490, (170, 85, 25), tap=("zinc", 55))
        + mark("automl", 92, 96, 48)
        + f'<text x="92" y="54" class="d" font-size="24" letter-spacing="0.5">IV — AUTOML</text>'
        + f'<text x="92" y="76" class="dim" font-size="13">a LangGraph agent, dealt its tools phase by phase.</text>'
        + m_fig("44", "defined across the dispatcher;",
                "no phase’s hand holds them all.")
        + bus("zinc", "M116,144 V236 H128", C=96, cd="M116,148 V236 H124")
        + lbl(128, 206, "THE REGISTRY · 44 TOOLS DEFINED", size=10, ls=1.1)
        + f'<rect x="128" y="214" width="276" height="44" rx="4" fill="none" '
          f'stroke="{T["zinc"]}" stroke-width="1.3"/>'
        + f'<path fill="none" stroke="{T["zinc"]}" stroke-width="2" d="{pins}"/>'
        + f'<path fill="none" stroke="{T["zinc"]}" stroke-width="1.4" d="{drops}"/>'
        + sets
        + lbl(92, 334, "SEVEN TOOL SETS — NO PHASE IS HANDED ALL 44", size=10, ls=1.1)
        + m_adm(376, "zinc",
                ["the sandbox guards against accidents,",
                 "not adversaries."],
                ["the network is an env var — the beta template",
                 "renders it bridge; no cap-drop, no pids-limit,",
                 "no seccomp."])
    )
    return head(
        490,
        "IV · AutoML — the 44-pin registry, phone cut",
        "IV · AutoML, phone cut — the dispatcher as its registry: a 44-pin "
        "strip, one pin per tool the graph defines, seven tool-set taps below "
        "it — no phase is handed all 44. The against-self line is the "
        "sandbox: it guards against accidents, not adversaries — the network "
        "is an env var the beta template renders as bridge, with no cap-drop, "
        "no pids-limit, no seccomp.",
        key="m-4-automl.svg",
        col=(88, 412), frame=(2.5, 35, 2.5), w=440,
    ) + css_close() + body + "</svg>"


# ── V · cadence, phone cut. The wall rotates with the flow: 37 stubs rain
# off a rail into the function's top edge, and the single output crosses a
# HORIZONTAL doored wall before the 7 tables. One comet runs entry to last
# table — the door is the only way through, and the drawing has exactly one
# current to prove it with.
def m_cadence() -> str:
    stubs = " ".join(f"M{124 + i * 264 / 36:.1f},202 V216" for i in range(37))
    fan = " ".join(f"M248,{y} H264" for y in range(350, 495, 24))
    tables = "".join(f'<rect x="264" y="{y - 8}" width="132" height="16" rx="3" '
                     f'fill="none" stroke="{T["zinc"]}" stroke-width="1.3"/>'
                     for y in range(350, 495, 24))
    body = (
        m_sec(640, (12, 175, 90), tap=("verd", 30))
        + mark("cadence", 92, 96, 48)
        + f'<text x="92" y="54" class="d" font-size="24" letter-spacing="0.5">V — CADENCE</text>'
        + f'<text x="92" y="76" class="dim" font-size="13">every route into one function; every row behind RLS.</text>'
        + m_fig("37", "route handlers, one function;",
                "RLS FORCEd on all 7 tables.")
        + bus("verd", "M116,144 V202 H388", C=132, cd="M116,148 V202 H384")
        + f'<path fill="none" stroke="{T["verd"]}" stroke-width="1.4" d="{stubs}"/>'
        + f'<rect x="100" y="216" width="296" height="60" rx="8" fill="none" '
          f'stroke="{T["verd"]}" stroke-width="1.6"/>'
        + lbl(112, 242, "ONE SERVERLESS FUNCTION", cls="ts", size=11.5, ls=1.3)
        + lbl(112, 260, "37 ROUTE HANDLERS", cls="ts dim", size=10, ls=1.1)
        # the wall, doored only where the output passes
        + f'<path class="bus" stroke="{T["verd"]}" d="M100,326 H236 M260,326 H396"/>'
        + f'<path class="bus" stroke="{T["verd"]}" d="M100,332 H236 M260,332 H396"/>'
        + lbl(100, 316, "RLS · FORCED", size=10.5)
        + bus("verd", "M248,276 V494", C=190, cd="M248,278.5 V490")
        + f'<path fill="none" stroke="{T["verd"]}" stroke-width="1.4" d="{fan}"/>'
        + tables
        + m_adm(524, "verd",
                ["every one of the six services",
                 "carries a conditional owner guard."],
                ["a caller that forgets the identity",
                 "still sends the query; the database’s",
                 "refusal cannot be forgotten."])
    )
    return head(
        640,
        "V · Cadence — one function, one door, phone cut",
        "V · Cadence, phone cut — 37 route handlers rain into one serverless "
        "function, and its single output passes through the one door in a "
        "wall — row-level security, FORCEd — before reaching the 7 tables "
        "behind it. The against-self line: every one of the six services "
        "carries a conditional owner guard; a caller that forgets the identity "
        "still sends the query, and the database's refusal is the one that "
        "cannot be forgotten.",
        key="m-5-cadence.svg",
        col=(88, 412), frame=(2.5, 43, 2.5), w=440,
    ) + css_close() + body + "</svg>"


# ── VI · applied, phone cut. The graded strip reflows 96 = 3×32 (the row
# split is layout, the 96 and the 2 are the claims); the cascade keeps the
# absence vocabulary — dashed outline, open lead — directly under the rules
# layer it never shipped behind. The caption says "the strip below" because
# here it IS below: each description is true of its own plate.
def m_applied() -> str:
    def row(y0: int, wrong: int | None) -> str:
        xs = [104 + i * 280 / 31 for i in range(32)]
        ticks = " ".join(f"M{x:.1f},{y0} V{y0 + 24}"
                         for i, x in enumerate(xs) if i != wrong)
        out = f'<path fill="none" stroke="{T["verd"]}" stroke-width="2" d="{ticks}"/>'
        if wrong is not None:
            out += (f'<path fill="none" stroke="{T["rust"]}" stroke-width="2" '
                    f'd="M{xs[wrong]:.1f},{y0 - 3} V{y0 + 27}"/>')
        return out
    body = (
        m_sec(610, (200, 45, 130), tap=("verd", 88))
        + mark("applied", 92, 96, 48)
        + f'<text x="92" y="54" class="d" font-size="24" letter-spacing="0.5">VI — APPLIED</text>'
        + f'<text x="92" y="76" class="dim" font-size="13">an inbox read by rules that keep score.</text>'
        + m_fig("0.979", "macro-F1 — the rules layer alone,",
                "graded on the strip below.")
        + bus("verd", "M116,144 V206", C=140, cd="M116,148 V202")
        + f'<rect x="92" y="206" width="160" height="42" rx="8" fill="none" '
          f'stroke="{T["verd"]}" stroke-width="1.6"/>'
        + lbl(104, 231, "THE RULES LAYER", cls="ts", size=11.5, ls=1.3)
        + bus("verd", "M252,227 H332 V380", C=20, cd="M256.5,227 H332 V376")
        # the cascade, in the board's absence vocabulary: dashed, lead open
        + f'<path fill="none" stroke="{T["verd"]}" stroke-width="1.4" d="M116,248 V264"/>'
        + f'<circle cx="116" cy="271" r="3.5" fill="none" stroke="{T["verd"]}" stroke-width="2"/>'
        + f'<rect x="92" y="284" width="140" height="42" rx="8" fill="none" '
          f'stroke="{T["zinc"]}" stroke-width="1.4" stroke-dasharray="5 4"/>'
        + lbl(104, 309, "THE CASCADE", cls="ts dim", size=10, ls=1.1)
        + lbl(92, 344, "LAYER TWO — NO EVALUATION", size=10, ls=1.1)
        + lbl(92, 360, "ARTIFACT SURVIVES", size=10, ls=1.1)
        + f'<rect x="92" y="380" width="304" height="102" rx="6" fill="none" '
          f'stroke="{T["zinc"]}" stroke-width="1.3"/>'
        + row(390, 21) + row(420, 8) + row(450, None)
        + lbl(92, 502, "96 LABELLED MESSAGES · 2 CALLED WRONG", size=10, ls=1.1)
        + m_adm(528, "verd",
                ["the full cascade scored 0.9583 — and",
                 "the artifact is gone; the run was overwritten."],
                ["what is deployed runs only that first layer."])
    )
    return head(
        610,
        "VI · Applied — the graded strip, phone cut",
        "VI · Applied, phone cut — the mail triage as the part that ships: "
        "the rules layer grades a labelled strip of 96 messages and gets 2 "
        "wrong — 0.979 macro-F1, rules layer alone. Below it, drawn dashed "
        "with its lead left open, is the cascade: layer two, whose 0.9583 has "
        "no evaluation artifact — the run was overwritten. What is deployed "
        "runs only that first layer.",
        key="m-6-applied.svg",
        col=(88, 412), frame=(2.5, 43, 2.5), w=440,
    ) + css_close() + body + "</svg>"


# ── VII · visualassist, phone cut. The policy stays TO SCALE — 100u per
# metre against desktop's 120 — with the arc chords rebuilt so each apex
# still lands on its ruler tick (chord x = tick − 0.134r, the 60° sagitta).
# The title is the one name Syne 800 cannot fit across 440 at any size worth
# reading, so it takes the hero's own two-line device. The legend moves
# below the arcs: at this width a label beside them would ride the 2 m
# chord. The slider keeps its severed lead, and keeps desktop's one licensed
# crossing — the dead 1.4u drop through the value it is set to.
def m_visualassist() -> str:
    body = (
        m_sec(650, (60, 145, 205))
        # the open stub: reaching for the zinc bus, not landing
        + f'<circle cx="76.5" cy="140" r="3.5" fill="none" stroke="{T["zinc"]}" stroke-width="2"/>'
        + f'<path class="bus" stroke="{T["zinc"]}" stroke-dasharray="3 6" d="M84,140 H90"/>'
        + f'<text x="92" y="44" class="d" font-size="24" letter-spacing="0.5">VII —'
          f'<tspan x="92" dy="26">VISUALASSIST</tspan></text>'
        + f'<text x="92" y="92" class="dim" font-size="13">it decides by distance when to speak —</text>'
        + f'<text x="92" y="108" class="dim" font-size="13">and when not to.</text>'
        + mark("visualassist", 92, 116, 48)
        # the one live current: mark to phone
        + bus("rust", "M140,140 H156 V210 H164", C=100, cd="M144,140 H156 V210 H159.5")
        + f'<g><rect x="164" y="195" width="18" height="30" rx="4" fill="{TILE}" '
          f'stroke="{T["edge"]}" stroke-width="1.2"/>'
          f'<circle cx="173" cy="203" r="1.5" fill="#F7F8F8"/></g>'
        # the policy, to scale: 100u per metre along a measured ruler
        + f'<path fill="none" stroke="{T["zinc"]}" stroke-width="1.4" '
          f'd="M184,210 H394 M234,206 V214 M284,206 V214 M384,206 V214"/>'
        + f'<path fill="none" stroke="{T["rust"]}" stroke-width="2" d="M227.3,185 A50,50 0 0 1 227.3,235"/>'
        + f'<path fill="none" stroke="{T["rust"]}" stroke-width="2" stroke-dasharray="4.5 4.8" '
          f'd="M270.6,160 A100,100 0 0 1 270.6,260"/>'
        + f'<path fill="none" stroke="{T["zinc"]}" stroke-width="2" d="M357.2,110 A200,200 0 0 1 357.2,310"/>'
        # the legend, keyed by the arcs' own strokes
        + f'<path fill="none" stroke="{T["rust"]}" stroke-width="2" d="M92,326 H104"/>'
        + lbl(110, 330, "0.5 M — INTERRUPT", cls="ts", size=11, ls=1.3)
        + f'<path fill="none" stroke="{T["rust"]}" stroke-width="2" stroke-dasharray="4.5 4.8" d="M92,348 H104"/>'
        + lbl(110, 352, "1.0 M — PULSE", cls="ts", size=11, ls=1.3)
        + f'<path fill="none" stroke="{T["zinc"]}" stroke-width="2" d="M92,370 H104"/>'
        + lbl(110, 374, "2.0 M — STAY SILENT", cls="ts", size=11, ls=1.3)
        # the settings slider, lead severed before the service that ignores it
        + lbl(92, 414, "SETTINGS · ALERT DISTANCE — METRES, READ ALOUD", size=10, ls=1.1)
        + f'<path fill="none" stroke="{T["zinc"]}" stroke-width="2" '
          f'd="M100,446 H400 M160,440 V452 M220,440 V452 M340,440 V452"/>'
        + f'<circle cx="220" cy="446" r="7" fill="{T["rust"]}"/>'
        + lbl(160, 470, "0.5", cls="dim", size=10, ls=0.5, anchor="middle")
        + lbl(220, 470, "1.0", cls="dim", size=10, ls=0.5, anchor="middle")
        + lbl(340, 470, "2.0", cls="dim", size=10, ls=0.5, anchor="middle")
        + f'<path fill="none" stroke="{T["rust"]}" stroke-width="1.4" d="M220,453 V499 H248"/>'
        + f'<circle cx="255" cy="499" r="3.5" fill="none" stroke="{T["rust"]}" stroke-width="2"/>'
        + f'<rect x="288" y="478" width="116" height="42" rx="8" fill="none" '
          f'stroke="{T["rust"]}" stroke-width="1.6"/>'
        + lbl(300, 503, "LIDARSERVICE", cls="ts", size=11.5, ls=1.3)
        + f'<rect x="92" y="548" width="4" height="16" fill="{T["rust"]}"/>'
        + f'<text x="106" y="561" class="dim" font-size="12">a slider labelled in metres, its value read aloud —</text>'
        + f'<text x="106" y="578" class="dim" font-size="12">bound to a threshold LiDARService never consults.</text>'
        + f'<text x="106" y="600" font-size="13">a live control that does nothing lies</text>'
        + f'<text x="106" y="619" font-size="13">to the person the app is for.</text>'
    )
    return head(
        650,
        "VII · VisualAssist — the alert policy to scale, phone cut",
        "VII · VisualAssist, phone cut — the alert policy to scale from the "
        "phone drawn on the plate: interrupt inside 0.5 m, pulse at 1.0, stay "
        "silent past 2.0. Below it, the settings slider the app actually "
        "shows — labelled in metres, its value read aloud — its lead drawn "
        "ending open before LiDARService, the threshold it never consults. A "
        "live control that does nothing lies to the person the app is for.",
        key="m-7-visualassist.svg",
        col=(88, 412), frame=(2.5, 35, 2.5), w=440,
    ) + css_close() + body + "</svg>"


# ── the return, phone cut. At 440 the chip row WRAPS — the chips are
# fixed-px components and keep their size, so the four drop columns the
# desktop return receives do not exist at any predictable x. The board does
# not pretend otherwise: the lanes RE-ENTER at pads (the colophon's edge
# vocabulary, inverted — a pad is where the board meets what is off-board),
# at MBUS_X, where the hero above the row handed them off.
def m_link_return() -> str:
    body = (
        "".join(f'<rect x="{x - 5}" y="0" width="10" height="22" fill="{T[k]}"/>'
                for k, x in MBUS_X.items())
        + bus("verd", "M40,22 V72", C=30, cd="M40,24.5 V69.5")
        + bus("rust", "M54,22 V72", C=150, cd="M54,24.5 V69.5")
        + bus("zinc", "M68,22 V72", C=100, cd="M68,24.5 V69.5")
        + lbl(404, 46, "THE EVIDENCE · SECTIONS II — VII", size=10.5, anchor="end")
    )
    return head(
        72,
        "the link ports rejoin the page bus — phone cut",
        "The link ports hand back to the page bus, phone cut: below the "
        "wrapped row of ports the three lanes re-enter the board at their "
        "pads and continue into the evidence, sections two to seven.",
        key="m-link-return.svg",
        col=(88, 412), frame=(0, 36, 0), w=440,
        faces="6",
    ) + css_close() + body + "</svg>"


# ── the colophon, phone cut. Same edge connector, same derived count —
# the two silkscreen lines reflow to four because 440 will not carry 55
# characters of 10.5px silkscreen past three bus lanes.
def m_colophon() -> str:
    body = (
        bus("verd", "M40,0 V100", C=150, cd="M40,2.5 V96")
        + bus("rust", "M54,0 V100", C=30, cd="M54,2.5 V96")
        + bus("zinc", "M68,0 V100", C=100, cd="M68,2.5 V96")
        + "".join(f'<rect x="{x - 5}" y="100" width="10" height="22" fill="{T[k]}"/>'
                  for k, x in MBUS_X.items())
        + f'<path class="bus" stroke="{T["zinc"]}" d="M32,126 L40,126 M32,126 L28,120 '
          f'M408,126 L400,126 M408,126 L412,120 M40,126 H400"/>'
        + lbl(404, 40, f"{CLAIMS_N} CLAIMS · {CLAIMS_N} COMMANDS",
              cls="ts mid", size=10.5, anchor="end")
        + lbl(404, 58, "RE-RUN IN CI FROM PINNED COMMITS",
              cls="ts mid", size=10.5, anchor="end")
        + lbl(404, 78, "what is my word rather than a derivation",
              cls="dim", size=10, ls=0.2, anchor="end")
        + lbl(404, 94, "says so where it stands",
              cls="dim", size=10, ls=0.2, anchor="end")
    )
    return head(
        150,
        "colophon — the board's edge, phone cut",
        f"Colophon, phone cut — the board's edge connector: the three buses "
        f"land on their pads and leave the page. {CLAIMS_N} claims, "
        f"{CLAIMS_N} commands, re-run in CI from pinned commits; what is my "
        f"word rather than a derivation says so where it stands.",
        key="m-colophon.svg",
        col=(28, 414), frame=(0, 27, 22), w=440,
        faces="T6",
    ) + css_close() + body + "</svg>"


# ── declared frames (top, rightGap, bottomGap), baked from gate.mjs
# measurement on this machine; tolerance 4 absorbs the CI ascent skew.
HERO_FRAME = (30, 37.7, 0)
JET_FRAME = (2.5, 55.9, 2.5)
WORK_FRAME = (2.5, 28, 2.5)
GLYPH_FRAME = (2.5, 35.5, 2.5)
AUTOML_FRAME = (2.5, 60.8, 2.5)
CADENCE_FRAME = (2.5, 51.7, 2.5)
APPLIED_FRAME = (2.5, 37, 2.5)
VA_FRAME = (2.5, 150, 2.5)
COLO_FRAME = (2.5, 48, 4)
MOB_FRAME = (36, 58, 0)
# The return plate's right edge is its one silkscreen line, which now ends
# 47.2u short of the canvas — 30 was authored against a longer string. Measured
# AFTER the dead faces came off, not before: check 12 normalises by a probe set
# in 'T' 400, so while that face was embedded the probe resolved to it and the
# same render measured 46.4. With only the 600 face on the plate the probe
# substitutes the weight it already has, and both checks read one ruler.
RET_FRAME = (0, 47.2, 0)
# The chips' frame is the MODULE, not the canvas: check 12 excludes the
# full-height through-lead by construction (a >=H-2 tall, <=5u wide element is
# the trace, not content), so first ink is the package's top edge at y=20 and
# the bottom margin is the 4u below it. The old 0,0.5,0 described the strip
# these chips replaced, where the lanes ran edge to edge.
CHIP_FRAME = {
    "portfolio": (20, 0.5, 4), "resume": (20, 0.5, 4),
    "linkedin": (20, 0.5, 4), "email": (20, 0.5, 4),
}

PLATES = {
    "plate-0-hero.svg": plate_hero,
    "plate-link-portfolio.svg": make_chip("portfolio"),
    "plate-link-resume.svg": make_chip("resume"),
    "plate-link-linkedin.svg": make_chip("linkedin"),
    "plate-link-email.svg": make_chip("email"),
    "plate-link-return.svg": plate_return,
    "plate-1-work.svg": plate_work,
    "plate-2-jetpack.svg": plate_jetpack,
    "plate-3-glyph.svg": plate_glyph,
    "plate-4-automl.svg": plate_automl,
    "plate-5-cadence.svg": plate_cadence,
    "plate-6-applied.svg": plate_applied,
    "plate-7-visualassist.svg": plate_visualassist,
    "plate-colophon.svg": plate_colophon,
}
MOBILE = {
    "m-0-hero.svg": m_hero,
    "m-1-work.svg": m_work,
    "m-2-jetpack.svg": m_jetpack,
    "m-3-glyph.svg": m_glyph,
    "m-4-automl.svg": m_automl,
    "m-5-cadence.svg": m_cadence,
    "m-6-applied.svg": m_applied,
    "m-7-visualassist.svg": m_visualassist,
    "m-link-return.svg": m_link_return,
    "m-colophon.svg": m_colophon,
}

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
        # The mobile twins are served as <source srcset> inside each section's
        # <picture>, and a <source> cannot carry an alt — the <img> in the same
        # picture is the desktop plate, checked below. A mobile description
        # still ships twice (the SVG's own <desc>/aria-label, and alt.json,
        # written from this same dict), so what README owes each mobile file
        # is SERVICE: a phone media query, in both themes. Asserted per file,
        # not assumed from the sweep — the sweep cannot see which media a
        # reference rides.
        if _fn.startswith("m-"):
            if not _re.search(rf'<source media="\(max-width: 500px\)" srcset="\./assets/{_re.escape(_fn)}"', _md):
                _fail.append(f"{_fn}: no <source media=\"(max-width: 500px)\"> serves it in README.md")
            if not _re.search(rf'<source[^>]*srcset="\./assets/light/{_re.escape(_fn)}"', _md):
                _fail.append(f"{_fn}: no <source> serves its light twin in README.md")
            continue
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
    # The four chips are ONE dark artwork in the README — GitHub's markdown
    # pipeline splits a <picture> inside a link (see the link-row doctrine),
    # so no theme switch is possible there and README rightly never serves
    # their light/ files. Those twins are still authored on purpose: gate.mjs
    # refuses a set with a missing twin, and the light file (same art,
    # data-canvas #ffffff) is exactly how the one artwork gets MEASURED on
    # the light canvas. A harness, not a served asset.
    _want -= {f"./assets/light/plate-link-{_k}.svg" for _k in CHIPS}
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
