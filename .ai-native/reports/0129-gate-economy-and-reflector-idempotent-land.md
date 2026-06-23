# Report 0129 — Gate as a request economy, and the reflector's idempotent land

## The arc

Smoothing the gate/landing process — and landing the first real fix
under that lens. Across many turns with bdo, the gate was reframed as a
**request economy** with two registers, distinguished by the
*relationship* across the handoff, not by ceremony:

- **co-worker** (in-scope, same engineering family) — a *direct handoff*
  plus a shaped read (the Taster's Clause, D-14): organized, reasoned,
  the pick named. **Not** a ticket. This is the common case and the one
  to nail first.
- **service-desk** (cross-boundary only — to bdo or another team) — a
  typed **requisition** (deliberately not a "form": underneath it is a
  *slot* with a refusal-tooth), policy-driven and consequence-monitored,
  carrying an **SLA** (so work can't silently rot) and an **escalation
  route**, handled by an **expediter** who answers with favorite-customer
  warmth.

The unifying law: always serve a shaped, warm thing — never a cold dump,
never a cold ticket. The bright line that keeps it honest: a session may
self-authorize the **act** (the forgiveness tier — reversible, observable),
but never the **verdict on its own value** (D-2 stays independent).
Contributing real work to the substrate earns a wider forgiveness lane
(the herald-reputation hook).

The durable home for this design is the registered memory
`ontum-gate-request-economy`. The concrete first builds it names:

1. **Act-fence revival — land it.** It was MISSED only for want of a
   merge receipt — an ordering artifact, not a flaw in the work. Landing
   it lights the forgiveness lane.
2. The **typed-requisition + SLA + escalation** boundary fold (the
   service-desk register, cross-boundary only).
3. **Expediter** wiring through `loop/brief.py` (the warm shaped reply).

## What landed (the live proof)

Issue **#547** — the reflector was double-firing owner-ask mirror issues,
burying bdo's desk. Root cause was a **fleet-coordination race**: parallel
worktree sessions fork *before* the local reflection-ack exists, each opens
an issue, and the union-merged log keeps one ack while GitHub keeps both —
proven on the record by a single event carrying two issue URLs.

The fix makes the mirror **idempotent against the live surface** rather
than against the local log: a stable hidden per-kind marker key
(`report_id` for owner-asks, `version` for the stamp queue), read
exhaustively/paginated, refusing to mint blind on a read failure (no
blind-mint on a partial read).

- Atom: `atom.reflector-idempotent-mirror.v0`, independently value-gated
  (`rcp.2682800ec38c`).
- Landed as **PR #587 → merge `rcp.merge.587`** (commit `c7000f7`).
- A parallel duplicate fix **#581** was independently adjudicated — a
  neutral judge picked #587 on merit (#581's title-keying breaks because
  the title embeds the ask count, `owner_asks.py:78`) — and **retired with
  credit**.
- Issue #547 closed warm (`evt.fa95c0df1191`).

## Method (worth recording)

This was a **viewport-rooted STEERING seat** that conducted ~9
worktree-born builder agents end-to-end — the Administrator pattern, live:
build → adjudicate → branded value-gate → fix-until-review-clean loop →
ready → reconcile spurious `CONFLICTING` → branded merge-node land →
issue-pen close. The review loop ran **six rounds**, each catching a real
bug: Buffer → injection/args → digest-edit → limit-500/key-mismatch →
splitlines-unicode. Durable home: memory `ontum-steering-seat-conducts-builders`.

The governance teeth behaved exactly as designed and are worth naming as
*non-conflicts*: the spawn rail correctly forced node-acts (judge/land) to
be branded, and the workstation fence correctly kept the steering seat out
of the viewport and foreign benches.

## needs-you

1. **Direction on the gate-economy build order.** Recommendation (in
   `ontum-gate-request-economy`): land **act-fence** first to light the
   forgiveness lane, then the boundary **requisition** fold. Your call on
   sequencing.
2. **Two non-blocking reflector follow-ups, left tracked, not resolved** —
   a digest cross-worktree edit edge case, and defensive paths. Confirm
   they need no further action, or say the word and I file them.
3. **Spend note (awareness, not a decision):** this session ran ~9 builder
   agents to honor "keep fixing until the quality bar is met" (the six
   review rounds). Flagging the cost.

No material conflicts between instructions this session.

## End-state

`report` — the gate-as-request-economy design is shaped and homed in
memory (`ontum-gate-request-economy`); the first real fix under that lens
landed (PR #587 / `rcp.merge.587`, atom
`atom.reflector-idempotent-mirror.v0`, value-gate `rcp.2682800ec38c`),
the duplicate #581 retired with credit and #547 closed warm. Awaiting
bdo's direction on which gate-economy build to take first.
