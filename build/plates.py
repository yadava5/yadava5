#!/usr/bin/env python3
"""
FALSIFIABLE — figure builder.

Every claim is followed by the mechanism that would catch it if it were a lie.

Design rules encoded here (each one is a finding, not a preference):
  * THE STORY IS "QUESTIONS I WANTED ANSWERED". Round 21. The old arc — five
    sections opening "I don't trust X" — is deleted; the client called it
    cocky, and the same construction five times read as a form letter. Each
    section now opens as a genuine question answered with evidence, including
    the answers that went against the author (jetpack loses to the JDK
    intrinsic; Glyph's OpenMP build is SLOWER below a size floor; Applied's
    best score is the cheap layer's). The questions live in the README
    headers; the plates perform the answers.
  * PERPETUAL PERFORMANCE. Round 21, and it inverts round 19's doctrine in
    the same change as the design it measures. "Still by default" was a sound
    fix for gate-food decoration, but eight of ten plates took the permission
    and froze for 84-100% of their loops (raster-measured), and the client's
    verdict was "very static feel". The one plate he did not criticise was
    the only one at 100% — the transit rider in continuous travel. So that is
    the floor now: EVERY plate carries one slow continuous carrier (a scan, a
    stream, a conveyor, a nib, a needle, a sweep, a ring — a different verb
    per section, because ten copies of one verb is the templating the client
    already rejected), plus its episodic gesture. Carriers are steady-state,
    so linear is legal there and only there; gestures ease. build/motion.mjs
    enforces the doctrine in pixels.
  * LOOPS WRAP SEAMLESSLY. frame[first] == frame[last] for every keyframe
    set: carriers are closed circuits, sawtooths that fade before they reset,
    or conveyors whose blocks hand their pose to the next. Negative delays
    start everything mid-cycle, chosen so t=0 is a full-opacity frame (gate
    check 6 reads t=0, and it is right to). Periods inside a plate and across
    plates are near-coprime so the page never beats into a synchronised
    pulse and the composite loop is unfindable.
  * ONE MODULAR SCALE: 13 / 21 / 34 / 55 on the golden ratio (Fibonacci),
    with ONE named exception — the 89px "B only", the loudest thing on the
    page and not a number. Round 20 shipped seven sizes plus an off-scale
    inline 26 inside one 708-wide figure, and that is what "unpolished"
    measured as. All small text is exactly 13, differentiated by tracking
    and ink (lbl/key at +1.6, kick at +2.4), never by a fourth size. The
    serif voice sits on the scale at 34.
  * viewBox 880 wide; the type column is a per-plate declaration (data-col,
    gate check 5), edges are per-plate declarations (data-frame, check 12).
  * every figure is exactly as tall as its evidence.
  * nothing comes to rest on top of a label — enforced by gate.mjs, 40
    samples across every loop.
  * an element that MOVES fades out before its position resets; elements
    that only fade may reset in one frame.
  * no animated filters — one animated blur costs more than 4000 animated
    rects. No SMIL either: CSS is the only motion layer, so the
    prefers-reduced-motion block can park the whole page, and every gate
    (document.getAnimations + currentTime seeking) can see and steer it.
"""
from __future__ import annotations
import base64, json, math, pathlib, re

# ── the grid defaults. L/R are the DEFAULT type column; TOP is the
# first-baseline convention for plates that open with a header line.
L, R = 150, 730
TOP = 56

# ── the canvas window: viewBox starts at VB_X so the authored 150/730 column
# lands 64 from each edge, and the narrower canvas renders larger at GitHub's
# column width.
VB_X, VB_W = 86, 708

# every plate's description is authored ONCE here and flows to three places:
# the SVG <desc>, the SVG aria-label, and the README's <img alt>.
ALT: dict[str, str] = {}

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT.parent / "assets"
OUT.mkdir(exist_ok=True)

# ── the embedded faces (regenerate with build/subset-fonts.py, which says why
# there are three). The page claims to be self-contained, so every glyph it
# draws must come from a face it carries: a glyph missing from its subset
# falls back to a PLATFORM font silently — the comma in the 34px "10,453"
# shipped in Menlo on macOS and DejaVu Sans Mono on Linux, and the serif
# voice was a different typeface per reader. charsets.py is the single source
# of truth: subset-fonts.py builds the woff2s from it, and the build-time
# gate below fails any plate that draws a character its face does not carry.
from charsets import MONO_CHARS, BOLD_CHARS, SERIF_CHARS
FONT = base64.b64encode((ROOT / "mono-subset.woff2").read_bytes()).decode()
FONT600 = base64.b64encode((ROOT / "mono-600-subset.woff2").read_bytes()).decode()
FONTSERIF = base64.b64encode((ROOT / "serif-subset.woff2").read_bytes()).decode()

# The real product marks, extracted from each app's own logo (see logos.json).
import re as _re_mod
_re_op = _re_mod.compile(r'(stroke|fill)-opacity="([0-9.]+)"')
LOGOS = json.loads((ROOT / "logos.json").read_text())


def logo(name: str, x: float, y: float, size: float, colour: str) -> str:
    """One product mark, drawn at `size` in `colour`.

    The 0.8 floor on stroke/fill-opacity is enforced here rather than patched
    into logos.json: tonal hierarchy inside a mark does not survive 28u, and
    two of the six marks shipped at 1.49:1 and 2.68:1 before this existed.
    """
    m = LOGOS[name]
    k = size / m["size"]
    body = _re_op.sub(
        lambda g: f'{g.group(1)}-opacity="{max(float(g.group(2)), 0.8):.2f}"', m["body"])
    return (f'<g transform="translate({x},{y}) scale({k:.4f})" '
            f'style="color:{colour}">{body}</g>')

W = 880

# ── the two palettes. THE PLATES OWN THEIR GROUND.
#
# Until 2026-08-08 the figures were transparent and every colour was measured
# against GitHub's canvas (#0d1117 / #ffffff) — which meant the single most
# identity-carrying decision a page makes was RENTED. It also meant this page
# and the portfolio it belongs to were two different designs: cold blue-greys
# and six saturated accents here, warm paper and one ink family there. A
# reader clicking between them met two different people.
#
# So the first <rect> is now opaque paper, and these are the Daylight Study's
# own tokens on their own grounds: #f2e4c9 (day) and #43372f (night), the two
# waypoints Portfolio-2.0 measures its inks against. Every ratio below was
# recomputed on this paper with the portfolio's own instrument
# (Portfolio-2.0/scripts/qa/check-palette.mjs:86-101 — the same WCAG 2.x
# formula gate.mjs:544-545 runs here) and reproduced 19/19.
#
# THE SIX-ACCENT BRAND SYSTEM IS RETIRED. Hue-per-project taught a lookup
# table that paid off nowhere: EXPLORATION.md's own test is "identify a
# section from a 200px crop with the words blurred", and what passes it is
# the ARMATURE — ledger, bench sheet, copybook, dial, disclosure, channel,
# sweep — not the hue. Two accents replace six, and they carry a semantic
# rather than an index: CLAY is my act (the thing I built, the claim), PINE
# is the check (the reference that stands, the gate, the database's refusal).
#
# Floors gate.mjs enforces (gate.mjs:603): 4.5:1 text, 3.0:1 non-text.
# NO UNMEASURED ALPHA, AND NO ALPHA UNDER ITS FLOOR. A rest-state alpha may
# ship only with its per-theme composited hex and ratio in the comment beside
# it — the page's two hair tokens (1.36 and 2.01 on day paper) and half-ink
# used as text (3.82, under the 4.5 text floor) are retired for failing that.
THEMES = {
    "dark": dict(                # night paper — the settled field
        GROUND="#43372f",   # the sheet itself; 1.65:1 against GitHub's dark canvas,
                            #   which is why every plate also draws a WIRE frame
        RULE="#948a80",     # 3.40:1 — hairlines, baselines, row rules
        WIRE="#a59b90",     # 4.21:1 — frames, brackets, boundaries, the sheet edge
        ROW="#948a80",      # 3.40:1 — tenant row fills
        REDACT="#2e2620",   # 1.29:1 — THE VOID. Legal only through the stroke
                            #   escape at gate.mjs:566-572, so redact() bakes a
                            #   mandatory WIRE edge in; never draw a bare bar.
        INK="#f6efe2", INK2="#d9d0c3", INK3="#c9c0b2",   # 10.06 / 7.54 / 6.39:1
        CLAY="#f4b090",     # 6.28:1 — accent TEXT, the stamp
        CLAY_G="#e08a5f",   # 4.36:1 — accent graphics: bars, scans, cones
        PINE="#aecfc0",     # 6.84:1 — the check. Text-grade on both papers.
    ),
    "light": dict(               # day paper — the golden waypoint
        GROUND="#f2e4c9",   # 1.26:1 against GitHub's white: a tint, not an object,
                            #   until the WIRE frame makes it a sheet
        RULE="#877e6d",     # 3.19:1
        WIRE="#746c5c",     # 4.14:1
        ROW="#877e6d",      # 3.19:1
        REDACT="#26231c",   # 12.48:1 — on paper a redaction is black ink; it takes
                            #   the same WIRE edge so the markup stays symmetric
        INK="#26231c", INK2="#5c564a", INK3="#6a6355",   # 12.48 / 5.79 / 4.74:1
        CLAY="#a03f20",     # 5.18:1
        CLAY_G="#c4532e",   # 3.62:1
        PINE="#2f5d50",     # 5.96:1
    ),
}
# Ember (#f57a3e) stays home: 2.16:1 on day paper. The portfolio reserves it
# for one stamp on its own dark plates; it never boards these. CHIP is gone —
# it had zero users in any shipped plate.

THEME = "dark"


def set_theme(name: str) -> None:
    """Point every colour global at one palette."""
    globals().update(THEMES[name])
    globals()["THEME"] = name
    t = THEMES[name]
    # The six project hues are gone, so the legend is no longer a colour key —
    # it is a list of marks. They draw in INK2 and take CLAY only when READ:
    # the index's read-chase and the colophon ring now say "this one" with
    # ink state and one accent instead of with six competing hues.
    globals()["LEGEND"] = [(n, t["INK2"]) for n in
                           ("GLYPH", "JETPACK", "CADENCE",
                            "APPLIED", "VISUALASSIST", "AUTOML")]
    globals()["LEGEND_READ"] = t["CLAY"]


set_theme("dark")


def op(v: float) -> float:
    """Translucent-accent opacity, per theme.

    The light lift (0.6 + 0.4v) was measured when the light ground was WHITE,
    where compositing destroys chroma contrast faster than compositing toward
    black. Both grounds are paper now — #f2e4c9 and #43372f — which are far
    closer in luminance, so the lift is no longer strictly required. It is
    kept because it is CONSERVATIVE in the direction that matters and because
    removing it would restate every translucent mark on the page in one
    unrelated commit. Re-measured on the new grounds for the one rest-state
    alpha the page still ships, Glyph's pen ghost: INK at 0.55 composites to
    #a59c91 = 4.25:1 on night paper, and the light lift takes it to 0.82,
    #3f3a2f-ward = well past 3.0 (the un-lifted 0.55 would be #827a6a =
    3.38:1, which also clears). Both sides of the branch are measured.
    """
    return v if THEME == "dark" else round(0.6 + 0.4 * v, 2)

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


def ink(d: str) -> tuple[float, float]:
    """x-extent of a DIGITS glyph's actual ink (see round 17's jitter note)."""
    n = [float(v) for v in re.findall(r'-?\d+\.?\d*', d)]
    xs = n[0::2]
    return min(xs), max(xs)


def digit(d: str, x: float, y: float, scale: float, *, centre: float | None = None) -> str:
    """Place a glyph so its INK lands where you asked, not its bounding box."""
    x0, x1 = ink(d)
    dx = x - x0 * scale if centre is None else x + (centre - (x1 - x0) * scale) / 2 - x0 * scale
    return f'transform="translate({dx:.2f},{y:.2f}) scale({scale})"'


EASE = "cubic-bezier(.4,0,.2,1)"
# ARREST: nearly all the deceleration in the last fifth — for a thing being
# STOPPED (the work plate's stamp lands with it; a stamp is an arrest).
ARREST = "cubic-bezier(.05,.75,.1,1)"
# BREATHE: symmetric sine, for ambient settles and yoyo carriers that are
# allowed a beat of rest at each end.
BREATHE = "cubic-bezier(.37,0,.63,1)"
# DRIFT: a near-sine whose slope never reaches zero — for yoyo carriers that
# must NOT stall at the turn, because the raster gate (and the eye) reads a
# stalled carrier as a freeze.
DRIFT = "cubic-bezier(.45,.05,.55,.95)"


def head(h: int, title: str, desc: str, key: str = "",
         col: tuple[int, int] = (150, 730),
         frame: tuple[float, float, float] | None = None,
         serif: bool = False) -> str:
    """Open a plate.

    `col` and `frame` are this plate's DECLARED geometry, written into the SVG
    root as data-col / data-frame and asserted by gate.mjs (checks 5 and 12):
    no edge is ever an accident — the file states its geometry and the render
    must match — without forcing every plate into one frame.
    `frame` is (top, rightGap, bottomGap): measured ink extents this plate
    stands behind, in viewBox units.
    `serif` embeds the serif face — only the two plates that speak in it pay
    its 10KB.
    """
    if key:
        # The light pass re-authors the same key. A plate and its light twin
        # must carry byte-identical descriptions — asserted, not assumed.
        if key in ALT and ALT[key] != desc:
            raise SystemExit(f"{key}: description diverged between themes")
        ALT[key] = desc
    fr = f' data-frame="{frame[0]:g},{frame[1]:g},{frame[2]:g}"' if frame else ''
    # Two REAL weights of the mono. .hero/.sub/.vast ask for 600, and with a
    # single 400 face every platform synthesised that bold differently —
    # FreeType widened "96.72%" 2u past its column edge on Linux while
    # CoreText held it inside. The serif face carries the serif voice for the
    # same reason: ui-serif/Georgia resolved to Liberation Serif on CI and to
    # Georgia on macOS, a different typeface per reader on a page that calls
    # itself self-contained. (Gelasio, OFL, metric-compatible with Georgia.)
    ser = (f"@font-face{{font-family:'S';font-weight:400;"
           f"src:url(data:font/woff2;base64,{FONTSERIF}) format('woff2')}}\n") if serif else ''
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="{VB_X} 0 {VB_W} {h}" width="{VB_W}" height="{h}" role="img" aria-label="{desc}" data-col="{col[0]},{col[1]}"{fr}>
<title>{title}</title><desc>{desc}</desc>
<style>
@font-face{{font-family:'M';font-weight:400;src:url(data:font/woff2;base64,{FONT}) format('woff2')}}
@font-face{{font-family:'M';font-weight:600;src:url(data:font/woff2;base64,{FONT600}) format('woff2')}}
{ser}text{{font-family:'M',ui-monospace,SFMono-Regular,Menlo,monospace}}
.hero{{font-size:55px;letter-spacing:-1px;fill:{INK};font-weight:600}}
.sub{{font-size:34px;letter-spacing:-0.5px;fill:{INK};font-weight:600}}
.unit{{font-size:34px;letter-spacing:-0.5px;fill:{INK2}}}
.say{{font-size:21px;fill:{INK2}}}
.lbl{{font-size:13px;letter-spacing:1.6px;fill:{INK2}}}
.key{{font-size:13px;letter-spacing:1.6px;fill:{INK}}}
.fine{{font-size:13px;letter-spacing:0.4px;fill:{INK2}}}
.kick{{font-size:13px;letter-spacing:2.4px;fill:{INK3}}}
@media (prefers-reduced-motion: reduce){{*{{animation:none!important}}}}
"""


def ground(h: int) -> str:
    """The sheet. THIS RECT MUST BE FIRST IN DOCUMENT ORDER — see below.

    It used to paint nothing (fill-opacity 0) and exist only so gate.mjs could
    read a contrast ground off it. Now it paints: the plate is a sheet of the
    portfolio's own paper laid on GitHub's page, which is the case-file idiom
    that property already uses, and it means every ratio the gate computes is
    against paper this design owns rather than a canvas it borrows.

    ORDER IS LOad-BEARING. gate.mjs:548 takes its contrast ground from the
    computed fill of the FIRST <rect> in document order, ignoring fill-opacity.
    Emit anything before this — including the frame below — and all 36 files
    grade every colour against the wrong ground, and they do it quietly.

    The frame is not decoration. Day paper measures 1.26:1 against GitHub's
    white and night paper 1.65:1 against its dark canvas: perceptible as a
    tint, invisible as an object. The WIRE edge (4.14 day / 4.21 night) is
    what makes it read as a sheet. It is a full-canvas rect, so gate.mjs
    filters it out of both `drawables` and check 12's element list by the same
    bbox rule that drops the slab — it cannot straddle anything, and its own
    contrast is not graded, which is why WIRE is measured here in the comment.
    """
    return (f'<rect x="{VB_X}" width="{VB_W}" height="{h}" fill="{GROUND}"/>'
            f'<rect x="{VB_X + 0.5}" y="0.5" width="{VB_W - 1}" height="{h - 1}" '
            f'fill="none" stroke="{WIRE}" stroke-width="1"/>')


def redact() -> str:
    """A redaction bar's paint — THE EDGE IS NOT OPTIONAL.

    Night REDACT (#2e2620) measures 1.29:1 on night paper, far under the 3.0
    non-text floor. It is legal only through the stroke escape at
    gate.mjs:566-572, which lets a non-text fill pass when its stroke already
    clears 3.0. So the edge is baked in here rather than left to the call
    site: no future plate can draw a bare void and discover the gate later.

    WIRE, not RULE. Both clear the floor, but WIRE carries the margin — 4.21
    night / 4.14 day against RULE's 3.40 / 3.19 — and a stroke that exists to
    make a fill LEGAL must not ride the palette's thinnest margin. One
    template serves both themes: on day paper the bar is solid ink (12.48:1)
    and takes the same edge, so the markup stays theme-symmetric and reads as
    an applied object rather than a hole.
    """
    return f'fill="{REDACT}" stroke="{WIRE}" stroke-width="1.4"'


# ────────────────────────────────────────────────────────────── PLATE 0
def plate_thesis() -> str:
    """The title page and index. Room: a book's opening.

    Who / what / where in twenty seconds: name, one serif sentence, contact,
    one line of languages (the five skill bands of round 20 were the least
    differentiated content in the best real estate — cut), and the index of
    sections with dot leaders. The index is where the reader is taught the
    document's system: one mark and one hue per system, and the section's
    answer compressed to a clause.

    Carriers: the dot leaders DRIFT toward their numerals, and the title-page
    ornament turns like a compositor's dingbat. Round 21 measured this plate
    at zero gestures in 270 samples — a carrier and nothing else, ranked
    last of nine, on the first thing anyone sees. So the index is now READ:
    row by row, in order, each leader lights to full ink, its numeral takes
    its section's hue and its mark swells — the reader's eye walking the
    table of contents — and once per cycle the whole index rings together,
    the one chord on a quiet title page. Still the arc's first bar, not its
    climax: every event is colour and 25% scale, nothing travels.
    """
    H, CX = 540, 440
    TC = 11.9                      # the read's clock — coprime with 9.4 and 27
    s = [head(H, "Ayush Yadav — computer science graduate, Cincinnati OH",
              "Ayush Yadav, a computer science graduate in Cincinnati, Ohio, open to "
              "full-time engineering roles. C++, TypeScript, Python, Java, Swift and "
              "Rust. An index of what follows: work, a year of it attested; jetpack, "
              "parallel gzip measured; Glyph, borrowed code made faster; Agentic "
              "AutoML, dataset in, model out; Cadence, the database that refuses; "
              "Applied, allowed to say not sure; and VisualAssist, which needs a "
              "lidar sensor.", key="plate-0-thesis.svg",
              col=(118, 762), frame=(43, 79.3, 34), serif=True)]
    s.append(f""".ser{{font-family:'S',ui-serif,Georgia,'Times New Roman',serif;font-size:34px;fill:{INK}}}
.orn{{transform-box:fill-box;transform-origin:center;animation:orn 27s linear infinite}}
@keyframes orn{{from{{transform:rotate(45deg)}}to{{transform:rotate(405deg)}}}}
/* the leaders drift toward their numerals — 75u is ten dash periods, so the
   wrap is invisible by construction */
@keyframes ld{{from{{stroke-dashoffset:0}}to{{stroke-dashoffset:-75}}}}
""")
    # the read: rows I..VII light in order across the first 90% of the clock,
    # then the chord — every leader, numeral and mark together at 92.5-97.5%.
    # Colour animations only, so the authored frame stays the finished frame.
    hues = dict(LEGEND)
    MARKS = [None, "JETPACK", "GLYPH", "AUTOML", "CADENCE", "APPLIED", "VISUALASSIST"]
    for i, mk in enumerate(MARKS):
        w0, w1 = i * 90 / 7 + 0.8, (i + 1) * 90 / 7 - 0.8
        s.append(f".ldc{i}{{animation:ld 9.4s linear infinite,ldc{i} {TC}s linear infinite}}"
                 f"@keyframes ldc{i}{{0%,{w0:.1f}%{{stroke:{RULE}}}{w0+1.2:.1f}%,{w1:.1f}%{{stroke:{INK}}}"
                 f"{w1+1.2:.1f}%,92.5%{{stroke:{RULE}}}93.8%,96%{{stroke:{INK}}}97.5%,100%{{stroke:{RULE}}}}}")
        if mk:  # the numeral takes its section's hue; the mark swells
            hue = hues[mk]
            s.append(f".nm{i}{{animation:nm{i} {TC}s linear infinite}}"
                     f"@keyframes nm{i}{{0%,{w0:.1f}%{{fill:{INK}}}{w0+1.2:.1f}%,{w1:.1f}%{{fill:{hue}}}"
                     f"{w1+1.2:.1f}%,92.5%{{fill:{INK}}}93.8%,96%{{fill:{hue}}}97.5%,100%{{fill:{INK}}}}}")
            s.append(f".ix{i}{{transform-box:fill-box;transform-origin:center;"
                     f"animation:ix{i} {TC}s {BREATHE} infinite}}"
                     f"@keyframes ix{i}{{0%,{w0:.1f}%{{transform:scale(1)}}{(w0+w1)/2:.1f}%{{transform:scale(1.25)}}"
                     f"{w1+1.2:.1f}%,92.5%{{transform:scale(1)}}94.5%{{transform:scale(1.15)}}"
                     f"96.5%,100%{{transform:scale(1)}}}}")
    s.append(f"</style>{ground(H)}")

    s.append(f'<text x="{CX}" y="{TOP}" text-anchor="middle" class="key" style="letter-spacing:5px">AYUSH YADAV</text>')
    s.append(f'<text x="{CX}" y="82" text-anchor="middle" class="lbl">CS GRADUATE · CINCINNATI, OHIO</text>')

    # the one serif voice, opening the bracket the colophon closes
    for i, ln in enumerate(["Systems, from SIMD kernels", "to the browser they run in."]):
        s.append(f'<text x="{CX}" y="{138 + i*42}" text-anchor="middle" class="ser">{ln}</text>')
    s.append(f'<text x="{CX}" y="214" text-anchor="middle" class="fine">Open to full-time software engineering roles · aesh.03.23@gmail.com</text>')

    # a title page's ornament earns its ink by being the only one: a short
    # rule with a set diamond — and the diamond turns, the page's first and
    # smallest motion, so the document is alive from its first inch.
    s.append(f'<path d="M380 244H500" stroke="{RULE}"/>')
    s.append(f'<g transform="translate(440,244)"><rect class="orn" x="-4" y="-4" width="8" height="8" fill="{RULE}"/></g>')

    s.append(f'<text x="{CX}" y="286" text-anchor="middle" class="fine">C++ · TypeScript · Python · Java · Swift · Rust</text>')

    # ── the index. Dot leaders run to the chapter numerals; the one place
    # all six hues appear together, taught in the reader's first ten seconds.
    s.append(f'<text x="{CX}" y="330" text-anchor="middle" class="kick">INDEX</text>')
    ROWS = [
        ("I",   None,           "WORK",           "a year of it, attested"),
        ("II",  "JETPACK",      "JETPACK",        "parallel gzip, measured"),
        ("III", "GLYPH",        "GLYPH",          "borrowed code, made faster"),
        ("IV",  "AUTOML",       "AGENTIC AUTOML", "dataset in, model out"),
        ("V",   "CADENCE",      "CADENCE",        "the database refuses"),
        ("VI",  "APPLIED",      "APPLIED",        "allowed to say not sure"),
        ("VII", "VISUALASSIST", "VISUALASSIST",   "needs a lidar sensor"),
    ]
    for i, (num, mark, name, tag) in enumerate(ROWS):
        y = 358 + i * 24
        if mark:
            s.append(f'<g class="ix{i}">' + logo(mark, 200, y - 13, 16, hues[mark]) + '</g>')
        nm_fill = hues.get(mark, INK2) if mark else INK2
        s.append(f'<text x="228" y="{y}" class="fine">'
                 f'<tspan fill="{nm_fill}">{name}</tspan>'
                 f'<tspan fill="{INK3}"> — {tag}</tspan></text>')
        lx = 228 + len(f"{name} — {tag}") * 8.2 + 14   # this row's text end
        # stroke via style, not attribute: the ldc chase animates it, and a
        # presentation attribute would report as overridden to check 15
        s.append(f'<path class="ldc{i}" d="M{lx:.0f} {y-4}H636" style="stroke:{RULE}" '
                 f'stroke-width="1.5" stroke-dasharray="1.5 6"/>')
        s.append(f'<text x="690" y="{y}" text-anchor="end" class="key{f" nm{i}" if mark else ""}">{num}</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────── PLATE I — WORK
def plate_work() -> str:
    """The ledger. Room: an account book.

    A year of paid engineering and a national competition, none of it in a
    repository a reader can clone — so the warrant is testimony, and the
    plate is the document testimony lives in: an account book. Date column
    left, item in the middle, AMOUNTS RIGHT-ALIGNED AT THE PAGE EDGE, full-
    width row rules, a double rule opening and closing the account.

    Carrier: an auditor's rule — a bright index head on a hairline — that
    travels down the account at reading pace, fades at the foot, returns to
    the head. Steady-state, so linear is correct. Round 21's live pass proved
    a scan drawn in the row rules' own grey and weight reads as a STRAY RULE,
    so the instrument now has its own vocabulary. Gestures, all on the scan's
    clock so the reader and the read cannot disagree: each amount PRESSES and
    its label lifts to full ink at the moment the rule crosses its row (the
    tally); the two linkage bars run tick-streams at rates proportional to
    99.6 and 32 (the jetpack device — the comparison, performed); and when
    the rule clears the closing rule, the ATTESTED stamp re-inks — a press,
    never an absence, because the round-21 blink measured as a glitch.
    """
    H, SCAN = 696, 15.9
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
              "from a public repository.", key="plate-0b-work.svg",
              frame=(40, 63.5, 26))]
    # The stamp rides the scan's clock: the rule reads the account top to
    # bottom, and only once it clears the closing rule does the stamp re-ink
    # — lifted and faded to 0.3, never absent, then pressed home (ARREST).
    # The scan is a sawtooth: constant descent, a fade before the reset so
    # nothing teleports while visible, and a negative delay so t=0 is
    # mid-travel at full opacity.
    s.append(f""".stp{{transform-box:fill-box;transform-origin:center;animation:stp {SCAN}s {ARREST} infinite;animation-delay:-4.4s}}
@keyframes stp{{0%,94%{{opacity:1;transform:scale(1)}}95.2%{{opacity:0.3;transform:scale(1.12)}}
  97%{{opacity:1;transform:scale(1.03)}}98.5%,100%{{opacity:1;transform:scale(1)}}}}
.scan{{animation:scan {SCAN}s linear infinite;animation-delay:-4.4s}}
@keyframes scan{{0%{{opacity:0;transform:translateY(0)}}3%{{opacity:1}}
  94%{{opacity:1;transform:translateY(452px)}}97%,100%{{opacity:0;transform:translateY(452px)}}}}
/* the linkage bars state their fractions twice — length, and the rate of the
   tick-stream inside each: 99.6 against 32, a 3.1x flow difference the eye
   reads without the caption (12u is one dash cycle, so wraps are seamless) */
.bf0{{animation:bf0 {12/(0.28*99.6):.3f}s linear infinite}}
.bf1{{animation:bf1 {12/(0.28*32):.3f}s linear infinite}}
@keyframes bf0{{from{{stroke-dashoffset:0}}to{{stroke-dashoffset:-12}}}}
@keyframes bf1{{from{{stroke-dashoffset:0}}to{{stroke-dashoffset:-12}}}}
""")
    # the tally: as the rule crosses each row, the amount presses (a 6% pulse
    # about its fixed right edge) and its label lifts to full ink with a slow
    # afterglow. The crossing percentages fall straight out of the scan's own
    # keyframes — 94% of the loop maps 452u of travel from y=96 — so the
    # reader and the thing read share one clock by construction.
    for i, ry in enumerate((186, 248, 310, 418, 480)):
        p = 94 * (ry - 12 - 96) / 452
        s.append(
            f".tly{i}{{transform-box:fill-box;transform-origin:right center;"
            f"animation:tly{i} {SCAN}s {BREATHE} infinite;animation-delay:-4.4s}}\n"
            f"@keyframes tly{i}{{0%,{p-2:.1f}%{{transform:scale(1)}}{p:.1f}%{{transform:scale(1.06)}}"
            f"{p+2:.1f}%,100%{{transform:scale(1)}}}}\n"
            f".wl{i}{{animation:wl{i} {SCAN}s linear infinite;animation-delay:-4.4s}}\n"
            f"@keyframes wl{i}{{0%,{p-1.5:.1f}%{{fill:{INK2}}}{p+0.5:.1f}%,{p+4:.1f}%{{fill:{INK}}}"
            f"{p+8:.1f}%,100%{{fill:{INK2}}}}}")
    s.append(f"</style>{ground(H)}")

    s.append(f'<text x="{L}" y="{TOP}" class="lbl">ACCOUNT OF A YEAR’S PAID WORK</text>')
    s.append(f'<text x="{R}" y="{TOP}" text-anchor="end" class="lbl">No. I — WORK</text>')
    # a ledger opens and closes with a double rule
    s.append(f'<path d="M{L} 68H{R}M{L} 72H{R}" stroke="{RULE}"/>')
    # the auditor's rule, reading the account: a hairline one voice brighter
    # than the row rules, led by a solid index head — an instrument, not a rule
    s.append(f'<g class="scan"><path d="M{L} 96H{R}" stroke="{INK2}" stroke-width="1.6"/>'
             f'<rect x="{L}" y="94.5" width="26" height="3" fill="{INK}"/></g>')
    for x, t, anch in ((L, "PERIOD", ""), (290, "ITEM", ""), (R, "FIGURE", ' text-anchor="end"')):
        s.append(f'<text x="{x}" y="96"{anch} class="kick">{t}</text>')

    s.append(f'<text x="{L}" y="124" class="kick">JUN 2025 –</text>')
    s.append(f'<text x="{L}" y="140" class="kick">MAY 2026</text>')
    s.append(f'<text x="290" y="124" class="key">ITSM DATA INTEGRATION INTERN</text>')
    s.append(f'<text x="290" y="144" class="fine">Miami University — OAS-to-Tableau migration</text>')
    s.append(f'<path d="M{L} 158H{R}" stroke="{RULE}"/>')

    ROWS = [
        (186, "ROW FIELD-USAGE TABLE",      "from 1.6M Oracle query logs, 5 years",  "57.8M"),
        (248, "CODE COMPLIANCE, 61 PROJECTS","from 0 — a legacy Laravel reporter",  "96.72%"),
        (310, "ROW MASTER ASSET INVENTORY", "Tableau + Workday, hash-deduped",  "10,453"),
    ]
    for i, (y, lab, det, amt) in enumerate(ROWS):
        s.append(f'<text x="290" y="{y}" class="lbl wl{i}">{lab}</text>')
        s.append(f'<text x="290" y="{y+20}" class="fine">{det}</text>')
        s.append(f'<text x="{R}" y="{y}" text-anchor="end" class="sub tly{i}">{amt}</text>')
        s.append(f'<path d="M{L} {y+34}H{R}" stroke="{RULE}"/>')

    s.append(f'<text x="{L}" y="376" class="kick">DATAFEST 2026</text>')
    s.append(f'<text x="290" y="376" class="key">TEAM LEAD OF 3 · NATIONAL ASA</text>')
    s.append(f'<path d="M{L} 390H{R}" stroke="{RULE}"/>')

    s.append(f'<text x="290" y="418" class="lbl wl3">HOLDOUT AUC, 349K PATIENTS</text>')
    s.append(f'<text x="290" y="438" class="fine">90-day care utilisation, SHAP-explained</text>')
    s.append(f'<text x="{R}" y="418" text-anchor="end" class="sub tly3">0.90</text>')
    s.append(f'<path d="M{L} 452H{R}" stroke="{RULE}"/>')

    s.append(f'<text x="290" y="480" class="lbl wl4">OF LINKAGE PRESERVED</text>')
    s.append(f'<text x="290" y="500" class="fine">7.7M encounters · DuckDB + Polars</text>')
    s.append(f'<text x="{R}" y="480" text-anchor="end" class="sub tly4">99.6%</text>')
    # the linkage claim is a comparison, so draw the comparison twice over:
    # LENGTH (widths always 300*frac from the value beside them), full ink for
    # the preserved fraction against half ink for the naive one (the light
    # theme's black-bar weight, ported), and the tick-streams above flowing at
    # the two rates — the one chart on the plate, finally its loudest
    for j, (frac, tag, fill, cls) in enumerate([(0.996, "star", INK, "bf0"),
                                                (0.32, "32% naive", INK2, "bf1")]):
        yy = 512 + j * 20
        w = 300 * frac
        s.append(f'<g><rect x="290" y="{yy}" width="300" height="12" fill="none" stroke="{WIRE}"/>'
                 f'<rect x="290" y="{yy}" width="{w:.2f}" height="12" fill="{fill}"/>'
                 f'<path class="{cls}" d="M290 {yy+6}H{290+w:.1f}" stroke="{GROUND}" '
                 f'stroke-opacity="0.55" stroke-width="4" stroke-dasharray="2 4"/></g>')
        s.append(f'<text x="602" y="{yy+11}" class="fine">{tag}</text>')

    # the account closes
    s.append(f'<path d="M{L} 564H{R}M{L} 568H{R}" stroke="{RULE}"/>')

    # ── the stamp. Rotated, hollow, struck over the closing rule — the whole
    # section's warrant in one device. Its two texts share the stamp's <g>,
    # which is what makes the composition legal to the collision checks.
    s.append(f'<g transform="translate(600,600) rotate(-7)"><g class="stp">'
             f'<rect x="-110" y="-31" width="220" height="62" rx="8" fill="none" stroke="{INK3}" stroke-width="2"/>'
             f'<text x="0" y="-2" text-anchor="middle" class="say" style="fill:{INK3};letter-spacing:4px">ATTESTED</text>'
             f'<text x="0" y="22" text-anchor="middle" class="kick">ON MY WORD</text>'
             f'</g></g>')

    s.append(f'<text x="{L}" y="666" class="fine" style="fill:{INK3}">ATTESTED — not derivable from a public repo</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── PLATE II
def plate_jetpack() -> str:
    """The bench sheet. Room: a test-bench record.

    The question is "is hand-vectorised code actually faster?", and the
    honest answer is BOTH WAYS: 6.4x on the parallel path, and a checksum
    that loses to the JDK's own intrinsic, printed here as the reference.

    Carriers: every measured bar carries a tick-stream INSIDE it, drifting at
    a rate proportional to the value beside it — the throughput, performed.
    The intrinsic's bar streams fastest on the plate, which is the argument.
    Second carrier: the bounded in-flight window runs as a true conveyor —
    four blocks in continuous descent, drained in order at the foot, each
    keyframe set phased in geometry so frame zero is the authored queue.
    """
    H, LOOP, a = 584, 11.3, CLAY_G
    BH, SP = 18, 26                # block height, conveyor pitch
    WX0, WX1 = 560, 690            # the window's bracket lines
    BY0, TRAVEL = 114, 96          # conveyor head, travel span
    s = [head(H, "jetpack — 6.4x parallel, and the intrinsic it does not beat",
              "jetpack: parallel gzip on JDK 25 reaches 422 megabytes per second against 66.2 "
              "single-threaded, a 6.4 times speedup, with blocks held in a bounded in-flight "
              "window drawn here as a running conveyor. Its hand-vectorised Adler-32 checksum "
              "runs at 4.26 gigabytes per second, 2.80 times the scalar baseline's 1.52, and "
              "is verified bit-identical against java.util.zip — whose own native intrinsic "
              "is faster still, at 14.06, and is printed here as the reference it loses to.",
              key="plate-2-jetpack.svg", frame=(35, 64, 14))]
    # ── the conveyor. Block k is AUTHORED at slot k; its keyframes carry it
    # to the foot, drain it (scaleX collapse, faded), re-enter it at the head
    # and walk it back into its authored slot by 100% — so the still frame is
    # the full queue and the phases live in geometry, not in delays. Round 22
    # tightened the drain-to-re-entry window from ~6.75% to ~3.5% of the loop
    # (round 21's live pass read the long hole as a dropped frame, not a
    # bounded queue). A FIFTH block was tried first and is structurally
    # impossible: with drains 20% apart the head has not opened a full
    # block-height when the re-entrant is due, and any later entry must
    # descend faster than its pursuer — the collision gate caught the 5-up
    # schedule riding 2u inside the block ahead. Four blocks, margins
    # re-derived per pursuer pair: 10.4 / 5.5 / 4.4 / 2.6u, all opening.
    cyc = []
    for k in range(4):
        r = 88 - 22 * k            # % of loop when this block reaches the foot
        cyc.append(
            f".b{k}{{transform-box:fill-box;transform-origin:right center;"
            f"animation:cyc{k} {LOOP}s linear infinite}}\n@keyframes cyc{k}{{"
            f"0%{{opacity:1;transform:translateY(0) scaleX(1)}}"
            f"{r:g}%{{opacity:1;transform:translateY({TRAVEL - SP*k}px) scaleX(1)}}"
            f"{r+2:g}%{{opacity:0;transform:translateY({TRAVEL - SP*k}px) scaleX(.08)}}"
            f"{r+3.5:g}%{{opacity:0;transform:translateY({-SP*k}px) scaleX(1)}}"
            f"{r+5.5:g}%{{opacity:1;transform:translateY({-SP*k}px) scaleX(1)}}"
            f"100%{{opacity:1;transform:translateY(0) scaleX(1)}}}}")
    s.append("".join(cyc))
    # ── the tick-streams: a dash pattern drifting inside each bar at a rate
    # proportional to the measured value. 12u is two dash periods (2 4), so
    # every wrap is seamless; linear, because throughput is steady state. The
    # 6u pitch is round 21's fix: at 12u the two loser bars degraded into
    # three dots and the comparison's baseline was nearly invisible.
    RATE = 48 / 422                # u/s per MB/s — the fastest bar sets 48u/s
    RATEB = 48 / 14.06             # the checksum lane scales to ITS maximum
    for i, v in enumerate([66.2, 422]):
        s.append(f".sa{i}{{animation:sa{i} {12/(v*RATE):.3f}s linear infinite}}"
                 f"@keyframes sa{i}{{from{{stroke-dashoffset:0}}to{{stroke-dashoffset:-12}}}}")
    for i, v in enumerate([1.52, 4.26, 14.06]):
        s.append(f".sb{i}{{animation:sb{i} {12/(v*RATEB):.3f}s linear infinite}}"
                 f"@keyframes sb{i}{{from{{stroke-dashoffset:0}}to{{stroke-dashoffset:-12}}}}")
    s.append(f"</style>{ground(H)}")

    # the instrument badge — chapter identification, boxed, top right
    s.append(f'<rect x="590" y="40" width="140" height="36" fill="none" stroke="{WIRE}"/>')
    s.append(f'<text x="660" y="62" text-anchor="middle" class="kick">II · JETPACK</text>')

    s.append(f'<text x="{L}" y="{TOP}" class="say" style="fill:{INK}">ONE VIRTUAL THREAD PER BLOCK</text>')
    s.append(f'<text x="{L}" y="82" class="lbl">JDK 25 · M1 PRO · 3 JMH FORKS</text>')
    s.append(f'<text x="{L}" y="170" class="hero">6.4<tspan class="unit">×</tspan></text>')

    s.append(f'<text x="{WX1}" y="98" text-anchor="end" class="kick">BOUNDED IN-FLIGHT WINDOW</text>')
    for j, ln in enumerate(["peak memory tracks", "the window,", "not the file"]):
        s.append(f'<text x="380" y="{146 + j*18}" class="fine">{ln}</text>')
    s.append(f'<path d="M{WX0} 106V232M{WX0} 106H{WX0+20}M{WX0} 232H{WX0+20}" stroke="{WIRE}" stroke-width="1"/>')
    s.append(f'<path d="M{WX1} 106V232M{WX1} 106H{WX1-20}M{WX1} 232H{WX1-20}" stroke="{WIRE}" stroke-width="1"/>')
    for k in range(4):
        s.append(f'<rect class="b{k}" data-max-x="{WX1}" x="{WX0+6}" y="{BY0 + k*SP}" '
                 f'width="107.8" height="{BH}" rx="2" style="fill:{a}"/>')

    # ── lane one: compression. Bars scale to this lane's own maximum; a
    # shared axis would invite exactly the cross-task comparison the prose
    # never makes, so each lane scales to its own (round 20's finding, kept).
    def lane(y, nm, val, w, mine, cls, tag=""):
        s.append(f'<text x="{L}" y="{y}" class="fine">{nm}</text>')
        s.append(f'<text x="412" y="{y}" text-anchor="end" class="key">{val}</text>')
        s.append(f'<g><rect x="470" y="{y-11}" width="{w:.1f}" height="14" fill="{a if mine else INK2}"/>'
                 f'<path class="{cls}" d="M470 {y-4}H{470+w:.1f}" stroke="{GROUND}" '
                 f'stroke-opacity="0.55" stroke-width="4" stroke-dasharray="2 4"/></g>')
        if tag:
            # CLAY text-grade (5.18 day / 6.28 night) — the graphic token is 3.62/4.36
            # and this is type, so it must clear 4.5 rather than 3.0.
            s.append(f'<text x="{470+w+12:.0f}" y="{y}" class="lbl" style="fill:{CLAY}">{tag}</text>')

    s.append(f'<text x="{L}" y="266" class="kick">COMPRESS — PARALLEL vs ONE THREAD · MB/s</text>')
    lane(296, "gzip, one thread", "66.2", 260*66.2/422, False, "sa0")
    lane(326, "parallel virtual threads", "422", 260, True, "sa1")

    # ── lane two: the checksum, and the reference it loses to. The intrinsic
    # gets the longest bar on the plate, and the fastest stream.
    s.append(f'<text x="{L}" y="370" class="kick">CHECKSUM — ADLER-32 · GB/s</text>')
    lane(400, "scalar, pure Java", "1.52", 260*1.52/14.06, False, "sb0")
    lane(430, "hand-vectorised", "4.26", 260*4.26/14.06, True, "sb1", "2.80×")
    lane(460, "java.util.zip intrinsic", "14.06", 260, False, "sb2")
    s.append(f'<text x="{L}" y="492" class="fine" style="fill:{INK}">not beaten — the reference stands</text>')

    # the verification readout: the known-answer vector the repo commits
    # (Adler32Test.java:36-37), fast path against reference, byte for byte
    s.append(f'<text x="{L}" y="532" class="lbl">SIMD ADLER-32</text>')
    s.append(f'<text x="330" y="532" class="say" style="fill:{INK}">11E60398</text>')
    s.append(f'<text x="{L}" y="564" class="lbl">java.util.zip</text>')
    s.append(f'<text x="330" y="564" class="say" style="fill:{INK}">11E60398</text>')
    s.append(f'<rect x="330" y="542" width="112" height="2" fill="{a}"/>')
    s.append(f'<text x="560" y="550" class="lbl" style="fill:{PINE}">identical</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── PLATE III
def plate_glyph() -> str:
    """The copybook. Room: a handwriting practice sheet.

    The authorship is stated on the plate because round 20 overclaimed it:
    the network was COURSE-PROVIDED (after Nielsen); the optimisation is the
    work, with Shree Chaturvedi credited; the browser application is the
    author's own. The question becomes "how much faster can you make code
    you didn't write?" and the committed benchmarks answer it both ways:
    3.5x on the 256 dot kernel, 6.9x SLOWER on the small axpy — parallelism
    has a floor, and printing the inversion is the point of the page.

    The net reads handwriting, so its 299 failures are drawn as failed
    homework: ruled baselines edge to edge, an amber margin line, every mark
    the true label of one missed image — the 220 in grey ink, the 79 the net
    was SURE about in heavy amber, so the field's own hue count is the 79.
    Carrier: the marker's nib reads the whole sheet, boustrophedon, one rule
    at a time, and the row under it lifts from grey to full ink — the grader
    working the field, which round 21 measured as the largest sleeping mass
    on the page. Gesture: the pen re-draws the hero 3.5 once per loop, over
    a half-ink ghost of itself, so the answer is NEVER absent (the round-21
    snap-to-nothing was the worst defect of the live pass). The nib's
    circuit is exactly two headline loops, so the two hands share a clock.
    """
    H, LOOP, SET, a = 556, 9.1, 7.6, CLAY_G
    NIB = 18.2                     # the nib's circuit — 2 x LOOP, commensurate
    s = [head(H, "Glyph — borrowed code made 3.5x faster, same 97.01%",
              "Glyph: a course-provided C++ MNIST network, hand-optimised — AVX-512, AVX2 and "
              "NEON kernels over a scalar fallback, written with Shree Chaturvedi; the React "
              "and TypeScript browser app is the author's own. The committed benchmarks "
              "answer both ways: 3.5 times faster on the 256 dot kernel under OpenMP and "
              "native codegen, and 6.9 times slower on the 128 axpy, because parallelism has "
              "a floor. Accuracy is unchanged at 97.01 percent on the 10,000-image MNIST "
              "test set, which means 299 wrong — every one of them drawn as a grid of the "
              "labels it missed, and the 79 it was most confident about drawn in a heavier "
              "stroke.", key="plate-1-glyph.svg",
              col=(96, 762), frame=(55, 10, 20))]
    s.append(f""".ink{{fill:none;stroke:{a};stroke-width:7;stroke-linecap:round;stroke-linejoin:round;
  stroke-dasharray:1;stroke-dashoffset:0;animation:draw {LOOP}s linear infinite;animation-delay:{-SET}s}}
/* 4% a glyph (round 19): at 17% the pen laid ink below the perceptual floor;
   at 4% each 100ms sample lays visible ink and the gesture reads as what the
   claim says — a pen stroke, by hand. The reset happens FADED over a
   half-ink ghost authored under every stroke, so the headline never blinks
   out of existence (round 21's live pass caught the snap) and the moving
   offset never resets while visible. */
@keyframes draw{{0%{{stroke-dashoffset:1;opacity:0}}1%{{opacity:1}}6%{{stroke-dashoffset:0}}
  96%{{opacity:1;stroke-dashoffset:0}}99.5%,100%{{opacity:0;stroke-dashoffset:0}}}}
/* the settle: as the pen lifts, the fresh digit relaxes — the second beat
   every gesture on this page owes to the .fil chip that taught it */
.stl{{transform-box:fill-box;transform-origin:center;animation:stl {LOOP}s {BREATHE} infinite}}
@keyframes stl{{0%,5%{{transform:scale(1)}}7.5%{{transform:scale(1.07)}}10%,100%{{transform:scale(1)}}}}
/* the nib: one closed boustrophedon circuit of the WHOLE field — up the
   margin, then every clear band between the ink rows, out and back. Closed
   path, so there is no wrap to hide and no reset to fade. Constant speed;
   the row groups below lift as it passes them. */
.nib{{offset-path:path('M146 436V296H773V324H146V352H773V380H146V408H773V436H146');
  offset-rotate:auto;animation:nib {NIB}s linear infinite;animation-delay:-9.3s}}
@keyframes nib{{from{{offset-distance:0%}}to{{offset-distance:100%}}}}
""")
    # the read: while the nib runs the band under row r, that row's grey ink
    # lifts to full — colour on the row group's `color`, the digits stroked
    # currentColor, so the lift needs one rule per row. Windows fall out of
    # the circuit's own geometry: climb 140u, band 627u, hop 28u, total 4042u.
    for r in range(6):
        s0 = (140 + r * 655) / 4042 * 100
        e0 = s0 + 627 / 4042 * 100
        if r < 5:
            s.append(f".rd{r}{{animation:rd{r} {NIB}s linear infinite;animation-delay:-9.3s}}"
                     f"@keyframes rd{r}{{0%,{s0-1:.1f}%{{color:{INK2}}}{s0+1:.1f}%,{e0-1:.1f}%{{color:{INK}}}"
                     f"{e0+1:.1f}%,100%{{color:{INK2}}}}}")
        else:  # the last band ends exactly at the wrap, so it stays lit across it
            s.append(f".rd{r}{{animation:rd{r} {NIB}s linear infinite;animation-delay:-9.3s}}"
                     f"@keyframes rd{r}{{0%{{color:{INK}}}1.5%,{s0-1:.1f}%{{color:{INK2}}}"
                     f"{s0+1:.1f}%,100%{{color:{INK}}}}}")
    s.append(f"</style>{ground(H)}")

    # the binder tab — chapter identification, rotated up the left edge
    s.append(f'<text transform="rotate(-90 112 480)" x="112" y="480" class="kick">III · GLYPH</text>')

    # ── the answer block: the pen DRAWS the answer — the question is about
    # work done by hand, and the hero is laid down by one. "3.5", stroke by
    # stroke, once per loop; the multiplier sits beside it in type.
    hx = 150
    for j, d in enumerate([DIGITS[3], "M60 147L61 150", DIGITS[5]]):
        dot = ';stroke-width:14' if j == 1 else ''
        gw = 14 if j == 1 else 7
        # the ghost: the same stroke at half ink, inside the settle group so
        # the pair moves as one. INK, not the accent: measured on paper,
        # INK at 0.55 composites to #a59c91 = 4.25:1 on night and #827a6a =
        # 3.38:1 on day (the light lift raises it to 0.82, higher again),
        # while the accent at the same alpha is 2.36 / 2.85 and fails the
        # 3.0 floor. It is faded handwriting, so it stays in the ink family.
        s.append(f'<g {digit(d, hx, 64, 0.55)}><g class="stl" style="animation-delay:{round(-SET + j*0.15,3)}s">'
                 f'<path d="{d}" fill="none" stroke="{INK}" stroke-opacity="{op(0.55)}" '
                 f'stroke-width="{gw}" stroke-linecap="round" stroke-linejoin="round"/>'
                 f'<path class="ink" d="{d}" pathLength="1" '
                 f'style="animation-delay:{round(-SET + j*0.15,3)}s{dot}"/></g></g>')
        x0, x1 = ink(d)
        hx += (x1 - x0) * 0.55 + 10
    # the multiplier, in the same hand as the digits it multiplies — round 21
    # called the typeset x "pasted on", and it was: two pen strokes now,
    # drawn fourth and fifth in the same 150ms wave, over the same ghost.
    # One group: the two strokes of a glyph CROSS, which is composition.
    xg = []
    for xd, dl in (("M0 0L38 42", -7.15), ("M38 0L0 42", -7.0)):
        xg.append(f'<path d="{xd}" fill="none" stroke="{INK}" stroke-opacity="{op(0.55)}" '
                  f'stroke-width="7" stroke-linecap="round"/>'
                  f'<path class="ink" d="{xd}" pathLength="1" style="animation-delay:{dl}s"/>')
    s.append(f'<g transform="translate({hx+8:.0f},124) scale(0.55)">'
             f'<g class="stl" style="animation-delay:-7.15s">' + "".join(xg) + '</g></g>')
    s.append(f'<text x="330" y="76" class="say" style="fill:{INK}">SOMEONE ELSE’S NET, 3.5× FASTER</text>')
    s.append(f'<text x="330" y="100" class="fine">benchDot/256 · openmp+native vs the course baseline</text>')
    s.append(f'<text x="330" y="120" class="fine" style="fill:{INK3}">6.9× SLOWER on benchAxpy/128 — threads have a floor</text>')
    s.append(f'<text x="330" y="140" class="fine" style="fill:{INK3}">three committed runs agree</text>')

    # the invariant: optimisation must not change the answers
    s.append(f'<text x="150" y="206" class="sub">97.01<tspan class="unit" style="font-size:21px">%</tspan></text>')
    s.append(f'<text x="330" y="176" class="lbl">MNIST TEST · n=10,000 — UNCHANGED</text>')
    s.append(f'<text x="330" y="206" class="say">299 wrong — 79 of them sure.</text>')

    # the kernel roll, one quiet line: what was written by hand, what was not.
    s.append(f'<text x="150" y="240" class="fine">3 KERNELS BY HAND, 1 AUTO —</text>')
    for cx, nm, hand in ((386, "AVX-512", True), (488, "AVX2", True),
                         (560, "NEON", True), (632, "wasm", False)):
        s.append(f'<circle cx="{cx}" cy="235" r="4" '
                 + (f'fill="{a}"' if hand else f'fill="none" stroke="{a}" stroke-width="1.8"') + '/>')
        s.append(f'<text x="{cx+12}" y="240" class="key">{nm}</text>')
    s.append(f'<text x="150" y="262" class="fine">4 BUILDS · 1 PATH COMPILED — nothing cross-checks them</text>')

    # ── the copybook field: rules edge to edge, the margin line, the errors
    # on their baselines. Each mark is the true label of one missed image,
    # from benchmarks/mnist_misclassified.csv; `conf` comes from the same
    # pinned CSV, so the 79 drawn heavy are the named 79. Round 21's 28%
    # opacity split could not carry a 500-mark field, so the split is now
    # ink: the 220 merely-wrong in grey (currentColor, lifted by the nib's
    # read), the 79 sure ones in heavy amber — hue AND weight, and the amber
    # count on the field IS the 79.
    rails = [f'<path d="M96 {288 + r*28}H784" stroke="{RULE}" stroke-width="1"/>' for r in range(6)]
    rails.append(f'<rect x="134.5" y="274" width="1.5" height="166" fill="{a}"/>')
    s.append('<g>' + "".join(rails) + '</g>')
    _e = json.loads((ROOT / "errors.json").read_text())
    errs, conf = _e["true"], _e["conf"]
    cols, pitch, sc = 50, 12.4, 0.08
    rowg: list[list[str]] = [[] for _ in range(6)]
    for i in range(len(errs)):
        r, c = i // cols, i % cols
        x, y = 150 + c * pitch, (288 + r * 28) - 150 * sc
        sure = conf[i]
        stroke = f'stroke="{a}" stroke-width="22"' if sure else 'stroke="currentColor" stroke-width="13"'
        rowg[r].append(f'<g {digit(DIGITS[errs[i]], x, y, sc, centre=11.4)}>'
                       f'<path d="{DIGITS[errs[i]]}" fill="none" {stroke} stroke-linecap="round"/></g>')
    for r in range(6):
        s.append(f'<g class="rd{r}" style="color:{INK2}">' + "".join(rowg[r]) + '</g>')
    # the nib, riding the clear bands between the ink rows — the whole field
    s.append(f'<g class="nib"><path d="M-16 0H0" stroke="{a}" stroke-width="3" stroke-linecap="round"/>'
             f'<circle cx="0" cy="0" r="3" fill="{a}"/></g>')
    s.append(f'<text x="150" y="490" class="fine" style="fill:{INK3}">each mark — the true label of one missed image, from the pinned CSV</text>')
    s.append(f'<text x="150" y="512" class="fine">course-provided net, after Nielsen — optimised with Shree Chaturvedi</text>')
    s.append(f'<text x="150" y="532" class="fine">the browser app is mine alone</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── PLATE IV
def plate_automl() -> str:
    """The phase dial. Room: a rotary instrument, and its sealed vessel.

    "One phase, one tool set" is a rotary fact — position selects capability,
    like a microscope turret — so the seven sets are sectors of a dial. The
    model's 15 carried tools live in the hub and NEVER move: they travel
    with the model, so they are simply always there. The 29 phase tools are
    ticks on the rim, lit only while their sector is active.

    Carrier: the needle CREEPS across the live sector and swings to the
    next — it is never still, because routing is never parked. Second
    carrier: a dashed feed drifts from the dial into the sandbox vessel —
    the Python the model writes, flowing into the only place allowed to run
    it. Sector windows, ticks and needle share one clock so they can never
    disagree about which phase is live, and 15/44 is set at headline weight
    because it is the claim.
    """
    H, LOOP, SET = 764, 13.3, 9.9
    a = CLAY_G
    CXD, CYD = 440, 296          # dial centre
    N = 7
    SPAN = 360 / N
    A = [round(100 / N * j + 2.25, 2) for j in range(N)]           # arrive at set j
    D = [round(100 / N * (j + 1) - 2.25, 2) for j in range(N)]     # depart set j
    pol = lambda deg, r: (CXD + r * math.sin(math.radians(deg)),
                          CYD - r * math.cos(math.radians(deg)))
    s = [head(H, "Agentic AutoML",
              "Agentic AutoML takes a dataset and a sentence and returns a trained model. "
              "Its tool registry holds 44 definitions, but the model never carries all of "
              "them: 15 travel with it in every phase and the remaining 29 arrive with the "
              "phase that needs them, routed by seven named tool sets — onboarding, "
              "preprocessing, feature proposal, feature continue, feature engineering, "
              "feature lifecycle and training lifecycle. The Python it writes executes in a "
              "container on an internal Docker network with no route out, a read-only root "
              "filesystem, a non-root user and the dataset mounted read-only, leaving 5 "
              "tmpfs mounts as the only writable surface. Behind it sits a 29-table Postgres "
              "schema with pgvector. Written with Shree Chaturvedi; the repository is public "
              "and licensed GPL-3.0.",
              key="plate-6b-automl.svg", frame=(40, 64, 26))]
    # sector windows and rim ticks on one shared clock
    phase = []
    for j in range(N):
        phase.append(
            f".sa{j}{{animation:sa{j} {LOOP}s linear infinite;animation-delay:{-SET}s}}\n"
            f"@keyframes sa{j}{{0%,{A[j]-1.5:g}%{{stroke:{ROW}}}{A[j]:g}%,{D[j]:g}%{{stroke:{a}}}"
            f"{min(D[j]+1.5, 99.9):g}%,100%{{stroke:{ROW}}}}}\n"
            f".tk{j}{{animation:tk{j} {LOOP}s linear infinite;animation-delay:{-SET}s}}\n"
            f"@keyframes tk{j}{{0%,{A[j]-1.5:g}%{{fill:{WIRE}}}{A[j]:g}%,{D[j]:g}%{{fill:{a}}}"
            f"{min(D[j]+1.5, 99.9):g}%,100%{{fill:{WIRE}}}}}")
    # ── the needle: creep + swing, never still. Within sector j it creeps
    # from centre-6° to centre+6° (the dwell is a slow read, not a hold);
    # between sectors it swings. The wrap from the last sector to the first
    # happens faded out, like every loop wrap on this page.
    ang = lambda j: -(N - 1 - j) * SPAN
    ndl = [f"0%{{opacity:0;transform:rotate({ang(0)-6:.2f}deg)}}",
           f"2%{{opacity:1;transform:rotate({ang(0)-6:.2f}deg)}}"]
    for j in range(N):
        if j:
            ndl.append(f"{A[j]:g}%{{transform:rotate({ang(j)-6:.2f}deg)}}")
        ndl.append(f"{D[j]:g}%{{transform:rotate({ang(j)+6:.2f}deg)}}")
    ndl.append(f"97%{{opacity:1;transform:rotate({ang(N-1)+6:.2f}deg)}}")
    ndl.append(f"100%{{opacity:0;transform:rotate({ang(N-1)+6:.2f}deg)}}")
    s.append("".join(phase) + f"""
/* the needle IS the routing. Round 21's live pass caught it parked for 9.3
   of every 13.3s while the sector chase ran on: without transform-box, its
   CSS rotation origin was left to the renderer's legacy SVG default, not
   the dial. So it now uses the same idiom as every other rotating element
   here — fill-box + origin:center — with a zero-ink balance path in its
   group pinning the fill-box's centre exactly on the dial's axis. */
.ndl{{transform-box:fill-box;transform-origin:center;animation:ndl {LOOP}s {EASE} infinite;animation-delay:{-SET}s}}
@keyframes ndl{{{"".join(ndl)}}}
/* the feed: what the model writes, flowing into the vessel. 12u per period,
   so the wrap is seamless; linear, because a pipe is steady state. */
.feed{{animation:feed 1.9s linear infinite}}
@keyframes feed{{from{{stroke-dashoffset:0}}to{{stroke-dashoffset:-12}}}}
</style>{ground(H)}""")

    s.append(f'<text x="{L}" y="{TOP}" class="kick">IV · AGENTIC AUTOML</text>')
    s.append(f'<text x="{L}" y="84" class="say" style="fill:{INK}">ONE PHASE, ONE TOOL SET</text>')
    s.append(f'<text x="{R}" y="{TOP}" text-anchor="end" class="key">44 TOOL DEFINITIONS</text>')
    s.append(f'<text x="{R}" y="104" text-anchor="end" class="fine">one MCP server over a LangGraph state machine</text>')
    # the headline the plate never had: every other section leads with its
    # number (6.4x, 3.5x, 0.979, B only) and this one buried 15-of-44 in
    # 11px small caps. The fraction is the claim; set it at the claim's size.
    s.append(f'<text x="{L}" y="176" class="hero">15<tspan class="unit">/44</tspan></text>')
    s.append(f'<text x="{L}" y="212" class="lbl">TRAVEL WITH THE MODEL</text>')

    # ── the dial. Arcs share one <g> — adjacent 51° arcs necessarily overlap
    # as bounding boxes, and the dial is one composed instrument.
    arcs = []
    for j in range(N):
        a0, a1 = j * SPAN + 3, (j + 1) * SPAN - 3
        x0, y0 = pol(a0, 92); x1, y1 = pol(a1, 92)
        arcs.append(f'<path class="sa{j}" d="M{x0:.1f} {y0:.1f}A92 92 0 0 1 {x1:.1f} {y1:.1f}" '
                    f'fill="none" stroke-width="13" style="stroke:{a if j == N-1 else ROW}"/>')
    ticks = []
    for j in range(N):
        n = 5 if j == N - 1 else 4
        for i in range(n):
            tang = j * SPAN + 8 + i * (SPAN - 16) / (n - 1)
            tx, ty = pol(tang, 112)
            ticks.append(f'<rect class="tk{j}" x="{tx-1.5:.1f}" y="{ty-5:.1f}" width="3" height="10" '
                         f'transform="rotate({tang:.1f} {tx:.1f} {ty:.1f})" '
                         f'style="fill:{a if j == N-1 else WIRE}"/>')
    # the needle, authored at its rest (the last sector's creep end). A RIM
    # index now — 84u to 106u, riding across the sector band — because with
    # the rotation origin actually on the dial's axis, a hub needle would
    # cross the 150u hub box every time it pointed near-horizontal. Drawn in
    # INK so it reads over the grey ring and the lit sector alike, at the
    # structural 2u. The zero-ink two-dot path spans +-110 so the group's
    # fill-box stays centred exactly on the axis whatever the needle's angle.
    th = (N - 1) * SPAN + SPAN / 2 + 6
    nx0, ny0 = math.sin(math.radians(th)) * 84, -math.cos(math.radians(th)) * 84
    nx1, ny1 = math.sin(math.radians(th)) * 106, -math.cos(math.radians(th)) * 106
    s.append('<g>' + "".join(arcs) + "".join(ticks)
             + f'<g transform="translate({CXD},{CYD})"><g class="ndl">'
             f'<path d="M-110 -110h0.01M110 110h0.01" fill="none"/>'
             f'<path d="M{nx0:.1f} {ny0:.1f}L{nx1:.1f} {ny1:.1f}" stroke="{INK}" stroke-width="2"/>'
             f'</g></g></g>')
    # the hub: what the model always holds. It does not move, because the 15
    # travel WITH the model — they are simply always there.
    s.append(f'<rect x="365" y="270" width="150" height="52" rx="6" fill="none" stroke="{a}"/>')
    s.append(f'<text x="{CXD}" y="292" text-anchor="middle" class="key">15 TRAVEL</text>')
    s.append(f'<text x="{CXD}" y="312" text-anchor="middle" class="kick">WITH THE MODEL</text>')
    # the seven sets, named around the rim
    NAMES = ["ONBOARD", "PREPROC", "PROPOSE", "CONTINUE", "ENGINEER", "LIFECYCLE", "TRAINING"]
    for j, nm in enumerate(NAMES):
        tang = j * SPAN + SPAN / 2
        lx, ly = pol(tang, 132)
        sn, cs = math.sin(math.radians(tang)), math.cos(math.radians(tang))
        if abs(sn) < 0.35:
            anch, lx, ly = 'middle', lx, ly + (14 if cs < 0 else -6)
        elif sn > 0:
            anch, lx, ly = 'start', lx + 6, ly + 4
        else:
            anch, lx, ly = 'end', lx - 6, ly + 4
        s.append(f'<text x="{lx:.0f}" y="{ly:.0f}" text-anchor="{anch}" class="kick">{nm}</text>')

    s.append(f'<text x="{R}" y="462" text-anchor="end" class="kick">29 ARRIVE WITH THE PHASE</text>')
    s.append(f'<text x="{R}" y="484" text-anchor="end" class="kick">SEVEN PHASE SETS</text>')

    # ── the feed, and the vessel it fills: where the generated Python runs.
    # Isometric, exploded — the five tmpfs trays lifted out on leaders,
    # because the count of writable surfaces IS the blast radius.
    s.append(f'<path class="feed" d="M382 388C330 442 290 470 262 522" fill="none" '
             f'stroke="{a}" stroke-width="1.6" stroke-dasharray="5 7"/>')
    s.append(f'<text x="418" y="524" class="kick">WHERE GENERATED PYTHON RUNS</text>')
    s.append(f'<path d="M183 568L258 532L333 568L258 604Z" fill="none" stroke="{a}" stroke-width="1.6"/>')
    s.append(f'<path d="M183 568V614L258 650L333 614V568" fill="none" stroke="{a}" stroke-width="1.6"/>')
    s.append(f'<path d="M258 604V650" stroke="{WIRE}" stroke-width="1"/>')
    for i in range(5):
        ty = 548 + i * 22
        s.append(f'<g><path d="M352 {ty}L366 {ty-7}L380 {ty}L366 {ty+7}Z" fill="none" stroke="{a}" stroke-width="1.4"/>'
                 f'<path d="M352 {ty}H338" stroke="{WIRE}" stroke-width="1"/></g>')
    # The trays no longer "breathe": round 21's live pass measured that
    # motion at under two rendered pixels — below the threshold of vision,
    # five animations buying nothing on the reader's compositor. An exploded
    # drawing is allowed to hold still; the dial and the feed carry the plate.
    FLAGS = ["--internal network — no route out",
             "--read-only — immutable rootfs",
             "--user sandbox — never root",
             "/datasets:ro — read-only mount",
             "5 tmpfs mounts — writable, transient"]
    for i, flag in enumerate(FLAGS):
        s.append(f'<text x="418" y="{548 + i*26}" class="fine" style="fill:{INK}">{flag}</text>')

    s.append(f'<text x="{L}" y="692" class="sub">29</text>')
    s.append(f'<text x="206" y="684" class="lbl">TABLES · POSTGRES + PGVECTOR</text>')
    s.append(f'<text x="206" y="706" class="fine">a Jupyter kernel per project, kept alive between cells</text>')
    s.append(f'<text x="{L}" y="{H-30}" class="fine" style="fill:{INK3}">public · GPL-3.0 · written with Shree Chaturvedi</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── PLATE V
def plate_cadence() -> str:
    """The redacted disclosure. Room: a FOIA response. Section: CADENCE.

    Round 21 merges the old refusal section into Cadence, because this IS
    Cadence's engineering: the old parser plate is retired and this plate
    carries the section. The system's actual product is a redacted document:
    you asked for everything, you received what you were entitled to. Tenant
    A's column comes back as redaction bars — blacked out by row-level
    security, not by the app — while B's rows return intact. The audit table
    keeps its named services and its guard marks, the caveats keep their
    asterisks, and the response to the unfiltered request is the loudest
    thing on the whole page: an 89px word that is not a number.

    Round 21's live pass found the two defects that undid the figure: at
    rest, A's and B's bars were near-identical grey slabs (the refusal only
    existed for 0.77s of a 9.7s loop), and in dark the redaction fill was
    one value off the returned rows. So the rest state now STATES the claim:
    tenant A's rows are redaction — black ink in light, a void held by a
    wire edge in dark, since a black bar on near-black paper vanishes —
    while tenant B's rows carry visible record-lines with a continuous
    emerald stream running through them: B's data flowing back, A's not,
    always. Carrier: that stream, plus the auditor's scan (the same
    instrument as plate I, turned inward, with the same bright index head).
    Gesture: the redactions are RE-STRUCK once per loop — each bar lifts
    faded, leaves its row blank for half a second (the void the database
    returned), then wipes back across left-to-right in a tight 60ms cascade
    down the column: the door slamming, and staying shut.
    """
    # PINE, not an arbitrary hue: this whole plate is the database refusing,
    # and the refusal is a CHECK. The accent says so.
    H, LOOP, a = 776, 9.7, PINE
    SCAN = 17.1
    rbar = redact()
    s = [head(H, "Cadence — six services audited, and the database that refuses",
              "Cadence, a calendar that files plain sentences, audited by its own author and "
              "drawn as a redacted disclosure. The IDOR: in six services — attachments, "
              "calendars, events, task-lists, tasks and tags — any authenticated user could "
              "read or delete another user's records by id. The guard marks per service: on "
              "read, all six carry the guard in the query itself; on delete, three do and "
              "three check ownership first. Tenant A's rows come back redacted — withheld "
              "by the database, not by the app — while tenant B's rows return. Two caveats "
              "stay on the plate: the tags test asserted the vulnerable query, and "
              "task-lists still has no regression test. Below, an unfiltered SELECT "
              "count(*) FROM tasks, run as B, comes back B only: PostgreSQL row-level "
              "security refused the rest.", key="plate-5-refusal.svg",
              frame=(45, 64, 28))]
    # the re-strike: 0% is the finished frame (redacted), held for 84% of the
    # loop; the bar lifts FADED (no visible retraction — the row is simply
    # blank, which is what the database sent), then wipes back left-to-right.
    # Round 21's bars returned to full width from a visible retraction, so
    # the resting figure showed A and B identical — the opposite of the claim.
    s.append(f""".vast{{font-size:89px;letter-spacing:-2px;fill:{INK};font-weight:600}}
.red{{transform-box:fill-box;transform-origin:left center;animation:red {LOOP}s {EASE} infinite}}
@keyframes red{{0%,84%{{opacity:1;transform:scaleX(1)}}85.5%{{opacity:0;transform:scaleX(1)}}
  86.5%{{opacity:0;transform:scaleX(.02)}}90.5%{{opacity:1;transform:scaleX(.02)}}
  95%,100%{{opacity:1;transform:scaleX(1)}}}}
/* B's stream: the record-lines inside every returned row drift toward the
   tenant — data coming back, continuously, on the side the guard allows.
   8u is one dash cycle, so the wrap is seamless. */
.bfl{{animation:bfl 1.7s linear infinite}}
@keyframes bfl{{from{{stroke-dashoffset:0}}to{{stroke-dashoffset:-8}}}}
.scan{{animation:scan {SCAN}s linear infinite;animation-delay:-6.1s}}
@keyframes scan{{0%{{opacity:0;transform:translateY(0)}}3%{{opacity:1}}
  94%{{opacity:1;transform:translateY(340px)}}97%,100%{{opacity:0;transform:translateY(340px)}}}}
</style>{ground(H)}""")

    s.append(f'<text x="{L}" y="{TOP}" class="kick">V · CADENCE — THE ISOLATION AUDIT</text>')
    s.append(f'<text x="{L}" y="88" class="say" style="fill:{INK}">SIX SERVICES, SELF-AUDITED</text>')
    s.append(f'<text x="{L}" y="116" class="kick">ANY USER COULD READ OR DELETE ANOTHER’S ROWS BY ID</text>')
    s.append(f'<text x="{L}" y="136" class="kick">THE MARKS SHOW WHERE EACH GUARD NOW SITS</text>')

    # the auditor's scan, turned on the author's own code — the plate-I
    # instrument, its index head in this section's emerald
    s.append(f'<g class="scan"><path d="M{L} 158H{R}" stroke="{INK2}" stroke-width="1.6"/>'
             f'<rect x="{L}" y="156.5" width="26" height="3" fill="{a}"/></g>')

    for x, t in ((340, "READ"), (396, "DELETE"), (492, "TENANT A")):
        s.append(f'<text x="{x}" y="170" class="kick">{t}</text>')
    s.append(f'<text x="{R}" y="170" text-anchor="end" class="kick">TENANT B</text>')
    # README order, which is the audit's order. The DELETE column tells the
    # 2026-08 sharpening: three services carry the owner predicate in the
    # DELETE itself, three check ownership first — a hollow mark is a
    # different mechanism, not a missing one.
    SVCS = [("attachments", False), ("calendars", False), ("events", True),
            ("task-lists*", False), ("tasks", True), ("tags**", True)]
    for i, (name, in_query) in enumerate(SVCS):
        y = 200 + i * 34
        s.append(f'<text x="{L}" y="{y}" class="lbl">{name}</text>')
        s.append(f'<rect x="354" y="{y-10}" width="8" height="8" fill="{a}"/>')
        if in_query:
            s.append(f'<rect x="427" y="{y-10}" width="8" height="8" fill="{a}"/>')
        else:
            s.append(f'<rect x="427" y="{y-10}" width="8" height="8" fill="none" stroke="{a}" stroke-width="1.4"/>')
        # A's row comes back REDACTED — there is nothing under the bar,
        # because the database never sent the row
        s.append(f'<rect class="red" x="480" y="{y-12}" width="110" height="16" rx="2" {rbar} '
                 f'style="animation-delay:{round(i*0.06,2)}s"/>')
        # B's row is the one that returns: record-lines inside, streaming
        s.append(f'<g><rect x="620" y="{y-12}" width="110" height="16" rx="2" fill="{ROW}" stroke="{a}"/>'
                 f'<path class="bfl" d="M626 {y-7}H724M626 {y-1}H724" stroke="{a}" '
                 f'stroke-width="1.5" stroke-dasharray="4 4"/></g>')

    # legends, in drawn marks rather than glyphs the font subset may not carry
    s.append(f'<rect x="{L}" y="398" width="8" height="8" fill="{a}"/>')
    s.append(f'<text x="166" y="406" class="fine">the guard is in the query</text>')
    s.append(f'<rect x="390" y="398" width="8" height="8" fill="none" stroke="{a}" stroke-width="1.4"/>')
    s.append(f'<text x="406" y="406" class="fine">checked first, then DELETE WHERE id</text>')
    s.append(f'<rect x="{L}" y="426" width="24" height="10" {rbar}/>')
    s.append(f'<text x="182" y="435" class="fine">withheld by row-level security, not by the app</text>')

    # the footnotes ARE the finding — an audit that means it keeps its asterisks
    s.append(f'<text x="{L}" y="466" class="fine" style="fill:{INK3}">*  task-lists — still has no regression test</text>')
    s.append(f'<text x="{L}" y="486" class="fine" style="fill:{INK3}">** tags — its test asserted the vulnerable query. Green forever.</text>')

    s.append(f'<path d="M{L} 518H{R}" stroke="{RULE}"/>')
    # the records request, unfiltered on purpose
    s.append(f'<text x="{L}" y="544" class="key">SELECT count(*) FROM tasks</text>')
    s.append(f'<text x="470" y="544" class="fine">as B — unfiltered on purpose</text>')
    # the response, at the largest type on the page — and it is not a number
    s.append(f'<text x="{L}" y="660" class="vast">B only</text>')
    s.append(f'<text x="520" y="660" class="lbl">ROW-LEVEL SECURITY</text>')
    s.append(f'<text x="{L}" y="712" class="say">The app didn’t remember to filter.</text>')
    s.append(f'<text x="{L}" y="{H-32}" class="say">The database refused.</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── PLATE VI
def plate_applied() -> str:
    """The sifting channel. Room: a sorting instrument in section.

    Rebuilt from zero this round: the old plate drew the funnel as two stray
    strokes, clip-art envelopes, three floating boxes and a dead bottom
    third, and the client's word for it was exact. The argument — a model
    allowed to say it doesn't know — is the best on the page, so the drawing
    now performs it end to end.

    A tapered channel with real walls. Three screens span the channel wall
    to wall — 201 regex rules, then e5 embeddings, then the SetFit head,
    cheapest first — labelled outside on level leaders. A continuous stream
    of messages falls in at the mouth; most are decided at a screen and ride
    a chute out to CLASSIFIED. The one message no layer is sure of lands on
    the 0.85 gate — a solid member drawn across the foot, the one edge in
    the channel nothing passes — pauses there, and is walked sideways to a
    human, where it rests. Below the gate, nothing is guessed.

    Carrier: the stream — five phased messages on three routes; at every
    instant something is falling, being tested, or being handed over. The
    still frame is honest: queued messages at the mouth, and the referred
    one resting beside the human it was handed to (data-rest, check 11/16).
    """
    H, a = 712, CLAY_G
    T1, T2, T3 = 8.6, 12.9, 15.5   # route periods — near-coprime, unfindable
    s = [head(H, "Applied — a classifier allowed to say it doesn't know",
              "Applied: a three-layer email classifier — 201 regex rules, then e5 embeddings, "
              "then a fine-tuned SetFit head, cheapest first — drawn as a sifting channel a "
              "stream of messages falls through. A message no layer is sure of stops at the "
              "0.85 confidence gate and is walked to a human instead of guessed at. It "
              "scores 0.979 macro-F1 — 2 mistakes on a 96-message evaluation set — measured "
              "with the rules layer alone; CI fails the build below 0.95. Inference runs in "
              "your browser: the int8 ONNX build is 22.8 megabytes, down from 90.4.",
              key="plate-4-applied.svg", col=(110, 762), frame=(41, 37.6, 26))]

    # ── the routes. Authored once here so the drawing and the motion cannot
    # disagree: the chutes the messages ride are the chutes the plate draws.
    P1 = "M440 104 C440 148 438 166 436 186 C434 208 420 224 342 232 C300 237 246 248 218 258"
    P2 = ("M440 104 C440 148 438 166 436 186 C434 214 436 250 438 276 "
          "C436 300 420 314 360 322 C316 328 250 340 222 348")
    # the walk to the human happens in translate keyframes (dv below), so the
    # refused message can be AUTHORED at its rest beside the human — with
    # motion off, the still frame shows the handover already made.
    s.append(f""".msg{{offset-rotate:0deg}}
.pa0{{offset-path:path('{P1}');animation:pa0 {T1}s {EASE} infinite;animation-delay:-3.1s}}
.pa1{{offset-path:path('{P1}');animation:pa1 {T1}s {EASE} infinite;animation-delay:-6.4s}}
@keyframes pa0{{0%{{offset-distance:0%;opacity:0}}5%{{opacity:1}}24%{{offset-distance:27%}}
  32%{{offset-distance:30%}}60%{{offset-distance:64%}}86%{{offset-distance:98%;opacity:1}}
  91%{{opacity:0;offset-distance:100%}}100%{{opacity:0;offset-distance:100%}}}}
@keyframes pa1{{0%{{offset-distance:0%;opacity:0}}5%{{opacity:1}}24%{{offset-distance:27%}}
  32%{{offset-distance:30%}}60%{{offset-distance:64%}}86%{{offset-distance:98%;opacity:1}}
  91%{{opacity:0;offset-distance:100%}}100%{{opacity:0;offset-distance:100%}}}}
.pb0{{offset-path:path('{P2}');animation:pb0 {T2}s {EASE} infinite;animation-delay:-5.2s}}
.pb1{{offset-path:path('{P2}');animation:pb1 {T2}s {EASE} infinite;animation-delay:-9.3s}}
@keyframes pb0{{0%{{offset-distance:0%;opacity:0}}4%{{opacity:1}}18%{{offset-distance:18%}}
  24%{{offset-distance:20%}}40%{{offset-distance:44%}}46%{{offset-distance:46%}}
  70%{{offset-distance:74%}}88%{{offset-distance:98%;opacity:1}}92%{{opacity:0;offset-distance:100%}}
  100%{{opacity:0;offset-distance:100%}}}}
@keyframes pb1{{0%{{offset-distance:0%;opacity:0}}4%{{opacity:1}}18%{{offset-distance:18%}}
  24%{{offset-distance:20%}}40%{{offset-distance:44%}}46%{{offset-distance:46%}}
  70%{{offset-distance:74%}}88%{{offset-distance:98%;opacity:1}}92%{{opacity:0;offset-distance:100%}}
  100%{{opacity:0;offset-distance:100%}}}}
/* the refused message: authored at rest beside the human; the loop replays
   its journey — inlet, three screens, the pause at the gate, the handover */
.dv{{animation:dv {T3}s {EASE} infinite}}
@keyframes dv{{0%,30%{{opacity:1;transform:translate(0,0)}}
  32%{{opacity:0;transform:translate(0,0)}}
  33%{{opacity:0;transform:translate(-208px,-385px)}}
  35%{{opacity:1;transform:translate(-208px,-385px)}}
  40%,43%{{transform:translate(-208px,-315px)}}
  47%,50%{{transform:translate(-208px,-225px)}}
  54%,57%{{transform:translate(-208px,-135px)}}
  61%,70%{{transform:translate(-208px,-44px)}}
  75%{{transform:translate(-146px,-32px)}}
  80%{{transform:translate(-66px,-11px)}}
  84%,100%{{opacity:1;transform:translate(0,0)}}}}
/* the human reacts: a small rise to receive, the moment the refused message
   arrives — same clock as the walk, so the nod can never miss the handover */
.hum{{animation:hum {T3}s {EASE} infinite}}
@keyframes hum{{0%,80%{{transform:translateY(0)}}84%{{transform:translateY(-3.5px)}}
  90%,100%{{transform:translateY(0)}}}}
</style>{ground(H)}""")

    s.append(f'<text x="440" y="54" text-anchor="middle" class="kick">VI · APPLIED</text>')
    s.append(f'<text x="440" y="84" text-anchor="middle" class="say" style="fill:{INK}">ALLOWED TO SAY IT DOESN’T KNOW</text>')

    # ── the channel: one composed instrument — walls, screens, chute guides,
    # gate, stream and the human, in a single <g> so the stream may pass
    # through the screens (which is the diagram's whole point).
    ch = []
    # walls — the left one drawn in three lengths, because the chutes leave
    # through real openings at their crossing heights; the right one stops
    # short of the foot, and that opening is the door to the human
    # walls at 3u — a full weight above the 2u screens, because a wall is the
    # thing the stream cannot pass and the drawing should say so (round 21
    # called the 1-2u channel "the most timid drawing in the set")
    wx = lambda y: 320 + 70 * (y - 120) / 348
    ch.append(f'<path d="M320 120L{wx(220):.1f} 220M{wx(244):.1f} 244L{wx(310):.1f} 310'
              f'M{wx(334):.1f} 334L390 468" stroke="{WIRE}" stroke-width="3"/>')
    ch.append(f'<path d="M560 120L{560 - 70 * 330 / 348:.1f} 450" stroke="{WIRE}" stroke-width="3"/>')
    # screens: wall-to-wall at their depth, perforated
    for sy in (186, 276, 366):
        wl = 320 + 70 * (sy - 120) / 348
        wr = 560 - 70 * (sy - 120) / 348
        ch.append(f'<path d="M{wl:.0f} {sy}H{wr:.0f}" stroke="{WIRE}" stroke-width="2" stroke-dasharray="7 5"/>')
        # level leader out to the label — perpendicular, never at an angle
        ch.append(f'<path d="M{wr:.0f} {sy}H586" stroke="{WIRE}" stroke-width="1"/>')
    # chute guides — the routes, drawn quietly so the still frame shows
    # them. RULE at full strength: the contrast gate is right that a
    # dimmed WIRE lands at 2.2:1, and 3:1 is the floor for marks that mean
    for d in (P1, P2):
        ch.append(f'<path d="{d}" fill="none" stroke="{RULE}" stroke-width="1" stroke-dasharray="2 6"/>')
    # each chute ends at a TERMINUS — a bar the exiting message visibly
    # arrives against before it fades. Round 21: "paths to nowhere, a third
    # of the plate's width spent fading into empty space."
    ch.append(f'<path d="M212 246V270M216 336V360" stroke="{WIRE}" stroke-width="2"/>')
    # the gate: a solid member across the foot — the one edge nothing passes
    ch.append(f'<rect x="390" y="468" width="100" height="4" fill="{a}"/>')
    ch.append(f'<path d="M490 470H586" stroke="{WIRE}" stroke-width="1"/>')
    # the walk to the human, drawn as the same faint guide
    ch.append(f'<path d="M446 458C500 462 560 476 620 494" fill="none" stroke="{RULE}" stroke-width="1" stroke-dasharray="2 6"/>')
    # the human: head and shoulders, on the plate, at the end of the walk —
    # and it REACTS (the .hum rise) when the refused message reaches it
    ch.append(f'<g class="hum"><g id="the-human"><circle cx="660" cy="497" r="8" fill="none" stroke="{INK2}" stroke-width="1.6"/>'
              f'<path d="M644 526C644 512 676 512 676 526" fill="none" stroke="{INK2}" stroke-width="1.6"/></g></g>')
    # the stream: four messages on the two decided routes, at 18u — round 21
    # measured the 14u tokens as too small to track on the dark slab...
    for cls in ("pa0", "pa1", "pb0", "pb1"):
        ch.append(f'<rect class="msg {cls}" x="-9" y="-9" width="18" height="18" rx="3.5" '
                  f'style="fill:{a};fill-opacity:{op(0.55)};stroke:{a};stroke-width:1.6"/>')
    # ...and the refused one, authored at rest beside the human
    ch.append(f'<rect class="dv" data-rest="the-human" data-rest-within="12" x="630" y="487" '
              f'width="18" height="18" rx="3.5" '
              f'style="fill:{INK2};fill-opacity:{op(0.7)};stroke:{INK2};stroke-width:1.6"/>')
    s.append('<g>' + "".join(ch) + '</g>')

    # the screen labels, on their level leaders
    s.append(f'<text x="594" y="191" class="key">201 REGEX RULES</text>')
    s.append(f'<text x="594" y="281" class="key">e5 EMBEDDINGS</text>')
    s.append(f'<text x="594" y="371" class="key">SETFIT HEAD</text>')
    s.append(f'<text x="594" y="213" class="fine">cheapest first —</text>')
    s.append(f'<text x="594" y="231" class="fine">most mail stops</text>')
    s.append(f'<text x="594" y="475" class="key" style="fill:{PINE}">0.85 GATE</text>')

    # what leaves the channel decided — a rotated tab at the left edge,
    # the one strip the stream can never enter
    s.append(f'<text transform="rotate(-90 128 300)" x="128" y="300" text-anchor="middle" class="kick">CLASSIFIED — DECIDED AT A SCREEN</text>')

    # the human's name, under the figure
    s.append(f'<text x="660" y="556" text-anchor="middle" class="lbl">A HUMAN</text>')
    s.append(f'<text x="400" y="510" text-anchor="middle" class="fine" style="fill:{INK3}">below the gate, nothing is guessed</text>')

    # ── the verdict. 0.979 is the number with an artifact behind it,
    # labelled for what it measures; the cascade's 0.9583 has none.
    s.append(f'<path d="M{L} 580H{R}" stroke="{RULE}"/>')
    s.append(f'<text x="{L}" y="628" class="hero">0.979</text>')
    s.append(f'<text x="330" y="606" class="lbl">MACRO-F1 · 96-MSG EVAL SET · 2 MISTAKES</text>')
    s.append(f'<text x="330" y="628" class="key" style="fill:{PINE}">RULES LAYER ONLY</text>')
    s.append(f'<text x="330" y="650" class="fine">SetFit off, embeddings emptied · CI fails below 0.95</text>')
    s.append(f'<text x="{L}" y="{H-30}" class="lbl">YOUR BROWSER</text>')
    s.append(f'<text x="300" y="{H-30}" class="fine">int8 ONNX · 90.4 MB → 22.8 MB</text>')
    s.append(f'<text x="{R}" y="{H-30}" text-anchor="end" class="fine" style="fill:{INK3}">never leaves your tab</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── PLATE VII
def plate_visualassist() -> str:
    """The depth sweep. Room: an instrument's field of view.

    NEW this round, at the client's choice. The skills banner has sold Swift
    since round one without a single Swift system on the page; this is the
    system — an iPhone app that turns ARKit LiDAR depth into spatial audio,
    haptics and speech for low-vision users. It is also the one system here
    with no live link, and the plate says why in plain words: it needs an
    iPhone with a lidar sensor. That is a reason, not an excuse.

    Carrier: the sweep — the phone's field of view oscillating across the
    obstacle field, on a curve that never stalls at the turn. The range
    rings drift outward continuously. Gesture: each obstacle blinks the
    moment the sweep crosses its bearing — and the crossing times are solved
    against the ACTUAL easing the sweep runs on. Round 21 solved them
    against a pure sine while the sweep ran the DRIFT bezier, and the live
    pass caught the consequence: points pulsing with the beam visibly
    elsewhere, causality broken at exactly the extreme bearings. The answer
    half of the claim is drawn too: audio arcs at the phone's ear flash with
    every detection — depth in, sound out.
    """
    H, a = 500, CLAY_G
    T, AMP = 8.9, 13.0             # sweep period and half-angle, degrees
    EX, EY = 238, 227              # the emitter — the phone's sensor

    # invert the DRIFT bezier: e(u) is progress through one half-sweep, so a
    # bearing phi is crossed at u with e(u) = (phi+AMP)/(2AMP). Bisection on
    # the y-polynomial, then the x-polynomial maps parameter to time.
    def _cross(q: float) -> float:
        p1x, p1y, p2x, p2y = .45, .05, .55, .95
        bez = lambda c1, c2, t: 3*(1-t)**2*t*c1 + 3*(1-t)*t**2*c2 + t**3
        lo, hi = 0.0, 1.0
        for _ in range(60):
            mid = (lo + hi) / 2
            if bez(p1y, p2y, mid) < q: lo = mid
            else: hi = mid
        return bez(p1x, p2x, (lo + hi) / 2)
    s = [head(H, "VisualAssist — LiDAR depth to spatial audio, in Swift",
              "VisualAssist: an iPhone app for low-vision users, written in Swift — ARKit "
              "LiDAR depth becomes spatial audio, haptics and speech, so the phone tells "
              "you what is in front of you. 7,177 lines across 38 Swift files, 5 CI "
              "workflows. It is the one system on this page you cannot click into, because "
              "it needs an iPhone with a lidar sensor.",
              key="plate-8-visualassist.svg", col=(118, 762), frame=(42, 64, 28))]
    # obstacle bearings (degrees off axis) and ranges — the field the sweep
    # reads. Pulse times fall where the sweep's sine crosses each bearing.
    PTS = [(-11.5, 196), (-6, 262), (-1.5, 152), (2.5, 236), (7, 180), (11, 272)]
    css = [f""".swp{{animation:swp {T}s {DRIFT} infinite;animation-delay:{-T/4}s}}
@keyframes swp{{0%{{transform:rotate({-AMP}deg)}}50%{{transform:rotate({AMP}deg)}}100%{{transform:rotate({-AMP}deg)}}}}
.ring{{animation:ring 11.7s linear infinite}}
@keyframes ring{{from{{stroke-dashoffset:0}}to{{stroke-dashoffset:-11}}}}"""]
    crossings = []
    for i, (phi, _r) in enumerate(PTS):
        # the sweep runs -AMP -> +AMP over 0-50% and back over 50-100%, DRIFT
        # eased per segment; solve each segment's bezier for this bearing
        q = max(0.0, min(1.0, (phi + AMP) / (2 * AMP)))
        t1 = 50 * _cross(q)
        t2 = 50 + 50 * _cross(1 - q)
        t1, t2 = sorted((t1, t2))
        crossings += [t1, t2]
        seg = "".join(
            f"{max(t-2.2,0):.1f}%{{transform:scale(1)}}{t:.1f}%{{transform:scale(1.7)}}"
            f"{min(t+2.2,100):.1f}%{{transform:scale(1)}}" for t in (t1, t2))
        css.append(f".pt{i}{{transform-box:fill-box;transform-origin:center;"
                   f"animation:pt{i} {T}s {BREATHE} infinite;animation-delay:{-T/4}s}}\n"
                   f"@keyframes pt{i}{{0%{{transform:scale(1)}}{seg}100%{{transform:scale(1)}}}}")
    # the output: audio arcs at the phone's left edge flash pink at EVERY
    # crossing — one detection, one utterance. Colour, not opacity, so the
    # authored frame stays the finished frame. Overlapping windows merge so
    # the keyframe percentages stay strictly increasing.
    ev: list[list[float]] = []
    for t in sorted(crossings):
        if ev and t - 1.7 <= ev[-1][1]: ev[-1][1] = min(t + 1.7, 100.0)
        else: ev.append([max(t - 1.7, 0.0), min(t + 1.7, 100.0)])
    aud = "".join(f"{a0:.1f}%{{stroke:{WIRE}}}{(a0+a1)/2:.1f}%{{stroke:{a}}}{a1:.1f}%{{stroke:{WIRE}}}"
                  for a0, a1 in ev)
    css.append(f".aud{{animation:aud {T}s linear infinite;animation-delay:{-T/4}s}}\n"
               f"@keyframes aud{{0%{{stroke:{WIRE}}}{aud}100%{{stroke:{WIRE}}}}}")
    s.append("\n".join(css) + f"</style>{ground(H)}")
    # the cone's falloff: dense at the sensor, thin where the points live —
    # authored per theme (light's old flat 0.64 wash drowned its own points)
    fo0, fo1 = (0.26, 0.05) if THEME == "dark" else (0.32, 0.07)
    s.append(f'<radialGradient id="fov" gradientUnits="userSpaceOnUse" cx="0" cy="0" r="290">'
             f'<stop offset="0" stop-color="{a}" stop-opacity="{fo0}"/>'
             f'<stop offset="1" stop-color="{a}" stop-opacity="{fo1}"/></radialGradient>')

    s.append(f'<text x="{L}" y="{TOP}" class="kick">VII · VISUALASSIST</text>')
    s.append(f'<text x="{R}" y="{TOP}" text-anchor="end" class="key">SWIFT · ARKIT · LIDAR</text>')
    s.append(f'<text x="{L}" y="88" class="say" style="fill:{INK}">CAN A PHONE TELL YOU WHAT IS IN FRONT OF YOU?</text>')

    # ── the scene: phone, sweep, range rings, obstacles. One composed
    # instrument — the sweep legitimately passes over everything in it.
    sc = []
    # the phone, drawn as a phone: body, screen line, the sensor it sweeps from
    sc.append(f'<rect x="176" y="168" width="58" height="118" rx="9" fill="none" stroke="{a}" stroke-width="2"/>')
    sc.append(f'<path d="M196 178H214" stroke="{a}" stroke-width="1.5" stroke-linecap="round"/>')
    sc.append(f'<circle cx="{EX}" cy="{EY}" r="3.5" fill="{a}"/>')
    # the audio out: two arcs at the phone's ear, flashing with each detection
    sc.append(f'<path class="aud" d="M170 220A8 8 0 0 0 170 234" fill="none" '
              f'style="stroke:{WIRE}" stroke-width="2" stroke-linecap="round"/>')
    sc.append(f'<path class="aud" d="M164 214A14 14 0 0 0 164 240" fill="none" '
              f'style="stroke:{WIRE}" stroke-width="2" stroke-linecap="round"/>')
    # the sweep: a wedge rotating about the sensor, filled with the radial
    # falloff and stroked at full accent so its edge stays legible (WCAG:
    # the component, not every channel of it).
    wr = 290
    wy = wr * math.tan(math.radians(10.4))
    sc.append(f'<g transform="translate({EX},{EY})"><path class="swp" '
              f'd="M0 0L{wr} {-wy:.0f}A{wr} {wr} 0 0 1 {wr} {wy:.0f}Z" '
              f'style="fill:url(#fov)" stroke="{a}" stroke-width="1.4"/></g>')
    # range rings, drifting outward — the depth field being read continuously
    for rr in (210, 280):
        y0 = rr * math.sin(math.radians(19))
        x0 = rr * math.cos(math.radians(19))
        sc.append(f'<path class="ring" d="M{EX+x0:.0f} {EY-y0:.0f}A{rr} {rr} 0 0 1 {EX+x0:.0f} {EY+y0:.0f}" '
                  f'fill="none" stroke="{WIRE}" stroke-width="1" stroke-dasharray="3 8"/>')
    # the obstacles: what the sweep finds, blinking as it crosses them
    for i, (phi, rr) in enumerate(PTS):
        px = EX + rr * math.cos(math.radians(phi))
        py = EY + rr * math.sin(math.radians(phi))
        sc.append(f'<circle class="pt{i}" cx="{px:.0f}" cy="{py:.0f}" r="4.5" fill="{a}"/>')
    s.append('<g>' + "".join(sc) + '</g>')

    # what the reading becomes
    s.append(f'<text x="{L}" y="400" class="fine">LIDAR DEPTH → SPATIAL AUDIO + HAPTICS + SPEECH</text>')
    s.append(f'<text x="{L}" y="424" class="key">7,177 LINES · 38 SWIFT FILES · 5 CI WORKFLOWS</text>')
    # the honest close: the only system here without a link, and why
    s.append(f'<text x="{L}" y="452" class="say" style="fill:{INK}">THE ONE SYSTEM HERE YOU CANNOT CLICK INTO</text>')
    s.append(f'<text x="{L}" y="{H-28}" class="fine" style="fill:{INK3}">no live link — it needs an iPhone with a lidar sensor</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── FOOTER
def plate_colophon() -> str:
    """The imprint. Room: a printer's colophon, shrunk to a footer.

    Centered, like the title page it answers — the serif's bracket made
    spatial, closing where it opened. The six product marks turn as a
    printer's device inside a drifting ring: the page's quietest motion,
    the arc's landing. One line of mechanism under it; the README's own
    footer carries the contact.
    """
    H, CX = 312, 440
    s = [head(H, "Colophon", "Colophon: every number on this page is re-derived in CI from a "
                             "pinned commit, except section one, which is attested and says so. "
                             "The page itself is animated SVG with no JavaScript and no server. "
                             "If a number here is wrong, it is wrong in public.",
              key="plate-7-colophon.svg", col=(118, 762), frame=(43, 155.7, 24),
              serif=True)]
    s.append(f""".ser{{font-family:'S',ui-serif,Georgia,'Times New Roman',serif;font-size:34px;fill:{INK}}}
.dev{{animation:dev 31s linear infinite}}
@keyframes dev{{from{{transform:rotate(0deg)}}to{{transform:rotate(360deg)}}}}
/* each mark counter-rotates about its own centre so it ORBITS upright —
   round 21's live pass caught the seven glyphs upside down for half of
   every 31s cycle, in both themes */
.cnt{{transform-box:fill-box;transform-origin:center;animation:cnt 31s linear infinite}}
@keyframes cnt{{from{{transform:rotate(0deg)}}to{{transform:rotate(-360deg)}}}}
.hal{{animation:hal 13.9s linear infinite}}
@keyframes hal{{from{{stroke-dashoffset:0}}to{{stroke-dashoffset:-44}}}}
</style>{ground(H)}""")
    s.append(f'<text x="{CX}" y="{TOP}" text-anchor="middle" class="kick">COLOPHON — EVERY NUMBER CHECKED IN CI</text>')

    # the serif answers the thesis — the only two sentences on this page the
    # machine did not derive, in the only face the machine does not use
    for i, ln in enumerate(["If a number here is wrong,", "it is wrong in public."]):
        s.append(f'<text x="{CX}" y="{110 + i*42}" text-anchor="middle" class="ser">{ln}</text>')

    # the printer's device: six marks turning slowly inside a drifting ring
    dev = [f'<path class="hal" d="M-52 0A52 52 0 1 1 52 0A52 52 0 1 1 -52 0" fill="none" stroke="{RULE}" stroke-width="1" stroke-dasharray="2 9"/>']
    dev.append('<g class="dev">')
    for k, (nm, c) in enumerate(LEGEND):
        ang = math.radians(k * 60)
        # ROUNDED, and it has to be. Unrounded these went into the file as the
        # full float repr, and libm does not agree to the last bit across
        # platforms: this machine emitted translate(...,6.999999999999995) and
        # CI's Linux emitted ...993, so the "assets match their generator"
        # check failed on a push whose build was byte-idempotent locally.
        # Trig output is not reproducible; its rounding is.
        x, y = round(30 * math.sin(ang), 3), round(-30 * math.cos(ang), 3)
        dev.append('<g class="cnt">' + logo(nm, x - 8, y - 8, 16, c) + '</g>')
    dev.append('</g>')
    s.append(f'<g transform="translate({CX},218)">' + "".join(dev) + '</g>')

    s.append(f'<text x="{CX}" y="{H-28}" text-anchor="middle" class="lbl">ANIMATED SVG · NO JAVASCRIPT · NO SERVER</text>')
    return "".join(s) + "</svg>"


PLATES = {
    "plate-0-thesis.svg": plate_thesis, "plate-0b-work.svg": plate_work,
    "plate-1-glyph.svg": plate_glyph,
    "plate-2-jetpack.svg": plate_jetpack,
    "plate-4-applied.svg": plate_applied, "plate-5-refusal.svg": plate_cadence,
    "plate-6b-automl.svg": plate_automl,
    "plate-8-visualassist.svg": plate_visualassist,
    "plate-7-colophon.svg": plate_colophon,
}

# ────────────────────────────────────────────────── mobile set
# At GitHub's real 324px column a label on an 880 canvas renders unreadable,
# so the phone gets its own plates: a 440 canvas on the SAME 13/21/34/55
# scale, carrying the hero and one thought. Each m-plate keeps a MOTIF of its
# section's room (the stamp, the copybook rules with real error labels, the
# bench bars, the sieve, the redaction bars, the dial arc, the sweep); the
# motifs are graphics only — no text, so no desc/claims churn. Round 21:
# every mobile plate also carries the page's smallest carrier, a highlight
# gliding along its accent rule, so the phone reader's page breathes too.
MW = 440


def _digits_row(y: float, n: int, x0: float, pitch: float, sc: float,
                start: int = 0) -> str:
    """A copybook rule with real error labels sitting on it (from the same
    pinned CSV the desktop field uses)."""
    _e = json.loads((ROOT / "errors.json").read_text())
    out = [f'<path d="M16 {y}H424" stroke="{RULE}" stroke-width="1"/>']
    for i in range(start, start + n):
        d = DIGITS[_e["true"][i]]
        out.append(f'<g opacity="{op(0.72)}" {digit(d, x0 + (i - start) * pitch, y - 150 * sc, sc, centre=pitch - 2)}>'
                   f'<path d="{d}" fill="none" stroke="{CLAY_G}" stroke-width="14" stroke-linecap="round"/></g>')
    return "".join(out)


def _motif(name: str) -> str:
    if name == "copybook":
        return _digits_row(212, 24, 34, 15.5, 0.055)
    if name == "bench":
        return (f'<path d="M300 84V148" stroke="{WIRE}" stroke-width="1"/>'
                f'<rect x="300" y="92" width="18.5" height="12" fill="{INK2}"/>'
                f'<rect x="300" y="118" width="118" height="12" fill="{CLAY_G}"/>')
    if name == "sieve":
        # compact and held above the body lines — the desktop channel owns
        # the full drawing; this is its monogram
        return (f'<g><path d="M330 70L348 132" stroke="{WIRE}" stroke-width="1.6"/>'
                f'<path d="M410 70L392 132" stroke="{WIRE}" stroke-width="1.6"/>'
                f'<path d="M334 86H406" stroke="{WIRE}" stroke-width="1.4" stroke-dasharray="5 4"/>'
                f'<path d="M338 102H402" stroke="{WIRE}" stroke-width="1.4" stroke-dasharray="5 4"/>'
                f'<path d="M342 118H398" stroke="{WIRE}" stroke-width="1.4" stroke-dasharray="5 4"/>'
                f'<rect x="348" y="138" width="44" height="3" fill="{CLAY_G}"/>'
                f'<circle cx="416" cy="156" r="6" fill="none" stroke="{INK2}" stroke-width="1.4"/></g>')
    if name == "redact":
        return (f'<rect x="300" y="84" width="110" height="12" rx="2" {redact()}/>'
                f'<rect x="300" y="104" width="110" height="12" rx="2" {redact()}/>'
                f'<rect x="300" y="124" width="110" height="12" rx="2" fill="{ROW}" stroke="{PINE}"/>')
    if name == "dial":
        out = ['<g>']
        for j in range(7):
            a0, a1 = j * 51.43 + 4, (j + 1) * 51.43 - 4
            p = lambda deg, r=34: (390 + r * math.sin(math.radians(deg)),
                                   104 - r * math.cos(math.radians(deg)))
            x0, y0 = p(a0); x1, y1 = p(a1)
            col = CLAY_G if j == 6 else ROW
            out.append(f'<path d="M{x0:.1f} {y0:.1f}A34 34 0 0 1 {x1:.1f} {y1:.1f}" '
                       f'fill="none" stroke="{col}" stroke-width="6"/>')
        th = math.radians(6 * 51.43 + 25.7)
        out.append(f'<path d="M{390 + 10*math.sin(th):.1f} {104 - 10*math.cos(th):.1f}'
                   f'L{390 + 26*math.sin(th):.1f} {104 - 26*math.cos(th):.1f}" '
                   f'stroke="{CLAY_G}" stroke-width="1.5"/></g>')
        return "".join(out)
    if name == "sweep":
        return (f'<g><circle cx="316" cy="116" r="3" fill="{CLAY_G}"/>'
                f'<path d="M338 92A34 34 0 0 1 338 140" fill="none" stroke="{CLAY_G}" stroke-width="2" stroke-linecap="round"/>'
                f'<path d="M352 78A54 54 0 0 1 352 154" fill="none" stroke="{CLAY_G}" stroke-width="2" stroke-linecap="round"/>'
                f'<circle cx="398" cy="104" r="4" fill="{CLAY_G}"/>'
                f'<circle cx="408" cy="132" r="4" fill="{CLAY_G}"/></g>')
    if name == "stamp":
        return (f'<g transform="translate(80,84) rotate(-8)">'
                f'<rect x="-52" y="-16" width="104" height="32" rx="5" fill="none" stroke="{INK3}" stroke-width="1.6"/>'
                f'<text x="0" y="4" text-anchor="middle" class="k" style="fill:{INK3};font-size:12px;letter-spacing:2px">ATTESTED</text></g>')
    return ""


def plate_mobile(accent: str, kicker: str, hero: str, unit: str,
                 line1: str, line2: str, desc: str,
                 layout: str = "left", motif: str = "", glide: float = 9.7) -> str:
    h = 224
    mid = layout == "center"
    ax = 'text-anchor="middle" ' if mid else ''
    tx = 220 if mid else 34
    hx, ha = (220, 'text-anchor="middle" ') if mid else ((406, 'text-anchor="end" ') if layout == "ledger" else (34, ''))
    rx, rw = (130, 180) if mid else (34, MW - 68)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {MW} {h}" width="{MW}" height="{h}" '
        f'role="img" aria-label="{desc}"><title>{kicker}</title><desc>{desc}</desc><style>'
        # both weights: .n is 600, and .u inherits it — see head()'s note on
        # why a synthesised bold is a per-platform rendering
        f"@font-face{{font-family:'M';font-weight:400;src:url(data:font/woff2;base64,{FONT}) format('woff2')}}"
        f"@font-face{{font-family:'M';font-weight:600;src:url(data:font/woff2;base64,{FONT600}) format('woff2')}}"
        f"text{{font-family:'M',ui-monospace,SFMono-Regular,Menlo,monospace}}"
        f".k{{font-size:13px;letter-spacing:2px;fill:{INK2}}}"
        f".n{{font-size:55px;letter-spacing:-1px;fill:{INK};font-weight:600}}"
        f".u{{font-size:34px;letter-spacing:-0.5px;fill:{INK2}}}"
        f".t{{font-size:21px;fill:{INK2}}}"
        # the glide: a light running the accent rule — constant speed (a
        # runner, not a pendulum: the pendulum's turns measured as stalls),
        # fading out at the far end and back in at the head
        f".gl{{animation:gl {glide}s linear infinite}}"
        f"@keyframes gl{{0%{{transform:translateX(0);opacity:1}}86%{{transform:translateX({rw-46}px);opacity:1}}"
        f"90%{{opacity:0}}91%{{transform:translateX(0);opacity:0}}95%{{opacity:1}}100%{{transform:translateX(0);opacity:1}}}}"
        f"@media (prefers-reduced-motion: reduce){{*{{animation:none!important}}}}"
        f"</style>"
        f'<rect width="{MW}" height="{h}" fill="{GROUND}" fill-opacity="0"/>',
        f'<text x="{tx}" y="40" {ax}class="k">{kicker}</text>']
    if layout == "ledger":
        # the account book opens with a double rule, and the figure sits at
        # the right edge — the desktop ledger's two signatures
        parts.append(f'<g><path d="M34 50H406M34 54H406" stroke="{accent}"/>'
                     f'<rect class="gl" x="34" y="49" width="46" height="6" fill="{INK}"/></g>')
    else:
        parts.append(f'<g><rect x="{rx}" y="52" width="{rw}" height="2" fill="{accent}"/>'
                     f'<rect class="gl" x="{rx}" y="51" width="46" height="4" fill="{INK}"/></g>')
    hero_y = 124
    parts.append(f'<text x="{hx}" y="{hero_y}" {ha}class="n">{hero}<tspan class="u">{unit}</tspan></text>')
    l_y = (168, 194)
    parts.append(f'<text x="{tx}" y="{l_y[0]}" {ax}class="t">{line1}</text>')
    parts.append(f'<text x="{tx}" y="{l_y[1]}" {ax}class="t">{line2}</text>')
    if motif:
        parts.append(_motif(motif))
    return "".join(parts) + "</svg>"


# (kicker, accent name, hero, unit, line1, line2, desc, layout, motif, glide s)
# The accent is the COLOUR'S NAME, resolved per theme at write time. Glide
# periods are all different, so no two plates on the phone breathe together.
MOBILE = {
 "m-0-thesis.svg": ("AYUSH YADAV · CINCINNATI, OH", "INK2", "6", " systems",
   "From SIMD kernels to the", "browser they run in.",
   "Ayush Yadav, a computer science graduate in Cincinnati, Ohio, open to "
   "full-time engineering roles: 6 systems, from SIMD kernels to the browser "
   "they run in.", "center", "", 8.1),
 "m-0b-work.svg": ("WORK · MIAMI UNIVERSITY", "INK2", "57.8", "M rows",
   "from 1.6M Oracle query logs —", "a year of it, attested.",
   "Experience, attested by the author rather than derived from a public "
   "repository: as ITSM Data Integration Intern at Miami University, a Python "
   "pipeline turned 1.6 million Oracle Analytics query logs into a 57.8 "
   "million-row field-usage table.", "ledger", "stamp", 10.9),
 "m-1-glyph.svg": ("GLYPH", "CLAY_G", "3.5", "×", "Someone else’s net, made", "faster by hand. 97.01% held.",
   "Glyph: a course-provided neural network, hand-optimised — 3.5 times faster on the committed dot benchmark, accuracy unchanged at 97.01 percent.",
   "left", "copybook", 12.3),
 "m-2-jetpack.svg": ("JETPACK", "CLAY_G", "6.4", "×", "Parallel gzip on JDK 25.", "The JDK intrinsic still wins.",
   "jetpack: parallel gzip on JDK 25, a 6.4 times speedup over one thread — and the JDK's own checksum intrinsic still wins.",
   "left", "bench", 9.1),
 "m-4-applied.svg": ("APPLIED", "CLAY_G", "0.979", "", "macro-F1, rules layer only.", "Below 0.85 it asks a human.",
   "Applied: an email classifier scoring 0.979 macro-F1 with the rules layer alone. Below the 0.85 confidence gate it asks a human rather than guessing.",
   "left", "sieve", 11.3),
 "m-5-refusal.svg": ("CADENCE", "PINE", "B", " only", "The app didn’t remember to", "filter. The database refused.",
   "Cadence: an unfiltered query run as tenant B returns B only. The app didn't remember to filter; PostgreSQL row-level security refused.",
   "left", "redact", 8.9),
 "m-6b-automl.svg": ("AGENTIC AUTOML", "CLAY_G", "44", "", "tools in the registry. The", "model holds its phase’s set.",
   "Agentic AutoML: dataset in, trained model out. Its registry holds 44 tool definitions, but the model only ever holds the set its phase needs.",
   "left", "dial", 12.9),
 "m-8-visualassist.svg": ("VISUALASSIST", "CLAY_G", "LiDAR", "", "Depth in, spatial audio out.", "Needs an iPhone’s sensor.",
   "VisualAssist: LiDAR depth in, spatial audio out — an iPhone app for "
   "low-vision users, in Swift. The one system here with no live link, "
   "because it needs an iPhone with a lidar sensor.", "left", "sweep", 10.1),
 "m-7-colophon.svg": ("COLOPHON", "RULE", "SVG", "",
   "No JavaScript, no server,", "no external assets.",
   "Colophon: this page is SVG with no JavaScript, no server and no "
   "external assets.", "center", "", 7.9),
}

# ────────────────────────────────────────────────── the build-time gate
# Cheap structural checks only. The REAL layout gate is build/gate.mjs.
import re as _re, sys as _sys, xml.dom.minidom as _xml

_fail = []


def _check_coverage(fn: str, svg: str) -> None:
    """Every character a plate draws must be in the charset of the face that
    will render it — a glyph outside its subset falls back to a platform font
    and NOTHING downstream can see it: the build succeeds, gate.mjs passes
    (the geometry is still legal), and the reader gets Menlo or DejaVu mid-
    word. font-weight INHERITS, so a <tspan class="unit"> inside a .sub text
    renders from the 600 face; the class stack is a union for that reason.
    """
    _ent = {'&amp;': '&', '&lt;': '<', '&gt;': '>', '&#39;': "'", '&quot;': '"'}
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
            face, chars = (('serif', SERIF_CHARS) if 'ser' in cls else
                           ('600', BOLD_CHARS) if cls & {'hero', 'sub', 'vast', 'n'} else
                           ('mono', MONO_CHARS))
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
    for fn, gen in PLATES.items():
        path = _out / fn
        path.write_text(gen())
        try:
            _xml.parseString(path.read_text())
        except Exception as e:
            _fail.append(f"{_theme}/{fn}: MALFORMED XML — {e}")
        if _theme == "dark":                    # text is theme-invariant
            _check_coverage(fn, path.read_text())
        print(f"{_theme:5s} {fn}: {path.stat().st_size:,} bytes")
    for _fn, (_k, _acc, _n, _u, _l1, _l2, _desc, _lay, _mo, _gl) in MOBILE.items():
        _svg = plate_mobile(globals()[_acc], _k, _n, _u, _l1, _l2, _desc, _lay, _mo, _gl)
        (_out / _fn).write_text(_svg)
        if _theme == "dark":
            _check_coverage(_fn, _svg)
    print(f"{_theme:5s} mobile set: {len(MOBILE)} plates at {MW}w")
set_theme("dark")

# ────────────────────────────────────────────────── alt/desc/README agreement
# Every description is authored once in ALT and must reach the README verbatim.
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
