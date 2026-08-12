#!/usr/bin/env python3
"""Regenerate the three embedded font subsets. Not run in CI — the woff2
files are committed and plates.py only base64s their bytes, so the build
stays deterministic across platforms and needs nothing beyond stdlib.

THE FACES ARE SYNE AND COMMISSIONER (BOARD, 2026-08-12). Fragment Mono,
Fraunces and Newsreader are retired with the paper design — they were the
portfolio's own voice, and "not a copy paste of my existing project" is the
brief. What survives from that pipeline is everything below build()'s
signature: the cmap check, the timestamp pin and the repro twin all exist
because each caught a real defect once, and a redesign is exactly when they
earn their keep.

Why these two:
  * Syne 800 ('D') — the display voice: the name, section romans, claim
    figures. Wide, geometric, a little strange; it reads as silkscreen
    lettering on the board and as nothing on ayush-yadav.com.
  * Commissioner 400/600 ('T') — text and labels. A low-contrast grotesque
    with a FLAR axis; at FLAR 40 the stems flare slightly, which keeps 11px
    caps labels from going pixel-grid sterile. Instanced HERE, at build time,
    because an axis choice left to render time is invisible — Fraunces at
    opsz 144 destroying 34px numerals is this repository's own scar.

Every axis is pinned, not just wght: Commissioner carries FLAR, VOLM and
slnt, and instancing one axis leaves a variable font whose remaining axes
resolve to defaults the SVG never states. VOLM (a rounding gimmick) and slnt
stay 0. A face with an opsz axis and no stated value is a build failure, not
a silent default — that rule survives from the Fraunces incident even though
neither current face carries the axis.

THE FULL NAME TABLE SHIPS. fontTools' subsetter drops nameIDs 13/14 (the OFL
licence text and URL) by default, so every subset this repo published before
2026-08-12 stripped the licence notice off a font whose licence is the reason
we may embed it at all. OFL §1 requires the copyright and licence notices to
travel with any redistributed version; ~1.3 KB per face is what compliance
costs. name_IDs='*' below, and an assertion that 13/14 actually landed —
a fix without a check is how the defect shipped the first time.

Sources (both OFL 1.1, from google/fonts@main):
  Syne[wght].ttf
    https://raw.githubusercontent.com/google/fonts/main/ofl/syne/Syne%5Bwght%5D.ttf
  Commissioner[FLAR,VOLM,slnt,wght].ttf
    https://raw.githubusercontent.com/google/fonts/main/ofl/commissioner/Commissioner%5BFLAR%2CVOLM%2Cslnt%2Cwght%5D.ttf

Usage: python3 build/subset-fonts.py <dir containing the two ttfs above>
Needs: fonttools, brotli.
"""
import pathlib, sys

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

from charsets import DISPLAY_CHARS, TEXT_CHARS, LABEL_CHARS

ROOT = pathlib.Path(__file__).resolve().parent
SRC = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT


def build(src: pathlib.Path, chars: str, out: pathlib.Path,
          axes: dict[str, float], features: list[str] | None = None,
          _repro: bool = True) -> None:
    font = TTFont(src)
    if "fvar" in font:
        # Pin EVERY axis. Start from the font's own defaults so an axis this
        # call does not name still resolves to a value this file can be read
        # to state; then require the two axes history has made dangerous to
        # be named explicitly: wght always, opsz whenever the face has one
        # (a POINT SIZE, not a style — the 144 scar, see the docstring).
        pinned = {a.axisTag: a.defaultValue for a in font["fvar"].axes}
        if "wght" in pinned and "wght" not in axes:
            raise SystemExit(f"{out.name}: {src.name} has a wght axis and this "
                             f"call does not pin it")
        if "opsz" in pinned and "opsz" not in axes:
            raise SystemExit(
                f"{out.name}: {src.name} has an opsz axis and this call "
                f"states no optical size. Pick one from the rendered size "
                f"of the text it sets.")
        unknown = set(axes) - set(pinned)
        if unknown:
            raise SystemExit(f"{out.name}: pins {sorted(unknown)}, which "
                             f"{src.name} does not carry")
        pinned.update(axes)
        font = instancer.instantiateVariableFont(font, pinned)
    opts = subset.Options(flavor="woff2", hinting=False, desubroutinize=True)
    # The OFL fix. The subsetter's default name_IDs keeps {0,1,2,3,4,5,6} and
    # silently drops 13/14 — the licence text and URL — so the notice did not
    # travel with the embedded font. '*' keeps the whole table; the assertion
    # after save() is what stops this regressing to a default again.
    opts.name_IDs = ["*"]
    opts.name_legacy = True
    if features is not None:
        opts.layout_features = features
    ss = subset.Subsetter(opts)
    ss.populate(text=chars)
    ss.subset(font)
    # fontTools stamps head.modified from the CLOCK on every save, because
    # TTFont defaults recalcTimestamp=True. So two builds of identical inputs
    # differ in bytes, the plates that embed this subset as base64 differ
    # with them, and "did that change anything?" stops being answerable by
    # looking. Set on the object about to be SAVED — instancing returns a new
    # font and the flag would not survive the assignment.
    font.recalcTimestamp = False
    font.save(out)
    # ── DID THE GLYPHS ACTUALLY SURVIVE?
    #
    # plates.py's coverage check compares the characters a plate DRAWS against
    # charsets.py — two Python constants agreeing with each other. It never
    # opens a font. So the one failure that matters here — a character
    # declared, requested, and absent from the binary because the SOURCE face
    # has no such glyph — is only caught at subset-build time, which is the
    # only time it can be introduced. Re-opened from disk so it verifies what
    # LANDED, woff2 round-trip included, not what was asked for.
    written = TTFont(out)
    have = {chr(c) for t in written["cmap"].tables for c in t.cmap}
    names = {n.nameID for n in written["name"].names}
    written.close()
    missing = sorted(set(chars) - have)
    if missing:
        raise SystemExit(
            f"{out.name}: {len(missing)} declared character(s) are NOT in the "
            f"built subset — {''.join(missing)!r}. Declared in charsets.py, "
            f"requested from {src.name}, and absent from the binary: the "
            f"source face has no glyph for them. They would render as a "
            f"platform fallback.")
    # The licence must land, not merely be requested — see the docstring.
    if not {13, 14} <= names:
        raise SystemExit(
            f"{out.name}: nameID 13/14 (the OFL notice) did not survive the "
            f"subset — present: {sorted(names)}. The embedded font would ship "
            f"without its licence text, which OFL §1 does not permit.")
    # ── AND IS THE BUILD ACTUALLY REPRODUCIBLE?
    #
    # Two assertions, kept from the previous pipeline with their history:
    # the timestamp one is exact (the written file must carry the SOURCE
    # face's modification date — without recalcTimestamp=False it is the
    # clock and fires every run), and the twin-build one catches everything
    # else that could vary (set iteration under a different PYTHONHASHSEED,
    # dict order, a temp path leaking into a table).
    written_modified = TTFont(out)["head"].modified
    source_modified = TTFont(src)["head"].modified
    if written_modified != source_modified:
        raise SystemExit(
            f"{out.name}: head.modified is {written_modified}, but "
            f"{src.name} says {source_modified} — the save stamped the clock. "
            f"Set recalcTimestamp=False on the font being saved; otherwise "
            f"every rebuild churns this subset and every plate that embeds it.")
    if _repro:
        twin = out.with_name(out.name + ".repro")
        try:
            build(src, chars, twin, axes, features, _repro=False)
            same = twin.read_bytes() == out.read_bytes()
        finally:
            twin.unlink(missing_ok=True)
        if not same:
            raise SystemExit(
                f"{out.name}: two builds of identical inputs produced different "
                f"bytes, and the timestamp is not the reason — that is checked "
                f"above. Something else in this pipeline varies between runs.")
        print(f"{out.name}: {out.stat().st_size:,} bytes, {len(set(chars))} chars, "
              f"all present in cmap, OFL notice intact, byte-identical on rebuild")


SYNE = SRC / "Syne[wght].ttf"
COMM = SRC / "Commissioner[FLAR,VOLM,slnt,wght].ttf"

# Syne's caps do the silkscreen work; no lowercase is requested, so the GSUB
# closure stays tiny. kern rides — 'AV' in the name needs it.
build(SYNE, DISPLAY_CHARS, ROOT / "syne-800.woff2", {"wght": 800})
# FLAR 40 on both weights: one flare for the whole family, chosen at 11-16px
# on the rendered plates (0 is sterile at label size, 70+ reads as a serif
# trying to happen). VOLM and slnt pin to 0 via the defaults.
#
# kern+figure features only. The default closure pulls ligature and alternate
# glyphs no plate can form and costs 3.7 KB per weight (22,560 vs 18,856 B,
# measured); the base64 of every embedded copy pays it again. Kerning stays
# because the text voice runs at 13-16px where 'AV'/'Ta' gaps read.
build(COMM, TEXT_CHARS, ROOT / "comm-400.woff2", {"wght": 400, "FLAR": 40},
      features=["kern", "lnum", "pnum"])
build(COMM, LABEL_CHARS, ROOT / "comm-600.woff2", {"wght": 600, "FLAR": 40},
      features=["kern", "lnum", "pnum"])
