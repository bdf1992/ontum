# CZ1 — Causality persists authored graphs (evidence)

> Probe **CZ1** of `outcomes/causality-outcome-pressure.probes.json`:
> *Causality persists authored graphs.* Resolves **met** when this file exists
> and attests a real, re-runnable drive (not aspirational prose).

## What persists, and how

The canvas engine (`causality/canvas.js`) carries a schema-driven save/restore
pair, `toJSON` / `fromJSON` (done-line 0082). A graph the user authors — nodes
with their typed config, the holonic `strata`/`anima` fields, edges with their
`sign`/`kind`/`gain`/`delay` — serializes to a plain object and restores into a
fresh engine. In the live surface (`canvas.html`) that object round-trips
through `localStorage` and file export/import; the durable claim is the
round-trip itself.

## The drive (re-runnable, with teeth)

```
node causality/canvas.persist.test.js
```

It builds a graph, edits a typed-config field (`prompt`), two holonic fields
(`anima.strength`, `strata.derived`), and adds a new node with its own config
(`gate.mode`); serializes; wipes into a **second** engine; restores; and asserts
every edited field and the new node survived the reload. The teeth: a negative
control drops a field before saving and asserts it is **detectably lost** — so a
serializer that silently forgot a field would fail the test, not pass it.

Last run: `PASSED — persistence round-trip holds, with teeth` (10 checks green).

This is the evidence the fold can re-run, not a procedure it cannot. The live
browser surface is `python -m http.server 8080` →
`http://localhost:8080/causality/canvas.html` (build a graph, reload, it
returns); the committed test is the deterministic proof of the same claim.
