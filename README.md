<div align="center">
<img src="./assets/plate-0-thesis.svg" width="100%" alt="The thesis plate: Ayush Yadav, and the sentence 'Every number on this page is followed by the thing that would catch it.' Below it, the six colours the document uses, one per system: Glyph, jetpack, Cadence, Applied, LifeQuest, AutoML.">
</div>

I build systems that prove themselves. Six of them are live, publicly reachable, and five of the six ship a **system card** — a print-format walkthrough of the architecture and the evidence behind its numbers. AutoML's equivalent is an expo booklet.

What follows is five system plates (LifeQuest and AutoML share the last), plus one for the habit that runs underneath all of them, between an opening and a colophon. Each shows the claim, then the mechanism that would catch the claim if it were a lie.

---

## I · Glyph — *I don't trust the library*

<picture>
  <source media="(max-width: 500px)" srcset="./assets/m-1-glyph.svg">
  <img src="./assets/plate-1-glyph.svg" width="100%" alt="Glyph: a neural network written from scratch in C++ with hand-written AVX-512, AVX2 and NEON kernels, plus an autovectorised WebAssembly build. It scores 97.01 percent on the 10,000-image MNIST test set, which means 299 wrong — every one of them drawn as a grid of the labels it missed. 79 of those errors were made with over 0.9 confidence.">
</picture>

A neural network written **from scratch in C++** — no framework — with hand-written SIMD kernels for AVX-512, AVX2 and NEON. On `main`, the WebAssembly build carries no intrinsics of its own: under Emscripten every ISA predicate misses and the scalar path is autovectorised by `-msimd128` (`CMakeLists.txt:279`). The branches are `#if`/`#elif`, so one binary compiles one path and nothing cross-checks them.

The live page and the repo diverge here, so be exact about which you're looking at. `getglyph.vercel.app` **does** fetch and instantiate WebAssembly — `/wasm/fast_mnist.wasm`, 46,960 bytes, `application/wasm`, and it is a SIMD build — but it came off a branch carrying real `wasm_simd128` intrinsics. What you can reproduce from `main` is the autovectorised one, which is not quite what the link serves. (An earlier revision claimed the opposite — that no `.wasm` was fetched at all — and a later one put a SIMD-instruction count here. The first was wrong; the second I could not reproduce twice with the same method, so it is gone rather than rounded.)

**97.01%** on the 10,000-image MNIST test set — 9,701 right, so **299 wrong**.

That same test set also selected the checkpoint and triggered early stopping (`apps/train_model.cpp:219-243`), so treat it as a training-time number, not a clean held-out one. The run wasn't seeded either. The grid above draws all 299 — each mark the true label of an image the model missed.

[live](https://getglyph.vercel.app) · [system card](https://getglyph.vercel.app/system-card) · [repo](https://github.com/yadava5/glyph)

---

## II · jetpack — *I don't trust my own optimisation*

<picture>
  <source media="(max-width: 500px)" srcset="./assets/m-2-jetpack.svg">
  <img src="./assets/plate-2-jetpack.svg" width="100%" alt="jetpack: parallel gzip on JDK 25 reaches 422 megabytes per second against 66.2 single-threaded, a 6.4 times speedup, with blocks held in a bounded in-flight window. Its hand-vectorised Adler-32 checksum runs at 4.26 gigabytes per second and is verified bit-identical against java.util.zip — whose own native intrinsic is faster still, at 14.06, and is printed here as the reference it loses to.">
</picture>

Parallel, gzip-compatible compression on **JDK 25**: one virtual thread per block, a bounded in-flight window so peak memory is independent of file size, and memory-mapped input via the Foreign Function & Memory API.

The checksum is hand-vectorised — so it is checked **bit-identical against `java.util.zip.Adler32`** across every input the test suite throws at it. The output is a byte-valid single gzip member any tool can decompress.

**422 MB/s parallel vs 66.2 MB/s single-threaded — 6.4×** on an M1 Pro (10 cores). That is a 3-fork JMH run with 99.9% confidence intervals spanning ±0.7% (single-threaded) to ±6.9% (the vectorised checksum), committed at [`benchmarks/jmh-results-rigorous.json`](https://github.com/yadava5/jetpack-compress/blob/main/benchmarks/jmh-results-rigorous.json) with the machine spec beside it, so you can re-run it and check.

The ratio itself is the least stable number here: it moved **6.89× → 6.38×** between the quick run and the rigorous one — an 8% spread, *wider* than either run's own interval, and wider than the 4% spread I disclose on the SIMD result below. `benchmarks/ENVIRONMENT.md` says so too. I quote the rigorous run because it is the more careful one, not because it is the kinder one.

And the row that stays in the table because it's true: the hand-vectorised Adler-32 reaches **4.26 GB/s**, while the JDK's own native intrinsic does **14.06 GB/s**. I don't beat it. The SIMD result is honest against the *scalar* baseline (2.80× on the 3-fork run, 2.92× on the quick one — they disagree at the second figure, and that spread is the uncertainty), and the intrinsic is printed next to it as the reference it loses to.

[live](https://jetpack-compress.vercel.app) · [system card](https://jetpack-compress.vercel.app/system-card) · [repo](https://github.com/yadava5/jetpack-compress)

---

## III · Cadence — *I don't trust the black box*

<picture>
  <source media="(max-width: 500px)" srcset="./assets/m-3-cadence.svg">
  <img src="./assets/plate-3-cadence.svg" width="100%" alt="Cadence: the sentence 'lunch with sam friday 1pm' is labelled in place — title, attendee, day and time — and filed into the Friday 1pm slot of a week grid that names its hours. Its 36 API handlers are bundled into a single serverless function, because the hosting plan allows 12.">
</picture>

A sentence typed the way you would say it becomes a calendar entry. The parser runs four parsers — chrono, hashtag, priority, language — and **every extracted span records the parser that produced it** — `source` is a required field on every tag, and conflict resolution depends on it, so a wrong tag is traceable to the parser that produced it. (The title is not a parser output: it is what is left of the sentence once the spans are removed, and it carries no `source`.)

**36 API handlers bundled into a single serverless function**, to live inside Vercel's 12-function cap without giving up routes.

[live](https://usecadenceapp.vercel.app) · [system card](https://usecadenceapp.vercel.app/system-card) · [repo](https://github.com/yadava5/cadence)

---

## IV · Applied — *I don't trust the model*

<picture>
  <source media="(max-width: 500px)" srcset="./assets/m-4-applied.svg">
  <img src="./assets/plate-4-applied.svg" width="100%" alt="Applied: a three-layer email classifier — 201 regex rules, then e5 embeddings, then a fine-tuned SetFit head, cheapest first. It scores 0.979 macro-F1 on a 96-message evaluation set, measured with the rules layer alone; anything that fails to clear the 0.85 confidence gate is referred to a human rather than guessed at. Inference runs inside your browser.">
</picture>

Your inbox already holds the verdict on most applications you've sent. A three-layer cascade reads it: **201 regex rules → e5 embeddings → a fine-tuned SetFit head**, cheapest first.

**0.979 macro-F1** on a 96-message, 8-class evaluation set, and CI fails the build below 0.95 with a real non-zero exit.

Worth being exact, because the number and the picture don't quite match: that score is generated with the `deterministic` profile, which switches the SetFit head off and empties the embedding store — so it measures **the regex layer alone**, and the rules-only baseline reproduces it to the last digit. The full three-layer cascade's own score, 0.9583, survives in exactly one line of prose (`docs/ML_EXECUTION_TRACKER.md:378`) because the run that produced it was overwritten by the deterministic re-run. I can hand you an artifact for 0.979 and not for 0.9583, so 0.979 is what the plate draws, labelled for what it actually measures.

Anything under the **0.85 confidence gate** is not guessed at — it goes to a human. The model is allowed to say it doesn't know.

The fine-tuned head exports to int8 ONNX (90.4 MB → 22.8 MB) and runs **in your browser**: the server ships the weights once, then classification happens in your tab and nothing you paste leaves it. `allowRemoteModels = false` keeps the model local. Be exact about where that lives: the ONNX weights and the browser build are on the **unmerged branch [`integration/web-migration`](https://github.com/yadava5/applied/tree/integration/web-migration/ml/browser)**, not on `main` — `grep -i onnx` on `main` returns nothing. Both byte counts above are re-derived from that branch's commit. That in-browser build is the [Hugging Face Space](https://huggingface.co/spaces/yadava5/jobtracker-classifier); the `[live]` link below runs the rules layer only.

[live](https://getapplied.vercel.app) · [system card](https://getapplied.vercel.app/system-card) · [repo](https://github.com/yadava5/applied)

---

## V · The refusal — *I don't trust myself*

<picture>
  <source media="(max-width: 500px)" srcset="./assets/m-5-refusal.svg">
  <img src="./assets/plate-5-refusal.svg" width="100%" alt="A query from one tenant travels toward another tenant's rows, reaches the PostgreSQL row-level-security boundary, and stops. Only the querying tenant's own rows come back — because the database refused, not because the application remembered to filter.">
</picture>

Application code that filters by user is code that has to *remember* to filter. So the database enforces it instead: **PostgreSQL Row-Level Security**, `FORCE`d on all **seven** tenant tables (`user_profiles` is deliberately excluded), with the app connecting as a dedicated non-`BYPASSRLS` role and the request identity carried as a transaction-local GUC.

The test that matters runs a raw, unfiltered `SELECT count(*) FROM tasks` as user B. It returns **user B's rows only** — because the database refused, not because the query remembered. Being exact: the migrations are hand-run, and production still connects as the owner role, so today this is proven in CI against ephemeral Postgres rather than enforced in the deployed database.

Auditing my own work, I found **seven IDOR vulnerabilities** in Cadence — endpoints where any authenticated user could read or delete another user's records by id. A later audit found an **eighth** of the same shape that the first sweep missed: `TagService` inherited the base class's unscoped `WHERE id = $1`, so any user could read or delete any other user's tag. All eight are fixed. **Seven carry a regression test** asserting the scoped SQL — that seven is what the plate draws, because it is the part a machine can count; the task-lists one has no test yet, so the count admits it. The tag one is worth naming, because its existing test asserted the *vulnerable* query and would have reported green forever.

[the migration](https://github.com/yadava5/cadence/blob/main/lib/config/migrations/0002_enable_rls.sql) · [the app role](https://github.com/yadava5/cadence/blob/main/lib/config/migrations/0003_create_cadence_app_role.sql) · [the isolation suite](https://github.com/yadava5/cadence/blob/main/lib/__tests__/rls.postgres.test.ts)

---

## VI · LifeQuest & Agentic AutoML

<picture>
  <source media="(max-width: 500px)" srcset="./assets/m-6-release.svg">
  <img src="./assets/plate-6-release.svg" width="100%" alt="LifeQuest turns real-world routines into tracked quests, for people rebuilding structure after a layoff or in retirement. Agentic AutoML moves a dataset through a hardened Docker sandbox and holds it for a human before a preprocessing step is committed and before a model is trained. This is the one section on the page a reader cannot check: the repository is private.">
</picture>

**LifeQuest** turns real-world routines into tracked quests with tiered progression — built for people rebuilding structure, whether after a layoff or in retirement. Tauri + React client, NestJS + Prisma API.

**Agentic AutoML** takes a dataset and returns a deployed model: LangGraph orchestration over an MCP tool registry, Python executed in a hardened Docker sandbox — non-root, read-only rootfs, an `--internal` Docker network with no outbound route (the beta deploy defaults to `bridge`), capped memory and CPU — and human approval gates before a preprocessing step is committed and before a model is trained. Worth being exact: preprocessing runs the code *before* it asks, so the gate protects what gets persisted rather than what gets spent — and whether a step needs approval is itself proposed by the model, defaulting to *no* approval when the model does not ask for one. Senior design at Miami University, co-built with Shree Chaturvedi.

[LifeQuest](https://getlifequest.vercel.app) · [system card](https://getlifequest.vercel.app/system-card) · [repo](https://github.com/yadava5/lifequest) — [AutoML](https://agentic-automl-platform.vercel.app) · [system card](https://agentic-automl-platform.vercel.app/system-card) · repo private

This is the one section on the page you cannot check. AutoML's repository is private, so nothing above is re-derivable by a reader, and the plate says so on its face rather than borrowing the credibility of the five sections that are.

---

<img src="./assets/plate-7-colophon.svg" width="100%" alt="Six systems, five system cards and one expo booklet. Every number here is traceable to the repository it came from, except AutoML's, whose repository is private — and the page itself is animated SVG with no JavaScript and no server.">

<div align="center">
<sub>

Open to full-time software engineering roles and collaborations — **[aesh.03.23@gmail.com](mailto:aesh.03.23@gmail.com)** · [LinkedIn](https://www.linkedin.com/in/ayush-yadav-developer)

</sub>
</div>
