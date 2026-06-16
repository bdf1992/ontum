# CZ2 — per-node / per-edge configuration (evidence)

> Probe **CZ2** of `outcomes/causality-outcome-pressure.probes.json`:
> *click node → config panel for its type; click edge → its config; a field
> change persists.* Resolves **met** when this file exists and attests a real,
> re-runnable drive (not aspirational prose).

## What the panel does

The inspector (`causality/inspector.js`) is the schema-driven, per-element config
panel, mounted by both the full canvas (`canvas.html`) and the component gallery
(`demos.html`) from one source. Selecting a node renders the fields **for its
type** — the typed `SCHEMA[type]` group plus the common and holonic groups — and
editing a field writes through `Causality.setPath` and fires the engine's
`onchange`. Selecting an edge renders the route config (the `EDGE_SCHEMA` fields:
`sign`, `kind`, `gain`, `delay`). Because the edit goes through the same schema
that `toJSON` serializes, a field change persists across a save→reload.

## The drive (re-runnable, with teeth)

```
node causality/inspector.test.js
```

It mounts the **real** inspector on a minimal DOM, fires the **real** input
events, and asserts:

- an *inference* node's panel shows its typed field (`prompt`) and **not**
  another type's field (`gate.mode`); a *gate* node's panel shows `gate.mode`
  and **not** `prompt` — the panel is config **for its type**, not a dump of
  every field (the teeth on "for its type");
- selecting an edge renders the `route` panel with its edge-schema fields;
- a node field edited *through the panel* survives a save→reload round-trip;
- an edge field (`gain`) edited *through the panel* survives the round-trip;
- negative control: a value typed into the box whose commit event **never
  fires** does **not** persist — so the persistence above is caused by the
  input→commit wiring, not by a side effect (the teeth on "a field change
  persists").

Last run: `PASSED — the inspector edits per node and per edge, and edits persist
(with teeth)` (10 checks green).

This complements `canvas.persist.test.js` (CZ1, the serialization core): CZ1
proves the graph round-trips; CZ2 proves the panel that authors per-element
config feeds that round-trip. The live browser surface is
`http://localhost:8080/causality/canvas.html` (click a node, edit a field;
click a wire, edit its route; reload — the edits return).
