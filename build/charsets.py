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
# The TEXT voice — Newsreader, and the reason it exists.
#
# Until round 25 this page had no text face. `text{font-family:'M',…}` made
# Fragment Mono the DEFAULT, so every label, eyebrow, caption, credit and
# statement on all 36 plates rendered in it and the serif only ever reached
# the display numerals. Nothing was chosen; mono was where everything landed.
# The client's word for it: "you love to use mono fonts everywhere".
#
# Monospace used everywhere destroys its own signal — if all of it is mono,
# mono means nothing. It now means one thing: a machine artifact quoted whole
# (a path, a query, a hex readout, a flag string, a bare identifier), carried
# by the opt-in `.mach` class. Prose that merely MENTIONS an identifier stays
# in the text face, which is what the README already does with backticks.
#
# Newsreader is not a new choice, it is the portfolio's own text face —
# Portfolio-2.0/out/fonts has carried it all along and this page never adopted
# it. So the 2026-08-08 "one body of work" unification is completed here
# rather than diverged from: Fraunces display, Newsreader text, Fragment Mono
# machine. Same inventory as MONO_CHARS, since the same strings are set.
TEXT_CHARS = MONO_CHARS
