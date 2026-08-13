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
# near the track so the pulse decays into the line — but each step must ALSO
# clear its neighbour by >24 summed |dRGB|, motion.mjs's changed-pixel
# threshold: a boundary under it does not exist to the gate or, by the
# gate's proxy, to the eye. Light rust shipped flat (29/22/20 internal
# edges, dE2000 3.8/3.0/2.9 — four short-rail plates read frozen) and was
# widened 2026-08-13 to 44/38/36 (dE 5.5/5.0/4.8, zinc's band; every step
# 9.0-14.0:1 on white), holding hue 13-15 deg with saturation rising to a
# fully-saturated head, the same shape dark rust already has (0.73->1.00).
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
              rust=("#571300", "#6F1F08", "#852A0D"),
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
    the frame stops changing for as long as it takes to cross. Every run on
    the page now clears the default segments; short runs buy their carrier
    with a SECOND train per pattern instead (_rail, _dbus), which keeps the
    ink duty cycle rather than rescaling the ramp.
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
    # ── .d ASKS FOR TABULAR LINING FIGURES, AND BOTH FEATURES ARE LOAD-BEARING.
    #
    # Syne's DEFAULT figures are old-style. 3 4 5 7 9 hang below the baseline,
    # 0 1 2 stop near x-height, and only 6 8 reach cap height, so "57.8M" drew
    # its 5 and 7 with their tops 9.5u below its 8 and its M at 56px — the
    # thing that was reported as "57 is placed a bit lower in height compared
    # to the rest". It was never a layout bug; nothing was misplaced. The page
    # was drawing text figures at display size.
    #
    # The order these are WRITTEN in is cosmetic — HarfBuzz applies lookups in
    # LookupList order, not in the order CSS names them — but the order they
    # APPLY in is the whole fix, so they are written in it. In Syne, 'lnum' is
    # lookup 26 (digit -> digit.lf) and 'tnum' is lookup 28, which carries TWO
    # mappings: digit -> digit.tosf, and digit.lf -> digit.tf. lnum runs first
    # and leaves no bare digit for tnum's first mapping to see, so the pair
    # lands on .tf, tabular lining.
    #
    # Asking for 'tnum' alone would land on .tosf — tabular OLDSTYLE. Uniform
    # widths, and the staggered heights entirely intact: the reported defect,
    # shipped, behind a change that looks like the fix and measures like it on
    # any width check. subset-fonts.py's assert_tabular_lining bounds the ink
    # top and the baseline for exactly that reason.
    #
    # Tabular, not merely lining, because these six figures head a column of
    # sections and are read down the page against each other. Uniform advances
    # cost nothing here — no figure on this page is set to a width — and they
    # are what makes the column agree with itself.
    #
    # Set on .d only. Commissioner was measured at BOTH the weights this page
    # ships, not just the one the captions use, and both are already lining:
    # the 400 spreads its digit ink tops 13/1000 em and its baselines 11/1000,
    # the 600 spreads them 14 and 12, with 1 2 4 7 sitting flat on the baseline
    # and the round figures overshooting it. That is drawing, not misalignment,
    # and it is the same order as the .tf set's 20. Neither weight carries
    # lnum, tnum, onum or pnum AT ALL, so there is nothing to ask Commissioner
    # for and nothing to fix — which also makes the lnum/pnum named in
    # subset-fonts.py's two Commissioner calls inert. They are left there: the
    # saving that comment claims comes from excluding fontTools' DEFAULT
    # feature set, which naming any list achieves, and dropping the two dead
    # tags would rewrite both text subsets and the base64 of every plate that
    # embeds them for no rendering change at all.
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{desc}" data-col="{col[0]},{col[1]}"{fr} data-canvas="{T['canvas']}">
<title>{title}</title><desc>{desc}</desc>
<style>
{fd}{ft}{f6}text{{font-family:'T',-apple-system,'Segoe UI',sans-serif;fill:{T['ink']}}}
.d{{font-family:'D',sans-serif;font-weight:800;font-feature-settings:'lnum' 1,'tnum' 1;fill:{T['ink']}}}
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


# ── optical alignment of the display line: the claim figures, and the romans.
#
# Every claim figure and its two caption lines are authored at the SAME x, and
# that is why they did not line up. A shared x makes the PEN ORIGINS identical;
# it says nothing about where the ink starts. Ink starts at the origin plus the
# glyph's own left side bearing, and Syne 800's figures are not tabular — their
# advances run 529..1158 and their side bearings 25..60 per 1000 em. At 62px a
# 60/1000 bearing is 3.7u of daylight the 13px caption underneath does not have,
# so the figure hangs back from its own caption. Measured in Chromium against
# the real embedded subset, every figure on this page sat 1.2..3.4u inside its
# captions — invisible to a gate, because the elements agreed on x exactly.
#
# Two terms, both measured off the rendered ink, neither taken from a table:
#
#   lsb   the face's own left side bearing, em/1000, read from the subset's
#         hmtx and confirmed against the Chromium raster to within 1/6 u. This
#         term is mechanical and scales with the type size.
#   over  the OPTICAL overshoot, authored units. A flat stem holds its leftmost
#         x for the glyph's whole height; a curve or a diagonal touches that x
#         at a single point and everything else falls back to the right, so the
#         two do not read level when they start level. Measured as how far the
#         apparent edge moves under a 1.5u isotropic low-pass of the real
#         raster, read at the half crossing — a construction in which a flat
#         stem's apparent edge IS its mechanical edge, and the flat 'I' of the
#         romans duly measures 0.17u, zero at the raster's resolution. The blur
#         is a fixed visual angle, so this term does not scale with type size,
#         and measurement agrees: the same glyph came out 0.33u at 62px and
#         0.50u at 44px. Capped at 2% of em — the overshoot Syne's own designer
#         allows a round, 'O' standing 20/1000 taller than 'H' at both ends.
#
# The edge being matched TO is the caption block's mean ink edge: TEXT_LSB, the
# mean over all 24 caption lines on the page (0.057 em; the spread across
# leading glyphs is 0.013..0.077 em, i.e. under 0.9u at caption size).
# Commissioner's own optical term at 12-13px is below 0.06u and is ignored.
#
# THE SECTION ROMANS are the same defect one size up, and they repeat seven
# times, which is why they are the visible one. `I — WORK` and `V — CADENCE`
# are authored at the same x as the subtitle under them and the mark tile
# beside them, and all three land somewhere different: measured at 8 device px
# per unit with every other element hidden, the roman's ink sat 1.66..2.46u
# right of its own tile, the subtitle 0.22..0.64u, and the I-plates and the
# V-plates disagreed with EACH OTHER by 0.67u apparent (2.0u mechanical) down
# the page. Three elements, one edge, seven sections, no two the same.
# ── THE FIGURE ROWS ARE THE TABULAR LINING GLYPHS' (2026-08-13).
#
# The five lsbs below are .tf's, off the subset's hmtx: 0 60->32, 4 50->20,
# 5 55->63, 6 30->29, 3 unmoved at 35. The old ones described .lf-less default
# figures this page no longer draws, and three of the five were wrong by more
# than a unit at 62px. Confirmed against the Chromium raster (30.2/34.3/18.1/
# 62.5/28.2 per 1000 em at 62px) so they are the shipped glyphs', not a table's.
#
# The optical term for the figures is now ONE number and it is the CAP, which
# is a simplification the arithmetic forces rather than a taste. fig_x passes
# cap_em=0.02, so what _ink() applies is min(over, 0.02*size) — at most 1.24u
# at 62, 1.12u at 56, 0.88u at 44. Both of the two independent estimators built
# to re-measure this put every .tf leading digit's apparent overshoot at or
# above its cap at every size on the page, so min() returns the cap and a
# per-digit `over` is arithmetic with no reader. FIG_OVER is written as the
# largest cap on the page for that reason: it is never the value applied.
#
# Neither estimator is offered as a measurement of the overshoot itself.
# Calibrated against the two values this file already depends on, both missed
# — 'V' reads 2.50-2.63u where the hand measurement says 1.49u — so the roman
# rows below are left exactly as they were and no digit inherits a number from
# an instrument that cannot reproduce a known answer.
#
# What makes the constant SAFE is not the estimate, it is that a constant
# cancels. The five mobile figures are authored at one x and are read down the
# page against each other; that agreement depends only on the differences
# between their lsbs (32/35/20/63/29, spread 43/1000 — so the table is still
# earning its keep). A shared `over` moves every figure identically against its
# own caption and cannot make two figures disagree. The one residual: if 0's
# true overshoot is below its cap — one estimator says so, the other does not —
# then "0.979" sits up to 0.45u left of flush. That is inside the 0.67u this
# page shipped with before the romans were fixed, and it is the same on every
# plate that draws it.
FIG_OVER = 1.24                # = 0.02 * 62, the largest display size here
D_OPTIC = {                    # display leading glyph -> (lsb em/1000, overshoot in u)
    "0": (32, FIG_OVER),
    "3": (35, FIG_OVER),
    "4": (20, FIG_OVER),
    "5": (63, FIG_OVER),
    "6": (29, FIG_OVER),
    # The romans. 'I' is a flat stem carrying an unusually deep bearing —
    # 85/1000, 2.55u of daylight at 30 — and, being flat, no overshoot at all:
    # its apparent edge IS its mechanical one, which is the construction the
    # `over` term is defined by. 'V' is the opposite shape and the reason this
    # table cannot be one number: almost no bearing (20/1000) but its leftmost
    # ink is a POINT, so it must overhang to read level. 1.47u is the same
    # low-pass read the figures got — 1.49u at 30 and 1.44u at 24, one
    # constant for both, and the two sizes agreeing to 0.05u is the evidence
    # for the claim above that this term is a fixed visual angle.
    "I": (85, 0.00),
    "V": (20, 1.47),
}
TEXT_LSB = 57                  # Commissioner 400's mean caption ink edge, em/1000
# Per-glyph, for the lines that must land ON an edge rather than near it:
# Commissioner 400's own xMin, em/1000, off the subset's outlines. TEXT_LSB
# above is their mean, and a mean is what a figure is aligned to because it
# faces a two-line caption block. A subtitle is ONE line and there is no mean
# to hide in: 't' starts 0.36u right of its pen origin at 14.5 and 'i' starts
# 0.96u, which is the whole of why the seven section subtitles disagreed with
# each other before they disagreed with the tile.
TEXT_OPTIC = {"S": 54.5, "a": 52.5, "e": 50.0, "i": 66.0, "n": 82.0, "t": 24.5}
# The section header's spine: the mark tile's painted left edge. _tile() draws
# rect x="0.75" under a 1u stroke, so paint starts 0.25u right of the mark's
# own x — and it starts there as a FLAT side 24u tall, an edge whose apparent
# position is its mechanical one. It is the largest object in the header and
# the only one whose edge is geometry rather than type, so it is the reference
# the type is brought to, not the other way round; and every section puts its
# mark at the section's x, so this is ONE number for the page.
SPINE = 0.25
# The declared type column of a desktop section plate. It moved from 148 with
# this change, and it had to: an 'I' whose ink lands on 150.25 has its PEN
# ORIGIN at 147.70, and check 5 measures getBoundingClientRect().x, which for
# SVG text is the pen box, not the ink (verified in Chromium — rectX equals the
# set x to the hundredth on all 48 plates). Shaving the correction to fit 148
# was the alternative and it is the one thing a declaration must never do: the
# column says where this plate's type starts, so when the type moves the
# declaration moves with it. The mobile plates keep col=(88,412) — their
# deepest origin is m-1-work's 57.8M at 89.38, and the romans land at 90.21.
SEC_COL = (147, 880)


def _ink(glyph: str, size: float, cap_em: float | None = None) -> float:
    """How far right of the pen origin the display face's ink actually starts.

    `cap_em` bounds the optical term to a fraction of the em. The figures pass
    2%; the romans pass nothing, and that is deliberate — see rom_x.
    """
    lsb, over = D_OPTIC[glyph]
    return lsb * size / 1000 + (over if cap_em is None else min(over, cap_em * size))


def fig_x(x: float, fig: str, size: float, cap: float = 13) -> float:
    """The x a display figure must be SET at to LAND on `x` optically.

    `x` stays the block's authored left edge — the number the captions are
    still set at, and the one the layout was reasoned about in. Only the
    figure moves, and only by what its own leading glyph costs.
    """
    shift = _ink(fig[0], size, cap_em=0.02) - TEXT_LSB * cap / 1000
    return round(x - shift, 2)


def rom_x(x: float, rom: str, size: float) -> float:
    """The x a section roman must be SET at to land its ink on the spine.

    No 2%-of-em cap here, and the omission is the argument. That cap bounds a
    ROUND's overshoot to the one Syne's own designer allows — 'O' standing
    20/1000 taller than 'H' — which is the right bound for a figure and the
    wrong one for an apex: at 30 it is 0.60u against 'V's measured 1.49u, so
    capping would leave the V-plates 0.89u inside the I-plates. That is a
    WIDER disagreement than the 0.67u the page ships with today, i.e. the cap
    would make the defect worse while looking like a correction.
    """
    return round(x + SPINE - _ink(rom[0], size), 2)


def txt_x(x: float, s: str, size: float) -> float:
    """The x a text line must be SET at to land ITS ink on the spine.

    Mechanical only, no optical term. At 13-14.5 the text face's strokes are
    thinner than the low-pass the display term is read under — the filter
    returns no half crossing at all, the apparent edge is the mechanical one —
    and it is also how every other text block on this page is set.
    """
    return round(x + SPINE - TEXT_OPTIC[s[0]] * size / 1000, 2)


def sec_roman(x: float, y: float, s: str, size: float) -> str:
    """A section roman, set so its ink lands on the plate's spine."""
    return (f'<text x="{rom_x(x, s, size)}" y="{y:g}" class="d" '
            f'font-size="{size:g}" letter-spacing="0.5">{s}</text>')


def sec_sub(x: float, y: float, s: str, size: float) -> str:
    """One line of a section subtitle, landing its ink on the same spine."""
    return (f'<text x="{txt_x(x, s, size)}" y="{y:g}" class="dim" '
            f'font-size="{size:g}">{s}</text>')


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
#   collectors  y=400/415/430, each turning straight down into its own
#               lane of the page bus at BUS_X. The fan band that used to
#               fill y=470-534 — one drop aimed at each fixed-px chip in
#               the old link row — died with those chips (2026-08-13): the
#               row's ports tap OFF the bundle now, so the hero's job at
#               its bottom edge is simply to land all three lanes at
#               63/90/117, the x every plate below carries them at.
def plate_hero() -> str:
    d_verd = "M766,80 V388 Q766,400 754,400 H75 Q63,400 63,412 V534"
    d_rust = "M744,216 V403 Q744,415 732,415 H102 Q90,415 90,427 V534"
    d_zinc = "M612,130 V418 Q612,430 600,430 H129 Q117,430 117,442 V534"
    c_verd = "M766,84 V388 Q766,400 754,400 H75 Q63,400 63,412 V531.5"
    c_rust = "M744,220 V403 Q744,415 732,415 H102 Q90,415 90,427 V531.5"
    c_zinc = "M612,134 V418 Q612,430 600,430 H129 Q117,430 117,442 V531.5"
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
# Four ports on the page bus, served as PERCENTAGE SLICES of one artwork —
# the interval strips' construction, ending two shipped defects at once:
#
#   · REGISTRATION, corrected 2026-08-13. The previous row was four fixed-px
#     chips calibrated to the 846px column; every 900u plate scales to the
#     column while a fixed-px image does not, so the lanes jogged at every
#     stub at every other width. A slice served at exactly its intrinsic
#     share of the 900 (integer percents, ROW_CUTS) scales by the same
#     factor as the plates above and below it, so the lanes land on the same
#     x at EVERY column width — registration by construction, not
#     calibration. Probed upstream before authoring: percentage slices open
#     no hairline at any width from 308 to 1200px.
#   · THE PIPELINE, corrected in the same change, on the client's read of
#     the render ("the pipeline through the chips is wrong"): the old row —
#     and the first draft of this one — fanned the three-lane bundle out
#     across the full width so each port could wear a lane at its own local
#     x. The bundle is the page's spine, and a spine does not disperse to
#     visit four components. Now the three buses run straight down the row
#     at BUS_X, whole and unbent — entry x, mid-row x and exit x are the
#     same three numbers as every plate above and below — and each port
#     TAPS OFF its lane at a junction dot: a horizontal rail at its own
#     tier, the way a component hangs off a trace. 63/90/117 all fall
#     inside slice one, so the bundle's continuity is owned by one slice
#     and cannot be broken by a cut. The hero hands the bundle over at
#     BUS_X (its fan band died with the chips) and the return plate passes
#     it on unchanged.
#
# THE GEOMETRY. Rails leave the bundle at three tiers — verd 70, rust 30,
# zinc 16 — and the packages stagger their bands so every rail reaches its
# own port's left edge without crossing a package it does not serve: rust
# clears J1's lid by 8u on its way to J2, then runs THROUGH J2 on the tile
# register to reach J3 (two components on one trace — the schematic truth
# of two links sharing the rust lane); zinc passes above everything to J4,
# whose package sits highest. Uneven bands are the client's own doctrine
# ("I like it uneven"), and they are what buys surface-only routing: the
# whole pipeline is visible end to end, no inner-layer dives inside the
# row. Nothing but the rails crosses a cut; a rail sub-path starting s
# units past its junction carries C − s, exactly like the interval rails;
# no text straddles a boundary.
#
# THE MARKS — real and in colour, the client's brief, every pair measured
# on its actual ground (scratchpad/row-contrast.py, 2026-08-13):
#   J1  the Waymark, the portfolio's own mark — geometry read from
#       brand/mark-night.svg AT BUILD TIME, not redrawn. The night cut in
#       both themes, because the module tile is its own dark ground: bar
#       #E08A5F 7.51:1 on the tile, glyph #F6EFE2 17.31:1.
#   J2  the résumé has no brand, so its mark is drawn from the Waymark's
#       own construction — the same bar at the same weight and station,
#       with a cream sheet standing astride it where J1's letterform
#       stands. The two self-owned ports read as a family because they are
#       built from one rule, not because they share a sticker style.
#   J3  LinkedIn's published mark, its own 24-box icon geometry: plate
#       #0A66C2 (3.48:1 on the tile, structure floor 3.0) under the white
#       glyphs (5.69:1 on the blue).
#   J4  a mailto: is not a Gmail link, and drawing Google's M on it would
#       claim a relationship that does not exist — so the mail mark is
#       designed in the board's own palette, on J3's construction: a
#       coloured plate carrying a glyph — the plate DARK verd #4FB39A
#       (7.77:1 on the tile), the envelope knocked out in the tile's own
#       ink (7.77:1 on the plate). Self-owned ports share the Waymark
#       construction; network ports share the plate construction.
#
# Module interiors keep the DARK register on every canvas (_OnTile): a
# package does not recolour with the room, and check 10 grades its ink
# against the tile either way. Everything riding the canvas — lanes,
# rails, junction dots, the canvas half of each pierce pad — is theme ink,
# because the row is theme-served now: <a><picture><source…><img></picture></a>
# on ONE source line survives GitHub's pipeline whole (the newline is the
# splitter, not the nesting — probed against the real /markdown API,
# 2026-08-13), so the old one-dark-artwork compromise is retired.
ROW_H = 110
ROW_CUTS = {1: 37, 2: 20, 3: 22, 4: 21}     # integer percents of the column
ROW_X0 = {1: 0, 2: 333, 3: 513, 4: 711}     # 900 × cumulative cuts
ROW_W = {k: v * 9 for k, v in ROW_CUTS.items()}
M_ROW_H = 84
M_ROW_X0 = {k: round(v * 440 / 900, 1) for k, v in ROW_X0.items()}
M_ROW_W = {k: round(v * 440 / 900, 1) for k, v in ROW_W.items()}
ROW_TIER = {"verd": 70, "rust": 30, "zinc": 16}     # rail y, desktop
M_ROW_TIER = {"verd": 52, "rust": 22, "zinc": 12}   # rail y, phone cut
ROW_C = {"verd": 20, "rust": 90, "zinc": 160}       # rail phase at the junction
# package bands (x0, x1, y0, y1). The bands stagger DOWNWARD as the tiers
# descend — J4 highest, J2/J3 middle, J1 lowest — see the routing note.
ROW_MOD = {"portfolio": (140, 328, 38, 102), "resume": (380, 500, 22, 86),
           "linkedin": (560, 690, 22, 86), "email": (750, 880, 8, 72)}
M_ROW_MOD = {"portfolio": (80, 156, 28, 76), "resume": (170, 244, 18, 66),
             "linkedin": (258, 340, 18, 66), "email": (356, 432, 6, 54)}

# J1's artwork, read from the brand file itself so the row can never drift
# from the mark the portfolio ships. The night cut serves both themes — the
# tile is its own dark ground (see the register note above).
_BRAND_NIGHT = (ROOT.parent / "brand" / "mark-night.svg").read_text()
_WAYMARK_D = re.search(r'd="(M468[^"]+)"', _BRAND_NIGHT).group(1)
_WAYMARK_BAR = re.search(r'stroke="(#[0-9a-fA-F]{6})"', _BRAND_NIGHT).group(1)
_WAYMARK_INK = re.search(r'fill="(#[0-9a-fA-F]{6})"', _BRAND_NIGHT).group(1)


class _OnTile:
    """Module interiors keep the DARK register on every canvas: the tile is
    its own (dark) ground, so its ink and its comet ramps never re-theme."""

    def __enter__(self):
        global T
        self._saved = T
        T = dict(T, ink=DARK["ink"], mid=DARK["mid"], dim=DARK["dim"],
                 verd=DARK["verd"], rust=DARK["rust"], zinc=DARK["zinc"],
                 ramp=DARK["ramp"])
        return self

    def __exit__(self, *a):
        global T
        T = self._saved


def _tile_mod(x0, y0, x1, y1):
    return (f'<rect x="{x0 + 0.5}" y="{y0}" width="{x1 - x0 - 1}" height="{y1 - y0}" '
            f'rx="3" fill="{TILE}" stroke="{T["edge"]}" stroke-width="1"/>')


def _pierce(bus_key, x, y, side="l"):
    """The pad where a rail pierces a package edge — the seam between the
    two registers: canvas half in theme ink, tile half in the DARK register."""
    canv_x, tile_x = (x - 3, x) if side == "l" else (x, x - 3)
    return (f'<rect x="{canv_x}" y="{y - 2.5}" width="3" height="5" fill="{T[bus_key]}"/>'
            f'<rect x="{tile_x}" y="{y - 2.5}" width="3" height="5" fill="{DARK[bus_key]}"/>')


def _land(bus_key, x, y, r=4.0):
    """A port land: ring plus solid centre, emitted INLINE (no wrapping <g>)
    so it stays in its module's group — gate.mjs composes by nearest
    enclosing group, and a land in its own group would collide with the
    tile it sits on."""
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="{T[bus_key]}" stroke-width="2"/>'
            f'<circle cx="{x}" cy="{y}" r="1.8" fill="{T[bus_key]}"/>')


def _tlbl(x, y, s, size=10.5, ls=0.9, dim=False):
    """Silkscreen ON a package: fill rides inline style, because head()'s
    <style> sets text fill from the THEME and the tile does not re-theme."""
    return (f'<text x="{x}" y="{y}" class="ts" font-size="{size}" letter-spacing="{ls}" '
            f'style="fill:{DARK["dim" if dim else "ink"]}">{s}</text>')


def mark_waymark(x, y, s):
    """The Waymark, verbatim: the brand file's own two paths, its transforms
    composed onto the placement. Presentation attributes ride each element
    (the flat-emitter law), and stroke-width scales with the transform, so
    44 in brand units is 44·s/512 = 3.3u drawn at s=38."""
    k = f"translate({x},{y}) scale({s / 512:.6f})"
    return (f'<path transform="{k}" d="M-2 293.9 H514" fill="none" '
            f'stroke="{_WAYMARK_BAR}" stroke-width="44"/>'
            f'<path transform="{k} translate(91.86,412) scale(0.22857,-0.22857)" '
            f'd="{_WAYMARK_D}" fill="{_WAYMARK_INK}"/>')


def mark_sheet(x, y, s):
    """J2's mark, from the Waymark's construction: the same bar at the same
    weight and station (293.9/512 of the box), with a cream sheet standing
    astride it where J1's letterform stands. Fold and rules are the tile's
    own ink — knockouts, like the envelope on J4's plate."""
    k = f"translate({x},{y}) scale({s / 512:.6f})"
    bar = (f'<path transform="{k}" d="M-2 293.9 H514" fill="none" '
           f'stroke="{_WAYMARK_BAR}" stroke-width="44"/>')
    x0, x1 = x + 0.30 * s, x + 0.70 * s
    y0, y1 = y + 0.20 * s, y + 0.82 * s
    f = 0.15 * s
    sheet = (f'<path d="M{x0:.1f},{y0:.1f} H{x1 - f:.1f} L{x1:.1f},{y0 + f:.1f} '
             f'V{y1:.1f} H{x0:.1f} Z" fill="{_WAYMARK_INK}"/>')
    fold = (f'<path d="M{x1 - f:.1f},{y0:.1f} V{y0 + f:.1f} H{x1:.1f}" fill="none" '
            f'stroke="{TILE}" stroke-width="{0.045 * s:.2f}"/>')
    rx0, rx1 = x0 + 0.09 * s, x1 - 0.09 * s
    rules = ('<path d="' + " ".join(f"M{rx0:.1f},{y + fy * s:.1f} H{rx1:.1f}"
                                    for fy in (0.34, 0.45))
             + f'" fill="none" stroke="{TILE}" stroke-width="{0.045 * s:.2f}"/>')
    return bar + sheet + fold + rules


# LinkedIn's published 24-box icon geometry — the mark as LinkedIn ships it,
# not a redrawing: the i-dot circle, the i-stem, and the n, white on the
# brand blue.
_LI_N = ("M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 "
         "0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 "
         "1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286z")


def mark_linkedin(x, y, s):
    k = s / 24
    return (f'<rect x="{x}" y="{y}" width="{s}" height="{s}" rx="{2 * k:.2f}" fill="#0A66C2"/>'
            f'<circle cx="{x + 5.337 * k:.2f}" cy="{y + 5.368 * k:.2f}" r="{2.064 * k:.2f}" fill="#FFFFFF"/>'
            f'<rect x="{x + 3.555 * k:.2f}" y="{y + 9 * k:.2f}" width="{3.564 * k:.2f}" '
            f'height="{11.452 * k:.2f}" fill="#FFFFFF"/>'
            f'<path transform="translate({x},{y}) scale({k:.4f})" d="{_LI_N}" fill="#FFFFFF"/>')


def mark_mail(x, y, s):
    """J4's mark, on J3's construction: a coloured plate carrying a glyph —
    the plate the board's own verd, the envelope the tile's own ink. NOT
    Gmail's M: a mailto: is not a Gmail link, and this page does not wear
    marks it has no claim to."""
    k = s / 24
    ex, ey = x + 4.5 * k, y + 7 * k
    ew, eh = 15 * k, 10.5 * k
    return (f'<rect x="{x}" y="{y}" width="{s}" height="{s}" rx="{2 * k:.2f}" fill="{DARK["verd"]}"/>'
            f'<rect x="{ex:.2f}" y="{ey:.2f}" width="{ew:.2f}" height="{eh:.2f}" rx="{1.2 * k:.2f}" '
            f'fill="none" stroke="{TILE}" stroke-width="{1.7 * k:.2f}"/>'
            f'<path d="M{ex:.2f},{ey + k:.2f} L{ex + ew / 2:.2f},{ey + 6.5 * k:.2f} '
            f'L{ex + ew:.2f},{ey + k:.2f}" fill="none" stroke="{TILE}" '
            f'stroke-width="{1.7 * k:.2f}"/>')


# ── the four descriptions, authored once; the same words serve both cuts.
DESC_PORT = {
    "portfolio": ("Port one of four on the link bus: ayush-yadav.com, the "
                  "portfolio, wearing the Waymark. The three page buses run "
                  "whole through the row — every port taps off its own lane, "
                  "and no lane leaves the bundle."),
    "resume": ("Port two of four: the résumé, as a PDF. Its mark is drawn "
               "from the Waymark's own construction — the same bar, with a "
               "sheet standing astride it — on a tap off the rust lane."),
    "linkedin": ("Port three of four: the LinkedIn profile, carrying "
                 "LinkedIn's own mark. The rust tap runs on through the "
                 "résumé's package to reach it."),
    "email": ("Port four of four: email — opens a mail draft. The mail mark "
              "is drawn in the board's own palette; the zinc tap reaches it "
              "past every other package."),
}


def row_s1() -> str:
    """Slice one: the whole bundle, its three junctions, and J1."""
    w = ROW_W[1]
    body = ""
    for k, C in zip(("verd", "rust", "zinc"), (135, 40, 190)):
        x = BUS_X[k]
        body += bus(k, f"M{x},0 V{ROW_H}", C=C, cd=f"M{x},2.5 V{ROW_H - 2.5}")
    for k in ("verd", "rust", "zinc"):
        body += _dot(k, BUS_X[k], ROW_TIER[k])
    body += _rail("verd", "M63,70 H140", ROW_C["verd"], "M63,70 H137.5")
    body += _rail("rust", f"M90,30 H{w}", ROW_C["rust"], f"M90,30 H{w}")
    body += _rail("zinc", f"M117,16 H{w}", ROW_C["zinc"], f"M117,16 H{w}")
    x0, x1, y0, y1 = ROW_MOD["portfolio"]
    body += f'<g>{_tile_mod(x0, y0, x1, y1)}'
    with _OnTile():
        body += (f'<path class="bus" stroke="{T["verd"]}" d="M{x0},70 H145"/>'
                 + _land("verd", 149, 70)
                 + mark_waymark(160, 51, 38)
                 + _tlbl(206, 74, "AYUSH-YADAV.COM", size=10.5, ls=0.8)
                 + _tlbl(148, 96, "J1", size=8.5, ls=1.2, dim=True))
    body += "</g>" + _pierce("verd", x0, 70)
    return head(ROW_H, "the link bus, port one — ayush-yadav.com",
                DESC_PORT["portfolio"], key="plate-port-portfolio.svg",
                col=(0, 327.5), frame=PORT_FRAME.get("plate-port-portfolio.svg"),
                faces="6", w=w) + css_close() + body + "</svg>"


def row_s2() -> str:
    """Slice two: J2 sits ON the rust rail — the rail crosses the package on
    the tile register and carries on toward J3; zinc passes above."""
    w, X0 = ROW_W[2], ROW_X0[2]
    cr = ROW_C["rust"] - (X0 - BUS_X["rust"])
    cz = ROW_C["zinc"] - (X0 - BUS_X["zinc"])
    x0, x1 = ROW_MOD["resume"][0] - X0, ROW_MOD["resume"][1] - X0
    y0, y1 = ROW_MOD["resume"][2], ROW_MOD["resume"][3]
    body = (_rail("zinc", f"M0,16 H{w}", cz, f"M0,16 H{w}")
            + _rail("rust", f"M0,30 H{x0}", cr, f"M0,30 H{x0 - 2.5}"))
    body += f'<g>{_tile_mod(x0, y0, x1, y1)}'
    with _OnTile():
        body += (f'<path class="bus" stroke="{T["rust"]}" d="M{x0},30 H{x1}"/>'
                 + comet("rust", f"M{x0},30 H{x1}", cr - x0)
                 + comet("rust", f"M{x0},30 H{x1}", cr - x0 - PAT / 2)
                 + _land("rust", 82, 30)
                 + mark_sheet(65, 39, 30)
                 + _tlbl(103, 58, "RÉSUMÉ", size=10.5, ls=1.1)
                 + _tlbl(55, 80, "J2", size=8.5, ls=1.2, dim=True))
    body += ("</g>" + _pierce("rust", x0, 30) + _pierce("rust", x1, 30, side="r")
             + _rail("rust", f"M{x1},30 H{w}", cr - x1, f"M{x1},30 H{w}"))
    return head(ROW_H, "the link bus, port two — the résumé",
                DESC_PORT["resume"], key="plate-port-resume.svg",
                col=(0, x1 - 0.5), frame=PORT_FRAME.get("plate-port-resume.svg"),
                faces="6", w=w) + css_close() + body + "</svg>"


def row_s3() -> str:
    """Slice three: the rust rail arrives and dies at J3's land."""
    w, X0 = ROW_W[3], ROW_X0[3]
    cr = ROW_C["rust"] - (X0 - BUS_X["rust"])
    cz = ROW_C["zinc"] - (X0 - BUS_X["zinc"])
    x0, x1 = ROW_MOD["linkedin"][0] - X0, ROW_MOD["linkedin"][1] - X0
    y0, y1 = ROW_MOD["linkedin"][2], ROW_MOD["linkedin"][3]
    body = (_rail("zinc", f"M0,16 H{w}", cz, f"M0,16 H{w}")
            + _rail("rust", f"M0,30 H{x0}", cr, f"M0,30 H{x0 - 2.5}"))
    body += f'<g>{_tile_mod(x0, y0, x1, y1)}'
    with _OnTile():
        body += (f'<path class="bus" stroke="{T["rust"]}" d="M{x0},30 H57"/>'
                 + _land("rust", 61, 30)
                 + mark_linkedin(71, 40, 28)
                 + _tlbl(107, 58, "LINKEDIN", size=10, ls=0.7)
                 + _tlbl(55, 80, "J3", size=8.5, ls=1.2, dim=True))
    body += "</g>" + _pierce("rust", x0, 30)
    return head(ROW_H, "the link bus, port three — LinkedIn",
                DESC_PORT["linkedin"], key="plate-port-linkedin.svg",
                col=(0, x1 - 0.5), frame=PORT_FRAME.get("plate-port-linkedin.svg"),
                faces="6", w=w) + css_close() + body + "</svg>"


def row_s4() -> str:
    """Slice four: the zinc rail, clear of every package it does not serve,
    dies at J4's land."""
    w, X0 = ROW_W[4], ROW_X0[4]
    cz = ROW_C["zinc"] - (X0 - BUS_X["zinc"])
    x0, x1 = ROW_MOD["email"][0] - X0, ROW_MOD["email"][1] - X0
    y0, y1 = ROW_MOD["email"][2], ROW_MOD["email"][3]
    body = _rail("zinc", f"M0,16 H{x0}", cz, f"M0,16 H{x0 - 2.5}")
    body += f'<g>{_tile_mod(x0, y0, x1, y1)}'
    with _OnTile():
        body += (f'<path class="bus" stroke="{T["zinc"]}" d="M{x0},16 H49"/>'
                 + _land("zinc", 53, 16)
                 + mark_mail(71, 26, 28)
                 + _tlbl(107, 44, "EMAIL", size=10.5, ls=1.1)
                 + _tlbl(47, 66, "J4", size=8.5, ls=1.2, dim=True))
    body += "</g>" + _pierce("zinc", x0, 16)
    return head(ROW_H, "the link bus, port four — email",
                DESC_PORT["email"], key="plate-port-email.svg",
                col=(0, x1 - 0.5), frame=PORT_FRAME.get("plate-port-email.svg"),
                faces="6", w=w) + css_close() + body + "</svg>"


def m_row_s1() -> str:
    w = M_ROW_W[1]
    body = ""
    for k, C in zip(("verd", "rust", "zinc"), (135, 40, 190)):
        x = MBUS_X[k]
        body += bus(k, f"M{x},0 V{M_ROW_H}", C=C, cd=f"M{x},2.5 V{M_ROW_H - 2.5}")
    for k in ("verd", "rust", "zinc"):
        body += _dot(k, MBUS_X[k], M_ROW_TIER[k], r=2.4)
    body += _rail("verd", "M40,52 H80", ROW_C["verd"], "M40,52 H77.5")
    body += _rail("rust", f"M54,22 H{w}", ROW_C["rust"], f"M54,22 H{w}")
    body += _rail("zinc", f"M68,12 H{w}", ROW_C["zinc"], f"M68,12 H{w}")
    x0, x1, y0, y1 = M_ROW_MOD["portfolio"]
    body += f'<g>{_tile_mod(x0, y0, x1, y1)}'
    with _OnTile():
        body += (f'<path class="bus" stroke="{T["verd"]}" d="M{x0},52 H85.5"/>'
                 + _land("verd", 90, 52, r=3.5)
                 + mark_waymark(105, 39, 26)
                 + _tlbl(85, 70, "J1", size=8, ls=1, dim=True))
    body += "</g>" + _pierce("verd", x0, 52)
    return head(M_ROW_H, "the link bus, port one — ayush-yadav.com, phone cut",
                DESC_PORT["portfolio"], key="m-port-portfolio.svg",
                col=(0, 155.5), frame=PORT_FRAME.get("m-port-portfolio.svg"),
                faces="6", w=w) + css_close() + body + "</svg>"


def m_row_s2() -> str:
    w, X0 = M_ROW_W[2], M_ROW_X0[2]
    cr = ROW_C["rust"] - (X0 - MBUS_X["rust"])
    cz = ROW_C["zinc"] - (X0 - MBUS_X["zinc"])
    x0 = round(M_ROW_MOD["resume"][0] - X0, 1)
    x1 = round(M_ROW_MOD["resume"][1] - X0, 1)
    y0, y1 = M_ROW_MOD["resume"][2], M_ROW_MOD["resume"][3]
    body = (_rail("zinc", f"M0,12 H{w}", cz, f"M0,12 H{w}")
            + _rail("rust", f"M0,22 H{x0}", cr, f"M0,22 H{x0 - 2.5}"))
    body += f'<g>{_tile_mod(x0, y0, x1, y1)}'
    with _OnTile():
        body += (f'<path class="bus" stroke="{T["rust"]}" d="M{x0},22 H{x1}"/>'
                 + comet("rust", f"M{x0},22 H{x1}", cr - x0)
                 + comet("rust", f"M{x0},22 H{x1}", cr - x0 - PAT / 2)
                 + _land("rust", 44.2, 22, r=3.5)
                 + mark_sheet(31.2, 29, 26)
                 + _tlbl(11.2, 62, "J2", size=8, ls=1, dim=True))
    body += ("</g>" + _pierce("rust", x0, 22) + _pierce("rust", x1, 22, side="r")
             + _rail("rust", f"M{x1},22 H{w}", cr - x1, f"M{x1},22 H{w}"))
    return head(M_ROW_H, "the link bus, port two — the résumé, phone cut",
                DESC_PORT["resume"], key="m-port-resume.svg",
                col=(0, x1 - 0.5), frame=PORT_FRAME.get("m-port-resume.svg"),
                faces="6", w=w) + css_close() + body + "</svg>"


def m_row_s3() -> str:
    w, X0 = M_ROW_W[3], M_ROW_X0[3]
    cr = ROW_C["rust"] - (X0 - MBUS_X["rust"])
    cz = ROW_C["zinc"] - (X0 - MBUS_X["zinc"])
    x0 = round(M_ROW_MOD["linkedin"][0] - X0, 1)
    x1 = round(M_ROW_MOD["linkedin"][1] - X0, 1)
    y0, y1 = M_ROW_MOD["linkedin"][2], M_ROW_MOD["linkedin"][3]
    body = (_rail("zinc", f"M0,12 H{w}", cz, f"M0,12 H{w}")
            + _rail("rust", f"M0,22 H{x0}", cr, f"M0,22 H{x0 - 2.5}"))
    body += f'<g>{_tile_mod(x0, y0, x1, y1)}'
    with _OnTile():
        body += (f'<path class="bus" stroke="{T["rust"]}" d="M{x0},22 H15.2"/>'
                 + _land("rust", 19.2, 22, r=3.5)
                 + mark_linkedin(35.2, 29, 26)
                 + _tlbl(11.2, 62, "J3", size=8, ls=1, dim=True))
    body += "</g>" + _pierce("rust", x0, 22)
    return head(M_ROW_H, "the link bus, port three — LinkedIn, phone cut",
                DESC_PORT["linkedin"], key="m-port-linkedin.svg",
                col=(0, x1 - 0.5), frame=PORT_FRAME.get("m-port-linkedin.svg"),
                faces="6", w=w) + css_close() + body + "</svg>"


def m_row_s4() -> str:
    w, X0 = M_ROW_W[4], M_ROW_X0[4]
    cz = ROW_C["zinc"] - (X0 - MBUS_X["zinc"])
    x0 = round(M_ROW_MOD["email"][0] - X0, 1)
    x1 = round(M_ROW_MOD["email"][1] - X0, 1)
    y0, y1 = M_ROW_MOD["email"][2], M_ROW_MOD["email"][3]
    body = _rail("zinc", f"M0,12 H{x0}", cz, f"M0,12 H{x0 - 2.5}")
    body += f'<g>{_tile_mod(x0, y0, x1, y1)}'
    with _OnTile():
        # the current crosses the package to a far-side land, J2-style: an
        # 8u entry stub left this plate's only motion a 6u comet window and
        # it froze under motion.mjs's 70% floor (43%/36% measured) — the
        # 58u through-run keeps a ramp boundary in frame at every t.
        body += (f'<path class="bus" stroke="{T["zinc"]}" d="M{x0},12 H66"/>'
                 + comet("zinc", f"M{x0},12 H63.5", cz - x0)
                 + comet("zinc", f"M{x0},12 H63.5", cz - x0 - PAT / 2)
                 + _land("zinc", 70, 12, r=3.5)
                 + mark_mail(33.4, 17, 26)
                 + _tlbl(12.4, 50, "J4", size=8, ls=1, dim=True))
    body += "</g>" + _pierce("zinc", x0, 12)
    return head(M_ROW_H, "the link bus, port four — email, phone cut",
                DESC_PORT["email"], key="m-port-email.svg",
                col=(0, x1 - 0.5), frame=PORT_FRAME.get("m-port-email.svg"),
                faces="6", w=w) + css_close() + body + "</svg>"


# ══════════════════════════════════════════════════ the return plate
#
# Below the link row the bundle simply CONTINUES — the ports tapped off it
# without moving it, so there is nothing to merge. What this plate still
# owes the page is its one line of wayfinding: it names what the bus runs
# into next, and it is the only text between the ports and section II.
def plate_return() -> str:
    body = (
        _dbus("verd", "M63,0 V64", 30, "M63,2.5 V61.5")
        + _dbus("rust", "M90,0 V64", 150, "M90,2.5 V61.5")
        + _dbus("zinc", "M117,0 V64", 100, "M117,2.5 V61.5")
        + lbl(640, 58, "THE EVIDENCE · SECTIONS II — VII", size=10.5)
    )
    return head(
        64,
        "the page bus continues past the link ports",
        "The three page buses continue past the link ports, whole, into the "
        "evidence — sections two to seven.",
        key="plate-link-return.svg",
        col=(44, 886), frame=RET_FRAME,
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
        + sec_roman(150, 54, "II — JETPACK", 30)
        + sec_sub(150, 76, "is hand-vectorised code actually faster?", 14.5)
        + f'<text x="{fig_x(640, "6.4×", 62)}" y="138" class="d" font-size="62">6.4×</text>'
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
        col=SEC_COL, frame=JET_FRAME,
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
        + sec_roman(150, 54, "I — WORK", 30)
        + sec_sub(150, 76, "twelve months of production data work — none of it public.", 14.5)
        + lbl(852, 30, "FIRST, THE EXCEPTION — ATTESTED, NOT DERIVED", size=10.5, anchor="end")
        + f'<text x="{fig_x(584, "57.8M", 56)}" y="150" class="d" font-size="56">57.8M</text>'
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
        col=SEC_COL, frame=WORK_FRAME,
    ) + css_close() + body + "</svg>"


# ══════════════════════════════════════════════════ III · glyph
#
# The section drawn as its own part: ONE register-lane bundle carrying
# current — NEON — and two UNPOPULATED FOOTPRINTS beside it, the board's own
# way of drawing a part it does not have (the idiom §I gives the page, and
# §VI and §VII repeat: outline dashed, lead left open). All three kernel
# families are written in glyph's source; the family is chosen at COMPILE
# time by #if on __AVX512F__ / __AVX2__ / __ARM_NEON, there is no runtime
# dispatch anywhere in the library, ci/release/sanitizers all build with
# -DFAST_MNIST_ENABLE_NATIVE=OFF, and the reference machine is an M1 Pro —
# arm64. So exactly one of the three could have produced 3.5×, and the
# drawing said all three did until 2026-08-13.
#
# The silkscreen reads WRITTEN · NOT MEASURED and not NOT COMPILED, which
# would assert a universal the evidence does not carry: those kernels were
# not compiled HERE, on this machine, in this CI. Not measured is exactly
# what the evidence shows.
#
# Then the one measured lane drops to the package that actually ships: the
# wasm_simd128 build, byte-counted and checked daily. The admission block
# runs four lines, the longest on the page, because this section owes three
# of them: the score (8 of 12 matrix ops lose, and the win never reaches the
# product), the bandwidth-bound worst case, and the checkpoint the test set
# picked. It is deliberately NOT a size floor — benchAxpy/128 is 16,384
# elements, four times above the gate that decides whether to thread at all.
def isa_slot(x: float, y: float, w: float, label: str, n: int,
             C: float | None = None) -> str:
    """One kernel family, drawn as the slot the board keeps for it.

    ONE emitter for all three, and that is the point: the outline, the
    designator, the 6u lane pitch and the lane COUNT — 2/4/8, the lanes a
    128/256/512-bit register holds — are identical whether or not the part
    is fitted, so the only difference a reader has to read is the one the
    evidence carries. `C` is a comet phase: pass none and the slot prints as
    a FOOTPRINT (outline dashed, pads bare, nothing driving them); pass one
    and the part is fitted (outline solid, lanes carrying the current at that
    phase, and both lanes on the SAME phase because that is what SIMD is —
    one instruction, the lanes in lockstep).

    The lanes' vertical span is (n-1)*6 either way, so the register-width
    claim survives the fitting: it is the pad rows and the lane rows that are
    countable, not the outline, whose height only follows them.

    The lane rows start 24u down — under the designator, which is printed in
    the slot the way silkscreen prints it — and clear the bottom edge by 10.
    A 2-lane part is the reason the bottom figure is not 6: at 6 the fitted
    track ran 4u off the outline and read as the edge of the box rather than
    as a lane inside it. The electrical centre a feeder must arrive at is
    y+24+3(n-1).
    """
    h = 34 + 6 * (n - 1)
    ys = [y + 24 + i * 6 for i in range(n)]
    out = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="none" '
           f'stroke="{T["zinc"]}" stroke-width="1.4"'
           + ('' if C is not None else ' stroke-dasharray="5 4"')
           + '/>' + lbl(x + 10, y + 15, label, size=10, ls=1.2))
    if C is None:
        # bare pads: short and FILLED where a live lane is stroked and
        # continuous. The gap between the two pad columns is where the part
        # would sit, and it is the whole of what makes the slot read empty.
        # One <g>, like §I's footprint — a pad inside the outline it serves
        # is composition, not collision.
        return "<g>" + out + "".join(
            f'<rect x="{x + 6}" y="{v - 1}" width="13" height="2" fill="{T["zinc"]}"/>'
            f'<rect x="{x + w - 19}" y="{v - 1}" width="13" height="2" fill="{T["zinc"]}"/>'
            for v in ys) + "</g>"
    # fitted: 6u of lead out of each side, tied off into one net by the bars
    # the feeder and the collector actually land on.
    out += (f'<path class="bus" stroke="{T["rust"]}" '
            f'd="M{x - 6},{ys[0]} V{ys[-1]} M{x + w + 6},{ys[0]} V{ys[-1]}"/>')
    for v in ys:
        out += bus("rust", f"M{x - 6},{v} H{x + w + 6}", C=C,
                   cd=f"M{x - 4},{v} H{x + w + 4}")
    return out


def plate_glyph() -> str:
    body = (
        bus("verd", "M63,0 V468", C=40, cd="M63,2.5 V465.5")
        + bus("rust", "M90,0 V468", C=130, cd="M90,2.5 V465.5")
        + bus("zinc", "M117,0 V468", C=8, cd="M117,2.5 V465.5")
        # SIMD tap into the mark, then the feeder down to the ONE junction
        # the current reaches. Rust ends and zinc continues at that dot: the
        # dot is the #if, and the colour change is the branch not taken.
        + bus("rust", "M90,120 H150", C=88, cd="M94,120 H145")
        + bus("rust", "M198,120 H264 V168", C=30, cd="M202,120 H264 V165")
        + f'<circle cx="264" cy="168" r="2.6" fill="{T["rust"]}"/>'
        + bus("rust", "M264,168 H288", C=60, cd="M266.5,168 H285")
        + isa_slot(294, 141, 132, "NEON", 2, C=96)
        # the two written-but-unbuilt families: routed to, never energised.
        # Each lead stops in an open ring short of its pads (§VI's severed
        # cascade, same construction) — the net exists, nothing drives it.
        + f'<path fill="none" stroke="{T["zinc"]}" stroke-width="1.4" '
          f'd="M264,168 V308 M264,232 H272 M264,308 H272"/>'
        + f'<circle cx="264" cy="232" r="2.2" fill="{T["zinc"]}"/>'
        + f'<circle cx="278.5" cy="232" r="3.5" fill="none" stroke="{T["zinc"]}" stroke-width="2"/>'
        + f'<circle cx="278.5" cy="308" r="3.5" fill="none" stroke="{T["zinc"]}" stroke-width="2"/>'
        + isa_slot(294, 199, 132, "AVX2", 4)
        + isa_slot(294, 263, 132, "AVX-512", 8)
        + lbl(294, 360, "WRITTEN · NOT MEASURED", size=10, ls=1.1)
        # one part in, one measurement out: the collector is a single run now
        + bus("rust", "M432,168 H456 V235 H492", C=142, cd="M434,168 H456 V235 H489")
        + f'<rect x="492" y="214" width="170" height="42" rx="8" fill="none" '
          f'stroke="{T["rust"]}" stroke-width="1.6"/>'
        + lbl(504, 240, "BENCHDOT/256", cls="ts", size=11.5, ls=1.3)
        # and drops to the package that ships
        + bus("rust", "M577,256 V300", C=55, cd="M577,258.5 V296")
        + f'<rect x="492" y="300" width="208" height="42" rx="8" fill="none" '
          f'stroke="{T["zinc"]}" stroke-width="1.6"/>'
        + lbl(504, 326, "WASM_SIMD128 · 43,751 B", cls="ts", size=11.5, ls=1.3)
        + lbl(492, 360, "BYTE-IDENTICAL TO MAIN · CHECKED DAILY BY THIS PAGE", size=10, ls=1.1)
        + mark("glyph", 150, 96, 48)
        + sec_roman(150, 54, "III — GLYPH", 30)
        + sec_sub(150, 76, "SIMD kernels over a net the course provided.", 14.5)
        + f'<text x="{fig_x(660, "3.5×", 62)}" y="150" class="d" font-size="62">3.5×</text>'
        + f'<text x="660" y="188" class="dim" font-size="13">benchDot/256 — OpenMP threads,</text>'
        + f'<text x="660" y="206" class="dim" font-size="13">same kernels · committed runs.</text>'
        + f'<rect x="150" y="382" width="4" height="16" fill="{T["rust"]}"/>'
        + f'<text x="164" y="395" class="mid" font-size="14">the same flags lose 8 of 12 matrix-op cases — worst, benchAxpy/128, 10.7× slower,</text>'
        + f'<text x="164" y="415" class="dim" font-size="13">memory-bandwidth-bound; axpy never pays at any size measured, and end-to-end,</text>'
        + f'<text x="164" y="433" class="dim" font-size="13">threading buys nothing. and 97.01% is a training-time number: the test set</text>'
        + f'<text x="164" y="451" class="dim" font-size="13">that graded the net also picked its checkpoint.</text>'
    )
    return head(
        468,
        "III · Glyph — SIMD kernels over a course-provided net: 3.5× from OpenMP threading on the NEON build, the one kernel family the reference machine compiled; the same flags lose 8 of 12 matrix-op cases, 10.7× slower at the worst, where memory bandwidth is the wall",
        "III · Glyph — SIMD kernels over a course-provided MNIST net, drawn "
        "as one register-lane bundle carrying current and two unpopulated "
        "footprints beside it. Kernels are written for NEON, AVX2 and "
        "AVX-512, but the family is chosen at compile time, there is no "
        "runtime dispatch, and the reference machine is arm64 — so only the "
        "NEON bundle was built, and only its lanes run to benchDot/256: "
        "3.5× from OpenMP threading over the same kernels, its own "
        "single-threaded build, from committed runs. The AVX2 and AVX-512 "
        "slots are printed with their pads bare and their leads left open, "
        "silkscreened: written, not measured. The package that ships is "
        "WASM_SIMD128, 43,751 bytes, byte-identical to main and checked "
        "daily by this page's own CI. The against-self results are printed: "
        "the same flags lose 8 of 12 matrix-op cases and buy nothing "
        "end-to-end — worst is benchAxpy/128, 10.7× slower, "
        "memory-bandwidth-bound, where axpy never pays at any size measured "
        "— and 97.01% is a training-time "
        "number — the test set that graded the net also picked its "
        "checkpoint.",
        key="plate-3-glyph.svg",
        col=SEC_COL, frame=GLYPH_FRAME,
    ) + css_close() + body + "</svg>"


# ══════════════════════════════════════════════════ IV · automl
#
# The tool library drawn as one registry strip: a 44-pin comb — one pin per
# tool SCHEMA, emitted by loop so the count is true by construction — with
# seven tool-set taps hanging below it. llm/tools.ts is the DISPATCHER and
# holds no schemas at all; the 44 are defined across the seven modules in
# llm/tools/ (dataTools 4, cellTools 8, packageTools 3, featureTools 6,
# preprocessingTools 14, trainingTools 6, uiTools 3) and exposed as the seven
# LLM_*_TOOLS phase sets. The drawing was always right; the caption named the
# wrong file until 2026-08-13. No tap spans the strip, which
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
        + sec_roman(150, 54, "IV — AUTOML", 30)
        + sec_sub(150, 76, "a LangGraph agent, dealt its tools phase by phase.", 14.5)
        + f'<text x="{fig_x(660, "44", 62)}" y="160" class="d" font-size="62">44</text>'
        + f'<text x="660" y="198" class="dim" font-size="13">tool schemas in llm/tools;</text>'
        + f'<text x="660" y="216" class="dim" font-size="13">no phase&#8217;s hand holds them all.</text>'
        + f'<rect x="150" y="308" width="4" height="16" fill="{T["zinc"]}"/>'
        + f'<text x="164" y="321" class="mid" font-size="14">the sandbox guards against accidents, not adversaries.</text>'
        + f'<text x="164" y="341" class="dim" font-size="13">the network is an env var — the beta template renders it bridge; no cap-drop, no pids-limit, no seccomp.</text>'
    )
    return head(
        380,
        "IV · AutoML — 44 tools defined; no phase is handed all of them",
        "IV · AutoML — the tool library drawn as one registry strip: a 44-pin "
        "comb, one pin per tool schema, with seven tool-set taps below "
        "it — no phase is handed all 44. The against-self line is the "
        "sandbox: it guards against accidents, not adversaries — the network "
        "is an env var the beta template renders as bridge, with no "
        "cap-drop, no pids-limit, no seccomp.",
        key="plate-4-automl.svg",
        col=SEC_COL, frame=AUTOML_FRAME,
    ) + css_close() + body + "</svg>"


# ══════════════════════════════════════════════════ V · cadence
#
# The whole API drawn as the one part it actually is: 36 entry stubs — one
# per route handler, 36 evenly across the same 150..330 span, count true by
# construction — into a
# single serverless package, whose single output crosses a doored wall
# before the 7 table frames behind it. The wall is the section's claim: the
# door is the only way through, because RLS is FORCEd. The app-side guards
# being conditional is the admission, and the drawing agrees — nothing else
# crosses the wall.
def plate_cadence() -> str:
    stubs = " ".join(f"M252,{150 + i * 180 / 35:.1f} H300" for i in range(36))
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
        + lbl(312, 258, "36 ROUTE HANDLERS", cls="ts dim", size=10, ls=1.1)
        + bus("verd", "M496,235 H600", C=66, cd="M500,235 H596")
        # the wall, doored only where the output passes
        + f'<path class="bus" stroke="{T["verd"]}" d="M560,150 V223 M560,247 V330"/>'
        + f'<path class="bus" stroke="{T["verd"]}" d="M566,150 V223 M566,247 V330"/>'
        + lbl(563, 140, "RLS · FORCED", size=10.5, anchor="middle")
        + bus("verd", "M600,165 V315", C=190, cd="M600,168 V312")
        + f'<path fill="none" stroke="{T["verd"]}" stroke-width="1.4" d="{fan}"/>'
        + tables
        + mark("cadence", 150, 96, 48)
        + sec_roman(150, 54, "V — CADENCE", 30)
        + sec_sub(150, 76, "every route, one function; RLS on every tenant row.", 14.5)
        + f'<text x="{fig_x(680, "36", 62)}" y="70" class="d" font-size="62">36</text>'
        + f'<text x="680" y="108" class="dim" font-size="13">route handlers, one function;</text>'
        + f'<text x="680" y="126" class="dim" font-size="13">RLS FORCEd on all 7 tables.</text>'
        + f'<rect x="150" y="374" width="4" height="16" fill="{T["verd"]}"/>'
        + f'<text x="164" y="387" class="mid" font-size="14">every one of the six services carries a conditional owner guard.</text>'
        + f'<text x="164" y="407" class="dim" font-size="13">a caller that forgets the identity still sends the query; the database&#8217;s refusal cannot be forgotten.</text>'
    )
    return head(
        440,
        "V · Cadence — 36 route handlers, one function, and a wall with one door",
        "V · Cadence — the whole API drawn as one part: 36 route handlers "
        "enter one serverless function, and its single output passes through "
        "the one door in a wall — row-level security, FORCEd — before "
        "reaching the 7 tables behind it. The against-self line: every one of "
        "the six services carries a conditional owner guard; a caller that "
        "forgets the identity still sends the query, and the database's "
        "refusal is the one that cannot be forgotten.",
        key="plate-5-cadence.svg",
        col=SEC_COL, frame=CADENCE_FRAME,
    ) + css_close() + body + "</svg>"


# ══════════════════════════════════════════════════ VI · applied
#
# The part that ships and the part that doesn't, on one plate. The rules
# layer grades a strip of 96 ticks — two of them rust, the two it called
# wrong — and below it the cascade is drawn in the board's absence
# vocabulary: a dashed outline, its lead ending in an open circle, because
# it is not what ships — the deployed app runs the rules layer alone. It is
# NOT drawn dashed for want of evidence: an evaluation artifact for the
# cascade was committed to applied on 2026-08-11, and this page pins an
# older commit, so the row still cites the tracker line until the pin moves.
# The wrong ticks are placed by hand;
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
        + lbl(252, 245, "THE FULL CASCADE", cls="ts dim", size=10, ls=1.1)
        + lbl(240, 286, "SCORED LOWER THAN THE RULES LAYER", size=10, ls=1.1)
        + mark("applied", 150, 96, 48)
        + sec_roman(150, 54, "VI — APPLIED", 30)
        + sec_sub(150, 76, "an inbox read by rules that keep score.", 14.5)
        + f'<text x="{fig_x(560, "0.979", 62)}" y="240" class="d" font-size="62">0.979</text>'
        + f'<text x="560" y="278" class="dim" font-size="13">macro-F1 — the rules layer alone,</text>'
        + f'<text x="560" y="296" class="dim" font-size="13">graded on the strip above.</text>'
        + f'<rect x="150" y="362" width="4" height="16" fill="{T["verd"]}"/>'
        + f'<text x="164" y="375" class="mid" font-size="14">the full cascade scored 0.9583 — lower than the rules layer alone.</text>'
        + f'<text x="164" y="395" class="dim" font-size="13">a tracker line records it. what is deployed runs only that first layer.</text>'
    )
    return head(
        430,
        "VI · Applied — 0.979 macro-F1, rules layer alone; the full cascade scored lower",
        "VI · Applied — the mail triage drawn as the part that ships: the "
        "rules layer grades a labelled strip of 96 messages and gets 2 wrong "
        "— 0.979 macro-F1, rules layer alone. Below it, drawn dashed with "
        "its lead left open — it is not what ships — is the full cascade, "
        "all three layers, and it scored lower: 0.9583, a number a tracker "
        "line records. What is deployed runs only that first layer.",
        key="plate-6-applied.svg",
        col=SEC_COL, frame=APPLIED_FRAME,
    ) + css_close() + body + "</svg>"


# ══════════════════════════════════════════════════ VII · visualassist
#
# The alert policy drawn to scale from the phone in the reader's hand:
# three arcs at 0.5 / 1.0 / 2.0 m along a measured ruler, their styles
# keyed to a swatch legend — solid rust buzzes and says Stop, dashed rust
# pulses and says Caution, and zinc is NOT a silent ring: past 1.0 m the
# automatic check does nothing, and 2.0 m is how far the manual Describe
# call reaches. The mark's own encoding at board scale. The behaviour
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
        + lbl(540, 180, "0.5 M — BUZZ + STOP", cls="ts", size=11, ls=1.3)
        + f'<path fill="none" stroke="{T["rust"]}" stroke-width="2" stroke-dasharray="4.5 4.8" d="M522,201 H534"/>'
        + lbl(540, 205, "1.0 M — PULSE + CAUTION", cls="ts", size=11, ls=1.3)
        + f'<path fill="none" stroke="{T["zinc"]}" stroke-width="2" d="M522,226 H534"/>'
        + lbl(540, 230, "2.0 M — DESCRIBE REACH", cls="ts", size=11, ls=1.3)
        # the settings slider, lead severed before the service that ignores it
        + lbl(150, 372, "SETTINGS · ALERT DISTANCE — METRES, READ ALOUD", size=10, ls=1.1)
        + f'<path fill="none" stroke="{T["zinc"]}" stroke-width="2" '
          f'd="M150,398 H458 M211.6,392 V404 M273.2,392 V404 M396.4,392 V404"/>'
        + f'<circle cx="273.2" cy="398" r="7" fill="{T["rust"]}"/>'
        + lbl(211.6, 422, "0.5", cls="dim", size=10, ls=0.5, anchor="middle")
        + lbl(273.2, 422, "1.0", cls="dim", size=10, ls=0.5, anchor="middle")
        + lbl(396.4, 422, "2.0", cls="dim", size=10, ls=0.5, anchor="middle")
        + f'<path fill="none" stroke="{T["rust"]}" stroke-width="1.4" d="M273.2,405 V411 H293 V436 H544"/>'
        + f'<circle cx="551" cy="436" r="3.5" fill="none" stroke="{T["rust"]}" stroke-width="2"/>'
        + f'<rect x="590" y="415" width="160" height="42" rx="8" fill="none" '
          f'stroke="{T["rust"]}" stroke-width="1.6"/>'
        + lbl(602, 440, "LIDARSERVICE", cls="ts", size=11.5, ls=1.3)
        + sec_roman(150, 54, "VII — VISUALASSIST", 30)
        + sec_sub(150, 76, "it decides by distance when to speak — and when not to.", 14.5)
        + mark("visualassist", 150, 96, 48)
        + f'<rect x="150" y="470" width="4" height="16" fill="{T["rust"]}"/>'
        + f'<text x="164" y="483" class="dim" font-size="13">a slider labelled in metres, its value read aloud — bound to a threshold LiDARService never consults.</text>'
        + f'<text x="164" y="505" font-size="14.5">a live control that does nothing lies to the person the app is for.</text>'
    )
    return head(
        524,
        "VII · VisualAssist — 0.5 m buzzes and says Stop, 1.0 m pulses and says Caution, and 2.0 m is how far the manual Describe call reaches; the slider is bound to nothing",
        "VII · VisualAssist — the alert policy drawn to scale from the phone "
        "in your hand: inside 0.5 m a critical buzz and a spoken Stop, out to "
        "1.0 m a warning pulse and a spoken Caution, and past 1.0 m the "
        "automatic check does nothing at all — silence begins there, not at "
        "the widest ring. The 2.0 m arc is the reach of the manual Describe "
        "call: zones farther out are not mentioned. Below it, the settings "
        "slider the app actually shows — labelled in metres, its value read "
        "aloud — drawn with its lead ending open before LiDARService, the "
        "threshold it never consults. A live control that does nothing lies "
        "to the person the app is for. And a three-second announcement "
        "cooldown sits above the critical branch, so the Stop the code "
        "comments call always-announce can be swallowed for as long as that.",
        key="plate-7-visualassist.svg",
        col=SEC_COL, frame=VA_FRAME,
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
_CLAIMS_ROWS = json.loads((ROOT / "claims.json").read_text())["claims"]
CLAIMS_N = len(_CLAIMS_ROWS)
# Two of the rows do not derive from a pinned commit at all: they curl the
# LIVE deployment, which is the only way a claim about what is SERVED can be
# true. Drawing one number over both provenances told the reader every figure
# came from frozen history, and the two that matter most -- the bytes and the
# sha256 of the wasm a visitor actually downloads -- did not. Both counts are
# DERIVED here rather than typed, so adding a row moves the drawing.
CLAIMS_LIVE = sum(1 for _c in _CLAIMS_ROWS if "live" in _c)
CLAIMS_PINNED = CLAIMS_N - CLAIMS_LIVE


def plate_colophon() -> str:
    body = (
        bus("verd", "M63,0 V140", C=150, cd="M63,2.5 V136")
        + bus("rust", "M90,0 V140", C=30, cd="M90,2.5 V136")
        + bus("zinc", "M117,0 V140", C=100, cd="M117,2.5 V136")
        + f'<rect x="58" y="140" width="10" height="22" fill="{T["verd"]}"/>'
        + f'<rect x="85" y="140" width="10" height="22" fill="{T["rust"]}"/>'
        + f'<rect x="112" y="140" width="10" height="22" fill="{T["zinc"]}"/>'
        + f'<path class="bus" stroke="{T["zinc"]}" d="M48,166 L56,166 M48,166 L44,160 M852,166 L844,166 M852,166 L856,160 M56,166 H844"/>'
        + lbl(852, 120, f"{CLAIMS_N} CLAIMS · {CLAIMS_N} COMMANDS · RE-RUN IN CI · "
                      f"{CLAIMS_PINNED} PINNED · {CLAIMS_LIVE} LIVE",
              cls="ts mid", size=10.5, anchor="end")
        + lbl(852, 140, "what is my word rather than a derivation says so where it stands",
              cls="dim", size=10, ls=0.2, anchor="end")
    )
    return head(
        170,
        "colophon — the board's edge; every claim is a command",
        f"Colophon — the board's edge connector: the three buses land on "
        f"their pads and leave the page. {CLAIMS_N} claims, {CLAIMS_N} "
        f"commands: {CLAIMS_PINNED} re-run in CI from pinned commits and "
        f"{CLAIMS_LIVE} against the live deployment; what is my word "
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
# and behind the row's email port, which mobile readers get too.
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
#   * the LINK ROW has a real phone cut since 2026-08-13 (m-port-*): the
#     ports are percentage slices of a 440u artwork, so the row registers
#     with the plates around it at every width instead of wrapping. The
#     bundle crosses it at MBUS_X like every other plate here.
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
    plates run — above the 8u floor, in the safe direction (see above). The
    FIGURE is set a little left of 172 so its ink lands there (see fig_x): the
    worst case on this page is 0.979, whose 0 is set at 169.64 and still leaves
    9.6u to the spine — the caption lines, which set the block's edge, do not
    move at all. Caption leading is set by Syne's em box, not its ink: the 44px
    figure's box reaches ~13u below the baseline, so the first caption sits 32
    down.
    Mobile prose never uses &#8217; — the entity's own digits would enter
    the drawn ⊆ description check — the literal ’ is in TEXT_CHARS."""
    return (f'<text x="{fig_x(172, fig, 44, cap=12)}" y="140" class="d" font-size="44">{fig}</text>'
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
        + sec_roman(92, 54, "I — WORK", 24)
        + sec_sub(92, 74, "twelve months of production data work —", 13)
        + sec_sub(92, 90, "none of it public.", 13)
        + lbl(404, 30, "THE EXCEPTION — ATTESTED, NOT DERIVED", size=10.5, anchor="end")
        + f'<text x="{fig_x(92, "57.8M", 44, cap=12)}" y="224" class="d" font-size="44">57.8M</text>'
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
        + sec_roman(92, 54, "II — JETPACK", 24)
        + sec_sub(92, 76, "is hand-vectorised code actually faster?", 13)
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


# ── III · glyph, phone cut. The same argument, one column wide: NEON fed and
# collected, the two written-but-unbuilt families printed as unpopulated
# footprints under it, leads open. The load-bearing ratio survives the cut —
# 2/4/8 pads for 128/256/512-bit registers — because the pads are emitted by
# the same helper the desktop uses, so a family cannot lose a lane on the
# phone alone. The plate is 22u taller than it was: that is the silkscreen
# line the footprints need, and it is the only thing that moved below them.
# The admission still runs longest: this section owes the same three
# sentences at every width.
def m_glyph() -> str:
    body = (
        m_sec(730, (40, 130, 8), tap=("rust", 88))
        + mark("glyph", 92, 96, 48)
        + sec_roman(92, 54, "III — GLYPH", 24)
        + sec_sub(92, 76, "SIMD kernels over a net the course provided.", 13)
        + m_fig("3.5×", "benchDot/256 — OpenMP threads,",
                "same kernels · committed runs.")
        + bus("rust", "M140,120 H160 V240", C=30, cd="M144,120 H160 V237")
        + f'<circle cx="160" cy="240" r="2.6" fill="{T["rust"]}"/>'
        + bus("rust", "M160,240 H188", C=60, cd="M162.5,240 H185")
        + isa_slot(194, 213, 132, "NEON", 2, C=96)
        + f'<path fill="none" stroke="{T["zinc"]}" stroke-width="1.4" '
          f'd="M160,240 V366 M160,292 H169 M160,366 H169"/>'
        + f'<circle cx="160" cy="292" r="2.2" fill="{T["zinc"]}"/>'
        + f'<circle cx="175.5" cy="292" r="3.5" fill="none" stroke="{T["zinc"]}" stroke-width="2"/>'
        + f'<circle cx="175.5" cy="366" r="3.5" fill="none" stroke="{T["zinc"]}" stroke-width="2"/>'
        + isa_slot(194, 259, 132, "AVX2", 4)
        + isa_slot(194, 321, 132, "AVX-512", 8)
        + lbl(194, 418, "WRITTEN · NOT MEASURED", size=10, ls=1.1)
        # the collector runs OUTSIDE the slot column and enters the chip from
        # the side: at x=344 it dropped straight through the silkscreen line,
        # and a moving trace across type is a strikethrough (gate check 3).
        + bus("rust", "M332,240 H380 V452 H360", C=142, cd="M334,240 H380 V452 H363")
        + f'<rect x="200" y="434" width="160" height="36" rx="8" fill="none" '
          f'stroke="{T["rust"]}" stroke-width="1.6"/>'
        + lbl(212, 456, "BENCHDOT/256", cls="ts", size=11.5, ls=1.3)
        + bus("rust", "M280,470 V494", C=55, cd="M280,472.5 V489.5")
        + f'<rect x="200" y="494" width="196" height="36" rx="8" fill="none" '
          f'stroke="{T["zinc"]}" stroke-width="1.6"/>'
        + lbl(212, 516, "WASM_SIMD128 · 43,751 B", cls="ts", size=11.5, ls=1.3)
        + lbl(200, 552, "BYTE-IDENTICAL TO MAIN", size=10, ls=1.1)
        + lbl(200, 567, "CHECKED DAILY BY THIS PAGE", size=10, ls=1.1)
        + m_adm(586, "rust",
                ["the same flags lose 8 of 12 matrix-op",
                 "cases — worst, benchAxpy/128, 10.7× slower;"],
                ["memory-bandwidth-bound. axpy never pays",
                 "at any size measured; end-to-end,",
                 "threading buys nothing. and 97.01% is a",
                 "training-time number: the test set that",
                 "graded the net also picked its checkpoint."])
    )
    return head(
        730,
        "III · Glyph — one register-lane bundle to the benchmark, two unpopulated footprints, phone cut",
        "III · Glyph, phone cut — SIMD kernels over a course-provided MNIST "
        "net. Kernels are written for NEON, AVX2 and AVX-512, but the family "
        "is chosen at compile time, there is no runtime dispatch, and the "
        "reference machine is arm64 — so only the NEON bundle carries "
        "current, into benchDot/256: 3.5× from OpenMP threading over the "
        "same kernels, its own single-threaded build, from committed runs, "
        "dropping to the package that ships: WASM_SIMD128, 43,751 bytes, "
        "byte-identical to main, checked daily by this page's own CI. The "
        "AVX2 and AVX-512 slots are printed with their pads bare and their "
        "leads left open, silkscreened: written, not measured. "
        "The against-self results are printed: the same flags lose 8 of 12 "
        "matrix-op cases and buy nothing end-to-end — worst is "
        "benchAxpy/128, 10.7× slower, memory-bandwidth-bound, where axpy "
        "never pays at any size measured — and 97.01% is a training-time "
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
        + sec_roman(92, 54, "IV — AUTOML", 24)
        + sec_sub(92, 76, "a LangGraph agent, dealt its tools phase by phase.", 13)
        + m_fig("44", "tool schemas in llm/tools;",
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
        "IV · AutoML, phone cut — the tool library drawn as one registry "
        "strip: a 44-pin comb, one pin per tool schema, seven tool-set taps "
        "below it — no phase is handed all 44. The against-self line is the "
        "sandbox: it guards against accidents, not adversaries — the network "
        "is an env var the beta template renders as bridge, with no cap-drop, "
        "no pids-limit, no seccomp.",
        key="m-4-automl.svg",
        col=(88, 412), frame=(2.5, 35, 2.5), w=440,
    ) + css_close() + body + "</svg>"


# ── V · cadence, phone cut. The wall rotates with the flow: 36 stubs rain
# off a rail into the function's top edge, and the single output crosses a
# HORIZONTAL doored wall before the 7 tables. One comet runs entry to last
# table — the door is the only way through, and the drawing has exactly one
# current to prove it with.
def m_cadence() -> str:
    # centred on the function box (x=100, w=296) the way the desktop cut centres
    # its bank on its own box: the eye levels the stub mass against the box, not
    # the rail, and the first stub sits on the rail's corner rather than clear of it.
    stubs = " ".join(f"M{116 + i * 264 / 35:.1f},202 V216" for i in range(36))
    fan = " ".join(f"M248,{y} H264" for y in range(350, 495, 24))
    tables = "".join(f'<rect x="264" y="{y - 8}" width="132" height="16" rx="3" '
                     f'fill="none" stroke="{T["zinc"]}" stroke-width="1.3"/>'
                     for y in range(350, 495, 24))
    body = (
        m_sec(640, (12, 175, 90), tap=("verd", 30))
        + mark("cadence", 92, 96, 48)
        + sec_roman(92, 54, "V — CADENCE", 24)
        + sec_sub(92, 76, "every route, one function; RLS on every tenant row.", 13)
        + m_fig("36", "route handlers, one function;",
                "RLS FORCEd on all 7 tables.")
        + bus("verd", "M116,144 V202 H380", C=132, cd="M116,148 V202 H376")
        + f'<path fill="none" stroke="{T["verd"]}" stroke-width="1.4" d="{stubs}"/>'
        + f'<rect x="100" y="216" width="296" height="60" rx="8" fill="none" '
          f'stroke="{T["verd"]}" stroke-width="1.6"/>'
        + lbl(112, 242, "ONE SERVERLESS FUNCTION", cls="ts", size=11.5, ls=1.3)
        + lbl(112, 260, "36 ROUTE HANDLERS", cls="ts dim", size=10, ls=1.1)
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
        "V · Cadence, phone cut — 36 route handlers rain into one serverless "
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
        + sec_roman(92, 54, "VI — APPLIED", 24)
        + sec_sub(92, 76, "an inbox read by rules that keep score.", 13)
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
        + lbl(104, 309, "THE FULL CASCADE", cls="ts dim", size=10, ls=1.1)
        + lbl(92, 344, "SCORED LOWER", size=10, ls=1.1)
        + lbl(92, 360, "THAN THE RULES LAYER", size=10, ls=1.1)
        + f'<rect x="92" y="380" width="304" height="102" rx="6" fill="none" '
          f'stroke="{T["zinc"]}" stroke-width="1.3"/>'
        + row(390, 21) + row(420, 8) + row(450, None)
        + lbl(92, 502, "96 LABELLED MESSAGES · 2 CALLED WRONG", size=10, ls=1.1)
        + m_adm(528, "verd",
                ["the full cascade scored 0.9583 —",
                 "lower than the rules layer alone."],
                ["a tracker line records it. what is deployed",
                 "runs only that first layer."])
    )
    return head(
        610,
        "VI · Applied — the graded strip, phone cut",
        "VI · Applied, phone cut — the mail triage as the part that ships: "
        "the rules layer grades a labelled strip of 96 messages and gets 2 "
        "wrong — 0.979 macro-F1, rules layer alone. Below it, drawn dashed "
        "with its lead left open — it is not what ships — is the full "
        "cascade, all three layers, and it scored lower: 0.9583, a number a "
        "tracker line records. What is deployed runs only that first layer.",
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
    # the one roman that runs to two lines. Both lines lead with 'V', so the
    # tspan carries the same correction as the element that owns it — a tspan
    # with its own x is a second pen origin, and leaving it at 92 would set the
    # section's own name one bearing right of its own title.
    rx = rom_x(92, "VII — VISUALASSIST", 24)
    body = (
        m_sec(650, (60, 145, 205))
        # the open stub: reaching for the zinc bus, not landing
        + f'<circle cx="76.5" cy="140" r="3.5" fill="none" stroke="{T["zinc"]}" stroke-width="2"/>'
        + f'<path class="bus" stroke="{T["zinc"]}" stroke-dasharray="3 6" d="M84,140 H90"/>'
        + f'<text x="{rx}" y="44" class="d" font-size="24" letter-spacing="0.5">VII —'
          f'<tspan x="{rx}" dy="26">VISUALASSIST</tspan></text>'
        + sec_sub(92, 92, "it decides by distance when to speak —", 13)
        + sec_sub(92, 108, "and when not to.", 13)
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
        + lbl(110, 330, "0.5 M — BUZZ + STOP", cls="ts", size=11, ls=1.3)
        + f'<path fill="none" stroke="{T["rust"]}" stroke-width="2" stroke-dasharray="4.5 4.8" d="M92,348 H104"/>'
        + lbl(110, 352, "1.0 M — PULSE + CAUTION", cls="ts", size=11, ls=1.3)
        + f'<path fill="none" stroke="{T["zinc"]}" stroke-width="2" d="M92,370 H104"/>'
        + lbl(110, 374, "2.0 M — DESCRIBE REACH", cls="ts", size=11, ls=1.3)
        # the settings slider, lead severed before the service that ignores it
        + lbl(92, 414, "SETTINGS · ALERT DISTANCE — METRES, READ ALOUD", size=10, ls=1.1)
        + f'<path fill="none" stroke="{T["zinc"]}" stroke-width="2" '
          f'd="M100,446 H400 M160,440 V452 M220,440 V452 M340,440 V452"/>'
        + f'<circle cx="220" cy="446" r="7" fill="{T["rust"]}"/>'
        + lbl(160, 470, "0.5", cls="dim", size=10, ls=0.5, anchor="middle")
        + lbl(220, 470, "1.0", cls="dim", size=10, ls=0.5, anchor="middle")
        + lbl(340, 470, "2.0", cls="dim", size=10, ls=0.5, anchor="middle")
        + f'<path fill="none" stroke="{T["rust"]}" stroke-width="1.4" d="M220,453 V459 H240 V499 H248"/>'
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
        "phone drawn on the plate: inside 0.5 m a critical buzz and a spoken "
        "Stop, out to 1.0 m a warning pulse and a spoken Caution, and past "
        "1.0 m the automatic check does nothing at all — silence begins "
        "there, not at the widest ring. The 2.0 m arc is the reach of the "
        "manual Describe call: zones farther out are not mentioned. Below it, "
        "the settings slider the app actually shows — labelled in metres, its "
        "value read aloud — its lead drawn ending open before LiDARService, "
        "the threshold it never consults. A live control that does nothing "
        "lies to the person the app is for. And a three-second announcement "
        "cooldown sits above the critical branch, so the Stop the code "
        "comments call always-announce can be swallowed for as long as that.",
        key="m-7-visualassist.svg",
        col=(88, 412), frame=(2.5, 35, 2.5), w=440,
    ) + css_close() + body + "</svg>"


# ── the return, phone cut. This plate used to re-enter the lanes at PADS —
# the honest drawing while the chip row wrapped at 440 and the lanes had no
# predictable x to survive it at. The row registers now, so the honest
# drawing is the simpler one: the bundle continues at MBUS_X, unbroken,
# exactly as the desktop return continues it at BUS_X.
def m_link_return() -> str:
    body = (
        _dbus("verd", "M40,0 V72", 30, "M40,2.5 V69.5")
        + _dbus("rust", "M54,0 V72", 150, "M54,2.5 V69.5")
        + _dbus("zinc", "M68,0 V72", 100, "M68,2.5 V69.5")
        + lbl(404, 46, "THE EVIDENCE · SECTIONS II — VII", size=10.5, anchor="end")
    )
    return head(
        72,
        "the page bus continues past the link ports — phone cut",
        "The three page buses continue past the link ports, whole, into the "
        "evidence — sections two to seven.",
        key="m-link-return.svg",
        col=(88, 412), frame=MRET_FRAME, w=440,
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
        + lbl(404, 58, f"RE-RUN IN CI · {CLAIMS_PINNED} PINNED · {CLAIMS_LIVE} LIVE",
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
        f"{CLAIMS_N} commands: {CLAIMS_PINNED} from pinned commits and "
        f"{CLAIMS_LIVE} against the live deployment; what is my word "
        f"rather than a derivation says so where it stands.",
        key="m-colophon.svg",
        col=(28, 414), frame=(0, 27, 22), w=440,
        faces="T6",
    ) + css_close() + body + "</svg>"


# ══════════════════════════════════════ the intervals — the section service
#
# Every `---` rule the README carried cost ~104px of dead run and drew
# Primer's grey — the one ink on the page from nobody's palette. The
# interval is now drawn in the board's own grammar: each section's links
# become TEST POINTS tapped off that section's own lane (the only way to
# recolour a link GitHub gives this page is to draw it), the three buses
# DIVE at via pads where they meet the prose band, and RESURFACE above the
# next plate. Registration is by construction, not calibration: a strip is
# ONE 900u artwork cut into slices on integer-percent boundaries, each slice
# served at exactly that percent of the column, so every slice scales by the
# same factor as the plates around it and the lanes land on the same x at
# EVERY column width. (The link row above ships the same construction since
# the connector-row change, 2026-08-13 — no fixed-px image survives.)
#
# Slices are STANDALONE plates, not viewBox windows of a shared file: every
# published plate faces the whole gate (canvas, column, frame, faces,
# motion), and a windowed cut would hold ink outside its own canvas. So
# nothing but the rail may cross a cut, rail segments continue across slices
# by phase arithmetic (a sub-path starting s units along the rail carries
# C - s), and text never straddles a boundary. Short runs go dead under
# motion.mjs's carrier floor with one comet train per PAT, so every rail and
# every dive/resurface lane carries TWO, spaced PAT/2: train (84u) +
# shortest window (22u) exceeds the 105u spacing, so the current never
# leaves the wire.
SEC_H = 108                       # strip height, desktop
M_SEC_H = 104                     # strip height, phone cut
RAIL_Y, TP_Y = 36, 64             # the tap rail and the probe row
M_RAIL_Y, M_TP_Y = 24, 48
# slice widths as integer percents of the column; boundaries in board units.
# s1 is wide because it carries the dive (vias + TO INNER LAYER) beside the
# lanes; a strip needs only the slices its section has links for, and a row
# that sums under 100% simply ends — a transparent plate over the canvas and
# no plate at all render identically.
SEC_CUTS = {1: 26, 2: 17, 3: 20, 4: 13, 5: 24}
SEC_X0 = {1: 0, 2: 234, 3: 387, 4: 567, 5: 684}          # 900 × cut sums
SEC_W = {k: SEC_CUTS[k] * 9 for k in SEC_CUTS}
TP_X = {1: 290, 2: 441, 3: 621, 4: 720}                  # probe x, global
M_SEC_X0 = {k: round(SEC_X0[k] * 440 / 900, 1) for k in SEC_X0}
M_SEC_W = {k: round(SEC_W[k] * 440 / 900, 1) for k in SEC_W}
M_TP_X = {1: 142, 2: 213, 3: 300, 4: 366}                # recomposed, not scaled
# the tap phases: C at the rail's global start (the junction on the lane)
FAM = {
    "rust": dict(busC=(100, 40, 170), railC=20),
    "zinc": dict(busC=(55, 150, 10), railC=65),
    "verd": dict(busC=(180, 90, 130), railC=45),
}


def _via(key: str, x: float, y: float, r: float = 5.0) -> str:
    """A via: annular ring, open barrel — the lane ends flush on the ring."""
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" '
            f'stroke="{T[key]}" stroke-width="2"/>')


def _tp(key: str, x: float, y: float, r: float = 5.5) -> str:
    """A test point: ring plus solid probe land — distinct from a via on
    purpose (a via has a drill; a probe pad is solid). One <g>: the land
    sits inside its own ring by composition, not collision."""
    return (f'<g><circle cx="{x}" cy="{y}" r="{r}" fill="none" '
            f'stroke="{T[key]}" stroke-width="2"/>'
            f'<circle cx="{x}" cy="{y}" r="2" fill="{T[key]}"/></g>')


def _dot(key: str, x: float, y: float, r: float = 2.6) -> str:
    """A junction dot: this tap is CONNECTED (the schematic convention)."""
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{T[key]}"/>'


def _rail(key: str, d: str, C: float, cd: str) -> str:
    """A rail segment: static track plus TWO comet trains per PAT."""
    return (f'<g><path class="bus" stroke="{T[key]}" d="{d}"/>'
            + comet(key, cd, C) + comet(key, cd, C - PAT / 2) + "</g>")


def _dbus(key: str, d: str, C: float, cd: str) -> str:
    """A dive/resurface lane: a run this short (~30u) needs both trains."""
    return _rail(key, d, C, cd)


def _tp_lbl(x: float, tp: str, label: str) -> str:
    return (lbl(x + 14, 52, tp, size=8.5, ls=1.2)
            + lbl(x + 14, 68, label, cls="ts", size=11.5, ls=1.3))


def _m_tp_lbl(x: float, label: str) -> str:
    return lbl(x, 66, label, cls="ts", size=10, ls=1, anchor="middle")


def _s1(fam: str) -> str:
    """Slice one: the three lanes dive at via pads, and the section's rail
    taps off its own lane at a junction dot."""
    bx, f = BUS_X[fam], FAM[fam]
    w = SEC_W[1]
    body = ""
    for k, C in zip(("verd", "rust", "zinc"), f["busC"]):
        x = BUS_X[k]
        body += (bus(k, f"M{x},0 V91", C=C, cd=f"M{x},2.5 V88.5")
                 + _via(k, x, 96))
    body += lbl(134, 99.5, "TO INNER LAYER", size=9, ls=1.1)
    body += _dot(fam, bx, RAIL_Y)
    body += _rail(fam, f"M{bx},{RAIL_Y} H{w}", f["railC"],
                  f"M{bx + 4},{RAIL_Y} H{w}")
    return body


def _mid(fam: str, n: int, tp: str, label: str) -> str:
    """A pass-through slice: the rail crosses whole; a stub drops to the
    probe at a junction dot."""
    f = FAM[fam]
    w, x = SEC_W[n], TP_X[n - 1] - SEC_X0[n]
    C = f["railC"] - (SEC_X0[n] - BUS_X[fam])
    return (_rail(fam, f"M0,{RAIL_Y} H{w}", C, f"M0,{RAIL_Y} H{w}")
            + _dot(fam, x, RAIL_Y)
            + f'<path class="bus" stroke="{T[fam]}" d="M{x},{RAIL_Y} V58"/>'
            + _tp(fam, x, TP_Y) + _tp_lbl(x, tp, label))


def _end(fam: str, n: int, tp: str, label: str) -> str:
    """The rail's last slice: it turns down into the final probe."""
    f = FAM[fam]
    x = TP_X[n - 1] - SEC_X0[n]
    C = f["railC"] - (SEC_X0[n] - BUS_X[fam])
    return (_rail(fam, f"M0,{RAIL_Y} H{x} V58", C, f"M0,{RAIL_Y} H{x} V55.5")
            + _tp(fam, x, TP_Y) + _tp_lbl(x, tp, label))


def _m_s1(fam: str) -> str:
    bx, f = MBUS_X[fam], FAM[fam]
    w = M_SEC_W[1]
    body = ""
    for k, C in zip(("verd", "rust", "zinc"), (30, 140, 80)):
        x = MBUS_X[k]
        body += (bus(k, f"M{x},0 V78", C=C, cd=f"M{x},2.5 V75.5")
                 + _via(k, x, 84, r=4))
    body += lbl(28, 99, "TO INNER LAYER", size=8.5, ls=0.8)
    body += _dot(fam, bx, M_RAIL_Y, r=2.4)
    body += _rail(fam, f"M{bx},{M_RAIL_Y} H{w}", 55, f"M{bx + 4},{M_RAIL_Y} H{w}")
    return body


def _m_mid(fam: str, n: int, label: str) -> str:
    w, x = M_SEC_W[n], M_TP_X[n - 1] - M_SEC_X0[n]
    C = 55 - (M_SEC_X0[n] - MBUS_X[fam])
    return (_rail(fam, f"M0,{M_RAIL_Y} H{w}", C, f"M0,{M_RAIL_Y} H{w}")
            + _dot(fam, x, M_RAIL_Y, r=2.4)
            + f'<path class="bus" stroke="{T[fam]}" d="M{x},{M_RAIL_Y} V43.5"/>'
            + _tp(fam, x, M_TP_Y, r=4.5) + _m_tp_lbl(x, label))


def _m_end(fam: str, n: int, label: str) -> str:
    x = M_TP_X[n - 1] - M_SEC_X0[n]
    C = 55 - (M_SEC_X0[n] - MBUS_X[fam])
    return (_rail(fam, f"M0,{M_RAIL_Y} H{x} V43.5", C, f"M0,{M_RAIL_Y} H{x} V41")
            + _tp(fam, x, M_TP_Y, r=4.5) + _m_tp_lbl(x, label))


def _probe_head(h: int, w: float, title: str, desc: str, key: str,
                frame) -> str:
    return head(h, title, desc, key=key, col=(0, w), frame=frame,
                faces="6", w=w)


# the VisualAssist strip: one fitted probe (the repo) and, in section I's
# idiom, the footprint the board expects and does not have — drawn dashed,
# its lead left open. The current still runs to the open end and dies there
# every loop, which is the drawing doing the section's arguing (plate I).
def _va_s2() -> str:
    x = TP_X[1] - SEC_X0[2]                              # 56
    C = FAM["rust"]["railC"] - (SEC_X0[2] - BUS_X["rust"])
    return (_rail("rust", f"M0,{RAIL_Y} H{x} V58", C, f"M0,{RAIL_Y} H{x} V55.5")
            + _dot("rust", x, RAIL_Y)
            + _rail("rust", f"M{x},{RAIL_Y} H{SEC_W[2]}", 115,
                    f"M{x},{RAIL_Y} H{SEC_W[2]}")
            + _tp("rust", x, TP_Y) + _tp_lbl(x, "TP1", "REPO"))


def _va_s3() -> str:
    w = SEC_W[3]
    x = TP_X[2] - SEC_X0[3]                              # 54
    return (_rail("rust", f"M0,{RAIL_Y} H42", 115 - (SEC_W[2] - 56),
                  f"M0,{RAIL_Y} H39")
            + f'<g><circle cx="{x}" cy="{TP_Y}" r="5.5" fill="none" '
            f'stroke="{T["rust"]}" stroke-width="2" stroke-dasharray="5 4"/></g>'
            + lbl(x + 14, 52, "TP2", size=8.5, ls=1.2)
            + lbl(x + 14, 68, "NOT FITTED", size=11.5, ls=1.3))


def _m_va_s2() -> str:
    x = M_TP_X[1] - M_SEC_X0[2]                          # 27.6
    C = 55 - (M_SEC_X0[2] - MBUS_X["rust"])
    return (_rail("rust", f"M0,{M_RAIL_Y} H{x} V43.5", C,
                  f"M0,{M_RAIL_Y} H{x} V41")
            + _dot("rust", x, M_RAIL_Y, r=2.4)
            + _rail("rust", f"M{x},{M_RAIL_Y} H{M_SEC_W[2]}", 115,
                    f"M{x},{M_RAIL_Y} H{M_SEC_W[2]}")
            + _tp("rust", x, M_TP_Y, r=4.5) + _m_tp_lbl(x, "REPO"))


def _m_va_s3() -> str:
    x = 233 - M_SEC_X0[3]                                # 43.8
    return (_rail("rust", f"M0,{M_RAIL_Y} H30", 115 - (M_SEC_W[2] - 27.6),
                  f"M0,{M_RAIL_Y} H27")
            + f'<g><circle cx="{x}" cy="{M_TP_Y}" r="4.5" fill="none" '
            f'stroke="{T["rust"]}" stroke-width="2" stroke-dasharray="5 4"/></g>'
            + lbl(x, 66, "NOT FITTED", size=10, ls=1, anchor="middle"))


# ── the dive and the resurface, full-width. The dive also carries the
# page's one legend for the whole idiom, beside the return plate's own
# wayfinding line: the reader meets both at the threshold of the evidence.
DIVE_H, M_DIVE_H = 44, 36


def plate_dive() -> str:
    body = ""
    for k, C in (("verd", 10), ("rust", 120), ("zinc", 60)):
        x = BUS_X[k]
        body += (_dbus(k, f"M{x},0 V29", C, f"M{x},2.5 V26.5")
                 + _via(k, x, 34))
    body += (lbl(134, 37.5, "TO INNER LAYER", size=9, ls=1.1)
             + lbl(886, 37.5, "TEST POINTS — PROBE THE CLAIM", size=10,
                   anchor="end"))
    return head(
        DIVE_H,
        "the buses dive beneath the prose",
        "The three page buses dive to an inner layer at via pads and run "
        "beneath the prose; the silkscreen legend says what the drawn links "
        "are: test points — probe the claim.",
        key="plate-dive.svg", col=(44, 886), frame=DIVE_FRAME, faces="6",
    ) + css_close() + body + "</svg>"


def m_dive() -> str:
    body = ""
    for k, C in (("verd", 10), ("rust", 120), ("zinc", 60)):
        x = MBUS_X[k]
        body += (_dbus(k, f"M{x},0 V23", C, f"M{x},2.5 V20.5")
                 + _via(k, x, 27, r=4))
    body += (lbl(82, 30.5, "TO INNER LAYER", size=8.5, ls=0.8)
             + lbl(404, 30.5, "TEST POINTS — PROBE THE CLAIM", size=8.5,
                   ls=0.8, anchor="end"))
    return head(
        M_DIVE_H,
        "the buses dive beneath the prose, phone cut",
        "The three page buses dive to an inner layer at via pads and run "
        "beneath the prose; the silkscreen legend says what the drawn links "
        "are: test points — probe the claim.",
        key="m-dive.svg", col=(28, 414), frame=M_DIVE_FRAME, faces="6", w=440,
    ) + css_close() + body + "</svg>"


def plate_resurface() -> str:
    body = ""
    for k, C in (("verd", 150), ("rust", 30), ("zinc", 100)):
        x = BUS_X[k]
        body += (_via(k, x, 9)
                 + _dbus(k, f"M{x},14 V44", C, f"M{x},16.5 V41.5"))
    body += lbl(134, 12.5, "FROM INNER LAYER", size=9, ls=1.1)
    return head(
        DIVE_H,
        "the buses resurface",
        "The three buses resurface from the inner layer at their via pads "
        "and enter the next plate.",
        key="plate-resurface.svg", col=(44, 886), frame=RESURF_FRAME,
        faces="6",
    ) + css_close() + body + "</svg>"


def m_resurface() -> str:
    body = ""
    for k, C in (("verd", 150), ("rust", 30), ("zinc", 100)):
        x = MBUS_X[k]
        body += (_via(k, x, 8, r=4)
                 + _dbus(k, f"M{x},12 V36", C, f"M{x},14.5 V33.5"))
    body += lbl(82, 11.5, "FROM INNER LAYER", size=8.5, ls=0.8)
    return head(
        M_DIVE_H,
        "the buses resurface, phone cut",
        "The three buses resurface from the inner layer at their via pads "
        "and enter the next plate.",
        key="m-resurface.svg", col=(28, 414), frame=M_RESURF_FRAME,
        faces="6", w=440,
    ) + css_close() + body + "</svg>"


# ── descriptions, authored once; the same words serve both cuts.
_D_S1 = ("The three page buses dive to an inner layer at via pads beneath "
         "the prose, and the section's test-point rail taps off the %s lane.")
_D_S2 = "Test point one — probe the section live, in the browser."
_D_S3 = ("Test point two — the system card, a print-format walkthrough of "
         "the architecture and the evidence.")
# AutoML is the one system on this page whose card is written but not
# deployed, so its probe lands on the card's SOURCE. The row that claims
# "four of them ship a system card" enumerates Glyph, jetpack, Cadence and
# Applied by name — AutoML was never in that four, and the probe used to
# point at a URL that 404s, which is the page asserting a fifth.
_D_S3_ZINC = ("Test point two — the system card's source. AutoML is the one "
              "system here whose card is written but not deployed.")
_S3_DESC = {"rust": _D_S3, "verd": _D_S3, "zinc": _D_S3_ZINC}
_S3_TITLE = {"rust": "the system card", "verd": "the system card",
             "zinc": "the system card's source"}
# 11 characters either way, so the silkscreen budget is unchanged.
_S3_LABEL = {"rust": "SYSTEM CARD", "verd": "SYSTEM CARD", "zinc": "CARD SOURCE"}
_S3_M_LABEL = {"rust": "CARD", "verd": "CARD", "zinc": "SOURCE"}
_D_S4 = "Test point three — the source repository."
_D_C5 = ("Test point four — the row-level-security isolation suite, run "
         "against real Postgres.")
_D_A5 = "Test point four — the in-browser demo of the mail classifier."
_D_V2 = "Test point one — the source repository, the one probe this section has."
_D_V3 = ("The next test point is an unpopulated footprint, drawn dashed with "
         "its lead open — there is no live deployment to probe; VisualAssist "
         "needs an iPhone with LiDAR in your hand.")
_LANE = {"rust": "rust", "zinc": "zinc", "verd": "verdigris"}


def _probe(fn: str, h: int, w: float, title: str, desc: str, body_fn):
    def gen():
        # THE BODY RUNS FIRST, and that is the whole of this function.
        # css_close() DRAINS the shared `_CSS` accumulator, so a plate's
        # keyframes reach its own file only if the calls that append to _CSS
        # have already happened. `head + css_close() + body_fn()` reads left
        # to right in Python exactly as it does in the output, and the output
        # order is the reverse of the evaluation order this needs: every one
        # of these 64 slices shipped the PREVIOUSLY emitted slice's keyframes
        # and 516 class references to keyframes that were in another file.
        # Every other generator in this file already binds `body` to a local
        # on the line above its `return`; this one inlined the call and lost
        # the ordering with it. Keep the binding.
        body = body_fn()
        return (_probe_head(h, w, title, desc, fn, PROBE_FRAME.get(fn))
                + css_close() + body + "</svg>")
    return gen


INTERVAL_PLATES: dict = {}
INTERVAL_MOBILE: dict = {}
for _f in ("rust", "zinc", "verd"):
    _fam = _f
    INTERVAL_PLATES[f"plate-probe-{_f}-s1.svg"] = _probe(
        f"plate-probe-{_f}-s1.svg", SEC_H, SEC_W[1],
        "the buses dive; the section rail taps off its lane",
        _D_S1 % _LANE[_f], (lambda ff: lambda: _s1(ff))(_fam))
    INTERVAL_MOBILE[f"m-probe-{_f}-s1.svg"] = _probe(
        f"m-probe-{_f}-s1.svg", M_SEC_H, M_SEC_W[1],
        "the buses dive; the section rail taps off its lane, phone cut",
        _D_S1 % _LANE[_f], (lambda ff: lambda: _m_s1(ff))(_fam))
    INTERVAL_PLATES[f"plate-probe-{_f}-s2.svg"] = _probe(
        f"plate-probe-{_f}-s2.svg", SEC_H, SEC_W[2],
        "test point one — live", _D_S2,
        (lambda ff: lambda: _mid(ff, 2, "TP1", "LIVE"))(_fam))
    INTERVAL_MOBILE[f"m-probe-{_f}-s2.svg"] = _probe(
        f"m-probe-{_f}-s2.svg", M_SEC_H, M_SEC_W[2],
        "test point one — live, phone cut", _D_S2,
        (lambda ff: lambda: _m_mid(ff, 2, "LIVE"))(_fam))
    INTERVAL_PLATES[f"plate-probe-{_f}-s3.svg"] = _probe(
        f"plate-probe-{_f}-s3.svg", SEC_H, SEC_W[3],
        f"test point two — {_S3_TITLE[_f]}", _S3_DESC[_f],
        (lambda ff: lambda: _mid(ff, 3, "TP2", _S3_LABEL[ff]))(_fam))
    INTERVAL_MOBILE[f"m-probe-{_f}-s3.svg"] = _probe(
        f"m-probe-{_f}-s3.svg", M_SEC_H, M_SEC_W[3],
        f"test point two — {_S3_TITLE[_f]}, phone cut", _S3_DESC[_f],
        (lambda ff: lambda: _m_mid(ff, 3, _S3_M_LABEL[ff]))(_fam))
for _f in ("rust", "zinc"):
    _fam = _f
    INTERVAL_PLATES[f"plate-probe-{_f}-s4.svg"] = _probe(
        f"plate-probe-{_f}-s4.svg", SEC_H, SEC_W[4],
        "test point three — the repository", _D_S4,
        (lambda ff: lambda: _end(ff, 4, "TP3", "REPO"))(_fam))
    INTERVAL_MOBILE[f"m-probe-{_f}-s4.svg"] = _probe(
        f"m-probe-{_f}-s4.svg", M_SEC_H, M_SEC_W[4],
        "test point three — the repository, phone cut", _D_S4,
        (lambda ff: lambda: _m_end(ff, 4, "REPO"))(_fam))
INTERVAL_PLATES["plate-probe-verd-s4.svg"] = _probe(
    "plate-probe-verd-s4.svg", SEC_H, SEC_W[4],
    "test point three — the repository", _D_S4,
    lambda: _mid("verd", 4, "TP3", "REPO"))
INTERVAL_MOBILE["m-probe-verd-s4.svg"] = _probe(
    "m-probe-verd-s4.svg", M_SEC_H, M_SEC_W[4],
    "test point three — the repository, phone cut", _D_S4,
    lambda: _m_mid("verd", 4, "REPO"))
INTERVAL_PLATES["plate-probe-cadence-s5.svg"] = _probe(
    "plate-probe-cadence-s5.svg", SEC_H, SEC_W[5],
    "test point four — the isolation suite", _D_C5,
    lambda: _end("verd", 5, "TP4", "THE ISOLATION SUITE"))
INTERVAL_MOBILE["m-probe-cadence-s5.svg"] = _probe(
    "m-probe-cadence-s5.svg", M_SEC_H, M_SEC_W[5],
    "test point four — the isolation suite, phone cut", _D_C5,
    lambda: _m_end("verd", 5, "RLS SUITE"))
INTERVAL_PLATES["plate-probe-applied-s5.svg"] = _probe(
    "plate-probe-applied-s5.svg", SEC_H, SEC_W[5],
    "test point four — the in-browser demo", _D_A5,
    lambda: _end("verd", 5, "TP4", "IN-BROWSER DEMO"))
INTERVAL_MOBILE["m-probe-applied-s5.svg"] = _probe(
    "m-probe-applied-s5.svg", M_SEC_H, M_SEC_W[5],
    "test point four — the in-browser demo, phone cut", _D_A5,
    lambda: _m_end("verd", 5, "DEMO"))
INTERVAL_PLATES["plate-probe-va-s2.svg"] = _probe(
    "plate-probe-va-s2.svg", SEC_H, SEC_W[2],
    "test point one — the repository", _D_V2, _va_s2)
INTERVAL_MOBILE["m-probe-va-s2.svg"] = _probe(
    "m-probe-va-s2.svg", M_SEC_H, M_SEC_W[2],
    "test point one — the repository, phone cut", _D_V2, _m_va_s2)
INTERVAL_PLATES["plate-probe-va-s3.svg"] = _probe(
    "plate-probe-va-s3.svg", SEC_H, SEC_W[3],
    "the footprint the board expects, not fitted", _D_V3, _va_s3)
INTERVAL_MOBILE["m-probe-va-s3.svg"] = _probe(
    "m-probe-va-s3.svg", M_SEC_H, M_SEC_W[3],
    "the footprint the board expects, not fitted, phone cut", _D_V3, _m_va_s3)

# ── declared frames (top, rightGap, bottomGap), baked from gate.mjs
# measurement on this machine; tolerance 4 absorbs the CI ascent skew.
#
# Three rightGaps moved with the figure fix (2026-08-13) and were re-baked from
# what check 12 measured, which is the one direction this is allowed to go: the
# declaration follows the drawing. Tabular figures are one width, and on these
# three plates the claim figure IS the rightmost ink, so the plate's right edge
# moved when the digits stopped being proportional. "0.979" is the largest:
# 0+9+7+9 advanced 4889/1000 em as text figures and 4582 as tabular, 19u
# narrower at 62px, and APPLIED_FRAME went 37 -> 59.3 to say so. Nothing was
# nudged to make a number fit; the numbers were re-read after the type changed.
HERO_FRAME = (30, 37.7, 0)
JET_FRAME = (2.5, 64.7, 2.5)
WORK_FRAME = (2.5, 35.7, 2.5)
GLYPH_FRAME = (2.5, 35.5, 2.5)
AUTOML_FRAME = (2.5, 60.8, 2.5)
CADENCE_FRAME = (2.5, 51.7, 2.5)
APPLIED_FRAME = (2.5, 59.3, 2.5)
VA_FRAME = (2.5, 150, 2.5)
COLO_FRAME = (2.5, 48, 4)
MOB_FRAME = (36, 58, 0)
# The return plates' frames, measured 2026-08-13 (dark and light identical).
# check 12 excludes a full-height TRACK by construction (a >=H-2 tall, <=5u
# wide element is the trace, not content), but a lane's COMET is inset 2.5u
# at each end and so falls back INTO the measurement — which is honest: the
# 2.5s below are the comets' authored insets, not accidents.
RET_FRAME = (2.5, 47.2, 2.5)
MRET_FRAME = (2.5, 36.8, 2.5)
# The row slices' frames, same provenance. Slice one's edges are its lane
# comets (see the note above); the tap slices' top edge is the zinc rail
# crossing at its tier, their right edge is that same rail running to the
# cut (0 — the current continues into the next slice by construction), and
# J4's high-set package is why slice four's first ink sits above its rail.
PORT_FRAME: dict[str, tuple[float, float, float]] = {
    "plate-port-portfolio.svg": (2.5, 0, 2.5),
    "plate-port-resume.svg": (16, 0, 24),
    "plate-port-linkedin.svg": (16, 0, 24),
    "plate-port-email.svg": (8, 20.5, 38),
    "m-port-portfolio.svg": (2.5, 0, 2.5),
    "m-port-resume.svg": (12, 0, 18),
    "m-port-linkedin.svg": (12, 0, 18),
    "m-port-email.svg": (6, 8.5, 30),
}
# the interval plates' frames, same provenance (gate.mjs measurement,
# 2026-08-13; dark and light measured identical). While a plate is being
# authored its entry may be absent: check 12 then fails it and prints the
# measured values, which is the sanctioned one-round-trip workflow. The
# resurface's huge rightGap is honest — its rightmost ink is the FROM INNER
# LAYER silkscreen; everything right of it is deliberately bare board.
DIVE_FRAME = (0, 14.8, 4.5)
M_DIVE_FRAME = (0, 36.6, 3.5)
RESURF_FRAME = (3.5, 662.1, 0)
M_RESURF_FRAME = (2.5, 263.7, 0)
PROBE_FRAME: dict[str, tuple[float, float, float]] = {
    "plate-probe-rust-s1.svg": (0, 0, 6.5),
    "plate-probe-zinc-s1.svg": (0, 0, 6.5),
    "plate-probe-verd-s1.svg": (0, 0, 6.5),
    "plate-probe-rust-s2.svg": (33.4, 0, 38),
    "plate-probe-zinc-s2.svg": (33.4, 0, 38),
    "plate-probe-verd-s2.svg": (33.4, 0, 38),
    "plate-probe-rust-s3.svg": (33.4, 0, 38),
    "plate-probe-zinc-s3.svg": (33.4, 0, 38),
    "plate-probe-verd-s3.svg": (33.4, 0, 38),
    "plate-probe-rust-s4.svg": (36, 12.4, 38),
    "plate-probe-zinc-s4.svg": (36, 12.4, 38),
    "plate-probe-verd-s4.svg": (33.4, 0, 38),
    "plate-probe-cadence-s5.svg": (36, 19, 38),
    "plate-probe-applied-s5.svg": (36, 34.5, 38),
    "plate-probe-va-s2.svg": (33.4, 0, 38),
    "plate-probe-va-s3.svg": (36, 31.7, 38),
    "m-probe-rust-s1.svg": (0, 0, 3),
    "m-probe-zinc-s1.svg": (0, 0, 3),
    "m-probe-verd-s1.svg": (0, 0, 3),
    "m-probe-rust-s2.svg": (21.6, 0, 36),
    "m-probe-zinc-s2.svg": (21.6, 0, 36),
    "m-probe-verd-s2.svg": (21.6, 0, 36),
    "m-probe-rust-s3.svg": (21.6, 0, 36),
    "m-probe-zinc-s3.svg": (21.6, 0, 36),
    "m-probe-verd-s3.svg": (21.6, 0, 36),
    "m-probe-rust-s4.svg": (24, 18.8, 36),
    "m-probe-zinc-s4.svg": (24, 18.8, 36),
    "m-probe-verd-s4.svg": (21.6, 0, 36),
    "m-probe-cadence-s5.svg": (24, 45.1, 36),
    "m-probe-applied-s5.svg": (24, 56.7, 36),
    "m-probe-va-s2.svg": (21.6, 0, 36),
    "m-probe-va-s3.svg": (24, 10.1, 36),
}

PLATES = {
    "plate-0-hero.svg": plate_hero,
    "plate-port-portfolio.svg": row_s1,
    "plate-port-resume.svg": row_s2,
    "plate-port-linkedin.svg": row_s3,
    "plate-port-email.svg": row_s4,
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
    "m-port-portfolio.svg": m_row_s1,
    "m-port-resume.svg": m_row_s2,
    "m-port-linkedin.svg": m_row_s3,
    "m-port-email.svg": m_row_s4,
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
# The interval set is generated AFTER the whole existing document, keyframe
# counter included: inserting it mid-sequence would rename every k-class in
# every file downstream of the insertion and rewrite 40 unchanged artworks.
INTERVALS = {
    "plate-dive.svg": plate_dive,
    "plate-resurface.svg": plate_resurface,
    **INTERVAL_PLATES,
    "m-dive.svg": m_dive,
    "m-resurface.svg": m_resurface,
    **INTERVAL_MOBILE,
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


def _check_css_refs(fn: str, svg: str) -> None:
    """A plate must be closed over its own stylesheet, in BOTH directions.

    `_CSS` is a shared mutable accumulator drained by css_close(), and the
    only thing keeping a plate's keyframes in the plate's own file is that
    every generator computes its BODY before it calls css_close(). One
    generator did not (`_probe`, whose `head + css_close() + body_fn()` reads
    left to right and so drained the accumulator before the body had filled
    it), and 64 of 120 published plates shipped with 516 class references to
    keyframes that had gone into the PREVIOUS file — every animation on every
    interval slice dead, and the whole set green. Nothing downstream saw it:
    a dangling class is not a parse error, not a collision, and not a missing
    face, and gate.mjs's dead-animation check was guarded on a duration that
    is zero for exactly this defect.

    So it is asserted here, at the point of emission, over the FILE:

      · every class an element carries must be selected by some rule in this
        plate's own stylesheet — a reference that resolves to nothing;
      · every keyframes block must be named by some rule, and every rule that
        names one must exist — an animation with no motion behind it;
      · every rule that DECLARES an animation must be carried by an element —
        the same leak seen from the other side, where the residue lands in
        the next file and ships base64 keyframes to a reader that animate
        nothing (assets/light/plate-0-hero.svg carried six of these).

    Shape, not literal: nothing here knows that the generated names look like
    `k463`, so a redesign is free to rename or renumber them. Both themes are
    checked — half the broken files were the light twins, and the coverage
    check above is theme-guarded only because TEXT is theme-invariant.
    """
    _style = "".join(_re.findall(r'<style>(.*?)</style>', svg, _re.S))
    # the embedded faces are the biggest thing in the file and the only place
    # a punctuation-heavy blob could impersonate a selector
    _style = _re.sub(r'base64,[A-Za-z0-9+/=]+', 'base64,', _style)
    body = _re.sub(r'<style>.*?</style>', '', svg, flags=_re.S)
    used = {t for m in _re.findall(r'class="([^"]*)"', body) for t in m.split()}
    # a class token in selector position: `.name` where name starts a word
    defined = set(_re.findall(r'\.([A-Za-z_][\w-]*)', _style))
    kfs = set(_re.findall(r'@keyframes ([\w-]+)', _style))
    named = {n for n in _re.findall(r'animation(?:-name)?:\s*([\w-]+)', _style)
             if n != "none"}
    # the classes whose rule declares an animation
    animated = {m for m in _re.findall(r'\.([A-Za-z_][\w-]*)\{[^}]*animation:', _style)}
    for c in sorted(used - defined):
        _fail.append(f"{fn}: an element carries class {c!r}, which no rule in this "
                     f"plate's own <style> defines — the reference resolves to "
                     f"nothing and whatever it was meant to do does not happen")
    for k in sorted(kfs - named):
        _fail.append(f"{fn}: defines @keyframes {k!r} that no rule names — "
                     f"dead payload on every reader's compositor")
    for n in sorted(named - kfs):
        _fail.append(f"{fn}: a rule declares animation {n!r} with no @keyframes "
                     f"{n!r} on this plate — the animation never runs")
    for c in sorted(animated - used):
        _fail.append(f"{fn}: rule .{c} declares an animation and no element on this "
                     f"plate carries that class — keyframes shipped to every "
                     f"reader that animate nothing")


# One build, two documents. Dark keeps every path it has always had; light
# lands in assets/light/ under the SAME basenames (gate.mjs keys on that).
for _theme in ("dark", "light"):
    set_theme(_theme)
    _out = OUT if _theme == "dark" else OUT / "light"
    _out.mkdir(exist_ok=True)
    # a plate this build no longer authors must not survive on disk: the
    # gates sweep the DIRECTORY, so a stale file is a stale claim surface
    for _stale in _out.glob("*.svg"):
        if not (_stale.name in PLATES or _stale.name in MOBILE or _stale.name in INTERVALS):
            _stale.unlink()
            print(f"{_theme:5s} {_stale.name}: removed (no longer authored)")
    for _fn, _gen in (PLATES | MOBILE | INTERVALS).items():
        _path = _out / _fn
        _path.write_text(_gen())
        try:
            _xml.parseString(_path.read_text())
        except Exception as e:
            _fail.append(f"{_theme}/{_fn}: MALFORMED XML — {e}")
        if _theme == "dark":                    # text is theme-invariant
            _check_coverage(_fn, _path.read_text())
        # NOT theme-guarded: the stylesheet is generated per theme and half
        # the dangling-class files were the light twins.
        _check_css_refs(f"{_theme}/{_fn}", _path.read_text())
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
    _want = {f"./assets/{_d}{_f}" for _f in set(PLATES) | set(MOBILE) | set(INTERVALS)
             for _d in ("", "light/")}
    # No exceptions since the connector-row change: every authored file —
    # the row slices included — is served in both themes, so both directions
    # of this sweep run over the full set. (The old chips' light twins were
    # authored-but-unserved measurement harnesses, and the carve-out that
    # allowed that died with them.)
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
