<picture>
  <source media="(prefers-color-scheme: light) and (max-width: 500px)" srcset="./assets/light/m-0-hero.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/light/plate-0-hero.svg">
  <source media="(max-width: 500px)" srcset="./assets/m-0-hero.svg">
  <img src="./assets/plate-0-hero.svg" width="100%" alt="Ayush Yadav — the estate drawn as one circuit board. Six product marks sit on a shared bus and every printed edge is a checkable claim: Cadence and Applied share forced row-level security, Glyph and jetpack share SIMD, AutoML feeds Postgres. VisualAssist hangs on an open stub — no URL, it needs an iPhone with LiDAR in your hand. B.S. Computer Science, Miami University, May 2026; open to full-time software engineering roles; aesh at gmail.">
</picture>

<a href="https://ayush-yadav.com"><img src="./assets/plate-link-portfolio.svg" alt="Port one of four on the link bus: ayush-yadav.com, the portfolio."></a><a href="https://ayush-yadav.com/resume.pdf"><img src="./assets/plate-link-resume.svg" alt="Port two of four on the link bus: the résumé, as a PDF."></a><a href="https://www.linkedin.com/in/ayush-yadav-developer"><img src="./assets/plate-link-linkedin.svg" alt="Port three of four on the link bus: the LinkedIn profile."></a><a href="mailto:aesh.03.23@gmail.com"><img src="./assets/plate-link-email.svg" alt="Port four of four on the link bus: email; opens a mail draft."></a>

<picture>
  <source media="(prefers-color-scheme: light) and (max-width: 500px)" srcset="./assets/light/m-link-return.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/light/plate-link-return.svg">
  <source media="(max-width: 500px)" srcset="./assets/m-link-return.svg">
  <img src="./assets/plate-link-return.svg" width="100%" alt="The four link ports hand back to the page bus — the three lanes merge and continue into the evidence, sections two to seven.">
</picture>

**C++ · TypeScript · Python · Java · Swift · Rust** — B.S. Computer Science, Miami University (May 2026). Cincinnati, Ohio. Open to full-time software engineering roles.

Seven systems. Every number is drawn on the plate beside it and re-derived in CI from a pinned commit, except §I and §VII's grant, which are my word and say so where they stand. Four of them ship a **system card**, a print-format walkthrough of the architecture and the evidence.

---

<picture>
  <source media="(prefers-color-scheme: light) and (max-width: 500px)" srcset="./assets/light/m-1-work.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/light/plate-1-work.svg">
  <source media="(max-width: 500px)" srcset="./assets/m-1-work.svg">
  <img src="./assets/plate-1-work.svg" width="100%" alt="I · Work — the one section drawn as an empty footprint: a component the board expects that is not fitted, because the year of paid work is off-repo. A 57.8M-row field-usage table, distilled from 1.6M Oracle Analytics query logs at Miami University. None of these numbers can be re-derived by a reader — the data belongs to Miami University and to a competition; this section is attested, not derived.">
</picture>

ITSM Data Integration Intern at Miami University, June 2025 to May 2026, and team lead of three at DataFest 2026. This is the only section whose numbers you cannot check for yourself, and the plate says so on its face.

---

<picture>
  <source media="(prefers-color-scheme: light) and (max-width: 500px)" srcset="./assets/light/m-2-jetpack.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/light/plate-2-jetpack.svg">
  <source media="(max-width: 500px)" srcset="./assets/m-2-jetpack.svg">
  <img src="./assets/plate-2-jetpack.svg" width="100%" alt="II · jetpack — parallel gzip on JDK 25, drawn as the SIMD bus fanning into four deflate blocks stitched back to one gzip member: 422 against 66.2 MB per second single-threaded, 6.4 times, on an M1 Pro from a 3-fork JMH run. The against-self result is printed on the plate: the JDK's own Adler-32 intrinsic does 14.06 GB per second and is not beaten; the hand-vectorised checksum reaches 4.26, bit-identical to java.util.zip.">
</picture>

Parallel gzip on JDK 25 — one virtual thread per block, a bounded in-flight window so peak memory is independent of file size, and a byte-valid *single* gzip member rather than the concatenated members parallel compressors usually emit.

[live](https://jetpack-compress.vercel.app) · [system card](https://jetpack-compress.vercel.app/system-card) · [repo](https://github.com/yadava5/jetpack-compress)

---

<picture>
  <source media="(prefers-color-scheme: light) and (max-width: 500px)" srcset="./assets/light/m-3-glyph.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/light/plate-3-glyph.svg">
  <source media="(max-width: 500px)" srcset="./assets/m-3-glyph.svg">
  <img src="./assets/plate-3-glyph.svg" width="100%" alt="III · Glyph — SIMD kernels over a course-provided MNIST net, drawn as three register-lane bundles — NEON, AVX2, AVX-512 — converging on benchDot/256: 3.5× over the course baseline on the reference machine. The package that ships is WASM_SIMD128, 43,751 bytes, byte-identical to main and checked daily in CI. The against-self results are printed: the same flags run 10.7× slower on benchAxpy/128, below the size floor, and 97.01% is a training-time number — the test set that graded the net also picked its checkpoint.">
</picture>

The network is not mine: a course-provided C++ MNIST net. The work is what happened to it — hand-written SIMD kernels over a scalar fallback, with **Shree Chaturvedi** credited for kernel contributions. The React browser application is mine.

[live](https://getglyph.vercel.app) · [system card](https://getglyph.vercel.app/system-card) · [repo](https://github.com/yadava5/glyph)

---

<picture>
  <source media="(prefers-color-scheme: light) and (max-width: 500px)" srcset="./assets/light/m-4-automl.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/light/plate-4-automl.svg">
  <source media="(max-width: 500px)" srcset="./assets/m-4-automl.svg">
  <img src="./assets/plate-4-automl.svg" width="100%" alt="IV · AutoML — the dispatcher drawn as its registry: a 44-pin strip, one pin per tool the graph defines, with seven tool-set taps below it — no phase is handed all 44. The against-self line is the sandbox: it guards against accidents, not adversaries — the network is an env var the beta template renders as bridge, with no cap-drop, no pids-limit, no seccomp.">
</picture>

A dataset and a sentence in, a trained model out, over a LangGraph state machine and an MCP tool server. **GPL-3.0** at the commit this page pins; a relicence to PolyForm Noncommercial is proposed in [PR #5](https://github.com/yadava5/ai-augmented-auto-ml-toolchain/pull/5) and needs my co-author's review.

[live](https://agentic-automl-platform.vercel.app) · [system card](https://agentic-automl-platform.vercel.app/system-card) · [repo](https://github.com/yadava5/ai-augmented-auto-ml-toolchain)

---

<picture>
  <source media="(prefers-color-scheme: light) and (max-width: 500px)" srcset="./assets/light/m-5-cadence.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/light/plate-5-cadence.svg">
  <source media="(max-width: 500px)" srcset="./assets/m-5-cadence.svg">
  <img src="./assets/plate-5-cadence.svg" width="100%" alt="V · Cadence — the whole API drawn as one part: 37 route handlers enter one serverless function, and its single output passes through the one door in a wall — row-level security, FORCEd — before reaching the 7 tables behind it. The against-self line: five of six app-side guards are conditional, if context userId; a caller that forgets the identity still sends the query, and the database's refusal is the one that cannot be forgotten.">
</picture>

Type *lunch with sam friday 1pm* and get a calendar entry. The engineering is what the audit turned up: application code that filters by user is code that has to remember to filter, so the database enforces it instead.

[live](https://usecadenceapp.vercel.app) · [system card](https://usecadenceapp.vercel.app/system-card) · [repo](https://github.com/yadava5/cadence) · [the isolation suite](https://github.com/yadava5/cadence/blob/main/lib/__tests__/rls.postgres.test.ts)

---

<picture>
  <source media="(prefers-color-scheme: light) and (max-width: 500px)" srcset="./assets/light/m-6-applied.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/light/plate-6-applied.svg">
  <source media="(max-width: 500px)" srcset="./assets/m-6-applied.svg">
  <img src="./assets/plate-6-applied.svg" width="100%" alt="VI · Applied — the mail triage drawn as the part that ships: the rules layer grades a labelled strip of 96 messages and gets 2 wrong — 0.979 macro-F1, rules layer alone. Below it, drawn dashed with its lead left open, is the cascade: layer two, whose 0.9583 has no evaluation artifact — the run was overwritten. What is deployed runs only that first layer.">
</picture>

Your inbox already holds the verdict on most applications you have sent. Three layers read it, cheapest first, and anything under the confidence gate is withheld from the board and walked to a human. The model is allowed to say it does not know.

[live](https://getapplied.vercel.app) · [system card](https://getapplied.vercel.app/system-card) · [in-browser demo](https://huggingface.co/spaces/yadava5/jobtracker-classifier) · [repo](https://github.com/yadava5/applied)

---

<picture>
  <source media="(prefers-color-scheme: light) and (max-width: 500px)" srcset="./assets/light/m-7-visualassist.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/light/plate-7-visualassist.svg">
  <source media="(max-width: 500px)" srcset="./assets/m-7-visualassist.svg">
  <img src="./assets/plate-7-visualassist.svg" width="100%" alt="VII · VisualAssist — the alert policy drawn to scale from the phone in your hand: interrupt inside 0.5 m, pulse at 1.0, stay silent past 2.0. Below it, the settings slider the app actually shows — labelled in metres, its value read aloud — drawn with its lead ending open before LiDARService, the threshold it never consults. A live control that does nothing lies to the person the app is for.">
</picture>

An iPhone app for low-vision users, in Swift: ARKit LiDAR depth becomes speech and haptics, so the phone tells you what is in front of you before you reach it. MUCAT Design Innovation finalist, with a **$2,500** prototyping grant — attested, like §I. It is the one system here you cannot click into; it needs an iPhone with a lidar sensor in your hand.

[repo](https://github.com/yadava5/VisualAssist)

---

<picture>
  <source media="(prefers-color-scheme: light) and (max-width: 500px)" srcset="./assets/light/m-colophon.svg">
  <source media="(prefers-color-scheme: light)" srcset="./assets/light/plate-colophon.svg">
  <source media="(max-width: 500px)" srcset="./assets/m-colophon.svg">
  <img src="./assets/plate-colophon.svg" width="100%" alt="Colophon — the board's edge connector: the three buses land on their pads and leave the page. 58 claims, 58 commands, re-run in CI from pinned commits; what is my word rather than a derivation says so where it stands.">
</picture>

[`build/claims.json`](https://github.com/yadava5/yadava5/blob/main/build/claims.json) ties every derived number to a commit SHA and to the shell command that re-derives it from the blob at that SHA. [The gate](https://github.com/yadava5/yadava5/blob/main/.github/workflows/gate.yml) runs those commands on every push and once a day, rejects any number no row accounts for, and closes with a negative test that breaks the plates on purpose and fails if a check sleeps through it.

The guarantee is narrower than it sounds: **numbers are gated, prose is not.** Every false claim an audit has turned up on this page has been a verb, not a figure.

Everything above, with **LifeQuest** — a quest tracker for people rebuilding after a layoff or retirement — is collected at **[ayush-yadav.com](https://ayush-yadav.com)**.
