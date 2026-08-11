#!/usr/bin/env python3
"""Regenerate the three embedded font subsets. Not run in CI — the woff2
files are committed and plates.py only base64s their bytes, so the build
stays deterministic across platforms and needs nothing beyond stdlib.

THE FACES ARE FRAGMENT MONO AND FRAUNCES. Read the note above FONTS at the
bottom of this file before the history below, which is kept because it is
the argument for embedding faces at all — but which names JetBrains Mono and
Gelasio, both retired on 2026-08-08. This header cost a reader a wrong
conclusion on 2026-08-11: a font brief went out naming the retired pair
because the top of the file still described them in the present tense, and
only the build() calls at the bottom said otherwise. A docstring that
contradicts the code twenty lines below it is the same defect this page's
whole gate exists to catch, in the one place nothing measures.

Why three faces (the finding, 2026-08-06, diag/ci-fonts run 31143030894):
  * .sub/.hero/.vast/.n ask for font-weight:600 on a family that embedded
    only a 400 face. Every platform SYNTHESISES that bold differently —
    FreeType widens the ink, CoreText smears it — which is how "96.72%"
    overhung its column by 2.5u on Linux and 0.45u on macOS. A real 600
    face renders the same ink everywhere.
  * .ser was ui-serif/Georgia/'Times New Roman' — all platform fonts. CI
    resolved it to Liberation Serif, macOS to Georgia: the page's serif
    voice was a different typeface per reader. Gelasio is metric-compatible
    with Georgia (OFL), so embedding it keeps the authored geometry.
  * the old mono subset had 70 glyphs; the 12 drawn characters it lacked
    ( ) * , : = ? @ × – ’ → fell back per platform — the comma in the
    34px headline "10,453" rendered in Menlo on macOS and DejaVu Sans
    Mono on Linux. plates.py now asserts coverage at build time.

Sources (both OFL 1.1):
  JetBrainsMono[wght].ttf  https://raw.githubusercontent.com/google/fonts/main/ofl/jetbrainsmono/JetBrainsMono%5Bwght%5D.ttf
  Gelasio[wght].ttf        https://raw.githubusercontent.com/google/fonts/main/ofl/gelasio/Gelasio%5Bwght%5D.ttf

Usage: python3 build/subset-fonts.py <dir containing the two ttfs above>
Needs: fonttools, brotli.
"""
import pathlib, sys

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

from charsets import MONO_CHARS, BOLD_CHARS, SERIF_CHARS, TEXT_CHARS

ROOT = pathlib.Path(__file__).resolve().parent
SRC = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT


def build(src: pathlib.Path, wght: int, chars: str, out: pathlib.Path,
          features: list[str] | None = None,
          metrics: tuple[int, int] | None = None,
          opsz: int | None = None, _repro: bool = True) -> None:
    font = TTFont(src)
    if "fvar" in font:
        # Pin EVERY axis, not just weight. Fraunces declares four — wght, opsz,
        # SOFT and WONK — and instancing one of them leaves a variable font
        # whose remaining axes resolve to a default the SVG never states. SOFT
        # goes to 0 and WONK to 0: the plates are drawings, and a wonky leg on
        # a figure that sits beside a hairline rule reads as a misprint.
        #
        # opsz is the one axis whose right value is a FUNCTION OF THE RENDERED
        # SIZE, so it cannot be a constant of this file — each call states its
        # own, and a face that HAS the axis and states nothing is a build
        # failure rather than a silent 144.
        #
        # It was 144 for both serif instances until 2026-08-11, on the argument
        # "these are 34-89px heroes, not body copy". The argument named the
        # right sizes and drew the wrong conclusion from them: 144 is not a
        # weight, it is a POINT SIZE, and 89px is 67pt. Measured, the 600 face
        # is set at 89/55/34px on a 708-wide sheet and at 55/34px on a 440-wide
        # sheet a phone shows near 390 — a real range of 22pt to 67pt, with
        # every one of them under half the cut they were being served.
        #
        # The 34px end broke visibly. Fraunces' 144pt cut draws the diagonal of
        # a "4" as a hairline; at 34px, and at 55px on a phone, that hairline
        # lands sub-pixel, the counter never closes, and the figure collapses
        # to a stem with a floating crossbar. m-6b-automl's hero "44" read as
        # two hooks in both themes, and so did every desktop numeral in the
        # same face at 34px — plate-6b's "/44" and "29", plate-1's "97.01".
        # Checked by rendering the shipped plates with each candidate instance
        # swapped in, at 708 and 390 CSS px, at device-pixel-ratio 1 and 2, in
        # both themes; not by looking at outlines.
        #
        # Prose survives what a figure cannot. A hairline lost inside a word is
        # repaired by the word's shape; a hairline lost inside a numeral is the
        # difference between 44 and something that is not a number. That is the
        # whole reason the two serif instances now hold DIFFERENT optical sizes
        # and neither is a compromise — see the two build() calls at the bottom.
        axes = {a.axisTag: a.defaultValue for a in font["fvar"].axes}
        axes.update({"wght": wght})
        if "opsz" in axes:
            if opsz is None:
                raise SystemExit(
                    f"{out.name}: {src.name} has an opsz axis and this call "
                    f"states no optical size. Pick one from the rendered size "
                    f"of the text it sets — see the note in build().")
            axes["opsz"] = opsz
        for tag, v in (("SOFT", 0), ("WONK", 0)):
            if tag in axes:
                axes[tag] = v
        font = instancer.instantiateVariableFont(font, axes)
    if metrics:
        # Gelasio matches Georgia's ADVANCES but not its vertical metrics
        # (hhea 1900/-700 vs Georgia's 1878/-449, a 1.27em line box against
        # 1.136em) — tall enough that the two serif lines set 42u apart, fine
        # under Georgia, overlapped under Gelasio. The page's serif geometry
        # was authored against Georgia, so the subset carries Georgia's
        # verticals. Baked into the font rather than CSS ascent-override,
        # which Safari does not support. All three metric sets are pinned to
        # the same values so no renderer's choice of table changes the box.
        asc, dsc = metrics
        font["hhea"].ascent, font["hhea"].descent, font["hhea"].lineGap = asc, dsc, 0
        os2 = font["OS/2"]
        os2.sTypoAscender, os2.sTypoDescender, os2.sTypoLineGap = asc, dsc, 0
        os2.usWinAscent, os2.usWinDescent = asc, -dsc
    opts = subset.Options(flavor="woff2", hinting=False, desubroutinize=True)
    if features is not None:
        # JetBrains Mono ships programming ligatures; their GSUB closure
        # doubles the subset for glyphs no plate can ever form. Monospace
        # also has no kerning worth keeping. Gelasio keeps its defaults —
        # the serif voice is the one place kerning is part of the design.
        opts.layout_features = features
    ss = subset.Subsetter(opts)
    ss.populate(text=chars)
    ss.subset(font)
    # fontTools stamps head.modified from the CLOCK on every save, because
    # TTFont defaults recalcTimestamp=True. So two builds of identical inputs
    # differ in bytes, the 32 plates that embed this subset as base64 differ
    # with them, and "did that change anything?" stops being answerable by
    # looking — which cost real time this month, spent hunting a fontTools
    # version difference that did not exist. Set on the object about to be
    # SAVED and not on the TTFont(src) above: instancing returns a new font and
    # the flag would not have survived the assignment.
    font.recalcTimestamp = False
    font.save(out)
    # ── DID THE GLYPHS ACTUALLY SURVIVE?
    #
    # Nothing asked this until 2026-08-11. plates.py has a check named for
    # charset coverage and it compares the characters a plate DRAWS against the
    # declarations in charsets.py — two Python constants agreeing with each
    # other. It never opens a font. So the one failure that matters here — a
    # character declared, requested, and absent from the binary because the
    # SOURCE face has no such glyph — was invisible to every gate in the
    # repository, and would reach a reader as a silent fallback: one letter of
    # a hero numeral set in Georgia, measured by the gate in Georgia, and
    # passing.
    #
    # Re-opened from disk rather than asserted against `font` in memory, so it
    # verifies what LANDED — the woff2 round-trip included — instead of what
    # was asked for. An in-memory check would have agreed with the request by
    # construction, which is the shape of the check it replaces.
    #
    # SCOPE, stated rather than implied: this file is not run by CI — plates.py
    # is deliberately stdlib-only so the workflow needs no pip step, and
    # fontTools lives here. So this fires when a subset is BUILT, not on every
    # push. That is the right place and not a compromise: the defect it catches
    # can only be introduced by building a subset, which is when it runs. It
    # would not catch a committed woff2 corrupted by hand, and nothing here
    # claims otherwise.
    #
    # Falsified before being trusted, the way this repository requires: built
    # with the real charset (clean, 41/41) and then with one CJK character
    # appended, which raised. Both halves run, because a probe that fails for a
    # broken harness proves nothing.
    written = TTFont(out)
    have = {chr(c) for t in written["cmap"].tables for c in t.cmap}
    written.close()
    missing = sorted(set(chars) - have)
    if missing:
        raise SystemExit(
            f"{out.name}: {len(missing)} declared character(s) are NOT in the "
            f"built subset — {''.join(missing)!r}. Declared in charsets.py, "
            f"requested from {src.name}, and absent from the binary: the "
            f"source face has no glyph for them. They would render as a "
            f"platform fallback.")
    # ── AND IS THE BUILD ACTUALLY REPRODUCIBLE?
    #
    # A determinism flag with nothing asserting determinism is a claim with no
    # gate behind it. TWO assertions, because the obvious one turned out not to
    # work and was nearly shipped as though it did.
    #
    # The obvious one is second below: build the same inputs again and require
    # byte identity. Falsified with the flag REMOVED, it passed — three times.
    # A subset takes 0.3s and head.modified has one-second resolution, so both
    # builds land in the same second and stamp the same clock. It is not a check
    # of the timestamp at all; it is a check of everything else that could vary
    # (set iteration under a different PYTHONHASHSEED, dict order, a temp path
    # leaking into a table), which is worth having and is not what it looked
    # like. Naming that here rather than letting the next reader assume.
    #
    # So the timestamp gets its own, and it is exact rather than probabilistic:
    # the written file must carry the SOURCE face's modification date. With the
    # flag that holds by construction; without it the value is the clock and
    # differs on every run, so this fires every time instead of almost never.
    # The four subsets committed today PREDATE this flag and carry a clock
    # stamp, so the next real subset build will change their bytes once — and
    # the 32 plates that embed them with it — before settling. That is stated
    # here rather than absorbed by rebuilding them now, because a rebuild would
    # churn 36 published files for a timestamp and hide the actual change the
    # next contributor makes inside it. Deterministic from that build onward.
    written_modified = TTFont(out)["head"].modified
    source_modified = TTFont(src)["head"].modified
    if written_modified != source_modified:
        raise SystemExit(
            f"{out.name}: head.modified is {written_modified}, but "
            f"{src.name} says {source_modified} — the save stamped the clock. "
            f"Set recalcTimestamp=False on the font being saved; otherwise "
            f"every rebuild churns this subset and the 32 plates that embed it.")
    if _repro:
        twin = out.with_name(out.name + ".repro")
        try:
            build(src, wght, chars, twin, features, metrics, opsz, _repro=False)
            same = twin.read_bytes() == out.read_bytes()
        finally:
            twin.unlink(missing_ok=True)
        if not same:
            raise SystemExit(
                f"{out.name}: two builds of identical inputs produced different "
                f"bytes, and the timestamp is not the reason — that is checked "
                f"above. Something else in this pipeline varies between runs.")
        print(f"{out.name}: {out.stat().st_size:,} bytes, {len(chars)} chars at "
              f"wght {wght}, all present in cmap, byte-identical on rebuild")


# ── 2026-08-08: the faces are the PORTFOLIO's now.
#
# This page and Portfolio-2.0 are one body of work and were set in two
# different typefaces. They are not any more: the profile takes the Daylight
# Study's own faces, subset through this same pipeline.
#
#   mono 400  Fragment Mono — still registered as family 'M', because
#             gate.mjs:115 checks the family BY NAME. Its advance is 618/1000,
#             not JetBrains' 600/1000, so gate.mjs's REF moved 448 -> 459.52
#             in the same commit; see the derivation written there.
#   bold 600  Fraunces — replaces the mono-600 hero face outright. The heroes
#             (6.4x, 3.5x, 97.01%, 0.979, 15/44, 57.8M, the 89px "B only") are
#             the emotional centre of every plate, and in Fraunces on paper
#             they ARE the portfolio. Registered as family 'S' weight 600.
#   serif 400 Fraunces — the serif voice, same family at 400.
#
# Gelasio and both JetBrains subsets are retired. Georgia's vertical metrics
# went with Gelasio: Fraunces is the authored face now, not a stand-in for a
# platform font, so there is nothing to be metric-compatible WITH. The
# `metrics` parameter above is kept because it is the record of why that
# override ever existed.
#
# Source: Portfolio-2.0/public/fonts — already latin-subset woff2s, which
# fontTools re-subsets happily. Measured result: every plate got SMALLER
# (Fragment Mono's subset is half JetBrains', and Fraunces' beats Gelasio's).
FONTS = SRC if len(sys.argv) > 1 else \
    pathlib.Path.home() / "Documents/Projects/Portfolio-2.0/out/fonts"

build(FONTS / "fragment-mono-latin.woff2", 400, MONO_CHARS,
      ROOT / "mono-subset.woff2", [])
# opsz 48 — the FIGURES. This face sets the claim figures and their units and
# nothing else, from the 89px "B only" down to a 34px unit a phone renders near
# 30px (22pt). 48 is the largest optical size at which the smallest of them
# still reads: at 72 the diagonal of a "4" is faint again at 34px in the light
# theme. It is not pushed lower because the largest use pays for it — rendered
# side by side at 89px, opsz 28 has lost most of the modulation 48 keeps and 9
# is plainly book weight enlarged. Both ends were checked by rendering the
# shipped plates with the candidate instance swapped in, at 708 and 390 CSS px,
# in both themes; neither was judged from an outline. A compromise across
# 22-67pt, stated as one.
build(FONTS / "fraunces-latin-var.woff2", 600, BOLD_CHARS,
      ROOT / "serif-600-subset.woff2", opsz=48)
# opsz 144 — the HEADLINE, and still right. The 400 face sets one thing: the
# 34px centred serif line on the title page and on the colophon. Both plates
# carry NO 600 face at all (head() drops it — they have no hero and no .sub),
# so the two optical sizes never meet on one sheet and no reader sees the
# family speak in two voices. At 34px, as prose, the display cut is doing the
# job a display cut exists for; the thesis is the most important sentence on
# the page and 144 is what makes it look set rather than typed.
build(FONTS / "fraunces-latin-var.woff2", 400, SERIF_CHARS,
      ROOT / "serif-subset.woff2", opsz=144)
# The text voice, added round 25 — see the note over TEXT_CHARS in charsets.py.
# No `features=[]`: kerning is part of a serif's design, the same reason Gelasio
# kept its defaults. No `metrics` override either — that parameter exists
# because Gelasio had to match Georgia's box, and Newsreader is the authored
# face here, not a stand-in for a platform font. Its file is already a static
# "Newsreader 16pt" Regular instance (no fvar), so build()'s instancing branch
# is skipped and the optical size stays the TEXT one — which is the whole
# point, and why Fraunces could not take this job: both its instances are
# pinned above 48, and the text voice is set at 13-21px.
build(FONTS / "newsreader-latin-var.woff2", 400, TEXT_CHARS,
      ROOT / "text-subset.woff2")
