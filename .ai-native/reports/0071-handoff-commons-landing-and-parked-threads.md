# Report 0071 — handoff: train mode shipped, the Commons one stamp from landing, threads parked

## What landed

- **Train mode — the first security mode (PR #169, MERGED to main).** Node 1
  (done-line 0096): a signed `security_mode` admission + bdo-gated
  `mode-train start|stop` verb (`loop/node.py`), the `active_mode` fold
  (`loop/reconcile.py`, fail-strict to `normal`), and `command_guard.py`'s
  observe / `would-deny` / exit-0 fork under train — observe-everything,
  block-nothing, fails strict. Node 2 (done-line 0097): `loop/train.py`, a
  read-only fold that turns a session's `would-deny` readings into a
  *proposed* stricter mode, and proposes nothing from no evidence. §10 teeth
  on both; 812 green at merge.

## What's floating

**At bdo's stamp (one gesture each):**
- **PR #174** (`claude/home-patterns`, OPEN) — the evolved Pattern Commons v1
  homed at `causality/patterns/`, governed; `merge.py` reproduces v1
  byte-identical; 803 green. Awaits **arc-confirm** (read as
  `epic.causality-surface`) → merge-node lands it. (This report rides in #174.)
- **v1 is PROPOSED** — promoting the Commons past `proposed` is bdo's (D-4).
- **C19 · RegisterFacet** — the third cross-cutting facet (commitment → line
  channel) the reconciliation named; proposed in
  `causality/patterns/RECONCILIATION.md`, deliberately NOT written into
  `causality/display-system.md` until bdo stamps.

**Parked — specs on disk, unbuilt:**
- **Theme A** — the portfolio register fix for bdo's four refusals (too dark /
  typography / arbitrary pacing / flat). Refusals lifted to intent in
  `causality/patterns/DEPOSITS.md`. The reviser was stopped at a pivot — UNBUILT.
- **The variation lab** — an interactable theme/variation array bdo steers by
  *use* (= Causality's own interaction model: typed 4D graph, recursive
  embedding, AI routing/provisioning). Full spec in
  `causality/patterns/LAB-PARKED.md`. Agreed sequence: finish Theme A first,
  then decide; foundry-first, home to `causality/` after.
- **Train-mode node 3** — the install verb (a bdo-gated pen that admits a
  *proposed* stricter mode → real enforcement). The fold proposes; nothing
  installs tightening yet. bdo's gate.

**Open question, unanswered:**
- **In-page virtual element iteration + versioning** (bdo's concept). Working
  read: every surface element a *versioned virtual object* you iterate in
  place — ontum's content-hash / supersession discipline brought into the
  surface. bdo pivoted before confirming whether he meant a specific technique
  or that capability. Folds into the variation lab.

**Ambient summons, left parked:**
- `value-gate.claude.v1` is summoned on `atom.serve-causality-surface.v0`
  (serve Causality's experience layer at a public URL bdo reaches from his
  phone; static-artifact publish; the loop stays local-first). Awaits a
  value-gate verdict.

**The product underneath:**
- **Causality CZ1–CZ4** (persistence / per-node config / real-data ingest /
  typed graph). The actual surface all the Commons / portfolio / lab work
  serves; still the unbuilt core. The loop points at CZ1/CZ3.

## Where the specs live

`causality/patterns/` (landing via PR #174): `pattern-commons.v1.json`
(library), `families/` (sources), `merge.py` (the deterministic fold),
`portfolio.html` (playable witness), `RUBRIC.md` (AI-native gate),
`RECONCILIATION.md` (register triad + C19), `DEPOSITS.md` (bdo's refusals),
`LAB-PARKED.md` (variation lab), `PORTFOLIO-DONE.md` / `LOOP.md` / `ISSUES.md`
(the loop record). The foundry original at `experience-foundry/evolution/` is
now a scratch copy; the repo is canonical.

## needs-you

- Confirm PR #174's arc → land the homed Commons.
- Promote v1 past PROPOSED (D-4) when you've looked.
- Stamp or decline the C19 · RegisterFacet amendment to `display-system.md`.
- (Not yours, flagged so it is not lost: the value-gate summons on
  `atom.serve-causality-surface.v0` awaits a verdict.)

## End-state

`report` — train mode shipped to main; the evolved Pattern Commons is one
arc-confirm from landing (PR #174); the portfolio register-fix (Theme A), the
variation lab, and train-mode node 3 are parked with specs on disk under
`causality/patterns/`; a fresh session can take any thread cold.
