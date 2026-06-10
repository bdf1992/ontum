# Done-line 0003 — the first real node: L0, and the real stamp

Written before code, per §9.4. When this line is met, stop.

> **Done when:** with realness *admitted* (a typed admission, I-8 — never a
> code literal) for the value gate and the owner stamp, the loop never
> auto-judges a real stage: a fresh atom parks at `needs-you` naming the
> awaited node; a summoned node's verdict lands through `loop/node.py`
> (idempotent by `(node, artifact_hash)` (I-2), D-2-guarded — a node cannot
> judge its own writer's event — verdict drawn from the stage's terminal
> set); a real `accept` advances the atom and a real reject parks it;
> atoms already settled under mock receipts do **not** regress when
> realness is admitted (the log is truth — receipts are not retroactively
> invalidated, D-5); and the repo's own field shows one real L0 receipt
> from a summoned session, with the atom parked at bdo's real stamp.

Scope: exactly one node goes real — L0 (§11 "Next") — plus the owner
stamp, because the pipeline mandate says the mock-bdo stamp is the first
mock replaced when *any* node becomes real (D-4). L1/L2/confirm stay
mocks. Realness is per-stage and admitted (latest admission wins), so the
phase-1 and flood tests — which admit nothing — run unchanged.

Per report 0004 §3: this is not just de-mocking. Real L0 is the system's
first **semantic sensor** — the first time the ambient field fires on
evidence about meaning rather than plumbing.

Source: doctrine §11 ("Next"), §5 (L0), D-2, D-4, D-10 (summoned, not
staffed), I-2, I-8; pipeline mandate in `loop/reconcile.py`; report 0003
§4 (open for bdo); report 0004 §3-4. Stamp: bdo, via chat 2026-06-10
("continue as expected").

Next, not now: the L0 second check going real (`confirmed | missed`), the
slow loop, corpus-to-system ingestion — each needs a fresh stamp.
