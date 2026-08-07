#!/usr/bin/env python3
"""Regenerate the three embedded font subsets. Not run in CI — the woff2
files are committed and plates.py only base64s their bytes, so the build
stays deterministic across platforms and needs nothing beyond stdlib.

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
        font = instancer.instantiateVariableFont(font, {"wght": wght})
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


build(SRC / "JetBrainsMono[wght].ttf", 400, MONO_CHARS, ROOT / "mono-subset.woff2", [])
build(SRC / "JetBrainsMono[wght].ttf", 600, BOLD_CHARS, ROOT / "mono-600-subset.woff2", [])
build(SRC / "Gelasio[wght].ttf", 400, SERIF_CHARS, ROOT / "serif-subset.woff2",
      metrics=(1878, -449))   # Georgia's, at the shared 2048 upem
