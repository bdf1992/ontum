# CZ3 — Causality ingests real Ontum evidence (evidence)

> Probe **CZ3** of `outcomes/causality-outcome-pressure.probes.json`:
> *Causality ingests real Ontum evidence — the editable canvas loads real
> log/atoms/term-projection, not demo data.* Resolves **met** when this file
> exists and attests a real, re-runnable drive (not aspirational prose).

## What is ingested, and from where

The dataset is not invented for the demo: it is
`causality/examples/ontum-terms.projection.json`, the **committed, byte-deterministic
output** of the term-economy fold (`python causality/term_economy.py project --write`).
It carries the repo's own vocabulary — real terms (`arc`, `atom`, `node`, `receipt`,
`seam`), their real classes (`overloaded`, `minted-runtime`, …), and 16 real
`evidence_edge`s pointing at real files (`loop/reconcile.py`,
`.ai-native/log/admissions.jsonl`, the epic JSONs). Per bdo's steer (2026-06-17),
this is the *arbitrary-but-genuinely-real* register of the capability — not a
general ingestion pipeline, and not synthetic demo data.

`causality/ingest.js` is a pure, deterministic adapter from that projection into
the canvas's own `fromJSON` graph shape: each term → a `source` node carrying its
real class in `data`; each evidence file → a `sink` node; each *resolved* edge →
a link. It **reads** the fold's committed output — it does not re-build the fold —
so Causality stays a projection, never a second source of truth (the directory's
one hard rule).

## The drive (re-runnable, with teeth)

```
node causality/ingest.test.js
```

It reads the **actual committed projection bytes** (no fixture), converts them,
and loads the result into the real `canvas.js` engine, asserting: one node per
real term; each node carrying its real class; links equal to the resolvable
evidence edges; the graph round-trips through `toJSON`/`fromJSON` (the real class
survives a reload). The teeth (§10): a tampered projection gains an
`evidence_edge` from a term it never lists — two locally-fine records that refuse
to fit — and the test asserts the adapter **invents no dangling node** and
**reports the refusal** rather than passing it silently. An adapter that quietly
drew the ghost node would fail this test, not pass it.

Last run: `PASSED — the canvas ingests real Ontum evidence, with teeth`
(13 checks green).

## The live surface

`python -m http.server 8080` → `http://localhost:8080/causality/canvas.html`,
then **load real ontum** (the new button): the canvas fetches the committed
projection, ingests it through the same adapter, and renders the real term graph
in place of a demo template — reporting `N terms · M evidence files · K edges`.
The committed test is the deterministic proof of the same claim the button
performs.
