# Done-line 0096 — Causality canvas ingests the real term-economy projection

Written before code, per §9.4. When this line is met, stop.

> **Arc:** causality-canvas

Probe **CZ3** of `outcomes/causality-outcome-pressure.probes.json` — *Causality
ingests real Ontum evidence*: today the editable canvas only ever shows demo
templates; the real log/atoms/term-projection never reach it. bdo's steer
(2026-06-17): do not build a general ingestion pipeline — **demonstrate the
required capability against an arbitrary but genuinely-real dataset**, and do
not slow down for a perfect one. The arbitrary-real dataset the repo already
produces, byte-deterministically, is `causality/examples/ontum-terms.projection.json`
(`term_economy.py project --write`): real terms, real evidence files, real
classes. This lands a deterministic adapter from that committed projection into
the canvas's own `fromJSON` graph shape, wired into the live surface, with §10
teeth — it does not double-build the fold (it reads its committed output) and
keeps Causality a projection, never a second source of truth.

> **Done when:** a pure, deterministic adapter (`causality/ingest.js`) turns the
> *committed* term-economy projection into the canvas graph shape — each real
> term a node carrying its real class, each real evidence file a node, each
> resolved `evidence_edge` a link — so the editable `canvas.html` loads real
> Ontum evidence (not a demo template) through one wired action and the existing
> `toJSON`/`fromJSON` persistence round-trips it; proven by a headless §10 check
> (`node causality/ingest.test.js`) that runs over the real committed bytes,
> asserts the node/edge counts and classes match the projection, and **has teeth**
> — an `evidence_edge` whose term is absent from the projection is *refused*
> (no dangling node invented) and the refusal is reported, a negative control
> the test would fail to catch if the adapter silently passed it; and
> `outcomes/evidence/cz3-ingest.md` attests the re-runnable drive.
