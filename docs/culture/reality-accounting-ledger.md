# Reality Accounting Ledger

> **Status: OWNER-STEERED / ADDITIVE — session-authored draft, provisional
> until bdo stamps it.** This is the handwritten retelling of the owner's
> *Reality Accounting Ledger* journal
> ([docs/sources/Owners Journal - Reality Accounting Ledger.pdf](../sources/Owners%20Journal%20-%20Reality%20Accounting%20Ledger.pdf),
> read-only inspiration), recut in this repo's own vocabulary, its real
> epics, and its on-disk implementation. It does **not** replace
> [the-idea.md](the-idea.md), define an epic, or claim the system already
> satisfies the realities below. It is an accounting surface for **desired
> realities that exceed the current implementation** — each entry names a
> target state, separates it from present evidence, and defines the smallest
> move that would make it more real.

## Why this file exists

High-level owner intent must not live only in conversation. Some desired
realities are too large, too early, or too cross-cutting to enter the repo
directly as an epic, a proposal, or a done-line — but losing them, or
mistaking them for shipped fact, are both failures. This ledger is the
**holding form** between those two failures: it preserves the target without
confusing it for current truth.

It is the third culture document, beside its siblings:

- [the-idea.md](the-idea.md) — *the public telling* (CONFIRMED by bdo,
  2026-06-21): what the project is for, written for a cold reader.
- [the-administrator.md](the-administrator.md) — *the operator telling*: how
  a fleet of work is overseen.
- **this file** — *the accounting layer beneath future explanations*: what
  owner-carried realities are not fully real yet, what already supports them,
  what is missing, and what would be dangerous to claim too early.

Per this directory's law ([CLAUDE.md](CLAUDE.md)): everything here is a fold
of the record told as prose. Where a sentence here and the record disagree,
**the record wins and the sentence is the bug.**

---

## The spine: one thesis under all four target realities

bdo's own phrasing for the upper target, recorded this session:

> **Reality cutting from a mode-free exploration based on consequence-
> propagation observations at different speeds, using generative systems
> that are AI-native.**

The source journal carried four separate target realities. This is the claim
underneath all of them — the verb the journal never named. It decomposes,
phrase by phrase, into parts that already exist on disk, and the seams
between them are where the unrealized work lives:

| the phrase | what it means here | where it lives today |
|---|---|---|
| **reality cutting** | a *reality* is an undifferentiated prior (all axes open, ⊘); the system **cuts** axes in it under a pressure, and each cut emits a *slot* (a distinction with a refusal-tooth). The basis is *derived*, never imported. | [loop/basis.py](../../loop/basis.py) — the membrane: `cut(reality, axis, pressure, refusal)`; [generative-basis-membrane.proposal.md](../../.ai-native/proposals/generative-basis-membrane.proposal.md) |
| **mode-free exploration** | begin from *raw* consequence-witnessing, not a fixed taxonomy; representation (the relational middle band) and mechanism come *after*, and the Observable gate fires *first*. | [loop/observe.py](../../loop/observe.py), [loop/relation_ledger.py](../../loop/relation_ledger.py), [loop/over_containment.py](../../loop/over_containment.py); `epic.model-free-mode-response` |
| **consequence-propagation observations** | a fact's *consequences* (a changed state distinct from the work) are nodes; effects propagate along typed, decaying edges within a bounded radius; the field is governed by what the world may *become*, not what an agent may *do*. | [loop/consequence_graph.py](../../loop/consequence_graph.py); `epic.consequence-graph-response`; the consequence-policy model |
| **at different speeds** | speed is the *meta-level* of an act — respond / retune / author — a gradient, not the §14 fast/slow binary. The field is *live* (liveness), not scheduler-driven; scheduling is one pulse among many. | [loop/heartbeat.py](../../loop/heartbeat.py), [loop/orchestrate.py](../../loop/orchestrate.py), [loop/slowloop.py](../../loop/slowloop.py); `epic.graded-speed` (held — see Accounting) |
| **generative systems, AI-native** | the basis, the operators, and the cuts are *composed by inference against a bounded standard* (govern the dial, not each output), not hand-authored — yet every generated piece carries its papers (provenance, a resolvable citation, an independent verdict). | [loop/basis.py](../../loop/basis.py) (the basis-generator); inference-as-composition; the doctrine's "deep bet" (small handle, unbounded reach) |

The reading: **the system witnesses consequence propagation (mode-free),
cuts reality into derived primaries from those traces (the membrane),
expresses the result as a felt field, and moves on it at graded speeds —
all composed generatively, all kept accountable to witnessed traces.** The
four target realities below are four faces of this one claim.

---

## The boundary that must never blur

The governing rule of this whole surface:

> **Desired reality may create pressure, but it may not count as current
> reality.** It can steer inquiry, shape probes, reveal missing mechanisms,
> or motivate a proposal. It cannot be treated as true until there is
> evidence, cannot authorize work by itself, cannot bypass a gate, and
> cannot become doctrine by sounding coherent.

Every entry preserves the difference between **witnessed · inferred ·
proposed · confirmed · implemented** — and that boundary is already a thing
this repo *enforces*, not just describes. It maps directly onto the term
economy's evidence grades
([causality/term_economy.py](../../causality/term_economy.py)): a term with
no resolvable evidence can never be `minted`; a citation that points to
nothing is a `ghost`. The same discipline runs over *desired realities* here
that runs over *vocabulary* there. If the boundary is unclear in an entry,
the entry is not ready to guide work.

---

## Target Reality 001 — Reality cutting: a derived basis, not an imported taxonomy

### Desired reality
The system should not begin from a fixed set of categories and force work to
fit them. It should begin from **consequence witnessing** — what happened,
what changed, what caused it, what it touched, what became possible, what
became unsafe, what pressure moved, what authority was used, what trace
proves it — and from those traces *derive its own* primaries, operators, and
field-forces. **The model comes after consequence.** "Reality cutting" is the
mechanism of that derivation: a reality is an undifferentiated prior, and a
cut under a pressure decides one axis, emitting one primary.

### Why it matters
This is the difference between a system that imposes meaning and one that
*discovers* it. A fixed taxonomy is a guess frozen at design time; a derived
basis flexes with the pressure it is actually under (the colour analogy:
B&W, grayscale, RGB, CMYK, PANTONE are all correct, each fitted to a
different pressure over the same spectrum). Govern the pressure, not the
basis.

### Current reality
The mechanism exists as a working **instrument**, not yet as an installed
organ. [loop/basis.py](../../loop/basis.py) is the membrane made mechanical:
`cut(reality, axis, pressure, refusal)` decides one open axis and emits a
slot, gated by a gamut law (a cut that discriminates nothing is *poetry* and
is refused; a merge across two distinct live refusals punches a *gamut hole*
and is refused). Its §10 self-test admits the four real basis moves and
refuses the four fakes, and passes this session. The five-primary work basis
it derives under accountability pressure — `APPEND · FOLD · HASH-IDENTITY ·
CITE · VERDICT` — is itself derived (not picked) and every primary cites a
real refusal-tooth in the running code (the panel report,
[corpus-derivation-organ.proposal.md](../../.ai-native/proposals/corpus-derivation-organ.proposal.md) §3).

### Partial reality
The instrument cuts slots and reality-transitions **in the abstract**.
Nothing yet binds a slot to a live corpus operation and confirms its refusal
fires against real code. The five primaries are derived for the *work* /
*accountability* pressure; the *meaning* reality is currently all-⊘ — the
membrane has not yet cut a single meaning-axis.

### Unrealized delta
- No slot is yet **`fit`** to a live operation (the honest next move:
  bind `CITE` to `consequence_graph.resolves` and confirm it rejects an
  unresolved citation — turning the checker into a kernel).
- No **meaning** cut has been driven for real (the corpus panel's CTA-1:
  drive RELATE · PREDICT · SCORE through `relation_ledger` with one actual
  meaning record and get a real `PREDICTIVE`/`TRIVIAL` fold).
- The derivation **skill** (explore → consequence-map → derive → generate →
  critique, with a mandatory self-demote-POSTURE test) is proposed, not
  built (CTA-2).

### Accounting
- [loop/basis.py](../../loop/basis.py) — the membrane instrument *(implemented; a model, not yet the membrane)*
- [generative-basis-membrane.proposal.md](../../.ai-native/proposals/generative-basis-membrane.proposal.md) — the full algebra *(proposed)*
- [corpus-derivation-organ.proposal.md](../../.ai-native/proposals/corpus-derivation-organ.proposal.md) — the derived grammar + CTAs *(proposed)*
- The absorbed ghost: `accounting-attributing-organ.proposal.md` — named in
  prior conversation as the home of "derive a medium's own primaries"; **no
  longer on disk**, its idea carried forward into the two proposals above
  (see Accounting of citations).

### Probe candidates
- **P1** — One slot is `fit` to a live operation and its refusal is shown
  firing against real code (not the model).
- **P2** — Given a corpus, the derivation skill produces a basis and
  *self-demotes* a non-primary (e.g. POSTURE) without a human catching it.
- **P3** — One meaning-bearing cut crosses for real and folds to
  `PREDICTIVE` or `TRIVIAL`.

### Next admissible move
`fit` exactly one slot (`CITE` → `consequence_graph.resolves`). More basis
algebra is *not* the move — that is where elegance starts to outrun teeth
(the proposal's own honest edge).

### Risk if misclaimed
If "derived primaries" are claimed before a slot is `fit`, the system treats
a *model of* the membrane as the membrane — an ungoverned story dressed as
mechanism. An inferred reality must stay accountable to witnessed traces.

---

## Target Reality 002 — The felt field

### Desired reality
The system should represent the state of work as a **felt field**: a
structured set of force-like pressures that make current reality legible
without the owner inspecting every file, branch, issue, and proposal. A
session should inherit signals — *hot, blocked, stale, risky, over-capacity,
ready, orphaned, converging, exploratory, owner-needed* — and the candidate
forces (pressure, gravity, friction, heat, cooling, tension, momentum,
inertia, freshness, capacity, risk) should each become a **computable fold,
or be rejected.** These are not decorative metaphors.

### Why it matters
It compresses an unbounded sprawl into a small, checkable state the owner can
read in seconds and a session can act on — the difference between a dashboard
you must read and a field you can feel.

### Current reality
The repo already computes real pressure folds: [loop/gaps.py](../../loop/gaps.py)
(a fixed pressure-ordered backlog — the top gap is the work),
[loop/orchestrate.py](../../loop/orchestrate.py) (senses pressure vs setpoint,
heats when stalled, cools when the human queue is at cap), the census, the
digest, retro, and heal. `epic.the-field` (`field.py`) carries the
field-reading direction, and the anti-confabulation gate already bites
(`field.py:316-393` — a node asserted as fact with no resolvable subject is
a ghost).

### Partial reality
The system can surface a *top* gap or *next* pressure point, and it computes
*some* forces (heat/cool in orchestrate). It cannot yet compute a **multi-
force payload** of the field at once (`pressure: high / friction: medium /
heat: high / freshness: stale / owner-load: over-cap / top allowed
discharge: ask owner to bless probe P3`).

### Unrealized delta
- There is **no admitted field-force register** — no shared definition of
  what each force is, its inputs, its fold/check, its failure mode, and its
  permitted response path.
- There is no structural guarantee that **a force cannot authorize action by
  itself** — it may only surface pressure or route to a gateway.

### Accounting
- [outcome-pressure-fold.proposal.md](../../.ai-native/proposals/outcome-pressure-fold.proposal.md) — the desired-vs-current pressure channel *(proposed)*
- [loop/gaps.py](../../loop/gaps.py), [loop/orchestrate.py](../../loop/orchestrate.py) — real pressure folds *(implemented)*
- [outcomes/](../../outcomes/) — the evidence-bearing probe pole *(implemented as form; probes per-outcome)*
- `strategy-metabolism.md`, `session-gateway.proposal.md`, `gated-pubsub-brokerage.proposal.md` — supporting shapes *(proposed)*
- The missing target: `field-forces.md` (a register) — **does not exist yet** (an unrealized delta, correctly absent).

### Probe candidates
- **P1** — At session wake, the system surfaces ≥3 *computed* field-forces
  with supporting evidence.
- **P2** — Each force carries a definition, input set, fold/check, failure
  mode, and permitted response path.
- **P3** — No field-force can authorize action directly — only surface or
  route.

### Next admissible move
Create `field-forces.md`: one entry per force (definition · inputs ·
computed fold/check · what it makes visible · what it may route · what it
must never authorize · failure mode). A force is admitted **only when it can
be checked.**

### Risk if misclaimed
If the felt field is claimed before it is computable, evocative language gets
mistaken for operational state — the project's vocabulary inflates and its
grip slips.

---

## Target Reality 003 — Liveness and graded speed, not scheduling

### Desired reality
The system should not be scheduler-native ("time arrives → run job"). The
root model is **liveness**: the field is on; signals arrive; folds re-derive
pressure; thresholds trip; gateways permit or refuse crossings; actuators
discharge allowed motion; receipts alter the next fold. Scheduling is **one
pulse source among many**, never the root. And motion happens at **graded
speed** — speed is the meta-level of an act (respond / retune / author), a
gradient, not a binary.

### Why it matters
A scheduler makes a long-running process into a hidden authority — "the
stream becomes the scheduler-god." Liveness keeps the stream a *carrier of
availability, not a source of permission.* Graded speed lets the system
answer in the moment, retune its own dials over the hour, and author new
capability over the arc — without collapsing all three into one tempo.

### Current reality
The repo already moves toward inherited pressure at session wake (the summon
hook hands every session its top gap), and runs an ambient control loop:
[loop/heartbeat.py](../../loop/heartbeat.py) (the guaranteed tick),
[loop/orchestrate.py](../../loop/orchestrate.py) (the fast ambient loop),
[loop/slowloop.py](../../loop/slowloop.py) (the slow loop's proposer) and
[loop/disposer.py](../../loop/disposer.py) (its bounded disposer). The fast
and slow tempos already slide in code.

### Partial reality
There are pulses and event-like behaviors, but **no single ambient-loop
doctrine** written down — and the doctrine itself names this gap: the
companion telling [the-ambient-loop.md](the-ambient-loop.md) is **absent**
(named in [the-idea.md](the-idea.md) and this directory's
[CLAUDE.md](CLAUDE.md) as a known, deliberately-empty hole). The `author`
speed band is a disconnected island — fast↔medium slide in code, but
"author new capability" is not yet on the same gradient (the graded-speed
arc's central gap).

### Unrealized delta
- No cold-readable **ambient-loop document** (`the-ambient-loop.md`).
- No standard **pulse grammar** (time · event · owner-arrival · repo-change ·
  external-signal · threshold-crossing · manual-wake), separated from
  authorization.
- No formal law that **a stream may witness and route but not command.**
- The **speed gradient** is not yet one continuous fold from respond →
  retune → author (the `epic.graded-speed` work is held off-trunk — see
  Accounting).

### Accounting
- [loop/heartbeat.py](../../loop/heartbeat.py), [loop/orchestrate.py](../../loop/orchestrate.py), [loop/slowloop.py](../../loop/slowloop.py), [loop/disposer.py](../../loop/disposer.py) — the ambient loop *(implemented)*
- `session-gateway.proposal.md`, `gated-pubsub-brokerage.proposal.md`, `outcome-pressure-fold.proposal.md` — supporting shapes *(proposed)*
- `epic.graded-speed` — the speed-gradient arc, **named in issue #498, work held on a rescue branch, not on main** (see Accounting of citations).
- The missing targets: `the-ambient-loop.md` and a unified gradient fold (`loop/gradient.py`, held) — **do not exist on main yet**.

### Probe candidates
- **P1** — The repo contains a cold-readable ambient-loop document.
- **P2** — Pulse types are defined and separated from authorization.
- **P3** — A pulse can cause sensing, folding, and routing, but cannot itself
  authorize consequential action.
- **P4** — Respond, retune, and author are three settings on **one**
  measurable gradient, not three disconnected mechanisms.

### Next admissible move
Write `the-ambient-loop.md` with the minimum law:

> Streams witness. Folds derive. Thresholds surface pressure. Gateways
> decide crossings. Actuators discharge permitted motion. Records preserve
> consequence. The owner steers authority.

### Risk if misclaimed
If liveness is misclaimed, a long-running process becomes a hidden
authority. The stream must remain a carrier of availability, not a source of
permission.

---

## Target Reality 004 — Learned operators, not fixed workflows

### Desired reality
The system should not only *run* predesigned workflows. It should learn
**operators**: repeated, attributed routes that reliably change the field
*inside an accepted consequence envelope*. A workflow says "do these steps in
this order"; an operator says "given this pressure, this authority, this
surface, and this reversibility class, this route has repeatedly produced
acceptable consequences." Candidate operators: turn owner intent into probes;
separate desired from current reality; surface a decision without flooding
the owner; route a raw idea into a proposal; request independent review;
quarantine unsafe motion; promote a snapshot; prune stale possibility;
derive a local primary from a corpus.

### Why it matters
Operators are the system *learning from its own consequence history* — the
difference between a tool you wield and a habit the system has earned. It is
the same shape as the deep bet (a small handle, unbounded reach), pointed at
the routes themselves.

### Current reality
The repo already has repeated, instrumented routes that are close to
operators: `ask`, `recommend`, `gate`, `fold`, `land`, `reflect`, `summon`,
`review`, `confirm`, plus the strategy lobe (`explore → claim → build →
prune`, [strategy-metabolism.md](../../.ai-native/proposals/strategy-metabolism.md),
`epic.strategy`). [loop/retro.py](../../loop/retro.py) already folds *all of
history* for recurring patterns — the raw material an operator-learner reads.

### Partial reality
The routes exist and recur, but they are **not yet classified as operators**,
and the system does not yet *measure* whether a route reliably creates
acceptable consequences. The strategy lobe metabolizes pre-evidence motion
but does not yet promote a route to "learned."

### Unrealized delta
- No **operator register**, and no clean distinction between *tool ·
  workflow · operator · reflex · surface · gateway · habit*.
- No **test** for whether an operator is *learned* (repeated consequence
  supports it) rather than merely *described*.
- No **accepted consequence envelope** attached to each admitted operator.

### Accounting
- [strategy-metabolism.md](../../.ai-native/proposals/strategy-metabolism.md), `epic.strategy` — the scout/claim/build/prune lobe *(proposed/partial)*
- [loop/retro.py](../../loop/retro.py) — the all-history pattern fold *(implemented)*
- `structured-communication-channel.proposal.md`, `gateway-policy-spine.proposal.md`, `session-gateway.proposal.md` — supporting shapes *(proposed)*
- The missing target: `operator-register.md` — **does not exist yet**.

### Probe candidates
- **P1** — The repo names 10 repeated routes and classifies each (tool /
  workflow / operator / reflex / surface / gateway / habit).
- **P2** — ≥3 operators have evidence of repeated successful use.
- **P3** — Each admitted operator has an accepted consequence envelope.

### Next admissible move
Create `operator-register.md`. Definition: *an operator is a repeated,
attributed route that reliably changes the field within an accepted
consequence envelope.*

### Risk if misclaimed
If operators are misclaimed, the system renames workflows as "learning,"
weakening the distinction. A route becomes an operator only when repeated
consequence supports it.

---

## Target Reality 005 — Consequence propagation as the field's connective tissue

### Desired reality
The connective tissue under all four realities above: govern **what the
world may become** (consequence), not what an agent may *do* (action) —
because AI actions are too many to enumerate, while consequences can be
witnessed, bounded, repaired, routed, or forbidden. A fact's *consequences*
(a changed state, distinct from the work-unit) are first-class nodes;
effects propagate along **typed, decaying edges within a bounded radius**;
the chain Root → Cause → Effect → Consequence → Obligation → Policy →
NextAction is the system's reasoning spine.

### Why it matters
This is the "observations" half of the thesis — the system's evidence about
reality is *consequence traces*, and everything else (the cuts, the field,
the operators) is computed from them. It is also the governance model that
makes bounded autonomy safe: bound the results you will accept, not the
actions allowed.

### Current reality
[loop/consequence_graph.py](../../loop/consequence_graph.py) is the
**tier-1 auditable plane** (done-line 0167, `epic.consequence-graph-response`):
a read-only fold where nodes are log subjects, edges are *literal log facts*
(no inferred causal edges yet), `failure`/`repair` marks fold from negating
receipts and healed bites, and one bounded typed decaying propagation pass
(radius 2, per-edge-kind decay, channels never netted) makes the field a
living target without smearing. Its §10 tooth refuses a mark whose citation
does not resolve. The Observable-as-gate ([loop/observe.py](../../loop/observe.py))
forces an exploratory act to declare its attribution path *before it runs* —
if it cannot name the receipt that ties effect back to actor, the act halts.

### Partial reality
Tier-1 (literal log edges) is real and read-only. **Tier-2 inferred causal
edges**, a `value`/money channel, the consequence *volume*, and any
*actuation* (the graph changing the world, not just witnessing it) are all
deferred — witness before actuator.

### Unrealized delta
- No **inferred** (tier-2) edges, so the graph cannot yet hypothesize a cause
  it did not literally log.
- No **actuator**: the graph names over-bites and next-moves but never clears
  a park or re-opens a verdict (propose-only, D-4).
- The full chain (Obligation → Policy → NextAction) is modeled in the
  proposal but not yet a running fold end-to-end.

### Accounting
- [loop/consequence_graph.py](../../loop/consequence_graph.py) — the tier-1 plane *(implemented, read-only)*
- [loop/observe.py](../../loop/observe.py), [loop/relation_ledger.py](../../loop/relation_ledger.py), [loop/over_containment.py](../../loop/over_containment.py) — the consequence/observation parts *(implemented)*
- `epic.consequence-graph-response`, `epic.model-free-mode-response` — the arcs *(confirmed/in-flight)*
- The consequence-policy model — captured in `change-management.proposal.md` *(proposed)*

### Probe candidates
- **P1** — Given 10 recorded work events, the system accounts for what
  changed, what caused it, and what downstream pressure moved (the journal's
  original P1 for TR-001 — it belongs here).
- **P2** — A consequence node is distinct from its work-unit and is cited; a
  mark with an unresolvable citation is refused.
- **P3** — The system distinguishes witnessed / inferred / proposed /
  confirmed / implemented so inference is never treated as fact.

### Next admissible move
Define the **minimum consequence-witness record** (the journal's TR-001 next
move, which belongs to this connective entry): *actor · surface ·
gesture/action · object · before-state · after-state · observed consequence ·
source/evidence · confidence · reversibility · authority · attribution ·
next pressure.* Then fit one part to write it.

### Risk if misclaimed
If consequence propagation is claimed beyond tier-1, the system begins
treating *inferred* causal edges as *witnessed* ones — the exact failure the
witnessed/inferred boundary exists to prevent.

---

## Accounting of citations — what is named, and whether it participates

The owner's directive: *account for what is cited and participates, and if
something is named but does not, say why.* This audits every file the source
journal cites (and the thesis parts), against what is on disk on `main`
this session. Verdicts use the same grades as the term economy.

### Resolves and participates

| cited | resolves at | participates as | verdict |
|---|---|---|---|
| `the-idea.md` | [docs/culture/the-idea.md](the-idea.md) | the public telling (CONFIRMED by bdo) | **minted-doctrine** |
| `outcome-pressure-fold.proposal.md` | [.ai-native/proposals/](../../.ai-native/proposals/outcome-pressure-fold.proposal.md) | the desired-vs-current pressure channel | **proposed** (captured shape, not implemented) |
| `session-gateway.proposal.md` | [.ai-native/proposals/](../../.ai-native/proposals/session-gateway.proposal.md) | the session-as-crossing shape | **proposed** |
| `gateway-policy-spine.proposal.md` | [.ai-native/proposals/](../../.ai-native/proposals/gateway-policy-spine.proposal.md) | the governance-over-PEP/PDP/PIP spine | **proposed** |
| `structured-communication-channel.proposal.md` | [.ai-native/proposals/](../../.ai-native/proposals/structured-communication-channel.proposal.md) | the typed owner↔agent channel | **proposed** (its first part shipped as `/recommend`) |
| `gated-pubsub-brokerage.proposal.md` | [.ai-native/proposals/](../../.ai-native/proposals/gated-pubsub-brokerage.proposal.md) | the brokerage / routing-on-record shape | **proposed** |
| `strategy-metabolism.md` | [.ai-native/proposals/strategy-metabolism.md](../../.ai-native/proposals/strategy-metabolism.md) | the scout/claim/build/prune lobe | **proposed/partial** (`epic.strategy`; scout lobe landed) |

> Note: the journal cites `strategy-metabolism.md` with no path; it lives at
> `.ai-native/proposals/strategy-metabolism.md` (a proposal, not an epic
> file). Resolves once the path is supplied.

### Named but does NOT participate — and why

| named | status on `main` | why it does not participate |
|---|---|---|
| `accounting-attributing-organ.proposal.md` | **GHOST** — on disk nowhere (only appears in the gitignored hook/tool-use traces, i.e. it was *typed* in past commands but never written as a file). | The idea — *derive a medium's own primaries / RGB rather than pick fixed containers* — was **carried forward, not dropped**: it is now the substance of [corpus-derivation-organ.proposal.md](../../.ai-native/proposals/corpus-derivation-organ.proposal.md) and [generative-basis-membrane.proposal.md](../../.ai-native/proposals/generative-basis-membrane.proposal.md) + [loop/basis.py](../../loop/basis.py). **Recommendation: cut the ghost citation; cite the two real proposals instead.** |
| `epic.graded-speed` | **NAMED, WORK HELD OFF-TRUNK** — referenced in issue #498 and in memory, but there is no `epic.graded-speed.json` in [.ai-native/epics/](../../.ai-native/epics/) and no `gradient.py` on `main`; the work sits on a rescue branch (PR #489). | The arc is real intent but its files have not landed. It participates as *pressure* (TR-003), not as *implementation*. **Recommendation: land or re-cut the arc so the citation resolves on `main`.** |
| `field-forces.md` | **DOES NOT EXIST** | Correct — it is TR-002's *next admissible move*, an unrealized delta. Named as a target, not claimed as fact. |
| `operator-register.md` | **DOES NOT EXIST** | Correct — TR-004's next admissible move, an unrealized delta. |
| `the-ambient-loop.md` | **DOES NOT EXIST** | Correct — TR-003's next admissible move; the doctrine and [the-idea.md](the-idea.md) already name it as a deliberately-empty, known hole. |

### Thesis parts — all resolve and participate

`loop/basis.py`, `loop/consequence_graph.py`, `loop/observe.py`,
`loop/relation_ledger.py`, `loop/over_containment.py`, `loop/heartbeat.py`,
`loop/orchestrate.py`, `loop/slowloop.py`, `loop/disposer.py`,
`loop/gaps.py`, `loop/retro.py`, and both new proposals
(`generative-basis-membrane`, `corpus-derivation-organ`) all resolve on disk
this session and participate as cited above. The membrane self-test
(`loop/basis.py`) runs and passes.

---

## Entry template

Each new entry uses the same accounting shape:

```
## Target Reality NNN — [short name]
### Desired reality      — what state the owner is trying to make real
### Why it matters        — why this changes the class of the system
### Current reality       — what exists today in files/code/tests/logs/records
### Partial reality       — seed, proposal, analogy, one-off, unresolved composition
### Unrealized delta      — what is missing
### Accounting            — which files/probes/receipts/folds support the inventory
### Probe candidates      — checkable desired-reality statements
### Next admissible move  — the smallest useful formal move
### Risk if misclaimed    — what breaks if treated as current fact too early
```

---

## Standing law

> Desired realities enter as **pressure**, not truth.
> They become **truth** only through evidence.
> They become **work** only through admitted routes.
> They become **authority** only through governance.
> They become **system behavior** only through implementation.
> They become **experience** only when their traces remain comparable.

---

## Where this comes from

- The **source journal** — bdo's *Owners Journal — Reality Accounting
  Ledger* ([docs/sources/](../sources/Owners%20Journal%20-%20Reality%20Accounting%20Ledger.pdf),
  read-only): the four target realities, the boundary discipline, the entry
  template, and the standing law are his — recut here in repo vocabulary.
- The **thesis spine** — bdo's phrasing this session ("reality cutting from a
  mode-free exploration based on consequence-propagation observations at
  different speeds using generative systems that are AI-native").
- The **parts and their grades** — the running code cited inline; the
  evidence discipline is [causality/term_economy.py](../../causality/term_economy.py)'s.
- The **frame** (goal vs engine, the slope measure) — [the-idea.md](the-idea.md)
  and [report 0004](../../.ai-native/reports/0004-the-frame-harness-and-fabric.md).

Where this retelling and the record disagree, the record wins and this file
is the bug. This file is **provisional until bdo stamps it.**
</content>
</invoke>
