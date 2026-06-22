# Graded speed — the meta-level of an act, read as one gradient (PROPOSED)

> **Status: PROPOSED** — bdo's direction, 2026-06-21 (this session), his to
> steer. A **reframe-and-wire** blueprint, not a new organ: three of its bands
> already exist in code; the build is *naming the dimension*, *reconciling one
> vocabulary collision*, and *wiring the one disconnected band onto the shared
> ledger*. Grounded file-by-file by the `graded-speed-foundation` workflow
> (6 subagents); every claim below cites disk. It **composes** existing organs
> and the §14/D-12 frame — it does not re-derive them (§10).

## The direction, in bdo's words

> *"A slow-meta-administrator … oversees slow-meta-operators … who design
> meta-architecture … traced and ingressable by a fast-norm-administrator all
> down the line. A shared ledger and a process over it. The ledger is a pointer
> to register authors and surfaces. Slow = creating the loop. Fast = using the
> loop, responding to pressures. … Why? Multiple speeds. The fast/slow can do
> medium speed, aka update config, and try to get fast and more efficient. A
> gradient, not binary: the thresholds are binary, the state is graded."*

## What this is

**Speed = the meta-level of a record on the shared ledger** — how deep into the
machine an act reaches. Not latency; *altitude*. The doctrine already has the
binary (§14, D-12, [`ai-native-loop-substrate.md`](../../ai-native-loop-substrate.md)):
*the fast loop holds the setpoint each pass; the slow loop moves the setpoint
itself.* bdo's request **extends that binary into a three-band gradient** and
asks that the whole stack be **traced and ingressable all down the line**.

| band (act-verb) | speed | reach | binary threshold (crossed when the record…) | already in code |
|---|---|---|---|---|
| **respond** | fast | exercises the pipeline | advances atom **state**; reads dials, writes none | [`orchestrate.py`](../../loop/orchestrate.py) — tick → sense pressure → budget → `pass_once` |
| **retune** | medium | moves a dial | writes a **setpoint/fence** the loop reads next pass | [`slowloop.py`](../../loop/slowloop.py) proposes · [`disposer.py`](../../loop/disposer.py) disposes in-fence |
| **author** | slow | adds a capability | adds/alters **machinery** read at runtime (a workflow, a real node, a surface, an author) | the workflow wrapper + `node_real` / `reflect` / `herald` |

**State graded, thresholds binary — already literally true in code:** continuous
`cool_ratio`/`pressure`/`prop` measured against binary bands (`slowloop.py:127,134`;
the cap `orchestrate.py:208`; the fence `disposer.py:150-161`). And **the
fast↔medium bands already slide, bidirectionally:** `orchestrate` writes tick
records → `slowloop` folds them (`:61`) → proposes → `disposer.evaluate` against
bdo's standing fence → `admit_setpoint` (`:189`) → `orchestrate` reads the new
dial next tick (`:285`). That is the gradient, live.

## What already exists (compose — do not rebuild, §10)

- **Shared ledger + process:** `reconcile.py:129` (`Fold`) over the three JSONL;
  `PIPELINE` (`:33`) + `pass_once` (`:436`).
- **Register authors / surfaces** — bdo's "the ledger is a pointer to register
  authors and surfaces" *is* the author band's registry: `herald.py:82`
  (`introduce`) for authors; `reflect.py:82` (`admit_surface`) for surfaces.
- **The meta-hierarchy** (admin→operators→workers) already has a home and a
  worked answer: Owner→Administrator→Conductor→Agent, bridges-as-**creases**,
  staff-as-**sensor-folds**, *not* a staffed org chart (D-10) —
  [`authoring-platform.proposal.md`](authoring-platform.proposal.md) §107-132.

## What is genuinely NEW (the only build)

1. **A read-only fold that names speed as one graded dimension** — `loop/gradient.py`,
   in the `gaps`/`census`/`heal` grain (stdlib, propose-only, evidence is a log
   record or `file:line`, the cut stays bdo's). It reads each record into a band,
   reports the profile, and is the single place the *fast-norm-administrator
   ingresses every band "all down the line."* It writes nothing.
2. **Wiring the `author` band onto the ledger.** Today it is a **disconnected
   island**: `lint.py`/the workflow wrapper never import the log, write no
   tick/admission, and nothing lets fast/medium *request* new machinery. That is
   the concrete gap behind "traced all down the line," and it is the fold's §10
   tooth: **`untraced-band-crossing`** — a machinery artifact (a workflow today;
   real nodes and surfaces as the band grows) with no current-bytes admission on
   the log is flagged. Non-vacuous test (heal-grade): an un-armed workflow is
   flagged; a correctly-armed one is not; editing the armed bytes flags it again.

## Built this session (the slow band, made concrete)

[`.claude/workflows/draft-capability.js`](../../.claude/workflows/draft-capability.js)
— a **slow-band workflow whose subagents draft fast-band machinery** (exactly
bdo's "workflows that author skills and workflows for fast agents"). From a
plain-language capability description it frames the shape, fans out to draft a
launchable workflow + companion skill, and routes the draft through the
**existing** A2 check (`author-workflow/lint.py`) rather than re-inventing
validation. Read-only on the repo (validates on a temp file outside the tree);
proposes drafts only — never arms or runs (A3/A4 gates). Verified passing its
own A2 check (`ok: true`, `fit.ok: true`).

## Calls to action — yours to stamp

- **CTA-1 (do this first):** **Reconcile the name collision.** Your *MEDIUM*
  (retune config) **is** the doctrine's *"slow loop"* (§14). Pick the vocabulary
  before any organ build, or two speed dimensions drift. *Recommended:* name
  bands by act-verb (**respond / retune / author**) and carry fast/medium/slow
  only as the gradient label — it sidesteps the collision entirely.
- **CTA-2:** **Graduate `epic.graded-speed`** (a reframe-and-wire arc) with
  `loop/gradient.py` as its first piece. Note: the workflow wrapper rides its own
  *unstamped* `epic.workflow-authoring` (no epic file on disk) — not
  `epic.repoprompt-parity`, as I'd misremembered. Decide whether graded-speed
  adopts the wrapper as its author-band machinery or leaves it a separate arc.
- **CTA-3:** **Set the ingress tiers.** Who may slide an act SLOW↔FAST, and the
  fast-norm-administrator's ingress scope. This is the authority dial named in
  the authoring-platform proposal — same dial, not a new one.

## Attribution carries attributes (bdo, 2026-06-21)

A correction to fold in: governance is *authenticated · authorized · attributed*,
but **"attributed" is not a binary owner-stamp — it is attribution, the attaching
of a typed attribute-set, and the attributes are the substance.** ontum already
*reads* attributes (each fold consumes one) but does not *mint* them at one seam:
actor+credential (herald), **band** (the gradient fold), arc (digest), caller·
surface·mind (inference gateway), tool-scope (`policy_scope`), consequence
(consequence-graph), cost (the accounting/RGB organ), prompt_hash·parent (§7
receipts). They are born in eight places or not at all, so no act carries the
full set and "who" degrades to a self-asserted `--by`.

**The session record (the runtime-witness, `activity.py` part 2) is therefore the
attribute-bearing root, not a provenance stamp:** a typed record from which every
act *inherits* the session's attributes (band, credential, arc) and *adds* its own
(surface, mind, consequence, cost) — attribution = inheritance-plus-accumulation
down the act tree. This is the "traced all down the line" requirement made
operational: attributes propagate down, so an administrator can ingress at any
node and read the **full attribute stack**. The attributes are also the
*primaries* the accounting/RGB organ infers over (an act is a *mix*, not a box).
**Build implication:** the missing piece is the **attribute schema minted at the
gateway and inherited down every act**, feeding the gradient / consequence-graph /
herald / RGB organ from one source — not a "log who logged in" line.

## The two axes (resolved by bdo, 2026-06-21)

The riskiest assumption was that **speed** and the **hierarchy** were one axis.
bdo resolved it: *"there are fast and slow workers too."* Speed crosses **every**
tier — so they are **two orthogonal dials**, a **role × speed matrix**:

| | **fast / `norm`** (respond — use loop) | **slow / `meta`** (author — create loop) |
|---|---|---|
| **administrator** | ingress + oversee live work | oversee the loop-building |
| **operator** | run a unit, respond to pressure | shape a unit's machinery |
| **worker** | do the work | design meta-architecture |

**The decoder for bdo's vocabulary:** `meta-` = the **slow** band (creating the
loop); `norm-` = the **fast** band (using it). So `slow-meta-administrator` and
`fast-norm-administrator` are the same *role* at opposite ends of the *speed*
axis, and a worker exists in both bands. `retune` (medium) is the graded middle
any role can drop into. **The epic needs two dials, not one** — a speed dial
(respond/retune/author) and an oversight dial (the authoring-platform tier
model). `loop/gradient.py` reads the speed axis; the tier model carries the
oversight axis; they compose, they do not fuse.

## What trying to RUN it surfaced (bdo, 2026-06-21: "it's there but not running")

Placing the workflow and then launching it exposed two real holes — the author
band is genuinely not yet wired to run:

1. **No run rail (A4).** `Workflow({name: 'draft-capability'})` does **not**
   resolve — `.claude/workflows/` is the wrapper's *aspirational* home, but
   nothing registers it as a launch source. The workflow runs only via its raw
   file path (the un-paved path A4 is meant to replace). "There but not running"
   is the missing run rail, exactly.
2. **The A2 check is not faithful to the runtime (a §10 misfit).** `lint.py`
   passed a `meta.description` built with string concatenation (`'…' + '…'`);
   the real Workflow runtime **refuses** it (`meta must be a pure literal`). The
   gate and the thing it guards disagree — two locally-fine things refusing to
   fit. **Fix:** `lint.py` must reject any non-literal node in `meta` (the
   runtime's actual rule), with a non-vacuous test (a `+`-concatenated meta is
   refused). This is a teeth-sharpening on the existing A2 check, not a new
   organ.
