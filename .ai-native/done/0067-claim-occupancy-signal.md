# Done-line 0067 — The claim: a session's prospective stake on a piece of work, with liveness read off the log

Written before code, per §9.4. When this line is met, stop.

Serves `epic.the-field` (bdo-confirmed): the loop's situational reality — its
horizon names "who or what is currently occupying that node." Today the log is
purely *retrospective* (a receipt records what happened); nothing records what a
session *intends or is doing now*, so two sessions raced the same goal (done-line
0062, the governed inference plane, built in parallel — report 0054 vs this
session's redundant /goal) with zero visibility into each other. The **claim** is
the prospective dual of the receipt: the forward-looking record that closes that
blind spot. The same record is `epic.virtual-fleet`'s *running* occupancy
(declared-vs-running).

> **Done when:** a session can see who is already working a piece *before* it
> starts, and the loop can tell *done* from *dropped* — all read off the log:
>
> 1. **The claim record** — a `claim` admitted record `{claimer (the session's
>    branch), target (a done-line / epic / atom id), ts}`, written through one
>    verb, append-only, superseded-never-erased. A claim **grants nothing**
>    (D-4) — it is a coordination *signal*, never a lock and never an
>    authorization.
> 2. **The occupancy fold** — a read-only fold (`loop.claims`) computing each
>    claimed target's state straight off the log + branch state, in three values:
>    - **active** — the claimer's branch is alive and the target's *proving
>      receipt* has not landed → a session is on this now;
>    - **satisfied** — the receipt that proves the target has landed → done, with
>      its evidence attached; don't redo;
>    - **abandoned** — the branch is dead/merged-away and no proving receipt
>      landed → dropped, free to re-pick.
> 3. **Supporting documentation is derived, not hand-listed** — the claim carries
>    one explicit forward reference (its target); the fold gathers the produced
>    receipts/atoms/report by *(target, branch)* so the trail can never drift
>    from the log. A claim is the missing *join key*: the effort/session axis the
>    three log streams lack.
> 4. **Auto-claim at one real seam** — minting/working a done-line through the
>    records pen writes its claim, so the fold is not dead-on-arrival (the way
>    `loop.minds` sat empty until something fired it).
> 5. **Surfaced at pickup** — the summon hook tells a session, for the gap it is
>    handed, whether that target reads *active* (and by which branch) **before**
>    it starts; an *abandoned* claim never warns.
>
> **The §10 teeth:** the three states must *discriminate*, or the fold is theatre
> — an **active** claim warns a second session at pickup (two sessions on one
> live target both read active: the exact warning the 0062 race needed); a
> **satisfied** claim reads "done" and names its receipt; an **abandoned** claim
> (dead branch, no receipt) reads "free" and does **not** warn — so a ghost
> session can never lock work. A claim naming no target, or a target not on the
> log, is refused. A claim and a log that disagree about a target's existence
> refuse to fit, and the verb is the gate that notices.

## Non-example (looks done, isn't)

A claim that is a hard lock a dead session holds forever (the *abandoned* state
exists precisely to refuse this). A claim that confers authority or gates
anything bdo-owned (it is advisory; D-4). Hand-listed supporting documentation
that drifts from the log. An occupancy view that collapses *done* and *dropped*
into one "not-active" — the whole value is telling "already built, don't redo"
from "abandoned, free to take." A claim surfaced nowhere at pickup (occupancy no
session reads is the retrospective log again).

## Out of scope, named

- **The virtual-fleet conductor** — spawning seats to fill an unclaimed gap is
  `epic.virtual-fleet`'s convergence; this builds the *running-occupancy record*
  it will read, not the apply pen.
- **Auto-claim at every seam** — one seam (the done-line pen) proves it;
  branch-creation and summon-acceptance claims are later increments.
- **Subsuming the fleet-safe-id guard** (done-line 0060) — it is already the
  narrow *id-claim* special case; this fold reads compatibly, but the guard's
  commit-time hard block stays where it is (soft signal early, hard block late).

The natural build order: the claim record + verb first, the three-state fold
second (the value), then the one auto-claim seam and the summon surfacing
(adoption). Out of room means ship the smaller whole — the record + fold + one
surfacing — never a half-wired signal no session reads (§9).
