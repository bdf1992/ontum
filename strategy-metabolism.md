# Strategy Metabolism — lawful pre-evidence motion

> **Status: PROPOSED** — captured from bdo's carry-over brief, 2026-06-20.
> Extends [explore-lobe.proposal.md](explore-lobe.proposal.md) (the design
> conversation that found the organ) and **supersedes its scope**: the
> explore lobe does **not** land alone. It is one quadrant of a four-organ
> metabolism. This note resolves nothing bdo lists as open (decisions A–D,
> §11); it adopts his recommendations as working defaults, marked.

## 1. The missing capability

Ontum has a strong **convergent / exploit lobe**. It can gate, fold, stamp,
classify, summarize, land, detect maintenance gaps, and enforce *no
evidence, no mint*. What it lacks is a lawful place for **pre-evidence
motion**. Not truth generation, not prediction, not capitalization:

> Given a purpose and a directional goal, read priors while **preserving
> uncertainty**, then emit **one marked, reversible call to action** that
> moves the system forward without pretending the future is closed.

That is the **Scout** function. Capital is the future banked — the most
aggressive uncertainty-terminator there is, one point of one axis. The
payout here is **motion**: the draw that never spends the principal.

## 2. The metabolism — four organs

| Loop (4X)  | Ontum-native | Function                | Ontum shape                                          |
|------------|--------------|-------------------------|------------------------------------------------------|
| Explore    | **Scout**    | find live possibility   | read priors, hold uncertainty, emit a conjectural CTA |
| Expand     | **Claim**    | bound territory         | turn a CTA into an arc / epic / spike / branch / watch |
| Exploit    | **Build**    | convert into capability | build, gate, stamp, fold, land (the existing loop)   |
| Extinguish | **Prune**    | retire dead futures     | expire stale conjecture, close branches, archive noise |

**The blind spot the conversation found:** exploration creates an immediate
need for claiming and pruning. Scout without Claim and Prune is beautiful
overgrowth — unmanaged possibility that consumes field-space. So the
priority is **not** "build the Scout lobe." It is: land a small metabolism
where Scout emits one CTA, Claim can bound it, Build can route it, and Prune
can retire it.

## 3. What this is NOT

Not a persona. Not a second source of truth. Not a rumor mill. Not an
autonomous planner that lands its own decisions. Not research notes. Not a
way to mint weak terms or bypass gates. Every Scout output stays marked:

```
status: conjecture
review_required: true
minted: false
truth_claim: false
```

The loop may **develop and requisition review**. It must **never
self-land**. Landing stays with the merge-node and bdo's confirm-arc (D-4).

## 4. Scout vs `gaps.py` — the bright line

`loop/gaps.py` / `loop/summon` emit calls to action from the **certain
present**: a mock stage exists, an atom is parked, a gate failed, a handoff
is incomplete. That is the **maintenance backlog**.

Scout emits calls to action from **priors + direction**: an opportunity
appears, a pattern suggests a possible next organ, the field's conditions
changed, prior work implies a frontier worth probing. That is the
**opportunity frontier**.

```
same output shape:  one move worth making
different source:   gaps = certain present  ·  Scout = uncertain frontier
```

A human must be able to tell at a glance which is which. Scout never
pollutes gap truth.

## 5. The signal chain

Ambient reporting agents and novelty/breaking-news detectors are **not** the
Scout lobe — they are **sensors** ("what changed in the field?" / "what
appeared that may matter?"). Scout **consumes** their signals and answers a
different question: *given our purpose, goal, and priors, what one move is
worth making now?*

```
ambient reporters / novelty agents
  → field changes
    → Scout            (one conjectural CTA)
      → Claim          (bound it: arc / spike / watch / defer)
        → Build        (the existing exploit loop: gate → stamp → land)
          → Prune       (retire what expired, duplicated, or was never ours)
```

## 6. The ScoutCTA schema — the frozen-candidate output

Scout emits **exactly one** CTA. No brainstorms, no many-option lists, no
generic "consider doing X." Strict shape:

```yaml
status: conjecture          # always
lobe: scout
purpose:                    # handed (v1) — the arc/epic/owner gives it
goal:                       # the directional goal
horizon:                    # what "done" would look like at goal scale
priors_consulted:           # the real records read (each resolves on disk)
uncertainty_held:           # what is deliberately NOT collapsed
why_this_move_now:
cta:                        # the one move worth making
cost:                       # priced motion (see §9) — mandatory
risk:
reversibility:              # how cheaply undone — mandatory
review_required: true       # always
expiry:                     # MANDATORY — a conjecture must decay
truth_claim: false          # always
minted: false               # always
```

**Expiry is mandatory.** A conjecture with no decay becomes a *ghost
obligation* — open possibility that never closes. The load-bearing fields
are `cta`, `priors_consulted`, `uncertainty_held`, `cost`, `reversibility`,
`expiry`. The teeth (§10), reused from causality with no second truth: every
entry in `priors_consulted` must be a `file:line` / log-record substring
that `term_economy.resolve_evidence` confirms is committed — a CTA whose
priors do not resolve is **refused as ungrounded** (the ghost refusal). A
fabricated/constant emitter cannot pass.

## 7. Claim organ (required adjacent)

Claim converts a conjectural CTA into bounded work. It does **not** prove the
CTA — it only says *this frontier is now bounded enough to work or watch.*

```yaml
status: claimed_frontier
source_cta:
claim_type: arc | epic | spike | branch | watch | defer
owner:
guard_policy:
budget:
review_date:
exit_condition:
expiry:
```

Claim is the missing bridge between possibility and execution.

## 8. Prune organ (required adjacent)

Prune is **not** a gate. A gate judges something trying to *land*; Prune
judges open *possibility* consuming field-space — "this conjecture expired /
was noise / duplicated another branch / is real but not ours / was useful
but is now spent / should be archived, not pursued."

```yaml
status: pruned
target:
reason:
evidence_or_basis:
effect:
reopen_condition:
```

Without Prune, Scout creates unmanaged growth.

## 9. Resource model — pricing motion

The strategy layer must **price motion**, or Scout always generates more
work. Resources it spends: attention, human review bandwidth, operator time,
repo churn, context window, token cost, trust, authority, latency, semantic
clutter, risk. Every Scout CTA carries a `cost` and an `attention_class`
(e.g. `"one review pass + one small branch + one §10 test"`, `small`). This
keeps exploration from becoming ambient debt.

## 10. The landable sequence — smallest useful metabolism

Develop-and-requisition-review only; never self-land (D-4).

1. **`strategy-metabolism.md`** — this note (P1). Names the metabolism,
   distinguishes maintenance from frontier CTAs, states Scout outputs are
   conjectural/review-required/expiring/non-minted, names Claim and Prune as
   required.
2. **Freeze the first ScoutCTA done-line** (P2) — input contract, output
   schema (§6), one example fixture, failure cases, review boundary.
3. **One hand-authored fixture CTA** (P3) — prove the shape feels useful and
   does *not* sound like truth, before any automation.
4. **Read-only `loop/scout.py`** (P4) — only after the fixture works: reads
   priors, requires purpose+goal, emits one marked CTA, mints nothing, alters
   no ledger, never self-claims or self-lands.
5. **Surface Scout beside `gaps.py`** (P5) — a clearly-marked FRONTIER CTA
   next to the MAINTENANCE GAPs; ignorable, claimable, or prunable.

## 11. Open decisions (bdo's) — his recommendations, adopted as working defaults

Marked proposed; freezing the P2 done-line locks them, so this is the moment
to change any.

- **A — Name:** `Scout lobe` *(reads the frontier, does not crown itself
  authority, returns one recommended move)*.
- **B — Loop naming:** `Scout → Claim → Build → Prune` *(Ontum-native, over
  importing the 4X terms directly)*.
- **C — Persistence:** **yes**, but only as marked, **expiring** conjecture
  traces — so the system can later learn whether acting on a CTA paid,
  without polluting the ledger.
- **D — Self-aiming:** **no, not in v1** — start **handed** (the user or
  current epic provides purpose+goal). A proposal-only self-aiming scout mode
  is a later increment, not the first slice.

## 12. Reconciliation with in-flight work (named, not silently resolved)

- [explore-lobe.proposal.md](explore-lobe.proposal.md) stands as the design
  capture (history); this note is the broader frame it feeds.
- The earlier working `epic.explore-lobe` is **renamed** to
  `epic.strategy-metabolism` (pieces Scout/Claim/Build/Prune) — adopting
  decisions A/B. Epics are not frozen, and the old file was never committed,
  so this is a clean rename, not a rewrite of history.
- **Frozen done-line 0140** (`atom.explore-fold.v0`) names "explore" (not
  "scout") and predates the ScoutCTA schema. A session cannot edit or
  supersede a frozen bar — **moving it is bdo's alone**
  (`loop.pen supersede-done … --by bdo`). It is **met** by `loop/explore.py`
  + `tests/test_explore.py` (the explore-fold read-only fold), so it ships as
  a coherent, tested slice rather than dead code; the name stays "explore"
  because the bar froze it. Whether to supersede it toward the Scout name
  stays bdo's call, surfaced not worked around.
- `loop/explore.py` (+ its test) is the explore-fold: the v0 read-only fold
  with the ghost-refusal teeth. `loop/scout_cta.py` (+ its test) is the
  ScoutCTA **contract** (done-line 0141, §6 schema). The generating
  `loop/scout.py` that joins the fold to the schema, and the **Claim** and
  **Prune** organs, are named but later lines.
