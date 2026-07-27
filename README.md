<div align="center">
<img src="./assets/plate-0-thesis.svg" width="100%" alt="Ayush Yadav. Every number on this page is followed by the thing that would catch it.">
</div>

I build systems that prove themselves. Six of them are live, publicly reachable, and each ships a **System Card** — a printed-quality walkthrough of the architecture and the evidence behind its numbers.

What follows is one plate per system. Each shows the claim, then the mechanism that would catch the claim if it were a lie.

---

## I · Glyph — *I don't trust the library*

<img src="./assets/plate-1-glyph.svg" width="100%" alt="A handwritten seven draws itself. Four instruction sets — AVX-512, AVX2, NEON and wasm128 — each return the same answer. The model scores 97.01 percent on the MNIST test set of 10,000 images, and all 299 misclassified digits are shown.">

A neural network written **from scratch in C++** — no framework — with hand-written SIMD kernels for AVX-512, AVX2, NEON and wasm128, compiled to WebAssembly so it runs in your browser.

**97.01%** on the held-out MNIST test set (n=10,000). Which means **299 wrong**, and the plate above shows every one of them.

[live](https://getglyph.vercel.app) · [system card](https://getglyph.vercel.app/system-card) · [repo](https://github.com/yadava5/glyph)

---

## II · jetpack — *I don't trust my own optimisation*

<img src="./assets/plate-2-jetpack.svg" width="100%" alt="Blocks pass through a bounded in-flight window and leave compressed. A SIMD Adler-32 checksum is compared digit by digit against java.util.zip and matches exactly. A table of speedups by block size includes a row reading 0.94 times, where the optimisation loses.">

Parallel, gzip-compatible compression on **JDK 25**: one virtual thread per block, a bounded in-flight window so peak memory is independent of file size, and memory-mapped input via the Foreign Function & Memory API.

The checksum is hand-vectorised — so it is checked **bit-identical against `java.util.zip.Adler32`**. The output is a byte-valid single gzip member any tool can decompress.

**~6.5× throughput.** And at 4 KiB blocks it runs **0.94×** — slower than the baseline. That row is in the table because it's true.

[live](https://jetpack-compress.vercel.app) · [system card](https://jetpack-compress.vercel.app/system-card) · [repo](https://github.com/yadava5/jetpack-compress)

---

## III · Cadence — *I don't trust the black box*

<img src="./assets/plate-3-cadence.svg" width="100%" alt="The sentence 'lunch with sam friday 1pm' is annotated in place by four parser stages, labelling title, attendee, date and time, and then filed into the Friday column of a calendar week.">

Type a sentence the way you'd say it and it becomes a calendar entry. The parser runs four stages — chrono, hashtag, priority, language — and **shows its work at every one**, so a wrong answer is always traceable to a stage.

**34 API handlers bundled into a single serverless function**, to live inside Vercel's 12-function cap without giving up routes.

[live](https://usecadenceapp.vercel.app) · [system card](https://usecadenceapp.vercel.app/system-card) · [repo](https://github.com/yadava5/cadence)

---

## IV · Applied — *I don't trust the model*

<img src="./assets/plate-4-applied.svg" width="100%" alt="Email falls through three classifier layers: 201 regex rules, e5 embeddings, and a SetFit head. Messages that fail to clear the 0.85 confidence gate divert sideways to a human. A confusion matrix lights up including its off-diagonal cells. Inference runs inside a boundary marked 'your browser', with zero server calls.">

Your inbox already holds the verdict on every application you've sent. A three-layer cascade reads it: **201 regex rules → e5 embeddings → a fine-tuned SetFit head**, cheapest first.

**0.979 macro-F1**, and CI fails the build below 0.95. Anything under the **0.85 confidence gate** is not guessed at — it goes to a human. The model is allowed to say it doesn't know.

The trained model exports to int8 ONNX and runs **in your browser**. No inference server. Nothing to trust.

[live](https://getapplied.vercel.app) · [system card](https://getapplied.vercel.app/system-card) · [repo](https://github.com/yadava5/applied)

---

## V · The refusal — *I don't trust myself*

<img src="./assets/plate-5-refusal.svg" width="100%" alt="A query from tenant A travels toward tenant B's rows, reaches the row-level-security boundary, and stops. Zero rows are returned. Seven IDOR vulnerabilities were found and fixed, by the author.">

Application code that filters by user is code that has to *remember* to filter. So the database enforces it instead: **PostgreSQL Row-Level Security**, `FORCE`d on every tenant table, with the app connecting as a dedicated non-`BYPASSRLS` role and the request identity carried as a transaction-local GUC.

The test that matters runs a raw, unfiltered `SELECT` as user B. It returns **user B's rows only** — because the database refused, not because the query remembered.

Auditing my own work, I found **seven IDOR vulnerabilities** in Cadence — endpoints where any authenticated user could read or delete another user's records by id. All seven are fixed, with tests asserting the scoped SQL.

---

## VI · LifeQuest & Agentic AutoML

<img src="./assets/plate-6-release.svg" width="100%" alt="A daily routine becomes three mission nodes on a path. A dataset token moves through a Docker-sandboxed pipeline, waits at a human approval gate, and is then deployed.">

**LifeQuest** turns real-world routines into map-based missions — built for people rebuilding structure after a layoff. Tauri + React client, NestJS + Prisma API.

**Agentic AutoML** takes a dataset and returns a deployed model: LangGraph orchestration over an MCP tool registry, Python executed in a Docker sandbox it cannot escape, and a human approval gate at every phase. Senior design at Miami University, co-built with Shree Chaturvedi.

[LifeQuest](https://getlifequest.vercel.app) · [card](https://getlifequest.vercel.app/system-card) — [AutoML](https://agentic-automl-platform.vercel.app) · [card](https://agentic-automl-platform.vercel.app/system-card)

---

<img src="./assets/plate-7-colophon.svg" width="100%" alt="Six systems, six system cards. Every number traces to a committed benchmark. Rendered as animated SVG with no JavaScript and no server. CS 2026, Miami University.">

<div align="center">
<sub>

Open to summer 2026 internships and collaborations — **[aesh.03.23@gmail.com](mailto:aesh.03.23@gmail.com)** · [LinkedIn](https://www.linkedin.com/in/ayush-yadav-developer)

</sub>
</div>
