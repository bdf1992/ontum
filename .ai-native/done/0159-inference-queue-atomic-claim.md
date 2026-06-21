# Done-line 0159 — The inference admission queue's claim is atomic — the bound holds under real parallelism

Written before code, per §9.4. When this line is met, stop.

> **Done when:** the inference admission semaphore claims a slot by atomically
> `os.link`-ing an already-written file into place (never the create-then-write
> `O_EXCL` window that let a concurrent reader see an empty slot, judge it
> `stale`, and double-claim it), so the bound HOLDS under real parallel
> contention; and a **multiprocessing concurrency test joins the suite** that
> spawns real parallel processes, counts concurrent holders directly (clock-free
> marker count), and asserts the bound is never exceeded and no acquire/release
> raises — a test PROVEN non-vacuous by FAILING on the pre-fix module (it
> measured a 3rd holder on a bound of 2) and PASSING on the fix, with the full
> suite green and the work atom-backed under epic.inference-gateway.

## Why

The inference admission queue (done-line 0152, PR #363) landed with a real
concurrency bug, and the gates missed it: every test in
`tests/test_inference_queue.py` called `acquire`/`release` **sequentially in one
process**, so they exercised the logic but never the cross-process race; and the
code review flagged the exact race and it was wrongly overruled as "intended
self-heal." bdo asked the question that caught it — *"and we know and stress
tested this?"* — and a real multiprocessing stress test answered no: under
parallel contention the semaphore admitted **6 holders on a bound of 3, and 2 on
a bound of 1**, plus `PermissionError`s on Windows.

Root cause: `_try_claim` created the slot file with `O_EXCL` (empty) and *then*
wrote its JSON. A second process reading the file in that window saw empty/torn
content, `_is_stale` returned True, and it stole the slot — two holders on one
index. `O_EXCL` makes the *create* atomic; it does not make create-plus-content
atomic.

The fix is minimal and stdlib (no new dependency, the loop/ law): write the
fully-formed content to a private temp file, then `os.link` it into the slot
path — link is atomic and fails if the slot exists, so the claim is exclusive
AND the slot is never observed empty. The lease/steal self-healing is unchanged.
The lasting fix is the **test**: the concurrency gate whose absence let the bug
through is now in the suite, and it bites (proven by failing on the old code).

## In scope (one increment)

- `loop/inference_queue.py` — `_try_claim` rewritten to the atomic `os.link`
  claim; the steal path and lease machinery unchanged.
- `tests/test_inference_queue.py` — `TestConcurrencyUnderRealParallelism`: real
  spawned processes, a direct clock-free concurrent-holder count, asserting the
  bound holds and no exception escapes; non-vacuous (fails on the pre-fix code).
- The module-layering doc line corrected from `O_EXCL` to the atomic-link claim.

## Not in scope (named, not invented away)

- **A mature lock library** (`filelock`): a defensible alternative to a
  hand-rolled file semaphore (hand-rolling cross-process locking is error-prone
  — this bug is the evidence). Kept stdlib here because the `os.link` fix is the
  smallest correct change; adopting a dependency is a larger, separate call.
- **Cross-machine** coordination — still single-host (local-first), as before.
