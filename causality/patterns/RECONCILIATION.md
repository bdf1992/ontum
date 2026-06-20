# RECONCILIATION — the "four registers" vs display-system.md

*bdo's call, 2026-06-16: reconcile the rubric's four registers with the
live spec (`causality/display-system.md`) before canonizing anything.
Done. This is the decision record that unblocks the register / topo /
async issues filed in round 1.*

## What the rubric (mine) claimed
Four truth registers as ONE axis: RECORD / RUNTIME / REQUEST / SIMULATION
(ink vs pencil).

## What display-system.md actually has (the authority)
- **Strata** — epistemic axis: fundamental / derived / learned (C1–C3). Channel: colour / layer (H4).
- **Anima** — felt axis: strength × tempo (C18). Channel: size & motion.
- **Two edge registers** — sync TypedConnection (C10) / async TypedIteration (C11).
- **A generative-typing lifecycle** — propose → ground → grade → admit (proposed → minted, D-4).
- **Divergence verdict taxonomy** — minted/projected/proposed/poetic/overloaded/orphaned/ghost (C4).
- The four registers RECORD/RUNTIME/REQUEST/SIMULATION appear **nowhere**.

## The finding — the rubric conflated TWO axes under one word
1. **COMMITMENT (ink vs pencil)** — durable record or proposal/simulation? NOT new:
   it is the existing lifecycle + the fundamental append + the C4 proposed/ghost classes.
   - RECORD (ink) = an admitted/minted type, or a fundamental append.
   - REQUEST (pencil) = a *proposed* type bound to a pen (lifecycle "propose"; the virtual-request-node; an NL draft awaiting admission).
   - SIMULATION (pencil) = a dry-run/preview, or a learned datum not yet graded vs its oracle.
2. **RUNTIME** — happening / parked right now? NOT a commitment state; it is PROCESS,
   already carried by anima-tempo (fast↔slow) + node activation + the async edge register.
   "Parked/in-flight" = a runtime-blocked process state, not a register.

So there are not four co-equal registers. There is **one commitment axis**
(proposed → simulated → admitted; pencil → ink) bound to the lifecycle, and
**runtime lives on the anima/process side**.

## The result — a THIRD cross-cutting facet (completes the triad)
display-system names two cross-cutting facets (strata, anima). This names the
third the lifecycle already implies but never labeled:

> **REGISTER = COMMITMENT** — where a unit sits on propose→admit; ink = admitted, pencil = proposed/simulated.

Three orthogonal facets, three channels (bdo's grammar, 2026-06-16) — no collisions:

```
strata (epistemic)     -> colour / layer        (display-system H4)
anima  (felt)          -> size / motion         (display-system C18)
register (commitment)  -> line-treatment + badge (solid=ink / dashed=pencil)
```

A node carries all three; no two facets compete for a channel.

## What this unblocks (round-1 corrections)
- **register family** — re-ground on the lifecycle (propose→admit) + C4 verdict
  classes; **drop the false display-system.md citation** (the ghost). pencil-vs-ink =
  proposed vs admitted; ghost-vs-record = the C4 ghost class (already exists);
  settle-on-commit = the admit step; provenance-trace = C15.
- **topo:register-strata** — was conflating commitment with epistemic origin; now two
  clean facets. A node's stratum (colour) and its commitment (line) are independent.
- **async** — parked/runtime is NOT a register; re-score those patterns on the
  anima-tempo / process side, not the commitment axis. Resolves 4-vs-5.
- **RUBRIC axis #1** — redefined from "four-register-bearing" to "commitment-bearing."

## Proposed amendment to display-system.md (awaits bdo's bless — D-4, his spec)
Add a C18-sibling: **C19 · RegisterFacet (commitment)** — the third cross-cutting
facet, ink/pencil bound to the generative-typing lifecycle, rendered on the line
channel. PROPOSED, not written — display-system.md is bdo's spec.
