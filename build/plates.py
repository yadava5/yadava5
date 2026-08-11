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
SERIF600 = base64.b64encode((ROOT / "serif-600-subset.woff2").read_bytes()).decode()
FONTSERIF = base64.b64encode((ROOT / "serif-subset.woff2").read_bytes()).decode()

# The mono cell, in px, at the size and tracking every label is set in. The
# arrow below advances exactly one of these so a line containing it measures
# the same as a line of type — which is what keeps checks 5, 12 and 19 honest
# about a mark that is a path rather than a glyph.
CELL_13 = 13 * 618 / 1000 + 0.4      # .fine / .lbl / .kick — 8.434px

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
    #a59c91 = 4.25:1 on night paper; the light lift takes it to 0.82, which
    composites to #4b463b = 7.47:1 on day paper (the un-lifted 0.55 would be
    #827a6a = 3.38:1, which also clears). Both sides of the branch are
    measured, as hexes rather than as a direction — a comment in a file whose
    doctrine is "no unmeasured alpha" does not get to hedge.
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
         serif: bool = False, bold: bool = True) -> str:
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
    # 'S' 400 — the serif voice proper — is only embedded where a plate speaks
    # in it. Measured, the face swap made every file smaller rather than larger:
    # Fragment Mono's subset is half JetBrains', and Fraunces' two beat
    # Gelasio's one.
    #
    # 'S' 600 was documented here as riding in EVERY plate, "because the heroes
    # are set in it and they are the emotional centre of each one". True of
    # seven plates and false of two: the title page and the colophon have no
    # hero and no .sub, so they shipped a ~5.4 KB base64 payload that no glyph
    # ever requested — twice over, counting the light twins. The comment was
    # the reason nobody looked. It is conditional now, and gate.mjs enforces
    # BOTH directions: a declared face nothing renders is dead payload, and a
    # rendered face nothing declares is a platform fallback. Dropping the face
    # is only safe because the second half exists.
    ser = (f"@font-face{{font-family:'S';font-weight:400;"
           f"src:url(data:font/woff2;base64,{FONTSERIF}) format('woff2')}}\n") if serif else ''
    ser600 = (f"@font-face{{font-family:'S';font-weight:600;"
              f"src:url(data:font/woff2;base64,{SERIF600}) format('woff2')}}\n") if bold else ''
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="{VB_X} 0 {VB_W} {h}" width="{VB_W}" height="{h}" role="img" aria-label="{desc}" data-col="{col[0]},{col[1]}"{fr}>
<title>{title}</title><desc>{desc}</desc>
<style>
@font-face{{font-family:'M';font-weight:400;src:url(data:font/woff2;base64,{FONT}) format('woff2')}}
{ser600}{ser}text{{font-family:'M',ui-monospace,SFMono-Regular,Menlo,monospace}}
.hero{{font-size:55px;letter-spacing:-1px;fill:{INK};font-weight:600;font-family:'S',Georgia,serif}}
.sub{{font-size:34px;letter-spacing:-0.5px;fill:{INK};font-weight:600;font-family:'S',Georgia,serif}}
.unit{{font-size:34px;letter-spacing:-0.5px;fill:{INK2}}}
.say{{font-size:21px;fill:{INK2}}}
.lbl{{font-size:13px;letter-spacing:1.6px;fill:{INK2}}}
.key{{font-size:13px;letter-spacing:1.6px;fill:{INK}}}
.fine{{font-size:13px;letter-spacing:0.4px;fill:{INK2}}}
.kick{{font-size:13px;letter-spacing:2.4px;fill:{INK3}}}
@media (prefers-reduced-motion: reduce){{*{{animation:none!important}}}}
"""


def ground(h: int, x: float = VB_X, w: float = VB_W) -> str:
    """The sheet. THIS RECT MUST BE FIRST IN DOCUMENT ORDER — see below.

    It used to paint nothing (fill-opacity 0) and exist only so gate.mjs could
    read a contrast ground off it. Now it paints: the plate is a sheet of the
    portfolio's own paper laid on GitHub's page, which is the case-file idiom
    that property already uses, and it means every ratio the gate computes is
    against paper this design owns rather than a canvas it borrows.

    `x`/`w` default to the desktop viewBox. The mobile set passes its own
    (0, 440): all EIGHTEEN files are one sheet of the same paper, and until
    2026-08-08 only the nine desktop ones were, because this function closed
    over VB_X/VB_W and the phone had a hand-written rect next door.

    ORDER IS LOad-BEARING. gate.mjs:556 takes its contrast ground from the
    computed fill of the FIRST <rect> in document order, ignoring fill-opacity.
    Emit anything before this — including the frame below — and all 36 files
    grade every colour against the wrong ground, and they do it quietly.

    The frame is not decoration. Day paper measures 1.26:1 against GitHub's
    white and night paper 1.65:1 against its dark canvas: perceptible as a
    tint, invisible as an object. The WIRE edge (4.14 day / 4.21 night) is
    what makes it read as a sheet. It is a full-canvas rect, so gate.mjs
    filters it out of both `drawables` (gate.mjs:156-161) and check 12's
    element list by the same bbox rule that drops the slab — it cannot
    straddle anything, and its own contrast is not graded, which is why WIRE
    is measured here in the comment. That rule is `bbox >= canvas - 2` in BOTH
    axes, so it holds on the 440x224 phone canvas too, where the frame's bbox
    is 439x223 — one unit of margin, not the desktop's comfortable slack.

    THE EDGE IS 1u ON BOTH SHEETS, AND THAT IS A RULING, NOT AN OVERSIGHT.
    One authored unit buys `column / viewBox_width * dpr` device pixels. Below
    1, the browser composites the stroke with the paper behind it and the
    RENDERED contrast is not the authored 4.21 / 4.14. Measured, worst cases,
    dpr 1 only: desktop day 2.91:1 in a 560px column, mobile day 2.35:1 in a
    288px column. At dpr 2 or 3 — every phone anyone actually holds — all
    eighteen files measure 4.08-4.21, i.e. essentially the authored ratio.

    A heavier mobile frame was measured and declined. 1.5u is the only weight
    that clears 3.0 at every dpr-1 column down to 288 (day 3.07 / 4.02 / 4.14
    at 288 / 343 / 390), but 1.5u of 440 is 0.341% of the phone sheet against
    1u of 708 = 0.141% of the desktop one: 2.4x the relative weight, for every
    reader at every dpr, to serve resized desktop windows. Two sets drawn by
    two different hands is a worse defect than the one it fixes.

    The failing quantity is sub-pixel rendering, not this colour. Every 1u
    mark in the system — grid rules, connectors, axis hairlines — dilutes
    identically at the same threshold; the frame is only the mark that got
    measured. The 3.0 floor is a floor on AUTHORED colour at AUTHORED
    geometry. Written down so the next audit does not rediscover it and ship
    the heavier frame this ruling declined.
    """
    return (f'<rect x="{x:g}" width="{w:g}" height="{h}" fill="{GROUND}"/>'
            f'<rect x="{x + 0.5:g}" y="0.5" width="{w - 1:g}" height="{h - 1}" '
            f'fill="none" stroke="{WIRE}" stroke-width="1"/>')


def arrow(x: float, y: float, w: float = CELL_13, ink: str | None = None) -> str:
    """A rightwards arrow, drawn. Never the character U+2192.

    Fragment Mono does not carry →, and a glyph outside the embedded subset
    falls back to a PLATFORM font silently. That is not hypothetical: the
    sibling property does exactly this today — its ⟶ renders at 17px inside a
    9.891px monospaced cell, 72% over, in a different typeface per reader,
    across 91 occurrences. charsets.py therefore omits the character so the
    coverage gate fails loudly on anyone who types it, and labels call this.

    The shaft plus head occupy one tracked mono cell, so a run of type with an
    arrow in it advances exactly as if the arrow were a glyph. Stroke 1.2 keeps
    it inside gate.mjs's hairline rule (`stroke-width <= 2`), which is what
    lets it sit on the same baseline as type without reading as a collision.
    """
    c = ink or INK2
    x0, x1 = x + 1.5, x + w - 1.6      # side bearings, as a real glyph carries
    return (f'<path d="M{x0:.2f} {y - 4:.2f}H{x1:.2f}M{x1 - 2.6:.2f} {y - 6.1:.2f}'
            f'L{x1:.2f} {y - 4:.2f}L{x1 - 2.6:.2f} {y - 1.9:.2f}" fill="none" '
            f'stroke="{c}" stroke-width="1.2" stroke-linecap="round" '
            f'stroke-linejoin="round"/>')


def arrowed(x: float, y: float, cls: str, before: str, after: str,
            ink: str | None = None) -> str:
    """One label reading `before → after`, with the arrow drawn as a path.

    Pass the two halves WITHOUT padding spaces; the gaps are placed
    geometrically. They have to be — the first version padded the strings and
    the arrow came out flush against the following word, because SVG collapses
    leading whitespace in a <text> run by default. Spacing that depends on a
    space character surviving XML whitespace handling is spacing you have not
    actually specified.

    The layout is exactly "before␣→␣after" on the mono grid — the arrow takes
    the cell at len(before)+1 and the second run starts at len(before)+3 — so
    the line measures the same as if the mark were a glyph, which is what
    keeps checks 5, 12 and 19 telling the truth about it.
    """
    xa = x + (len(before) + 1) * CELL_13
    return (f'<text x="{x}" y="{y}" class="{cls}">{before}</text>'
            + arrow(xa, y, ink=ink)
            + f'<text x="{x + (len(before) + 3) * CELL_13:.2f}" y="{y}" class="{cls}">{after}</text>')


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

    THE ESCAPE'S UNSTATED PREMISE, now stated: it assumes the fill is DARKER
    THAN THE GROUND. A contrast ratio is unsigned, so 1.29 says a bar is mute
    and says nothing about which side of the paper it is mute on — and this
    bar's whole meaning is its polarity. Darker than the sheet is removal;
    lighter is a highlight. The gate is structurally blind to that flip, which
    is exactly how the phone shipped one; see the note in _motif().

    The 1.29 is not a number to fix. On paper, a mute fill whose boundary
    carries the object is what a redaction looks like; a high-contrast bar is
    a blackout that shouts, which inverts the motif's tone as surely as the
    sign flip inverted its meaning. Do not darken REDACT to raise it.
    """
    return f'fill="{REDACT}" stroke="{WIRE}" stroke-width="1.4"'


# ────────────────────────────────────────────────────────────── PLATE 0
def plate_thesis() -> str:
    """The title page and index. Room: a book's opening.

    Who / what / where in twenty seconds: name, one serif sentence, contact,
    one line of languages (the five skill bands of round 20 were the least
    differentiated content in the best real estate — cut), and the index of
    sections with dot leaders, framed as the portfolio's manifest card. The
    index is where the reader is taught the document's system: one mark per
    system, one accent that means BEING READ, and the section's answer
    compressed to a clause.

    Carriers: the dot leaders DRIFT toward their numerals, and the title-page
    ornament turns like a compositor's dingbat. Round 21 measured this plate
    at zero gestures in 270 samples — a carrier and nothing else, ranked
    last of nine, on the first thing anyone sees. So the index is now READ:
    row by row, in order, each leader lights to full ink, its name lifts to
    full ink, its numeral takes clay and its mark swells — the reader's eye
    walking the table of contents — and once per cycle the whole index rings
    together,
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
              col=(118, 762), frame=(44, 71.5, 26), serif=True, bold=False)]
    s.append(f""".ser{{font-family:'S',ui-serif,Georgia,'Times New Roman',serif;font-size:34px;fill:{INK}}}
.orn{{transform-box:fill-box;transform-origin:center;animation:orn 27s linear infinite}}
@keyframes orn{{from{{transform:rotate(45deg)}}to{{transform:rotate(405deg)}}}}
/* the leaders drift toward their numerals — 75u is ten dash periods, so the
   wrap is invisible by construction */
@keyframes ld{{from{{stroke-dashoffset:0}}to{{stroke-dashoffset:-75}}}}
""")
    # The ornament and the leader drift are the CARRIER; the read below is the
    # GESTURE. Both were cut in round 24 on the argument that camo serves an
    # arbitrary frame, so ambient motion buys nothing — which holds for the
    # gesture and inverts for the carrier. A drifting leader field says the
    # same thing in every frame: it cannot be caught mid-lie, and it is alive
    # whichever instant a reader gets. The gesture is the one that most
    # readers miss. Cutting the carrier and keeping the gesture kept the
    # fragile half. motion.mjs's header records that this page has already run
    # the experiment: v2 made stillness legal, eight of ten plates froze, and
    # the verdict was "very static feel" — the only plate spared was the one
    # in continuous travel.
    # the read: rows I..VII light in order across the first 90% of the clock,
    # then the chord — every leader, name, numeral and mark together at
    # 92.5-97.5%. Colour animations only, so the authored frame stays the
    # finished frame.
    MARKS = [None, "JETPACK", "GLYPH", "AUTOML", "CADENCE", "APPLIED", "VISUALASSIST"]
    for i, mk in enumerate(MARKS):
        w0, w1 = i * 90 / 7 + 0.8, (i + 1) * 90 / 7 - 0.8
        s.append(f".ldc{i}{{animation:ld 9.4s linear infinite,ldc{i} {TC}s linear infinite}}"
                 f"@keyframes ldc{i}{{0%,{w0:.1f}%{{stroke:{RULE}}}{w0+1.2:.1f}%,{w1:.1f}%{{stroke:{INK}}}"
                 f"{w1+1.2:.1f}%,92.5%{{stroke:{RULE}}}93.8%,96%{{stroke:{INK}}}97.5%,100%{{stroke:{RULE}}}}}")
        # the row's name lifts INK2 -> INK while it is read: the manifest
        # card's `.stamped b{color:var(--ink)}`, translated. The animation is
        # ON THE TSPAN, and the tspan carries no fill of its own. A fill
        # animated on the parent <text> never reaches a tspan that has one —
        # the keyframe runs, check 13 sees a property animate, and nothing
        # changes on screen. That is 6aec558 exactly, on this same plate: an
        # instrument-satisfying no-op. Nor a presentation attribute on the
        # tspan, which would report as overridden to check 15. So the tspan
        # inherits .fine's INK2 and owns nothing but the animation.
        s.append(f".rw{i}{{animation:rw{i} {TC}s linear infinite}}"
                 f"@keyframes rw{i}{{0%,{w0:.1f}%{{fill:{INK2}}}{w0+1.2:.1f}%,{w1:.1f}%{{fill:{INK}}}"
                 f"{w1+1.2:.1f}%,92.5%{{fill:{INK2}}}93.8%,96%{{fill:{INK}}}97.5%,100%{{fill:{INK2}}}}}")
        # the numeral takes CLAY while its row is read. CLAY, not the mark's
        # own tone: when the six project hues collapsed into one ink family,
        # hues[mk] resolved to INK2 for every row, so the numeral animated
        # INK -> INK2 and the row being READ came out DIMMER than its
        # neighbours. No gate can see that — both tones clear their floors and
        # the animation still moves, so checks 10 and 13 are satisfied by a
        # backwards read. Caught by looking. No longer gated on the mark
        # either: under the hue system row I had no section hue to take, but
        # under ink-state CLAY means "being read", and row I is read too.
        s.append(f".nm{i}{{animation:nm{i} {TC}s linear infinite}}"
                 f"@keyframes nm{i}{{0%,{w0:.1f}%{{fill:{INK}}}{w0+1.2:.1f}%,{w1:.1f}%{{fill:{LEGEND_READ}}}"
                 f"{w1+1.2:.1f}%,92.5%{{fill:{INK}}}93.8%,96%{{fill:{LEGEND_READ}}}97.5%,100%{{fill:{INK}}}}}")
        # the mark swells. Row I's mark is not a product logo — no repo, no
        # logos.json entry — but it is no longer NO mark: round 23 gives it
        # the section's own device, a miniature of the attested stamp, so the
        # index teaches one rule with no exception (the one row without a
        # glyph read as an omission, not a distinction).
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

    # ── the index: the portfolio's `run 042 — manifest` card idiom — mono
    # rows, dot leaders, numerals right, and the read-chase is that card's
    # `.stamped` promotion. This is the handshake between the two surfaces.
    #
    # UNBOXED in round 23. The card was a full outlined rectangle here, and
    # the house-style audit was blunt about the form: hairlines are the only
    # divider in this estate — the sites contain content with hairline RULES
    # between rows, never a surrounding stroked box. So the frame is now two
    # hairlines, one opening the table and one closing it, spanning exactly
    # the rows' own ink (marks at 200 to numerals at 690). The closing rule
    # sits at y=514, within check 12's tolerance of the old box edge, so the
    # declared frame stands.
    s.append(f'<text x="{CX}" y="330" text-anchor="middle" class="kick">INDEX</text>')
    s.append(f'<path d="M200 340H690" stroke="{RULE}"/>')
    s.append(f'<path d="M200 514H690" stroke="{RULE}"/>')
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
            s.append(f'<g class="ix{i}">' + logo(mark, 200, y - 13, 16, INK2) + '</g>')
        elif name == "WORK":
            # section I's own device at index scale: a miniature of the
            # ATTESTED stamp — rotated hollow rect, one line of "text" —
            # centred where a product mark's 16u box would put it, in the
            # marks' INK2, swelling on the same read clock
            s.append(f'<g class="ix{i}"><g transform="translate(208,{y-5}) rotate(-8)">'
                     f'<rect x="-7.5" y="-5.5" width="15" height="11" rx="2" '
                     f'fill="none" stroke="{INK2}" stroke-width="1.3"/>'
                     f'<path d="M-4 0.5H4" stroke="{INK2}" stroke-width="1.3"/></g></g>')
        s.append(f'<text x="228" y="{y}" class="fine">'
                 f'<tspan class="rw{i}">{name}</tspan>'
                 f'<tspan fill="{INK3}"> — {tag}</tspan></text>')
        lx = 228 + len(f"{name} — {tag}") * 8.2 + 14   # this row's text end
        # stroke via style, not attribute: the ldc chase animates it, and a
        # presentation attribute would report as overridden to check 15
        s.append(f'<path class="ldc{i}" d="M{lx:.0f} {y-4}H636" style="stroke:{RULE}" '
                 f'stroke-width="1.5" stroke-dasharray="1.5 6"/>')
        s.append(f'<text x="690" y="{y}" text-anchor="end" class="key nm{i}">{num}</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────── PLATE I — WORK
def plate_work() -> str:
    """The ledger. Room: an account book.

    A year of paid engineering and a national competition, none of it in a
    repository a reader can clone — so the warrant is testimony, and the
    plate is the document testimony lives in: an account book. Date column
    left, item in the middle, AMOUNTS RIGHT-ALIGNED AT THE PAGE EDGE, full-
    width row rules, a double rule opening and closing the account.

    THE LEDGER NOW HOLDS STILL. Round 24 deleted the auditor's scan, its
    tally pulses and the stamp's re-ink — not as polish but as a retraction:
    gate.mjs's new moving-hairline check proved the scan crossed "DATAFEST
    2026" and both employment dates somewhere in every loop, and GitHub
    serves these plates through camo as an <img>, so the frame a reader
    lands on is arbitrary. A travelling rule that can render a true claim
    struck through is worse than no motion, and an account book has no
    reason to animate. What remains is the plate's one semantic device: the
    two linkage bars run tick-streams at rates proportional to 99.6 and 32,
    so the comparison performs its own fractions — and nothing else moves.
    """
    H = 676
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
              frame=(44, 63.5, 21))]
    # the linkage bars state their fractions twice — length, and the rate of
    # the tick-stream inside each: 99.6 against 32, a 3.1x flow difference the
    # eye reads without the caption (12u is one dash cycle, so wraps are
    # seamless). This is the plate's ONLY motion — see the docstring.
    s.append(f""".bf0{{animation:bf0 {12/(0.28*99.6):.3f}s linear infinite}}
.bf1{{animation:bf1 {12/(0.28*32):.3f}s linear infinite}}
@keyframes bf0{{from{{stroke-dashoffset:0}}to{{stroke-dashoffset:-12}}}}
@keyframes bf1{{from{{stroke-dashoffset:0}}to{{stroke-dashoffset:-12}}}}
""")
    s.append(f"</style>{ground(H)}")

    s.append(f'<text x="{L}" y="{TOP}" class="lbl">ACCOUNT OF A YEAR’S PAID WORK</text>')
    s.append(f'<text x="{R}" y="{TOP}" text-anchor="end" class="lbl">No. I — WORK</text>')
    # a ledger opens and closes with a double rule
    s.append(f'<path d="M{L} 68H{R}M{L} 72H{R}" stroke="{RULE}"/>')
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
        s.append(f'<text x="290" y="{y}" class="lbl">{lab}</text>')
        s.append(f'<text x="290" y="{y+20}" class="fine">{det}</text>')
        s.append(f'<text x="{R}" y="{y}" text-anchor="end" class="sub">{amt}</text>')
        s.append(f'<path d="M{L} {y+34}H{R}" stroke="{RULE}"/>')

    s.append(f'<text x="{L}" y="376" class="kick">DATAFEST 2026</text>')
    s.append(f'<text x="290" y="376" class="key">TEAM LEAD OF 3 · NATIONAL ASA</text>')
    s.append(f'<path d="M{L} 390H{R}" stroke="{RULE}"/>')

    s.append(f'<text x="290" y="418" class="lbl">HOLDOUT AUC, 349K PATIENTS</text>')
    s.append(f'<text x="290" y="438" class="fine">90-day care utilisation, SHAP-explained</text>')
    s.append(f'<text x="{R}" y="418" text-anchor="end" class="sub">0.90</text>')
    s.append(f'<path d="M{L} 452H{R}" stroke="{RULE}"/>')

    s.append(f'<text x="290" y="480" class="lbl">OF LINKAGE PRESERVED</text>')
    s.append(f'<text x="290" y="500" class="fine">7.7M encounters · DuckDB + Polars</text>')
    s.append(f'<text x="{R}" y="480" text-anchor="end" class="sub">99.6%</text>')
    # the linkage claim is a comparison, so draw the comparison twice over:
    # LENGTH (widths always 300*frac from the value beside them), full ink for
    # the preserved fraction against half ink for the naive one (the light
    # theme's black-bar weight, ported), and the tick-streams above flowing at
    # the two rates — the one chart on the plate, finally its loudest
    for j, (frac, tag, fill, cls) in enumerate([(0.996, "star", INK, "bf0"),
                                                (0.32, "32% naive", INK2, "bf1")]):
        # 508, not 512: round 24's stamp tighten put the stamp's rotated top
        # edge at y=543.8, which cut straight through the "32% naive" label
        # (bbox to ~546.5) — a label half-in, half-out of a frame is neither
        # contained nor clear, and check 3 is right to refuse it. The bars
        # rise 4u and the stamp drops 4u; both clearances are now ~5.5u, and
        # the stamp's foot stays ~6u clear of the source line at 652.
        yy = 508 + j * 20
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
    s.append(f'<g transform="translate(600,592) rotate(-7)"><g>'
             f'<rect x="-110" y="-31" width="220" height="62" rx="8" fill="none" stroke="{INK3}" stroke-width="2"/>'
             f'<text x="0" y="-2" text-anchor="middle" class="say" style="fill:{INK3};letter-spacing:4px">ATTESTED</text>'
             f'<text x="0" y="22" text-anchor="middle" class="kick">ON MY WORD</text>'
             f'</g></g>')

    # the source footer, in the grammar every plate now closes with — this
    # section's source is testimony, and the line says so plainly
    s.append(f'<text x="{L}" y="652" class="fine" style="fill:{INK3}">source: my word — not derivable from a public repo</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── PLATE II
def plate_jetpack() -> str:
    """The bench sheet. Room: a test-bench record.

    The question is "is hand-vectorised code actually faster?", and the
    honest answer is BOTH WAYS: 6.4x on the parallel path, and a checksum
    that loses to the JDK's own intrinsic, printed here as the reference.

    The plate's one moving device (round 24's budget) is the bounded
    in-flight window run as a true conveyor — four blocks in continuous
    descent, drained in order at the foot, each keyframe set phased in
    geometry so frame zero is the authored queue. The per-bar tick-streams
    are stilled to drawn perforation: rate-as-motion read as texture at the
    arbitrary frame camo actually serves, and the lengths already argue.
    """
    H, LOOP, a = 604, 11.3, CLAY_G
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
              key="plate-2-jetpack.svg", frame=(36, 64, 13))]
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
    # Round 24 stilled the five tick-streams: one semantic device per plate,
    # and this plate's is the conveyor — the bounded in-flight window, the
    # engineering idea the section leads with. The bars keep the perforated
    # texture as DRAWN dashes (the comparison still reads at any frame);
    # only the drift is gone.
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
    def lane(y, nm, val, w, mine, cls, tag="", ref=False):
        # three tones, three standings: CLAY_G is mine, PINE is the reference
        # that stands, INK2 is a baseline I merely measured. Before this the
        # intrinsic wore the same INK2 as the two things it beats, so the
        # longest bar on the plate — the whole argument of the second lane —
        # was drawn in the losers' colour.
        fill = PINE if ref else (a if mine else INK2)
        s.append(f'<text x="{L}" y="{y}" class="fine">{nm}</text>')
        s.append(f'<text x="412" y="{y}" text-anchor="end" class="key">{val}</text>')
        s.append(f'<g><rect x="470" y="{y-11}" width="{w:.1f}" height="14" fill="{fill}"/>'
                 f'<path d="M470 {y-4}H{470+w:.1f}" stroke="{GROUND}" '
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
    lane(460, "java.util.zip intrinsic", "14.06", 260, False, "sb2", ref=True)
    s.append(f'<text x="{L}" y="492" class="fine" style="fill:{INK}">not beaten — the reference stands</text>')

    # the verification readout: the known-answer vector the repo commits
    # (Adler32Test.java:36-37), fast path against reference, byte for byte
    s.append(f'<text x="{L}" y="532" class="lbl">SIMD ADLER-32</text>')
    s.append(f'<text x="330" y="532" class="say" style="fill:{INK}">11E60398</text>')
    s.append(f'<text x="{L}" y="564" class="lbl">java.util.zip</text>')
    s.append(f'<text x="330" y="564" class="say" style="fill:{INK}">11E60398</text>')
    s.append(f'<rect x="330" y="542" width="112" height="2" fill="{a}"/>')
    s.append(f'<text x="560" y="550" class="lbl" style="fill:{PINE}">identical</text>')
    s.append(f'<text x="{L}" y="588" class="fine" style="fill:{INK3}">source: benchmarks/jmh-results-rigorous.json</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── PLATE III
def plate_glyph() -> str:
    """The copybook. Room: a handwriting practice sheet.

    The authorship is stated on the plate because round 20 overclaimed it:
    the network was COURSE-PROVIDED (after Nielsen); the optimisation is the
    work, with Shree Chaturvedi credited; the browser application is the
    author's own. The question becomes "how much faster can you make code
    you didn't write?" and the committed benchmarks answer it both ways:
    3.5x on the 256 dot kernel, 10.7x SLOWER on the small axpy — parallelism
    has a floor, and printing the inversion is the point of the page.

    The axpy figure read 6.9x until 2026-08-10, and the correction is a
    sourcing one rather than an arithmetic one: 6.9 was the honest ratio in
    docs/benchmarks/bench_summary.csv, which is the December record taken on
    a different, fanless machine that glyph's own ENVIRONMENT.md had already
    retired in favour of the 2026-08-02 M1 Pro runs. Both ratios on this
    plate now come from that reference machine. The dot figure survives the
    move at 3.5 only because the run glyph names as canonical agrees with the
    old CSV to one decimal; the other 2026-08-02 pair would have drawn 3.6.

    The net reads handwriting, so its 299 failures are drawn as failed
    homework: ruled baselines edge to edge, an amber margin line, every mark
    the true label of one missed image — the 220 in grey ink, the 79 the net
    was SURE about in heavy amber, so the field's own hue count is the 79.
    The plate's ONE motion (round 24's budget) is the one that re-derives a
    claim: the pen draws the hero 3.5 stroke by stroke once per loop, over a
    half-ink ghost of itself, so the answer is never absent. The nib that
    used to ride the field is gone — ambient travel, meaningless on the
    arbitrary frame a camo-served <img> actually shows a reader.
    """
    H, LOOP, SET, a = 576, 9.1, 7.6, CLAY_G
    NIB = 18.2                     # the nib's circuit — 2 x LOOP, commensurate
    s = [head(H, "Glyph — borrowed code made 3.5x faster, same 97.01%",
              "Glyph: a course-provided C++ MNIST network, hand-optimised — AVX-512, AVX2 and "
              "NEON kernels over a scalar fallback, written with Shree Chaturvedi; the React "
              "and TypeScript browser app is the author's own. The committed benchmarks "
              "answer both ways: 3.5 times faster on the 256 dot kernel under OpenMP and "
              "native codegen, and 10.7 times slower on the 128 axpy, because parallelism has "
              "a floor. Accuracy is unchanged at 97.01 percent on the 10,000-image MNIST "
              "test set, which means 299 wrong — every one of them drawn as a grid of the "
              "labels it missed, and the 79 it was most confident about drawn in a heavier "
              "stroke.", key="plate-1-glyph.svg",
              col=(96, 770), frame=(56, 10, 17))]
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
   the row groups below lift as it passes them.
   RESTORED at its authored coordinates. I first "corrected" these 8u upward
   on the theory that the field had moved when the plate grew 556 -> 576; it
   had not — the rails were always 288 + r*28, and the circuit deliberately
   rides 8u BELOW each rail, in the clear band. Shifting it put the nib
   straight through the digit rows, which gate.mjs reported as eight collisions
   against the miss marks. The measurement is the field, not the plate. */
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
    # Order matters here, and it did not until round 22. The evidence line
    # belongs to the DOT ratio and sits under the dot caption; the axpy loss
    # goes last, as the kicker. Drawn the other way round, nearest-caption
    # pairing attaches "three committed runs, spread under two percent" to the
    # axpy number — for which it is flatly false: the reference machine has
    # exactly one committed axpy run, and the cross-machine spread on that
    # kernel is 69%. That would have misread the one number on this plate that
    # exists to argue against its own author.
    s.append(f'<text x="330" y="120" class="fine" style="fill:{INK3}">three committed runs, spread under two percent</text>')
    # Led with the case name, like the benchDot caption two lines up, because
    # this line has a hard length budget and that phrasing is the short one.
    # "10.7×" is one glyph wider than the "6.9×" it replaced, which spent the
    # 6u of design margin gate.mjs check 5 reserves, and the check caught it at
    # all 40 timesteps of both themes.
    #
    # The .fine column is MONOSPACE, which is the whole lesson: the first fix
    # attempted here swapped the em dash for a middot on the theory that a
    # narrower separator would buy the space back. It bought nothing — every
    # glyph in this face has the same advance — and gate.mjs returned a
    # byte-identical 244->683 to prove it. Only the character COUNT moves this
    # measurement. The budget is 51: the benchDot caption at y100 sits exactly
    # there and passes. This line is 50.
    s.append(f'<text x="330" y="140" class="fine" style="fill:{INK3}">benchAxpy/128 · 10.7× SLOWER, threads have a floor</text>')

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
    s.append(f'<text x="150" y="556" class="fine" style="fill:{INK3}">source: benchmarks/ — pinned runs and the misclassification CSV</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── PLATE IV
def plate_automl() -> str:
    """The tool manifest. Room: a stores ledger — what may be drawn, by whom.

    REDRAWN from scratch in round 24. The phase dial was chartjunk by the
    house's own test: seven near-equal sectors encoding neither magnitude
    nor membership, while a centre text box did all the work. The section's
    claim is SET MEMBERSHIP UNDER LEAST PRIVILEGE, so the plate now draws
    the sets themselves: the 44-tool registry as 44 marks, the 15-tool base
    set bracketed and filled, the other 29 hollow — a drawn set difference.

    What it deliberately does NOT draw: per-phase mark counts. The source
    audit put numbers on some of them (training 12, onboarding 4) but no
    claims row exists for those and this page does not draw unregistered
    numbers, so per-phase membership is stated in words: no phase gets all
    15, five declared sets are imported by the phases that name them, two —
    preprocessing and feature engineering — are exported and imported by
    NOTHING, printed and struck through, the estate's absence-as-evidence
    device (the strikes are static hairlines; the moving-hairline check
    does not apply). The one claim that survived the audit gets the verdict
    row: TRAINING, a route, and a pine stop before PREPROCESSING.

    Round 25 corrected the reason on that row. It read "at any layer",
    which repeated the section's own error: the stage allow-list, the
    request builder and the provider call pass one array between them, so
    that is a single mechanism counted three times. The call actually dies
    in the executor, which resolves a tool name against training's handler
    set and then the MCP registry — neither of which holds a preprocessing
    name. Same verdict, real mechanism, one layer.

    The sandbox vessel is retired with the dial: the containment facts are
    two lines of type, "no route out BY DEFAULT" kept on its face. No
    motion at all — round 24's budget allows a plate to hold still, and a
    stores ledger should.
    """
    H, a = 578, CLAY_G
    s = [head(H, "Agentic AutoML — one phase, one tool set",
              "Agentic AutoML takes a dataset and a sentence and returns a trained model, "
              "one MCP server over a LangGraph state machine. Its registry holds 44 tool "
              "definitions, drawn here as 44 marks with the 15-tool base set bracketed — "
              "and no phase gets all 15: every request is narrowed again per stage. Of the "
              "seven declared per-phase sets, two — preprocessing and feature "
              "engineering — are exported and imported by nothing, drawn struck through; "
              "the rest are imported by the phases that name them. What survives is "
              "that a training-phase model cannot reach a preprocessing tool: the executor "
              "resolves tool names against training's own handler set and then the MCP "
              "registry, and no preprocessing name is in either. The Python it writes runs in a container "
              "on an internal Docker network with no route out by default, a read-only "
              "root filesystem, a non-root user, the dataset mounted read-only and 5 tmpfs "
              "mounts as the only writable surface. Behind it, a 29-table Postgres schema "
              "with pgvector. Public, GPL-3.0, written with Shree Chaturvedi.",
              key="plate-6b-automl.svg", frame=(28, 62, 17))]
    # The carrier: a dim point walking the 44-mark shelf, one traverse per
    # loop. The dial this plate replaced carried a needle; a set diagram has
    # no needle, so the carrier is drawn from the diagram's own material —
    # the registry being read. One @keyframes with 44 staggered negative
    # delays, not 44 rules. It is deliberately INERT: it lights no particular
    # mark and encodes no count, so it cannot become a number nothing derives.
    s.append(f""".mk{{stroke-dasharray:3 3;animation:mk 2.6s linear infinite}}
@keyframes mk{{from{{stroke-dashoffset:0}}to{{stroke-dashoffset:-6}}}}
</style>{ground(H)}""")

    s.append(f'<text x="{L}" y="{TOP - 16}" class="kick">IV · AGENTIC AUTOML</text>')
    s.append(f'<text x="{R}" y="{TOP - 16}" text-anchor="end" class="kick">ONE MCP SERVER · LANGGRAPH</text>')
    s.append(f'<text x="{L}" y="74" class="say" style="fill:{INK}">ONE PHASE, ONE TOOL SET</text>')

    # ── the claim triplet: the fraction at claim size, and the narrowing
    # lines beside it — no phase gets even the base set whole
    s.append(f'<text x="{L}" y="152" class="hero">15<tspan class="unit">/44</tspan></text>')
    s.append(f'<text x="{L}" y="180" class="lbl">IN THE BASE SET</text>')
    for i, ln in enumerate(["no phase gets all 15 —", "every request narrows per stage,",
                            "a training-phase model cannot", "reach a preprocessing tool"]):
        s.append(f'<text x="330" y="{126 + i*18}" class="fine">{ln}</text>')

    # ── the registry, drawn as itself: 44 marks on one shelf. The base 15
    # filled (they travel furthest), the other 29 hollow (they arrive only
    # with a phase). The bracket is the set boundary made visible.
    for i in range(44):
        x = L + i * 13
        if i < 15:
            # the base set is HELD: it is the part that is always there
            s.append(f'<rect x="{x}" y="210" width="7" height="7" fill="{a}"/>')
        else:
            # the other 29 arrive only with a phase, so their outlines run —
            # drawn pending rather than absent. This is the plate's carrier,
            # and it is inert: it lights no particular mark and encodes no
            # count, so it can never become a number nothing derives.
            s.append(f'<rect class="mk" x="{x}" y="210" width="7" height="7" fill="none" '
                     f'stroke="{WIRE}" stroke-width="1.2"/>')
    # the bracket stays SOLID and still: it delimits the base set, which is the
    # part that is never pending. Only the 29 run.
    s.append(f'<path d="M{L} 226v4M{L} 230H{L + 14*13 + 7}M{L + 14*13 + 7} 230v-4" '
             f'fill="none" stroke="{WIRE}" stroke-width="1.2"/>')
    s.append(f'<text x="{L}" y="248" class="lbl">THE BASE SET — 15</text>')
    s.append(f'<text x="{L + 43*13 + 7}" y="248" text-anchor="end" class="lbl">THE OTHER 29 — PHASE TOOLS</text>')

    # ── the seven declared sets, and the two nobody imports. The dead pair
    # is printed AND struck — absence presented as evidence, not omitted.
    s.append(f'<text x="{L}" y="288" class="kick">SEVEN DECLARED PER-PHASE SETS</text>')
    # "five are imported…" drew a number whose MEANING no row carries. It passed
    # only because automl.sandbox_tmpfs licenses a 5 on this plate for the tmpfs
    # mounts — a different noun entirely. The count-noun trap, arriving through
    # the gate's permissive direction rather than its strict one. The positive
    # count is arithmetic a reader can do from "seven declared" and the two
    # named below, so it does not need drawing. 45 chars.
    s.append(f'<text x="{L}" y="312" class="fine">each imported by the phase that names it — except</text>')
    s.append(f'<text x="{L}" y="334" class="fine" style="fill:{INK3}">preprocessing · feature-engineering — exported, imported by nothing</text>')
    # the strikes, measured on the mono grid: 13 chars, then a 3-char gap,
    # then 19 — static hairlines, drawn through dead names on purpose
    x1 = L + 13 * CELL_13
    x2 = L + 16 * CELL_13
    x3 = x2 + 19 * CELL_13
    s.append(f'<path d="M{L - 2} 330H{x1 + 2:.1f}M{x2 - 2:.1f} 330H{x3 + 2:.1f}" '
             f'stroke="{INK3}" stroke-width="1.2"/>')

    # ── the verdict row: the one route the audit proved cannot exist
    s.append(f'<text x="{L}" y="370" class="key">TRAINING</text>')
    s.append(f'<path d="M240 365H340" stroke="{WIRE}" stroke-width="1.2"/>')
    s.append(f'<rect x="344" y="355" width="4" height="20" fill="{PINE}"/>')
    s.append(f'<text x="360" y="370" class="key" style="fill:{INK3}">PREPROCESSING</text>')
    s.append(f'<text x="{L}" y="392" class="fine">no preprocessing name resolves on this path</text>')

    # ── where the generated Python runs — the containment, stated plainly
    s.append(f'<text x="{L}" y="430" class="kick">WHERE GENERATED PYTHON RUNS — CONTAINED BY DEFAULT</text>')
    s.append(f'<text x="{L}" y="452" class="fine" style="fill:{INK}">--internal network — no route out by default · non-root user</text>')
    s.append(f'<text x="{L}" y="472" class="fine" style="fill:{INK}">read-only root · /datasets:ro · 5 tmpfs — the only writable surface</text>')

    # ── the stores behind it, and the imprint
    s.append(f'<text x="{L}" y="514" class="sub">29</text>')
    s.append(f'<text x="206" y="514" class="lbl">TABLES · POSTGRES + PGVECTOR</text>')
    s.append(f'<text x="206" y="534" class="fine">public · GPL-3.0 · written with Shree Chaturvedi</text>')
    s.append(f'<text x="{L}" y="558" class="fine" style="fill:{INK3}">source: backend/src/services/llm/tools/index.ts</text>')
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
    one value off the returned rows. So the rest state STATES the claim:
    tenant A's rows are redaction — black ink in light, a void held by a
    wire edge in dark — while tenant B's rows carry visible record-lines.

    ROUND 24 CUT THIS PLATE TO ONE MOVING IDEA. The auditor's scan is
    deleted: gate.mjs's moving-hairline check proved it crossed every
    service name and both printed confessions somewhere in its loop, and a
    camo-served <img> lands a reader on an arbitrary frame — an instrument
    that can strike out "tags**" is asserting a deletion the audit never
    made. The emerald stream inside B's rows is stilled too (the drawn
    record-lines carry "returned" without moving). What remains is the one
    motion that re-derives meaning: the redactions are RE-STRUCK once per
    loop — each bar lifts faded, leaves its row blank for half a second
    (the void the database returned), then wipes back left-to-right in a
    tight cascade down the column: the door slamming, and staying shut.
    """
    # PINE, not an arbitrary hue: this whole plate is the database refusing,
    # and the refusal is a CHECK. The accent says so.
    H, LOOP, a = 762, 9.7, PINE
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
              frame=(44, 64, 23))]
    # the re-strike: 0% is the finished frame (redacted), held for 84% of the
    # loop; the bar lifts FADED (no visible retraction — the row is simply
    # blank, which is what the database sent), then wipes back left-to-right.
    # Round 21's bars returned to full width from a visible retraction, so
    # the resting figure showed A and B identical — the opposite of the claim.
    s.append(f""".vast{{font-size:89px;letter-spacing:-2px;fill:{INK};font-weight:600;font-family:'S',Georgia,serif}}
/* the tenant-B rows stream their record-lines: the plate's CARRIER, restored.
   Only .bfl comes back — .scan does NOT. That one swept a rule down the table
   and across every service name and both printed confessions, drawing true
   claims struck out; gate.mjs check 3 now fails on exactly that, deliberately,
   so restoring it would correctly turn the build red. The carrier stays, the
   strikethrough does not. */
.bfl{{animation:bfl 1.7s linear infinite}}
@keyframes bfl{{from{{stroke-dashoffset:0}}to{{stroke-dashoffset:-8}}}}
.red{{transform-box:fill-box;transform-origin:left center;animation:red {LOOP}s {EASE} infinite}}
@keyframes red{{0%,84%{{opacity:1;transform:scaleX(1)}}85.5%{{opacity:0;transform:scaleX(1)}}
  86.5%{{opacity:0;transform:scaleX(.02)}}90.5%{{opacity:1;transform:scaleX(.02)}}
  95%,100%{{opacity:1;transform:scaleX(1)}}}}
</style>{ground(H)}""")

    s.append(f'<text x="{L}" y="{TOP}" class="kick">V · CADENCE — THE ISOLATION AUDIT</text>')
    s.append(f'<text x="{L}" y="88" class="say" style="fill:{INK}">SIX SERVICES, SELF-AUDITED</text>')
    s.append(f'<text x="{L}" y="116" class="kick">ANY USER COULD READ OR DELETE ANOTHER’S ROWS BY ID</text>')
    s.append(f'<text x="{L}" y="136" class="kick">THE MARKS SHOW WHERE EACH GUARD NOW SITS</text>')

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
    s.append(f'<text x="{L}" y="640" class="vast">B only</text>')
    s.append(f'<text x="520" y="640" class="lbl">ROW-LEVEL SECURITY</text>')
    s.append(f'<text x="{L}" y="684" class="say">The app didn’t remember to filter.</text>')
    s.append(f'<text x="{L}" y="712" class="say">The database refused.</text>')
    # the source footer every plate closes with: the isolation suite is the
    # artifact that makes the sentence above checkable
    s.append(f'<text x="{L}" y="736" class="fine" style="fill:{INK3}">source: rls.postgres.test.ts — the isolation suite</text>')
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
    cheapest first — labelled outside on level leaders. Decided mail leaves
    by the chutes to CLASSIFIED (drawn as static guides). The one message
    no layer is sure of lands on the 0.85 gate — a solid member across the
    foot, the one edge nothing passes — pauses, and is walked sideways to a
    human, where it rests. Below the gate, nothing is guessed.

    Round 24: the four ambient stream messages are deleted and the channel
    is compressed 72u — the taper below the SetFit screen was the empty
    fifth of the plate. The one motion kept is the one that IS the section's
    claim: the refused message replaying its journey — inlet, three screens,
    the pause at the gate, the handover — with the human's small rise to
    receive it. Authored at rest beside the human (data-rest), so the still
    frame any camo-served reader lands on shows the handover already made.
    """
    H, a = 652, CLAY_G
    T1, T2, T3 = 8.6, 12.9, 15.5   # route periods — near-coprime, unfindable
    s = [head(H, "Applied — a classifier allowed to say it doesn't know",
              "Applied: a three-layer email classifier — 201 regex rules, then e5 embeddings, "
              "then a fine-tuned SetFit head, cheapest first — drawn as a tapered sifting "
              "channel. The one message no layer is sure of stops at the 0.85 confidence "
              "gate across the channel's foot and is walked to a human instead of guessed "
              "at. It scores 0.979 macro-F1 — 2 mistakes on a 96-message evaluation set — "
              "measured with the rules layer alone, which is also all the hosted app runs; "
              "CI fails the build below 0.95. On the Hugging Face Space the fine-tuned head "
              "runs inside your own browser tab: the int8 ONNX build is 22.8 megabytes, "
              "down from 90.4.",
              key="plate-4-applied.svg", col=(110, 776), frame=(42, 25.4, 23))]

    # ── the chutes: static guides now — where decided mail leaves. Authored
    # here beside the walls so drawing and geometry cannot disagree.
    # The routes enter at 109, not 88. 88 was authored against the taller
    # pre-compression channel; after the 72u trim it put an 18u token's box
    # straight over the headline at y=84 — gate.mjs check 3 caught it the
    # moment the ambient stream came back. 109 is the same inlet the refused
    # message uses (its rest box is y 100-118), so both routes now enter at
    # the channel mouth rather than through the type above it.
    P1 = "M440 109 C440 130 438 143 436 156 C434 176 420 190 342 198 C300 203 246 214 218 224"
    P2 = ("M440 109 C440 130 438 143 436 156 C434 184 436 214 438 240 "
          "C436 262 420 276 360 284 C316 290 250 302 222 312")
    # the walk to the human happens in translate keyframes (dv below), so the
    # refused message can be AUTHORED at its rest beside the human — with
    # motion off, the still frame shows the handover already made.
    #
    # The inlet is -315px, not -329: the 72u channel compression carried the
    # old inlet offset up with it and at 35% of the loop the token surfaced
    # ON the section headline (gate check 3, t=5.42s). -315 puts it at
    # y=100-118 — ten units clear of the headline's descenders, still above
    # the channel mouth at 104, so it reads as mail entering the channel.
    # RESTORED — the stream is this plate's carrier, and the argument that
    # deleted it ("ambient travel means nothing on an arbitrary camo frame")
    # is an argument about a GESTURE. Four messages perpetually on the two
    # routes are semantically identical in every frame: no frame lies, and
    # the plate is alive whichever instant a reader is handed. The refused
    # message's journey is the gesture and stays exactly as re-choreographed.
    # The paths are the CURRENT P1/P2, so the stream follows the compressed
    # channel rather than the pre-compression one.
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
.dv{{animation:dv {T3}s {EASE} infinite}}
@keyframes dv{{0%,30%{{opacity:1;transform:translate(0,0)}}
  32%{{opacity:0;transform:translate(0,0)}}
  33%{{opacity:0;transform:translate(-208px,-315px)}}
  35%{{opacity:1;transform:translate(-208px,-315px)}}
  40%,43%{{transform:translate(-208px,-261px)}}
  47%,50%{{transform:translate(-208px,-185px)}}
  54%,57%{{transform:translate(-208px,-109px)}}
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
    wx = lambda y: 320 + 70 * (y - 104) / 292
    ch.append(f'<path d="M320 104L{wx(198):.1f} 198M{wx(220):.1f} 220L{wx(274):.1f} 274'
              f'M{wx(296):.1f} 296L390 396" stroke="{WIRE}" stroke-width="3"/>')
    ch.append(f'<path d="M560 104L{560 - 70 * 274 / 292:.1f} 378" stroke="{WIRE}" stroke-width="3"/>')
    # screens: wall-to-wall at their depth, perforated
    for sy in (168, 244, 320):
        wl = 320 + 70 * (sy - 104) / 292
        wr = 560 - 70 * (sy - 104) / 292
        # RULE, a step below the walls' WIRE: a wall is what the stream cannot
        # pass and a screen is what it passes THROUGH, and the drawing now says
        # which is which by weight AND tone rather than weight alone. 3.40 night
        # / 3.19 day at 2u — legal for a mark, and a full unit heavier than the
        # RULE guides below, so the three-tier hierarchy reads.
        ch.append(f'<path d="M{wl:.0f} {sy}H{wr:.0f}" stroke="{RULE}" stroke-width="2" stroke-dasharray="7 5"/>')
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
    ch.append(f'<path d="M212 212V236M216 300V324" stroke="{WIRE}" stroke-width="2"/>')
    # the gate: a solid member across the foot — the one edge nothing passes.
    # PINE, because the gate is the check, and its two labels ("0.85 GATE",
    # "RULES LAYER ONLY") already are. Drawn in the accent it was the only
    # pine claim on the plate whose subject was painted in my own colour.
    ch.append(f'<rect x="390" y="396" width="100" height="4" fill="{PINE}"/>')
    ch.append(f'<path d="M490 398H586" stroke="{WIRE}" stroke-width="1"/>')
    # the walk to the human, drawn as the same faint guide
    ch.append(f'<path d="M446 386C500 390 560 404 620 422" fill="none" stroke="{RULE}" stroke-width="1" stroke-dasharray="2 6"/>')
    # the human: head and shoulders, on the plate, at the end of the walk —
    # and it REACTS (the .hum rise) when the refused message reaches it
    # INK, a step above the refused message that arrives beside them. At INK2
    # the person and the packet were the same tone, so the end of the walk read
    # as two objects rather than a subject receiving one.
    ch.append(f'<g class="hum"><g id="the-human"><circle cx="660" cy="425" r="8" fill="none" stroke="{INK}" stroke-width="1.6"/>'
              f'<path d="M644 454C644 440 676 440 676 454" fill="none" stroke="{INK}" stroke-width="1.6"/></g></g>')
    # the stream: four messages on the two decided routes, at 18u — round 21
    # measured the 14u tokens as too small to track on the dark slab
    for cls in ("pa0", "pa1", "pb0", "pb1"):
        ch.append(f'<rect class="msg {cls}" x="-9" y="-9" width="18" height="18" rx="3.5" '
                  f'style="fill:{a};fill-opacity:{op(0.55)};stroke:{a};stroke-width:1.6"/>')
    # ...and the refused message, authored at rest beside the human
    ch.append(f'<rect class="dv" data-rest="the-human" data-rest-within="12" x="630" y="415" '
              f'width="18" height="18" rx="3.5" '
              f'style="fill:{INK2};fill-opacity:{op(0.7)};stroke:{INK2};stroke-width:1.6"/>')
    s.append('<g>' + "".join(ch) + '</g>')

    # the screen labels, on their level leaders
    s.append(f'<text x="594" y="173" class="key">201 REGEX RULES</text>')
    s.append(f'<text x="594" y="249" class="key">e5 EMBEDDINGS</text>')
    s.append(f'<text x="594" y="325" class="key">SETFIT HEAD</text>')
    s.append(f'<text x="594" y="195" class="fine">cheapest first —</text>')
    s.append(f'<text x="594" y="213" class="fine">most mail stops</text>')
    s.append(f'<text x="594" y="403" class="key" style="fill:{PINE}">0.85 GATE</text>')

    # what leaves the channel decided — a rotated tab at the left edge,
    # the one strip the stream can never enter
    s.append(f'<text transform="rotate(-90 128 250)" x="128" y="250" text-anchor="middle" class="kick">CLASSIFIED — DECIDED AT A SCREEN</text>')

    # the human's name, under the figure
    s.append(f'<text x="660" y="484" text-anchor="middle" class="lbl">A HUMAN</text>')
    s.append(f'<text x="400" y="438" text-anchor="middle" class="fine" style="fill:{INK3}">below the gate, nothing is guessed</text>')

    # ── the verdict. 0.979 is the number with an artifact behind it,
    # labelled for what it measures; the cascade's 0.9583 has none.
    s.append(f'<path d="M{L} 508H{R}" stroke="{RULE}"/>')
    s.append(f'<text x="{L}" y="556" class="hero">0.979</text>')
    s.append(f'<text x="330" y="534" class="lbl">MACRO-F1 · 96-MSG EVAL SET · 2 MISTAKES</text>')
    s.append(f'<text x="330" y="556" class="key" style="fill:{PINE}">RULES LAYER ONLY</text>')
    s.append(f'<text x="330" y="578" class="fine">SetFit off, embeddings emptied · CI fails below 0.95</text>')
    s.append(f'<text x="{L}" y="602" class="lbl">YOUR BROWSER</text>')
    s.append(arrowed(300, 602, "fine", "int8 ONNX · 90.4 MB", "22.8 MB"))
    s.append(f'<text x="{R}" y="602" text-anchor="end" class="fine" style="fill:{INK3}">never leaves your tab</text>')
    s.append(f'<text x="{L}" y="626" class="fine" style="fill:{INK3}">source: backend/jobtracker/classifier/hybrid.py</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── PLATE VII
def plate_visualassist() -> str:
    """The alert policy. Room: an instrument's field of view, and its
    calibration card.

    REBUILT in round 23. The round-22 plate drew a generic cone, six
    scattered dots and two unlabelled arcs — an instrument with no reading —
    while the section it illustrates had just been rewritten around the one
    piece of engineering worth a drawing: THREE DISTANCE BANDS and what each
    one emits. The only numbers the old plate carried were inventory (lines,
    files, workflows) — counts of typing, not decisions. The section's real
    numbers are 0.5 / 1.0 / 2.0 metres: they measure what the app does to a
    person walking. So the plate now draws the policy itself, twice over:

    * THE SCENE — the phone's field of view with the three thresholds as
      arcs at TRUE PROPORTION (100/200/400u on one scale), ticked and
      dimensioned on the beam axis like a drafting section. The two arcs
      where the app interrupts are CLAY (my act, my chosen thresholds); the
      2.0 m arc is PINE, because the deliberate silence inside it is the
      check working — an aid that narrates every wall is an aid you switch
      off, and the estate draws "the system working" in pine everywhere else.
    * THE TABLE — a ruled calibration card, one row per band: the distance
      at claim size, what fires, and the haptic signature drawn as a
      waveform on a hairline track. One continuous bar for the 0.5 m buzz,
      three transient ticks for the 1.0 m pulse, and for 2.0 m the track is
      a FLATLINE: the absence is drawn, not left blank, so the row states
      "no alert fires" as evidence rather than as missing content. The
      source path (LiDARService.swift — no line numbers, which would be
      unregistered digits) and the finding that the Settings sliders cannot
      reach these constants close the card.

    The plate's one moving device (round 24's budget): the approach. One
    obstacle walks in from beyond the field at constant speed (the honest
    physical statement; its crossing times are LINEAR in distance, so no
    bezier inversion — round 21's sweep bug category is structurally gone)
    and trips each band in turn: crossing 2.0 m lights that row's numeral
    pine and nothing else — silence, performed; crossing 1.0 m fires three
    staggered vibration ticks at the phone and one brief speech flash;
    crossing 0.5 m holds the vibration marks and speech arcs lit while the
    walker is inside — the continuous full-strength buzz — and then the
    walker stops and fades: the interrupt worked. Every output mark sits at
    the phone under a plain label, because round 22's unlabelled speaker
    arc read as a rendering artifact.

    The inventory line survives, demoted to the repo corner where it
    belongs: it identifies the artifact, it is not the argument.
    """
    H, a = 748, CLAY_G
    T = 13.7                        # the approach's clock
    EX, EY = 238, 272               # the emitter — the phone's sensor
    SC = 200                        # u per metre — one scale, stated by ticks
    R05, R10, R20 = SC * 0.5, SC * 1.0, SC * 2.0
    SPAN = 15                       # field half-angle, degrees
    sin_, cos_ = math.sin(math.radians(SPAN)), math.cos(math.radians(SPAN))
    X0, X1 = 676.0, 290.0           # the walk: start and stop (inside 0.5 m)
    TRAVEL = X0 - X1
    ARRIVE = 80.0                   # % of loop when the walker reaches X1
    # crossing times are linear in distance — constant walking speed
    c20, c10, c05 = (round(ARRIVE * (X0 - (EX + r)) / TRAVEL, 1)
                     for r in (R20, R10, R05))
    s = [head(H, "VisualAssist — three distance bands: stop, caution, silence",
              "VisualAssist: an iPhone app for low-vision users, written in Swift — ARKit "
              "LiDAR depth becomes speech and haptics, and the plate draws its alert "
              "policy as three distance bands in front of the phone, to scale. Inside "
              "0.5 metres: a continuous haptic at full strength, and speech. Inside "
              "1.0 metres: a triple pulse, softer, and a shorter phrase. Both spoken "
              "alerts name a direction as well as a distance. Inside 2.0 metres nothing "
              "fires at all — the zone turns yellow on screen and the distance is read "
              "only if you press for it, because an aid that narrates every wall is an "
              "aid you switch off. An obstacle drawn approaching the phone trips each band in turn. "
              "7,177 lines across 38 Swift files, 5 CI workflows. It is the one system "
              "on this page you cannot click into, because it needs an iPhone with a "
              "lidar sensor.",
              key="plate-8-visualassist.svg", col=(118, 762), frame=(44, 60, 25))]
    # ── the walk, and everything it triggers. The obstacle is authored at
    # its start (beyond the outer band), travels linearly, rests briefly
    # inside the stop band — the interrupt WORKED — and fades before the
    # reset, so nothing teleports while visible and t=0 is a full-opacity
    # authored frame.
    # the beam holds still (round 24: one moving device per plate, and this
    # plate's is the approach); its dashes read as a drawn datum line
    css = [f""".dtm{{animation:dtm 2.4s linear infinite}}
@keyframes dtm{{from{{stroke-dashoffset:0}}to{{stroke-dashoffset:-8}}}}
.obs{{animation:obs {T}s linear infinite}}
@keyframes obs{{0%{{opacity:1;transform:translateX(0)}}
  {ARRIVE:g}%,87%{{opacity:1;transform:translateX({-TRAVEL:g}px)}}
  89%{{opacity:0;transform:translateX({-TRAVEL:g}px)}}
  89.5%,93%{{opacity:0;transform:translateX(0)}}
  95.5%,100%{{opacity:1;transform:translateX(0)}}}}"""]
    # each band's row numeral lights while the walker is inside that band —
    # the read-chase idiom, driven by the scene. The silent band lights PINE
    # (the check), the interrupting bands CLAY (the act). Fill animations on
    # tspans that own nothing, exactly as the index rows learned in 6aec558.
    for cls, on, off, col in (("rn2", c20, c10, PINE),
                              ("rn1", c10, c05, CLAY),
                              ("rn0", c05, 86.0, CLAY)):
        css.append(f".{cls}{{animation:{cls} {T}s linear infinite}}"
                   f"@keyframes {cls}{{0%,{on-0.7:g}%{{fill:{INK}}}{on+0.7:g}%,{off-0.7:g}%{{fill:{col}}}"
                   f"{off+0.7:g}%,100%{{fill:{INK}}}}}")
    # the outputs, at the phone: speech arcs flash once per utterance — a
    # brief word at 1.0 m, a held phrase at 0.5 m — and the vibration marks
    # fire three STAGGERED transients at 1.0 m (the triple pulse, performed
    # in sequence) then hold through the stop band (the continuous buzz).
    css.append(f".spk{{animation:spk {T}s linear infinite}}"
               f"@keyframes spk{{0%,{c10-0.7:g}%{{stroke:{WIRE}}}{c10+0.7:g}%,{c10+4.3:g}%{{stroke:{a}}}"
               f"{c10+5.7:g}%,{c05-0.7:g}%{{stroke:{WIRE}}}{c05+0.7:g}%,{c05+10:g}%{{stroke:{a}}}"
               f"{c05+11.4:g}%,100%{{stroke:{WIRE}}}}}")
    for k in range(3):
        p0 = c10 + k * 1.6
        css.append(f".vb{k}{{animation:vb{k} {T}s linear infinite}}"
                   f"@keyframes vb{k}{{0%,{p0-0.6:g}%{{stroke:{WIRE}}}{p0:g}%,{p0+1.1:g}%{{stroke:{a}}}"
                   f"{p0+1.7:g}%,{c05-0.6:g}%{{stroke:{WIRE}}}{c05:g}%,86%{{stroke:{a}}}"
                   f"87%,100%{{stroke:{WIRE}}}}}")
    s.append("\n".join(css) + f"</style>{ground(H)}")

    s.append(f'<text x="{L}" y="{TOP}" class="kick">VII · VISUALASSIST</text>')
    s.append(f'<text x="{R}" y="{TOP}" text-anchor="end" class="key">SWIFT · ARKIT · LIDAR</text>')
    # the inventory, demoted to the repo corner: it identifies the artifact
    s.append(f'<text x="{R}" y="76" text-anchor="end" class="kick">7,177 LINES · 38 SWIFT FILES · 5 CI WORKFLOWS</text>')
    s.append(f'<text x="{L}" y="100" class="say" style="fill:{INK}">CAN A PHONE TELL YOU WHAT IS IN FRONT OF YOU?</text>')

    # ── the scene: one composed instrument, so the walker may legitimately
    # cross the ticks, the arcs and the beam (the applied channel's ruling).
    sc = []
    # the phone is an object in the world — INK; only the sensor is the act
    sc.append(f'<rect x="176" y="213" width="58" height="118" rx="9" fill="none" stroke="{INK}" stroke-width="2"/>')
    sc.append(f'<path d="M196 223H214" stroke="{INK}" stroke-width="1.5" stroke-linecap="round"/>')
    sc.append(f'<circle cx="{EX}" cy="{EY}" r="3.5" fill="{a}"/>')
    # the field's edges — structure, WIRE, clear of the sensor dot
    for sgn in (-1, 1):
        sc.append(f'<path d="M{EX + 26*cos_:.1f} {EY + sgn*26*sin_:.1f}'
                  f'L{EX + R20*cos_:.1f} {EY + sgn*R20*sin_:.1f}" '
                  f'stroke="{WIRE}" stroke-width="1.2"/>')
    # the three thresholds, at true proportion. Weight ranks the policy —
    # the hard interrupt heaviest — and colour states whose act each one is:
    # the two interrupting bands CLAY, the silent band PINE, the check.
    for r, col, w in ((R05, a, 2.4), (R10, a, 1.8), (R20, PINE, 1.6)):
        x, dy = EX + r * cos_, r * sin_
        sc.append(f'<path d="M{x:.1f} {EY-dy:.1f}A{r:g} {r:g} 0 0 1 {x:.1f} {EY+dy:.1f}" '
                  f'fill="none" stroke="{col}" stroke-width="{w}"/>')
    # the beam: the datum, drifting inward at a constant rate — the sensor
    # sampling, and this plate's CARRIER. The walker is the gesture and keeps
    # its semantic pause at the stop band (it arrives, the interrupt fires, it
    # halts); that pause left the plate frozen for 13% of the loop. A carrier
    # is the right instrument for the gap because it is phase-invariant: 8u is
    # one dash period, so the wrap is invisible and every frame reads alike.
    sc.append(f'<path class="dtm" d="M246 {EY}H690" fill="none" stroke="{a}" '
              f'stroke-width="1.3" stroke-dasharray="2 6"/>')
    # dimension ticks where each threshold crosses the axis
    for r in (R05, R10, R20):
        sc.append(f'<rect x="{EX + r - 1.25:g}" y="{EY-7}" width="2.5" height="14" fill="{WIRE}"/>')
    # the walker: the world approaching — INK, authored at the start
    sc.append(f'<circle class="obs" cx="{X0:g}" cy="{EY}" r="5.5" fill="{INK}"/>')
    # the outputs, AT the phone and labelled below it — round 22's speaker
    # arc was unlabelled and near-invisible, and read as an artifact
    sc.append(f'<path class="spk" d="M166 231A10 10 0 0 0 166 251" fill="none" '
              f'style="stroke:{WIRE}" stroke-width="2" stroke-linecap="round"/>')
    sc.append(f'<path class="spk" d="M159 222A19 19 0 0 0 159 260" fill="none" '
              f'style="stroke:{WIRE}" stroke-width="2" stroke-linecap="round"/>')
    for k, d in enumerate(("M168 289L156 295", "M170 301L157 307", "M168 313L156 319")):
        sc.append(f'<path class="vb{k}" d="{d}" fill="none" style="stroke:{WIRE}" '
                  f'stroke-width="2" stroke-linecap="round"/>')
    s.append('<g>' + "".join(sc) + '</g>')
    # the dimensions, read off the axis — the numbers ARE the policy
    for r, t in ((R05, "0.5 m"), (R10, "1.0 m"), (R20, "2.0 m")):
        s.append(f'<text x="{EX + r + 8:g}" y="294" class="key">{t}</text>')
    s.append(f'<text x="205" y="356" text-anchor="middle" class="kick">SPEECH + HAPTICS</text>')

    # ── the calibration card: one row per band, ruled, no box. The header
    # carries the ruling that makes these three numbers a design decision
    s.append(f'<path d="M{L} 396H{R}" stroke="{RULE}"/>')
    s.append(f'<text x="{L}" y="422" class="kick">THE ALERT POLICY — THE SLIDER CHANGES NOTHING</text>')
    ROWS = [
        ("0.5", "rn0", "STOP — CONTINUOUS HAPTIC, FULL STRENGTH", INK,
         # Reported, not quoted. Neither utterance is a fixed string: the app
         # interpolates "Stop! Obstacle \(nearestDirection) at \(distanceStr)"
         # and "Caution, \(distanceStr) \(nearestDirection)". MONO_CHARS
         # carries no "!", so a colon-quote here would render a paraphrase in
         # quotation form — the plate asserting an exact string it cannot set.
         # These lines name the PARTS each utterance contains, in order.
         # Round 25 fixed a real error here: this row said "one spoken word:
         # Caution", which the source contradicts twice over — it is three
         # parts, and it names a direction. README quotes the format strings.
         # 33 chars fits; the row's right edge is the haptic-signature track
         # at x=628, not the type column, and a 45-char attempt sat on the bar.
         ["speaks Stop, direction, distance"]),
        ("1.0", "rn1", "CAUTION — A TRIPLE PULSE, SOFTER", INK,
         ["speaks Caution, distance, direction"]),
        ("2.0", "rn2", "SILENT — NO ALERT FIRES", PINE,
         ["the zone turns yellow on screen —",
          "the distance is yours if you press for it"]),
    ]
    for i, (num, cls, key, kcol, fines) in enumerate(ROWS):
        y = 462 + i * 62
        s.append(f'<text x="{L}" y="{y}" class="sub {cls}">{num}<tspan class="unit"> m</tspan></text>')
        s.append(f'<text x="300" y="{y}" class="key" style="fill:{kcol}">{key}</text>')
        for j, fn in enumerate(fines):
            s.append(f'<text x="300" y="{y + 20 + j*20}" class="fine">{fn}</text>')
        # the haptic signature, on a hairline track: one continuous bar, three
        # transients, and — for the silent band — a pine FLATLINE: the absence
        # drawn as evidence, in the check's colour
        ty = y + 11
        if i == 0:
            s.append(f'<path d="M620 {ty}H716" stroke="{RULE}" stroke-width="1"/>')
            s.append(f'<rect x="628" y="{ty-4.5}" width="80" height="9" rx="2" fill="{a}"/>')
        elif i == 1:
            s.append(f'<path d="M620 {ty}H716" stroke="{RULE}" stroke-width="1"/>')
            for k in range(3):
                s.append(f'<rect x="{628 + k*30}" y="{ty-4.5}" width="18" height="9" rx="2" fill="{a}"/>')
        else:
            s.append(f'<path d="M620 {ty}H716" stroke="{PINE}" stroke-width="1.4"/>')
        if i < 2:
            s.append(f'<path d="M{L} {y+34}H{R}" stroke="{RULE}"/>')
    s.append(f'<path d="M{L} 642H{R}" stroke="{RULE}"/>')
    # the source footer, path only — line numbers are digits no claims row
    # carries, so the file is named and the range is not
    s.append(f'<text x="{L}" y="664" class="fine" style="fill:{INK3}">source: VisualAssist/Services/LiDARService.swift · let constants</text>')

    # the honest close: the only system here without a link, and why
    s.append(f'<text x="{L}" y="696" class="say" style="fill:{INK}">THE ONE SYSTEM HERE YOU CANNOT CLICK INTO</text>')
    s.append(f'<text x="{L}" y="720" class="fine" style="fill:{INK3}">no live link — it needs an iPhone with a lidar sensor</text>')
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
                             "pinned commit, except section one and the VisualAssist grant, "
                             "which are attested and say so. "
                             "The page itself is animated SVG with no JavaScript and no server. "
                             "If a number here is wrong, it is wrong in public.",
              key="plate-7-colophon.svg", col=(118, 762), frame=(44, 161, 25),
              serif=True, bold=False)]
    # The device turns again. Cutting it read as "ambient travel means nothing
    # at an arbitrary camo frame" — but that is the argument against a GESTURE,
    # not a CARRIER. A slow orbit is identical in every frame, so there is no
    # frame at which it misleads, and it is moving at whichever instant the
    # reader is handed. It is also the only motion on the page's last plate,
    # and mutations.mjs probe 11 anchors on these three literals: cutting them
    # left gate.mjs check 13 unexercised, which is this repo's signature
    # defect arriving through a design change.
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
        # TWO groups, because this card carries two claims and used to draw
        # only one. It showed the gzip pair — 66.2 against 422, the 6.4× — and
        # captioned it "The JDK intrinsic beats it." The intrinsic had no bar
        # at all, so the long accent bar was the only thing the sentence could
        # attach to and the reader took away the opposite of the truth. That is
        # the same defect as a wrong verb in the prose, drawn instead of typed.
        #
        # So the checksum group is drawn too, scaled WITHIN itself (4.26 against
        # 14.06) and separated by a gap and a tick — the desktop plate's
        # arrangement at monogram scale. Putting GB/s on the same axis as MB/s
        # would have fixed the caption by telling a different lie.
        #
        # The intrinsic takes INK2, not PINE: teal means "safe / guarded /
        # checked" everywhere else on this page, and the longest, most
        # confident bar meaning "this one beats me" would have been the colour
        # system arguing with the sentence.
        # Four bars have to live inside the ORIGINAL two-bar envelope (bottom
        # ~130). The card glides, so anything reaching y=150 lands on the body
        # line at baseline 168 partway through the loop — gate.mjs caught that
        # on the first attempt, at eight consecutive timesteps.
        return (f'<path d="M300 84V133" stroke="{WIRE}" stroke-width="1"/>'
                # gzip: one thread, then the bounded window
                f'<rect x="300" y="86" width="18.5" height="8" fill="{INK2}"/>'
                f'<rect x="300" y="96" width="118" height="8" fill="{CLAY_G}"/>'
                # the group break — these are different units, not one axis
                f'<path d="M300 109H310" stroke="{WIRE}" stroke-width="1"/>'
                # checksum: mine, then the JDK's — the longest bar on the card
                f'<rect x="300" y="113" width="36" height="8" fill="{CLAY_G}"/>'
                f'<rect x="300" y="123" width="118" height="8" fill="{INK2}"/>')
    if name == "sieve":
        # compact and held above the body lines — the desktop channel owns
        # the full drawing; this is its monogram
        return (f'<g><path d="M330 70L348 132" stroke="{WIRE}" stroke-width="1.6"/>'
                f'<path d="M410 70L392 132" stroke="{WIRE}" stroke-width="1.6"/>'
                f'<path d="M334 86H406" stroke="{WIRE}" stroke-width="1.4" stroke-dasharray="5 4"/>'
                f'<path d="M338 102H402" stroke="{WIRE}" stroke-width="1.4" stroke-dasharray="5 4"/>'
                f'<path d="M342 118H398" stroke="{WIRE}" stroke-width="1.4" stroke-dasharray="5 4"/>'
                f'<rect x="348" y="138" width="44" height="3" fill="{CLAY_G}"/>'
                # head AND shoulders: the bare circle read as a stray mark,
                # not as the human below the gate — the desktop plate's
                # figure, at monogram scale
                f'<circle cx="416" cy="156" r="6" fill="none" stroke="{INK2}" stroke-width="1.4"/>'
                f'<path d="M405 171C405 162 427 162 427 171" fill="none" stroke="{INK2}" stroke-width="1.4"/></g>')
    if name == "redact":
        # THE ONE PLACE THE PHONE WAS ACTUALLY WORSE OFF, and the reason the
        # ground above stopped being transparent. Every other token gains
        # contrast on GitHub's canvas over the paper the gate measures — the
        # smallest gain is day RULE at +0.82 — so for nineteen of the twenty
        # token/theme pairs a borrowed ground was an error of MAGNITUDE, and
        # in the safe direction. Night REDACT was an error of SIGN.
        #
        # 1.29:1 on night paper, 1.27:1 on #0d1117 — nearly the same number
        # describing opposite objects, because #2e2620 sits BETWEEN them:
        # Y(#0d1117)=0.0055 < Y(#2e2620)=0.0207 < Y(#43372f)=0.0413.
        #
        # This motif is an OPPOSITION: two bars withheld, one row returned.
        # Measured at the three bar centres, signed against the surround:
        #
        #   rented #0d1117   withheld +0.0152  withheld +0.0152  returned +0.2548
        #   own paper        withheld -0.0206  withheld -0.0206  returned +0.2190
        #
        # So the defect is not that the voids were invisible — 1.27 is as mute
        # as 1.29. It is that ALL THREE MARKS POINTED THE SAME WAY. Withheld
        # and returned both read as light added to the ground, and the only
        # thing left telling them apart was how much. On paper the withheld
        # bars go negative and the opposition is the drawing again.
        #
        # Night only. Day was never wrong: #26231c is darker than #ffffff and
        # darker than #f2e4c9, so that theme read as applied ink on both
        # grounds (15.68 -> 12.48), which is the reading redact() intends.
        #
        # No numeric floor could have caught it: a contrast ratio is unsigned.
        # That is why the fix is opaque paper and not a different REDACT hex.
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
    if name == "bands":
        # the alert policy at monogram scale: three arcs at TRUE proportion
        # (0.5 / 1.0 / 2.0 m on one scale — 19/38/76u), the two interrupting
        # thresholds in the act's clay, the silent one in the check's pine,
        # and the world approaching as one INK dot. Replaces the "sweep"
        # motif, whose arcs were decorative radii tied to no number.
        out = [f'<circle cx="308" cy="112" r="3" fill="{CLAY_G}"/>']
        for r, col, w in ((19, CLAY_G, 2), (38, CLAY_G, 1.6), (76, PINE, 1.6)):
            dy, dx = r * 0.5, r * 0.866         # ±30° about the axis
            out.append(f'<path d="M{308+dx:.1f} {112-dy:.1f}A{r} {r} 0 0 1 '
                       f'{308+dx:.1f} {112+dy:.1f}" fill="none" stroke="{col}" '
                       f'stroke-width="{w}" stroke-linecap="round"/>')
        out.append(f'<circle cx="400" cy="112" r="4" fill="{INK}"/>')
        return '<g>' + "".join(out) + '</g>'
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
        f"@font-face{{font-family:'S';font-weight:600;src:url(data:font/woff2;base64,{SERIF600}) format('woff2')}}"
        f"text{{font-family:'M',ui-monospace,SFMono-Regular,Menlo,monospace}}"
        f".k{{font-size:13px;letter-spacing:2px;fill:{INK2}}}"
        f".n{{font-size:55px;letter-spacing:-1px;fill:{INK};font-weight:600;font-family:'S',Georgia,serif}}"
        f".u{{font-size:34px;letter-spacing:-0.5px;fill:{INK2}}}"
        f".t{{font-size:21px;fill:{INK2}}}"
        # the glide: a light running the accent rule — constant speed (a
        # runner, not a pendulum: the pendulum's turns measured as stalls),
        # fading out at the far end and back in at the head.
        #
        # RESTORED. It was cut on the argument that GitHub serves these
        # through camo as <img>, so the phase a reader lands on is arbitrary
        # and ambient motion buys nothing. That argument is right about a
        # GESTURE — a one-shot burst most readers never see, whose mid-flight
        # frames are where a frame can lie — and backwards about a CARRIER.
        # A carrier is phase-INVARIANT: every frame of a texture drift says
        # the same thing, so it has no lying frame and it is alive at
        # whatever instant camo hands over. Deleting it kept the fragile
        # class and threw away the robust one. See motion.mjs's v1/v2/v3
        # history: v2 already tried legal stillness and the verdict was
        # "very static feel".
        f".gl{{animation:gl {glide}s linear infinite}}"
        f"@keyframes gl{{0%{{transform:translateX(0);opacity:1}}86%{{transform:translateX({rw-46}px);opacity:1}}"
        f"90%{{opacity:0}}91%{{transform:translateX(0);opacity:0}}95%{{opacity:1}}100%{{transform:translateX(0);opacity:1}}}}"
        f"@media (prefers-reduced-motion: reduce){{*{{animation:none!important}}}}"
        f"</style>"
        # The phone gets the same sheet the desktop does. It used to get a
        # DECLARED ground at zero alpha — the colour was right, the paint was
        # missing — so a phone reader was handed the marks on GitHub's canvas
        # while gate.mjs graded them against paper (it reads the first rect's
        # fill and ignores fill-opacity). Nineteen of the twenty token/theme
        # ratios are more forgiving on the real canvas than on the paper, so
        # that was survivable; see the redaction note in _motif() for the one
        # that is not, and which this rect actually fixes.
        + ground(h, 0, MW),
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
   "from 1.6M Oracle query logs", "a year of it, attested.",
   "Experience, attested by the author rather than derived from a public "
   "repository: as ITSM Data Integration Intern at Miami University, a Python "
   "pipeline turned 1.6 million Oracle Analytics query logs into a 57.8 "
   "million-row field-usage table.", "ledger", "stamp", 10.9),
 "m-1-glyph.svg": ("GLYPH", "CLAY_G", "3.5", "×", "Someone else’s net, made", "faster by hand. 97.01% held.",
   "Glyph: a course-provided neural network, hand-optimised — 3.5 times faster on the committed dot benchmark, accuracy unchanged at 97.01 percent.",
   "left", "copybook", 12.3),
 "m-2-jetpack.svg": ("JETPACK", "CLAY_G", "6.4", "×", "Parallel gzip on JDK 25.", "The JDK intrinsic beats it.",
   "jetpack: parallel gzip on JDK 25, a 6.4 times speedup over one thread — and the JDK's own checksum intrinsic still wins.",
   "left", "bench", 9.1),
 "m-4-applied.svg": ("APPLIED", "CLAY_G", "0.979", "", "macro-F1, rules layer only.", "Below 0.85 it asks a human.",
   "Applied: an email classifier scoring 0.979 macro-F1 with the rules layer alone. Below the 0.85 confidence gate it asks a human rather than guessing.",
   "left", "sieve", 11.3),
 "m-5-refusal.svg": ("CADENCE", "PINE", "B", " only", "The app didn’t remember to", "filter — the database did.",
   "Cadence: an unfiltered query run as tenant B returns B only. The app didn't remember to filter; PostgreSQL row-level security refused.",
   "left", "redact", 8.9),
 "m-6b-automl.svg": ("AGENTIC AUTOML", "CLAY_G", "44", "", "tools in the registry. The", "model holds its phase’s set.",
   "Agentic AutoML: dataset in, trained model out. Its registry holds 44 tool definitions, but the model only ever holds the set its phase needs.",
   "left", "dial", 12.9),
 # Round 23 re-hung this plate on the section's real numbers. "LiDAR" as the
 # hero was a technology name where every other m-plate leads with a measured
 # claim; the rewritten section is about three fixed distances, so the phone
 # reader now gets the nearest threshold at claim size and the policy's two
 # poles in the body lines. 24 characters each — the budget here is 27 (the
 # phone column runs 30-412 and gate.mjs counts, not the em dashes; the old
 # "Depth in, speech and haptics out." overflowed to 462 and was caught at
 # every sampled timestep). No exclamation mark and no double quotes: the
 # mono face's subset carries neither (charsets.py), and a paraphrase in the
 # face the page owns beats the exact utterance in a platform fallback.
 "m-8-visualassist.svg": ("VISUALASSIST", "CLAY_G", "0.5", " m", "Inside it the phone says", "Stop. At 2.0 m, silence.",
   "VisualAssist: an iPhone app for low-vision users, in Swift. Inside 0.5 "
   "metres the phone interrupts — a continuous haptic at full strength and "
   "speech that names the direction and the distance; at 2.0 metres it is "
   "deliberately silent. No live link — it needs an iPhone with a lidar sensor.",
   "left", "bands", 10.1),
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
