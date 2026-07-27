<div align="center">
<img src="./assets/plate-0-thesis.svg" width="100%" alt="Ayush Yadav. Every number on this page is followed by the thing that would catch it.">
</div>

I build systems that prove themselves. Six of them are live, publicly reachable, and each ships a **system card** — a printed-quality walkthrough of the architecture and the evidence behind its numbers.

What follows is one plate per system, plus one for the habit that runs underneath all of them. Each shows the claim, then the mechanism that would catch the claim if it were a lie.

---

## I · Glyph — *I don't trust the library*

<img src="./assets/plate-1-glyph.svg" width="100%" alt="A handwritten seven draws itself. Four instruction sets — AVX-512, AVX2, NEON and wasm128 — each return the same answer. The model scores 97.01 percent on the 10,000-image MNIST test set, which means 299 wrong; the grid is a count of those 299, not the digits themselves.">

A neural network written **from scratch in C++** — no framework — with hand-written SIMD kernels for AVX-512, AVX2, NEON and wasm128, compiled to WebAssembly. (The linked demo currently ships the labelled-JS fallback — the WASM build is behind a flag, and the page says so itself rather than quietly claiming the fast path.)

**97.01%** on the 10,000-image MNIST test set — 9,701 right, so **299 wrong**.

Full disclosure, because this page is about disclosure: that same test set also selected the checkpoint and triggered early stopping (`apps/train_model.cpp:219-243`), so treat it as a training-time number, not a clean held-out one. The run wasn't seeded either. The weights are committed; the error list isn't, so the grid above is a count of the 299 — not the digits.

[live](https://getglyph.vercel.app) · [system card](https://getglyph.vercel.app/system-card) · [repo](https://github.com/yadava5/glyph)

---

## II · jetpack — *I don't trust my own optimisation*

<img src="./assets/plate-2-jetpack.svg" width="100%" alt="Blocks pass through a bounded in-flight window and leave compressed. A hand-vectorised Adler-32 checksum is compared digit by digit against java.util.zip and matches exactly. A measured table lists the JDK's own native intrinsic at 14.1 GB/s, marked not beaten.">

Parallel, gzip-compatible compression on **JDK 25**: one virtual thread per block, a bounded in-flight window so peak memory is independent of file size, and memory-mapped input via the Foreign Function & Memory API.

The checksum is hand-vectorised — so it is checked **bit-identical against `java.util.zip.Adler32`** across every input the test suite throws at it. The output is a byte-valid single gzip member any tool can decompress.

**~435 MB/s parallel vs ~67 MB/s single-threaded — roughly 6.5×** on 10 cores. It is a quick JMH run (1 fork, 3+4 iterations), so read the multiple, not the digits.

And the row that stays in the table because it's true: the hand-vectorised Adler-32 reaches **4.34 GB/s**, while the JDK's own native intrinsic does **14.1 GB/s**. I don't beat it. The SIMD result is honest against the *scalar* baseline (2.8×), and the intrinsic is printed next to it as the reference it loses to.

[live](https://jetpack-compress.vercel.app) · [system card](https://jetpack-compress.vercel.app/system-card) · [repo](https://github.com/yadava5/jetpack-compress)

---

## III · Cadence — *I don't trust the black box*

<img src="./assets/plate-3-cadence.svg" width="100%" alt="The sentence 'lunch with sam friday 1pm' is annotated in place by four parser stages, labelling title, attendee, date and time, and then filed into the Friday column of a calendar week.">

A sentence typed the way you would say it becomes a calendar entry. The parser runs four stages — chrono, hashtag, priority, language — and **every extracted span records the parser that produced it** (`source` on each tag), so a wrong answer is traceable to the stage that caused it.

**36 API handlers bundled into a single serverless function**, to live inside Vercel's 12-function cap without giving up routes.

[live](https://usecadenceapp.vercel.app) · [system card](https://usecadenceapp.vercel.app/system-card) · [repo](https://github.com/yadava5/cadence)

---

## IV · Applied — *I don't trust the model*

<img src="./assets/plate-4-applied.svg" width="100%" alt="Email falls through three classifier layers: 201 regex rules, e5 embeddings, and a SetFit head. Messages that fail to clear the 0.85 confidence gate divert sideways to a human. The measured basis is shown: 96 authored messages, 8 classes, a 0.95 CI floor. The fine-tuned head runs inside a boundary marked 'your browser', with remote models disabled.">

Your inbox already holds the verdict on most applications you've sent. A three-layer cascade reads it: **201 regex rules → e5 embeddings → a fine-tuned SetFit head**, cheapest first.

**0.979 macro-F1**, and CI fails the build below 0.95. Anything under the **0.85 confidence gate** is not guessed at — it goes to a human. The model is allowed to say it doesn't know.

The fine-tuned head exports to int8 ONNX and runs **in your browser** — `allowRemoteModels = false`, so it cannot phone home. The server never sees the learned model.

[live](https://getapplied.vercel.app) · [system card](https://getapplied.vercel.app/system-card) · [repo](https://github.com/yadava5/applied)

---

## V · The refusal — *I don't trust myself*

<img src="./assets/plate-5-refusal.svg" width="100%" alt="A query from tenant A travels toward tenant B's rows, reaches the row-level-security boundary, and stops. Zero rows are returned. Seven IDOR vulnerabilities were found and fixed, by the author.">

Application code that filters by user is code that has to *remember* to filter. So the database enforces it instead: **PostgreSQL Row-Level Security**, `FORCE`d on every tenant table, with the app connecting as a dedicated non-`BYPASSRLS` role and the request identity carried as a transaction-local GUC.

The test that matters runs a raw, unfiltered `SELECT` as user B. It returns **user B's rows only** — because the database refused, not because the query remembered.

Auditing my own work, I found **seven IDOR vulnerabilities** in Cadence — endpoints where any authenticated user could read or delete another user's records by id. All seven are fixed; six carry a regression test asserting the scoped SQL, and the task-lists one does not yet.

[the migration](https://github.com/yadava5/cadence/blob/main/lib/config/migrations/0002_enable_rls.sql) · [the app role](https://github.com/yadava5/cadence/blob/main/lib/config/migrations/0003_create_cadence_app_role.sql) · [the isolation suite](https://github.com/yadava5/cadence/blob/main/lib/__tests__/rls.postgres.test.ts)

---

## VI · LifeQuest & Agentic AutoML

<img src="./assets/plate-6-release.svg" width="100%" alt="Three seeded quests appear along a path. A dataset token moves through a hardened Docker sandbox, waits at a human approval gate, and is then deployed.">

**LifeQuest** turns real-world routines into tracked quests with tiered progression — built for people rebuilding structure, whether after a layoff or in retirement. Tauri + React client, NestJS + Prisma API.

**Agentic AutoML** takes a dataset and returns a deployed model: LangGraph orchestration over an MCP tool registry, Python executed in a hardened Docker sandbox — non-root, read-only rootfs, no network, capped memory and CPU — and human approval on every phase that mutates data or spends compute, with the model forbidden from approving its own steps. Senior design at Miami University, co-built with Shree Chaturvedi.

[LifeQuest](https://getlifequest.vercel.app) · [system card](https://getlifequest.vercel.app/system-card) — [AutoML](https://agentic-automl-platform.vercel.app) · [system card](https://agentic-automl-platform.vercel.app/system-card)

---

<img src="./assets/plate-7-colophon.svg" width="100%" alt="Six systems, six system cards. Every number traces to a committed benchmark. Rendered as animated SVG with no JavaScript and no server. CS 2026, Miami University.">

<div align="center">
<sub>

Open to summer 2026 internships and collaborations — **[aesh.03.23@gmail.com](mailto:aesh.03.23@gmail.com)** · [LinkedIn](https://www.linkedin.com/in/ayush-yadav-developer)

</sub>
</div>
