"""The three embedded faces' character sets — the single source of truth.

subset-fonts.py builds the woff2 subsets from these; plates.py asserts at
build time that every character a plate draws is covered by the face that
will render it. A glyph outside its subset falls back to a PLATFORM font
silently — that is how the comma in the 34px headline "10,453" shipped in
Menlo on macOS and DejaVu Sans Mono on Linux.
"""
MONO_CHARS = ("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
              " %()*+,-./:=?@·×–—’→")
BOLD_CHARS = " %+,-./0123456789ABDGKLMRSVeiklmnorstwxy×"   # .hero/.sub/.vast/.n
SERIF_CHARS = "abcdefghijklmnopqrstuvwxyzACDFIMSTW ,.’"    # the serif voice
