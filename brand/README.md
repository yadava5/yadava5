# The Waymark — ayush-yadav.com

The portfolio's mark: a Fraunces capital **A** threaded onto the site's red
line. The A is extracted from the portfolio's own font binary
(`fraunces-latin-var.woff2`, instanced at opsz 9 / wght 600 / WONK 1) and
converted to a path — no font dependency, nothing to fall back. Its crossbar
contour is removed and replaced by the clay thread at the crossbar's exact
band, running off both edges of the frame.

It is the site's thesis drawn as a letter: *"Traveller, there is no road —
the road is made by walking."* The thread is the road; the initial stands on
it like a station; the live version walks the road in once per arrival.

## Files

| file | use |
|---|---|
| `mark-day.svg` | in-page mark on the day paper (`#f2e4c9`) — masthead, footer |
| `mark-night.svg` | in-page mark on the night paper (`#43372f`) |
| `favicon.svg` | browser tab icon; adapts to light/dark via `prefers-color-scheme` |
| `favicon-live.svg` | animated tab icon: thread draws in once (1.5 s), then still |
| `favicon-16.png` `favicon-32.png` | PNG fallbacks for browsers without SVG favicons |
| `favicon-512.png` | web app manifest icon |
| `apple-touch-icon-180.png` | iOS home screen (square corners — iOS masks it) |
| `build.py` + `fraunces-latin-var.woff2` | build inputs; regenerate with `python3 build.py` (needs fontTools) |
| `proof-sheet.png` | the mark at 512 and honestly at 16, day and night |

## Construction

512 × 512 canvas.

- Cap height **320** (62.5% of canvas); baseline at **y = 412**; letter
  centred horizontally.
- Thread: **44 px** band centred at **y ≈ 294** — the centre of the glyph's
  own crossbar contour (font units 463–570 on a 1400 cap), so the thread *is*
  the crossbar. It bleeds to both edges; that is the point. 44 px ≈ 1.4 px at
  a 16 px favicon — the survival floor; do not thin it.
- Tile corner radius **56** (11%) on the favicon variants only.
- Paint order: paper, thread, letter — the ink always overprints the road.

Clear space (untiled marks): at least 0.25 × rendered height above and below.
The sides need none — the thread is designed to run to, or past, the
container's edges. Do not re-add a crossbar, and do not set the letter in a
live font; the path is the mark.

## Palette (measured, WCAG / APCA on its own paper)

| role | day | night |
|---|---|---|
| paper | `#f2e4c9` | `#43372f` |
| ink | `#26231c` — 12.5:1, Lc 87 | `#f6efe2` — 10.1:1, Lc 90 |
| thread (clay) | `#c4532e` — 3.6:1, Lc 56 | `#e08a5f` — 4.4:1, Lc 43 |

These are the site's live tokens (`--ink`, `--thread`), not approximations.
If the site's palette moves, regenerate rather than recolour by hand.

## Wiring the `<head>`

```html
<link rel="icon" href="/favicon.svg" type="image/svg+xml" sizes="any">
<link rel="icon" href="/favicon-32.png" type="image/png" sizes="32x32">
<link rel="apple-touch-icon" href="/apple-touch-icon-180.png">
<meta name="theme-color" content="#f2e4c9" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#43372f" media="(prefers-color-scheme: dark)">
```

For the live tab icon, point the first line at `/favicon-live.svg` instead.
Firefox plays it (one draw per load, then still); Chromium and Safari render
the finished mark. The animation is CSS-only, honours
`prefers-reduced-motion`, and its base state is the completed mark — any
renderer that ignores the CSS shows the finished logo, never a blank.

PNG regeneration (paths only, so librsvg is safe here):

```sh
python3 build.py
rsvg-convert -w 16  -h 16  _raster-day.svg    -o favicon-16.png
rsvg-convert -w 32  -h 32  _raster-day.svg    -o favicon-32.png
rsvg-convert -w 512 -h 512 _raster-day.svg    -o favicon-512.png
rsvg-convert -w 180 -h 180 _raster-square.svg -o apple-touch-icon-180.png
```
