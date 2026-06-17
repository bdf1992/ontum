# Report 0077 — The cadence: name a part, nail it to one shot, over and over

## What landed

bdo's request: *name and nail one part and decompose it until you can do it in
one shot — over and over and over.* I ran his own decomposition procedure on my
own work, three clean nails this session, each a one-shot node with teeth and a
receipt.

**Done-line 0104 — the change-axis gate** (the procedure's teeth): a pure
read-only stdlib fold judges a declared decomposition manifest and refuses
`smeared-axis`, `dependency-cycle`, `uncontracted-seam`, `incomplete-axis`,
`smuggled-seam` (the AI-native contract missing trust/authority/change_rate).
bdo's UI split is the coherent anchor; the §10 test derives each break by one
mutation and proves the gate non-vacuous.

**Done-line 0105 — the undercut detector** (the dual): a module may declare
`also_changes_for`; the gate refuses it as `undercut-axis` — two axes collapsed
into one module — distinct from the two-modules-one-axis overcut. 11 gate tests
green.

**The gate bites reality** (`decompose/examples/loop-layering.manifest.json`): a
declared reading of ontum's OWN documented fold-layering (reconcile <-
orchestrate, reconcile <- slowloop, slowloop <- disposer) is judged `coherent`.
The check now judges a real part of the system, not a toy — and the loop's
layering survives its own change test.

The cadence in one line: **name → decompose to one-shot leaves → build → green
test (the receipt) → commit → next.** Each refusal is one hardened invariant;
they compound.

## needs-you

(gh CLI is unavailable in this container, so the reflect mirror cannot open
issues; these are surfaced to the surface bdo is actually reading — the chat —
and here.)

- **The next one-shot is named and pickable:** wire the gate into the loop as a
  `decomposition-drift` gap kind (loop/gaps.py) + a summon surface, so a refused
  decomposition nags ambiently like every other gap. Its one open sub-question
  before it is truly one-shot: *which manifests are watched* (a committed
  `decompose/*.manifest.json` glob vs. a registry). Name the rule and it is one
  shot.
- **The agnostic fork stays spent on AI-native** unless you want plain non-AI
  designs judged too (contract fields become optional-by-kind — a schema move).

## End-state

`report` — three one-shot nails landed and committed on
`claude/decomposition-change-axes-a57frr` (done-lines 0104, 0105, plus a real
ontum manifest the gate judges coherent); full gate suite green. The cadence is
demonstrated and the next nail is named. Ready to push.
