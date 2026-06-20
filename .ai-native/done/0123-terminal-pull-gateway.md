# Done-line 0123 — The terminal-pull gateway — the piece-scale pull queue, and the namespace gap it makes visible

Written before code, per §9.4. When this line is met, stop.

**Goal:** The foreign reviewer's top-priority throughput fix
(`atom.landing-throughput-resp-terminal-pull-gateway.v0`), verified
against the live repo — the epic's own discipline: a PROPOSED finding is
checked before it is acted on. `loop.merge` gates land-readiness at
**arc scale** (the whole arc must be complete), so today it reports
*nothing ready* while ~25 receipt-complete pieces sit under confirmed
arcs. The terminal-pull gateway is the missing **piece-scale** sensor:
`next_landable_slice` — the ordered, capacity-bounded queue of pieces
that have passed every gate and could be pulled now, without waiting for
unbuilt siblings. Verifying the finding surfaced the true binding
constraint: the merge log's `landed` receipts key on `(epic, pr, head)`
with **no atom id/hash** (90 of 90), so the pipeline namespace and the
git-merge namespace **do not join per piece** — the loop cannot confirm
any completed piece reached main. The gateway is the first sensor of
terminal-pull readiness, and the first to make that namespace gap a
named, visible fact. **Arc:** `epic.landing-throughput-response`.

> **Done when:** A read-only fold `loop/gateway.py` — run as `python -m
> loop.gateway`, ending in `done | report` (D-6) — computes
> `next_landable_slice(root)`: per **confirmed** arc, the pieces that are
> **receipt-complete** (`next_action is None`), **not superseded**, and
> whose arc harbours **no refusal divergence**, ordered and split by the
> admitted `max_inflight_atoms` capacity into *pull-now* (within
> headroom) and *queued-behind-capacity*. It **composes** the `digest`
> dataset and `merge`'s readiness rather than re-deriving state (§10, no
> second truth). It surfaces, as a named **finding**, that its slice
> **cannot be joined to the merge namespace per piece** (landed receipts
> carry `epic/pr/head`, never an atom) — so it never falsely claims a
> piece reached main. Proven by tests with teeth (§10): a receipt-complete
> piece under a confirmed arc appears in the slice; the same piece under
> an arc harbouring a refusal is **held out** with its reason (two
> locally-fine facts refuse to fit); the capacity split honours the
> admitted setpoint; and the namespace-gap finding fires whenever a
> `landed` receipt cannot be matched to a completed piece. The work is
> dogfooded as an atom on the log (the off-log gate): atom authored,
> announced, an independent value-gate judge's receipt naming it. Full
> suite green.

> **Non-example:** a gateway that fakes a per-atom pull join (matching
> `landed` receipts to atoms by epic and calling a piece "on main" —
> mercury, a join the log does not carry); a second land-readiness truth
> that re-derives arc/piece state instead of folding `digest`/`merge`;
> pulling over a refusal under the arc (the §10 contradiction smoothed
> away); hard-coding an age/churn or capacity *threshold* as a code
> constant (thresholds are admitted records, not constants — firm
> invariant); reaching into live git to validate workspace binding (a
> pure log fold does not subprocess git — that is the actuator's reach, a
> later piece).

> **Out of scope — named (later pieces of this epic):** the **actuator**
> that enforces the threshold both ways (shed / fill voids); the
> **patrol** that routes and detains; **workflow-as-code** route
> inference; the **contribution economy** and **exemplars/notorieties**;
> and the **per-atom↔PR join** itself (closing the namespace gap is its
> own build — this node only makes the gap visible). Age/churn and
> capacity *thresholds* as admitted dials ride a later increment.

> **Evidence expected:** `loop/gateway.py`; `tests/test_gateway.py`; the
> atom + its value-gate receipt; `loop/CLAUDE.md` updated with the new
> organ; the full suite green; a merge receipt.
