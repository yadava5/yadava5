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

from charsets import MONO_CHARS, BOLD_CHARS, SERIF_CHARS

ROOT = pathlib.Path(__file__).resolve().parent
SRC = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT


def build(src: pathlib.Path, wght: int, chars: str, out: pathlib.Path,
          features: list[str] | None = None,
          metrics: tuple[int, int] | None = None) -> None:
    font = TTFont(src)
    if "fvar" in font:
        # Pin EVERY axis, not just weight. Fraunces declares four — wght, opsz,
        # SOFT and WONK — and instancing one of them leaves a variable font
        # whose remaining axes resolve to a default the SVG never states. opsz
        # goes to the display end (these are 34-89px heroes, not body copy),
        # SOFT to 0 and WONK to 0: the plates are drawings, and a wonky leg on
        # a figure that sits beside a hairline rule reads as a misprint.
        axes = {a.axisTag: a.defaultValue for a in font["fvar"].axes}
        axes.update({"wght": wght})
        for tag, v in (("opsz", 144), ("SOFT", 0), ("WONK", 0)):
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
    font.save(out)
    print(f"{out.name}: {out.stat().st_size:,} bytes, {len(chars)} chars at wght {wght}")


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
build(FONTS / "fraunces-latin-var.woff2", 600, BOLD_CHARS,
      ROOT / "serif-600-subset.woff2")
build(FONTS / "fraunces-latin-var.woff2", 400, SERIF_CHARS,
      ROOT / "serif-subset.woff2")
