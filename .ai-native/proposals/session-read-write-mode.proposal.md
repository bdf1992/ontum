# Read by default, write-on as the first ledger line — the session read/write mode

**Status: PROPOSED** (bdo's to name; a session's only to propose, D-4).
Born from bdo, 2026-06-23: *"We should start every single session in READ
only mode, and turning write on is a named event that happens alongside the
first actual write — this way we can track when a session is in a Read or
Write mode. AKA when you write, you also write to the ledger as the first
write. When you read, you're good… for now."*

## The shape (the purpose)

Every session is **born read-only**. A session's first deliberate write is not
the mutation itself — it is a `session_write_on` line on the append-only log
that names the **read → write crossing**, and the mutation follows it. So a
session's mode is never a stored flag: it is a **fact folded from the log** (the
log is truth; everything else is a fold). A session that only reads never
appears as a writer. A session that writes, its *very first ledger line* is the
one that says "I am now writing."

This is the **session-level sensor** the substrate does not have yet.
`gradient.py` reads the speed *of an act* (respond/retune/author); `forest.py`
reads the status *of a work-item* (parked/stranded/merged); neither carries the
*session* axis — "is this session a reader or a writer, and when did it cross?"
It is also the natural seed of two named-not-built pieces already on the record:
the **runtime witness** (activity organ 2 — every firing a first-class receipt)
and **session-gateway**'s typed, registered, addressable sessions (this is their
*birth-mode*).

## Session identity already exists — locally (bdo, 2026-06-23)

bdo: *"the session record right now is local — you have locally-inspectable
Claude sessions on my PC; we can use those for now."* This dissolves what looked
like piece 1. We do **not** mint a session identity:

- Claude Code already gives every session a `session_id` and writes its
  transcript to `~/.claude/projects/<project>/<session_id>.jsonl` on the PC.
- `.claude/hooks/session_register.py` (a `SessionStart` hook, done-line 0135)
  already records every session — `session_id → {cwd, ts}` — into the local
  registry `~/.claude/ontum-sessions.json` (today consumed by `loop.watcher`'s
  continue-probe). `forest.py` already names "live sessions (`watcher.py` as a
  source)" as a planned source.

So **the local Claude sessions ARE the session record, for now** (local-first —
`loop/`'s standing law, no new store). The mode attaches to the existing
`session_id`. This is the right "for now": when sessions later need to be
registered/typed/addressable on the log (session-gateway), this primitive's
write-on records are already keyed to the same id and graduate cleanly.

### The consequence: a reader writes nothing

This makes *"when you read, you're good… for now"* literal. A read-only session
already has a local record (its transcript + the registry entry); it does **not**
need a `session_started` line on the append-only log just to announce it opened.
**Read mode = a known local session with no write-on on the ledger.** The ledger
only learns about a session at the moment it *crosses into writing*. One new log
shape, written once, only when a session actually writes — the cheapest possible
grain.

## The write-on is a narration of authorship, not a flag (bdo, 2026-06-23)

bdo: *"you name your justification for picking up the pen, the way you will
write; you narrate your authorship — like a monologue of context that can be
cold-read because it's warmly written and journalistic."*

This is what saves the habit from being a bureaucratic checkbox. A
`session_write_on` does not say "1" — it carries a short **warm, first-person
monologue** that a **cold reader** (a future mortal session, bdo, a judging
node) can pick up and immediately understand. It covers three beats — *not as
rigid form fields, as a narration that touches them*:

- **the justification for picking up the pen** — *why* I am crossing into write
  mode now; what I am about to author and to what end;
- **the way I will write** — *how* I intend to work: the manner, the scope I'm
  reaching for, the posture (careful / sweeping / a single surgical edit);
- **the authorship narration** — the monologue of context itself: enough warmly-
  told background that someone arriving cold knows who is writing, into what,
  and why, without having to reconstruct it.

It is **journalistic**: written warmly *so that* it reads true cold — the
warmth is not decoration, it is the property that carries the context across the
gap that kills sessions. This is the repo's standing cold-reader discipline (the
fence rule "written as a story for a cold reader"; the Taster's warm-serve, D-14)
applied to a session's own birth as a writer. The structured sibling already
exists for autonomous exploratory acts — `observe.gate()`'s DECLARE
(actor · action · receipt · scope · rollback); the write-on is its **warm,
prose, session-scale** counterpart: a monologue where `observe` is a form.

In an **emergency** the narration compresses — a one-line warmly-told lede
("hot-fixing the heartbeat routing, no time for the full monologue") rather than
nothing. You still say *why*; you just say it short. The habit bends to a quick
honest note; it does not vanish.

## The cut — and how the local model nearly draws it for us

The `SessionStart` hooks **already write**: the heartbeat ticks the loop
(`advanced=3` this very session), the `Stop` reflect beat writes, `git.py sync`
writes. So "every session starts read-only" looks incoherent on day one — *are
those the session writing?*

The local-session model resolves most of this **by construction**: mode is
defined by a `session_write_on` **keyed to this `session_id`**, and the ambient
hooks write their own records (`tick` by `heartbeat.v0`, the reflect beat, sync)
— *none* keyed to the session as a deliberate writer. So the heartbeat does not
flip the session out of read mode; the session simply has no write-on yet. The
remaining principle for bdo to confirm (CTA-1) is narrow: **a hook firing
around a session is never "the session writing" — only the session's own
deliberate hand (the pens, `Write`, `Edit`) writes a `session_write_on`.**

## Concept list

### Records (ONE new log shape — the truth)
- **`session_write_on`** — the named crossing, and the *only* new log shape;
  appended as the **first deliberate write** of the session, *ahead of* the
  mutation it precedes. Idempotent — write-twice is a no-op (the `node.py`
  write-once pattern). Carries `session_id` (the local Claude id), `ts`, the
  triggering act, an `emergency` flag (default false), and — the heart of it —
  the **`narration`**: the warm journalistic monologue (justification · the way
  I'll write · authorship context) described above. A read-only session writes
  no such record — and writes nothing else to the ledger either.
- *(No `session_started` log record.)* A session's existence is already on the
  PC (transcript + `ontum-sessions.json`); the ledger stays silent until the
  session writes. Read = known-local-session ∧ no write-on.

### Enforcement — the habit, reinforced (bdo, 2026-06-23)

bdo: *"'I'm writing now' needs to be a rather important habit — and if it's not
done you get told by the environment and go back and do it, unless you're in a
hurry and it's an emergency type thing."*

The write-on is **not** a passive record the loop politely appends for you — it
is a **habit the environment reinforces**. The guard does **not** silently
write it on your behalf; it makes *you* form the habit, and corrects you when
you skip it.

- A **`mode_guard`** `PreToolUse` sibling of `write_guard`/`freeze_guard`: when
  a session's first **deliberate work-write** (a pen / `Write` / `Edit`) arrives
  with **no `session_write_on` recorded for this `session_id`**, the guard
  **refuses it** — exit 2, with the message *"declare write-on first: record
  your crossing into write mode, then write."* You **go back**, record the
  write-on, and proceed. The habit is the point; the refusal is the teeth.
- Recording the write-on is itself an allowed, cheap log-append — it is the
  *declaration*, distinct from the work-write it precedes (so there is no
  chicken-and-egg: declaring is always permitted, the work-write is what's
  gated on the declaration existing).
- **Never gates the owner** (the guard law) and **fails open on its own
  errors** — a broken guard never traps a session. It corrects *sessions* (the
  deliberate hand), never bdo.

### The emergency escape — named, never silent

The reinforcement is **not** an absolute wall (it is not `freeze_guard`). bdo's
*"unless you're in a hurry and it's an emergency type thing"* is a first-class
escape — but a **recorded** one (absence is information; a bypass leaves a
trace):

- A session that is genuinely in a hurry declares the crossing with an
  **`emergency` flag** — the work-write proceeds, and a `session_write_on`
  marked `emergency: true` is recorded **alongside** it (order relaxed from
  *before* to *recorded*). The session is still on the record as a **writer**;
  only the strict before-ordering is waived, and the waiver is **visible** — a
  hurried crossing is never an invisible one.
- So the invariant *"every writer's crossing is on the ledger"* holds
  unconditionally; the emergency only relaxes *when* the line is written, never
  *whether* it is. A fold can later count emergency crossings — if the escape
  is being leaned on, that itself is a signal (the dead-valve / over-use shape).

### Fold (the read)
- **`loop/session.py`** (or a section of an existing sibling) — crosses the
  **local session set** (the `ontum-sessions.json` registry / the
  `~/.claude/projects` transcripts — reusing `watcher.load_registry`, not a
  second reader, I-4) against the `session_write_on` records on the log, and
  reports per-session **mode** (reader vs writer), the reader/writer census over
  a span, and the read→write crossing time. Sibling of
  `gradient`/`forest`/`census`: stdlib, deterministic, `--json`, a `done |
  report | needs-you` line. Read-only.

### Boundary / non-goals (what this is *not*)
- **Not a permission system.** Read mode is a *state*, not a *prohibition*. The
  crossing is *recorded*, not gated-against.
- **Not a second identity for hook actors.** `heartbeat.v0` et al. keep their
  own attribution; the mode is the deliberate actor's.
- **No double-build.** Not `gradient` (the act axis), not `forest` (the work
  axis), not the summon hook's existing read-only posture (D-10, the *hook*
  layer) — this is the read-only posture lifted to the **session** as a
  first-class actor.

## Red team: can a session write some other allowed way? (bdo, 2026-06-23)

bdo: *"Can anyone get around the rule by writing in some other way that is
allowed? Red-team it when you build it."* The honest answer up front: **yes —
trivially, if the guard only hooks the `Write`/`Edit` tools.** In this repo most
real writing does **not** go through the Write tool; it goes through **shell**.
A tool-layer guard walls the front door and leaves the garage open. The bypass
classes, and what actually closes each:

| # | Bypass (an "allowed" write) | Closed by |
|---|---|---|
| 1 | Shell file write — `echo > f`, `Set-Content`, `python -c "open(f,'w')"` | **Consequence-fence (L2).** The working-tree diff shows the change regardless of path; no write-on for this session → caught and shamed (`trespass_shame` sibling). Ground-truth, not an intent guess. |
| 2 | A pen via Bash — `pr.py land`, `node.py judge`, `loop.* admit` | **Chokepoint gate.** Every *ledger* write funnels through `reconcile.append_line`; it requires a write-on (or `emergency`) for the session before a work-append. The write-on itself is exempt (it's the declaration). |
| 3 | Direct log append — `python -c "append_line(...)"` | **Same chokepoint** — append_line is the one door (already true, I-2). |
| 4 | Subagent / child session (`CLAUDE_CODE_CHILD_SESSION` is set) | **Per-session rule + an open decision.** A child is its own `session_id` and declares its own write-on. But a parent that only *spawns writers* and never writes itself — is it a writer by proxy? **The sharpest open hole (CTA-7).** |
| 5 | MCP write tools | **Consequence-fence (L2).** If it changed the tree or the log, the diff catches it — no per-tool wrapper needed. (A purely *external* effect that touches neither tree nor log is out of this fence's territory — flag at build.) |
| 6 | A human editing in the IDE directly | **Out of scope** — the rule governs *sessions*, not bdo's own hand. |

**The architecture this forces — watch the CONSEQUENCE, not the paths (bdo,
2026-06-23).** bdo: *"It should look for the consequence of using the write
tools… otherwise we'd have to fence many paths. Maybe install a general fence
anyway."* Watching *paths* is action-space — unbounded and leaky, the exact trap
the consequence-policy model (#354) exists to escape; every new write path is a
new hole, and it leans on `tags.classify` (known-incomplete). Watching the
**consequence** — *did state actually change, with no write-on?* — is
**path-agnostic and bounded**: one territory, not N doors. Two layers:

- **L1 — prevent (cheap, narrow): the chokepoint gate.** `reconcile.append_line`
  — airtight for the **log**, the truth-critical surface. Composes `active_mode`'s
  existing per-session fold; no new posture engine. This one genuinely *prevents*
  an undeclared log write.
- **L2 — catch (path-agnostic, broad): the consequence-fence.** *One* observer
  over the **consequence territory** — the working tree + the log diff per turn
  (`git status --porcelain` + a log-tail delta, already sensed by the
  garden/forest). If state changed this turn and there is no write-on for this
  `session_id` → caught, **however** the write happened (Write tool, `echo >`, a
  pen, MCP, or a path no one anticipated). It is ground-truth, not an intent
  guess. This is the **general fence** bdo reaches for — and it is *more* bounded
  than per-path guards, not less. It composes `observe.gate()` directly: the
  write-on narration **is** the DECLARE, and the consequence-fence is `observe`'s
  "every effect must name its declaration," applied to state-change.

`command_guard`'s existing per-command watch stays as a **free early signal**
(it already runs), no longer the thing completeness depends on. The `trespass_
shame` pattern is reused for the social signal when the consequence-fence catches
an undeclared change.

**The honest tradeoff:** the consequence is detected *after* the change (a
Stop-hook diff), so L2 **catches-and-reconciles** rather than prevents — fine,
paired with L1 which prevents on the surface that most needs it. **The honest
non-goal:** short of walling shell itself (which breaks the repo) no layer makes
*every* write impossible *before* it happens; the consequence-fence makes every
write impossible to **hide**, which is the property that actually matters (a
writer is always on the record as a writer).

**"Red-team it when you build it"** is a build requirement, not a wish: the build
ships an **adversarial test per row** (the §10 discipline — if every write passed
on the first try the check isn't doing its job). Each test fires a bypass and
asserts it is **either gated** (append_line refuses) **or witnessed** (lands on
`tool-use.jsonl` and trips the shame fold). A write that is *neither* is a
failing test.

### Short read, limited — and the session knows (bdo, 2026-06-23)

bdo: *"make sure it's a short read and limited, and it knows."*

- **Short & limited.** The mode fold is **bounded** — scoped to *this*
  `session_id` and the recent tail, not a full-history scan on every hook (the
  `trespass_count` grain). Cheap enough to run on the hot path.
- **It knows.** The guard is **never a sprung trap.** The session is told its
  posture ambiently — a summon/hook line: *"you are in READ mode; declare
  write-on before your first write"* — so the habit is **known**, the carrot
  (briefing) paired with the stick (the gate). A session always knows it is a
  reader and exactly how to cross.

> Naming note (CTA-4): `mode` is **taken** — `reconcile.active_mode` already
> means the `normal`/`train` *security* posture. The read/write axis needs a
> distinct name (`write_posture` / `authorship` → `reader | writer`) so the two
> postures never collide.

## The fence is policy-driven, configurable, and smart (bdo, 2026-06-24)

bdo: *"Let's create the fence, but it only stops specific situations — the ones
under policy. The policy can be configured and is smart."* The fence is **not** a
blanket "every undeclared write is blocked." It splits into two motions:

- **Observe — broad.** The consequence-fence *witnesses* **every** state-change
  (the working-tree + log diff), cheaply, ground-truth. Witnessing is universal
  and never blocks.
- **Act — narrow, under policy.** The fence only **stops** (gates / escalates /
  forbids) a change when the **policy names that situation**. Everything the
  policy does not name is witnessed and waved through. So "observe everything,
  stop only what policy says" — the consequence-policy model (#354) exactly.

What the policy is, and the facets it needs:

1. **An admitted record — configurable, bdo's (the setpoints law).** The policy
   is drawn by bdo (`--by bdo`), withdrawable/superseding, never a code constant
   — the disposer-fence / inference-RBAC / `act_fence` draw-fence shape. **Default
   is permissive:** with no policy drawn, the fence *stops nothing* — it only
   witnesses. (A deliberate inversion of the inference gateway's deny-by-default:
   that gates *thought*; this gates *the owner's repo*, and bdo asked it to stop
   only specific situations.)
2. **The decision vocabulary is `act_fence`'s three tiers** — `forgiveness`
   (allow, witnessed) / `permission` (gate: require the write-on declaration,
   or escalate) / `forbidden` (stop hard). Compose `act_fence`, don't reinvent
   the tiering.
3. **"Smart" = inference-backed, bounded.** For a situation no static rule
   covers, the policy may ask the **inference gateway** (`loop/inference.py`,
   RBAC'd, receipted, concurrency-bounded) to judge "is this a stop-situation?"
   — and **degrades safe** to the static default (witness-only) when inference is
   unavailable. Smart, but governed: the dial bdo tunes is the policy, not each
   verdict.
4. **A typed *situation*, not prose.** What the policy matches on is the
   `observe.gate()` DECLARE shape — actor · posture (`reader|writer`) · scope
   (which paths) · what-changed · `emergency`. Typed so the policy is a
   reproducible classifier, not a vibe.
5. **The fence's own decisions are receipted.** Every stop/allow/escalate is a
   log fact (auditable; a consequence-graph node) and the fence is a declared
   collector in `.claude/activity-register.json` (the activity-accounting law —
   no silent collector).
6. **A stop is never a dead-end — the session knows the one move.** When the
   policy stops a change, the session is told the reconcile path (declare the
   write-on / escalate / back out), carrot paired with stick.
7. **Home: extend `fence/` (the family-neutral registry), don't fork it.** Today
   its rules are argv-prefix shaped; the consequence/situation rule is a new
   *kind* under the same registry, so one fence concept renders to both Claude
   and Codex (the parity law), never two drifting lists.

## Spec: who · how · when · field · watchers · docs (bdo's six, 2026-06-23)

- **Who writes it.** The **writing session, by its own deliberate hand** — never
  a hook, never the loop. It is a narration of *its* authorship, so it must be
  *its* voice; the `by` on the record is the session. (A hook that wrote it for
  you would defeat the habit — the whole point is the session forms it.)

- **How.** Through **one pen** (I-2, one write path): a CLI verb
  `python -m loop.session write-on --narration "<warm monologue>" [--emergency]`
  that appends the record via `reconcile.append_line` (line-atomic, torn-tail
  tolerant). The pen resolves the writer's id from **`CLAUDE_CODE_SESSION_ID`**
  (confirmed present in-process this session) — no `--session-id` to forget, no
  registry ambiguity. There is deliberately no second write path.

- **When.** At the **crossing** — the deliberate first act *before* the
  session's first work-write. The `mode_guard` enforces the order: a first
  work-write with no write-on for this `session_id` is refused, you go back and
  declare. In **emergency**, recorded *alongside* the write (order relaxed, flag
  set).

- **The field description (the schema).** One record:
  - `type`: `"session_write_on"`
  - `session_id`: the local Claude id (from `CLAUDE_CODE_SESSION_ID`)
  - `by`: the author (the session / node id) — provenance
  - `ts`: timestamp
  - `narration`: **the warm journalistic monologue** — justification · the way
    I'll write · authorship context (the heart; free prose, CTA-5)
  - `emergency`: bool, default `false` (CTA-6)
  - `triggering_act`: optional — the write it preceded (file / atom / pen)
  - Lives in **`events.jsonl`** — it is a thing that *happened* (a session
    crossed), not a governance admission. *(File placement: confirm under
    CTA-4.)*

- **What can watch it.** It is a plain log fact, so every fold can:
  - **`loop/session.py`** — the primary reader: per-session mode, reader/writer
    census, crossing time;
  - **`mode_guard`** — watches for its *absence* before a work-write (the teeth);
  - **`forest.py`** — already plans "live sessions as a source"; write-on tells
    it which sessions are *writers*, to decorate the forest;
  - **`gradient.py`** — can band the crossing on the session axis (an authored
    act); **`digest`/`summon`** — surface the census and the emergency-use rate;
  - the **runtime witness** (activity organ 2) — write-on is a natural
    first-class witnessed firing.

- **Where it is documented.** Now: this proposal. When built: the
  **`loop/session.py` docstring** (canonical, the `gradient.py` pattern) + a
  **`loop/CLAUDE.md`** module-layering entry and the record kind in its
  architecture section; **`.claude/CLAUDE.md`** for the `mode_guard` hook wiring;
  **`.claude/activity-register.json`** if the guard collects data (the
  activity-accounting law — no undeclared collector); and the **doctrine** *iff*
  bdo elevates "read by default" to a session-posture invariant (his call — it
  is plausibly a D-number).

## Design locked — bdo delegated the mechanism to Claude (2026-06-24)

bdo: *"you design the fence, I think — you're the one who can jump it, lol."* The
mechanism is mine to design; the integrity comes from **adversarial self-design**
(every jump I know becomes a closed hole or a NAMED gap, never hidden), an
**independent reviewer**, and **bdo's policy stamp**. I author the lock; I do not
hold its key — the policy dial and the last stop stay his (D-4, two gates).

Decisions taken as designer:

- **Naming / placement (CTA-4):** the axis is `write_posture` (`reader | writer`,
  not `mode` — taken by `active_mode`); the record is `session_write_on` in
  `events.jsonl`.
- **Build order (CTA-2):** **increment 1 = the witness** — the record + the
  `loop.session write-on` pen + the `loop/session.py` fold. It **stops nothing
  and breaks nothing** (witness before actuator). **Increment 2 = the fence** —
  the L1 `append_line` chokepoint + the L2 consequence-fence under policy, with
  the full bypass red-team suite.
- **First policy situation:** shipped as a **recommended copy-paste default** —
  *undeclared write to a governed surface (log / atoms / done-lines)* — which
  **bdo draws** (the policy content is his stamp; the mechanism only accepts it).
- **Proxy-write (CTA-7):** a parent that spawns writers declares a proxy
  write-on; built in increment 2.

Open for bdo (policy, never mechanism): whether to draw the recommended starting
policy, and whether to fence the emergency-use rate once it has live instances.

## Calls to action (against the purpose: a session's mode is a folded fact)

- **CTA-1 — the cut (bdo).** Confirm that "the session's hand" *excludes*
  ambient hook beats: only the session's own deliberate write emits a
  `session_write_on`; a hook firing around it never does. *(Rec: yes — the
  local-session model already enforces this by keying on `session_id`.)*
- **CTA-2 — build order.** Smallest real piece first = **the one record +
  the pen + the fold** (witness before actuator). Enforcement is **two-layer**,
  consequence-first (not per-path): **L1** the `append_line` **chokepoint gate**
  (prevents undeclared log writes) + **L2** the **consequence-fence** (one
  observer over the working-tree + log diff per turn — catches any undeclared
  state-change, path-agnostic, composing `observe.gate()`). Each ships with its
  adversarial red-team test. *(Rec: yes — record/fold first so the fence has a
  true write-on to check against; `heal` before any actuator.)*
- **CTA-3 — home.** Live as its **own small proposal** that `session-gateway`
  cites (it is the *birth-mode* of a registered session), rather than buried in
  the gateway. *(Rec: yes — it is sharp and independently landable.)*
- **CTA-4 — vocabulary.** One record kind `session_write_on` (no
  `session_started`). The axis is **not** `mode` (taken by `active_mode`'s
  security posture) — `write_posture` / `authorship`, values `reader | writer`.
  Confirm the names and the `events` vs `admissions` file placement.
- **CTA-5 — the narration's shape.** A **free warm monologue that touches**
  the three beats (justification · the way I'll write · authorship context),
  *not* three rigid form fields. The guard checks the write-on **exists**; the
  prose's quality is a cold-reader's judgment, never machine-gated. *(Rec: free
  monologue — a form would kill the warmth that is the whole point.)*
- **CTA-6 — the emergency escape.** An explicit, **recorded** `emergency` flag
  that relaxes ordering (write proceeds, write-on recorded alongside) but never
  whether the crossing is logged; a fold counts emergency crossings so leaning
  on it is visible. *(Rec: yes — named-and-recorded, never silent. Open: should
  the rate of emergency use be fenced/surfaced once it has live instances?)*
- **CTA-7 — the subagent/proxy hole (the sharpest).** A child session
  (`CLAUDE_CODE_CHILD_SESSION`) writes under its own id and declares its own
  write-on — but is a **parent that only spawns writers** a writer by proxy?
  *(Rec: spawning-to-write is itself a deliberate write — the parent declares a
  write-on naming the proxy; otherwise a session launders all its writing through
  children and reads "reader" forever. Confirm.)*

## Why it earns a place (not ceremony)

The substrate's whole posture is "the log is truth; sessions are mortal; the
files stay." Today a mortal session's *most basic posture* — was it a reader or
a writer? — leaves **no trace at all**. This primitive makes that posture a
recorded fact at the cheapest possible grain (one line, only when a session
actually crosses), and it is the first foothold for the session-gateway and the
runtime witness that several arcs already depend on.
