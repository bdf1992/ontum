# Done-line 0152 — The inference admission queue — bounded in-flight, witnessed backpressure

Written before code, per §9.4. When this line is met, stop.

> **Done when:** the inference gateway admits each completion through a bounded
> in-flight semaphore (`loop/inference_queue.py`) sized by an **admitted**
> concurrency dial (a bdo-signed record, default-safe when unset — never a code
> constant), so N callers hammering the plane can never hold more than the
> bound's worth of model/KV-cache resident at once; a request that finds every
> slot taken **waits** up to a bound and, still saturated, is **refused with a
> witnessed `saturated` receipt** (backpressure on the record, never a silent
> host-kill); the semaphore is **lease-based** so a hard-killed caller's slot
> self-heals on the next acquire (torn-tail safe, the substrate's mortality
> law); a read-only **stats fold** (`python -m loop.inference_queue`) reports
> live in-flight, throughput, per-mind latency, and saturation over the
> receipts; and the §10 teeth PROVE the bound bites (a `bound=1` plane refuses
> the second concurrent acquire) and that an expired lease frees the slot —
> neither check vacuous — with the full suite green and the work atom-backed
> under epic.inference-gateway so the PR is a landable unit.

## Why

bdo, 2026-06-20, after his llama-server hammered the host into a swap-thrash
freeze: *"do we have a requisition / summon queue in front of this installed in
the gateway… the idea would be we should allow requests and then they get
processed with stats."* The gateway (`.claude/skills/gateway/gateway.py`) today
**authorizes** and **receipts-with-stats** per call, but fires each completion
immediately and synchronously — no admission control, no concurrency bound, no
backpressure. N concurrent callers become N concurrent loads on the metal; the
only queue is Ollama's internal one, which the loop neither controls nor
witnesses. That unbounded fan-in is the mechanism behind "hammering kills my
PC."

This is the **summon queue on a new axis**: `loop/summon.py` admits *atoms*
waiting for *nodes*; this admits *requests* waiting for a *model slot* — same
law (log-as-truth, level-triggered, the receipts already the stats channel). It
is the missing in-flight bound the inference-gateway arc's horizon implies
(*"a jammed provider becomes a receipt and a fallback instead of a stuck
seam"*) — now also a jammed *host* becomes a `saturated` receipt instead of a
freeze. It is a better fix than blunt-capping Ollama's `max-loaded-models`: the
bound lives at the loop's door, applies backpressure, and witnesses every
request.

## In scope (one increment)

- `loop/inference_queue.py` — the lease-based file semaphore (stdlib, no
  network: a local-first coordination primitive, the loop/ law), the admitted
  concurrency dial (read + bdo-signed set), and the read-only stats fold over
  the receipts. Sibling of the other loop folds.
- The gateway wired to acquire a slot before the completion and release after,
  receipting `saturated` when it cannot within the wait — the only edit to the
  egress.
- The §10 teeth + tests proving the bound bites and the lease self-heals (both
  non-vacuous).

## Not in scope (named, not invented away)

- **Cross-machine** coordination — the semaphore is single-host (local-first);
  a distributed bound is a later axis if the plane ever serves beyond one box.
- **Priority / fairness** in the queue (FIFO vs. caller-class weighting) — this
  increment is a flat bound; weighting rides the gateway-economy arc later.
- **The container memory-fence** — an orthogonal host-survival belt bdo may
  still want; this increment makes it unnecessary for loop-originated load but
  does not govern non-gateway callers.
