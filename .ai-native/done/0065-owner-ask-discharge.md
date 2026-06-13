# Done-line 0065 — Owner-asks gain a log-backed discharge: a resolved ask is closed by citing the record that closed it

Written before code, per §9.4. When this line is met, stop.

Serves `epic.owner-harness` (bdo-confirmed): spend bdo's attention like it is
the most expensive resource — and do not cry-wolf his floor. The owner-ask beat
(done-line 0058) knows two states: an ask is *stranded* or *surfaced to his
inbox*. It has no third state for an ask a later session genuinely **resolved**,
so it screams resolved work forever — exactly what desensitizes a floor. The
open-only design is deliberate ("a free-text ask carries no log-backed answered
signal"); this adds the missing signal **without** handing a session a free
stop-card: a discharge is not a session's say-so, it is a pointer at the record
that closed the ask.

> **Done when:** a session can silence the owner-ask floor for a *resolved* ask
> — and ONLY by citing the log record that closed it:
>
> 1. **A discharge record** — a new admission type `owner_ask_discharged`, keyed
>    on the ask-**group** id (the per-report grain the beat screams), carrying
>    **one or more cited resolving record ids**, a one-line reason, and `--by`.
>    Written through one verb: `python -m loop.reflect discharge-ask --ask
>    <group-id> --cite <record-id> [--cite <record-id> ...] --reason "<why>"
>    --by <who>`. Append-only; a re-run over the same set folds to one (I-2).
> 2. **The cite is verified, never trusted** — the verb **refuses** a discharge
>    whose `--cite` names a record not on the log (no event/receipt/admission
>    with that id), **refuses** an empty cite set, and **refuses** an `--ask`
>    that is not a live owner-ask group. A discharge that cannot point at a real
>    closing record is rejected and writes nothing.
> 3. **The fold subtracts it** — `unsurfaced_owner_ask_groups` becomes *groups −
>    surfaced − baselined − discharged* (`silent |= discharged_ask_ids(fold)`);
>    a discharged group no longer screams and is no longer offered to the mirror.
> 4. **Loud, not silent** — the discharge is a durable admission on the log
>    (never the gitignored nag-state), and `python -m loop.reflect status` lists
>    each discharged ask with its cite, reason and signer, so a bogus discharge
>    is auditable — never an invisible self-clear.
> 5. **Dogfood** — the real ask in report 0052 (`ask.0a77fb3a288c`) is discharged
>    citing the supersede `adm.0ef4d2bfe067` that closed its RBAC clause, and
>    after it `loop.reflect` reports its unsurfaced count = 0 and the
>    owner-ask-shame beat falls silent on its own.
>
> **The §10 teeth:** a discharge with a fabricated or absent cite is refused and
> the floor keeps screaming (no evidence, no silence); a genuine
> *decision-for-bdo* nobody actually made has **no record to cite** and so
> cannot be discharged — only surfaced or said-plainly; discharging an unknown
> ask id is refused; and an ask re-parked under a *new* report is a new group
> that surfaces afresh (history is never retro-invalidated). A well-formed
> discharge record and a log missing its cited id are each locally fine and
> *refuse to fit* — the verb is the gate that notices.

## Non-example (looks done, isn't)

A boolean `resolved: true` a session sets on its own ask (the free stop-card
this exists to refuse). Editing a prior report's needs-you text to delete the
asks (erasing history to dodge the nag). A discharge that quiets the beat but
lands only in gitignored nag-state, or cites an id no fold checks (a silent
self-clear). Auto-guessing resolution by semantic match between an ask and a
record (the cite is an attested, existence-checked pointer, never an inference).

## Out of scope, named

- **Typed/linked needs-you asks** — this adds discharge to the existing
  free-text fold; restructuring asks into a schema is a separate whole.
- **Surfacing discharges into the owner's digest** — the audit trail is
  `reflect status` + the durable log; a digest section is a later increment.
- **Machine-checking the cite's *semantic* relevance** to the ask — existence
  on the log plus an attributed reason is the honest floor; a bad-faith but
  real cite is auditable like every story-pen, never silently trusted. Naming
  this limit is the point, not hiding it.
