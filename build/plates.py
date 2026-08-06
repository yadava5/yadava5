#!/usr/bin/env python3
"""
FALSIFIABLE — figure builder.

Every claim is followed by the mechanism that would catch it if it were a lie.

Design rules encoded here (each one is a finding, not a preference):
  * viewBox 880 wide, type column 150→730 — symmetric, 36% more legible at
    mobile than 1200
  * type scale 64 / 32 / 20 / 16 / 13, plus three named exceptions: the 34px
    serif (the only voice that is not the machine's — it opens the document on
    the thesis and closes it on the colophon, one bracket), the 26px .unit
    suffix that hangs off a hero, and plate III's 26px sentence specimen,
    which is set at the size a user would type.
  * NO SLAB, NO BORDER, NO ACCENT BAR. Round 19. The plates used to be opaque
    cards — slab fill, EDGE stroke, a 4u coloured bar at x=0 — and the client
    read them as cards and called them unrefined. He was right for a reason
    the build could not see: every other mark on this page earns its ink from
    data, and the bar was a coloured flag whose only job was "cards have a
    coloured edge now" — the one element the falsifiability conceit cannot
    defend. In the light theme the ten 600-step bars were the heaviest ink on
    the page: the eye went to the frame, not the content. So the figures are
    now transparent ink drawn directly on GitHub's own canvas (#0d1117 dark,
    #ffffff light — the set is still built twice and <picture> still picks),
    and what ties them into one document is what ties a printed report
    together: one repeated frontispiece rule with the chapter at its right
    end, and a shared type column. A document, not a deck.
  * every figure is exactly as tall as its evidence. The old set landed eight
    of ten plates inside a 130u height band, so the page had no way to say
    "this one matters" — the refusal weighed the same as a gzip benchmark.
    Heights now run ~330 to ~700: Cadence pays for one filed chip, not a week
    of empty calendar, and the refusal is the broadside.
  * STILL BY DEFAULT; motion only where it performs the claim it sits beside.
    The old doctrine was "never still", enforced by a raster gate demanding
    ~0.5% pixel change per sample — and it got what KPI-driven design always
    gets: seven plates grew travelling hairlines whose own comments admit they
    existed "to carry the raster gate", and four of them spent part of every
    loop striking through text (the colophon's crossed out the author's email).
    Five gestures survive because they ARE their claims: Glyph's pen draws the
    digits, jetpack's window is shown binding, Cadence files the chip, Applied
    walks one message to the human, AutoML's phase clock routes the tools.
    Everything else holds still, on purpose. motion.mjs and gate.mjs checks
    13/17 were re-authored in the same change — see the reasoning there.
  * near-coprime loop lengths so plates never beat into a synchronised pulse
  * the finished frame is authored; animation supplies the START, never the end
    (share cards and static renderers capture frame zero)
  * nothing comes to rest on top of a label. The gate samples 40 points
    across every loop and measures getBoundingClientRect, so this is enforced
    rather than hoped for.
  * long travels use cubic-bezier(.4,0,.2,1). The old expo-out covered 221u in
    a single 0.33s step — it read as a teleport, not as motion.
  * an element that MOVES fades out before its position resets, so the loop
    wrap is never a visible snap-back. Elements that only fade still reset in
    one frame; that is a blink, not a jump, and it is the cheaper trade.
  * no animated filters — one animated blur costs more than 4000 animated rects
"""
from __future__ import annotations
import base64, json, pathlib, re

# ── the grid, as constants rather than as eight independent judgement calls.
# Measured across the desktop set before this existed: first ink at 19, 23, 40
# and 56; rightmost ink 150, 164, 164.8 and 166 short of the canvas. So the
# document's right edge visibly wandered as you scrolled it, and its top margin
# had three values. L/R are the type column; TOP is the first baseline for a
# label row; HERO_GAP is the space between a 64px numeral and the label that
# explains it, which had been eyeballed at 8.2 on one plate and 23.1 on another.
L, R = 150, 730
TOP = 56
HERO_GAP = 16

# ── the canvas window.
# The type column is L..R = 580 units wide on an 880-unit canvas, so 34.1% of
# every plate was margin and ink covered 7.1% of the document. That 150 was
# chosen for one reason — legibility of a 16u label on a phone — and the phone
# is out of scope now, so the reason is gone and the emptiness is not.
#
# Rather than move several hundred coordinates, tighten the WINDOW: the viewBox
# starts at VB_X and is VB_W wide, so authored x=150 lands 64 from the left edge
# and authored x=730 lands 64 from the right. Every relative position, every
# travel distance and every collision is untouched.
#
# The second effect is the one that matters more. The plate scales to the width
# of GitHub's readme column either way, so a narrower canvas renders everything
# LARGER: a 16px label goes from ~17.8px to ~22px at a 980px column. The plates
# were not only empty, they were small.
VB_X, VB_W = 86, 708

# every plate's description is authored ONCE here and flows to three places:
# the SVG <desc>, the SVG aria-label, and the README's <img alt>. They diverged
# once already; the gate below now fails the build if the README drifts.
#
# Since <picture> allows exactly ONE alt for both the desktop and the mobile
# source, these strings describe the CLAIM rather than the picture — so the same
# sentence is true whichever image the browser actually chose.
ALT: dict[str, str] = {}

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT.parent / "assets"
OUT.mkdir(exist_ok=True)
FONT = base64.b64encode((ROOT / "mono-subset.woff2").read_bytes()).decode()

# The real product marks, extracted from each app's own logo and stripped to the
# mark alone — the card already sets the name in type, so the wordmark would say
# it twice, and the background tile would sit on a slab that is already the same
# near-black. Every stroke and fill is currentColor, so the card supplies the
# system's legend colour and the six marks read as one family rather than six
# pasted assets. Inlined, not linked: nothing external can load in this medium.
import re as _re_mod
_re_op = _re_mod.compile(r'(stroke|fill)-opacity="([0-9.]+)"')
LOGOS = json.loads((ROOT / "logos.json").read_text())


def logo(name: str, x: float, y: float, size: float, colour: str) -> str:
    """One product mark, drawn at `size` in `colour`.

    Tonal hierarchy inside a mark does not survive being shrunk to 28u. Two of
    the six carried stroke-opacity straight out of their source SVG — Cadence
    at 0.28 on three strokes, Applied at 0.65 on two — which rendered at 1.76:1
    and 5.02:1 on the dark slab and 1.49:1 and 2.68:1 on the light one, against
    a 3:1 floor. Both were invisible to gate.mjs until check 10 learned to read
    the sibling opacity properties, because they are neither `opacity` nor an
    rgba alpha.

    So the floor is enforced here rather than patched into logos.json: these
    marks are extracted from each app's own logo, and the next one extracted
    will carry whatever its designer chose too.
    """
    m = LOGOS[name]
    k = size / m["size"]
    body = _re_op.sub(
        lambda g: f'{g.group(1)}-opacity="{max(float(g.group(2)), 0.8):.2f}"', m["body"])
    return (f'<g transform="translate({x},{y}) scale({k:.4f})" '
            f'style="color:{colour}">{body}</g>')

W = 880

# ── the two palettes. The figures are transparent, so the ground they are
# measured against is GitHub's own canvas: #0d1117 dark, #ffffff light. That
# is a REAL change of ground, not a renaming — the old dark slab was #0A0A0B
# and the old light slab #F6F7F8, and two greys that cleared their floors on
# those slabs fail on these: dark RULE #5A606A measured 2.99:1 on #0d1117
# (floor 3:1) and dark INK3 #767B84 measured 4.45:1 (text floor 4.5:1). Both
# are re-derived below; every value in this table was recomputed against its
# own canvas in this round, never carried over on the assumption that a
# near-black is a near-black.
#
# GROUND is written into each SVG as a full-size rect at fill-opacity 0: it
# paints nothing, and it is the reference gate.mjs check 10 reads its slab
# colour from, so every contrast in the pipeline is measured against the
# canvas the figure actually ships on.
#
# The six accents are the same six identities in both palettes — dark at
# roughly the 400 step of each family, light at the 600–700 step, because
# #F5A524 on white is under 2:1: an accent you cannot see. All six light
# accents clear the 4.5:1 TEXT floor, not just the 3:1 non-text one, because
# four of them are drawn as labels; an accent legible as a bar but illegible
# as a word would split one identity into two colours.
THEMES = {
    "dark": dict(
        GROUND="#0d1117",   # GitHub's dark canvas — the ground under the ink
        RULE="#5D636D",     # 3.13:1 — section rules (was #5A606A: 2.99 here)
        WIRE="#6E737C",     # 3.86:1 — connectors, boundaries, brackets, frames
        ROW="#5D636D",      # 3.13:1 — tenant row fills
        INK="#F7F8F8", INK2="#8A8F98", INK3="#7A7F88",  # 17.79 / 5.82 / 4.70:1
        AMBER="#F5A524", LIME="#B8E62E", EMERALD="#34D399",   # 9.27/12.97/9.84
        CYAN="#22D3EE", PINK="#F472B6", INDIGO="#818CF8",     # 10.47/7.15/6.34
        CHIP="#0E2A22",     # the filed event's fill, a tint of the accent —
                            # 1.24:1 on its own; its accent stroke carries it
    ),
    "light": dict(
        GROUND="#ffffff",   # GitHub's default canvas — ink on the page itself
        RULE="#848A93",     # 3.48:1
        WIRE="#737981",     # 4.39:1
        ROW="#848A93",      # 3.48:1
        INK="#1A1D21", INK2="#555B63", INK3="#6B7178",  # 16.91 / 6.86 / 4.93:1
        AMBER="#B45309",    # 5.02:1 — Glyph
        LIME="#4D7C0F",     # 4.99:1 — jetpack
        EMERALD="#047857",  # 5.48:1 — Cadence
        CYAN="#0E7490",     # 5.36:1 — Applied
        PINK="#BE185D",     # 6.04:1 — LifeQuest
        INDIGO="#4F46E5",   # 6.29:1 — AutoML
        CHIP="#DEF2E8",
    ),
}

THEME = "dark"


def set_theme(name: str) -> None:
    """Point every colour global at one palette.

    The plate functions read these globals at call time, so the same code
    draws both documents — the light set is the same document in a different
    light, not a second design.
    """
    globals().update(THEMES[name])
    globals()["THEME"] = name
    # one colour per system, in the order the README presents them
    t = THEMES[name]
    globals()["LEGEND"] = [
        ("GLYPH", t["AMBER"]), ("JETPACK", t["LIME"]), ("CADENCE", t["EMERALD"]),
        ("APPLIED", t["CYAN"]), ("LIFEQUEST", t["PINK"]), ("AUTOML", t["INDIGO"]),
    ]


set_theme("dark")


def op(v: float) -> float:
    """Translucent-accent opacity, per theme.

    The raw values are tuned against the dark canvas, where alpha is cheap:
    lime at .5 over #0d1117 still measures 3.99:1. The same .5 over white is
    under 2.1:1 — compositing toward white destroys chroma contrast far
    faster than compositing toward black, and no accent dark enough to
    survive .5 on white exists. So light lifts every alpha through
    0.6 + 0.4v: the tuned ordering is preserved. Re-measured this round
    against the new grounds for every surviving translucent use — the two
    weakest are Glyph's .wrong grid marks (amber, .72 → 5.27:1 dark, .89 →
    4.15:1 light) and Cadence's filing lead (emerald, .7 → 5.31:1 dark,
    .88 → 4.37:1 light); the solid uses never had alpha.
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

# ── the pen, normalised.
# Every DIGITS path is authored inside a nominal 120x160 box, but the INK inside
# that box is a different width for every glyph: "1" spans x 38..64 and "4"
# spans 28..100. Drawing them all at translate(x,y) therefore left the 299-error
# grid with mark widths from 1.77u to 4.90u and gaps from 6.40u to 9.23u in a
# nominal 11.4u cell — a 44% jitter, which is the visible raggedness — and hung
# the hero "7" 34.5u to the right of the 150 column it was supposed to sit on.
#
# The fix is NOT to equalise widths: stretching "1" to the width of "0" would
# distort the letterforms. It is to measure each glyph's ink and place it
# deliberately — flush left for the hero, centred in its cell for the grid.
# Every command in DIGITS takes coordinate PAIRS (M, L, C, Z), so the even-index
# numbers are the x values.
def ink(d: str) -> tuple[float, float]:
    n = [float(v) for v in re.findall(r'-?\d+\.?\d*', d)]
    xs = n[0::2]
    return min(xs), max(xs)


def digit(d: str, x: float, y: float, scale: float, *, centre: float | None = None) -> str:
    """Place a glyph so its INK lands where you asked, not its bounding box."""
    x0, x1 = ink(d)
    dx = x - x0 * scale if centre is None else x + (centre - (x1 - x0) * scale) / 2 - x0 * scale
    return f'transform="translate({dx:.2f},{y:.2f}) scale({scale})"'


def frontis(numeral: str, name: str, claim: str) -> str:
    """The frontispiece: every figure opens the same way, like a chapter.

    One 16px claim at the left edge of the column, the chapter rail at the
    right, one hairline rule under both. This is the entire shared chrome of
    the document now that the slab is gone — the repeated device that makes
    ten transparent figures read as one numbered report — and it is also the
    fix for two audit findings at once: the CLAIM armature used to be an 11px
    kicker applied to some plates and not others (subliminal where it existed,
    conspicuous where it was forgotten), and the first ink used to start at
    three different heights. Now every figure's first ink is the same class at
    the same y, which is what check 12 enforces.
    """
    return (f'<text x="{L}" y="{TOP}" class="lbl">{claim}</text>'
            f'<text x="{R}" y="{TOP}" class="lbl" text-anchor="end">'
            f'<tspan fill="{INK}">{numeral}</tspan>  {name}</text>'
            f'<path d="M{L} 70H{R}" stroke="{WIRE}"/>')


EASE = "cubic-bezier(.4,0,.2,1)"
# EASE is ease-IN-out: it accelerates first, then settles. That is right for a
# thing travelling somewhere, and wrong for a thing being STOPPED — plate V's
# comment claimed its query "decelerates into the boundary" while easing into it
# like a lift arriving. A refusal needs an arrest: nearly all the deceleration
# in the last fifth of the travel.
ARREST = "cubic-bezier(.05,.75,.1,1)"

# One curve did every job. A census of the 21 animation classes found
# cubic-bezier(.4,0,.2,1) on 16 of them — arrivals, impacts and ambient pulses
# all on the same symmetric ease-in-out — which is why the document had one
# gesture performed eight times. Motion carries meaning here or it is
# decoration, and three verbs need three curves.
ARRIVE  = "cubic-bezier(.16,1,.3,1)"      # expo-out: fast away, long settle
IMPACT  = "cubic-bezier(.34,1.56,.64,1)"  # overshoots slightly, then sets
BREATHE = "cubic-bezier(.37,0,.63,1)"     # symmetric sine, for ambient loops


def head(h: int, title: str, desc: str, key: str = "") -> str:
    if key:
        # The light pass re-authors the same key. The two themes are one
        # document, so a plate and its light twin must carry byte-identical
        # descriptions — asserted, not assumed, because a colour name drifting
        # into a desc would silently fork the accessible text per theme.
        if key in ALT and ALT[key] != desc:
            raise SystemExit(f"{key}: description diverged between themes")
        ALT[key] = desc
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="{VB_X} 0 {VB_W} {h}" width="{VB_W}" height="{h}" role="img" aria-label="{desc}">
<title>{title}</title><desc>{desc}</desc>
<style>
@font-face{{font-family:'M';src:url(data:font/woff2;base64,{FONT}) format('woff2')}}
text{{font-family:'M',ui-monospace,SFMono-Regular,Menlo,monospace}}
.hero{{font-size:64px;letter-spacing:-1.5px;fill:{INK};font-weight:600}}
.sub{{font-size:32px;letter-spacing:-0.5px;fill:{INK};font-weight:600}}
.unit{{font-size:26px;fill:{INK2}}}
.say{{font-size:20px;fill:{INK2}}}
.lbl{{font-size:16px;letter-spacing:1.6px;fill:{INK2}}}
.key{{font-size:16px;letter-spacing:1.6px;fill:{INK}}}
.fine{{font-size:13px;letter-spacing:0.6px;fill:{INK2}}}
.kick{{font-size:11px;letter-spacing:2.6px;fill:{INK3}}}
@media (prefers-reduced-motion: reduce){{*{{animation:none!important}}}}
"""


def ground(h: int) -> str:
    # The invisible ground. fill-opacity 0, so it paints nothing and the
    # figure is transparent ink on GitHub's own canvas — but the rect still
    # CARRIES the canvas colour, because gate.mjs check 10 reads its contrast
    # ground off the plate's first <rect>. Removing it would not make the
    # gate lenient; it would make it measure against nothing.
    return f'<rect x="{VB_X}" width="{VB_W}" height="{h}" fill="{GROUND}" fill-opacity="0"/>'


# ────────────────────────────────────────────────────────────── PLATE 0
def plate_thesis() -> str:
    """Identity and contact sheet.

    This plate used to open with a thesis about falsifiability and a colour
    legend. It was the most distinctive thing on the page and the wrong thing to
    lead with: a reader met a sentence about numbers catching lies before
    learning what any of this is. The proof is the payoff, not the premise, so
    it moved to the colophon and this became the answer to "who is this and what
    have they built" — legible in about eight seconds, after which everything
    below is optional depth.

    STILL, deliberately. This is the eight-second first impression, and the
    old version spent it with an index cursor drifting through the contact
    sheet and the six logos bobbing on a stagger — both of which existed, by
    their own comments' admission, to carry the raster gate. A title page that
    fidgets reads as a banner ad; a title page that holds still reads as a
    document that is sure of itself. The motion doctrine inverted this round
    (see the header), so the first plate gets to be the stillest.
    """
    H = 640   # last caption baseline at H-30, like every figure in the set
    # what he actually works in, grouped so it can be scanned rather than read.
    # The description below is GENERATED from this table rather than authored
    # beside it. It used to be authored, and it drifted: it named SQL and
    # fuzzing, neither of which this plate has ever drawn. Nothing could catch
    # that — plates.py asserts the README alt equals ALT[fn] and the dark desc
    # equals the light desc, both of which compare copies of one string to each
    # other; gate.mjs check 9 compares the desc's NUMBERS to the drawing and
    # never its words. So the accessible copy could say anything at all and
    # still be "in agreement". Now the two cannot disagree.
    SKILLS = [
        ("LANGUAGES", "Languages",              "C++ · TypeScript · Python · Java · Swift · Rust"),
        ("SYSTEMS",   "systems work in",        "SIMD AVX-512 · Vector API · WebAssembly · OpenMP"),
        ("ML",        "machine learning with",  "LangGraph · MCP · in-browser ONNX · SetFit"),
        ("WEB",       "web and backend in",     "React · Next.js · Tauri · SwiftUI · FastAPI · NestJS"),
        ("INFRA",     "infrastructure on",      "GitHub Actions · Docker · Postgres · CodeQL"),
    ]

    def _prose(items: str) -> str:
        parts = [p.strip() for p in items.split("·")]
        return ", ".join(parts[:-1]) + " and " + parts[-1]

    _bands = "; ".join(f"{lead} {_prose(items)}" for _, lead, items in SKILLS)
    s = [head(H, "Ayush Yadav — computer science graduate, Cincinnati OH",
              "Ayush Yadav, a computer science graduate in Cincinnati, Ohio, open to full-time "
              f"engineering roles. {_bands}. Below, the six "
              "systems this page documents: Glyph, jetpack, Cadence, Applied, LifeQuest and "
              "Agentic AutoML.", key="plate-0-thesis.svg")]
    s.append(f""".ser{{font-family:ui-serif,Georgia,'Times New Roman',serif;font-size:34px;fill:{INK}}}
</style>{ground(H)}""")

    # the title page carries its own frontispiece: the author where the claim
    # goes, the degree where the chapter goes — same y, same rule, so the
    # document's opening line is the same line every chapter repeats
    s.append(f'<text x="{L}" y="{TOP}" class="key" style="letter-spacing:5px">AYUSH YADAV</text>')
    s.append(f'<text x="{R}" y="{TOP}" class="lbl" text-anchor="end">CS GRADUATE · CINCINNATI, OH</text>')
    s.append(f'<path d="M{L} 70H{R}" stroke="{WIRE}"/>')

    # the one serif voice in the document, saying what the work IS. The
    # colophon answers it in the same voice — one bracket, opened and closed.
    for i, ln in enumerate(["Systems, from SIMD kernels", "to the browser they run in."]):
        s.append(f'<text x="{L}" y="{124 + i*42}" class="ser">{ln}</text>')
    s.append(f'<text x="{L}" y="204" class="fine">Open to full-time software engineering roles · aesh.03.23@gmail.com</text>')

    for i, (dom, _lead, items) in enumerate(SKILLS):
        y = 244 + i * 24
        s.append(f'<text x="{L}" y="{y}" class="kick">{dom}</text>')
        s.append(f'<text x="262" y="{y}" class="fine">{items}</text>')

    # the contact sheet: every system on the page, at a glance. This is the
    # only place the six hues appear together — the legend, taught once. The
    # three caption lines used to sit 16u apart with one grey step between
    # them and merged at a glance; 18/20u of leading and the stack line one
    # step dimmer give the sheet the same anatomy as a typeset caption.
    s.append(f'<path d="M{L} 380H{R}" stroke="{RULE}"/>')
    CARDS = [
        ("GLYPH",     "A neural net in C++",   "C++ · SIMD · WASM"),
        ("JETPACK",   "Parallel gzip",         "Java · Vector API"),
        ("CADENCE",   "NL calendar + tasks",   "TS · Postgres"),
        ("APPLIED",   "Inbox → job pipeline",  "Python · ONNX"),
        ("LIFEQUEST", "Routines as quests",    "Tauri · NestJS"),
        ("AUTOML",    "Dataset → model",       "LangGraph · Docker"),
    ]
    for i, (nm, what, stack) in enumerate(CARDS):
        col, row = i % 3, i // 3
        x, y = L + col * 197, 408 + row * 112
        c = LEGEND[i][1]
        s.append(logo(nm, x, y, 28, c))
        s.append(f'<text x="{x}" y="{y+52}" class="key">{nm}</text>')
        s.append(f'<text x="{x}" y="{y+72}" class="fine">{what}</text>')
        s.append(f'<text x="{x}" y="{y+90}" class="fine" style="fill:{INK3}">{stack}</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────── PLATE I — WORK
def plate_work() -> str:
    """A year of paid engineering, and a national competition.

    Neither appears in any repository a reader can clone — the Oracle logs, the
    Tableau inventory and the compliance dashboard belong to Miami University,
    and the DataFest data is a competition set. Every other number on this page
    is re-derived in CI from a pinned commit; these are the author's word, and
    the plate says so on its face rather than borrowing the warrant of the ones
    that are checked.
    """
    H = 584
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
              "from a public repository.", key="plate-0b-work.svg")]
    s.append(f"</style>{ground(H)}")

    s.append(frontis("I", "WORK", "A YEAR OF PAID WORK — NOT IN ANY REPO"))
    s.append(f'<text x="{L}" y="98" class="kick">ITSM DATA INTEGRATION INTERN · MIAMI UNIVERSITY</text>')
    s.append(f'<text x="{L}" y="118" class="fine">Jun 2025 – May 2026</text>')

    # ── THE BARS, third attempt, and the postmortem the first two earned.
    # Attempt one drew every fill at the full track width — 100% under a label
    # reading 96.72%. Attempt two fixed the widths and filled the naive bar in
    # RULE on a track that was also RULE: 1.00:1, computed, both themes — an
    # invisible fill, so the bar read as 100% under a label saying 32%. Same
    # wrong picture, new cause, on the page whose whole argument is that the
    # drawn number is the measured number.
    #
    # The fix is architectural, not another colour swap: the track is now a
    # HOLLOW frame (WIRE stroke, no fill) and every fill is solid INK2, so
    # fill-against-track can never again be a pair of similar greys — it is
    # ink against empty canvas, 5.82:1 dark and 6.86:1 light, measured. And
    # every width below is 300*frac from the value beside it, never a number
    # typed by eye.
    ROWS = [
        ("57.8M",  "ROW FIELD-USAGE TABLE",     "from 1.6M Oracle Analytics query logs, 5 years"),
        ("96.72%", "CODE COMPLIANCE ACROSS 61 PROJECTS", "from 0 — a legacy Laravel reporter, refactored"),
        ("10,453", "ROW MASTER ASSET INVENTORY","Tableau and Workday consolidated, hash-deduped"),
    ]
    for i, (num, lab, det) in enumerate(ROWS):
        y = [160, 216, 292][i]
        s.append(f'<text x="{L}" y="{y}" class="sub">{num}</text>')
        s.append(f'<text x="330" y="{y-8}" class="lbl">{lab}</text>')
        s.append(f'<text x="330" y="{y+12}" class="fine">{det}</text>')
    s.append(f'<g><rect x="330" y="232" width="300" height="14" fill="none" stroke="{WIRE}"/>'
             f'<rect x="330" y="232" width="{300*0.9672:.2f}" height="14" fill="{INK2}"/></g>')

    s.append(f'<path d="M{L} 336H{R}" stroke="{RULE}"/>')
    s.append(f'<text x="{L}" y="368" class="kick">DATAFEST 2026 · TEAM LEAD, 3-PERSON, NATIONAL ASA COMPETITION</text>')
    s.append(f'<text x="{L}" y="414" class="sub">0.90</text>')
    s.append(f'<text x="330" y="406" class="lbl">HOLDOUT AUC</text>')
    s.append(f'<text x="330" y="426" class="fine">90-day care utilisation for 349K patients</text>')
    # the linkage claim is a comparison, so draw the comparison — and after two
    # rounds of this pair lying, the comparison is carried by LENGTH alone:
    # both fills the same ink, both tracks the same hollow frame, 298.8 against
    # 96. Two bars that differ only in the measured quantity cannot smuggle a
    # colour bug back in.
    s.append(f'<text x="{L}" y="478" class="sub">99.6%</text>')
    s.append(f'<text x="330" y="462" class="lbl">OF LINKAGE PRESERVED</text>')
    for j, (frac, tag) in enumerate([(0.996, "star"), (0.32, "32% naive")]):
        yy = 470 + j * 20
        s.append(f'<g><rect x="330" y="{yy}" width="300" height="12" fill="none" stroke="{WIRE}"/>'
                 f'<rect x="330" y="{yy}" width="{300*frac:.2f}" height="12" fill="{INK2}"/></g>')
        s.append(f'<text x="642" y="{yy+11}" class="fine">{tag}</text>')
    s.append(f'<text x="330" y="526" class="fine">7.7M encounters · DuckDB + Polars star schema</text>')

    s.append(f'<text x="{L}" y="{H-30}" class="fine" style="fill:{INK3}">ATTESTED — not derivable from a public repo</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── PLATE I
def plate_glyph() -> str:
    H, LOOP, SET, a = 596, 9.1, 7.6, AMBER
    s = [head(H, "Glyph — 97.01%, and the 299 it gets wrong",
              "Glyph: a neural network written from scratch in C++ with hand-written AVX-512, "
              "AVX2 and NEON kernels, plus an autovectorised WebAssembly build. It scores 97.01 "
              "percent on the 10,000-image MNIST test set, which means 299 wrong — every one of "
              "them drawn as a grid of the labels it missed. The 79 it was most confident about "
              "are drawn in a heavier stroke than the rest.", key="plate-1-glyph.svg")]
    # Two gestures, both of them the claim. The pen draws the hero 299 — a net
    # "written from scratch, by hand" introduced by handwriting — and the four
    # ISA tokens arrive at the collector. The read head that used to pass over
    # the error grid all loop long is gone: it was the raster gate's element,
    # not the argument's, and the grid is stronger as a still exhibit.
    s.append(f""".ink{{fill:none;stroke:{a};stroke-width:7;stroke-linecap:round;stroke-linejoin:round;
  stroke-dasharray:1;stroke-dashoffset:0;animation:draw {LOOP}s linear infinite;animation-delay:{-SET}s}}
/* 4%, not the old 17%: at 17% the pen laid ~190u² of new ink per 100ms sample,
   under the ~660u² perceptual floor — a draw-on nobody could see drawing, and
   measured at exactly the gate's minimum. At 4% (~0.4s a glyph, strokes
   overlapping down the 150ms stagger) each sample lays visible ink, and the
   gesture reads as what the claim says: a pen stroke, by hand. */
@keyframes draw{{0%{{stroke-dashoffset:1}}4%{{stroke-dashoffset:0}}100%{{stroke-dashoffset:0}}}}
.tok{{animation:run {LOOP}s {ARRIVE} infinite}}
@keyframes run{{0%{{opacity:0;transform:translateX(-190px)}}5%{{opacity:1;transform:translateX(-190px)}}
  34%,96%{{opacity:1;transform:translateX(0)}}100%{{opacity:0;transform:translateX(0)}}}}
.wrong{{opacity:{op(0.72)}}}
.sure{{opacity:1}}
</style>{ground(H)}""")

    s.append(frontis("II", "GLYPH", "THE 299 IT GETS WRONG — ALL OF THEM"))
    # 0.68 keeps the three glyphs clear of the mechanism column at x=330;
    # they end at 306. Each is placed by its own ink, not its nominal box.
    hx = 150
    for j, d in enumerate([DIGITS[2], DIGITS[9], DIGITS[9]]):
        s.append(f'<g {digit(d, hx, 100, 0.68)}>'
                 f'<path class="ink" d="{d}" pathLength="1" '
                 f'style="animation-delay:{round(-SET + j*0.15,3)}s"/></g>')
        x0, x1 = ink(d)
        hx += (x1 - x0) * 0.68 + 12

    # MECHANISM — four instruction sets, one compiled path
    s.append(f'<text x="330" y="104" class="kick">3 KERNELS BY HAND, 1 AUTO</text>')
    for i, name in enumerate(["AVX-512", "AVX2", "NEON", "wasm (auto)"]):
        y = 128 + i * 34
        s.append(f'<text x="330" y="{y+5}" class="key">{name}</text>')
        s.append(f'<path d="M470 {y}H660" stroke="{WIRE}" stroke-width="1"/>')
        # A 4u ring with a 2.2/2 dash renders as roughly six disconnected dots
        # at 1:1 — it read as a broken glyph, not as "autovectorised". Hollow
        # against three filled is the same distinction and survives the scale.
        hand = i < 3
        s.append(f'<circle class="tok" data-rest="one-answer" data-rest-within="2" '
                 f'cx="660" cy="{y}" r="4" '
                 + (f'fill="{a}" ' if hand else f'fill="none" stroke="{a}" stroke-width="1.8" ')
                 + f'style="animation-delay:{round(-SET + i*0.12,3)}s"/>')
    # four instruction sets, one answer — so all four tokens must actually
    # arrive at the collector, not merely set off in its direction
    s.append(f'<path id="one-answer" d="M660 124V234" stroke="{WIRE}" stroke-width="1"/>')
    # It says "1 PATH COMPILED", not "1 ANSWER" — nothing in the repo tests
    # that the four builds agree, and the README says so itself ("nothing
    # cross-checks them"). The plate must not make the stronger claim the
    # prose declines to.
    s.append(f'<text x="330" y="264" class="lbl">4 BUILDS · 1 PATH COMPILED</text>')

    # VERDICT — the hero clears the rule by 16u; at 64px its box runs from
    # baseline-64 to baseline+19, which is 84u tall, not the 60 I first assumed.
    s.append(f'<path d="M150 300H730" stroke="{RULE}"/>')
    s.append(f'<text x="150" y="384" class="hero">97.01<tspan class="unit">%</tspan></text>')
    s.append(f'<text x="470" y="384" class="lbl">MNIST TEST · n=10,000</text>')
    s.append(f'<text x="150" y="428" class="say">299 wrong. The 79 it was sure of are bold.</text>')

    # THE EXHIBIT — the REAL errors, still. Each mark is the true label of one
    # image the model got wrong, read from benchmarks/mnist_misclassified.csv
    # in the Glyph repo, so the picture IS the evidence. 50 per row leaves 49
    # in the last of six rows — the honest ragged end of a list. `conf` comes
    # from the same column of the same pinned CSV that glyph.confident_errors
    # derives from, so the 79 drawn heavy and the 79 named above are the same
    # 79. The rows no longer bob and no head passes over them: evidence in a
    # display case, not on a conveyor.
    _e = json.loads((ROOT / "errors.json").read_text())
    errs, conf = _e["true"], _e["conf"]
    gx, gy, cols = 150, 460, 50
    for r in range((len(errs) + cols - 1) // cols):
        for i in range(r * cols, min((r + 1) * cols, len(errs))):
            x, y = gx + (i % cols) * 11.4, gy + r * 14.0
            sure = conf[i]
            s.append(f'<g class="{"sure" if sure else "wrong"}" {digit(DIGITS[errs[i]], x, y, 0.068, centre=10.4)}>'
                     f'<path d="{DIGITS[errs[i]]}" fill="none" stroke="{a}" '
                     f'stroke-width="{22 if sure else 13}" stroke-linecap="round"/></g>')
    s.append(f'<text x="150" y="{H-30}" class="fine" style="fill:{INK3}">each mark — the true label of one missed image, from the pinned CSV</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── PLATE II
def plate_jetpack() -> str:
    H, LOOP, SET, a = 542, 10.3, 7.2, LIME
    s = [head(H, "jetpack — 6.4x parallel, and the intrinsic it does not beat",
              "jetpack: parallel gzip on JDK 25 reaches 422 megabytes per second against 66.2 "
              "single-threaded, a 6.4 times speedup, with blocks held in a bounded in-flight "
              "window. Its hand-vectorised Adler-32 checksum runs at 4.26 gigabytes per second "
              "and is verified bit-identical against java.util.zip — whose own native intrinsic "
              "is faster still, at 14.06, and is printed here as the reference it loses to.",
              key="plate-2-jetpack.svg")]
    # ── the window, drawn DOING what its caption claims. The old form slid four
    # blocks in once and held them for 60% of the loop, with three hairlines
    # cycling inside the bracket to carry the raster gate — a decoration doing
    # the work the diagram should. Now the diagram does it: the in-order writer
    # drains the OLDEST block from the top slot, the queue advances one slot,
    # and a fresh block enters the bottom from the left. Four blocks in
    # rotation, one drain every quarter loop, and the count in flight never
    # exceeds four — which is the entire claim. The drain is a shrink toward
    # the right edge (streamed out to the file), not a slide past x=294: the
    # window's far line is declared with data-max-x and a block visibly
    # crossing it would be the bound failing to bind.
    #
    # Each block gets its OWN keyframes, one quarter-loop apart. A shared
    # class would put four 2.6s delays in one stagger group, and check 14 is
    # right that 2.6s siblings do not read as one gesture — these are four
    # positions in a rotation, not a wave. The timeline is simulated once
    # here rather than authored four times by eye.
    BH, SP, BY0 = 18, 26, 186      # block height, slot pitch, top slot y
    cyc = []
    for k in range(4):
        off = lambda j: (j - k) * SP
        stop = lambda t, j, x=0, o=1, sx=1: seg.append(
            (t, f"opacity:{o};transform:translate({x}px,{off(j)}px) scaleX({sx})"))
        seg, c = [], k
        stop(0, k)
        for j in range(4):
            e = 2 + 25 * j
            if j == k:                       # this block's own drain
                stop(e, 0); stop(e + 3.5, 0, o=0, sx=0.08)
                stop(e + 5.5, 3, x=-88, o=0) # hidden reposition to the entry
                stop(e + 9, 3); c = 3
            else:                            # the queue advances one slot
                stop(e + 1.5, c); c -= 1; stop(e + 5, c)
        stop(100, k)
        cyc.append(f".b{k}{{transform-box:fill-box;transform-origin:right center;"
                   f"animation:cyc{k} {LOOP}s {EASE} infinite}}\n@keyframes cyc{k}{{"
                   + "".join(f"{t:g}%{{{v}}}" for t, v in seg) + "}")
    s.append("".join(cyc) + f"""
.mt{{transform-box:fill-box;transform-origin:left center;animation:mt {LOOP}s {ARRIVE} infinite}}
@keyframes mt{{0%,6%{{transform:scaleX(0);opacity:0}}11%{{opacity:1}}24%,100%{{transform:scaleX(1);opacity:1}}}}
</style>{ground(H)}""")
    s.append(frontis("III", "JETPACK", "ONE VIRTUAL THREAD PER BLOCK"))
    s.append(f'<text x="330" y="104" class="lbl">PARALLEL vs SINGLE-THREAD GZIP</text>')
    # NOT "CI ±5%": the 3-fork run's 99.9% intervals span ±0.7% to ±6.9%, so a
    # single figure would be a claim the committed JSON contradicts.
    s.append(f'<text x="330" y="126" class="lbl">JDK 25 · M1 PRO · 3 JMH FORKS</text>')
    s.append(f'<text x="150" y="148" class="hero">6.4<tspan class="unit">×</tspan></text>')

    # The bounded in-flight window, drawn DOING what its caption claims — the
    # one rotation on this plate, kept because the bound is shown binding:
    # data-max-x declares the far line, and a block crossing it would fail the
    # gate, not just the caption.
    s.append(f'<text x="400" y="180" class="kick">BOUNDED IN-FLIGHT WINDOW</text>')
    s.append(f'<path d="M174 172V288M174 172H194M174 288H194" stroke="{WIRE}" stroke-width="1"/>')
    s.append(f'<path d="M294 172V288M294 172H274M294 288H274" stroke="{WIRE}" stroke-width="1"/>')
    # Authored full: the finished frame shows the window holding its bound of
    # four, which is the picture the caption describes. The keyframes above
    # supply the rotation; block k's 0% IS its authored slot, so there is no
    # negative delay to carry and no start pose to hide.
    for k in range(4):
        s.append(f'<rect class="b{k}" data-max-x="294" x="180" y="{BY0 + k*SP}" '
                 f'width="107.8" height="{BH}" rx="2" style="fill:{a}"/>')
    for j, ln in enumerate(["peak memory", "tracks the window,", "not the file"]):
        s.append(f'<text x="400" y="{214 + j*20}" class="fine">{ln}</text>')

    # checksum audit: the fast path checked against the reference
    s.append(f'<text x="150" y="336" class="lbl">SIMD ADLER-32</text>')
    s.append(f'<text x="150" y="360" class="lbl">java.util.zip</text>')
    # the known-answer vector the repo commits: Adler32Test.java:36-37
    # One string per row; the match is drawn as a rule that sweeps the width
    # of the two rows it is comparing — the second surviving gesture, because
    # "verified bit-identical" is a comparison and the sweep performs it.
    s.append(f'<text x="330" y="336" class="key">11E60398</text>')
    s.append(f'<text x="330" y="360" class="key">11E60398</text>')
    s.append(f'<rect class="mt" x="330" y="342" width="90" height="2" fill="{a}" style="animation-delay:{-SET}s"/>')
    s.append(f'<text x="556" y="352" class="lbl" style="fill:{a}">identical</text>')

    # the verdict — the measured table, including the reference he does NOT beat
    s.append(f'<path d="M150 384H730" stroke="{RULE}"/>')
    rows = [
        ("Adler-32 scalar (pure Java)", "1.52", "GB/s", ""),
        ("Adler-32 hand-vectorised", "4.26", "GB/s", "2.80×"),
        ("java.util.zip intrinsic", "14.06", "GB/s", "not beaten"),
        ("gzip, one thread", "66.2", "MB/s", ""),
        ("parallel virtual threads", "422", "MB/s", "6.4×"),
    ]
    for i, (name, score, unit, note) in enumerate(rows):
        y = 416 + i * 24
        s.append(f'<text class="lbl" x="150" y="{y}">{name}</text>')
        # D14 — five values left-aligned at x=470 in a monospace face, so the
        # decimal points did not line up (14.06 pushed a column right) and GB/s
        # sat in the same column as MB/s with nothing to say which was bigger.
        # Numeral right-aligned, unit in its own column.
        s.append(f'<text class="key" x="530" y="{y}" text-anchor="end">{score}</text>')
        s.append(f'<text class="lbl" x="542" y="{y}">{unit}</text>')
        if note:
            fill = INK if note == "not beaten" else a
            s.append(f'<text class="lbl" x="604" y="{y}" style="fill:{fill}">{note}</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── PLATE III
def plate_cadence() -> str:
    """The smallest system figure, on purpose.

    The old plate paid a full week grid — MON through THU permanently empty,
    ~40% of the plate blank calendar — to file one chip, and the audit called
    the emptiness what it was. The claim is 'filed into the Friday 1pm slot',
    and one Friday column shows exactly that. What the plate buys with the
    space: the 36/12 line, the best verbal-visual joke on the page, stops
    hiding under an empty calendar. The now-line went with the week: it was
    the one sweep with a real referent, but it spent part of every loop
    passing through the chip — the single object the diagram exists to file —
    and a single day column gives it no travel worth having. The one gesture
    left is the filing itself: lead draws, chip lands.
    """
    H, LOOP, SET, a = 468, 7.9, 5.6, EMERALD
    SENT, FS, CW = "lunch with sam friday 1pm", 26, 15.62
    s = [head(H, "Cadence — a parser that shows its work",
              "Cadence: the sentence 'lunch with sam friday 1pm' is labelled in place with the "
              "parser that produced each span — compromise found the person, chrono-node found "
              "both the day and the time — while the title is left unmarked because it is what "
              "remains once the spans are removed and carries no parser. It is then filed into "
              "the 1pm slot of a Friday day column that names its hours. Its 36 API handlers "
              "are bundled into a single serverless function, because the hosting plan allows "
              "12.", key="plate-3-cadence.svg")]
    s.append(f""".ul{{animation:ul {LOOP}s {EASE} infinite;transform-box:fill-box;transform-origin:left center}}
@keyframes ul{{0%,4%{{transform:scaleX(0);opacity:0}}8%{{opacity:1}}18%,100%{{transform:scaleX(1);opacity:1}}}}
.an{{animation:an {LOOP}s linear infinite}}
@keyframes an{{0%,6%{{opacity:0}}8%,100%{{opacity:1}}}}
/* the filing itself, drawn: a lead from the chrono span down to the slot it
   names, redrawn every loop just before the chip lands */
.lead{{stroke-dasharray:1;animation:lead {LOOP}s {EASE} infinite;animation-delay:{-SET}s}}
@keyframes lead{{0%,8%{{stroke-dashoffset:1}}26%,100%{{stroke-dashoffset:0}}}}
/* the chip ARRIVES rather than fades — a 0.16s appearance and a 12% settle
   pop. Tuned against the raster, not by taste alone: the old gentle fade
   spread the chip's arrival across six samples at ~6 RGB units each, under
   the diff threshold, so the one gesture this plate keeps was invisible. An
   event being filed into a calendar lands with a thunk anyway. */
.fil{{transform-box:fill-box;transform-origin:center;animation:fil {LOOP}s {BREATHE} infinite}}
@keyframes fil{{0%,16%{{opacity:0;transform:scale(.94)}}18%{{opacity:1;transform:scale(1)}}
  44%{{transform:scale(1)}}50%{{transform:scale(1.12)}}56%,100%{{opacity:1;transform:scale(1)}}}}
</style>{ground(H)}""")
    s.append(frontis("IV", "CADENCE", "EVERY SPAN CARRIES ITS PARSER"))
    s.append(f'<text x="150" y="118" font-size="{FS}" fill="{INK}" letter-spacing="0">{SENT}</text>')
    # This diagram used to label TITLE / WHO / DAY / TIME — field TYPES, not
    # parsers — and underlined the title in the same green as the rest, while
    # README §IV states the opposite: the title is what is LEFT once the spans
    # are removed, and it carries no `source` at all.
    #
    # Now it names the parser that produced each span, from Cadence's own
    # booklet/src/content.ts: chrono-node (priority 10) reads dates and times,
    # compromise (priority 6) does the in-browser NLP pass that finds people.
    # "friday" and "1pm" therefore share a label, which is the useful part —
    # one parser, two spans. The title gets no underline, because it has no
    # parser to carry.
    for i, (start, ln) in enumerate([(11, 3), (15, 6), (22, 3)]):
        x, w = 150 + start * CW, ln * CW
        s.append(f'<rect class="ul" x="{x:.0f}" y="128" width="{w:.0f}" height="2" fill="{a}" '
                 f'style="animation-delay:{round(-SET + i * 0.12, 3)}s"/>')
    # friday and 1pm are ONE parser's output, so they get one bracket and one
    # label. That is the fact worth drawing: a parser is not a field.
    bx, bw = 150 + 15 * CW, 10 * CW
    s.append(f'<path d="M{bx:.0f} 136V142H{bx+bw:.0f}V136" fill="none" stroke="{a}" opacity="{op(0.7)}"/>')
    s.append(f'<text class="an fine" x="{150 + 11 * CW:.0f}" y="162" '
             f'style="fill:{a};animation-delay:{round(-SET, 3)}s">compromise</text>')
    s.append(f'<text class="an fine" x="{bx + bw / 2:.0f}" y="162" text-anchor="middle" '
             f'style="fill:{a};animation-delay:{round(-SET + 0.12, 3)}s">chrono</text>')
    s.append(f'<text x="150" y="188" class="kick">THE TITLE IS WHAT IS LEFT — IT CARRIES NO PARSER</text>')

    s.append(f'<path d="M150 210H730" stroke="{RULE}"/>')
    # ── one day, filed into. The hour gutter is right-aligned so it cannot
    # drift into the type column; "1pm".."4pm" never strip to bare numerals,
    # so the labels add no unaudited numbers, and the bare "12" is the same
    # hosting-cap 12 the hero line cites — accounted for, not smuggled.
    s.append(f'<text x="150" y="240" class="kick">FILED — INTO THE HOUR IT NAMES</text>')
    s.append(f'<text x="560" y="240" class="lbl">FRI</text>')
    s.append(f'<rect x="560" y="252" width="96" height="160" rx="3" fill="none" stroke="{WIRE}"/>')
    for hy, hl in ((268, "12"), (300, "1pm"), (332, "2pm"), (364, "3pm"), (396, "4pm")):
        s.append(f'<text x="548" y="{hy}" class="fine" text-anchor="end">{hl}</text>')
    for hr in (284, 316, 348, 380):
        s.append(f'<path d="M560 {hr}H656" stroke="{RULE}" stroke-width="1"/>')
    # the lead from the parsed span to the slot it names — a hairline, so it
    # may pass over the column frame, routed from where the chrono bracket
    # ends so it never crosses its own label
    s.append(f'<path class="lead" d="M540 142C600 180 604 240 604 286" pathLength="1" '
             f'fill="none" stroke="{a}" stroke-width="1.4" opacity="{op(0.7)}"/>')
    s.append(f'<g class="fil" style="animation-delay:{-SET}s">'
             f'<rect x="564" y="288" width="88" height="20" rx="3" fill="{CHIP}" stroke="{a}"/>'
             f'<text x="572" y="302" class="fine" style="fill:{a}">lunch</text></g>')

    # the joke gets the floor it earned: nothing under it, nothing beside it
    # but the empty afternoon it refuses to pay for
    s.append(f'<text x="150" y="372" class="hero">36</text>')
    s.append(f'<text x="232" y="356" class="lbl">HANDLERS IN ONE FUNCTION</text>')
    s.append(f'<text x="232" y="380" class="lbl">THE PLAN ALLOWS 12</text>')
    s.append(f'<text x="150" y="{H-30}" class="fine" style="fill:{INK3}">36 routes in one dispatch table — counted from api/index.ts</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── PLATE IV
def plate_applied() -> str:
    """The cascade, redrawn from scratch.

    The audit called the old composition the weakest on the page and every
    charge held: the three layers were dashed hairlines at the far right with
    their labels at the far left (the eye ping-ponged), the envelopes were
    unlabelled rounded rects that said nothing about mail, and a four-slot
    refill cycle meant the still frame was frequently a stack with a hole in
    it — a mid-refill snapshot that read as a bug. Underneath all of it, three
    of the four moving parts existed to feed the raster gate.

    Now the three layers are drawn as what they are — a stack the mail falls
    through, labels inside — and exactly ONE thing moves: a single message
    that descends the cascade, fails the 0.85 gate, is visibly held there
    (the pause is the refusal), and is walked to the human. That journey is
    the entire claim of the system, performed once per loop; the plate is
    still the rest of the time, and its rest pose is the message with the
    person it was referred to.
    """
    H, LOOP, a = 554, 11.7, CYAN
    s = [head(H, "Applied — a classifier allowed to say it doesn't know",
              "Applied: a three-layer email classifier — 201 regex rules, then e5 embeddings, "
              "then a fine-tuned SetFit head, cheapest first. It scores 0.979 macro-F1 on a "
              "96-message evaluation set, measured with the rules layer alone; anything that "
              "fails to clear the 0.85 confidence gate is referred to a human rather than "
              "guessed at. Inference runs inside your browser.", key="plate-4-applied.svg")]
    # One keyframes, no delay: 0% IS the authored rest, so the still frame and
    # frame zero are both the finished pose. The hidden reposition at 56-58%
    # happens at opacity 0; the fall lane sits to the RIGHT of the layer
    # boxes, so the message never straddles a frame edge in flight.
    s.append(f""".div{{animation:dv {LOOP}s {EASE} infinite}}
@keyframes dv{{0%,54%{{opacity:1;transform:translate(0,0)}}
  56%{{opacity:0;transform:translate(0,0)}}
  58%{{opacity:0;transform:translate(-46px,-238px)}}
  60%{{opacity:1;transform:translate(-46px,-238px)}}
  74%{{transform:translate(-46px,-76px)}}
  80%{{transform:translate(-46px,-76px)}}
  88%,100%{{opacity:1;transform:translate(0,0)}}}}
</style>{ground(H)}""")
    s.append(frontis("V", "APPLIED", "ALLOWED TO SAY IT DOESN’T KNOW"))
    # 0.979 is the number with artifacts behind it. 0.9583 — the full
    # cascade — has none: the run that produced it was overwritten by the
    # deterministic re-run. So the hero is the number I can hand you,
    # labelled for what it actually measures, and the gap is stated rather
    # than papered over.
    s.append(f'<text x="150" y="148" class="hero">0.979</text>')
    s.append(f'<text x="400" y="104" class="lbl">MACRO-F1 · 96-MSG EVAL SET</text>')
    s.append(f'<text x="400" y="126" class="lbl" style="fill:{a}">RULES LAYER ONLY</text>')
    s.append(f'<text x="400" y="146" class="fine">SetFit off, embeddings emptied</text>')
    s.append(f'<text x="400" y="166" class="fine">CI fails the build below 0.95</text>')

    # the cascade: labels INSIDE the layers they name
    s.append(f'<text x="330" y="192" class="kick">THE CASCADE — CHEAPEST FIRST</text>')
    for i, label in enumerate(["201 REGEX RULES", "e5 EMBEDDINGS", "SETFIT HEAD"]):
        y = 200 + i * 48
        s.append(f'<rect x="330" y="{y}" width="260" height="36" fill="none" stroke="{WIRE}"/>')
        s.append(f'<text x="346" y="{y+23}" class="lbl">{label}</text>')

    # the gate that is allowed to decline
    s.append(f'<text x="150" y="360" class="lbl" style="fill:{a}">0.85 CONFIDENCE GATE</text>')
    s.append(f'<path d="M390 356H640" stroke="{a}" stroke-width="1"/>')

    # outcomes. The envelopes carry a flap now, so they read as mail rather
    # than as anonymous rounded rects — the audit's exact words.
    def envelope(x, y, col):
        return (f'<g><rect x="{x}" y="{y}" width="30" height="20" rx="2" '
                f'style="fill:{col};fill-opacity:{op(0.5)};stroke:{col};stroke-width:1.6"/>'
                f'<path d="M{x} {y}L{x+15} {y+9}L{x+30} {y}" fill="none" stroke="{col}" stroke-width="1.2"/></g>')
    s.append(f'<text x="150" y="424" class="lbl">CLASSIFIED</text>')
    for i in range(4):
        s.append(envelope(330 + i * 44, 410, a))
    # the one that does not clear the gate reaches a PERSON — if it merely
    # left the stack, the plate would say nothing
    s.append(f'<g class="div">'
             f'<rect data-rest="the-human" data-rest-within="10" x="656" y="410" width="30" height="20" rx="2" '
             f'style="fill:{INK2};fill-opacity:{op(0.5)};stroke:{INK2};stroke-width:1.6"/>'
             f'<path d="M656 410L671 419L686 410" fill="none" stroke="{INK2}" stroke-width="1.2"/></g>')
    s.append(f'<circle id="the-human" cx="700" cy="446" r="11" fill="none" stroke="{INK2}" stroke-width="1.4"/>')
    s.append(f'<text x="{R}" y="478" class="lbl" style="fill:{INK2}" text-anchor="end">A HUMAN</text>')

    s.append(f'<path d="M150 496H730" stroke="{RULE}"/>')
    s.append(f'<text x="150" y="515" class="lbl">YOUR BROWSER</text>')
    s.append(f'<text x="330" y="504" class="fine">int8 ONNX · 90.4 MB → 22.8 MB</text>')
    s.append(f'<text x="330" y="{H-30}" class="fine">nothing you paste leaves the tab</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── PLATE V
def plate_refusal() -> str:
    """The Cadence isolation audit, drawn service by service.

    Two defects this layout replaces. The plate said IDOR IN SIX SERVICES and
    then drew four anonymous grey bars per tenant — an assertion where the page
    promises evidence, on the one plate whose whole subject is what happens
    when you take an assertion at its word. And its mechanism was a recolour of
    the AutoML approval gate: a token travels, meets a line, is held. Two
    consecutive plates drew "something is stopped" with the same object.

    So the six services are NAMED, and the refusal happens to the ROWS. Each
    service row carries its owner-scoped read and delete marks — the property
    claims.mjs re-derives from the guard in the query, not from a commit
    message — and tenant A's row is struck out of a read run as B while B's
    row returns. The two asterisks are the most interesting thing the audit
    found and they stay on the plate: the tags test asserted the vulnerable
    query, so it would have reported green forever, and task-lists still has
    no regression test. A drawn caveat is worth more than a drawn trophy.
    """
    H, a = 700, EMERALD
    s = [head(H, "The refusal — six services named, and the database that declines",
              "The IDOR found auditing Cadence, drawn service by service: in six services — "
              "attachments, calendars, events, task-lists, tasks and tags — any authenticated "
              "user could read or delete another user's records by id. Each service row "
              "carries its owner-guard marks: on read, all six carry the guard in the query "
              "itself; on delete, three do, and the other three check ownership first and "
              "then delete by id. Tenant A's rows are struck out of a read run as tenant B, "
              "and only B's return. Two caveats stay on the plate: the tags test asserted "
              "the vulnerable query, and task-lists still has no regression test. Below, the "
              "layer that does not depend on remembering: an unfiltered SELECT count(*) FROM "
              "tasks, run as B, comes back B only, because PostgreSQL row-level security "
              "refused the rest.", key="plate-5-refusal.svg")]
    # ── THE BROADSIDE. This is the best story on the page — the audit's words —
    # and the old set gave it the same slab as a gzip benchmark: eight of ten
    # plates inside a 130u band, so nothing could say "this one matters". Now
    # the heights say it: the refusal is the tallest figure in the document and
    # the only place the 64px hero face is spent on a WORD.
    #
    # STILL, and the stillness was earned the honest way: the first draft of
    # this round animated the strikes — a redraw wave down A's column, 80ms a
    # row, once per loop — and the re-authored motion gate measured it at 0 of
    # 67 samples visible. Six 102x2 hairlines are simply below what a reader
    # can see at readme scale, and a gesture nobody can see is instrument-food
    # by this build's own definition. The old read-head sweep is gone for the
    # worse crime: on a plate where a strike MEANS "withheld", it spent part
    # of every loop applying the plate's own symbol to the wrong nouns. So the
    # table stands as a finished exhibit — struck, guarded, footnoted — which
    # is what an audit that is OVER should look like.
    s.append(f"</style>{ground(H)}")

    s.append(frontis("VI", "THE REFUSAL", "SIX SERVICES, SELF-AUDITED"))
    s.append(f'<text x="{L}" y="98" class="kick">ANY USER COULD READ OR DELETE ANOTHER’S ROWS BY ID</text>')
    s.append(f'<text x="{L}" y="118" class="kick">THE MARKS SHOW WHERE EACH GUARD NOW SITS</text>')

    # ── the table: six services, named. Column headers in the same 11px voice.
    # B's header names it the CALLER, because that is the entire scene: B asks,
    # and what B gets back is the last column.
    for x, t in ((340, "READ"), (404, "DELETE"), (480, "TENANT A")):
        s.append(f'<text x="{x}" y="152" class="kick">{t}</text>')
    s.append(f'<text x="{R}" y="152" class="kick" text-anchor="end">TENANT B — CALLER</text>')
    # README order, which is the audit's order — not alphabetical, and not
    # anonymised. The footnote markers are resolved at the bottom of the plate.
    #
    # The DELETE column tells the truth the 2026-08 audit sharpened: all six
    # services carry the owner predicate in the READ query, but only events,
    # tasks and tags carry it in the DELETE itself — attachments, calendars
    # and task-lists check ownership first and then run DELETE WHERE id. A
    # hollow mark is not a missing mark; it is a different mechanism, and the
    # legend says which. The plate used to draw all twelve marks identical,
    # which overstated what claims.mjs actually derives.
    SVCS = [("attachments", False), ("calendars", False), ("events", True),
            ("task-lists*", False), ("tasks", True), ("tags**", True)]
    for i, (name, in_query) in enumerate(SVCS):
        y = 182 + i * 34
        s.append(f'<text x="{L}" y="{y}" class="lbl">{name}</text>')
        # read: the guard is in the query, all six — the fact claims.mjs
        # counts from AND "userId" = $ in the six service files
        s.append(f'<rect x="354" y="{y-10}" width="8" height="8" fill="{a}"/>')
        # delete: in the query for three; checked-then-deleted for the rest
        if in_query:
            s.append(f'<rect x="427" y="{y-10}" width="8" height="8" fill="{a}"/>')
        else:
            s.append(f'<rect x="427" y="{y-10}" width="8" height="8" fill="none" stroke="{a}" stroke-width="1.4"/>')
        # tenant A's row EXISTS — grey, framed like any stored row — and is
        # struck out of the result. Withheld is not deleted.
        s.append(f'<rect x="480" y="{y-12}" width="110" height="16" rx="2" fill="{ROW}" stroke="{WIRE}"/>')
        s.append(f'<rect x="484" y="{y-5}" width="102" height="2" fill="{a}"/>')
        # tenant B's row is the one that comes back
        s.append(f'<rect x="620" y="{y-12}" width="110" height="16" rx="2" fill="{ROW}" stroke="{a}"/>')

    # the legend, in drawn marks rather than glyphs the font subset may not carry
    s.append(f'<rect x="{L}" y="380" width="8" height="8" fill="{a}"/>')
    s.append(f'<text x="166" y="388" class="fine">the guard is in the query</text>')
    s.append(f'<rect x="390" y="380" width="8" height="8" fill="none" stroke="{a}" stroke-width="1.4"/>')
    s.append(f'<text x="406" y="388" class="fine">checked first, then DELETE WHERE id</text>')

    # the footnotes ARE the finding. A table of six green rows is a trophy;
    # these two lines are what an audit that means it looks like.
    s.append(f'<text x="{L}" y="420" class="fine" style="fill:{INK3}">*  task-lists — still has no regression test</text>')
    s.append(f'<text x="{L}" y="440" class="fine" style="fill:{INK3}">** tags — its test asserted the vulnerable query. Green forever.</text>')

    s.append(f'<path d="M{L} 472H{R}" stroke="{RULE}"/>')
    # unfiltered on purpose: a predicate that names B and returns B proves nothing
    s.append(f'<text x="{L}" y="512" class="key">SELECT count(*) FROM tasks</text>')
    s.append(f'<text x="470" y="512" class="fine">as B — unfiltered on purpose</text>')
    # the payoff, at the size the page reserves for its biggest numbers —
    # except it is not a number
    s.append(f'<text x="{L}" y="600" class="hero">B only</text>')
    s.append(f'<text x="470" y="600" class="lbl">ROW-LEVEL SECURITY</text>')
    s.append(f'<text x="{L}" y="640" class="say">The app didn’t remember to filter.</text>')
    s.append(f'<text x="{L}" y="{H-32}" class="say">The database refused.</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── PLATE VI
def plate_release() -> str:
    H, LOOP, SET = 660, 13.1, 9.8
    BEAT = round(LOOP / 4, 2)
    s = [head(H, "LifeQuest",
              "LifeQuest turns real-world routines into tracked quests, for people rebuilding "
              "structure after a layoff or in retirement. One source tree in apps/desktop is "
              "built twice — as a Tauri 2 native binary and as a web app — with a shared Zod "
              "schema package meant to hold both builds and the API to one contract. Behind "
              "it: 10 Prisma models and 14 REST endpoints across 6 NestJS controllers. When "
              "it generates a quest it asks OpenAI, falls back to Hugging Face, and if "
              "neither is configured it returns nothing rather than inventing one. Licensed "
              "MIT; a real schema test suite exists, and CI does not run it.",
              key="plate-6-release.svg")]
    # ── the quest list, run as a rotation — kept, because it IS the claim.
    # LifeQuest's claim is that ROUTINES become quests, and a routine is a
    # thing that recurs: the top quest completes (its ring fills), files away,
    # the list advances one slot, and the completed quest re-enters at the
    # bottom to come around again. Four quests, one completion every quarter
    # loop. Everything else this plate used to animate — the source box's
    # knock, the endpoint shoves, the interior washes, the label flips — was
    # tuned, by its own comments' admission, to what the raster gate could
    # see, and the doctrine that demanded that is gone. The chain holds still
    # now; RETURNS NOTHING never moved, and now it is in good company.
    #
    # One keyframes per quest: four 3.2s siblings in one class would be a
    # queue, not a wave, and check 14's 200ms ceiling is right to refuse it.
    QP, QY = 28, 104                   # quest pitch, first circle centre
    E = [2 + 24.5 * j for j in range(4)]
    quests = []
    for k in range(4):
        off = lambda j: (j - k) * QP
        stop = lambda t, j, x=0, o=1: seg.append(
            (round(t, 1), f"opacity:{o};transform:translate({x}px,{off(j)}px)"))
        seg, c = [], k
        stop(0, k)
        for j, e in enumerate(E):
            if j == k:                 # complete: nudge, fill (see .c{k}), file away
                stop(e, 0); stop(e + 1.2, 0, x=6); stop(e + 2.6, 0)
                stop(e + 3.5, 0); stop(e + 5.8, 0, o=0)
                stop(e + 6.8, 3, x=-16, o=0)   # hidden reposition below the list
                stop(e + 8.5, 3, x=-16, o=0)
                stop(e + 11, 3); c = 3         # …and the routine comes around again
            else:                      # the list advances one slot — unhurried:
                stop(e + 4, c); c -= 1         # ~4u per 100ms reads as the list
                stop(e + 9.5, c)               # breathing, not twitching
        stop(100, k)
        quests.append(
            f".q{k}{{animation:qst{k} {LOOP}s {EASE} infinite}}\n@keyframes qst{k}{{"
            + "".join(f"{t:g}%{{{v}}}" for t, v in seg) + "}\n"
            f".c{k}{{animation:cir{k} {LOOP}s linear infinite}}\n@keyframes cir{k}{{"
            f"0%,{E[k]:g}%{{fill-opacity:0}}{E[k]+1.5:g}%,{E[k]+5:g}%{{fill-opacity:1}}"
            f"{E[k]+6.5:g}%,100%{{fill-opacity:0}}}}\n"
            # the completing quest's label brightens for exactly as long as it
            # is the one being completed, and files away bright
            f".t{k}{{animation:tq{k} {LOOP}s linear infinite}}\n@keyframes tq{k}{{"
            f"0%,{E[k]:g}%{{fill:{INK2}}}{E[k]+1:g}%,{E[k]+5.5:g}%{{fill:{INK}}}"
            f"{E[k]+7:g}%,100%{{fill:{INK2}}}}}")
    s.append("".join(quests) + f"""
/* One build leaves the shared tree down each branch, four times a loop. */
.bd{{animation:bd {BEAT}s {EASE} infinite}}
@keyframes bd{{0%{{opacity:0;transform:translateX(-42px)}}
  16%{{opacity:1}}84%{{opacity:1}}
  100%{{opacity:0;transform:translateX(0)}}}}
</style>{ground(H)}""")
    s.append(frontis("VII", "LIFEQUEST", "WHAT YOU MEANT TO DO, AS QUESTS"))
    # circle and label move as one quest, so they share a <g>; the rail of
    # connectors stays put — it belongs to the LIST, not to any quest on it
    QUESTS = ["Reconnect with a mentor", "Document a new routine",
              "Share a win", "Take the morning walk"]
    for i, txt in enumerate(QUESTS):
        s.append(f'<g class="q{i}">'
                 f'<circle class="c{i}" cx="158" cy="{QY+i*QP}" r="7" '
                 f'style="fill:{PINK};fill-opacity:0;stroke:{PINK};stroke-width:1.6"/>'
                 f'<text x="178" y="{QY+5+i*QP}" class="lbl t{i}">{txt}</text></g>')
        if i < 3:
            s.append(f'<path d="M158 {QY+8+i*QP}V{QY+20+i*QP}" stroke="{WIRE}" stroke-width="1"/>')
    s.append(f'<text x="150" y="240" class="say">For people rebuilding structure —</text>')
    s.append(f'<text x="150" y="268" class="say">after a layoff, or in retirement.</text>')

    s.append(f'<path d="M150 296H730" stroke="{RULE}"/>')
    s.append(f'<text x="150" y="326" class="kick">ONE SOURCE TREE, BUILT TWICE</text>')

    # the fork: the same apps/desktop tree is a Vite web build and a Tauri
    # native binary, and packages/schemas is the Zod contract meant to keep
    # both of them honest against the NestJS API ("meant to": the README
    # carries the two precisions — controller uptake and a Zod major skew).
    s.append(f'<rect x="150" y="336" width="240" height="70" rx="3" fill="none" stroke="{WIRE}"/>')
    s.append(f'<text x="166" y="366" class="fine" style="fill:{INK}">apps/desktop</text>')
    s.append(f'<text x="166" y="388" class="fine">React · Vite</text>')
    s.append(f'<path d="M390 371H420M420 353V389" fill="none" stroke="{WIRE}"/>')
    for i, (dy, txt) in enumerate([(-18, "TAURI 2 · NATIVE BINARY"), (18, "VITE BUILD · WEB APP")]):
        s.append(f'<path d="M420 {371+dy}H462" fill="none" stroke="{WIRE}"/>')
        # a build leaving down each branch, four times a loop — so the fork is
        # shown, not asserted
        s.append(f'<circle class="bd" cx="462" cy="{371+dy}" r="3.5" fill="{PINK}" '
                 f'style="animation-delay:{round(-BEAT*0.5 + i*0.12, 3)}s"/>')
        s.append(f'<text x="{R}" y="{376+dy}" class="lbl" text-anchor="end" style="fill:{PINK}">{txt}</text>')
    s.append(f'<text x="150" y="430" class="fine">packages/schemas — one Zod contract for both builds</text>')

    s.append(f'<path d="M150 454H730" stroke="{RULE}"/>')
    # one ledger row, not two 62u stat blocks — the numbers matter, the
    # ceremony around them did not
    s.append(f'<text x="150" y="496" class="sub">10</text>')
    s.append(f'<text x="230" y="496" class="lbl">PRISMA MODELS</text>')
    s.append(f'<text x="430" y="496" class="sub">14</text>')
    s.append(f'<text x="510" y="496" class="lbl">REST ENDPOINTS</text>')
    s.append(f'<text x="150" y="520" class="fine">quests, rewards, meetups, rituals · across 6 NestJS controllers</text>')

    # The quest generator asks OpenAI, then Hugging Face, and if neither is
    # configured it returns null rather than inventing a quest. Drawn as a
    # chain because that is the shape of the code (ai-content.service.ts:49-56)
    # and because the last link is the honest one. Still, all three: the box
    # that never answers no longer needs neighbours that fidget to make its
    # stillness legible.
    s.append(f'<text x="150" y="556" class="kick">QUEST GENERATION — ASKS, THEN FALLS BACK, THEN DECLINES</text>')
    for i, (txt, col) in enumerate([("OPENAI", PINK), ("HUGGING FACE", PINK), ("RETURNS NOTHING", INK3)]):
        x = 150 + i * 204
        s.append(f'<rect x="{x}" y="570" width="172" height="30" rx="3" fill="none" stroke="{WIRE}"/>')
        s.append(f'<text x="{x+14}" y="590" class="fine" style="fill:{col}">{txt}</text>')
        if i < 2:
            s.append(f'<path d="M{x+172} 585H{x+204}" stroke="{WIRE}"/>')
    s.append(f'<text x="150" y="{H-30}" class="fine" style="fill:{INK3}">MIT · a real schema test suite exists — CI does not run it</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── PLATE VII
def plate_automl() -> str:
    """AutoML's own plate.

    It shared plate VII with LifeQuest until now — a quest tracker and a
    multi-agent ML pipeline on one slab, which the audit called two plates in
    one and measured as the least dense in the set. It also carried the line
    "the one section you cannot check", because the repository was private.
    That stopped being true on 2026-07-30, so every figure here is DERIVED from
    a pinned commit like the other five systems, and the plate is built around
    the one mechanism that is genuinely unusual: the model is never handed the
    whole tool registry.
    """
    H, LOOP, SET = 638, 13.3, 9.9
    TICKS, GEN = 44, 15
    # pitch is set so the LAST tick's right edge lands on R, not so the first
    # 44 pitches span the column — the old form left the strip 8.3u short.
    PITCH = (R - L - 5) / (TICKS - 1)
    BARS, BX = 7, L + GEN * PITCH           # the seven sets sit under the routed 29
    BGAP = 8
    BPITCH = (R - BX + BGAP) / BARS   # last bar's right edge lands on R
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
              key="plate-6b-automl.svg")]
    # ── the phase clock. Everything that claims "one phase, one tool set" is
    # keyed to one set of seven windows: the marker (.mk) steps to set j, the
    # model's carried cluster (.mv) travels there, the slice of the 29 that
    # routes to that phase lights (.p0-.p6), and the set's own bar lights with
    # it (.sb0-.sb6). Windows are ~1.6s holds with 0.6s transits, all on the
    # same -9.9s clock, so the four devices can never disagree about which
    # phase is active.
    A = [round(100 / 7 * j + 2.25, 2) for j in range(7)]           # arrive at set j
    D = [round(100 / 7 * (j + 1) - 2.25, 2) for j in range(7)]     # depart set j
    phase = []
    for j in range(7):
        phase.append(
            f".p{j}{{animation:p{j} {LOOP}s linear infinite;animation-delay:{-SET}s}}\n"
            f"@keyframes p{j}{{0%,{A[j]-1.5:g}%{{fill:{WIRE}}}{A[j]:g}%,{D[j]:g}%{{fill:{INDIGO}}}"
            f"{min(D[j]+1.5, 99.9):g}%,100%{{fill:{WIRE}}}}}\n"
            f".sb{j}{{animation:kb{j} {LOOP}s linear infinite;animation-delay:{-SET}s}}\n"
            f"@keyframes kb{j}{{0%,{A[j]-1.5:g}%{{fill:{ROW}}}{A[j]:g}%,{D[j]:g}%{{fill:{INDIGO}}}"
            f"{min(D[j]+1.5, 99.9):g}%,100%{{fill:{ROW}}}}}")
    s.append(f"""{"".join(phase)}
/* THE 15 TRAVEL WITH THE MODEL — so they travel. The cluster is the model's
   carried registry: a frame of fifteen ticks that physically steps from set
   to set under the strip, arriving as each phase's slice lights above it.
   This is the plate's claim performed instead of captioned, and it is also
   what the raster gate sees: fifteen 5u ticks displacing 55u together move
   ~1% of the canvas per sample, where the marker hairline alone moved
   nothing. The wrap from the seventh set back to the first is a 332u jump,
   so it happens faded out, like the marker's. */
.mv{{animation:mv {LOOP}s {EASE} infinite;animation-delay:{-SET}s}}
@keyframes mv{{0%{{opacity:0;transform:translateX({-6*BPITCH:.1f}px)}}
  1.8%{{opacity:1;transform:translateX({-6*BPITCH:.1f}px)}}
  {"".join(f"{D[j]:g}%{{transform:translateX({-(6-j)*BPITCH:.1f}px)}}"
           f"{A[j+1]:g}%{{transform:translateX({-(5-j)*BPITCH:.1f}px)}}" for j in range(6))}
  97.5%{{opacity:1;transform:translateX(0)}}100%{{opacity:0;transform:translateX(0)}}}}
/* The marker is the claim: it steps through the seven sets one at a time and
   is never over more than one, because that is what phase-aware routing does.
   Seven holds of ~1.6s each — under the 2.4s ceiling on a dead run, and the
   sandbox scan runs underneath it the whole time so the plate is never still. */
/* The wrap from the seventh set back to the first is a 328u jump, which the
   gate calls a teleport and is right to. So it happens with the marker faded
   out, the same way plate VII's token resets — a cycle that visibly snaps
   backwards reads as a glitch, not as a new run starting. */
.mk{{animation:mk {LOOP}s steps(1,end) infinite;animation-delay:{-SET}s}}
@keyframes mk{{0%{{opacity:0;transform:translateX({-6*BPITCH:.1f}px)}}
  2%,12%{{opacity:1;transform:translateX({-6*BPITCH:.1f}px)}}
  14.3%,26%{{transform:translateX({-5*BPITCH:.1f}px)}}
  28.6%,40%{{transform:translateX({-4*BPITCH:.1f}px)}}
  42.9%,55%{{transform:translateX({-3*BPITCH:.1f}px)}}
  57.1%,69%{{transform:translateX({-2*BPITCH:.1f}px)}}
  71.4%,83%{{transform:translateX({-1*BPITCH:.1f}px)}}
  85.7%,97%{{opacity:1;transform:translateX(0)}}
  100%{{opacity:0;transform:translateX(0)}}}}
</style>{ground(H)}""")
    s.append(frontis("VIII", "AGENTIC AUTOML", "ONE PHASE, ONE TOOL SET"))

    # ── the registry, drawn at its real size
    s.append(f'<text x="{L}" y="160" class="hero">{TICKS}</text>')
    s.append(f'<text x="270" y="136" class="key">TOOL DEFINITIONS</text>')
    s.append(f'<text x="270" y="160" class="fine">one MCP server over a LangGraph state machine</text>')
    # The 15 core ticks are static now — their staggered arrival was a reveal,
    # not a claim. The 29 routed ones stay animated because their lighting IS
    # the claim: each lights (WIRE→INDIGO) in the window of the set that
    # routes it, assigned by position, so the lit block in the registry tracks
    # the marker and the cluster below it. Authored lit for the LAST set — the
    # still frame shows the final phase, where the marker and cluster rest.
    for i in range(TICKS):
        x = L + i * PITCH
        if i < GEN:
            s.append(f'<rect x="{x:.1f}" y="190" width="5" height="22" fill="{INDIGO}"/>')
        else:
            j = min(BARS - 1, int((x + 2.5 - BX) // BPITCH))
            s.append(f'<rect class="p{j}" x="{x:.1f}" y="190" width="5" height="22" '
                     f'style="fill:{INDIGO if j == BARS - 1 else WIRE}"/>')
    # brackets naming the two halves. The labels sit at the two OUTER edges —
    # left under the 15, right-anchored under the far end of the 29 — because
    # putting both flush-left made them collide, and the gate said so.
    s.append(f'<path d="M{L} 220V226H{L+(GEN-1)*PITCH+5:.1f}V220" fill="none" stroke="{WIRE}"/>')
    s.append(f'<text x="{L}" y="244" class="kick" style="fill:{INDIGO}">{GEN} TRAVEL WITH THE MODEL</text>')
    s.append(f'<path d="M{BX:.1f} 220V226H{L+(TICKS-1)*PITCH+5:.1f}V220" fill="none" stroke="{WIRE}"/>')
    s.append(f'<text x="{R}" y="244" class="kick" text-anchor="end">{TICKS-GEN} ARRIVE WITH THE PHASE</text>')

    # ── the model's carried cluster, in its own lane between the registry and
    # the sets. Fifteen ticks at the registry's own pitch inside a thin frame:
    # what the model holds, where the model currently is. Its right edge rests
    # on R at the final set — the authored, finished pose.
    CLW = 200
    CLX = R - CLW
    s.append(f'<g class="mv"><rect x="{CLX}" y="254" width="{CLW}" height="22" rx="2" '
             f'fill="none" stroke="{INDIGO}"/>'
             + "".join(f'<rect x="{CLX + 4 + t*PITCH:.1f}" y="258" width="5" height="14" '
                       f'style="fill:{INDIGO}"/>' for t in range(GEN)) + '</g>')

    # ── the seven sets, and the marker that is only ever under one of them.
    # The marker underlines rather than overlays: an indigo rect ON the bar is
    # a collision as far as the gate is concerned, and it was right to say so —
    # two filled rects at the same coordinates is exactly what a bug looks like.
    # The active bar also lights (.sb): four devices, one clock.
    for i in range(BARS):
        x = BX + i * BPITCH
        last = ' id="set-last"' if i == BARS - 1 else ''
        s.append(f'<rect{last} class="sb{i}" x="{x:.1f}" y="288" width="{BPITCH-BGAP:.1f}" height="8" rx="1" '
                 f'style="fill:{INDIGO if i == BARS - 1 else ROW}"/>')
    s.append(f'<rect class="mk" data-rest="set-last" data-rest-within="14" '
             f'x="{BX + (BARS-1)*BPITCH:.1f}" y="302" width="{BPITCH-BGAP:.1f}" height="3" rx="1" fill="{INDIGO}"/>')
    s.append(f'<text x="{L}" y="300" class="lbl">SEVEN PHASE SETS</text>')

    s.append(f'<path d="M{L} 316H{R}" stroke="{RULE}"/>')

    # ── the sandbox, quoted from the container it actually builds. Named
    # honestly this round: the page said `--network none` since the plate
    # existed, and it was never true — dockerBuilder.ts passes the configured
    # network, which defaults to `automl-sandbox`, created with
    # `docker network create --internal` (networkManager.ts). An --internal
    # network has no gateway: nothing inside can route out, which is the
    # isolation the sentence was reaching for. The repo's own comment still
    # says "default: none"; the repo's own test asserts the configured
    # network. This page sides with the test.
    s.append(f'<text x="{L}" y="346" class="kick">WHERE THE GENERATED PYTHON RUNS</text>')
    s.append(f'<rect x="{L}" y="360" width="330" height="124" rx="3" fill="none" stroke="{INDIGO}"/>')
    for i, (flag, why) in enumerate([("--internal network", "no route out"),
                                     ("--read-only", "immutable rootfs"),
                                     ("--user sandbox", "never root"),
                                     ("/datasets:ro", "read-only mount")]):
        s.append(f'<text x="{L+16}" y="{390+i*26}" class="fine" style="fill:{INK}">{flag}</text>')
        s.append(f'<text x="{L+186}" y="{390+i*26}" class="fine">{why}</text>')
    # the five writable mounts, drawn because their count IS the blast radius
    s.append(f'<text x="520" y="382" class="key">5 TMPFS MOUNTS</text>')
    s.append(f'<text x="520" y="404" class="fine">the only surface it can</text>')
    s.append(f'<text x="520" y="422" class="fine">write to, and none of it</text>')
    s.append(f'<text x="520" y="440" class="fine">survives the container</text>')
    for i in range(5):
        s.append(f'<rect x="{520+i*30}" y="456" width="20" height="14" rx="1" '
                 f'fill="none" stroke="{INDIGO}"/>')

    s.append(f'<path d="M{L} 516H{R}" stroke="{RULE}"/>')
    s.append(f'<text x="{L}" y="556" class="sub">29</text>')
    s.append(f'<text x="200" y="556" class="lbl">TABLES · POSTGRES + PGVECTOR</text>')
    s.append(f'<text x="200" y="578" class="fine">a Jupyter kernel per project, kept alive between cells</text>')
    s.append(f'<text x="{L}" y="{H-30}" class="fine" style="fill:{INK3}">public · GPL-3.0 · written with Shree Chaturvedi</text>')
    return "".join(s) + "</svg>"


# ────────────────────────────────────────────────────────────── PLATE IX
def plate_colophon() -> str:
    """The closing plate, and the serif's second and last appearance.

    The thesis opens in the author's voice — the one serif in a monospace
    document — and until now that voice never spoke again, so the device read
    as a one-off effect. The colophon is the other place the author speaks,
    and what he has to say here is the page's actual thesis, so it closes the
    bracket: same face, same size, stating what every figure above submits to.

    STILL, like the plate it answers. The first draft of this round kept one
    gesture — the header rule drawing itself once per loop — and the
    re-authored motion gate measured it at 1 of 127 samples visible: a 580x1
    hairline drawn over two and a half seconds moves ~23 square units per
    sample against a ~660 floor, so the gesture existed only for the
    instrument that used to demand it. The plate's ANIMATED SVG line describes
    the page, which remains true — five figures above perform their claims —
    and the raster pass that used to descend this plate (spending about a
    second of every loop lying across the author's degree and email — a
    strikethrough on the one actionable line of the document) is gone with the
    doctrine that demanded it, as are the two nudging text lines that fed the
    same gate.
    """
    H = 356
    s = [head(H, "Colophon", "Six systems, five system cards and one expo booklet. Every number "
                             "here is traceable to the repository it came from, and the page "
                             "itself is animated SVG "
                             "with no JavaScript and no server.", key="plate-7-colophon.svg")]
    s.append(f""".ser{{font-family:ui-serif,Georgia,'Times New Roman',serif;font-size:34px;fill:{INK}}}
</style>{ground(H)}""")
    s.append(f'<text x="{L}" y="{TOP}" class="lbl">EVERY NUMBER CHECKED IN CI</text>')
    s.append(f'<text x="{R}" y="{TOP}" class="lbl" text-anchor="end">'
             f'<tspan fill="{INK}">IX</tspan>  COLOPHON</text>')
    s.append(f'<path d="M{L} 70H{R}" stroke="{WIRE}"/>')

    # the serif answers the thesis plate — the only two sentences on this page
    # the machine did not derive, in the only face the machine does not use
    for i, ln in enumerate(["If a number here is wrong,", "it is wrong in public."]):
        s.append(f'<text x="{L}" y="{124 + i*42}" class="ser">{ln}</text>')

    for i, ln in enumerate(["Six systems. Five system cards, one booklet.",
                            "Every number traces to its repo, except §I."]):
        s.append(f'<text class="say" x="150" y="{214 + i*28}">{ln}</text>')
    s.append(f'<text x="150" y="270" class="fine" style="fill:{INK3}">§I is my employment and DataFest work — attested, not derivable</text>')
    s.append(f'<text x="150" y="298" class="lbl">ANIMATED SVG · NO JAVASCRIPT · NO SERVER</text>')
    s.append(f'<text x="150" y="{H-30}" class="lbl">B.S. CS · MIAMI UNIVERSITY ’26</text>')
    s.append(f'<text x="{R}" y="{H-30}" class="lbl" text-anchor="end">aesh.03.23@gmail.com</text>')
    return "".join(s) + "</svg>"


PLATES = {
    "plate-0-thesis.svg": plate_thesis, "plate-0b-work.svg": plate_work,
    "plate-1-glyph.svg": plate_glyph,
    "plate-2-jetpack.svg": plate_jetpack, "plate-3-cadence.svg": plate_cadence,
    "plate-4-applied.svg": plate_applied, "plate-5-refusal.svg": plate_refusal,
    "plate-6-release.svg": plate_release, "plate-6b-automl.svg": plate_automl,
    "plate-7-colophon.svg": plate_colophon,
}

# ────────────────────────────────────────────────── mobile set
# At GitHub's real 324px column a 16-unit label on an 880 canvas renders at
# 5.9px — unreadable. So the phone gets its own plates: a 440 canvas at the SAME
# absolute type sizes (≈11.8px rendered), carrying the hero and one line. The
# argument itself is already in the markdown, which is selectable, searchable
# and theme-native. Served via <picture media="(max-width:500px)">.
#
# The <desc> here used to be the desktop plate's string verbatim, and it
# described a picture the mobile file does not draw: m-5's said six services
# are "drawn service by service" over three text nodes, m-3's said a sentence
# "is labelled in place" over a plate that draws one number. The README's
# single <img> alt stays the desktop description — <picture> permits one alt,
# and that string describes the CLAIM, true whichever source loaded — but the
# file's own <desc>/aria-label is what a reader gets when the SVG is opened
# directly, so each mobile plate now carries a description of ITSELF. gate.mjs
# check 9 holds the pair honest in the direction that matters here: every
# number a mobile plate DRAWS must appear in its own description.
MW = 440


def plate_mobile(accent: str, kicker: str, hero: str, unit: str,
                 line1: str, line2: str, desc: str) -> str:
    h = 224   # a 64px hero's glyph box is 84u tall; 208 could not hold it
    # Same dissolution as the desktop set: no slab, no border, no accent bar
    # at x=0 — the client's "cards" complaint named the mobile device by
    # description, since the 4u bar was borrowed FROM this set. The system's
    # hue survives as the header rule under the kicker: one accent mark with a
    # referent (this system's colour, taught by the thesis sheet), not a frame.
    # The first rect carries the canvas colour at fill-opacity 0 for the same
    # reason as ground() above.
    return "".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {MW} {h}" width="{MW}" height="{h}" '
        f'role="img" aria-label="{desc}"><title>{kicker}</title><desc>{desc}</desc><style>'
        f"@font-face{{font-family:'M';src:url(data:font/woff2;base64,{FONT}) format('woff2')}}"
        f"text{{font-family:'M',ui-monospace,SFMono-Regular,Menlo,monospace}}"
        f".k{{font-size:16px;letter-spacing:1.8px;fill:{INK2}}}"
        f".n{{font-size:64px;letter-spacing:-1.5px;fill:{INK};font-weight:600}}"
        f".u{{font-size:26px;fill:{INK2}}}"
        f".t{{font-size:16px;fill:{INK2}}}"
        f"</style>"
        f'<rect width="{MW}" height="{h}" fill="{GROUND}" fill-opacity="0"/>',
        f'<text x="34" y="40" class="k">{kicker}</text>',
        f'<rect x="34" y="52" width="{MW-68}" height="2" fill="{accent}"/>',
        f'<text x="34" y="124" class="n">{hero}<tspan class="u">{unit}</tspan></text>',
        f'<text x="34" y="168" class="t">{line1}</text>',
        f'<text x="34" y="194" class="t">{line2}</text>',
        "</svg>"])


# The accent is the COLOUR'S NAME, resolved per theme at write time — a hex
# baked into this dict would hand the light pass the dark palette.
MOBILE = {
 "m-0-thesis.svg": ("AYUSH YADAV · CINCINNATI, OH", "INK2", "6", " systems",
   "From SIMD kernels to the", "browser they run in.",
   "Ayush Yadav, a computer science graduate in Cincinnati, Ohio, open to "
   "full-time engineering roles: 6 systems, from SIMD kernels to the browser "
   "they run in."),
 "m-0b-work.svg": ("WORK · MIAMI UNIVERSITY", "INK2", "57.8", "M rows",
   "from 1.6M Oracle query logs —", "a year of paid work, attested.",
   "Experience, attested by the author rather than derived from a public "
   "repository: as ITSM Data Integration Intern at Miami University, a Python "
   "pipeline turned 1.6 million Oracle Analytics query logs into a 57.8 "
   "million-row field-usage table."),
 "m-1-glyph.svg": ("GLYPH", "AMBER", "97.01", "%", "A neural net written from", "scratch in C++. 299 wrong.",
   "Glyph: a neural network written from scratch in C++. It scores 97.01 percent on the MNIST test set — 299 wrong."),
 "m-2-jetpack.svg": ("JETPACK", "LIME", "6.4", "×", "Parallel gzip on JDK 25.", "The JDK intrinsic still wins.",
   "jetpack: parallel gzip on JDK 25, a 6.4 times speedup over one thread — and the JDK's own checksum intrinsic still wins."),
 "m-3-cadence.svg": ("CADENCE", "EMERALD", "36", "", "handlers bundled into one", "function. The plan allows 12.",
   "Cadence: 36 API handlers bundled into one serverless function, because the hosting plan allows 12."),
 "m-4-applied.svg": ("APPLIED", "CYAN", "0.979", "", "macro-F1, rules layer only.", "Below 0.85 it asks a human.",
   "Applied: an email classifier scoring 0.979 macro-F1 with the rules layer alone. Below the 0.85 confidence gate it asks a human rather than guessing."),
 "m-5-refusal.svg": ("THE REFUSAL", "EMERALD", "B", " only", "The app didn't remember", "to filter. The database refused.",
   "The refusal: a query run as tenant B returns B only. The app didn't remember to filter; PostgreSQL row-level security refused."),
 # This entry once described a plate that no longer exists and asserted "Not
 # public" after the repository went public. It survived because stale prose
 # carrying no digits passes the number check silently. Parked is not a
 # licence to serve a false sentence.
 "m-6-release.svg": ("LIFEQUEST", "PINK", "10", "", "Prisma models, 14 endpoints.", "One tree, built desktop and web.",
   "LifeQuest: routines as tracked quests — 10 Prisma models and 14 REST endpoints behind one source tree, built desktop and web."),
 "m-6b-automl.svg": ("AGENTIC AUTOML", "INDIGO", "44", "", "tools in the registry. The model", "only ever holds its phase's set.",
   "Agentic AutoML: dataset in, trained model out. Its registry holds 44 tool definitions, but the model only ever holds the set its phase needs."),
 # The desktop colophon draws ANIMATED SVG and is animated. This one drew the
 # word "Animated" at 64px and carries no @keyframes at all — the whole mobile
 # set is static by design. Nothing could catch it: motion.mjs globs plate-*
 # only, and gate.mjs wraps its motion checks in `if (dur)`, so a plate with no
 # animations is exempt from every one of them. Same class of defect as
 # m-6-release telling phone readers AutoML was private: stale prose carrying
 # no digits passes the number check in silence.
 "m-7-colophon.svg": ("COLOPHON", "RULE", "SVG", "",
   "No JavaScript, no server,", "no external assets.",
   "Colophon: this page is SVG with no JavaScript, no server and no "
   "external assets."),
}

# ────────────────────────────────────────────────── the build-time gate
# Cheap structural checks only. The REAL layout gate is build/gate.mjs, which
# renders every plate in Chromium and measures 40 samples across each loop —
# arithmetic here cannot see a transform, and pretending otherwise is how nine
# collisions once shipped under a PASS.
import re as _re, sys as _sys, xml.dom.minidom as _xml

_fail = []
# One build, two documents. Dark keeps every path it has always had — it is
# the README's <img> fallback and the thing every external pin points at.
# Light lands in assets/light/ under the SAME basenames: build/gate.mjs keys
# its second measuring pass on that directory, so the naming is load-bearing.
for _theme in ("dark", "light"):
    set_theme(_theme)
    _out = OUT if _theme == "dark" else OUT / "light"
    _out.mkdir(exist_ok=True)
    for fn, gen in PLATES.items():
        path = _out / fn
        path.write_text(gen())
        try:
            _xml.parseString(path.read_text())
        except Exception as e:
            _fail.append(f"{_theme}/{fn}: MALFORMED XML — {e}")
        print(f"{_theme:5s} {fn}: {path.stat().st_size:,} bytes")
    for _fn, (_k, _acc, _n, _u, _l1, _l2, _desc) in MOBILE.items():
        (_out / _fn).write_text(plate_mobile(globals()[_acc], _k, _n, _u, _l1, _l2, _desc))
    print(f"{_theme:5s} mobile set: {len(MOBILE)} plates at {MW}w")
set_theme("dark")

# ────────────────────────────────────────────────── alt/desc/README agreement
# Every description is authored once in ALT and must reach the README verbatim —
# three surfaces drifted apart once and left a retracted claim alive in the
# accessible text.
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
print("\nBUILD OK — all plates parse, alts agree. Run `node build/gate.mjs` to measure them.")
