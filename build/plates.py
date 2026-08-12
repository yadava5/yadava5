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
from charsets import MONO_CHARS, BOLD_CHARS, SERIF_CHARS, TEXT_CHARS
FONT = base64.b64encode((ROOT / "mono-subset.woff2").read_bytes()).decode()
SERIF600 = base64.b64encode((ROOT / "serif-600-subset.woff2").read_bytes()).decode()
FONTSERIF = base64.b64encode((ROOT / "serif-subset.woff2").read_bytes()).decode()
FONTTEXT = base64.b64encode((ROOT / "text-subset.woff2").read_bytes()).decode()

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
        # ONE accent, not two. The split was text #f4b090 6.28:1 and graphics
        # #e08a5f 4.36:1 — and the graphics token is what carried EMPHASIS: the
        # 79 confident misses, the 15-tool base set, the lit index numeral. So
        # the colour meaning "look here" sat at 43% of the contrast of the
        # ordinary ink it was meant to stand out from. Emphasis that recedes.
        # 7.08:1 measured, against INK2's 7.54 — parity with the body ink
        # rather than half of it, and it keeps its chroma (LCh C27.6). Parity
        # with INK itself is unreachable: on this ground an orange cannot
        # reach 10:1 without going pastel, so the ceiling plus chroma is the
        # honest target. Both names kept, one hex, so no call site churns.
        CLAY="#f7bfa2", CLAY_G="#f7bfa2",   # 7.08:1 — accent, text and graphics
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
        # same merge, same reasoning: was text #a03f20 5.18 / graphics #c4532e
        # 3.62. 5.76:1 measured against INK2's 5.79 — parity, and C51.7 chroma.
        CLAY="#953a1d", CLAY_G="#953a1d",   # 5.76:1 — accent, text and graphics
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

# ── THE GROUND LADDER: rotate hue, hold luminance. Round 27.
#
# The client's verdict on the one-paper system was exact: "the card color is
# same, they are still cards." The 2026-08-08 retirement of hue-per-project was
# right about ACCENTS — six accent hues taught a lookup table that paid off
# nowhere — and wrong to take the paper with it: nine sheets of identical brown
# is the sameness he named. So the hue comes back where it belongs, in the
# STOCK, not the ink: each section's plate is printed on its own paper, solved
# in LCh at EXACTLY the reference ground's WCAG relative luminance (dark
# Y=0.041309, light Y=0.785811, dY 0.000% — bisected, not eyeballed), so every
# contrast ratio in the file carries over unchanged. INK, CLAY and PINE do not
# rotate: one hand, one ink, one pair of semantic accents, different paper.
#
# Chroma is C=16 on both themes — twice the reference brown's C=8 in dark,
# just past the reference cream's C=14.9 in light — chosen by rendering the
# candidates at plate scale and looking: C=10 was a whisper (the timidity the
# verdict was about), C=18+ turned the light stock to candy. The mid tokens
# (RULE/WIRE, the ruling printed on the stock) rotate with their paper at
# their own reference Y; dark REDACT rotates so the void stays a darker cut of
# its own sheet; light REDACT stays #26231c on every stock — a redaction on
# paper is black ink, whatever the paper.
#
# Every hex below is solved output, and every ratio in the comments is
# measured on that hex (WCAG 2.x, same formula as gate.mjs:738). Worst text
# token anywhere: INK3 light 4.72:1 (floor 4.5, reference was 4.74 — hex
# rounding). APCA spot floors, dark: INK2 Lc -70.9, INK3 Lc -61.3 on every
# new paper (dim-text floor 60). The two shipped rest-state alphas were
# re-composited on their new stocks: glyph's pen ghost #a19e8c 4.27:1 night /
# #49463b 7.55:1 day (floor 3.0); applied's stream token fill 3.29 / 4.07
# with its full-strength CLAY stroke carrying the escape besides.
PAPERS: dict[tuple[str, str], dict[str, str]] = {
    # II · jetpack — the bench sheet on instrument steel (H200)
    ("jetpack", "dark"):  dict(GROUND="#104041", RULE="#7d8f8f", WIRE="#8da0a0", REDACT="#122b2c"),
    #   INK 10.03 · INK2 7.51 · INK3 6.37 · CLAY 7.06 · PINE 6.82 · RULE 3.38 · WIRE 4.19
    ("jetpack", "light"): dict(GROUND="#beeeef", RULE="#698484", WIRE="#577272", REDACT="#26231c"),
    #   INK 12.44 · INK2 5.78 · INK3 4.72 · CLAY 5.75 · PINE 5.95 · RULE 3.18 · WIRE 4.11
    # III · glyph — the copybook on schoolroom manila (H110)
    ("glyph", "dark"):    dict(GROUND="#393b22", RULE="#8c8c80", WIRE="#9d9d91", REDACT="#28291a"),
    #   INK 10.08 · INK2 7.55 · INK3 6.40 · CLAY 7.09 · PINE 6.85 · RULE 3.39 · WIRE 4.21
    ("glyph", "light"):   dict(GROUND="#e7e8c8", RULE="#80806f", WIRE="#6d6e5d", REDACT="#26231c"),
    #   INK 12.52 · INK2 5.81 · INK3 4.75 · CLAY 5.78 · PINE 5.99 · RULE 3.20 · WIRE 4.15
    # IV · automl — the stores ledger on baize green (H150)
    ("automl", "dark"):   dict(GROUND="#273f2d", RULE="#838f85", WIRE="#94a096", REDACT="#1d2b20"),
    #   INK 10.01 · INK2 7.50 · INK3 6.36 · CLAY 7.05 · PINE 6.80 · RULE 3.40 · WIRE 4.21
    ("automl", "light"):  dict(GROUND="#cfedd6", RULE="#738376", WIRE="#617164", REDACT="#26231c"),
    #   INK 12.49 · INK2 5.80 · INK3 4.74 · CLAY 5.77 · PINE 5.97 · RULE 3.20 · WIRE 4.13
    # V · cadence — the disclosure file on records-office slate (H260)
    ("cadence", "dark"):  dict(GROUND="#223c51", RULE="#838d97", WIRE="#949ea9", REDACT="#1b2935"),
    #   INK 10.02 · INK2 7.51 · INK3 6.36 · CLAY 7.05 · PINE 6.81 · RULE 3.39 · WIRE 4.21
    ("cadence", "light"): dict(GROUND="#cfe9ff", RULE="#728190", WIRE="#606e7d", REDACT="#26231c"),
    #   INK 12.51 · INK2 5.81 · INK3 4.75 · CLAY 5.78 · PINE 5.98 · RULE 3.19 · WIRE 4.16
    # VI · applied — the mailroom channel on madder rose (H350)
    ("applied", "dark"):  dict(GROUND="#4e313e", RULE="#97888e", WIRE="#a8989f", REDACT="#34232a"),
    #   INK 10.02 · INK2 7.51 · INK3 6.37 · CLAY 7.05 · PINE 6.81 · RULE 3.40 · WIRE 4.18
    ("applied", "light"): dict(GROUND="#ffdcec", RULE="#8f7982", WIRE="#7c6770", REDACT="#26231c"),
    #   INK 12.47 · INK2 5.79 · INK3 4.73 · CLAY 5.76 · PINE 5.96 · RULE 3.20 · WIRE 4.14
    # VII · visualassist — the calibration card on night violet (H320)
    ("visualassist", "dark"):  dict(GROUND="#453349", RULE="#928993", WIRE="#a39aa5", REDACT="#2e2431"),
    #   INK 10.07 · INK2 7.55 · INK3 6.40 · CLAY 7.09 · PINE 6.85 · RULE 3.41 · WIRE 4.24
    ("visualassist", "light"): dict(GROUND="#f4def9", RULE="#877b8a", WIRE="#756978", REDACT="#26231c"),
    #   INK 12.44 · INK2 5.78 · INK3 4.72 · CLAY 5.74 · PINE 5.95 · RULE 3.19 · WIRE 4.12
    # I · work keeps the reference kraft verbatim — the account book is the
    # paper the whole system was measured on, and it stays byte-identical.
    # 0 and ∎ (thesis, colophon) own no paper at all; see F1_CANVAS.
}

# section per published file. The mobile card is the same sheet as its plate.
PAPER_OF: dict[str, str] = {
    "plate-0b-work.svg": "work",        "m-0b-work.svg": "work",
    "plate-1-glyph.svg": "glyph",       "m-1-glyph.svg": "glyph",
    "plate-2-jetpack.svg": "jetpack",   "m-2-jetpack.svg": "jetpack",
    "plate-4-applied.svg": "applied",   "m-4-applied.svg": "applied",
    "plate-5-refusal.svg": "cadence",   "m-5-refusal.svg": "cadence",
    "plate-6b-automl.svg": "automl",    "m-6b-automl.svg": "automl",
    "plate-8-visualassist.svg": "visualassist", "m-8-visualassist.svg": "visualassist",
    "plate-0-thesis.svg": "work",       "m-0-thesis.svg": "work",       # transparent
    "plate-7-colophon.svg": "work",     "m-7-colophon.svg": "work",     # transparent
}


def set_paper(section: str) -> None:
    """Point the five paper tokens at this plate's own stock.

    Resets from THEMES first, so papers never leak between plates: a build
    that forgot to call this would print every plate on the reference kraft,
    which is exactly the shipped state before round 27 — wrong, but never
    silently mis-measured, because gate.mjs reads the ground off each plate's
    own first <rect> whatever colour it is.
    """
    t = THEMES[THEME]
    fam = PAPERS.get((section, THEME), {})
    for k in ("GROUND", "RULE", "WIRE", "REDACT"):
        globals()[k] = fam.get(k, t[k])
    globals()["ROW"] = globals()["RULE"]


# ── F1: the two frontispieces (title page, colophon) carry NO paper at all —
# pure ink on GitHub's own canvas, so the document opens and closes on the
# page itself and the seven sheets between read as objects laid on it. The
# declared hex is the canvas each theme is GRADED against, and it is the
# WORST of the canvases GitHub actually serves that theme on: dark readers
# hold #0d1117, #22272e (dimmed) or #010409 (high contrast), and #22272e is
# the lightest of the three, so light ink measured there clears the floor on
# all of them; light themes are white. Measured on that worst case:
#   dark  · INK 13.14:1 (Lc -94.6) · INK2 9.85:1 (Lc -75.5) · INK3 8.35:1
#           (Lc -66.0) · RULE 4.44:1 — and higher on the other two canvases
#   light · INK 15.68:1 (Lc +102.6) · INK2 7.28:1 · INK3 5.95:1 · RULE 4.01:1
# gate.mjs reads data-canvas and grades against it instead of a first <rect>;
# a plate declaring it while also painting a sheet fails there, deliberately.
F1_CANVAS = {"dark": "#22272e", "light": "#ffffff"}


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
         serif: bool = False, bold: bool = True, mono: bool = True,
         canvas: str | None = None) -> str:
    """Open a plate.

    `col` and `frame` are this plate's DECLARED geometry, written into the SVG
    root as data-col / data-frame and asserted by gate.mjs (checks 5 and 12):
    no edge is ever an accident — the file states its geometry and the render
    must match — without forcing every plate into one frame.
    `frame` is (top, rightGap, bottomGap): measured ink extents this plate
    stands behind, in viewBox units.
    `serif` embeds the serif face — only the two plates that speak in it pay
    its 10KB.
    `canvas` declares this plate TRANSPARENT (an F1 frontispiece): it names
    the worst GitHub canvas the theme is graded against — see F1_CANVAS —
    and the plate must then paint no sheet, which gate.mjs asserts.
    """
    if key:
        # The light pass re-authors the same key. A plate and its light twin
        # must carry byte-identical descriptions — asserted, not assumed.
        if key in ALT and ALT[key] != desc:
            raise SystemExit(f"{key}: description diverged between themes")
        ALT[key] = desc
    fr = f' data-frame="{frame[0]:g},{frame[1]:g},{frame[2]:g}"' if frame else ''
    cv = f' data-canvas="{canvas}"' if canvas else ''
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
    # 'M' is conditional for the same reason: it is the MARKED case now, not
    # the default, so a plate that quotes no machine artifact should not carry
    # its payload. gate.mjs fails a declared-but-unrendered face, so this is
    # enforced rather than remembered.
    mon = (f"@font-face{{font-family:'M';font-weight:400;"
           f"src:url(data:font/woff2;base64,{FONT}) format('woff2')}}\n") if mono else ''
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="{VB_X} 0 {VB_W} {h}" width="{VB_W}" height="{h}" role="img" aria-label="{desc}" data-col="{col[0]},{col[1]}"{fr}{cv}>
<title>{title}</title><desc>{desc}</desc>
<style>
@font-face{{font-family:'T';font-weight:400;src:url(data:font/woff2;base64,{FONTTEXT}) format('woff2')}}
{mon}{ser600}{ser}text{{font-family:'T',Georgia,serif}}
.mach{{font-family:'M',ui-monospace,SFMono-Regular,Menlo,monospace}}
.hero{{font-size:55px;letter-spacing:-1px;fill:{INK};font-weight:600;font-family:'S',Georgia,serif}}
.sub{{font-size:34px;letter-spacing:-0.5px;fill:{INK};font-weight:600;font-family:'S',Georgia,serif}}
.unit{{font-size:34px;letter-spacing:-0.5px;fill:{INK2}}}
.say{{font-size:21px;fill:{INK2}}}
.lbl{{font-size:13px;letter-spacing:1.2px;fill:{INK2}}}
.key{{font-size:13px;letter-spacing:1.2px;fill:{INK}}}
.fine{{font-size:13px;letter-spacing:0px;fill:{INK2}}}
.kick{{font-size:13px;letter-spacing:2px;fill:{INK3}}}
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


# (arrow()/arrowed() — the drawn → that advanced one mono cell — left with
# their last caller, applied's ONNX size pair, in round 28. Their ruling
# outlives them in charsets.py: the subsets still omit U+2192 on purpose, so
# the coverage gate fails loudly on anyone who types the character instead of
# drawing it. CELL_13 went with them; nothing measures on the mono grid now.)


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


def redact_bar(x: float, y: float, w: float, h: float, rx: float = 2,
               cls: str = "", extra: str = "") -> str:
    """A withheld record: the mute bar, plus a HATCH that makes it an act.

    The docstring above still stands on luminance — do not darken REDACT. This
    is the other axis. Night REDACT is 1.29:1 on night paper, and a design
    review measured the bars at APCA Lc 0.0, reading as six EMPTY outlined
    boxes: "tenant A has no rows", which is a materially different claim from
    "tenant A's rows were withheld by the database". A meaning inversion on the
    plate's central evidence, present in every frame of the dark theme.

    Luminance cannot fix it and the arithmetic says so. Night ground #43372f
    has relative luminance 0.0414, so even PURE BLACK caps the ratio at
    (0.0414+0.05)/0.05 = 1.83:1 — half a stop, nowhere near separation. Real
    separation needs a fill LIGHTER than the ground, which flips removal into
    highlight: the exact sign error the phone shipped once, recorded above.

    So the fix adds STRUCTURE, not luminance. Hatch in WIRE — 5.44:1 on the
    fill at night, 3.02:1 on day ink — clearly-read strokes over a bar whose
    1.29:1 mute void is left exactly as authored. A hatched bar cannot read as
    an empty box, and it does not shout.

    45 degrees ASCENDING, deliberately: tenant B's returned rows carry
    HORIZONTAL record-lines, and a hatch that rhymed with them would blur the
    one opposition this plate exists to draw. 6u perpendicular pitch, round
    caps, endpoints inset 1u so the strokes stop inside the bar and no clip
    path is needed. Hairlines in the same <g> as the bar, so the collision
    rules' same-group exemption covers them by construction.
    """
    PITCH = 6.0                       # perpendicular; horizontal period 6*sqrt2
    period = PITCH * 2 ** 0.5
    inset = 1.0
    x_lo, x_hi = x + inset, x + w - inset
    y_lo, y_hi = y + inset, y + h - inset
    seg = []
    x0 = x - h                        # first "/" whose top-right can enter the bar
    while x0 <= x + w:
        t1 = max(x_lo, x0 + inset)
        t2 = min(x_hi, x0 + h - inset)
        if t2 - t1 > 0.5:             # skip corner slivers that read as dirt
            seg.append(f"M{t1:.1f} {y + h - (t1 - x0):.1f}L{t2:.1f} {y + h - (t2 - x0):.1f}")
        x0 += period
    hatch = (f'<path d="{"".join(seg)}" stroke="{WIRE}" stroke-width="1" '
             f'stroke-linecap="round" fill="none"/>') if seg else ''
    c = f' class="{cls}"' if cls else ''
    # The re-strike animation rides the GROUP, not the rect: transform-box
    # fill-box works on a <g>, so the wipe carries the hatch with the bar and
    # t=0 stays the authored redacted frame.
    return (f'<g{c}{extra}><rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" '
            f'rx="{rx:g}" {redact()}/>{hatch}</g>')


# ────────────────────────────────────────────────────────────── PLATE 0
def plate_thesis() -> str:
    """The frontispiece. Room: a title page — and no card under it, at all.

    Round 27, and the room changes for the first time since the paper system
    landed. The client's verdict on the nine-sheet set was "they are still
    cards ... all the card looks same as hell", and the title page was the
    worst offender: a 15-run index restating the seven section headers that
    sit in prose forty pixels below it, on the same brown sheet as every
    other plate. Both cuts land here. The index is gone — the READ chase it
    carried moves onto a single row of seven sigils, which is all the
    teaching the system actually needs (one mark per section, met again
    beside each plate) — and the sheet goes with it: this plate paints NO
    ground and NO frame. Pure ink on GitHub's own canvas, so the document
    opens on the page itself and the seven papers that follow read as sheets
    laid upon it. A transparent plate's grading floors live at F1_CANVAS.

    What remains is what the prose forty pixels down cannot carry: the name,
    one serif sentence, the contact line, and the sigil row with its folio
    numerals. The numerals are set in the TEXT face, not the mono — a folio
    number is typography, not a machine value; the mono face is not aboard
    this plate at all.

    Motion: the compositor's rule is the CARRIER — a dashed rule drifting
    toward the turning diamond, ten dash periods per wrap so the loop is
    invisible — and the read is the GESTURE: the seven sigils lift to full
    ink one by one, each with its numeral, the reader's eye walking the row;
    once per cycle the row rings together, the title page's one chord.
    Colour and 18% scale only; nothing travels, so no frame can lie.
    """
    H, CX = 348, 440
    TC = 11.9                      # the read's clock — coprime with 9.4 and 27
    s = [head(H, "Ayush Yadav — computer science graduate, Cincinnati OH",
              "Ayush Yadav — systems, from SIMD kernels to the browser they run "
              "in. A computer science graduate in Cincinnati, Ohio, open to "
              "full-time software engineering roles. The seven sections that "
              "follow are marked here as a row of sigils, one per system; each "
              "mark returns beside its own plate.", key="plate-0-thesis.svg",
              col=(118, 762), frame=(46, 103, 23), serif=True, bold=False,
              mono=False, canvas=F1_CANVAS[THEME])]
    s.append(f""".ser{{font-family:'S',ui-serif,Georgia,'Times New Roman',serif;font-size:34px;fill:{INK}}}
.orn{{transform-box:fill-box;transform-origin:center;animation:orn 27s linear infinite}}
@keyframes orn{{from{{transform:rotate(45deg)}}to{{transform:rotate(405deg)}}}}
/* the rule drifts toward the diamond — 75u is ten dash periods, so the wrap
   is invisible by construction. This is the plate's carrier: a texture drift
   says the same thing in every frame, so the arbitrary frame camo hands a
   reader is never a lying one. */
.led{{animation:led 9.4s linear infinite}}
@keyframes led{{from{{stroke-dashoffset:0}}to{{stroke-dashoffset:-75}}}}
""")
    # the read: sigil i lifts INK2 -> INK across its window, its numeral
    # INK3 -> INK on the same clock, and the row rings together at 91-97.5%.
    # The colour animates on the WRAPPER <g>, whose style owns `color`, and
    # every stroke inside is drawn in currentColor — the inheritance is real,
    # so this cannot repeat 6aec558 (an animation running on a parent whose
    # child owns the property, an instrument-satisfying no-op). The swell
    # rides the same wrapper, comma-joined.
    for i in range(7):
        w0, w1 = i * 88 / 7 + 0.8, (i + 1) * 88 / 7 - 0.8
        s.append(f".sg{i}{{transform-box:fill-box;transform-origin:center;"
                 f"animation:sgc{i} {TC}s linear infinite,sgw{i} {TC}s {BREATHE} infinite}}"
                 f"@keyframes sgc{i}{{0%,{w0:.1f}%{{color:{INK2}}}{w0+1.2:.1f}%,{w1:.1f}%{{color:{INK}}}"
                 f"{w1+1.2:.1f}%,91%{{color:{INK2}}}93%,95.5%{{color:{INK}}}97.5%,100%{{color:{INK2}}}}}"
                 f"@keyframes sgw{i}{{0%,{w0:.1f}%{{transform:scale(1)}}{(w0+w1)/2:.1f}%{{transform:scale(1.18)}}"
                 f"{w1+1.2:.1f}%,91%{{transform:scale(1)}}94%{{transform:scale(1.12)}}"
                 f"97.5%,100%{{transform:scale(1)}}}}")
        s.append(f".nm{i}{{animation:nm{i} {TC}s linear infinite}}"
                 f"@keyframes nm{i}{{0%,{w0:.1f}%{{fill:{INK3}}}{w0+1.2:.1f}%,{w1:.1f}%{{fill:{INK}}}"
                 f"{w1+1.2:.1f}%,91%{{fill:{INK3}}}93%,95.5%{{fill:{INK}}}97.5%,100%{{fill:{INK3}}}}}")
    s.append("</style>")

    s.append(f'<text x="{CX}" y="{TOP}" text-anchor="middle" class="key" style="letter-spacing:5px">AYUSH YADAV</text>')
    s.append(f'<text x="{CX}" y="84" text-anchor="middle" class="kick">CS GRADUATE · CINCINNATI, OHIO</text>')

    # the one serif voice, opening the bracket the colophon closes
    for i, ln in enumerate(["Systems, from SIMD kernels", "to the browser they run in."]):
        s.append(f'<text x="{CX}" y="{140 + i*42}" text-anchor="middle" class="ser">{ln}</text>')
    s.append(f'<text x="{CX}" y="214" text-anchor="middle" class="fine">Open to full-time software engineering roles · aesh.03.23@gmail.com</text>')

    # the compositor's rule: dashes running toward a set diamond that turns —
    # the page's first motion, and its carrier. One group, composed on purpose.
    s.append(f'<g><path class="led" d="M300 246H580" style="stroke:{INK2}" '
             f'stroke-width="1.5" stroke-dasharray="1.5 6"/>'
             f'<g transform="translate(440,246)"><rect class="orn" x="-4" y="-4" width="8" height="8" fill="{INK2}"/></g></g>')

    # ── the sigil row: the whole index, compressed to its marks. One mark
    # per section in reading order, folio numeral beneath, and the read
    # walks it. Row I has no product logo — its device is the attested
    # stamp at sigil scale, in currentColor so it rides the same chase.
    SIGILS = [None, "JETPACK", "GLYPH", "AUTOML", "CADENCE", "APPLIED", "VISUALASSIST"]
    NUMERALS = ["I", "II", "III", "IV", "V", "VI", "VII"]
    for i, mk in enumerate(SIGILS):
        cx = 200 + i * 80
        if mk:
            s.append(f'<g class="sg{i}" style="color:{INK2}">'
                     + logo(mk, cx - 9, 279, 18, "currentColor") + '</g>')
        else:
            s.append(f'<g class="sg{i}" style="color:{INK2}">'
                     f'<g transform="translate({cx},288) rotate(-8)">'
                     f'<rect x="-8.5" y="-6" width="17" height="12" rx="2" '
                     f'fill="none" stroke="currentColor" stroke-width="1.4"/>'
                     f'<path d="M-4.5 1H4.5" stroke="currentColor" stroke-width="1.4"/></g></g>')
        s.append(f'<text x="{cx}" y="322" text-anchor="middle" class="kick nm{i}">{NUMERALS[i]}</text>')
    return "".join(s) + "</svg>"

# ────────────────────────────────────────────────────────── PLATE I — WORK
def plate_work() -> str:
    """The ledger. Room: an account book.

    A year of paid engineering and a national competition, none of it in a
    repository a reader can clone — so the warrant is testimony, and the
    plate is the document testimony lives in: an account book. Date column
    left, item in the middle, AMOUNTS RIGHT-ALIGNED AT THE PAGE EDGE, full-
    width row rules, a double rule opening and closing the account.

    Round 28 cuts the account to its rulings. The verdict this round answers
    is "too much text in every card for no reason", and the ledger was the
    densest sheet in the set: 31 runs, most of them detail lines restating
    the README paragraph directly below the plate. The F3 exception stands —
    a ledger IS rows — but a row is a date, an item and an amount, not an
    item plus two captions. So: the 10,453 inventory row goes (the weakest
    figure, prose keeps it), every second caption line goes, the three
    column heads go (a four-row account does not need PERIOD/ITEM/FIGURE
    taught), and each row's one indispensable qualifier moves INTO its item
    line — FROM 1.6M ORACLE LOGS, FROM 0, 349K PATIENTS — because a figure
    whose baseline is missing is a lie of omission, not a shorter truth.
    Seventeen runs. The stamp stays: the attestation IS the claim, and the
    source line stays with it, the one plate whose source is testimony.

    THE LEDGER STILL HOLDS STILL (round 24's retraction, kept): a travelling
    rule can render a true claim struck through on the arbitrary frame camo
    serves. The one motion is semantic — the two linkage bars run tick-
    streams at rates proportional to 99.6 and 32, the comparison performing
    its own fractions.
    """
    H = 560
    s = [head(H, "Experience: a year as ITSM Data Integration Intern at Miami University, and "
                 "team lead at DataFest 2026",
              "Experience, drawn as a ledger. As ITSM Data Integration Intern at Miami "
              "University, June 2025 to May 2026: a 57.8 million-row field-usage table "
              "from 1.6 million Oracle Analytics query logs, and code compliance lifted "
              "from 0 to 96.72 percent across a 61-project portfolio. At DataFest 2026, "
              "team lead of 3: 90-day care utilisation modelled at 0.90 holdout AUC for "
              "349 thousand patients, preserving 99.6 percent of social-determinant "
              "linkage against 32 percent under a naive join. These figures are attested "
              "by the author rather than derived from a public repository.",
              key="plate-0b-work.svg",
              frame=(44, 64, 24))]
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

    # the institution joins the account header — a 47-char employer line
    # beside a date column measured 8u into the figure column (rendered and
    # looked at, not estimated), and the ledger's own grammar had the answer:
    # an account book names the house at the head of the page, not per entry
    s.append(f'<text x="{L}" y="{TOP}" class="lbl">ACCOUNT OF A YEAR’S PAID WORK — MIAMI UNIVERSITY</text>')
    s.append(f'<text x="{R}" y="{TOP}" text-anchor="end" class="lbl">No. I — WORK</text>')
    # a ledger opens and closes with a double rule
    s.append(f'<path d="M{L} 68H{R}M{L} 72H{R}" stroke="{RULE}"/>')

    s.append(f'<text x="{L}" y="100" class="key">ITSM DATA INTEGRATION INTERN</text>')
    s.append(f'<text x="{R}" y="100" text-anchor="end" class="kick">JUN 2025 – MAY 2026</text>')
    s.append(f'<path d="M{L} 116H{R}" stroke="{RULE}"/>')

    # each item carries its own baseline in the label — FROM 1.6M LOGS, FROM 0
    # — because a figure whose denominator moved to the prose reads as bigger
    # than it is, and this sheet's warrant is already only testimony. Labels
    # sit at the column edge: the per-row date column is gone (the dates are
    # one line, above), and 34px serif figures are ~21u a glyph — a label
    # starting at 290 met "57.8M" at 621 and lost.
    for y, lab, amt in ((150, "FIELD-USAGE TABLE — FROM 1.6M ORACLE LOGS", "57.8M"),
                        (206, "CODE COMPLIANCE, 61 PROJECTS — FROM 0", "96.72%")):
        s.append(f'<text x="{L}" y="{y}" class="lbl">{lab}</text>')
        s.append(f'<text x="{R}" y="{y}" text-anchor="end" class="sub">{amt}</text>')
        s.append(f'<path d="M{L} {y+16}H{R}" stroke="{RULE}"/>')

    s.append(f'<text x="{L}" y="252" class="kick">DATAFEST 2026 — TEAM LEAD OF 3 · NATIONAL ASA</text>')
    s.append(f'<path d="M{L} 266H{R}" stroke="{RULE}"/>')

    s.append(f'<text x="{L}" y="300" class="lbl">HOLDOUT AUC — 349K PATIENTS, 90-DAY WINDOW</text>')
    s.append(f'<text x="{R}" y="300" text-anchor="end" class="sub">0.90</text>')
    s.append(f'<path d="M{L} 316H{R}" stroke="{RULE}"/>')

    s.append(f'<text x="{L}" y="350" class="lbl">OF SOCIAL-DETERMINANT LINKAGE PRESERVED</text>')
    s.append(f'<text x="{R}" y="350" text-anchor="end" class="sub">99.6%</text>')
    # the linkage claim is a comparison, so draw the comparison twice over:
    # LENGTH (widths always 300*frac from the value beside them), full ink for
    # the preserved fraction against half ink for the naive one, and the
    # tick-streams flowing at the two rates — the one chart on the plate
    for j, (frac, tag, fill, cls) in enumerate([(0.996, "", INK, "bf0"),
                                                (0.32, "32% naive", INK2, "bf1")]):
        yy = 366 + j * 20
        w = 300 * frac
        s.append(f'<g><rect x="{L}" y="{yy}" width="300" height="12" fill="none" stroke="{WIRE}"/>'
                 f'<rect x="{L}" y="{yy}" width="{w:.2f}" height="12" fill="{fill}"/>'
                 f'<path class="{cls}" d="M{L} {yy+6}H{L+w:.1f}" stroke="{GROUND}" '
                 f'stroke-opacity="0.55" stroke-width="4" stroke-dasharray="2 4"/></g>')
        if tag:
            s.append(f'<text x="462" y="{yy+11}" class="fine">{tag}</text>')

    # ── the account closes, and the closing rule RUNS INTO THE STAMP.
    #
    # (Round 26's occlusion ruling, kept through the round-28 shortening: the
    # rules end at x=600, the stamp's own centre, and the stamp's opaque body
    # is what terminates them — the upper one surfaces further right than the
    # lower, which is the occlusion reading itself off the -7 degree rake and
    # what tells a reader the stamp is ON the sheet rather than tangled in the
    # ruling. The "32% naive" tag's bbox ends ~5u clear of the stamp's raked
    # top edge — round 24's collision, re-measured at the new coordinates.)
    s.append(f'<path d="M{L} 424H600M{L} 428H600" stroke="{RULE}"/>')

    # ── the stamp. Rotated, struck over the closing rule — the whole section's
    # warrant in one device. Its two texts share the stamp's <g>, which is what
    # makes the composition legal to the collision checks (gate.mjs:353).
    #
    # The GROUND fill is the occluder and it is free of the contrast gate twice
    # over: a non-text fill is skipped outright when the shape's own stroke
    # clears 3.0 (INK3 measures 6.39:1 night / 4.74:1 day), and paper-on-paper
    # computes 1.00:1, which the gate waves through explicitly as "it IS the
    # slab". The rules that pass beneath are 1u paths — hairlines, and hairlines
    # are exempt from the graphic-on-graphic rule — so nothing here is legal by
    # luck.
    s.append(f'<g transform="translate(600,450) rotate(-7)"><g>'
             f'<rect x="-110" y="-31" width="220" height="62" rx="8" fill="{GROUND}" stroke="{INK3}" stroke-width="2"/>'
             f'<text x="0" y="-2" text-anchor="middle" class="say" style="fill:{INK3};letter-spacing:4px">ATTESTED</text>'
             f'<text x="0" y="22" text-anchor="middle" class="kick">ON MY WORD</text>'
             f'</g></g>')

    # the source footer stays on THIS plate alone: everywhere else the source
    # line was a caption restating the claims file, but here the attestation
    # IS the claim, and the line is the only place the sheet says so plainly
    s.append(f'<text x="{L}" y="532" class="fine mach" style="fill:{INK3}">source: my word — not derivable from a public repo</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── PLATE II
def plate_jetpack() -> str:
    """The bench sheet. Room: a test-bench record.

    The question is "is hand-vectorised code actually faster?", and the
    honest answer is BOTH WAYS: 6.4x on the parallel path, and a checksum
    that loses to the JDK's own intrinsic, printed here as the reference.

    Round 28 cuts the sheet to that one sentence. The conveyor — four
    blocks, six keyframe sets, a bracket, three captions — was a diagram of
    a MECHANISM (the bounded in-flight window), and the mechanism's whole
    story is in the README paragraph directly below; the gzip lane's two
    bars restated a ratio the hero already carries. What the prose cannot
    carry is the shape of the loss: three bars at TRUE SCALE — 1.52 scalar,
    4.26 mine, 14.06 the intrinsic, the longest and in PINE because the
    reference stands — and the two checksums printed IDENTICAL, which is
    the one figure that makes "not beaten" honest rather than modest. The
    hexes carry no labels saying whose is whose, deliberately: they are the
    same eight glyphs, and not being able to tell them apart IS the claim.

    Motion: the conveyor's carrier is re-sited into the bars — each runs
    the ledger's tick-stream idiom at a rate proportional to its own
    throughput, so the comparison performs its fractions in every frame
    (dash cycle 12u, offset rate 0.6u/s per GB/s; the wrap is seamless and
    frame zero is authored). Periods 13.2 / 4.7 / 1.4s, phase-invariant:
    no frame can lie, whichever instant camo hands a reader.
    """
    H, a = 336, CLAY_G
    VALS = (1.52, 4.26, 14.06)
    s = [head(H, "jetpack — 6.4x parallel, and the intrinsic it does not beat",
              "jetpack: parallel gzip on JDK 25 — a 6.4 times speedup over one thread. Its "
              "hand-vectorised Adler-32 checksum reaches 4.26 gigabytes per second, 2.80 "
              "times the 1.52 scalar baseline, and returns bit-identical output to "
              "java.util.zip, drawn as two identical checksums — whose own intrinsic is "
              "faster still at 14.06 and takes the longest bar on the sheet: not beaten, "
              "the reference stands.",
              key="plate-2-jetpack.svg", frame=(30, 64, 21))]
    # one keyframe set per bar because each runs at its OWN rate — the rate is
    # the datum. 12u is one full dash cycle at "2 4"x2, so the wrap is seamless.
    for k, v in enumerate(VALS):
        s.append(f".bj{k}{{animation:bj{k} {20/v:.2f}s linear infinite}}"
                 f"@keyframes bj{k}{{from{{stroke-dashoffset:0}}to{{stroke-dashoffset:-12}}}}\n")
    s.append(f"</style>{ground(H)}")

    s.append(f'<text x="{L}" y="40" class="kick">II · JETPACK</text>')

    # ── the parallel result, one figure — the mechanism behind it lives in
    # the prose one scroll-line down, where it was already stated verbatim
    s.append(f'<text x="{L}" y="110" class="hero">6.4<tspan class="unit">×</tspan></text>')
    s.append(f'<text x="{L}" y="138" class="lbl">PARALLEL GZIP · JDK 25</text>')

    # ── the verification pair, unlabelled on purpose: the same eight glyphs
    # twice, an equals between them. Double rule, not single — one rule under
    # a stacked pair reads as a fraction bar (rendered and looked at), and a
    # ratio is exactly the wrong figure for a claim of identity. PINE holds
    # the equality — the check.
    s.append(f'<text x="{R}" y="84" text-anchor="end" class="say mach" style="fill:{INK}">11E60398</text>')
    s.append(f'<rect x="626" y="94" width="104" height="1.6" fill="{PINE}"/>'
             f'<rect x="626" y="99" width="104" height="1.6" fill="{PINE}"/>')
    s.append(f'<text x="{R}" y="118" text-anchor="end" class="say mach" style="fill:{INK}">11E60398</text>')
    s.append(f'<text x="{R}" y="142" text-anchor="end" class="fine" style="fill:{PINE}">mine and the JDK’s — identical</text>')

    # ── the checksum bench: three bars on ONE scale, because this lane's
    # whole argument is the relative lengths. Three tones, three standings:
    # CLAY_G is mine, PINE is the reference that stands, INK2 a baseline.
    s.append(f'<text x="{L}" y="196" class="kick">ADLER-32 · GB/s</text>')
    BARX, BARW = 420, 310
    for k, (v, nm, mine, ref) in enumerate(((1.52, "scalar, pure Java", False, False),
                                            (4.26, "hand-vectorised", True, False),
                                            (14.06, "java.util.zip intrinsic", False, True))):
        y = 224 + k * 28
        w = BARW * v / VALS[-1]
        fill = PINE if ref else (a if mine else INK2)
        s.append(f'<text x="{L}" y="{y}" class="fine">{nm}</text>')
        s.append(f'<text x="400" y="{y}" text-anchor="end" class="key">{v:g}</text>')
        s.append(f'<g><rect x="{BARX}" y="{y-11}" width="{w:.1f}" height="14" fill="{fill}"/>'
                 f'<path class="bj{k}" d="M{BARX} {y-4}H{BARX+w:.1f}" stroke="{GROUND}" '
                 f'stroke-opacity="0.55" stroke-width="4" stroke-dasharray="2 4"/></g>')
        if mine:
            # CLAY text-grade — this is type, so 4.5 is its floor, not 3.0
            s.append(f'<text x="{BARX+w+12:.0f}" y="{y}" class="lbl" style="fill:{CLAY}">2.80×</text>')

    s.append(f'<text x="{L}" y="310" class="say" style="fill:{INK}">not beaten — the reference stands.</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── PLATE III
def plate_glyph() -> str:
    """The copybook. Room: a handwriting practice sheet.

    The authorship correction (round 20) now lives in the description and
    the README rather than in drawn runs: the network was COURSE-PROVIDED
    (after Nielsen); the optimisation is the work, with Shree Chaturvedi
    credited; the browser application is the author's own. The committed
    benchmarks answer "how much faster can you make code you didn't write?"
    both ways — 3.5x on the 256 dot kernel, 10.7x SLOWER on the small axpy —
    and round 28 moves the axpy inversion to the README alone: it is a
    caveat on the SPEED claim, and the speed claim is a kicker now, not the
    plate. The 3.5 still comes from the reference machine's 2026-08-02 runs
    (the 2026-08-10 sourcing correction stands; the December fanless record
    stays excluded).

    The net reads handwriting, so its 299 failures are drawn as failed
    homework: ruled baselines EDGE TO EDGE — round 28 bleeds the field to
    the sheet's own frame, the second full-bleed on the page (cadence's
    disclosure is the first; one full-bleed is a one-off, two is a system) —
    an accent margin line, every mark the true label of one missed image:
    the 220 merely wrong in grey ink, the 79 the net was SURE about in heavy
    accent, so the field's own accent count is the 79.

    The same round cuts everything that was not the field. The pen-drawn
    hero, kernel roll, build census, credits and both source captions were
    five stacked sections restating the README paragraph below the plate;
    what survives in type is one kicker (3.5x lives there now, at claim
    strength but not claim SIZE — the plate's claim is the field), the
    97.01% figure, and one sentence: 299 wrong — 79 of them sure. Three
    runs. The field is the plate.

    Motion: the caret carrier, kept exactly as round 26 reasoned it — a
    closed boustrophedon circuit of the clear bands, upright (offset-rotate
    0deg, NOT auto: auto inverts the mark's meaning every other row), the
    row ink lifting as it passes. The pen gesture went with the pen; the
    row-lifts are the glance now, and each recolours a whole row, far past
    the raster gate's burst floor.
    """
    H, a = 446, CLAY_G
    READ = 19.3                    # the caret's circuit clock
    ROWS_N, COLS, RP, SC = 8, 42, 32, 0.12
    Y0 = 190                       # first rail
    # 14.6, not (784-150)/COLS. The RAILS are the full bleed; the copy is not.
    # Every far-edge hop of the caret's circuit crosses the row between two
    # bands at XF=773, where its ink spans 765..776.5 (round 26's geometry
    # plus half its 3u stroke) — and at 15.095u pitch the terminal column's
    # ink ran to 781, so the climb struck the last glyph on every far hop.
    # Transient, but a strike-through is a strike-through. At 14.6 the widest
    # glyph (digit 4: 8.64u of ink, 1.32u of cap) ends at 760.5, 4.5u clear
    # of the climb — the copy stops at the copybook's own right margin, the
    # mirror of the 146 climb clearing column 0 on the left.
    PITCH = 14.6
    s = [head(H, "Glyph — borrowed code made 3.5x faster, same 97.01%",
              "Glyph: a course-provided C++ MNIST network, hand-optimised — 3.5 times "
              "faster on the committed dot benchmark, written with Shree Chaturvedi; the "
              "browser app is the author's own. Accuracy is unchanged at 97.01 percent, "
              "and the plate draws what unchanged cost: 299 wrong, every one an "
              "edge-to-edge page of the labels it missed, with the 79 it was most "
              "confident about drawn heavier and in the accent.",
              key="plate-1-glyph.svg",
              col=(150, 730), frame=(30, 0, 24), mono=False)]
    # ── the circuit, derived from the field's own geometry rather than pasted
    # as literals (the round-26 caret was "restored at its authored
    # coordinates" once already because a hand-typed path and a moved field
    # disagreed; deriving both from Y0/RP makes that disagreement impossible).
    # Up the margin band, then every clear band between the ink rows,
    # boustrophedon, closed — no wrap to hide, no reset to fade.
    bands = [Y0 + r * RP + 7.5 for r in range(ROWS_N)]
    XN, XF = 146, 773              # near and far ends of a band run
    seg = [f"M{XN} {bands[-1]:g}V{bands[0]:g}"]
    for r in range(ROWS_N):
        seg.append(f"H{XF if r % 2 == 0 else XN}")
        if r < ROWS_N - 1:
            seg.append(f"V{bands[r+1]:g}")
    CIRCUIT = "".join(seg)
    climb, band, hop = bands[-1] - bands[0], XF - XN, RP
    total = climb + ROWS_N * band + (ROWS_N - 1) * hop
    # the caret sits mid-field at frame zero: check 12 measures the render at
    # whatever instant the sampling loop left it near, and a carrier parked at
    # the field's extreme would move the plate's measured edge with it.
    DELAY = round(-0.46 * READ, 2)
    s.append(f""".car{{offset-path:path('{CIRCUIT}');
  offset-rotate:0deg;animation:car {READ}s linear infinite;animation-delay:{DELAY}s}}
@keyframes car{{from{{offset-distance:0%}}to{{offset-distance:100%}}}}
""")
    # the read: while the caret runs the band under row r, that row's grey ink
    # lifts to full — colour on the row group's `color`, the digits stroked
    # currentColor. Windows fall out of the circuit's own arithmetic.
    for r in range(ROWS_N):
        s0 = (climb + r * (band + hop)) / total * 100
        e0 = s0 + band / total * 100
        if r < ROWS_N - 1:
            s.append(f".rd{r}{{animation:rd{r} {READ}s linear infinite;animation-delay:{DELAY}s}}"
                     f"@keyframes rd{r}{{0%,{s0-1:.1f}%{{color:{INK2}}}{s0+1:.1f}%,{e0-1:.1f}%{{color:{INK}}}"
                     f"{e0+1:.1f}%,100%{{color:{INK2}}}}}")
        else:  # the last band ends exactly at the wrap, so it stays lit across it
            s.append(f".rd{r}{{animation:rd{r} {READ}s linear infinite;animation-delay:{DELAY}s}}"
                     f"@keyframes rd{r}{{0%{{color:{INK}}}1.5%,{s0-1:.1f}%{{color:{INK2}}}"
                     f"{s0+1:.1f}%,100%{{color:{INK}}}}}")
    s.append(f"</style>{ground(H)}")

    # ── the whole voice of the plate: a kicker carrying the speed claim, the
    # invariant at claim size, and the sentence the field performs
    s.append(f'<text x="{L}" y="40" class="kick">III · GLYPH — SOMEONE ELSE’S NET, 3.5× FASTER BY HAND</text>')
    s.append(f'<text x="{L}" y="112" class="hero">97.01<tspan class="unit" style="font-size:34px">%</tspan></text>')
    s.append(f'<text x="{L}" y="144" class="say">299 wrong — 79 of them sure.</text>')

    # ── the copybook field, FULL BLEED: rules frame edge to frame edge, the
    # margin line, the errors on their baselines. Each mark is the true label
    # of one missed image, from benchmarks/mnist_misclassified.csv; `conf`
    # comes from the same pinned CSV, so the 79 drawn heavy are the named 79.
    # Hue AND weight carry the split — currentColor 13 against accent 22 —
    # and the accent count on the field IS the 79.
    rails = [f'<path d="M86 {Y0 + r*RP}H794" stroke="{RULE}" stroke-width="1"/>'
             for r in range(ROWS_N)]
    rails.append(f'<rect x="134.5" y="170" width="1.5" height="252" fill="{a}"/>')
    s.append('<g>' + "".join(rails) + '</g>')
    _e = json.loads((ROOT / "errors.json").read_text())
    errs, conf = _e["true"], _e["conf"]
    rowg: list[list[str]] = [[] for _ in range(ROWS_N)]
    for i in range(len(errs)):
        r, c = i // COLS, i % COLS
        x, y = 150 + c * PITCH, (Y0 + r * RP) - 150 * SC
        stroke = (f'stroke="{a}" stroke-width="22"' if conf[i]
                  else 'stroke="currentColor" stroke-width="13"')
        rowg[r].append(f'<g {digit(DIGITS[errs[i]], x, y, SC, centre=PITCH - 2)}>'
                       f'<path d="{DIGITS[errs[i]]}" fill="none" {stroke} stroke-linecap="round"/></g>')
    for r in range(ROWS_N):
        s.append(f'<g class="rd{r}" style="color:{INK2}">' + "".join(rowg[r]) + '</g>')
    # the caret — shape, weight and clearances exactly as round 26 derived
    # them (closed so it reads as an object, stroke 3 so it stays out of the
    # hairline class, asymmetric so the margin climb clears column 0's ink)
    s.append(f'<g class="car"><path d="M-6.5 5L-2.25 -3.5L2 5Z" fill="{a}" '
             f'stroke="{a}" stroke-width="3" stroke-linecap="round" '
             f'stroke-linejoin="round"/></g>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── PLATE IV
def plate_automl() -> str:
    """The tool manifest. Room: a stores ledger — cut to the requisition line.

    Round 28, and this plate is the doctrine's proof: 23 runs and 1,821
    characters — the worst density on the page — become four runs and the
    strip. The round-24 redraw was right about the MARK (44 marks, 15
    filled, the bracketed set difference) and wrong to keep three stacked
    sections of type around it: the per-phase sets, the strikes, the
    container flags, the schema line and the licence are all in the README
    paragraph directly below, verbatim. What the prose cannot carry is the
    drawn set membership, so that is all the plate is now: the fraction at
    claim size, the registry as itself, and the one sentence that survived
    every audit. At 240u it is also the smallest sheet on the page, next to
    a 616u disclosure — the silhouette is the point.

    What it still deliberately does NOT draw: per-phase mark counts (the
    source audit's training-12 / onboarding-4 have no claims row, and this
    page does not draw unregistered numbers), and the schema/licence
    numerals, which now live only where the prose already carried them.

    The carrier is unchanged in kind: the 29 phase-tool outlines run
    (drawn pending rather than absent), inert — lighting no particular
    mark, encoding no count. Stroke and clock are heavier and faster than
    round 24's because the sheet is 2.4x smaller and the raster gate
    measures FRACTIONS of canvas: the same ink on a quarter the paper is
    the difference between a carrier and a stall.
    """
    H, a = 240, CLAY_G
    s = [head(H, "Agentic AutoML — one phase, one tool set",
              "Agentic AutoML takes a dataset and a sentence and returns a trained model, "
              "one MCP server over a LangGraph state machine. Its registry holds 44 tool "
              "definitions, drawn as 44 marks with the 15-tool base set filled and "
              "bracketed — no phase gets all 15, and a training-phase model cannot reach "
              "a preprocessing tool.",
              key="plate-6b-automl.svg", frame=(30, 64, 22), mono=False)]
    s.append(f""".mk{{stroke-dasharray:3 3;animation:mk 1.7s linear infinite}}
@keyframes mk{{from{{stroke-dashoffset:0}}to{{stroke-dashoffset:-6}}}}
</style>{ground(H)}""")

    s.append(f'<text x="{L}" y="40" class="kick">IV · AGENTIC AUTOML</text>')

    # ── the claim, then the registry that proves it drawable: the fraction
    # at claim size, 44 marks on one shelf, the base set filled and bracketed
    s.append(f'<text x="{L}" y="118" class="hero">15<tspan class="unit">/44</tspan></text>')
    s.append(f'<text x="{L}" y="146" class="lbl">IN THE BASE SET — NO PHASE GETS ALL 15</text>')

    P = (R - L - 8) / 43           # the shelf spans the full type column
    for i in range(44):
        x = L + i * P
        if i < 15:
            # the base set is HELD: it is the part that is always there
            s.append(f'<rect x="{x:.1f}" y="170" width="8" height="8" fill="{a}"/>')
        else:
            # the other 29 arrive only with a phase, so their outlines run
            s.append(f'<rect class="mk" x="{x:.1f}" y="170" width="8" height="8" fill="none" '
                     f'stroke="{WIRE}" stroke-width="1.6"/>')
    s.append(f'<path d="M{L} 186v4M{L} 190H{L + 14*P + 8:.1f}M{L + 14*P + 8:.1f} 190v-4" '
             f'fill="none" stroke="{WIRE}" stroke-width="1.2"/>')

    # the one sentence every audit of this section left standing
    s.append(f'<text x="{L}" y="214" class="fine">a training-phase model cannot reach a preprocessing tool</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── PLATE V
def plate_cadence() -> str:
    """The redacted disclosure. Room: a FOIA response — and the record now
    IS the plate. Section: CADENCE.

    Round 27 rebuilds this plate around the client's verdict ("too much text
    in every card for no reason"): the audit table's six service names, four
    column heads, the two-mark legend and both footnotes are cut — every one
    of them stands in the README prose directly below, verbatim — and the
    evidence they crowded is promoted to the full sheet. Six row-pairs run
    edge to edge, frame to frame: tenant A's records come back as hatched
    redaction bars, tenant B's as returned records with their stream
    running. Nothing labels them but the two tenants, because the drawing
    now states what the labels used to: half the disclosure withheld BY THE
    DATABASE, half returned.

    What survives in type is the exhibit's pivot and its moral: the one
    unfiltered query, run as B on purpose — the plate's only machine value,
    in the machine face; the response at the loudest size on the page (89px,
    and not a number); and the two-line thesis of the whole estate. Eight
    runs, down from twenty-four.

    Motion is unchanged doctrine, re-sited: the CARRIER is tenant B's
    record-lines streaming inside every returned row; the GESTURE is the
    re-strike — each redaction lifts faded, leaves its row blank for half a
    second (the void the database sent), then wipes back left-to-right in a
    tight cascade down the column. The door slamming, and staying shut.
    """
    H, LOOP, a = 616, 9.7, PINE    # the accent IS the check — the refusal
    s = [head(H, "Cadence — an unfiltered query, and the database that refuses",
              "Cadence, drawn as a redacted disclosure. Six row-pairs run edge "
              "to edge: tenant A's records come back as hatched redaction bars "
              "— withheld by PostgreSQL row-level security, not by the "
              "application — while tenant B's records return intact. Below, an "
              "unfiltered SELECT count(*) FROM tasks, run as B on purpose, "
              "comes back B only. The app didn't remember to filter; the "
              "database refused.", key="plate-5-refusal.svg",
              frame=(46, 0, 22))]
    # the re-strike: 0% is the finished frame (redacted), held for 84% of the
    # loop; the bar lifts FADED (no visible retraction — the row is simply
    # blank, which is what the database sent), then wipes back left-to-right.
    # Round 21's bars returned to full width from a visible retraction, so
    # the resting figure showed A and B identical — the opposite of the claim.
    s.append(f""".vast{{font-size:89px;letter-spacing:-2px;fill:{INK};font-weight:600;font-family:'S',Georgia,serif}}
/* tenant B's rows stream their record-lines: the plate's CARRIER, alive in
   every frame — 8u is one dash cycle, so the wrap is seamless. The auditor's
   scan stays deleted; gate.mjs check 3 fails a rule swept across type, and
   this plate no longer carries any type for one to cross. */
.bfl{{animation:bfl 1.7s linear infinite}}
@keyframes bfl{{from{{stroke-dashoffset:0}}to{{stroke-dashoffset:-8}}}}
.red{{transform-box:fill-box;transform-origin:left center;animation:red {LOOP}s {EASE} infinite}}
@keyframes red{{0%,84%{{opacity:1;transform:scaleX(1)}}85.5%{{opacity:0;transform:scaleX(1)}}
  86.5%{{opacity:0;transform:scaleX(.02)}}90.5%{{opacity:1;transform:scaleX(.02)}}
  95%,100%{{opacity:1;transform:scaleX(1)}}}}
</style>{ground(H)}""")

    s.append(f'<text x="{L}" y="{TOP}" class="kick">V · CADENCE — THE ISOLATION AUDIT</text>')
    s.append(f'<text x="258" y="92" text-anchor="middle" class="kick">TENANT A</text>')
    s.append(f'<text x="622" y="92" text-anchor="middle" class="kick">TENANT B</text>')

    # ── the disclosure, edge to edge: the redaction runs to the frame and
    # BECOMES the plate. Six pairs — one per audited service, drawn as
    # records rather than named, because the six names are in the prose one
    # scroll-line below and were the sameness the round exists to cut.
    for i in range(6):
        y = 112 + i * 42
        # A's records: withheld — there is nothing under the bar, because
        # the database never sent the row. The wipe cascades 60ms per row.
        s.append(redact_bar(86, y, 344, 26, cls="red",
                            extra=f' style="animation-delay:{round(i*0.06,2)}s"'))
        # B's records: the ones that return — record-lines inside, streaming
        s.append(f'<g><rect x="450" y="{y}" width="344" height="26" rx="2" fill="{ROW}" stroke="{a}" stroke-width="1.6"/>'
                 f'<path class="bfl" d="M458 {y+7}H786M458 {y+13}H786M458 {y+19}H786" '
                 f'stroke="{a}" stroke-width="1.5" stroke-dasharray="4 4"/></g>')

    # the records request, unfiltered on purpose
    s.append(f'<text x="{L}" y="404" class="say mach" style="fill:{INK}">SELECT count(*) FROM tasks</text>')
    s.append(f'<text x="510" y="404" class="fine">run as B — unfiltered on purpose</text>')
    # the response, at the largest type on the page — and it is not a number
    s.append(f'<text x="{L}" y="512" class="vast">B only</text>')
    s.append(f'<text x="{L}" y="560" class="say">The app didn’t remember to filter.</text>')
    s.append(f'<text x="{L}" y="588" class="say">The database refused.</text>')
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

    Round 28 strips the type back to the instrument's own callouts. The
    subtitle, the spine tab, the two cheapest-first captions, the
    below-the-gate caption, the ONNX/browser block and the source line all
    stand in the README paragraph below, verbatim; the drawing keeps its
    three screen labels, the pine gate figure and the human, because an
    unlabelled member is how round 22's speaker arc read as a rendering
    fault. The channel itself LIFTS 34u (one wrapper transform — its
    internal geometry is five interlocking keyframe systems and is not
    re-derived), and the verdict row moves into the reclaimed foot. One
    run there is non-negotiable and stays in the check's own pine: RULES
    LAYER ALONE — 0.979 must never read as the whole cascade's score.
    """
    H, a = 530, CLAY_G
    DY = 34                        # the channel's lift, one wrapper transform
    T1, T2, T3 = 8.6, 12.9, 15.5   # route periods — near-coprime, unfindable
    s = [head(H, "Applied — a classifier allowed to say it doesn't know",
              "Applied: a three-layer email classifier — 201 regex rules, then e5 "
              "embeddings, then a fine-tuned SetFit head, cheapest first — drawn as a "
              "tapered sifting channel. The one message no layer is sure of stops at the "
              "0.85 confidence gate across the channel's foot and is walked to a human "
              "instead of guessed at. It scores 0.979 macro-F1, 2 mistakes on a "
              "96-message evaluation set, measured with the rules layer alone.",
              key="plate-4-applied.svg", col=(150, 730), frame=(44, 64, 16),
              mono=False)]

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

    # ── the channel: one composed instrument — walls, screens, chute guides,
    # gate, stream and the human, in a single <g> so the stream may pass
    # through the screens (which is the diagram's whole point).
    ch = []
    # walls at 3u — a full weight above the 2u screens, because a wall is the
    # thing the stream cannot pass and the drawing should say so (round 21
    # called the 1-2u channel "the most timid drawing in the set")
    wx = lambda y: 320 + 70 * (y - 104) / 292
    # ── THE PORTS. Round 26. The openings were authored 198-220 and 274-296
    # while the chutes cross the wall at 198.0 and 283.6 — so the upper one let
    # its chute out at its TOP EDGE and the remaining 21 of its 22 units were
    # plain missing wall. That is what read as a broken wall: not the ratio of a
    # 22u opening to a 1u dotted line, which is fine, but 21u of opening with
    # nothing passing through it. The openings are DERIVED from the crossings
    # now, so a chute and its port cannot drift apart again.
    #
    # The crossings are the parameters at which P1 and P2 leave x > wx(y):
    # P1 exits at its own endpoint (342,198), and P2 at t≈0.985 of its last
    # cubic, y≈283.6. Authored rather than solved — a cubic/line intersection
    # in the generator would be more machinery than two numbers deserve — but
    # gate.mjs check 3 sees the result, and a port that missed its chute would
    # leave the token crossing 3u of wall.
    #
    # 22u is the port width and it is derived too: an 18u token plus 2u of
    # clearance each side, so a port is exactly as wide as the mail that leaves
    # through it, measured on the wall's own 13.5-degree rake.
    PORT_W, PORTS = 22, (198.0, 283.6)
    edges = [104]
    for c in PORTS:
        edges += [c - PORT_W / 2, c + PORT_W / 2]
    edges.append(396)
    ch.append('<path d="' + "".join(
        f'M{wx(y0):.1f} {y0:g}L{wx(y1):.1f} {y1:g}'
        for y0, y1 in zip(edges[0::2], edges[1::2]))
        + f'" stroke="{WIRE}" stroke-width="3"/>')
    ch.append(f'<path d="M560 104L{560 - 70 * 274 / 292:.1f} 378" stroke="{WIRE}" stroke-width="3"/>')
    # ── the jambs, and they are the whole of this round's correction to the
    # drawing. A member that simply STOPS reads as broken; an opening whose ends
    # turn outward reads as a machined port, which is the one convention that
    # separates an aperture from a fracture in any sectioned instrument. Six
    # units along the outward normal, at both ends of both ports and at the foot
    # of the right wall — the door the refused message leaves by, which until
    # now was also just a stroke that ran out. No member moved; five ends got a
    # lip, and the channel reads as one wall with two ports and a door.
    JAMB = 6.0
    _lw = (70 ** 2 + 292 ** 2) ** 0.5          # left wall, running down-right
    lnx, lny = -292 / _lw * JAMB, 70 / _lw * JAMB      # outward normal, to -x
    for y in edges[1:5]:
        ch.append(f'<path d="M{wx(y):.1f} {y:g}l{lnx:.1f} {lny:.1f}" '
                  f'stroke="{WIRE}" stroke-width="3" stroke-linecap="round"/>')
    _rw = (65.6849 ** 2 + 274 ** 2) ** 0.5     # right wall, running down-left
    ch.append(f'<path d="M{560 - 70 * 274 / 292:.1f} 378'
              f'l{274 / _rw * JAMB:.1f} {65.6849 / _rw * JAMB:.1f}" '
              f'stroke="{WIRE}" stroke-width="3" stroke-linecap="round"/>')
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
    # the whole instrument lifts as one object — every keyframe, offset-path
    # and rest declaration inside is relative to the same coordinates it was
    # tuned in, so nothing internal is re-derived
    s.append(f'<g transform="translate(0,-{DY})">' + "".join(ch) + '</g>')

    # the screen labels, right-aligned at the column edge: the rightmost ink
    # on this plate must be a declared coordinate, not a floating text width
    # (check 12's tolerance is 4u and a left-anchored run drifts more than
    # that between platforms)
    s.append(f'<text x="{R}" y="{168 - DY + 5}" text-anchor="end" class="key">201 REGEX RULES</text>')
    s.append(f'<text x="{R}" y="{244 - DY + 5}" text-anchor="end" class="key">e5 EMBEDDINGS</text>')
    s.append(f'<text x="{R}" y="{320 - DY + 5}" text-anchor="end" class="key">SETFIT HEAD</text>')
    s.append(f'<text x="{R}" y="{396 - DY + 7}" text-anchor="end" class="key" style="fill:{PINE}">0.85 GATE</text>')

    # the human's name, under the figure
    s.append(f'<text x="660" y="450" text-anchor="middle" class="lbl">A HUMAN</text>')

    # ── the verdict. 0.979 is the number with an artifact behind it,
    # labelled for what it measures; the cascade's 0.9583 has none — and the
    # pine run is the reason 0.979 can be drawn at claim size at all.
    s.append(f'<path d="M{L} 426H{R}" stroke="{RULE}"/>')
    s.append(f'<text x="{L}" y="500" class="hero">0.979</text>')
    # the qualifiers stand BESIDE the figure, not above it. At 55px the hero's
    # LAYOUT box climbs to ~446 — Fraunces carries deep vertical metrics, not
    # just its ink — so a 13px line at y=452 overlapped it in every frame
    # (gate check 2 reads boxes, and boxes are what line-height is made of;
    # the 104u foot cannot hold rule + label + a 68u em box with honest gaps).
    # Side by side the two share no column and cannot collide; the pine run
    # keeps the hero's own baseline, nearest the number it must qualify.
    s.append(f'<text x="330" y="478" class="lbl">MACRO-F1 · 96-MSG EVAL SET · 2 MISTAKES</text>')
    s.append(f'<text x="330" y="500" class="key" style="fill:{PINE}">RULES LAYER ALONE</text>')
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
    * THE SIGNATURES — round 28 deletes the calibration card, which restated
      the cone in words, and draws the haptic signature of each band INSIDE
      the scene, on the beam: one continuous bar under the stop band, three
      transient marks under the caution band, and under the silent band
      NOTHING — the absence the pine arc already declares. One policy verb
      per band (STOP / CAUTION / SILENT, lit by the walker's crossing, the
      read-chase re-sited from the dead table's numerals) and the two-line
      caption are all the type the policy needs; the slider finding, the
      inventory, the source path and the no-link close live in the README
      paragraph below, verbatim.

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

    """
    H, a = 388, CLAY_G
    T = 13.7                        # the approach's clock
    EX, EY = 238, 210               # the emitter — the phone's sensor
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
              "LiDAR depth becomes speech and haptics, drawn as the alert policy in "
              "front of the phone, to scale. At 0.5 metres the phone interrupts, a "
              "continuous haptic drawn as a solid bar on the beam; at 1.0 metres, a "
              "triple pulse, drawn as three marks; at 2.0 metres nothing fires at all, "
              "and the silence is deliberate — an aid that narrates every wall is an "
              "aid you switch off. An obstacle drawn approaching the phone trips each "
              "band in turn.",
              key="plate-8-visualassist.svg", col=(150, 730), frame=(30, 64, 24),
              bold=False, mono=False)]
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

    s.append(f'<text x="{L}" y="40" class="kick">VII · VISUALASSIST</text>')
    s.append(f'<text x="{R}" y="40" text-anchor="end" class="key">SWIFT · ARKIT · LIDAR</text>')

    # ── the scene: one composed instrument, so the walker may legitimately
    # cross the ticks, the arcs, the beam and the haptic signatures (the
    # applied channel's ruling).
    sc = []
    # the phone is an object in the world — INK; only the sensor is the act
    sc.append(f'<rect x="176" y="151" width="58" height="118" rx="9" fill="none" stroke="{INK}" stroke-width="2"/>')
    sc.append(f'<path d="M196 161H214" stroke="{INK}" stroke-width="1.5" stroke-linecap="round"/>')
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
    # ── the haptic signatures, drawn INSIDE the bands they describe — this
    # is what deleted the calibration card. One continuous bar under the stop
    # band, three transients under the caution band, and under the silent
    # band NOTHING: the pine arc is already the drawn absence, and a flatline
    # on top of the running beam would have been two datums on one axis.
    # 8u below the beam so the walker passes over the datum, not the marks.
    sc.append(f'<rect x="252" y="{EY+8}" width="78" height="9" rx="2" fill="{a}"/>')
    for k in range(3):
        sc.append(f'<rect x="{346 + k*30}" y="{EY+8}" width="18" height="9" rx="2" fill="{a}"/>')
    # the walker: the world approaching — INK, authored at the start
    sc.append(f'<circle class="obs" cx="{X0:g}" cy="{EY}" r="5.5" fill="{INK}"/>')
    # the outputs, AT the phone and labelled below it — round 22's speaker
    # arc was unlabelled and near-invisible, and read as an artifact
    sc.append(f'<path class="spk" d="M166 169A10 10 0 0 0 166 189" fill="none" '
              f'style="stroke:{WIRE}" stroke-width="2" stroke-linecap="round"/>')
    sc.append(f'<path class="spk" d="M159 160A19 19 0 0 0 159 198" fill="none" '
              f'style="stroke:{WIRE}" stroke-width="2" stroke-linecap="round"/>')
    for k, d in enumerate(("M168 227L156 233", "M170 239L157 245", "M168 251L156 257")):
        sc.append(f'<path class="vb{k}" d="{d}" fill="none" style="stroke:{WIRE}" '
                  f'stroke-width="2" stroke-linecap="round"/>')
    s.append('<g>' + "".join(sc) + '</g>')
    # the dimensions, read off the axis — the numbers ARE the policy
    for r, t in ((R05, "0.5 m"), (R10, "1.0 m"), (R20, "2.0 m")):
        s.append(f'<text x="{EX + r + 8:g}" y="246" class="key">{t}</text>')
    # one policy verb per band, centred in it, lit by the walker's crossing —
    # the read-chase the dead table's numerals used to carry. The silent verb
    # lights PINE (the check), the interrupting verbs CLAY (the act).
    for cx, cls, word in ((288, "rn0", "STOP"), (388, "rn1", "CAUTION"),
                          (538, "rn2", "SILENT")):
        s.append(f'<text x="{cx}" y="268" text-anchor="middle" class="key {cls}">{word}</text>')
    # left-anchored at the column edge, opening the caption stack the two fine
    # lines below continue. Centred it sat at x=205 — under the 58u phone —
    # but 152u of tracked caps centred on a 58u object put its left edge at
    # 129, 21u outside the column (check 5, every sample). Nothing that long
    # centres on the phone; anchored at L the outputs it names sit directly
    # above its first words and the three left edges align.
    s.append(f'<text x="{L}" y="300" class="kick">SPEECH + HAPTICS</text>')

    # the policy's one ruling, in words the prose below carries verbatim
    s.append(f'<text x="{L}" y="340" class="fine" style="fill:{INK}">the silence is deliberate —</text>')
    s.append(f'<text x="{L}" y="360" class="fine" style="fill:{INK3}">an aid that narrates every wall is an aid you switch off</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── FOOTER
def plate_colophon() -> str:
    """The imprint. Room: a printer's colophon, shrunk to a footer.

    Centered, like the title page it answers — the serif's bracket made
    spatial, closing where it opened. The six product marks turn as a
    printer's device inside a drifting ring: the page's quietest motion,
    the arc's landing. One line of mechanism under it; the README's own
    footer carries the contact.

    Round 27 takes the sheet out from under it. This was already the
    sparsest plate in the set and the one the client did not fault, so it
    becomes the second frontispiece: no ground, no frame, ink on GitHub's
    own canvas — the bracket the title page opens now closes on the same
    bare page it opened on. Nothing else moves; the ring, the counter-
    rotation and the halo stay exactly as authored (mutations.mjs probe 11
    anchors on those three literals, and they are the plate's carrier).
    """
    H, CX = 312, 440
    s = [head(H, "Colophon", "Colophon: every number on this page is re-derived in CI from a "
                             "pinned commit, except section one and the VisualAssist grant, "
                             "which are attested and say so. "
                             "The page itself is animated SVG with no JavaScript and no server. "
                             "If a number here is wrong, it is wrong in public.",
              key="plate-7-colophon.svg", col=(118, 762), frame=(46, 170, 25),
              serif=True, bold=False, mono=False, canvas=F1_CANVAS[THEME])]
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
</style>""")
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


def _motif(name: str) -> str:
    if name == "copybook":
        # MOVED OUT OF THE BOTTOM BAND. It was one rule at y=212 carrying 24
        # errors: 3.75u under the prose bbox and 12u off the canvas — neither
        # the 24u bottom margin its eight siblings hold nor a bleed, and the
        # in-between is what read as clipped.
        #
        # A bleed was not available. ground() draws this sheet's edge as an
        # OBJECT — rect 0.5,0.5,439,223 in WIRE — so ink run to the boundary
        # reads as ink hitting the paper's edge, not as a field continuing
        # past a crop. The desktop copybook is not bled either: M96..H784 on
        # an 880 canvas is full-COLUMN. And a 24u margin is arithmetically
        # closed here, because line2's bbox already ends at y=200.
        #
        # So the copybook becomes what the other seven motifs are — its
        # section's room as a monogram, in the zone the bench, the sieve and
        # the dial occupy, and which on this card was empty. Envelope 82..138,
        # inside the bench's warning that a motif reaching y=150 lands on the
        # body line at baseline 168 partway through the loop.
        #
        # Three rules AND the margin line. The vertical clay is what makes a
        # ruled sheet read as a copybook rather than as an underline; it is
        # the desktop field's own signature and the one element the bottom
        # strip never had.
        _e = json.loads((ROOT / "errors.json").read_text())
        sc, pitch = 0.065, 10.5
        out = [f'<rect x="308" y="82" width="1.5" height="56" fill="{CLAY_G}"/>']
        for r in range(3):
            y = 92 + r * 20
            out.append(f'<path d="M300 {y}H418" stroke="{RULE}" stroke-width="1"/>')
            for c in range(10):
                i = r * 10 + c
                d = DIGITS[_e["true"][i]]
                # The desktop field's ink logic at monogram scale: grey for
                # merely wrong, clay for the ones the net was sure of. Eight
                # of these thirty are sure, which is the pinned CSV's own
                # 79-in-299 rate — the sample carries the field's information,
                # not a decorative slice of it. Both strokes are heavier than
                # a straight scale of the desktop's 13/22, because a 9.75u
                # glyph still needs the 1u every hairline in this system
                # holds; below that the browser composites with the paper.
                ink_ = (f'stroke="{CLAY_G}" stroke-width="24"' if _e["conf"][i]
                        else f'stroke="{INK2}" stroke-width="15"')
                out.append(f'<g {digit(d, 314 + c * pitch, y - 150 * sc, sc, centre=pitch - 2)}>'
                           f'<path d="{d}" fill="none" {ink_} stroke-linecap="round"/></g>')
        return '<g>' + "".join(out) + '</g>'
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
        return (redact_bar(300, 84, 110, 12)
                + redact_bar(300, 104, 110, 12)
                + f'<rect x="300" y="124" width="110" height="12" rx="2" fill="{ROW}" stroke="{PINE}"/>')
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
                 layout: str = "left", motif: str = "", glide: float = 9.7,
                 frame: tuple[float, float, float] | None = None) -> str:
    h = 224
    if layout == "frontis":
        # ── F1 on the phone: the same ruling as the desktop pair — no sheet,
        # no frame, ink on GitHub's own canvas, graded against the declared
        # data-canvas (F1_CANVAS: the worst of the theme's real canvases).
        # The serif speaks the sentence; the dashed rule is the carrier (70u
        # is ten dash periods, so the wrap is seamless); and the only faces
        # aboard are the text face and the serif 400 it actually renders —
        # S600 would be dead payload here, and gate.mjs fails a declared
        # face nothing renders, so this stays honest without being remembered.
        fr = f' data-frame="{frame[0]:g},{frame[1]:g},{frame[2]:g}"' if frame else ''
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {MW} {h}" width="{MW}" height="{h}"{fr} '
            f'data-canvas="{F1_CANVAS[THEME]}" role="img" aria-label="{desc}">'
            f'<title>{kicker}</title><desc>{desc}</desc><style>'
            f"@font-face{{font-family:'T';font-weight:400;src:url(data:font/woff2;base64,{FONTTEXT}) format('woff2')}}"
            f"@font-face{{font-family:'S';font-weight:400;src:url(data:font/woff2;base64,{FONTSERIF}) format('woff2')}}"
            f"text{{font-family:'T',Georgia,serif}}"
            f".k{{font-size:13px;letter-spacing:2px;fill:{INK2}}}"
            f".ser{{font-family:'S',ui-serif,Georgia,serif;font-size:21px;fill:{INK}}}"
            f".gl{{animation:gl {glide}s linear infinite}}"
            f"@keyframes gl{{from{{stroke-dashoffset:0}}to{{stroke-dashoffset:-70}}}}"
            f"@media (prefers-reduced-motion: reduce){{*{{animation:none!important}}}}"
            f"</style>"
            f'<text x="220" y="40" text-anchor="middle" class="k">{kicker}</text>'
            f'<path class="gl" d="M150 68H290" style="stroke:{INK2}" stroke-width="1.5" stroke-dasharray="2 5"/>'
            f'<text x="220" y="112" text-anchor="middle" class="ser">{line1}</text>'
            f'<text x="220" y="142" text-anchor="middle" class="ser">{line2}</text>'
            f'<text x="220" y="194" text-anchor="middle" class="k">{hero}</text>'
            '</svg>')
    mid = layout == "center"
    ax = 'text-anchor="middle" ' if mid else ''
    tx = 220 if mid else 34
    hx, ha = (220, 'text-anchor="middle" ') if mid else ((406, 'text-anchor="end" ') if layout == "ledger" else (34, ''))
    rx, rw = (130, 180) if mid else (34, MW - 68)
    # This plate's DECLARED edges, same contract as head()'s: gate.mjs check 12
    # measures the render and the two must agree. plate_mobile writes its own
    # root rather than calling head(), which is the whole reason the mobile set
    # went ten rounds without one — the attribute had nowhere to be written.
    fr = f' data-frame="{frame[0]:g},{frame[1]:g},{frame[2]:g}"' if frame else ''
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {MW} {h}" width="{MW}" height="{h}"{fr} '
        f'role="img" aria-label="{desc}"><title>{kicker}</title><desc>{desc}</desc><style>'
        # both weights: .n is 600, and .u inherits it — see head()'s note on
        # why a synthesised bold is a per-platform rendering.
        # No 'M' here at all: the phone cards quote no machine artifact — they
        # are a kicker, a figure and two lines of statement — so mono has
        # nothing to mark on them and its payload would be dead weight in nine
        # files. gate.mjs fails a declared face nothing renders, so this stays
        # honest without anyone remembering it.
        f"@font-face{{font-family:'T';font-weight:400;src:url(data:font/woff2;base64,{FONTTEXT}) format('woff2')}}"
        f"@font-face{{font-family:'S';font-weight:600;src:url(data:font/woff2;base64,{SERIF600}) format('woff2')}}"
        f"text{{font-family:'T',Georgia,serif}}"
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
    # A unit that begins with a space cannot carry that space as a character:
    # XML collapses a leading space in a text node, so " only" set as a tspan
    # rendered the m-5 hero as "Bonly" and " m" glued m-8's to "0.5m". The gap
    # is geometry now — dx of one 600-weight serif space at 34px (~0.25 em).
    # Spacing that depends on a space character surviving XML whitespace
    # handling is spacing you have not actually specified.
    u, udx = unit, ''
    if u.startswith(' '):
        u, udx = u.lstrip(' '), ' dx="8.5"'
    parts.append(f'<text x="{hx}" y="{hero_y}" {ha}class="n">{hero}<tspan class="u"{udx}>{u}</tspan></text>')
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
 # The two frontispieces went transparent with their desktop twins in round
 # 27: hero-less, serif-spoken, no sheet. The "6 systems" hero went with the
 # card — a count of the page's own contents was the one number on the phone
 # that measured nothing — and its exemption goes in the same change.
 "m-0-thesis.svg": ("AYUSH YADAV · CINCINNATI, OH", "INK2",
   "OPEN TO FULL-TIME ROLES", "",
   "Systems, from SIMD kernels", "to the browser they run in.",
   "Ayush Yadav, a computer science graduate in Cincinnati, Ohio, open to "
   "full-time software engineering roles: systems, from SIMD kernels to the "
   "browser they run in.", "frontis", "", 8.1),
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
 "m-7-colophon.svg": ("COLOPHON", "RULE",
   "SVG · NO JAVASCRIPT · NO SERVER", "",
   "If a number here is wrong,", "it is wrong in public.",
   "Colophon: if a number here is wrong, it is wrong in public. This page "
   "is animated SVG with no JavaScript, no server and no external assets.",
   "frontis", "", 7.9),
}

# ─────────────────────────────────── the phone canvas declares its edges too
# (top, rightGap, bottomGap) in viewBox units on the 440x224 sheet, asserted
# by gate.mjs check 12 within tolerance 4. Kept as a separate block rather than
# an eleventh tuple field because that is what these are: nine decisions a
# reviewer can read in one place, which a value buried at the end of a ten-item
# tuple is not.
#
# Check 12 was guarded `if (!mobile)` from round 11 to round 21, so until now
# there was nothing for these to be. It found a defect on its first run: every
# card holds top 30 and bottom 24, and m-1-glyph held 12 — its copybook motif
# sat below both prose baselines, 3.75u under line 2 and 12u off the sheet
# edge, which is neither a margin nor a bleed. The motif moved into the zone
# its siblings use and the card now holds 24 like the rest.
#
# rightGap is the one column that legitimately varies, and it varies for a
# reason worth stating rather than averaging away:
#   · 90.5 / 110.8 — the two CENTERED cards (thesis, colophon). Centred text
#     leaves the right margin by construction; the gap is the layout, not slack.
#   · 13         — applied's sieve reaches x=427, past the 412 text column. A
#     graphic overhang into the margin, on purpose: the figure below the gate
#     is the point of the card. Text is still held to 412 by check 5.
#   · 16..34     — the left-layout cards, where a motif occupies the right.
MFRAME = {
 # The two frontis cards: rightGap is the centred kicker (m-0) or the centred
 # bottom line (m-7) — widths derived from the embedded fonts' own hmtx
 # advances (kicker 264.2u, "SVG · NO JAVASCRIPT · NO SERVER" 279.1u), and
 # bottomGap is the 13px caps line's em-box descent (194 + 3.45).
 "m-0-thesis.svg":      (30, 88, 26.5),
 "m-0b-work.svg":       (30, 34, 24),
 "m-1-glyph.svg":       (30, 21.5, 24),
 "m-2-jetpack.svg":     (30, 22, 24),
 "m-4-applied.svg":     (30, 13, 24),
 "m-5-refusal.svg":     (30, 30, 24),
 "m-6b-automl.svg":     (30, 16, 24),
 "m-7-colophon.svg":    (30, 80.5, 26.5),
 "m-8-visualassist.svg": (30, 34, 24),
}
if set(MFRAME) != set(MOBILE):
    raise SystemExit(f"MFRAME/MOBILE disagree: {set(MFRAME) ^ set(MOBILE)}")

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
            # `mach` is tested FIRST and wins over everything: it is the opt-in
            # that selects the mono face, so whatever else a run inherits, a
            # .mach run is set in 'M'. The final fallback is the TEXT face now,
            # not the mono one — that inversion is the whole redesign.
            #
            # What this branch CANNOT do, stated because the comment here used
            # to claim the opposite: it cannot catch those two arms being
            # swapped. TEXT_CHARS is MONO_CHARS — the same object, deliberately,
            # since the same strings are set in both faces — so exchanging them
            # changes the word in the message and nothing else. The distinctions
            # with teeth are 600 and serif. Nor does anything downstream close
            # it: gate.mjs asserts that whatever face an element RENDERS in is
            # embedded by that plate, which a wrongly-monospaced caption
            # satisfies, because 'M' is embedded. A run wearing the wrong class
            # is caught by reading it, not by a check.
            face, chars = (('mono', MONO_CHARS) if 'mach' in cls else
                           ('serif', SERIF_CHARS) if 'ser' in cls else
                           ('600', BOLD_CHARS) if cls & {'hero', 'sub', 'vast', 'n'} else
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
    for fn, gen in PLATES.items():
        set_paper(PAPER_OF[fn])       # each plate is printed on its own stock
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
        set_paper(PAPER_OF[_fn])      # the phone card is the same sheet
        _svg = plate_mobile(globals()[_acc], _k, _n, _u, _l1, _l2, _desc, _lay, _mo, _gl,
                            MFRAME[_fn])
        (_out / _fn).write_text(_svg)
        if _theme == "dark":
            _check_coverage(_fn, _svg)
    print(f"{_theme:5s} mobile set: {len(MOBILE)} plates at {MW}w")
set_theme("dark")

# ────────────────────────────────────────────────── alt/desc/README agreement
# Every description is authored once in ALT and must reach the README verbatim.
(OUT / "alt.json").write_text(json.dumps(ALT, indent=2, sort_keys=True))
_readme = ROOT.parent / "README.md"
# Fails CLOSED. This was `if _readme.exists():` and skipped in silence when it
# did not, so the one assertion that a screen reader hears the description the
# plate authored was conditional on a filename resolving. macOS is case-
# insensitive and the Linux runner is not: `Readme.md` passes here and asserts
# nothing on the machine that publishes. A check allowed not to run is not one.
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
    # Both directions, over all 36 published files. The loop above reads the
    # nine desktop-dark <img> tags; the other 27 references — every light twin
    # and the entire mobile set — arrive through <source srcset> and had no
    # assertion of any kind, which is the same coverage hole check 12 carried
    # for ten rounds. A plate authored and never referenced is a file no reader
    # can reach; a reference to a plate never authored is a broken image on the
    # page itself, and GitHub renders that as a torn icon, not as nothing.
    _want = {f"./assets/{_d}{_f}" for _f in set(PLATES) | set(MOBILE)
             for _d in ("", "light/")}
    # The trailing lookahead is load-bearing and was missing on the first
    # draft: without it `…/m-4-applied.svgX` still matches through `.svg`, so a
    # reference typo'd into a filename nothing publishes reads as present and
    # the check passes. Falsifying it is what found that.
    _have = set(_re.findall(r'\./assets/(?:light/)?[\w.-]+\.svg(?![\w.-])', _md))
    for _p in sorted(_want - _have):
        _fail.append(f"{_p}: this build authors it and README.md references it nowhere")
    for _p in sorted(_have - _want):
        _fail.append(f"{_p}: README.md references it and no build authors it — broken image")

if _fail:
    print("\nGATE FAILED:")
    for f in _fail:
        print(f"  · {f}")
    _sys.exit(1)
