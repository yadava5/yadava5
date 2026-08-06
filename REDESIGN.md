# REDESIGN — the plates become paper

Round 19. Branch `design/plate-refresh`. `npm test` green (build → gate →
motion → claims), `build/mutations.mjs` 12/12 caught.

## What changed

**The cards are gone.** Every figure is now transparent ink drawn directly on
GitHub's own canvas (#0d1117 dark, #ffffff light) — no slab, no border, no 4u
accent bar. This is the critique's direction B ("the ledger"): the page reads
as one typeset technical report whose figures sit in the prose, not as ten
pasted cards. What ties the figures together is a single repeated device, the
**frontispiece** — a 16px claim at the left, the chapter rail at the right,
one hairline rule — at the same y on every figure. Both of the client's
sentences are answered structurally: the accent bar (the thing that made them
cards) and the travelling scan hairlines (the thing that made them unrefined)
no longer exist anywhere in the set.

**Stillness is the default.** The old doctrine — "never still", enforced by a
raster gate demanding pixel change per sample — produced seven carrier
hairlines, four of which periodically struck through text. Inverted: a plate
now animates only where the motion performs the claim beside it. Five gestures
survive: Glyph's pen draws the 299 (fast now — a stroke, not a reveal),
jetpack's window rotates inside its bound, Cadence files the chip (with a real
landing), Applied walks one refused message to the human, AutoML's phase clock
routes the tools. Five figures are still by design: thesis, work, the refusal,
the colophon — and the mobile set, as before.

**Dynamic range.** Heights were 614/566/576/537/545/532/570/660/640/269 —
eight of ten inside a 130u band. Now 640/584/596/542/468/554/700/660/638/356.
Cadence dropped a week of empty calendar to become the small figure (468) and
its 36-vs-12 line finally has the floor; **the refusal is the broadside**
(700) and the only place the 64px hero face is spent on a word: `B only`.

**Per-plate:** Applied was rebuilt from scratch (labels inside the layers,
envelopes that read as mail, exactly one moving object); the thesis contact
sheet got caption anatomy (more leading, dimmer stack line); the serif now
closes the bracket it opens — the colophon answers the thesis in the same
face: *"If a number here is wrong, / it is wrong in public."*

**Palette re-measured, not carried over.** The ground really changed
(#0A0A0B → #0d1117, #F6F7F8 → #ffffff), and two dark values that passed on the
old slab fail on the new canvas: RULE/ROW #5A606A measured 2.99:1 (3:1 floor)
→ #5D636D (3.13:1); INK3 #767B84 measured 4.45:1 (4.5:1 text floor) → #7A7F88
(4.70:1). Every other value re-verified against its own canvas; the surviving
translucent uses re-computed (worst: light amber .89 → 4.15:1, non-text).

## The five corrections (all landed, all re-derived)

1. **The false bar.** Work plate's "32% naive" fill was RULE-on-RULE — 1.00:1,
   a 100% bar under a 32% label, second recurrence of the same defect. Fixed
   architecturally: tracks are hollow (WIRE frames), fills are solid INK2, so
   fill-vs-track can never again be two similar greys; every width is
   `300*frac` from the value beside it. The compliance bar was checked too —
   290.16/300 for 96.72%, correct, and its 3.28% gap is now visible inside
   the hollow frame.
2. **Applied §V, unmerged branch** — re-authored: merged 2026-08-03 via
   `d349f02f`, no PR; `main` carries `ml/` and both ONNX artifacts at the
   quoted bytes. The page now tells the merge story as its own kind of story
   (a silent state change the pins exist to catch). The `applied`/`applied-web`
   two-source split is **collapsed**; both byte counts cite `main` at
   `5b895d8d…` (sizes verified via contents API before re-pinning).
3. **Applied §V, "exactly one line of prose"** — replaced with the stronger
   true claim: 0.9583 still has *no evaluation artifact*, and
   `test_evaluate_classifier_layer_guard.py` now enforces the rules-vs-cascade
   distinction that used to survive only as a sentence.
4. **AutoML §VIII, `--network none`** — never true. Plate, desc and prose now
   name the real mechanism: a Docker network created with `--internal` (no
   gateway, no route out), noting the repo's own stale comment vs its test.
5. **LifeQuest §VII, "no unit-test suite"** — replaced with the sharper truth:
   a real suite exists (16 cases in `packages/schemas`, new derived claim row
   `lifequest.schema_tests`) **and CI does not run it**. Plus the two Zod
   precisions (two of six controllers import the package; Zod 4 vs Zod 3).
6. **Cadence §VI** — the README no longer contradicts itself: production
   connects as the owner role (`BYPASSRLS`), RLS is staged; and the cutover
   understatement is fixed — proven through the production Supavisor pooler as
   a `NOSUPERUSER NOBYPASSRLS` role, one `DATABASE_URL` swap remaining. "The
   guard sits in the query" is now drawn honestly: filled marks (in the query —
   read ×6, delete ×3) vs hollow marks (checked first, then `DELETE WHERE id`),
   with a legend, plus the conditional-on-`userId` caveat in prose.

**Re-pinned** all six repos to the audited heads (`$repin_note` in
claims.json); `glyph.msimd128_line` 279 → 330 (`CMakeLists.txt:330` in prose).
New material used: the Cadence unreachable-handlers story ("failed closed",
§IV, with the fix commit linked and a `README.md:401` exemption), Glyph's own
README retraction. Passed over: Glyph's coverage %, jetpack's tooling commits —
they didn't earn plate space.

## Gates re-authored (deliberately, in this change)

- **motion.mjs** — inverted. Was: ≥25% of intervals alive, no dead run over
  2.4s. Now: a plate with no animations passes ("still by design"); a plate
  *with* animations must show its gesture in ≥3 sampled intervals at the 0.2%
  raster floor — an invisible animation is instrument-food and fails. Rasters
  over the real canvas per theme (transparent plates over a white test page
  would blind the diff for the dark set).
- **gate.mjs checks 13/17** — the 35% floor, 2.4s ceiling and the
  "has no animations at all" failure are deleted; what remains is
  "declares animations that never move anything" (geometry side of the same
  rule). Reasoning written into both files.
- **mutations.mjs** — kept meaningful: retired probes for the two deleted
  checks, added probes for the new check ("a declared animation never moves
  anything") and for check 14 (stagger). Re-targeted four probes whose
  anchors the redesign moved. All 12 fire.

The new motion gate immediately earned its keep against my own first draft: it
measured the refusal's strike-wave at 0/67 visible samples and the colophon's
rule-draw at 1/127, so both plates became still (recorded in their
docstrings), Cadence's chip landing was re-tuned from a six-sample sub-threshold
fade to a visible arrival, and Glyph's pen went from 17% to 4% draw time.

## Deliberately kept

The 299 grid (now a still exhibit — no read head, no bobbing), the
single-stroke digit face, the lone serif voice (now a two-plate bracket), the
jetpack table with "not beaten", every honesty device verbatim ("RULES LAYER
ONLY", "ATTESTED", the refusal's two footnotes, RETURNS NOTHING),
one-hue-per-system taught once on the contact sheet, the rail (as the right
end of the frontispiece), the alt/desc/README single-sourcing, per-theme
builds, `op()`, and the whole claims machinery — now at 53 derived numbers.
No JavaScript, no server: the boast stands.

## What I'd do next

- The six logos at 28u are the only place the hues appear together; a reader
  who skips the thesis meets each hue cold. A one-line legend under the
  colophon would close that loop.
- `IMPACT` in plates.py is now an unused curve — delete it or find the gesture
  that needs it.
- The mobile set is honest but plain; the accent rule under the kicker is the
  only hue it carries. It could take the frontispiece proper.
- gate.mjs's bottom-margin uniformity (check 12) is satisfied at ≤2u by
  authoring discipline (last baseline at H−30, say-enders at H−32); a helper
  in plates.py could make that impossible to get wrong instead of merely
  checked.

## Note for the reviewer

`node_modules/.shoot/{shoot,sheet}.mjs` were re-pointed at this worktree's
assets to render review shots (as instructed). `node_modules` is shared with
the parent checkout via symlink, so flip `REPO` back before rendering the
parent's assets.
