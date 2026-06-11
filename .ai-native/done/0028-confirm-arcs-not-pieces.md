# Done-line 0028 — confirming an arc: the owner steers arcs, the loop carries pieces

Written before code, per §9.4. When this line is met, stop.

> **Done when:** bdo can confirm an *arc* — `loop.node confirm-arc --epic <id>
> --by bdo`, an admitted `arc_confirmed` record — and that one confirmation is
> his standing stamp for every piece under the epic: the loop satisfies the
> owner-stamp on his confirmation (the receipt cites `authorized_by`) and
> carries the arc's pieces, while an *unconfirmed* arc's pieces still park for
> him. He is escalated only by a gate's refusal (the existing reject→park) or
> by completion. Confirmation is his alone (`--by bdo`, unknown epics refused),
> withdrawable (`--off`, superseding). The `loop.node arcs` view shows what is
> confirmed. §10 proof: a confirmed arc's atom auto-stamps and reaches done; an
> unconfirmed one parks; the firm invariant "the owner is the last stop" is
> moved up to arc scale, not removed — and that is recorded in loop/CLAUDE.md,
> not worked around silently.

## Why (bdo, 2026-06-10)

"far too many escalations to me and too many open items that require my direct
attention." The diagnosis: every piece shipped as its own stamp, and work
bypassed the loop's gates straight to his merge, so he carried 100% of
confirmation. This is the lift he named — confirm arcs, not pieces.

## Out of scope, named (later increments)

- **Work flowing through the loop as atoms.** This makes the owner-stamp
  arc-confirmable; it does not yet route the *building* (still code→PR). Until
  increments enter as atoms through the gates, arc-confirmation drains only the
  atom queue, not the PR queue. Changing how work enters is the larger move.
- **An arc-completion signal.** Escalation on refusal is the existing
  reject→park; a "your arc completed" surface (inbox/arcs) is a read worth
  adding next.
- **next_action arc-awareness is threaded only where the owner's queue is read
  (inbox).** Other callers keep the await classification until the pass stamps;
  harmless (the loop drains on its beat), tightened later if it matters.
