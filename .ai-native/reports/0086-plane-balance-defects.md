# Report 0086 — Balanced planes — named defects from the all-eyes-no-hands read

A design conversation (bdo + Claude), no build. Started from an uploaded
behavior-catalog handoff (exemplar/specimen/definition + emergent discovery),
moved through example/sampler vocabulary, and ended on a plane-balance read of
the system as defined in `session-gateway.proposal.md` (esp. §13/§13.10) and the
36 `loop/` modules. bdo's method: a dense definition in one plane *obscures* its
missing counterpart in another — look at the dense plane and the sparse one shows
up by silhouette. It did. This report names what surfaced as defects so it
survives the session.

## What landed

No code, no atom, no version bump (none claimed — design only). What landed is
this report: the plane census, the named defects, and the priority order, plus
the owner-asks surfaced below.

**The reframe (carried, not built):** the behavior-catalog handoff is not a new
arc — it is the *general substrate* of which `epic.test-metabolism` is the first
single-author instance (definition/archetype + classifier/reviewer/auditor seats
+ refusing seams + admit/send_back/needs_instrumentation). `loop/gate_eval.py`
(charades / matched-variant atoms) is the specimen+eval cousin already running.
The one net-new primitive with no repo analog is **exemplar** (a pointer to the
canonical best instance — the repo grades pass/refuse but never says "emulate
*this* one"). A "sampler" is a producer of candidate examples aimed at the
boundary; the gate judges them; misfits teach where a definition or the world has
a hole. Both already exist in two domains (gate_eval; the test-metabolism
mutation lane) — "sampler" is a name for a thing the repo does, not new machinery.

**bdo's standing steer (recorded):** strict on *fit* (does it cohere / is the
evidence real), loose on everything else — strict, not rigid; and *do not make
the owner a blocker* — propose/decide/act by default, surface sparingly.

## Named defects (the plane imbalance)

Plane census, grounded: control/sensing ≈ 30 organs (incl. six pure observation
folds: census, gaps, digest, retro, heal, owner_asks); data plane ≈ 3 (gateway
pen, web, runs — flow lives in the log+atoms, *no message/queue module*);
management plane ≈ 2 (pen, fence) **with authentication, scheduling, migration,
and retention all absent.**

- **DEFECT-0086-A — attribution-without-authentication (P0).** The `--by`
  discipline records *who claims* to act on every record, so identity looks
  handled; it is not. `loop/inference.py` states it outright — "identity is a
  caller's `node_real` admission + its rungs" (a self-written record) and
  `GRANTOR = "bdo"` is a string constant. Attribution ≠ authentication; nothing
  verifies the signature. The whole privilege-accretion + contribution-economy
  (§13.1, §13.10: wealth/notoriety/trust accrue *to an actor*) is forgeable and
  uncomputable until this exists — mock-shame already caught 22 forged landings
  here. **Obscured by:** the richness of the attribution discipline.

- **DEFECT-0086-B — sensing-without-scheduling (P1).** `loop/temporal.py` reads
  the hour richly (the hour *is* pressure) but is explicitly read-only,
  clock-at-the-edge: it senses time, nothing *acts* on time. The proposal's
  patrol is "the scheduled surfacer" with no scheduler under it. No durable
  timer, deadline, expiry, retry/backoff. **Obscured by:** the depth of the
  time-*sensing* fold.

- **DEFECT-0086-C — message-without-a-home (P1).** The proposal's keystone is
  "a message is a typed particle that travels," but no record type *is* a
  message — there are atoms and events only. "Queues are cache, a fold over the
  log" is correct and load-bearing, and it absorbs the data plane's central
  object so its absence is invisible. `dead-letter` is a named router outcome
  (§13.9) with no handler (retry/poison/who-works-it). **Obscured by:** the
  cache-is-a-fold principle.

- **DEFECT-0086-D — all-eyes-no-hands (P0, the meta-defect).** ~30 afferent
  organs that sense/judge/surface; exactly **one** efferent organ that acts
  autonomously (the disposer, and only to re-dial setpoints inside a fence).
  The proposal's observation fiber (§13.6) is fully real; its actuator hand
  (§13.10) is essentially unbuilt. Every deficit the sensors find waits for a
  human session to wander by and discharge it. "Balanced planes" is therefore
  not *more control* — it is giving the existing eyes a small set of *safe
  hands* (an authenticated identity to act *as*, a clock to act *on time*, a
  message to act *upon*), each fenced exactly the way the disposer already is.

- **Tail (P2, named so they are not re-discovered):** attention is a budget
  dimension (§7) with no meter; the log is append-only with no
  retention/compaction (event-sourcing's replay-cost tax, named in
  test-metabolism); no migration for in-flight messages past a changed
  gateway/schema; foreign-system *ingress* is thin (envoy exports;
  arc-intake reads back); a mesh **simulator** (the "sampler" pointed at the
  mesh) does not exist. The guard's roving half (patrol) is designed; its fixed
  half ("station" / standing gateway) is named but not paired.

**Priority order for a future session/arc:** A and D first (authentication is the
floor the economy stands on; the actuator hand is the through-line that turns
sensors into action), then B and C (a clock and a message are two of the three
"safe hands" D needs), then the P2 tail. Smallest safe first hand is likely the
disposer-shaped actuator pattern applied to one deficit — to be scoped against a
done-line before any build.

## needs-you

Surfaced to bdo directly in this session (he was live in chat); recorded here so
they survive it. **Not** silently parked — but a chat is mortal too, so the
GitHub mirror is offered:

1. **Name the Anthology** the session gateway homes under (re-derives
   `owner-harness / substrate / inference-gateway / virtual-fleet / the-field`;
   throughline ≈ *the loop governs, provisions, and staffs itself safely*). This
   is directly the throughline this conversation circled; the gateway design is
   homeless until it has a name. (carried from report 0085)
2. **Land PRs #203 / #213 / #219** — the merge-node's, once their arc is
   confirmed (#219/#203 serve confirmed arcs). (carried from report 0085)
3. **Stray commit `bcd6bad`** — local-only/unpushed on
   `claude/causality-experience`; low-harm (origin clean, identical content if
   it ever double-lands). Left for that session / the gardener. (carried from
   report 0085)

Open offer (bdo's call, outward-facing so not done unprompted): mirror these to
GitHub via `python .claude/skills/reflect/reflect.py apply --surface
github-issues --by <who>`, or enable the standing rule
(`python -m loop.reflect rule --kind owner-ask-backlog --surface github-issues
--on --by bdo`).

Also still open from prior session: react to `session-gateway.proposal.md` as a
unit (§12b "still open / yours": the arc name, confirm the glue definition, veto
any closure).

## End-state

`report` — design conversation landed; four plane defects named
(A authentication / B scheduling / C message-home / D all-eyes-no-hands) with a
priority order; three owner-asks surfaced to bdo and recorded; no build, no atom,
no version bump.
