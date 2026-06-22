# The Administration loop — requirements (PROPOSED, grown by running it)

**Status:** PROPOSED · owner **bdo** · the requirements for a by-hand Administration
loop, written so a fresh session can **launch it now**, and grown by *running* it.
**Composes:** the Administrator blueprint (`administrator.proposal.md`, PR #416,
Administrator → Conductor → Agents) and `epic.virtual-fleet` (the declarative fleet).
Never a second authority — it reuses the spawn rail, herald, trust ladder, and folds.

**The method (bdo's steer):** run the loop **by hand** to *build the requirements we
need*. Every time the Administrator does something manual that should be a fold, an
admission, or a beat, the friction is appended here as a requirement. The by-hand run is
the requirements-discovery instrument; the automated Administrator is its posterior.

---

## The launchable artifact

- **`/administer`** (`.claude/skills/administer/SKILL.md`) — the ritual a fresh session
  invokes to *be* the Administrator: declare the work, launch N Conductors within budget,
  monitor, synthesize, re-dispatch, and capture requirements. **This is launchable now.**
- **`loop/fleet.py`** — the Administrator's eyes: a read-only fold over every in-flight and
  recent Conductor and its Agents. `python -m loop.fleet`.

---

## Requirements

### Satisfied — the loop can launch on these today

| # | requirement | satisfied by |
|---|---|---|
| **R1** | **Conductor primitive** — launch one fanned-out unit, detached, journalled | the `Workflow` tool (background run, `journal.jsonl`, `<task-notification>` on completion) |
| **R2** | **Concurrency bound** — N Conductors must not thrash the host | `loop/inference_queue.py` (admitted bound) + the per-workflow cap `min(16, cores−2)` |
| **R3** | **Governed launch** — a spawn is branded, rung-checked, §7-pinned | the spawn rail (`ontum-node:<id>`) + `loop/trust.py` |
| **R4** | **Reputation** — agents/operators earn standing from logged work | `loop/herald.py` (exemplars / notoriety / meta-reputation over provenance edges) |
| **R5** | **Completion signal** — the Administrator is told when a Conductor finishes | `<task-notification>` re-invokes the session |
| **R6** | **Result persistence** — a Conductor's output survives a mortal session | task output files + `agent-*.jsonl` transcripts |
| **R7** | **The fleet glance (eyes)** — one read-only fold of all Conductors + Agents | **`loop/fleet.py` (built this session)** |
| **R8** | **Liveness in the glance** — RUNNING vs STALLED, so dead seats aren't counted filled | **`loop/fleet.py` v1 (built this session): a RUNNING run idle past the staleness setpoint reads STALLED — proven on the two 3-day zombies** |
| **R13** | **Requirements capture** — the by-hand run records its own friction | **this document + the `/administer` discipline (built this session)** |
| **R15** | **Delegated oversight** — the loop fans out monitoring to subagents | **the Agent tool (`run_in_background`): a monitor-subagent per Conductor folds its transcript and returns a digest, so oversight scales with the concurrency dial, not the Administrator's context (built into `/administer` this session)** |
| **R18** | **Upward launch-request (propose-dispose dispatch)** — a subagent can't launch a Workflow (R17) but can *request* one from its admin | **the subagent's return message + `SendMessage` continue-channel IS the request; the Administrator holds the Workflow tool + the bound + the rail and accepts/refuses (the merge-node/confirm-arc propose-dispose shape, D-4). The fleet self-extends, governed — a monitor that sees more work is needed requests a Conductor, the Administrator grants within budget. Built into `/administer` this session.** |
| **R16** | **Reputation-routed dispatch** — route work to earned standing | **`loop/herald.py` reputation (exemplars/notoriety) + the `/administer` re-dispatch discipline; the routing fold itself is the next hardening** |

### Missing — the by-hand run builds these (priority order)

| # | requirement | why it's needed | the build |
|---|---|---|---|
| **R9** | **Declared fleet / launch registry** — desired occupancy as admitted records | so "which Conductors should be running, under which conditions" is data, not a session's memory | `epic.virtual-fleet`: the declarative plan (which seats, fill condition, capacity from setpoints) |
| **R17** | **Recursion depth — can a subagent launch a Workflow?** | ANSWERED by running (2026-06-21): **no.** A spawned Agent-subagent has no `Workflow` tool in its toolset (it ran `loop.fleet` fine — delegated monitoring works — but `ToolSearch` for a workflow launcher returned nothing; only the `Agent` spawn primitive is held). So the tree is fixed: **Administrator(session) → {Conductors(Workflows), monitor-subagents(Agents)}**; monitors read and report, they do not dispatch. Settled, not assumed — moves to fact. | n/a (answered) |
| **R10** | **The apply beat** — converge declared→actual one receipted step per tick | so the fleet self-fills within setpoint budgets and trust rungs, not by hand | the ambient apply beat (virtual-fleet horizon) |
| **R11** | **Operator-tier governance** — manage the agent network by reputation | "operators manage a network of agents based on their work" — promote/retire/route on herald standing | the operator layer over `herald.py` (promotion/retirement folds) |
| **R12** | **Cross-session continuity** — a fresh Administrator inherits the fleet state | so the summon hands the *fleet* at wake, not just the gap backlog | extend the session-lifecycle gateway (PR #280) to hand `loop.fleet` |
| **R14** | **Result→work bridge** — a Conductor's synthesis lands as queued work, not transcript | so a result becomes an atom/proposal the loop folds, never stranded context | generalize the envoy `respond` seam (foreign result → value-gated atoms) to Conductor results |

---

## How a discovered requirement is added

When the `/administer` loop hits friction, append a row to the **Missing** table with:
the requirement, the concrete friction that surfaced it (cite the run/`run_id`), why it's
needed, and the smallest build. R8 is the worked example — surfaced by the very first
`loop/fleet.py` run catching two 3-day zombies. That is the loop building its own
requirements, which is the point.
