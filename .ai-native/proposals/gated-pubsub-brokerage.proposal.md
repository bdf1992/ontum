# Gated pub/sub brokerage — the one bus for every seam (PROPOSED)

> **Status: PROPOSED** — bdo's direction, 2026-06-21 (this design conversation),
> his to steer. A blueprint, not a build: it unifies two proposals already on
> the record — [`git-gh-gateway.proposal.md`](git-gh-gateway.proposal.md) and
> the platform-brokerage blueprint (in-flight, PR #354) — into one spine, and
> names the first buildable slice. No code is implied as done; every mechanism
> below is mapped to a primitive that already exists or named as a hole.

---

## The problem this names

A session asked the loop's own folds "what is the backlog?" and they came back
clean — no drift, owner inbox 0, top gap "exercise an idle part" — while GitHub
showed **16 open PRs and 16 open issues**. The right reading of *"the gauge says
empty while the tank is visibly full"* is **the gauge is not wired to the
tank**, not "the tank is empty."

Three symptoms of one cause:

1. **The situational folds are blind to the real queue.** `loop.node inbox`,
   `loop.summon`, and `loop.gaps` are computed only from the local log's
   internal pipeline state; they never fold in open PRs or issues. So the
   surfaces that decide *what's on bdo* and *what a session does next* steer at
   trivial gaps while real work sits unseen.
2. **GitHub artifacts are not all local-request reflections.** The reflect pen
   already projects three kinds (`owner-stamp-queue`, `owner-ask-backlog`,
   `merge-divergences`) log → GitHub, and for those the surface honestly mirrors
   the log. But PRs, headless-run trackers, blueprints, and raw-`gh` issues
   originate *on GitHub* with no local record — so the loop is structurally
   blind to them.
3. **Publishing is ungoverned at the edge.** Issue #412 names it: GitHub issue
   creation has no general pen and a prompt-parity hole — a raw-`gh` issue is an
   *ungated publish*.

## The shape: a gated pub/sub bus over the log

The log is already described as a pub/sub topic ([`loop/reflect.py`], per
`loop/CLAUDE.md`: *"the log is the topic, rules the subscriptions, reflection
records the acks, drift the unconsumed backlog"*). Today that bus has three
subscriptions and only publishes outward. This generalizes it into the full
spine, and — the load-bearing constraint — **every hop is a gateway crossing**
(who-may decided at each seam), per the per-dir gateway stack already on record
(`authN → fence·policy·guard·gate·threshold → pen → patrol → ledger → heal`).

The brokerage *routes* records; the gateways decide *who may* at each seam:

- **publish** — a gateway decides who may append to a topic (the pen + policy).
  This closes #412 by construction: there is no ungated publish.
- **subscribe / deliver** — authZ on who receives what.
- **transform** — the transformation queue runs under a gateway, bounded the way
  `loop/inference_queue.py` already bounds its request queue (an admitted
  concurrency dial, a file semaphore — local coordination, not a broker).
- **egress** (project → GitHub) — writes authorized, teeth at the boundary
  (the git/gh-gateway asymmetry: writes authorized, reads witnessed).
- **witness** (GitHub → local) — external reality enters only through the
  inbound gateway; nothing raw is trusted.

## The component map (every piece is a primitive that exists)

| Pub/sub piece | ontum primitive on disk |
|---|---|
| Topic | the append-only log (`.ai-native/log/`) — truth at rest |
| Publish | appending a request-record through a pen/gateway |
| Subscription | admitted `rule` records (kind × consumer) — `loop/reflect.py` |
| Brokerage | the Herald, generalized (`loop/herald.py`; platform-brokerage #354) — a fold-router, not a daemon |
| Transformation queue | the reflect translator (`SURFACE_KINDS`), bounded like `loop/inference_queue.py` |
| Processing | the consumers: reflect (→ GitHub), the situational folds (→ gaps/inbox), the gateway (→ git/gh acts) |
| Acks / backlog | reflection records / `drift` — the unconsumed queue |
| Transport/cache | `queues/`/`offsets/` — a pure, rebuildable fold over the log |

## The no-broker law, and how it holds

"No broker, no daemon, no network at runtime" *sounds* violated by "pub/sub +
queue + brokerage." It is not, for the same reason the rest of the loop isn't:

- the **topic is the log** — truth at rest, never a running bus;
- the **transport/queue is rebuildable cache** (`queues/`/`offsets/` are "a pure
  fold over the log, deletable and rebuilt at any time"), so **truth is never in
  transit** — only ephemeral messages move;
- the **brokerage is a fold-router**, not a process — standing is recomputed
  from records (the Herald's law), never asserted by a live daemon.

`loop/inference_queue.py` is the existence-proof: a bounded, local processing
queue that explicitly *"is a local coordination primitive, not the no-network
ban's broker."*

## Two flows over the one bus

- **Outbound** — a local request (open-PR, file-issue, owner-ask) is published
  through a gate → transformed per subscriber → projected to GitHub. Locally
  available by construction; GitHub is a gated projection.
- **Inbound** — an external event (bdo's click, the cloud daily-digest routine,
  Codex, a foreign review) is **witnessed** through a gate → published as a
  record → transformed → folded into the situational state. The gaps/inbox
  folds finally see it; GitHub is a witnessed mirror, never an independent
  source of truth.

## What it unifies and closes

- `git-gh-gateway.proposal.md` — this is its read/write spine, both legs.
- the platform-brokerage blueprint (#354) — its first concrete link
  ("generalize the Herald + routing-on-record").
- the reflect pen's partiality — three kinds become the general case.
- #412 — ungoverned issue creation: a gated publish has a pen by definition.
- the blind-gauge wiring — the situational folds subscribe to the PR/issue
  topic, so backlog becomes visible without trusting GitHub as truth.

## First increment (the smallest real slice)

Skeleton-first, one real node (§9): build the **inbound witness leg for the PR/
issue backlog** first, because it directly fixes the symptom that surfaced this
design.

- a read-gateway fold that witnesses `gh pr list` / `gh issue list` into the log
  as `witnessed_artifact` records (reads witnessed, never trusted as truth);
- a subscription that joins those records into `loop.gaps` (a new gap class:
  *PR awaiting land/review*, *issue awaiting resolution*) and `loop.node inbox`
  (blueprints/owner-asks awaiting bdo);
- the §10 teeth: the witness fold must be able to *disagree* with a stale local
  read and surface the divergence — if it can only ever agree, it is not wired.

Done-line: the situational folds report the same backlog count the page shows,
and a session that blinks in is handed "N PRs await landing, M issues await
you" instead of "exercise an idle part."

## Open holes (grip discipline — carried, not hidden)

- **Migration of the already-born.** The 32 open artifacts predate this spine;
  some have no local origin record. The inbound witness covers them, but a
  raw-`gh` issue created tomorrow still needs the publish gate to *exist* — the
  general-issue pen (#412) is a precondition, not implied done here.
- **Topic granularity.** One topic (the log) with kind-filtered subscriptions,
  or per-kind topics? Unresolved. *Non-example:* a second log file per topic
  would be a second source of truth — refused.
- **Who authorizes a subscription.** A new subscriber (a fold that wants the
  PR topic) is itself a gated act (an admitted `rule`, bdo's stamp). The
  authority graph for "who may subscribe" is named, not designed.
- **Ordering vs level-triggered.** The bus is level-triggered (re-fold to
  current), not ordered-delivery. Consumers that need order (a transform chain)
  must declare it; this is unspecified.

## Not in scope

This proposal does not route inference, tool-use, or the inter-session mesh
through the bus — only the git/gh artifact seam (PRs, issues) as the first
domain. The wider "all activity through one gateway" (the activity-accounting
arc) composes with this later; it is not assumed here.
