<div align="center">
<picture>
  <source media="(prefers-color-scheme: light) and (max-width: 500px)" srcset="./assets/light/m-0-thesis.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/light/plate-0-thesis.svg">
  <source media="(max-width: 500px)" srcset="./assets/m-0-thesis.svg">
  <img src="./assets/plate-0-thesis.svg" width="100%" alt="Ayush Yadav, a computer science graduate in Cincinnati, Ohio, open to full-time engineering roles. Languages C++, TypeScript, Python, Java, Swift and Rust; systems work in SIMD AVX-512, Vector API, WebAssembly and OpenMP; machine learning with LangGraph, MCP, in-browser ONNX and SetFit; web and backend in React, Next.js, Tauri, SwiftUI, FastAPI and NestJS; infrastructure on GitHub Actions, Docker, Postgres and CodeQL. Below, the six systems this page documents: Glyph, jetpack, Cadence, Applied, LifeQuest and Agentic AutoML.">
</picture>
</div>

**C++ · TypeScript · Python · Java · Swift · Rust** — B.S. Computer Science, Miami University (May 2026). Based in Cincinnati, OH; open to full-time software engineering roles: **[aesh.03.23@gmail.com](mailto:aesh.03.23@gmail.com)** · [LinkedIn](https://www.linkedin.com/in/ayush-yadav-developer)

Every number below is recomputed in CI from a pinned commit, except §I, which is my word. Six systems are live, publicly reachable, and five of the six ship a **system card** — a print-format walkthrough of the architecture and the evidence behind its numbers. AutoML's equivalent is an expo booklet.

---

## I · Work — *a year of it, and it isn't in a repo*

<picture>
  <source media="(prefers-color-scheme: light) and (max-width: 500px)" srcset="./assets/light/m-0b-work.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/light/plate-0b-work.svg">
  <source media="(max-width: 500px)" srcset="./assets/m-0b-work.svg">
  <img src="./assets/plate-0b-work.svg" width="100%" alt="Experience. As ITSM Data Integration Intern at Miami University from June 2025 to May 2026: a Python pipeline turning 1.6 million Oracle Analytics query logs into a 57.8 million-row field-usage table; code compliance lifted from 0 to 96.72 percent across a 61-project portfolio; and a 10,453-row master asset inventory consolidated from Tableau and Workday. At DataFest 2026, team lead of three: 90-day care utilisation modelled for 349 thousand patients at 0.90 holdout AUC, over 7.7 million encounters processed with DuckDB and Polars, preserving 99.6 percent of social-determinant linkage against 32 percent under a naive join. These figures are attested by the author rather than derived from a public repository.">
</picture>

For a year I was **ITSM Data Integration Intern at Miami University**. A Python pipeline ingested **1.6M Oracle Analytics query logs** — five years, 1,153 users, 66 dashboards — into a **57.8M-row** field-usage table, flagging which fields were actually in use for an OAS-to-Tableau migration. A second pass consolidated asset data siloed across Tableau and Workday into one **10,453-row, 35-field** master inventory with hash-based dedup, backed by ruff + pytest in CI. And a legacy Laravel compliance reporter became a clean ETL feed powering a 37-month dashboard that lifted code compliance **from 0% to 96.72%** across a **61-project** portfolio.

At **DataFest 2026** I led a three-person team in the national ASA competition: 90-day care utilisation modelled for **349K patients** at **0.90 holdout AUC** with XGBoost, CatBoost and LightGBM, drivers explained with SHAP, and PyTorch DeepSurv and GRU survival models benchmarked against them. **7.7M encounters (1.4 GB)** went through a DuckDB + Polars star schema that preserved **99.6%** of social-determinant linkage against **32%** under a naive join.

Be exact about the warrant here, because it is different from every other section: **none of these numbers can be re-derived by you.** The Oracle logs, the Tableau inventory and the compliance dashboard belong to Miami University; the DataFest data is a competition set that is not mine to publish. Everything else on this page is fetched from a pinned commit and recomputed in CI. This section is my word, and the plate says so on its face.

Also from that year: Dean's List in Fall 2023, Spring 2025 and Fall 2025; finalist in MUCAT Design Innovation with a LiDAR visual-assistance proposal and a $2,500 prototyping grant; and fourth place at Social Innovation Weekend, where LifeQuest was first built with a seven-person team.

---

## II · Glyph — *I don't trust the library*

<picture>
  <source media="(prefers-color-scheme: light) and (max-width: 500px)" srcset="./assets/light/m-1-glyph.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/light/plate-1-glyph.svg">
  <source media="(max-width: 500px)" srcset="./assets/m-1-glyph.svg">
  <img src="./assets/plate-1-glyph.svg" width="100%" alt="Glyph: a neural network written from scratch in C++ with hand-written AVX-512, AVX2 and NEON kernels, plus an autovectorised WebAssembly build. It scores 97.01 percent on the 10,000-image MNIST test set, which means 299 wrong — every one of them drawn as a grid of the labels it missed. The 79 it was most confident about are drawn in a heavier stroke than the rest.">
</picture>

A neural network written **from scratch in C++** — no framework — with hand-written SIMD kernels for AVX-512, AVX2 and NEON. On `main`, the WebAssembly build carries no intrinsics of its own: under Emscripten every ISA predicate misses and the scalar path is autovectorised by `-msimd128` (`CMakeLists.txt:279`). The branches are `#if`/`#elif`, so one binary compiles one path and nothing cross-checks them.

The live page and `main` diverge. `getglyph.vercel.app` **does** fetch and instantiate WebAssembly — `/wasm/fast_mnist.wasm`, 46,960 bytes, `application/wasm` — and it is a SIMD build, off [`yadava5/fix-hero-media-validation`](https://github.com/yadava5/glyph/tree/yadava5/fix-hero-media-validation), which carries real `wasm_simd128` intrinsics.

`curl -s https://getglyph.vercel.app/wasm/fast_mnist.wasm | shasum -a 256` gives `396dc0f4848ddc0b9c35420cdad5e5cc0af53f4a408024ba10f7364470d9807e` — byte-identical to that branch's blob. What `main` builds is the autovectorised one, which is not what the link serves.

**97.01%** on the 10,000-image MNIST test set — 9,701 right, so **299 wrong**.

That same test set also selected the checkpoint and triggered early stopping (`apps/train_model.cpp:219-243`), so treat it as a training-time number, not a clean held-out one. The run wasn't seeded either. The grid above draws all 299 — each mark the true label of an image the model missed.

[live](https://getglyph.vercel.app) · [system card](https://getglyph.vercel.app/system-card) · [repo](https://github.com/yadava5/glyph)

---

## III · jetpack — *I don't trust my own optimisation*

<picture>
  <source media="(prefers-color-scheme: light) and (max-width: 500px)" srcset="./assets/light/m-2-jetpack.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/light/plate-2-jetpack.svg">
  <source media="(max-width: 500px)" srcset="./assets/m-2-jetpack.svg">
  <img src="./assets/plate-2-jetpack.svg" width="100%" alt="jetpack: parallel gzip on JDK 25 reaches 422 megabytes per second against 66.2 single-threaded, a 6.4 times speedup, with blocks held in a bounded in-flight window. Its hand-vectorised Adler-32 checksum runs at 4.26 gigabytes per second and is verified bit-identical against java.util.zip — whose own native intrinsic is faster still, at 14.06, and is printed here as the reference it loses to.">
</picture>

Parallel, gzip-compatible compression on **JDK 25**: one virtual thread per block, a bounded in-flight window so peak memory is independent of file size, and memory-mapped input via the Foreign Function & Memory API.

The checksum is hand-vectorised — so it is checked **bit-identical against `java.util.zip.Adler32`** across every input the test suite throws at it. The output is a byte-valid single gzip member any tool can decompress.

**422 MB/s parallel vs 66.2 MB/s single-threaded — 6.4×** on an M1 Pro (10 cores). That is a 3-fork JMH run with 99.9% confidence intervals spanning ±0.7% (single-threaded) to ±6.9% (the vectorised checksum), committed at [`benchmarks/jmh-results-rigorous.json`](https://github.com/yadava5/jetpack-compress/blob/main/benchmarks/jmh-results-rigorous.json) with the machine spec beside it, so you can re-run it and check.

The ratio itself is the least stable number here: it moved **6.89× → 6.38×** between the quick run and the rigorous one — an 8% spread, *wider* than either run's own interval, and wider than the 4% spread I disclose on the SIMD result below. `benchmarks/ENVIRONMENT.md` says so too.

The hand-vectorised Adler-32 reaches **4.26 GB/s**, while the JDK's own native intrinsic does **14.06 GB/s**. I don't beat it. The SIMD result is measured against the *scalar* baseline (2.80× on the 3-fork run, 2.92× on the quick one — they disagree at the second figure, and that spread is the uncertainty), and the intrinsic is printed next to it as the reference it loses to.

[live](https://jetpack-compress.vercel.app) · [system card](https://jetpack-compress.vercel.app/system-card) · [repo](https://github.com/yadava5/jetpack-compress)

---

## IV · Cadence — *I don't trust the black box*

<picture>
  <source media="(prefers-color-scheme: light) and (max-width: 500px)" srcset="./assets/light/m-3-cadence.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/light/plate-3-cadence.svg">
  <source media="(max-width: 500px)" srcset="./assets/m-3-cadence.svg">
  <img src="./assets/plate-3-cadence.svg" width="100%" alt="Cadence: the sentence 'lunch with sam friday 1pm' is labelled in place with the parser that produced each span — compromise found the person, chrono-node found both the day and the time — while the title is left unmarked because it is what remains once the spans are removed and carries no parser. It is then filed into the Friday 1pm slot of a week grid that names its hours. Its 36 API handlers are bundled into a single serverless function, because the hosting plan allows 12.">
</picture>

A sentence typed the way you would say it becomes a calendar entry. Four parsers run over it: chrono-node for dates and times, compromise for people, plus hashtag and priority passes. **Every extracted span records which one produced it** — `source` is a required field on every tag and conflict resolution depends on it, so a wrong tag is traceable to its parser. The title is not a parser output: it is what is left once the spans are removed, and it carries no `source`.

**36 API handlers bundled into a single serverless function**, to live inside Vercel's 12-function cap without giving up routes.

[live](https://usecadenceapp.vercel.app) · [system card](https://usecadenceapp.vercel.app/system-card) · [repo](https://github.com/yadava5/cadence)

---

## V · Applied — *I don't trust the model*

<picture>
  <source media="(prefers-color-scheme: light) and (max-width: 500px)" srcset="./assets/light/m-4-applied.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/light/plate-4-applied.svg">
  <source media="(max-width: 500px)" srcset="./assets/m-4-applied.svg">
  <img src="./assets/plate-4-applied.svg" width="100%" alt="Applied: a three-layer email classifier — 201 regex rules, then e5 embeddings, then a fine-tuned SetFit head, cheapest first. It scores 0.979 macro-F1 on a 96-message evaluation set, measured with the rules layer alone; anything that fails to clear the 0.85 confidence gate is referred to a human rather than guessed at. Inference runs inside your browser.">
</picture>

Your inbox already holds the verdict on most applications you've sent. A three-layer cascade reads it: **201 regex rules → e5 embeddings → a fine-tuned SetFit head**, cheapest first.

**0.979 macro-F1** on a 96-message, 8-class evaluation set, and CI fails the build below 0.95 with a real non-zero exit.

That score is **two mistakes**. The set is balanced at 12 messages per class — which is why macro-F1 and weighted-F1 come out identical — so one more error moves it about a point. jetpack's numbers on this page carry ±0.7% to ±6.9% because a JMH run hands you an interval; a 96-row evaluation does not, and quoting three decimals off two mistakes would be borrowing a precision I don't have.

That score is generated with the `deterministic` profile, which switches the SetFit head off and empties the embedding store — so it measures **the regex layer alone**, and the rules-only baseline reproduces it to the last digit. The full three-layer cascade's own score, 0.9583, survives in exactly one line of prose (`docs/ML_EXECUTION_TRACKER.md:378`) because the run that produced it was overwritten by the deterministic re-run. I can hand you an artifact for 0.979 and not for 0.9583, so 0.979 is what the plate draws, labelled for what it actually measures.

Anything under the **0.85 confidence gate** is not guessed at — it goes to a human. The model is allowed to say it doesn't know.

The fine-tuned head exports to int8 ONNX (90.4 MB → 22.8 MB) and runs **in your browser**: the server ships the weights once, then classification happens in your tab and nothing you paste leaves it. `allowRemoteModels = false` keeps the model local. the ONNX weights and the browser build are on the **unmerged branch [`integration/web-migration`](https://github.com/yadava5/applied/tree/integration/web-migration/ml/browser)**, not on `main` — `main` has no `ml/` directory and no ONNX artifact at all, and `grep -i onnx` there returns only that repo's own README. Both byte counts above are re-derived from that branch's commit. That in-browser build is the [Hugging Face Space](https://huggingface.co/spaces/yadava5/jobtracker-classifier); the `[live]` link below runs the rules layer only.

[live](https://getapplied.vercel.app) · [system card](https://getapplied.vercel.app/system-card) · [repo](https://github.com/yadava5/applied)

---

## VI · The refusal — *I don't trust myself*

<picture>
  <source media="(prefers-color-scheme: light) and (max-width: 500px)" srcset="./assets/light/m-5-refusal.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/light/plate-5-refusal.svg">
  <source media="(max-width: 500px)" srcset="./assets/m-5-refusal.svg">
  <img src="./assets/plate-5-refusal.svg" width="100%" alt="The IDOR found auditing Cadence, drawn service by service: in six services — attachments, calendars, events, task-lists, tasks and tags — any authenticated user could read or delete another user's records by id. Each service now carries the owner guard in its read and delete queries, so tenant A's rows are struck out of a read run as tenant B and only B's return. Two caveats stay on the plate: the tags test asserted the vulnerable query, and task-lists still has no regression test. Below, the layer that does not depend on remembering: an unfiltered SELECT count(*) FROM tasks, run as B, comes back B only, because PostgreSQL row-level security refused the rest.">
</picture>

Application code that filters by user is code that has to *remember* to filter. So the database enforces it instead: **PostgreSQL Row-Level Security**, `FORCE`d on all **seven** tenant tables (`users` and `user_profiles` are deliberately excluded — both are read and written pre-auth, so RLS on them would break login), with the app connecting as a dedicated non-`BYPASSRLS` role and the request identity carried as a transaction-local GUC.

The test that matters runs a raw, unfiltered `SELECT count(*) FROM tasks` as user B. It returns **user B's rows only** — because the database refused, not because the query remembered. The migrations are hand-run, and production still connects as the owner role, so today this is proven in CI against ephemeral Postgres rather than enforced in the deployed database.

Auditing my own work, I found the same defect in **six services** — attachments, calendars, events, task-lists, tasks and tags — where any authenticated user could read or delete another user's records by id, because the service dropped the `userId` the handler had passed it and fell through to the base class's unscoped `WHERE id = $1`. Events, tasks and tags carried it on both read and delete. All six now scope every query by owner, and that is what the plate draws, because it is the part a machine can count from the code rather than from my own commit messages.

Tags was missed by the first sweep entirely, and is the one worth naming: its existing test asserted the *vulnerable* query, so it would have reported green forever. Task-lists is the one still without a regression test.

[the migration](https://github.com/yadava5/cadence/blob/main/lib/config/migrations/0002_enable_rls.sql) · [the app role](https://github.com/yadava5/cadence/blob/main/lib/config/migrations/0003_create_cadence_app_role.sql) · [the isolation suite](https://github.com/yadava5/cadence/blob/main/lib/__tests__/rls.postgres.test.ts)

---

## VII · LifeQuest

<picture>
  <source media="(prefers-color-scheme: light) and (max-width: 500px)" srcset="./assets/light/m-6-release.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/light/plate-6-release.svg">
  <source media="(max-width: 500px)" srcset="./assets/m-6-release.svg">
  <img src="./assets/plate-6-release.svg" width="100%" alt="LifeQuest turns real-world routines into tracked quests, for people rebuilding structure after a layoff or in retirement. One source tree in apps/desktop is built twice — as a Tauri 2 native binary and as a web app — with a shared Zod schema package holding both of them to the same contract as the API. Behind it: 10 Prisma models and 14 REST endpoints across 6 NestJS controllers. When it generates a quest it asks OpenAI, falls back to Hugging Face, and if neither is configured it returns nothing rather than inventing one.">
</picture>

**LifeQuest** turns the things you meant to do into quests you can finish — built for people rebuilding structure, whether after a layoff or in retirement.

One source tree in `apps/desktop` is built twice: `vite build` for the web, and the same tree wrapped as a Tauri 2 native binary. `packages/schemas` is a Zod package both builds and the NestJS API import, so a shape can only change in one place. The API is 14 REST endpoints across 6 controllers over 10 Prisma models.

Quest generation asks OpenAI, falls back to Hugging Face, and returns `null` if neither key is configured rather than inventing a quest. There is no unit-test suite here; coverage is a Playwright spec, and the `test:api` script is `vitest --passWithNoTests`.

[LifeQuest](https://getlifequest.vercel.app) · [system card](https://getlifequest.vercel.app/system-card) · [repo](https://github.com/yadava5/lifequest)

---

## VIII · Agentic AutoML

<picture>
  <source media="(prefers-color-scheme: light) and (max-width: 500px)" srcset="./assets/light/m-6b-automl.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/light/plate-6b-automl.svg">
  <source media="(max-width: 500px)" srcset="./assets/m-6b-automl.svg">
  <img src="./assets/plate-6b-automl.svg" width="100%" alt="Agentic AutoML takes a dataset and a sentence and returns a trained model. Its tool registry holds 44 definitions, but the model never carries all of them: 15 travel with it in every phase and the remaining 29 arrive with the phase that needs them, routed by seven named tool sets — onboarding, preprocessing, feature proposal, feature continue, feature engineering, feature lifecycle and training lifecycle. The Python it writes executes in a container with no network, a read-only root filesystem, a non-root user and the dataset mounted read-only, leaving 5 tmpfs mounts as the only writable surface. Behind it sits a 29-table Postgres schema with pgvector. Written with Shree Chaturvedi; the repository is public and licensed GPL-3.0.">
</picture>

**Agentic AutoML** takes a dataset and a sentence and gives back a trained model. A LangGraph state machine drives it; an MCP server exposes the tools.

The part worth looking at is what the model is allowed to hold. The registry has **44** tool definitions, but `LLM_TOOL_DEFINITIONS` — the set that travels with the model everywhere — is **15** of them: data, cell and package tools. The other 29 arrive with the phase that needs them, through seven exported sets: onboarding, preprocessing, feature proposal, feature continue, feature engineering, feature lifecycle, training lifecycle. A model in the training phase cannot reach a preprocessing tool, because it was never handed one.

The Python it writes runs in a container built by `dockerBuilder.ts`: `--network none`, `--read-only` root, `--user sandbox`, datasets mounted `:ro`, memory and CPU capped. Five `--tmpfs` mounts are the entire writable surface, and none of it survives the container. When a cell raises, the repair loop re-prompts on the actual traceback rather than a summary of it.

Behind that: a **29**-table Postgres schema with pgvector, and a Jupyter kernel held open per project so state survives between cells.

[AutoML](https://agentic-automl-platform.vercel.app) · [expo booklet](https://agentic-automl-platform.vercel.app/system-card) · [repo](https://github.com/yadava5/ai-augmented-auto-ml-toolchain)

Licensed **GPL-3.0** at the commit this page pins. A relicence to PolyForm Noncommercial is proposed in [PR #5](https://github.com/yadava5/ai-augmented-auto-ml-toolchain/pull/5) and needs my co-author's review before it means anything; until that merges, GPL-3.0 is what you get, and under GPL-3.0 commercial use needs no arrangement with either of us.

---

<picture>
  <source media="(prefers-color-scheme: light) and (max-width: 500px)" srcset="./assets/light/m-7-colophon.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/light/plate-7-colophon.svg">
  <source media="(max-width: 500px)" srcset="./assets/m-7-colophon.svg">
  <img src="./assets/plate-7-colophon.svg" width="100%" alt="Six systems, five system cards and one expo booklet. Every number here is traceable to the repository it came from, and the page itself is animated SVG with no JavaScript and no server.">
</picture>

<div align="center">
<sub>

**[aesh.03.23@gmail.com](mailto:aesh.03.23@gmail.com)** · [LinkedIn](https://www.linkedin.com/in/ayush-yadav-developer) · [github.com/yadava5](https://github.com/yadava5)

</sub>
</div>
