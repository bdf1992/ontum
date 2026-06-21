# The Administrator — fleet oversight + governed agent launching (PROPOSED)

**Status:** PROPOSED blueprint. bdo's to steer; not a build. Foundation-first (blueprint before code, #348): the full shape and the open design calls are agreed here before any organ is written.

## 0. Naming (bdo, 2026-06-21)

A *conductor* controls ONE unit of a fleet. The fleet-level overseer is the **Administrator** (bdo's alternatives: Administrator / Controller — Administrator is recommended because ontum already calls `orchestrate` the *control* loop and positions itself as control theory, so "Controller" collides; Administrator reads cleanly as fleet governance). Three tiers:

- **Administrator** — oversees the WHOLE fleet; launches a Conductor (or a worker agent directly) per live unit; bounded by admitted governance; escalates the owner-gated to bdo. The agent-launcher at fleet scale.
- **Conductor** — drives ONE unit to done (a task / PR / atom-chain), launching the worker agents that unit needs. Generalizes what a session does today by hand.
- **Agents** — the workers a Conductor launches: value-gate/value-confirm judges, the merge-node, drains, cleanups, resumes.

The mesh (herald roster + reputation) registers all of them; the trust ladder governs what each tier may do; the inference queue bounds how many run at once.

## 1. The problem / why now

Right now the repo runs a fleet — 14 open PRs, parallel overnight sessions (#388, #389, #397, #400 are different sessions) — with **no single part watching the whole fleet**. Tonight a session hand-conducted exactly ONE unit (the review queue: oversee → launch a value-gate judge → launch a merge-node → run the drain → hit a landing-gate gap → escalate). It worked, but it was ad-hoc, one unit, by hand. Neither bdo nor the system can answer, from one place: *what is every unit doing, what is blocked, what is ready, and what one launch would move it?* The owner-facing digest is arc-first (what landed); it is not a fleet-of-agents oversight surface.

## 2. The frame: a projection + a governed loop, never a second authority

The Administrator READS the fleet (a fold over what already exists) and LAUNCHES agents (through the existing spawn rail). Two hard rails keep it honest:

- **No second source of truth.** It composes the existing folds (digest / census / heal / gaps / activity / watcher / herald); the log stays truth; it invents no new state. (§10, the projection rule Causality lives by.)
- **No authority bdo did not grant.** Every launch is bounded by admitted policy (trust rung, fence, the inference-queue concurrency dial) and is receipted. Owner-gated items (arc confirms, doctrine changes, loosening a gate) are ESCALATED, never auto-launched. The Administrator proposes and dispatches; it never signs an owner's line (D-4).

## 3. What already exists (compose, do not rebuild)

- **The launcher** — the spawn rail (`spawn_guard`, `ontum-node:<id>` branding, prompt-pin, rung-check). Proven tonight: launched a value-gate judge, a merge-node, and drain judges, each branded and receipted.
- **The mesh** — `herald` (roster + reputation + vouching), `trust` (the capability ladder), `inference_queue` (launch backpressure / concurrency dial).
- **The sensors** — `digest`, `census`, `heal`, `retro`, `gaps`, `activity`, `watcher` (session lifecycle). Each senses ONE axis; none sees the fleet whole.
- **The launchable agents** — the merge-node, `gate.py launch` / `drain`, cleanup, `continue-probe` resume.

The pieces are all here. What is missing is the part that reads them together and acts.

## 4. The Administrator's organs (what this blueprint adds)

1. **The eyes** — `loop/fleet.py`: a pure read-only fold. One glance-able map of every live unit / agent / block AND the single governed launch each needs (PR ready → merge-node; queue parked → drain; branch stranded → cleanup; session idle → resume; block → escalate to bdo). Composes the existing folds; no second truth. THIS IS THE FIRST INCREMENT.
2. **The hand** — the launch loop: rides the eyes, dispatches the recommended branded agent (or a Conductor) per item, bounded by trust + fence + inference-queue, every launch receipted, level-triggered + idempotent (a re-fire is the I-2 no-op, like the drain). Escalates the owner-gated.
3. **The Conductor** — the per-unit driver: generalize tonight's hand-conducting into a branded role a session/spawn fills, that takes ONE unit from where it is to done (or to an honest escalation).
4. **The dial** — an admitted authority record: which launches are standing-authorized vs which escalate. bdo's to set (the setpoints law).

## 5. Governance (the gateway spine: separation of powers)

The Administrator is the regulatory branch made active: it senses (the folds), decides (what each unit needs), and dispatches (the launch) — but the *policy* of what it MAY launch without asking is an admitted record bdo sets, and the *constitution* (the fence, the trust ladder, D-4) is above it. A launch outside the dial's bounds escalates, exactly as the disposer escalates an out-of-fence setpoint. Its own standing is earned forward through the herald's reputation, so an Administrator that launches badly is visible by construction.

## 6. The mesh / brokerage tie-in

This is the conductor of the platform-brokerage layer: it routes WORK to the herald's registered AGENT mesh, bounds and prices the launch, and the reputation fold makes a bad launcher visible. Knowledge stays a fold; transport (the launched agent) is ephemeral; truth is never in transit. The no-broker law holds: this is brokerage as a fold over records, not a daemon holding state.

## 7. A caveat carried from the platform blueprint

A node is both a holon (its interior is an atom-graph) and a gate-face. The Administrator must not conflate *oversee a unit* with *be the unit*: it oversees and launches; the Conductor drives; the agents do the work. Three tiers, three jobs — the Demeter rule for the fleet.

## 8. Concept list (the buildable pieces, labelled)

- **C1 fleet-fold** (the eyes, read-only) — FOUNDATION. Build first.
- **C2 per-item launch recommendation** (the one governed launch per item) — rides C1; pure, no action.
- **C3 the launch loop** (the hand, governed + receipted + idempotent) — rides C2 + the spawn rail.
- **C4 the Conductor role** (per-unit driver, branded) — generalizes tonight's hand-conducting.
- **C5 the authority dial** (admitted: standing-authorized vs escalate) — bdo's.
- **C6 the owner oversight surface** (the fleet glance, arc-first like the digest).
- **C7 reputation feedback** (launched-agent outcomes → herald reputation).

## 9. Calls to action (against the purpose: oversee all tasks as a mesh + launcher)

- **CTA-1 (bdo):** pick the name — **Administrator** (recommended) or Controller — and confirm the three-tier frame (Administrator → Conductor → Agents).
- **CTA-2 (bdo):** confirm the hard frame (projection + governed loop, never a second authority).
- **CTA-3 (bdo):** set the authority dial (what is standing-authorized vs what escalates) — the one decision that bounds everything the Administrator may do unattended.
- **CTA-4 (session):** build **C1** (`loop/fleet.py`, the read-only fleet-fold) as the first increment — the eyes before the hand. Atom-backed, §10-tested, composing the existing folds.
- **CTA-5 (session):** once C1 reads true, build C2 then C3 behind the dial.

## 10. What this is NOT

- NOT a second source of truth (it folds the log; it never holds state).
- NOT an autonomous authority (every launch is dial-bounded; owner-gated escalates; D-4 holds).
- NOT a replacement for bdo's confirms — it makes them FEWER and SHARPER (one dial authorizes many launches), never absent.

## 11. Tonight, as the existence proof

This blueprint was written the same night a session hand-conducted one unit end-to-end (review queue: rcp.merge.395 landed via an independent merge-node; a first real drain ran; a pure-log landing-gate gap was found and escalated rather than worked around). That session WAS a Conductor, by hand. The Administrator is that pattern made standing and fleet-wide.
