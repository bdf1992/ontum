# Report 0093 — Sketch, ink, paint — the pen as one of three marks

**Date:** 2026-06-19 · branch `claude/pen-architecture-analogy-72boq5`

bdo asked to extend the **pen architecture** into a larger craft analogy —
Media / Medium / Method / Muse / Mode, with three referents (a pencil
sketch, a pen linework, a paint-over) — and to define the architecture,
implementation details, and how we leverage it against our flaws.

## What landed

- **`sketch-ink-paint.proposal.md`** (repo root, house `.proposal.md`
  form, matching `outcome-pressure-fold.proposal.md`). A design proposal,
  not adopted. Its spine:
  - **The pen is the *ink* of a three-mark making** — sketch (provisional,
    erasable), ink (committed, receipted), paint (additive, surfaced).
    ontum mastered the ink (the pens + their invariants) and left the
    sketch and paint stages unnamed.
  - **Load-bearing mapping:** comics penciller → inker → colorist are
    different hands, which *is* ontum's worker → reviewer → surfacer/owner
    (D-2 "no one signs their own line" = "the penciller doesn't ink their
    own pencils"; D-4 the colorist/owner is the last stop).
  - **The five M's are five axes** profiling each mark; the framework
    re-derives the existing pen invariants as the ink-stage method.
  - **Diagnosis:** every recurring backlog flaw is a *stage confusion* —
    off-log strands (sketch off-book), unadmitted actors (ink by an
    un-admitted hand), mocks (pencil in ink's slot), idle organs (a pen
    that laid no mark), parked owner-asks (paint on the wrong wall),
    slow-loop write-back (a stroke the colorist may not yet lay).
  - **Implementation** is a label + a read-only fold + a boundary check on
    existing pens — no new write path.

- **bdo's mid-session correction folded in as the proposal's centre**
  ("The book keeps everything"): a pencil sketch belongs **on the log
  too** — erased, it still leaves a trace (the whiteout/supersede ghost) —
  because *comparison is how the system gets better*. This fixed a real
  contradiction in the first draft (sketch was defined off-log while
  off-log strands were diagnosed as a flaw). One book; the eraser leaves a
  mark; the first build now leads with a sketch primitive that lands a
  draft **on the log**.

- Committed via the git pen, pushed via the PR pen to
  `claude/pen-architecture-analogy-72boq5`. No PR opened (not requested).

## needs-you

The proposal ends with four open questions (it is a conversation, not an
adopted change). The load-bearing one:

- **Un-admitted writes: accept-and-stamp-sketch, or refuse at the seam?**
  My lean is accept-and-stamp — hard refusal would have stranded the
  merge-node's 22 landings instead of making them visible (repeating the
  off-book failure). The other three: is "mark" a doctrine concept or a
  fold label; does naming the sketch surface change *who* may ink (lean:
  no); and first-build scope (epic vs single done-line).

- Nothing blocking. The proposal is a sketch itself — react to it, or let
  it sit on the book as a ghost to compare against.

## End-state

`report` — `sketch-ink-paint.proposal.md` written, corrected to bdo's
"one book / the eraser leaves a trace" principle, committed and pushed to
`claude/pen-architecture-analogy-72boq5`; four open questions parked for
bdo; no PR opened.
