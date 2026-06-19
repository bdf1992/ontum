# The code-review gate (PROPOSED) — the next chapter of anthology.self-governing-loop

**Status:** PROPOSED. Shape locked with bdo via /ask (2026-06-18); this spec is
the foundation. The reviewer node prompt is written
(`.ai-native/nodes/code-review.claude.v1.md`). The `PIPELINE` cutover + the
merge-node precondition are the **careful, high-blast-radius increment** that
follows — deliberately not rushed; this doc is its reviewed plan.

## Why

bdo, 2026-06-18: *"you must requisition a code review to consider your work
landed."* The intent rule (#232) made that behavioral; this is its structural
teeth. Code review is a **distinct sensor**: value-gate asks "worth it?",
value-confirm asks "delivered?", and neither reads the code for correctness or
clarity. It is the third A made enforceable — **authority** (may this land —
is it correct?) checked before the merge-node lands, its **attribution** a
signed receipt by an independent reviewer, never the author (D-2).

## The two halves (bdo's /ask picks)

1. **A real `PIPELINE` stage** — code-review, summon-queued like every gate;
   its verdict is a receipt.
2. **A merge-node precondition** — the merge-node refuses to land any PR whose
   atom lacks a `code.reviewed = clean` receipt (the off-log-gate pattern,
   extended from "has an atom" to "passed review").

Reviewer: an independent **spawn-rail node** (`ontum-node:code-review.claude.v1`,
branded + rung-checked) for normal changes; **escalate to cloud
`/code-review ultra`** for high-blast-radius changes (reversibility ×
uncertainty sets the depth).

## The PIPELINE insertion

A new stage between handoff and value-confirm (code-correctness before
delivery-confirm):

```
handoff.ready --[code-review]--> code.reviewed --[value-confirm]--> atom.value_confirmed
```

- new stage: `{event: "handoff.ready", seam: "handoff-to-review",
  node: "code-review.mock.v0", verdict: "clean",
  next_event: "code.reviewed", state: "code_reviewed",
  terminal_expected: ["clean", "needs_changes"]}`
- value-confirm's input event changes `handoff.ready` → `code.reviewed`.

## The migration (the dangerous part — design it before touching code)

Inserting a stage means the fold now requires `code.reviewed` *before*
`atom.value_confirmed`. Two ways this bites, each with its handling:

1. **Settled atoms must stay settled.** ~25 atoms are already
   `value_confirmed` under the old pipeline (handoff.ready → confirm, no review
   in between). The fold must NOT re-open them for a now-missing
   `code.reviewed` event. **Handling: grandfather** — an atom whose
   `atom.value_confirmed` event predates the stage's introduction is complete;
   the fold treats a pre-existing terminal as terminal. (Equivalently: the
   stage applies only to atoms created at/after its admission.)
2. **Live in-flight atoms must not stall.** Atoms past handoff but not yet
   confirmed should flow, not block, while the stage is mock. **Handling:**
   the stage ships as `code-review.mock.v0` (auto-verdict `clean`), so
   in-flight atoms auto-pass it; it only bites once `admit-real` names the
   real node. Doctrine: every stage starts mock, becomes real by admission.

**§10 teeth (the test that must pass before this lands):**
- a settled atom (value_confirmed pre-stage) stays settled after the stage is
  added — the migration didn't un-finish history;
- a fresh atom created after the stage cannot reach value_confirmed without a
  `code.reviewed` event;
- once real, a fabricated reviewer that always says `clean` fails an eval with
  a planted bug (the gate can actually refuse).

## Build order

1. **[done]** the reviewer node prompt (`code-review.claude.v1.md`).
2. add `code-review.mock.v0` to `PIPELINE` + value-confirm rewiring + the
   migration handling + the §10 migration test. *(The high-blast-radius
   increment; its own dedicated session, itself code-reviewed — bootstrap via
   `/code-review ultra` since it edits the core fold.)*
3. the merge-node precondition (refuse land without `code.reviewed = clean`),
   inert until the stage is real.
4. `admit-real code-review.mock.v0 → code-review.claude.v1` (bdo's stamp) +
   grant the reviewer class its rung (bdo, via rung-intake).
5. wire the spawn-rail reviewer + the cloud-ultra escalation path.

## Relationship to PR #237 (the generative QC standard) — reconciled

PR #237 captures a *generative quality-control standard* for **ambient
operations**: a capability-indexed, self-updating `derive_type` an operation
generates an expectation from and scores the actual against (meters:
impact/energy/heal), with **airgaps** so the judged cannot move its own bar
(the "bar becomes a mirror" failure). Reconciliation (bdo authorized,
2026-06-19):

- **Not a duplicate, and not a merge.** Different *object* and *judgment
  shape*: #237 scores **continuous operation** against meters; code-review
  makes a **discrete pass/fail** call on a **code diff** at the landing seam.
  Correctness/clarity is not meter-scored; ambient smoothness is not
  diff-reviewed. Forcing one into the other weakens both — code-review is
  **not** an instance of #237's standard.
- **Shared principle — inherited, not reinvented.** #237's load-bearing
  insight is the **anti-mirror / airgap** law: a quality bar must not rise to
  whatever the system already does, or the teeth never bite. That is exactly
  code-review's §10 risk ("a fabricated reviewer that always says `clean`").
  Code-review's teeth **cite #237's airgap** — its AG-2 ("capability-admission
  must not move the bar in the same act") maps onto "passing review must not be
  inferred from the code passing its own tests" — rather than authoring a
  weaker copy.
- **Build order:** independent. Code-review builds on its own and references
  #237's principle for its anti-mirror teeth. They are **siblings** under one
  quality theme, serving different arcs (session-gateway vs
  landing-throughput-response), not one framework.

## Open / named

- The migration handling (grandfather vs created-after-admission) is the one
  real design choice in step 2 — pick whichever the fold expresses most simply
  without a second source of truth.
- Whether `needs_changes` sends the atom back to a build stage or parks it for
  the author (the seam's send-back semantics) — settle in step 2.
