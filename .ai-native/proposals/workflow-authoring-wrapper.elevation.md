# Elevating the workflow wrapper from the pens' hard-won lessons

> Companion to [`workflow-authoring-wrapper.proposal.md`](workflow-authoring-wrapper.proposal.md).
> The account of a five-agent lesson-mining pass (bdo's directive, 2026-06-21:
> *"learn from the many mistakes and ideas the Pens have, so the greenfield…
> elevates from our many learned lessons and memories"*). Each row cites where
> the lesson was paid for. **Status of each: ✅ applied · ◐ CTA (named, not yet
> built) · ⊘ bdo's dial.**

## The headline correction (doctrine-miner)

`lint.py` clears the **easy bar** (a single workflow validates) but failed the
**§10 bar**: *can two locally-fine workflows refuse to fit, and does the gate
notice?* As shipped, no — `lint(path)` read one file and never a sibling, so it
was a per-file **cell check** named like a gate. The real cross-file seam is
**workflow composition**: a workflow may invoke another by name
(`workflow('slug')`), and a locally-fine workflow that references a **missing or
malformed sibling** is the misfit the gate must catch. ✅ **Applied** — a `fit`
check now resolves every `workflow(...)` reference against the directory and
refuses a dangling one, with a non-vacuous test (`tests/test_workflow_fit.py`):
two valid files where A→B pass; A→(absent B) is refused.

## Record-correctness bugs the records-miner pinned in `arm` (all cited)

| Lesson | Paid for at | Status |
|---|---|---|
| `now_ts()` in the arm id breaks I-2 idempotence — re-arming the same bytes litters a duplicate. Key on `(ARMED, slug, version_hash, by)`, clock in payload. | `make_receipt` has no ts (`reconcile.py`); I-2 | ✅ applied |
| `version_hash` used `read_text` (universal-newline translation) ≠ the repo's canonical `read_bytes` identity — the 0007 CRLF trap reborn; `.js` wasn't `-text`-pinned. | done-line 0007, `.gitattributes`, `reconcile.py` atom id | ✅ applied (raw bytes + `.gitattributes` pin) |
| `armings()` hand-rolled a JSONL reader — a **second read path** that drifts from the canonical fold. | I-4; `reconcile.read_jsonl` | ✅ applied (folds through `read_jsonl`) |
| No **disarm / withdrawal** path — a workflow armed then found dangerous (no byte edit) couldn't be un-armed except by editing the file. | `arc_confirmation`'s `enabled:false` supersession | ✅ applied (`disarm`, superseding, latest-wins) |
| Actuator failed **open or by traceback** when the check was unreachable, instead of **closed-but-named**. | guard-miner: "an unguarded repo that still looks guarded" | ✅ applied (named refusal if the check can't load) |

## The teeth still missing — CTAs, in priority order

1. ◐ **Author ≠ armer (D-2 self-dealing).** `arm` records any `--by`; a session
   can author *and* arm its own draft. Named by **four** miners (PR #6, guard #3,
   doctrine #2, memory #7). Needs authoring to record who drafted (no author
   record exists today). Then `arm` refuses `by == author` and records the
   non-author attestation (mirror `pr.py land --attest-non-author`).
2. ◐ **The prompt-parity hole / off-log run.** Arming is **unenforced ceremony**
   until (a) a `fence/policy.py` rule with `decision:"forbidden"` (never
   `prompt` — the silent-no-op-on-Claude hole that #412 closed for `gh issue`)
   forces launches through the rail, and (b) **A4** is the only sanctioned launch
   path and leaves a `workflow_run` receipt + an audit fold (the `pr_audit`
   analogue) that flags any run with no preceding arm. *This is why A4 matters:
   without it the arm gate guards nothing.*
3. ◐ **Mutation must gate, not just flag — and the flag is a soft tooth.** The
   prose-verb regex can be evaded; and a `mutates` workflow lacking per-agent
   `isolation:'worktree'` is currently locally-fine. Fix: **read-only must be
   earned** (ambiguous → `mutates`), refuse an unscoped mutator (the no-sweep
   lesson), and scan the primitive outside comments/strings (reuse
   `_strip_strings`).
4. ◐ **Spawn-rail bypass.** A run's `agent()` calls spawn outside the branded
   `ontum-node:<id>` rail (no §7 prompt hash, no trust rung). A4 must route
   sub-agents through the rail — or declare the exception on the record (absence
   is information).
5. ◐ **Account every run + stale-arm healing.** Every run writes a first-class
   receipt (activity-accounting / runtime-witness shape); `status` distinguishes
   "never armed" from "armed-then-edited" (the heal version-split).

## The one dial that is bdo's (⊘ — not a session's to set)

**Risk-tiered arming by consequence class.** The arm act is a *typed gesture
that licenses a consequence* (the gesture/consequence-policy model). Typedness
should scale with blast radius: a **read-only** workflow may be armed by an
independent node; a **mutating / high-blast** one should require **bdo's stamp**.
That tiering is the authority dial named in the platform proposal — D-4 makes the
thresholds bdo's. Per *Apple-not-IKEA*, the wrapper will ship **default-safe
tiers + an owner's manual** (the one gesture to change each), not a cold
question — but the defaults are proposed to bdo, his to retune.

## The two-birds alignment with `epic.repoprompt-parity` (bdo, 2026-06-21)

Read the confirmed arc, not memory: `epic.repoprompt-parity`'s value is *"a
finished, AI-driven boundedness organ for AI workflows… the topology of parallel
AI work can be configured and controlled… bounded runs train the surface that
governs the next run."* **Workflows are the topology of parallel AI work; this
wrapper bounds them.** So the wrapper is not a separate epic to graduate — it is
a **build under the confirmed arc**. Two birds:

1. ✅ **No redundant epic.** Home the wrapper's pieces under
   `epic.repoprompt-parity` instead of graduating `epic.workflow-authoring`.
   bdo already confirmed that arc, so the wrapper's remaining teeth (A4 + the
   fence rule + the risk dial) inherit its authorization — he sees refusals and
   completion, not a fresh stamp. This *is* the `dont-double-build` discipline
   `parity.py` enforces, applied to ourselves.
2. ✅ **A new parity-matrix row, with teeth.** The wrapper's authored→reviewed→
   byte-armed gate is a real boundedness technique the wave-1 matrix doesn't yet
   carry. It becomes a tracked row (a `build` atom now, a `have`-with-evidence
   once A4 lands), advancing `atom.boundedness-parity-matrix`. It sits under /
   beneath `atom.topology-control-surface.v0` — the wrapper is *how a workflow is
   bounded before the canvas renders its braid*.

### ⚠️ The sharp catch — the alignment CORRECTS the wrapper's design

The arc carries an explicit **§10 fence on the whole arc**: *"review here is PULL,
never PUSH… ontum makes [bdo] the last stop who CAN look, never the curator who
MUST. Any piece that would make a human review context before a handoff is out of
bounds by construction."* That is **precisely the operator seat bdo left**
(`epic.owner-harness`).

My wrapper's A3 makes **arm-before-every-run a blanket requirement** — that is
PUSH, and under this arc's constitution it is **out of bounds**. The fix is not
to drop the gate; it is the **risk-tiered dial**, which is the PULL form:
*read-only / reversible runs are bounded-by-default and run without a human arm
(glance-able on pull); only irreversible / high-blast runs require an arm or
escalate to bdo.* So the dial I flagged as "nice to have" is, under the confirmed
arc, **required** — the arc forbids the blanket-arm stance I built. This is two
locally-fine things refusing to fit (the wrapper's gate vs. the arc's PULL fence),
and noticing it is the win.

### The throughline that decides it — not a cold choice to hand bdo

There is already a **throughline** for "how much must the owner be in the loop":
**bounded standing authorization** — *the owner draws the bound once; the system
acts within it and escalates only at the edge.* It is landed, not hypothetical:

- **The disposer's `auto_admit_fence`** (done-line 0091): bdo draws per-dial
  bounds *once*; the loop self-admits an in-fence change citing the fence as
  `authorized_by`, and escalates an out-of-fence one. The loop executes the
  stamp, never signs its own line.
- **D-4 at arc scale** (done-line 0028): bdo confirmed `epic.repoprompt-parity`;
  the loop carries its pieces and escalates only refusals/completion.
- (`atom.act-fence.v0` — parked — was the same pattern aimed at *acts*; named,
  not yet landed.)

So the run-gate is **not a per-run question** and **not a new dial to invent**
(§10 don't-double-build): it is the disposer's fence shape applied to workflow
runs. Per *Apple-not-IKEA*, the wrapper **ships default-safe tiers** and gives
bdo the one redraw-the-fence gesture — D-4 preserved via a documented knob, never
a cold choice. The **default fence I am setting** (his to redraw):

| Consequence tier | Default authorization | Escalates? |
|---|---|---|
| **read-only** (reversible; worst case wasted tokens) | runs **bounded-by-default**, no arm — glance-able on pull | no (FYI on the record) |
| **mutates, worktree-isolated** (reversible — work preserved on a branch) | an **independent node** may arm (D-2) | no, unless out of fence |
| **mutates, un-isolated / high-blast / irreversible** | **bdo's stamp** (escalate) | yes |

This *is* the arc's PULL-not-PUSH fence, made operational by the existing
bounded-standing-authorization machinery — one throughline, not a fresh fork.

## The other throughlines this rides (compose, don't double-build — §10)

The authority dial is one throughline. Reading the arc surfaced more — and the
first reframes the wrapper from a *gate* into a *learning surface*:

1. **Bounded runs train the surface that governs the next run** (the arc's deep
   nature; `atom.meta-exemplar-layer.v0`). A workflow run is **not terminal** —
   it is an **exemplar**: the run + its gate decisions + whether it stayed in
   bounds + the rule that broke it. This reframes **A5** from *"receipt the run"*
   to *"the run is an exemplar the next arm/authoring decision learns from."* The
   run receipt is training data, not just an audit line. Building A5 as plain
   accounting would have missed the arc's whole point.
2. **What each agent ingests is a budgeted fold** (`atom.context-fold.v0` +
   `atom.context-budget-dial.v0`) — not the raw prose the author typed. The
   wrapper *composes* the context-fold; it doesn't re-roll context assembly.
3. **The run handoff is replayable** (`atom.context-hash.v0`): a run receipt
   carries a `context_hash`, so a run can be re-derived from the log and a hidden
   non-log input is caught — the same teeth as the wrapper's byte-bound arm.
4. **The workflow renders as a typed braid with knots** (`atom.topology-control-
   surface.v0`): the wrapper is the *authoring* side of that canvas surface — a
   knot is a dependency a strand can't cross until it resolves. Same object,
   not a second canvas.
5. **The run's sub-agents ride the branded spawn rail** (§7 / D-10): each
   `agent()` a run spawns goes through `ontum-node:<id>` (pinned prompt, trust
   rung), or the wrapper declares the exception on the record — never an
   ungoverned spawn one layer down.
6. **The run is a witnessed collector** (`loop/activity.py`): a run spawns agents
   and collects outputs, so it declares its data-practice and is witnessed — it
   cannot be a silent collector outside the accounting the harness enforces.

The shape: the wrapper is **one piece in `epic.repoprompt-parity`'s mesh** — it
*cites and composes* the arc's other pieces (context-fold, context-hash,
topology-surface, meta-exemplar) rather than rebuilding any. That is the
`dont-double-build` discipline the arc is itself organized around.

## What the wrapper already got right (don't regress)

Content-hash byte-binding (edit un-arms) · one shared definition imported, not
copied (`review` imports `lint`; A4 must import `is_armed`) · risk read from
structure not prose · torn-tail tolerance · log-is-one-topic (no sidecar truth)
· refusals that name the paved path. *(PR #3, guard #4–8, records #2/#7/#10.)*
