"""The three embedded faces' character sets — the single source of truth.

subset-fonts.py builds the woff2 subsets from these; plates.py asserts at
build time that every character a plate draws is covered by the face that
will render it. A glyph outside its subset falls back to a PLATFORM font
silently — that is how the comma in the 34px headline "10,453" shipped in
Menlo on macOS and DejaVu Sans Mono on Linux.
"""
# → is DELIBERATELY ABSENT. Fragment Mono does not carry U+2192, and a glyph
# outside its subset falls back to a platform font silently — which is exactly
# the live defect on Portfolio-2.0, where ⟶ renders 72% wider than a mono cell
# in a different typeface per reader, 91 times. Here the arrow is drawn by
# arrow() in plates.py as a PATH advancing one tracked cell, so it is the same
# mark for everyone. Leaving the character out of this set turns the
# convention into a loud build failure for anyone who types it in a label.
MONO_CHARS = ("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
              " %()*+,-./:=?@·×–—’")
BOLD_CHARS = " %+,-./0123456789ABDGKLMRSVeiklmnorstwxy×"   # .hero/.sub/.vast/.n
SERIF_CHARS = "abcdefghijklmnopqrstuvwxyzACDFIMSTW ,.’"    # the serif voice
