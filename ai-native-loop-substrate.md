---
title: AI-Native Loop Substrate — Project Doctrine
version: 0.4.0
status: working harness — system descriptions folded in (ambient control + the mechanism); build §11 next
intent: >
  One idea we're building around: the files are the environment, the agent is the
  (mortal) process, and the console just routes between them. The worker is a Claude
  model; Claude Code is our proof-of-concept scaffold. First goal is small, local
  operations. This doc is a method of discipline for building onton, not a second
  system beside it.
owner: bdo (PM)
working_with: Claude (engineering)
changelog:
  - version: 0.4.0
    note: >
      Folded the missing system descriptions into the spec. They were living only in
      the culture layer (docs/culture/), and their absence here was the defect — not a
      fork to decide. Added the mechanism (§16: the place composes the environment via
      nested files + @ + location; nodes are summoned virtual subscriptions, not staffed
      processes; the ledger remembers and no one signs their own line) and ambient
      control (§15: the system is a bidirectional homeostat — cooperation is the heat,
      the setpoints hold it both ways, pressure is field-state, ports are valves, the
      herringbone-solenoid is the push-pull actuator; every site is a transducer, and
      agent vs environment is a difference of rate). New decisions D-9..D-12,
      implications I-7..I-8. The reconcile loop (D-8) is unchanged — ambient control
      wraps it, it doesn't replace it. The full telling stays in docs/culture/the-idea.md
      and docs/culture/the-ambient-loop.md.
    rollback: ai-native-loop-substrate-v0_3_0.md
  - version: 0.3.0
    note: >
      Closed all open calls (§1.3 + §13) into decisions; fixed the I-4 trajectory
      collision so trajectory is respected. Dissolved the six §15 addendum
      candidates — handoff-witness was already §5; shadow-branch folded into I-4;
      prompt-is-code folded into §7; local-incident, surfacer-calibration, and
      restart/backpressure cut as out-of-scope for the §11 first build (git keeps
      them). Fixed the offsets-as-cache leak in §14 against D-5. This is the version
      where the doc stops growing design surface and becomes the working harness for
      building onton.
    rollback: ai-native-loop-substrate-v0_2_2.md
  - version: 0.2.2
    note: addendum pass — added durable seam event surfaces and candidate addendum shapes. Behavioral direction clarified; first local build still unchanged.
    rollback: ai-native-loop-substrate-v0_2_1.md
  - version: 0.2.1
    note: wording pass — retoned from directive voice to a working-doc register. No behavioral change.
    rollback: ai-native-loop-substrate-v0_2.md
note: >
  This is a doc we work from, not a rulebook we answer to. If something here is
  wrong or in the way, say so and we change it — most of it is a choice, and the
  choices are labeled. A few things are firmer; those are called out where they live.
---

# AI-Native Loop Substrate

## 0. The shape we're building toward

Work moves through a versioned, file-defined environment, and every unit of value
gets a second set of eyes before it turns into code. Claude does the work, the
console routes it, and the files hold the truth. Sessions come and go; the files
stay.

Two things sharpen that shape, and they describe how the system actually runs — not
future ideas: **the place composes the environment** (where a node stands decides what
it loads — §16), and **the system is an ambient controller** (it doesn't only push work
forward, it holds the field at a workable temperature — heating when it stalls, cooling
when it runs away — §15).

This is a working harness — a method of discipline for building onton, not a system
beside it. The buckets in §1 and the build rule in §9/§12 are the method; everything
else is the current best guess at the shape, and is meant to be cheap to change.

---

## 1. How we're sorting the work

Four buckets. The only discipline is putting each item in one — that's what keeps us
honest about what's settled, what follows from it, what to talk through first, and
what we'll just learn by doing.

### 1.1 Decisions we're building on

Calls we've made so the rest has something to stand on. None of these are sacred —
changing one is just a bigger conversation than changing a detail, so let's flag it
when we want to.

- **D-1. Files are the environment; the agent is the process; the console routes.**
- **D-2. Keep the writer and the reviewer separate** — a worker doesn't sign off on its
  own work. *(This one's firm — it's the whole point of the second set of eyes.)*
- **D-3. The console routes and reports; it doesn't make value calls.**
- **D-4. The human is the last stop.** Nothing in the system signs its own approval.
  *(Firm.)*
- **D-5. Truth lives in the file log, not in a session's memory.**
- **D-6. Every node ends with a clear result, never a silent hand-off.** *(Firm.)*
- **D-7. The session is where work runs** — short-lived, capped by context (§2).
- **D-8. We drive work by reconciling toward a goal state, re-read from the log each
  pass**, rather than firing on one-shot events. *(Closed in §13.2 — reconcile stays;
  §14 adds the event ergonomics without moving truth out of the log.)*
- **D-9. The place composes the environment.** Where a node runs decides what it knows:
  the briefing is the stack of every environment file along its path (nested,
  `@`-composed, location-scoped). The same model at a different site is a different
  program. (Mechanism in §16.)
- **D-10. Nodes are summoned, not staffed.** A node is a standing offer — *if this
  signal fires at this place, this runs* — not a long-lived process you babysit. It
  blinks in, reads the local environment, does one bounded thing, writes its result, and
  is gone. (§16.)
- **D-11. The system is an ambient controller, not only a reconciler.** It holds the
  field at a setpoint *both ways*: heat when work stalls (stoke cooperation), cool when
  it runs away (throttle, shed, bleed). Pressure is visible field-state, ports are the
  valves, the actuator is push-pull. Reconcile (D-8) is the loop this rides on; ambient
  control is what it regulates toward and how. (§15.)
- **D-12. Every site is a transducer; agent and environment differ only in rate.** Each
  node reads the medium, is moved by it, and writes back. A fast site is an agent; a slow
  site is an environment. Same primitive — they co-adapt, and they nest. (§15.)

### 1.2 What those decisions imply

Once the above are in place, these come along for the ride. Worth knowing so they
don't surprise us mid-build.

- **I-1. Because sessions are short-lived, state has to live in files** (from D-5, D-7).
- **I-2. Because we retry and reconcile, every node should be safe to run twice.**
  Content-hashed receipts are how a node knows it already handled this version of an
  atom and can skip re-doing it.
- **I-3. A watcher needs at least as much range as what it watches** (requisite
  variety). So the surfacer (§6) has to see wider than any single worker, or it's
  blind in the same places they are. This is just how we size it.
- **I-4. Two pieces that agree on their shared seam *and* share the same trajectory
  should be the *same* piece.** The trajectory clause is load-bearing: per §4, the
  same content under a different trajectory isn't the same thing. So collapse only
  *drift* — two pieces that diverged by accident. Leave deliberate divergence alone: a
  shadow branch, a competing proposal, or the same content carried down a different
  trajectory are distinct on purpose. The failure we're guarding against is two
  competing "truths" for one seam *by accident*, not two intentional readings of it.
  (Which gate enforces this is §13.4 — deferred at local scale; the wording is fixed
  now so we don't build the over-collapsing version later.)
- **I-5. A rendered file's version is computed from its inputs** (a hash of the
  sources + config that built it), with a human-readable semver alongside.
- **I-6. The trickiest gap is between two sessions of the *same* run**, not just
  between nodes — a resume is a hand-off and deserves the same care.
- **I-7. Because control is bidirectional, more cooperation isn't monotonically good.**
  Over-cooperation overheats — work generated faster than it can be reviewed or
  reconciled. The cool path (throttle / shed / bleed) is load-bearing, and the system
  must be able to tell itself to back off, not only to do more. (from D-11.)
- **I-8. Because pressure is field-state, setpoints are admitted records.** A threshold,
  limit, or cap lives in the log as a typed admission — a dial read at runtime,
  adjustable by admission, learned by the slow loop — not a literal baked into a node.
  (from D-5, D-11.)

### 1.3 Settled before building (was: open)

These were the calls where guessing wrong is expensive. They're closed now — the
question kept, the verdict appended. We record the verdict, we don't erase the
question; that's D-5 applied to our own doc.

- **Q-1. Reviewer independence.** → **Settled:** the lever is *agenda* independence,
  not *weights*. A reviewer with a different, adversarial agenda catches more than a
  different base model carrying the same agenda — different weights still share
  training-distribution blind spots (the herringbone in §3 is opposition of agenda,
  not of model). Going local makes a different review model a cheap bonus (§8), not a
  requirement. Full rationale in §13.1.
- **Q-2. How atoms declare what they connect to.** → **Settled:** the `incidence`
  block on the atom (§5) — `serves / touches / must_not_collide_with / hands_off_to`.
  That shape is the connection declaration L1 checks against; it's pinned.
- **Q-3. What "success" means.** → **Settled:** §10 — catching a local-looks-fine /
  globally-wrong problem before it spreads through spec → plan → tasks → code. We grade
  on *that catch*, not on average quality. Tasks closing isn't value landing (L0's
  `confirmed | missed`).
- **Q-4. The end-states and their triggers.** → **Settled:** the five in §4
  (`done · report · needs-you · rejected · needs-amend`), triggered by gate verdicts,
  with the human at the top of the chain (D-4). `needs-you` / `halt_for_human` are the
  escalation edges.

### 1.4 We'll learn these by building

Let's not over-spec these — a few real passes will tell us more than planning will:
exact atom/session fields and statuses, the actual prompt wording per node, how big an
"atom" should be, where determinism first breaks, whether the theater detector
actually catches anything, and the right thresholds for restart and backpressure
later on.

---

## 2. Sessions: where work runs

A session is the container everything runs in — workers and the control agent alike.
It's capped by the context window, so it's not a good place to keep truth: it holds
its own slice and reads the rest from files. When context fills, the session ends and
the files remain. The control agent is no exception — it checkpoints and resumes like
any worker.

Session types differ mostly by how much they can see and touch:

| type | who | sees | can | ends when |
|---|---|---|---|---|
| **worker** | one instance at one site | its site's environment | work, read-mostly, edit rarely | it returns a result, or context fills |
| **control** | the switchboard | a system-wide index | route, launch, swap config | you close it, or context fills |
| **surfacer** | the co-operator | widest — across sessions | read everything, write nothing | it reports, or context fills |
| **reviewer** | a review node | the artifact + what it hands to | read-only, adversarial; ideally a different model | it returns a result |

Control and surfacer can be one agent in two hats or two sessions — the real
difference is how wide they see, and the surfacer needs to stay wider than any worker
(I-3).

---

## 3. A way to picture it (the gear model)

A useful mental image for how one node drives the next without you pushing each step:

- A node's **result is the torque** — a node that ends without one is a gear spinning
  free: motion, nothing moved. (That's the rabbit-hole failure, in one picture.)
- The **mesh is the reconcile pass** — the next node engages because the log shows an
  atom short of its goal, not because we caught an event.
- The **gear ratio is fan-out** — one accepted story drives several tasks; a gate that
  admits everything is a stripped gear.
- The **pulley is your stamp** — a little input from you holds a big autonomous load.
  Your involvement is leverage, not a bottleneck.
- The **herringbone is worker + reviewer run opposite each other** — their opposition
  cancels the drift a single one would push downstream onto you.

---

## 4. Nodes, trajectories, end-states

A piece of work is defined by the path it took through the nodes — its **trajectory** —
not just its text. Same content with a different trajectory isn't the same thing (this
is the rule I-4 respects).

Every node ends with one of: `done · report · needs-you · rejected · needs-amend`.

A few things we avoid, and why they'd bite: a node signing off on its own output
(defeats the second set of eyes), a prompt editing and approving itself, and anything
self-approving (work should propel itself but never authorize itself).

---

## 5. The review stack

Each layer is the same shape: read what it needs, judge, admit or send back — read-only,
least-privilege, doesn't mutate.

| layer | gate | reads | returns |
|---|---|---|---|
| L0 | **value** | the goal the work claims to serve | accept · reject(no value) · reject(wrong value) · amend |
| L1 | **placement** | the global structure + what the atom connects to (Q-2) | fits · collides · wrong seam |
| L2 | **hand-off** | a cleared atom + what it hands to | ready for spec · send back |

**L0 — the story + the three-bucket check.** First-person, plain language, what
becomes possible and why it's worth it to you: `As an AI, I need to <capability, no
mechanism>, because <you> want <value>.` Then check whose appetite the *because*
serves — yours (ships), the agent's (drop it), or the work's own (drop it). Tag honest
confidence (`high | guessing`). After it's built, a second check: did the value
actually land (`confirmed | missed`)? Tasks closing isn't the same as value landing.

**L1 — placement: does it fit, and is it unique.** Locally fine doesn't mean globally
fine — the seam between two good pieces can still fail. And per I-4, two pieces that
agree on their shared seam *and share the same trajectory* should be one piece (collapse
drift, not deliberate shadows). L1 watches both.

**Atom** (the story is the value part of a larger atom):

```yaml
atom:
  id: atom.example.v0
  story:
    text: "As an AI, I need to <capability>, because Bdo wants <owner value>."
    value_confidence: high | guessing
    owner_stamp: pending | accept | reject_no_value | reject_wrong_value | amend
  concern_surface: systems | story | eval | prompt | repo | handoff   # one only
  incidence: { serves: [], touches: [], must_not_collide_with: [], hands_off_to: [] }
  desired_state: value_confirmed            # what we reconcile toward (D-8)
  verdicts:
    value_gate: pending | accept | reject_no_value | reject_wrong_value | amend
    placement_gate: pending | sound | collision | wrong_seam | halt_for_human
    eval_gate: pending | passed | reproduced_failure | invalid_eval | halt_for_human
  lineage: { prompt_versions: [], source_artifacts: [], receipts: [] }
```

**Hand-offs.** Every hand-off between nodes — and between sessions of one run (I-6) —
gets a quick witness, the same five questions every time: what the sender preserved,
what the receiver requires, what changed meaning during transfer, what got dropped
because there was no receiving node, and what the receiver added from its own prior.
This is where drift and blind pockets are most likely — the sender preserved one
invariant, the receiver expected another, and both can look locally correct.

---

## 6. The surfacing co-operator

Its job is to point at what the workers aren't looking at — it filters signals about
the work, not the work itself. We keep it honest with a few habits: several reviewers
with deliberately different agendas (their disagreement is itself useful, and the
variety is the Q-1 hedge), the ability to ask "what did you decide not to show me, and
why," the occasional look at something it skipped, and any change to what it prioritizes
being logged and reversible rather than quiet. How wide it sees is set by I-3.

---

## 7. Prompts as code, the manifest, versioning

We treat a prompt as versioned source with clear edges: what role it plays, what it
reads, what it's allowed to write, what it won't do, what it returns, and the evals
that back it. A prompt is *code* precisely when it changes what the system will admit,
reject, route, or ignore — wording that touches none of those is a patch; wording that
touches any of them is not "just prose," and gets versioned and eval'd like code.

The doc has three tiers, and only the first is hand-authored from scratch:

- the **manifest** — the one file you author by hand. It says which sources and config
  compose each environment and how the nodes connect.
- the **prompts** it references — hand-authored too, but as separately-versioned
  source the manifest points at, not as free prose.
- the **rendered environment file** — a build artifact whose version is a hash of its
  inputs (I-5) plus a semver. The smarts live in the build step; the include mechanism
  stays simple (it just inlines files, it doesn't resolve config at runtime).

Versioning follows behavior: a patch is wording, a minor adds a check or field or
eval, a major changes what a prompt is allowed to decide. We pair a prompt change with
an eval change — if it's sharper, an eval should show how, with a way back if it isn't.

Later, once we're local and steady: restart policy (who brings back a crashed session,
and when to escalate to you instead of looping) and backpressure (bounded queues, so a
slow stage — usually the human — doesn't get flooded).

---

## 8. What we lean on in Claude Code (and how to leave it)

So we know what's portable if we ever lift this to open-source / local:

| Claude Code gives us | role here | local replacement |
|---|---|---|
| `CLAUDE.md` auto-load | injects the environment | a context assembler that prepends the rendered file to the system prompt |
| `@path` imports (recursive, depth 5) | compose the environment | a build-time include step; note CC imports load at launch and don't shrink footprint |
| path-scoped rules (glob) | location → what loads | a glob → context router |
| nested environment files | per-site environments | per-site prompt fragments keyed by site |
| subagents (own context, own tools) | worker / reviewer sessions (§2) | separate model processes, each with its own prompt + tool allowlist |
| subagent tool/permission settings | role → access | a per-worker permission gate |
| hooks (JSON over stdin) | node triggers | an event bus + handlers that are safe to re-run |
| CC session + compaction lifecycle | the runtime container (D-7) | our own session object: spawn, checkpoint to files, resume |
| *(we build this)* | the reconcile loop (D-8) | a loop that reads the log and nudges each atom toward its goal, safely re-run (I-2) |
| *(we build this)* | the durable log (D-5) | an append-only log in files; state is a fold over it; we replay results, not reasoning |
| skills (load on use) | lazy reference | a lazy-load / retrieval step |
| the model itself | worker + reviewer | an adapter behind a standard endpoint; a different local review model helps Q-1 |

The pieces that take real work to rebuild are the isolated worker, the trigger mesh,
the reconcile loop, and the durable log — the last two CC doesn't hand us, so they're
ours to write.

These aren't portability trivia. The first four rows *are* the mechanism §16 names —
nested files + `@` + glob are how the place composes the environment (D-9); hooks +
subagents are how summoned nodes fire (D-10). §8 is the Claude-Code realization; §16 is
the system-level description.

---

## 9. How we keep this shippable

A few working agreements so this doesn't become a thing we polish forever:

1. A version means a real capability landed, not "I added more structure."
2. No receipt, no version bump.
3. Build the skeleton first, then one real node at a time — no second one until the
   first has a passing receipt.
4. Write the one-line "done" before starting. When it's met, stop.
5. Timebox the work, not the result — if we run out of room, we shrink the scope and
   ship the smaller thing.
6. Every version leaves behind something useful on its own, so stopping anywhere still
   leaves working pieces.

---

## 10. The test that matters

The easy bar is "atoms validate." The real one: can we make two locally-fine atoms
*refuse to fit*, and does L1 notice? We're testing the seam, not the cell. If
everything passes on the first try, the check isn't doing its job yet.

---

## 11. First goal: small, local

**For the first run (a mocked loop, all local):** one model endpoint (local or remote),
a durable log in files (D-5), one worker session, one atom with a goal state, mock
nodes that return fixed results, a reconcile pass (D-8) that moves one atom along, and
re-runs that don't double-act (I-2).

**It works when:** one fake atom reaches its goal state through reconcile passes over
the log, and killing the session midway loses nothing — the next pass picks it up from
the files. That one test exercises D-5, D-7, D-8, I-1, and I-2 together.

**Next:** make exactly one node real (start with L0), and don't make a second one real
until the first has a passing receipt.

**Not in scope yet:** the surfacer ensemble, a control session, multi-site work, the
review ensemble, restart policy, backpressure, a separate review model — each becomes
its own useful version later.

---

## 12. A reminder to ourselves

Let's run this against something real once before adding to the doctrine. If we catch
ourselves editing this file instead of building §11, that's the signal to close it and
go build.

---

## 13. Calls — now closed

Each of these was an open call; here's where it landed. Same discipline as §1.3 — the
verdict is recorded, not the question erased.

1. **Q-1 — reviewer independence.** *Agenda* independence over *model* independence.
   Different weights share training-distribution blind spots; different, adversarial
   agendas don't. At local scale, pick reviewers by opposing agenda first; a different
   review model is a cheap bonus once we're local (§8), not a precondition.

2. **D-8 — reconcile vs. event-driven.** Reconcile stays. §14 gives us the event
   *ergonomics* (don't poll; wake on change) without moving truth out of the log —
   events expose unfinished state, the reconcile pass still decides what's short of the
   goal. The §11 midway-kill test is what proves it earns its keep.

3. **The fit test — concretely.** Two locally-fine atoms refuse to fit when they name
   the *same seam with incompatible shape*. Concrete instance: atom A declares
   `hands_off_to: [seam.X]` and emits a value of one type; atom B declares
   `incidence.touches: [seam.X]` but its receiver can only consume another. Both pass
   their own value gate (L0); L1's `placement_gate` reads the global structure, sees the
   seam-X type clash, and returns `collision` (or `wrong_seam` if A declared a seam B
   doesn't actually expose). The test is built right when that pair *fails on purpose*
   and a flat "both atoms valid" run would have missed it (§10).

4. **Uniqueness (I-4).** The *wording* is fixed now (trajectory clause, §1.2). The
   *gate* is deferred — at local scale, with one worker and a handful of atoms,
   accidental drift-duplicates are cheap to spot by hand. Add the gate when the atom
   count makes a duplicate easy to miss, and have it collapse only drift, never
   trajectory.

5. **Session ↔ CC session.** Many-to-one. One run spans several CC sessions via
   file-checkpointed resume — that's the whole point of I-6 (a resume is a hand-off).
   Our session object is the durable unit; the CC session is just the container it
   currently runs inside.

---

## 14. Seams: durable event surfaces

The seam between nodes and loops is not just a conceptual boundary and not just an
ephemeral async queue. It is a durable, subscribable event surface. Artifacts announce
state changes there; nodes subscribe to the changes they know how to judge; nodes
append receipts rather than becoming the truth themselves.

Working definition:

> **A seam is a durable, subscribable event surface between loops, where artifacts
> announce state changes and nodes append verdict receipts.**

This keeps the useful part of async messaging without losing D-5, D-6, D-8, I-1,
and I-2. Events can wake the system up, but the log remains authoritative and the
reconcile pass decides what is still short of the atom's desired state.

The weak version is:

```text
events trigger agents
```

The stronger version, the one we're building:

```text
events expose unfinished state;
agents subscribe;
receipts accumulate;
reconcile advances the artifact;
the file log remains authoritative.
```

### 14.1 Minimal local shape

For the first local build, do not add a real broker yet. Use files that behave like
a queue and a replayable log:

```text
.ai-native/
  log/
    events.jsonl
    receipts.jsonl
  queues/
    value-to-placement.pending.jsonl
    placement-to-handoff.pending.jsonl
  offsets/
    placement-gate.offset
    surfacer.offset
    eval-node.offset
```

This gives the first build queue semantics, replay, idempotence, and crash recovery
without adding infrastructure.

One rule keeps it honest against D-5: **`queues/` and `offsets/` are a cache, never
truth.** They're a fold over `log/` — delete them and a replay rebuilds them exactly.
"Is it in the pending queue" is never the state of an atom; the state is always the fold
over events + receipts (§14.4). The moment a node treats queue membership or its own
offset as authoritative, D-8 is broken. Later this can be backed by NATS, Redis Streams,
Kafka, SQLite, or another broker, but the behavioral contract — and the cache rule —
stays the same.

### 14.2 Event shape

A seam event should name the artifact, the artifact hash, the seam it is crossing,
the expected receiving work, and the terminal states that would close the event.

```yaml
event:
  id: evt.2026-...
  type: atom.created | story.stamped | placement.rejected | prompt.changed | eval.failed
  artifact_id: atom.example.v0
  artifact_hash: sha256:...
  from_node: value-loop.story-author
  seam: value-to-placement
  requires:
    - placement_gate
  visible_to:
    - placement-reviewer
    - surfacer
    - reconcile-controller
  terminal_expected:
    - sound
    - collision
    - wrong_seam
    - halt_for_human
```

Subscribers are virtual nodes. Examples:

```text
placement-gate subscribes to: story.accepted
handoff-gate subscribes to: placement.sound
eval-node subscribes to: prompt.changed, atom.admitted
surfacer subscribes to: rejected, halt_for_human, drift, repeated-failure
control/router subscribes to: anything short of desired_state
```

### 14.3 Receipt shape

A subscriber does not consume truth. It appends a receipt. The receipt is the thing
the reconcile pass can replay, fold, and compare against the desired state.

```yaml
receipt:
  event_id: evt.2026-...
  node: placement-gate.v0.1
  artifact_id: atom.example.v0
  artifact_hash: sha256:...
  verdict: wrong_seam
  reason: accepted value story does not declare the receiver seam it depends on
  next_suggested_event: amend.incidence
```

### 14.4 Reconcile rule

The reconcile pass reads the durable log and asks:

```text
What goal state does this atom want?
What events have been announced?
What receipts exist?
What is missing?
Which seam should receive the next event?
```

That means async events are the wake-up surface, not the source of truth. The source
of truth remains the file log, and the state of an atom is still a fold over events
and receipts.

### 14.5 Why this supports the main agenda

This strengthens the doctrine without changing the first build:

- It makes seams concrete enough to implement locally.
- It preserves the file-log authority already named in D-5.
- It supports D-8 reconcile instead of replacing it with fire-and-forget events.
- It gives surfacers and reviewers a natural subscription surface.
- It makes cross-loop blind spots inspectable because hand-offs become explicit
  events with receipt trails.

---

## 15. Ambient control

The reconcile loop (D-8) pushes work forward. Ambient control is the layer around it
that keeps the field *workable* while it does — and it's a description of how the system
runs, not a future feature. The full telling is in
[docs/culture/the-ambient-loop.md](culture/the-ambient-loop.md); the load-bearing shape:

- **The medium is the log.** Pressure isn't a hidden metric — it's visible field-state
  (queue depth, staleness, contradiction-count, smell). Sensors read the log, valves
  write the log. The log is the air the control signals move through (D-5).
- **The setpoint is an admitted dial (I-8).** What temperature to hold is a typed
  record, audited and adjustable by admission — not a literal in a node.
- **Control is bidirectional.** Compare sensed pressure to the setpoint and act *both
  ways*:
  - **too cold → heat:** the field is stalled — stoke cooperation (fan-out, summon
    nodes, ring more signals).
  - **too hot → cool:** the field is in runaway — throttle spawning, shed or defer load,
    widen tolerance, bleed through the ports, slow the fan-out.
- **The actuator is push-pull (the herringbone-solenoid).** It turns the pressure signal
  into corrective motion in either direction without the action becoming a new source of
  pressure downstream; the worker/reviewer opposition (§3) is what keeps either direction
  from overshooting.
- **Two time-scales.** The **fast loop** holds the setpoint each pass. The **slow loop**
  moves the setpoint itself — accumulated outcomes re-admit the dial, so the operating
  temperature is learned (run hot to explore, cool to consolidate). The slow loop *is*
  the environment adapting; the fast loop is the agent acting (D-12).

The thing this names that orchestration misses: **cooling is the load-bearing
direction** (I-7). Every "add more agents" approach can heat; almost none can tell
themselves to back off. Heating is easy; knowing when to chill is the capability.

"Temperature" is two things at once — how much activity, and how hot the inference runs
(creative ↔ deterministic). The same control move can mean *spawn fewer workers* or
*drop the fleet's sampling temperature toward determinism* when risk spikes.

---

## 16. The mechanism: place, summons, ledger

D-1 ("files are the environment") and D-5 ("truth lives in the log") are realized by
three moves that §8 only listed as portability notes. They're how the system actually
runs; the plain-language telling is in
[docs/culture/the-idea.md](culture/the-idea.md).

- **The place is the program (D-9).** A node's briefing is composed *on arrival* from the
  stack of environment files along its path — root rules, then site rules, then the rules
  at the exact spot it runs (nested files, `@`-composed, glob-scoped). Nobody configures
  the node; the environment assembles itself around where it stands. Move it and it's a
  different program on the same model.
- **Summoned, not staffed (D-10).** A node is a standing offer the system answers, not a
  process on a roster. A signal (a hook) fires, a node blinks in at a place, reads the
  local environment, does one bounded thing, writes its line, and dissolves — holding no
  state, because the place and the log hold it instead. This is why mortality is safe
  (I-1): kill a node mid-line and the next one summoned reads the log and continues.
- **The ledger remembers; no one signs their own line.** The append-only log is the only
  thing allowed to remember; the state of any work is the read down it (D-5). A result
  isn't true because its author says so — a *different* reader countersigns (D-2), and
  the last countersign is always yours (D-4). A node propels work; it never authorizes it
  (§4).
