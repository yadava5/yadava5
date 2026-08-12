"""The three embedded faces' character sets — the single source of truth.

subset-fonts.py builds the woff2 subsets from these; plates.py asserts at
build time that every character a plate draws is covered by the face that
will render it. A glyph outside its subset falls back to a PLATFORM font
silently — that is how the comma in the 34px headline "10,453" once shipped
in Menlo on macOS and DejaVu Sans Mono on Linux.

BOARD (2026-08-12): the faces are Syne 800 (display, family 'D') and
Commissioner 400/600 (text and labels, family 'T'), Commissioner instanced at
FLAR 40 — see subset-fonts.py for why the axis is pinned there. The mono,
serif and text faces of the paper design are retired with it; there is no
mono on this page at all, because nothing on it quotes a machine artifact
whole. The day a plate does, the face comes back through this file first.
"""
# → is DELIBERATELY ABSENT from every set, same reason as always: an arrow
# drawn as a glyph is a different mark per fallback font. On this page flow is
# drawn — the buses carry it — so no label should ever need the character, and
# leaving it out turns "someone typed an arrow" into a loud build failure.
#
# The display voice: section romans, the name, and the claim figures
# (6.4×, 3.5×). Caps and digits only, plus the marks of a figure — a display
# face that suddenly needs lowercase is a label wearing the wrong class.
DISPLAY_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .·×—–-&’"
# The text voice, Commissioner 400: every sentence on the board. É/é ride for
# RÉSUMÉ/résumé; @ for the email the hero prints.
TEXT_CHARS = ("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
              " %()+,-./:;=?!@·×—–’&_Éé")
# The label voice, Commissioner 600: eyebrows, port names, bus tags. Set in
# caps almost everywhere, but it keeps the lowercase so an emphasis run inside
# a sentence ("not beaten") can take weight without changing face.
LABEL_CHARS = TEXT_CHARS
