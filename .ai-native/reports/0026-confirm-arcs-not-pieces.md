# Report 0026 — confirming an arc: the lift from stamping pieces to steering arcs

## What landed

**[done-line 0028](../done/0028-confirm-arcs-not-pieces.md) — met.** bdo's own
diagnosis turned into mechanism: *"far too many escalations to me ... I need to
know why."* The why was that every piece shipped as its own stamp and the work
bypassed the loop's gates straight to his merge — so he carried 100% of
confirmation. This makes the owner's stamp arc-confirmable.

- **[loop/reconcile.py](../../loop/reconcile.py)** — `arc_confirmation()` folds
  `arc_confirmed` admissions; `pass_once` now, at the owner-stamp stage of a
  *confirmed* arc, satisfies the stamp on bdo's standing confirmation instead of
  parking — the receipt carries `authorized_by` (the confirmation's id), so it
  is attributable to his actual decision, at arc scale.
- **[loop/node.py](../../loop/node.py)** — `confirm-arc` (bdo-only, unknown
  epics refused, withdrawable with `--off`) and an `arcs` view of what is
  confirmed; the owner inbox no longer lists a confirmed arc's pieces.
- **[loop/orchestrate.py](../../loop/orchestrate.py)** — `next_action` is
  arc-aware: a confirmed arc's owner-stamp classifies as the loop's to take.
- **[loop/CLAUDE.md](../../loop/CLAUDE.md)** — the firm invariant is amended on
  the record: "the owner is the last stop — *at arc scale*." His stamp is moved
  up a level, not removed.
- **[tests/test_arc_confirm.py](../../tests/test_arc_confirm.py)** — the §10
  proof: a confirmed arc's atom auto-stamps and reaches done; an unconfirmed one
  parks; only bdo confirms. Suite: 220 OK.

## needs-you

- **Stamp this PR** (arc-confirmation, done-line 0028) — and it is itself the
  last per-piece stamp before the lift: once merged, you can
  `confirm-arc --epic epic.experience-layer --by bdo` and its pieces stop
  pinging you.
- **The honest limit:** this drains the *atom* queue. The building still enters
  as code→PR, so the PR queue only shrinks once increments flow through the loop
  as atoms. That is the next move and the bigger one — named in the done-line.

## End-state

`report` — the owner's stamp lifts from piece to arc: one `confirm-arc` is a
standing authorization the loop carries pieces under, escalating only refusals.
The mechanism bdo asked for exists and is proven; closing the PR-bypass so the
loop metabolizes the building itself is the named next step. Ready for your
stamp.
