# The 8×8 matrix — working fill

Legend: `●` native · `✓` have · `◐` build · `✗` void · `⊘` unopened.
Rows = pointers, cols = systems.

| ↓P / S→ | Records | Repo | Reason | Peers | Names | Settings | Sessions | Resource |
|---|---|---|---|---|---|---|---|---|
| APPEND  | ● | ⊘ | ⊘ | ⊘ | ⊘ | ⊘ | ⊘ | ✓ |
| CITE    | ⊘ | ● | ⊘ | ⊘ | ⊘ | ✓ | ⊘ | ◐ |
| VERDICT | ⊘ | ⊘ | ● | ⊘ | ⊘ | ⊘ | ⊘ | ✓ |
| FOLD    | ⊘ | ✓ | ⊘ | ● | ⊘ | ⊘ | ⊘ | ✓ |
| HASH    | ◐ | ⊘ | ⊘ | ⊘ | ● | ⊘ | ✗ | ◐ |
| ADMIT   | ⊘ | ⊘ | ⊘ | ⊘ | ⊘ | ● | ✓ | ✓ |
| STEP    | ⊘ | ⊘ | ⊘ | ⊘ | ✗ | ⊘ | ● | ◐ |
| SOURCE  | ✓ | ✓ | ✓ | ◐ | ✗ | ✓ | ◐ | ● |

Score so far: 8 native · 11 have · 6 build · 3 void · 36 unopened.

---

## Worked axis — **Resource** (the newest system; stress-tested first)

Resource = bounded consumable capacity: inference slots, step/token
budgets, compute. Native pointer **SOURCE** (draw on it as input).

### Column — `POINTER(Resource)`

| cell | verdict | example | non-example (refusal) | citation |
|---|---|---|---|---|
| `APPEND(Resource)`  | ✓ have  | a slot acquire/release or `saturated` outcome is appended | spending a slot with no record | `loop/inference_queue.py` (lease + saturated receipt) |
| `CITE(Resource)`    | ◐ build | a tick citing its remaining step-budget as the constraint it acted under | acting with no stated budget | `loop/orchestrate.py` reads `step_budget_per_tick` but does not yet *cite* it as provenance |
| `VERDICT(Resource)` | ✓ have  | deciding the inference plane is **saturated / exhausted** | declaring a resource spent without measuring it | `loop/inference_queue.py` (stats fold → `saturated`) |
| `FOLD(Resource)`    | ✓ have  | the in-flight / throughput / saturation stats fold | treating a cached count as authoritative | `loop/inference_queue.py` (stats fold) |
| `HASH(Resource)`    | ◐ build | a lease **token** identifying one held slot | a slot with no unique claim (double-claim) | leases exist (`os.link` atomic claim) but a *content-hash identity* of a resource is marginal |
| `ADMIT(Resource)`   | ✓ have  | `inference_queue admit --bound N --by bdo` — the concurrency dial | a bound as a code constant | `loop/inference_queue.py` (`set_bound`, admitted not constant) |
| `STEP(Resource)`    | ◐ build | decrementing the step budget by one unit per tick | unbounded consumption per tick | `loop/orchestrate.py` budgets steps; "step a resource" not yet first-class |
| `SOURCE(Resource)`  | ● native| draw on the resource as material input to a computation | — | the diagonal |

### Row — `SOURCE(System)` (Resource's native pointer across all systems)

| cell | verdict | example | non-example (refusal) | citation |
|---|---|---|---|---|
| `SOURCE(Records)`    | ✓ have  | a fold reads the log as input | inventing input not on the log | every `Fold` in `loop/reconcile.py` |
| `SOURCE(Repository)` | ✓ have  | a session reads repo files as context | citing a file that does not resolve (ghost) | the read tools / `term_economy` resolution |
| `SOURCE(Reason)`     | ✓ have  | a gate reads prior receipts as input to its judgment | judging blind to prior verdicts | `loop/node.py` idempotence on `(node, artifact_hash)` |
| `SOURCE(Peers)`      | ◐ build | an agent reads other agents' folds / reputation as input | asserting standing instead of reading it | `loop/herald.py` reputation fold exists; consuming it as *input* is not yet wired |
| `SOURCE(Names)`      | ✗ void  | — | a name is an identity, not material to consume | collapses — "use a name as input" is just `CITE`/`HASH` |
| `SOURCE(Settings)`   | ✓ have  | orchestrate reads the admitted setpoint dial as input | budgeting off a hard-coded constant | `loop/orchestrate.py` (reads admitted setpoint) |
| `SOURCE(Sessions)`   | ◐ build | continue-probe reads a session's transcript / mtime as input | resuming with no read of prior state | `loop/watcher.py` (mtime as activity signal) — partial |
| `SOURCE(Resource)`   | ● native| draw on the resource as input | — | the diagonal |

### Finding

The 8th system **holds**. Resource is not vacuous: across 14 composed
cells it scores **6 have · 5 build · 1 void**, all grounded in the real
inference-queue / orchestrate machinery. `SOURCE(X)` reads cleanly as
"*X as input to a computation*" for almost every system — a genuine
universal read-op — which is why the row is dense. The single void,
`SOURCE(Names)`, is the honest one: consuming a name as *material* just
*is* `CITE` or `HASH`, so it refuses.

This is §10 working: the matrix did **not** pass everything. One void
per axis is the check earning its keep.

---

## Open questions (held, not guessed)

- **Cube composing unit:** 6 faces or 8 corners? `grammar.md` geometry.
- **Voids found so far:** `STEP(Names)`, `SOURCE(Names)`, `HASH(Sessions)`
  — are these *all* of Names'/Sessions' structural zeros, or a pattern
  (timeless/mortal systems refuse consumption-style pointers)?
- **Next axis to fill:** recommend **Names** (to confirm the
  timeless-system void pattern) or **Sessions** (mortal-system void
  pattern) — the two systems already showing voids.
