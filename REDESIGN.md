# REDESIGN — questions, answered in motion

## Copy pass — every line of text, before ship

The brief: no exaggeration, no filler, no page arguing with itself. Every
number unchanged, every anchor updated in the same edit as its sentence.
Prose went **1,908 → 1,675 words (−12%)**; the whole file 2,933 → 2,671;
alt text 837 → 808. No drawn text changed, so no figure moved.

What was cut, and why:

- **The page's autobiography.** Three places narrated the page's own past
  errors: Glyph's "the page you are reading once said otherwise", AutoML's
  43-word account of the retracted `--network none` claim, VisualAssist's
  "has sold Swift from the start". The corrected facts all stay; the
  changelog of how they got corrected lives in claims.json, where it
  already was. A hiring page carries its conclusions, not its revisions.
- **Qualifications of qualifications.** Applied's evaluation paragraphs
  went ~180 → ~110 words: each caveat (2 mistakes, balanced set, rules
  layer alone, 0.9583 has no artifact) is now stated once, cleanly.
  Deleted: the macro-vs-weighted-F1 aside, "the rules-only baseline
  reproduces it to the last digit" (circular — the deterministic profile
  *is* the rules baseline), the three-decimals meta-commentary, and the
  per-claim "re-derived from the pinned commit" reassurance the intro
  already makes globally. jetpack lost "an 8% spread wider than either
  run's own interval" — the 6.89→6.38 disclosure itself stays, with both
  endpoints still deriving.
- **Inventory numbers in §I.** 1,153 users, 66 dashboards, 35-field,
  37-month: qualifier-of-qualifier detail on figures that are already
  attested-only. Their four attested rows are deleted with them, plus
  glyph.correct (9,701 — redundant with 10,000 − 299). 52 numbers still
  re-derive.
- **§I's warrant paragraph halved** — it restated the intro and the
  stamped plate; one sentence now carries it.
- **The seven AutoML set names** left the prose (the anchored phrase
  "through seven exported sets" survives); the enumeration stays in the
  alt text and on the dial's rim, which is where a reader meets it.
- **Two alt strings tightened** (Cadence −14 words, Applied −11), edited
  identically in plates.py and the README; alt.json regenerated;
  gate.mjs check 9 re-verified both directions. The glyph desc is
  untouched — the mutations probe keys on "which means 299 wrong".

Kept on purpose: every load-bearing caveat (ATTESTED framing, the
intrinsic jetpack loses to, RULES LAYER ONLY, BYPASSRLS staging, the tags
test, task-lists' missing regression test, the licence position, Shree
Chaturvedi's credit, the lidar reason), every number that survives, both
run-to-run spreads, and all contact affordances as markdown links.

Flagged for the client rather than decided silently: the deleted
"commercial use needs no arrangement with either of us" clause (a real
legal statement, not filler), the deleted `test_evaluate_classifier_
layer_guard.py` name, and the three autobiography cuts above — any can
come back with one sentence.

Gates: plates.py build, gate.mjs, motion.mjs --gate, claims.mjs — all
green after the pass (52 derived, 14 attested). mutations.mjs not re-run
this pass (no probe anchor was touched); run it before ship.

---

## Round 22 — the motion is the number

Built from round 21's tree, against the live-observation report (nine plates
watched and scrubbed in Chrome, both themes). The governing finding was
jetpack's: its dash speed encodes throughput exactly — 6.38, 2.80, 9.25, the
printed numbers — and it ranked first of nine because of it. Round 22 ports
that principle: **wherever a figure has a number, the motion now carries it**,
and a carrier that means nothing was treated as decoration to be replaced.

### The three mandatory reworks

**Work** (was ranked 8/9; two animations, one camouflaged as a table rule).
The scan is now an instrument — a 1.6u hairline one voice brighter than the
row rules, led by a 26u solid INK index head — and it has a job: as it
crosses each of the five value rows, that row's amount *presses* (6% scale
about its fixed right edge) and its label lifts from INK2 to full INK with a
slow afterglow — the audit, tallying. Crossing times are derived from the
scan's own keyframes, so reader and read share one clock by construction.
The two linkage bars run jetpack tick-streams at rates proportional to
**99.6 vs 32** (periods 0.430s / 1.339s — the 3.1x the caption states), and
the preserved bar is full INK against half-ink naive (the light theme's
black-bar weight, ported to dark). The stamp rides the same clock: when the
rule clears the closing double rule, ATTESTED re-inks — lifted, faded to
0.3, pressed home — never absent (the round-21 blink measured as a glitch).

**Cadence** (motion contradicted the claim: 92% of the loop showed A and B
identical). The rest state now *states* the refusal: tenant A's rows are
redaction — black ink in light, and in dark a **void** (#161B22 field held
by a WIRE edge, because a black bar on near-black paper vanishes; the
biggest theme delta of the live pass, closed). Tenant B's rows carry two
record-lines with a continuous emerald dash-stream flowing through them —
B's data returning, always; A's never. Gesture: the redactions are
re-struck once per loop — each bar lifts *faded* (the row is simply blank,
which is what the database sent), holds blank half a second, then wipes back
left-to-right in a 60ms cascade down the column. The scan gains the same
index head as Work, in this section's emerald.

**Glyph** (91% dead; the headline snapped out of existence between frames).
The pen now writes over a **half-ink ghost** of itself (op 0.55 — measured
3.52:1 dark / 3.66:1 light against the slabs), and the stroke fades before
its dash-offset resets, so "3.5" is never absent. The typeset x is deleted;
the multiplier is **two pen strokes in the same hand**, drawn fourth and
fifth in the same 150ms wave. The 500-digit field wakes: the 220
merely-wrong labels are grey ink (currentColor), the 79 the net was *sure*
of stay heavy amber — hue and weight, so the amber count on the field IS
the 79 — and the nib now runs a closed boustrophedon circuit of the whole
sheet (up the margin, along every clear band between rules), lifting the
row it reads from grey to full ink. Its circuit is 18.2s = exactly two
headline loops, replacing the incommensurate 24.7s, so the two hands share
a clock.

### The fixed bug

**Colophon:** the six product marks counter-rotate about their own centres
(`transform-box:fill-box`), so they orbit upright instead of spending half
of every 31s cycle upside down. Same idiom as every other rotating element.

### The other six — critique, and what was done about it

- **jetpack** (1/9 — the model). Weakest mark: the two loser bars degraded
  to three dots and the drain left a 6.75%-per-block hole read live as a
  dropped frame. Dashes densified 12u→6u pitch (speed encoding untouched —
  offsets still drift at the measured rates), drain tightened to ~3.5%. A
  fifth block was tried and is *structurally impossible* — any re-entrant
  after a 20%-spaced drain must descend faster than its pursuer, and the
  collision gate caught the 5-up schedule riding 2u inside the block ahead.
  Four blocks, margins re-derived per pursuer pair (10.4/5.5/4.4/2.6u, all
  opening). The critique's ask is met by the shorter hole, not the fifth
  block; documented in the plate.
- **Applied** (2/9 — best narrative, timid drawing). Walls 2u→3u (a full
  weight above the dashed screens — the impassable edge drawn as one);
  message tokens 14u→18u; each chute ends at a **terminus bar** the exiting
  message visibly arrives against before fading (the live pass: "paths to
  nowhere"); and the human *reacts* — a 3.5u rise to receive, on the same
  clock as the refused message's walk, so the nod cannot miss the handover.
- **VisualAssist** (3/9 — causality was fake). The pulses were solved
  against a sine; the sweep runs the DRIFT bezier — that mismatch is exactly
  the live finding "points pulse with the beam elsewhere, worst at extreme
  bearings". Crossing times are now solved by inverting the actual bezier
  (bisection on the y-polynomial, x-polynomial to time). The cone gets a
  radial falloff (dense at the sensor, thin where the points live; light no
  longer floods at 0.64 alpha). And the *answer* half of the claim is drawn:
  two audio arcs at the phone's ear flash pink at **every** crossing — one
  detection, one utterance — colour animation, so the authored frame stays
  the finished frame.
- **AutoML** (5/9 — no headline, needle adrift). **15/44** is set at hero
  weight with "TRAVEL WITH THE MODEL" under it — the only section that had
  no big number now leads with its fraction. The needle's rotation origin
  was left to the renderer's legacy SVG default; it now uses the shared
  fill-box idiom with a zero-ink balance path pinning the origin to the
  dial's axis, and it became a **rim index** (84u→106u, in INK, crossing the
  sector band) because a correctly-centred hub needle physically crosses the
  150u hub box at horizontal angles — the gate proved it. Sector arcs
  10u→13u. The five sub-two-pixel tray animations are deleted: motion below
  the threshold of vision is pure compositor cost.
- **Thesis** (9/9 — zero gestures in 270 samples, on the first thing anyone
  sees). The index is now *read*: rows I→VII light in order — leader to full
  INK, numeral takes its section's hue, mark swells 25% — and once per 11.9s
  cycle the whole index rings together, the one chord on a quiet title page.
  All colour-and-scale; nothing travels; the leaders' drift and the
  ornament stay. Gestures: 0→64 of 270 (dark), 11→95 (light).
- **Colophon** (6/9). Beyond the counter-rotation fix, left alone — it is a
  footer. The observer's deeper question (is a revolving device the right
  emblem for "checked in CI"? a check *passing* might say more) is real but
  is a content decision, flagged for the client rather than taken.

### Measured, before → after (desktop, dark; gesture column of motion.mjs)

| plate | alive | gesture before | gesture after |
|---|---|---|---|
| Thesis | 100→100% | 0/270 | **64/270** (light 11→95) |
| Work | 97→100% | 154/159* | **159/159** |
| Glyph | 96→100% | 20/247 (8%) | **60/182 (33%)** |
| jetpack | 100% | 113/113 | 113/113 |
| Applied | 100% | 64/155 | **104/155** (light 59→102) |
| Cadence | 97→100% | 165/171* | **167/171** |
| AutoML | 100% | 28/133 | 28/133 |
| Colophon | 100% | 7/310 | **132/310** (light 309→307) |
| VisualAssist | 100% | 117/117 | 117/117 |

\* honesty note: Work's and Cadence's *before* numbers were already high
because the camouflaged hairline fed the raster metric every interval while
the plate read as dead — the live observation, not this column, was the
true baseline. The rework changed what the gesture *is*, not only its count.
AutoML's count is unchanged: its round-22 gains (headline, arc weight,
needle origin, tray deletion) are legibility gains the raster metric does
not price.

### Gates re-authored this round (reasoning in the files)

- **mutations.mjs, rest-short probe** — re-anchored the way its own pass-3
  note demanded: keyed on the `data-rest-within` attribute with the shift
  computed, instead of a literal x that every redesign is entitled to move
  (the token resize 14u→18u moved 632→630 and would have staled it a fourth
  time).
- **mutations.mjs, moves-nothing probe** — moved from the title page (which
  now carries the index chase, so freezing its two old carriers no longer
  silences it) to the colophon, freezing all three of its animations.
- **gate.mjs and motion.mjs — untouched.** The collision gate caught two
  real defects in this round's first build (the 5-block conveyor overlap,
  the needle/hub crossing) and both were fixed in the design, not the gate.
  12/12 mutations fire; 36/36 plates pass motion; GATE PASSED.

No `desc`, alt, README or claims text changed — the claims machinery is
untouched and `head()`'s cross-theme assertion still holds.

---

## Round 21 (prior) — questions, answered in motion

Round 21. Branch `design/voices`, built forward from round 20's working tree.
`npm test` green (build → gate → motion → claims), `build/mutations.mjs`
12/12 caught, claims.json restructured deliberately (below) — 53 numbers
re-derive from pinned commits.

## The three verdicts this round answers

1. **"very static feel"** — measured, not felt: eight of ten plates were
   frozen 84–100% of their loops. The doctrine is inverted. Every plate now
   carries one slow continuous carrier plus its episodic gesture, and
   `build/motion.mjs` v3 enforces it in pixels (see below). Desktop liveness
   went from a median of ~14% to **96–100% on every plate**.
2. **"highly unpolished"** — the cause was typographic: seven sizes plus an
   off-scale inline 26 in one 708-wide figure. The scale is now
   **13 / 21 / 34 / 55 on the golden ratio** (Fibonacci), one named
   exception: the 89px `B only`. All small text is exactly 13,
   differentiated by tracking and ink, never by a fourth size. The serif
   voice sits on the scale at 34. Desktop and mobile share the ladder.
3. **"the applied was is just trash"** — rebuilt from zero (below).

## The story: "Questions I wanted answered"

The "I don't trust X" motif is deleted. Each section opens as a question in
its README header and the plate performs the answer — including the answers
that went against the author (the intrinsic that wins, the OpenMP build
that is *slower* below a size floor, the best score belonging to the cheap
layer). Content restructure per CONTENT-PLAN: LifeQuest cut, the refusal
merged into Cadence, AutoML moved up to §IV, VisualAssist added as §VII,
frontispiece and colophon shrunk. **Glyph's authorship corrected** — the
net was course-provided (after Nielsen); the page now claims the harder
true thing: someone else's code, made faster, with Shree Chaturvedi
credited on the plate itself.

## Each section: question · form · motion · liveness (dark/light, % of loop alive)

| § | question | form | carrier + gesture | alive |
|---|---|---|---|---|
| 0 Frontispiece | who / what / where in 20s | title page & index — serif thesis, one language line, dot-leadered index teaching six marks and six hues | leaders **drift** toward their numerals; the ornament diamond **turns** (27s) | 100 / 100 |
| I Work | a year of it, and it isn't in a repo | the account book — amounts at the right edge, double rules | an auditor's rule **reads** down the account (15.9s); the ATTESTED stamp **lands** | 97 / 97 |
| II jetpack | is hand-vectorised code actually faster? | the bench sheet — two lanes, each to its own scale, the intrinsic drawn longest | tick-streams **flow** inside every bar at the measured rate (the intrinsic streams fastest); the bounded window runs as a true **conveyor** | 100 / 100 |
| III Glyph | how much faster can you make code you didn't write? | the copybook — 299 true labels on ruled lines; authorship credit on the face | the pen **draws** the answer "3.5" and each digit settles; the nib **laps** the last rules (24.7s) | 96 / 100 |
| IV AutoML | how much should a model be allowed to hold? | the phase dial and sealed vessel | the needle **creeps and swings**, never parked; the generated-Python feed **flows** into the vessel; the tmpfs trays breathe | 100 / 99 |
| V Cadence | can the database refuse, so the code needn't remember? | the redacted disclosure — guard marks, redacted column, the 89px `B only` | the audit scan **reads** the disclosure (17.1s — the plate where the instrument turns inward); the bars **redact** in a wave | 97 / 97 |
| VI Applied | what should a classifier do when it isn't sure? | **rebuilt**: a tapered channel with real walls, screens spanning wall to wall on level leaders, doorway gaps where the chutes leave, a solid 0.85 gate, a drawn human | a phased **stream** of messages falls, is decided, exits; the refused one pauses at the gate and is **walked** to the human, where the still frame also rests it (data-rest) | 100 / 100 |
| VII VisualAssist | can a phone tell you what's in front of you? | **new**: the depth sweep — a drawn phone, a wedge of view, range rings, obstacle points | the sweep **oscillates** (never stalling); rings **drift** outward; each point **blinks exactly when the sweep crosses its bearing** (crossing times computed from the same sine) | 100 / 100 |
| Footer | — | the imprint — serif close, six marks as a printer's device | the device **turns** (31s) inside a drifting dashed ring | 100 / 100 |

Mobile: every card carries a light **running** its accent rule (nine
different periods), 85–96% alive; motifs re-cut (sieve, sweep) to the new
desktop drawings. Mobile enters the motion gate for the first time.

## Gates re-authored (reasoning in each file)

- **motion.mjs v3 — the inversion the round is about.** v1 was a quota and
  grew gate-food; v2 legalised stillness and eight plates froze. v3: no
  still plates; ≥95% of desktop intervals (70% mobile) must clear the
  carrier floor (FLOOR/10 — the round-20 rider's measured band); and each
  loop must read at a glance — ≥3 full-FLOOR bursts **or** a carrier strong
  enough to be the glance (≥90% of intervals at FLOOR/4; the title page
  measures 270/270 there). Mobile measured for the first time
  (scope-widening). Both themes still measured separately.
- **mutations.mjs** — four probes re-anchored to the new compositions
  (the hide-probe to the refused message's 30% hold; the rest-short probe
  to its new rest beside the human; the contrast probe to the new .fine
  tracking; the moves-nothing probe to the title page, whose two carriers
  it freezes both of). All 12 fire.
- **gate.mjs** — untouched. Its collision/frame-zero/contrast checks
  caught nine real defects in this round's first build (fading chips
  half-dim mid-fall, a 2.2:1 chute guide, a queue of trays) and each was
  fixed in the design, not the gate.

## Claims machinery (every number still re-derives)

- LifeQuest rows and repo pin **deleted**; `cadence.handlers` and the
  Vercel cap are prose-only now.
- **Added**: `glyph.dot256_speedup` (3.5×) and `glyph.axpy128_slowdown`
  (6.9× slower) — both derived as ratios from the pinned
  `bench_summary.csv`, answering the section's question in both
  directions; `repos.visualassist` pinned at `b0e6203`, with
  `visualassist.swift_lines` (7,177 over all 38 blobs),
  `visualassist.swift_files` (38, with the tree-API cross-check in the
  note) and `visualassist.workflows` (5).
- `applied.eval_misclassified` (2) now drawn on the plate ("2 MISTAKES").
- Exemptions retired with the content that used them; benchmark case names
  (`/256`, `/128`) exempted with reasons.

## Deliberately kept

The 299 error grid and its pen, the ledger, the dial, the redacted
disclosure and `B only`, the serif bracket (both bookends still the only
centered plates), every honesty device ("RULES LAYER ONLY", the stamp, the
two asterisked footnotes, "not beaten — the reference stands"),
one-hue-per-system (PINK passes from LifeQuest to VisualAssist — no new
colour, nothing re-measured by hand, and check 10 re-measures everything
per build anyway), alt/desc/README single-sourcing, per-theme builds, and
no JavaScript, no server.

## Renders

`scratchpad/v3/` — per-plate dark/light at two loop points,
`SEQUENCE-{dark,light}.png`, `MOBILE-dark.png`.
