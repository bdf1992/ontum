# Proposal: `epic.environments` — snapshots that cross gated environments

**Status:** proposed, blessed and authorized by bdo in session (2026-06-19).
Captured here so sessions inherit the arc from the record, not from chat
(his standing rule). The owner steers at arc scale (done-line 0006); this is
the design the arc record (`.ai-native/epics/epic.environments.json`) condenses.

## Where this came from

bdo asked a genuine question: reading the past sessions, would *this process*
— named environments and recorded deployments — have helped, even just toward
the requirement that **someone else accepts your work** (D-2; no one signs their
own line)? The honest, evidence-backed answer is yes, and the evidence sits in
the session that proposed the arc:

- the garden report opened with **13 stranded branches**, 19 worktree chores,
  and a run of *"merged PR, but the cut is held — N commits not on origin/main —
  unlanded work"*;
- the same gap is the one `loop/pull.py` (the terminal-pull gateway) was chipping
  at: the **per-atom pipeline namespace and the per-PR git namespace do not
  join**.

The common root: **work has no clean checkpoint between "built" and "accepted."**
It strands because there is no frozen, named unit a second party can take in one
bite. The acceptance discipline has been hanging off PRs — mutable, mid-flight —
which is *why* it strands.

## The spine: a snapshot is the natural acceptance unit

bdo's reframe, and the center of gravity for the whole arc: **a snapshot is the
unit someone else accepts.** Immutable, named, recorded — the way an atom's
identity already *is* the sha256 of its bytes. A **deployment** is the act of
promoting a snapshot from one environment to the next; **acceptance attaches to
the snapshot, not the branch.** That is the unit that joins the per-atom ↛ per-PR
gap, and the artifact a reviewer (the merge-node, bdo's confirm, or an external
model family) takes whole.

## Two axes, deliberately named apart

"Environment" was carrying two different meanings; separating them is the naming
work this arc does.

- **The deploy axis** — *where a version is promoted to.* A served surface climbs
  rungs, each promotion a gated, recorded deployment (a receipt on a surface bdo
  can open anywhere): **preview → staging → production.**
- **The runtime axis** — *where the loop itself runs:* local viewport / web+mobile
  remote / cloud agent — and the parity that makes the paved pens behave the same
  on all three (issue #245).

## The pieces, each pinned to a real need

| piece | the real need it accommodates |
|---|---|
| **snapshot = the acceptance unit** *(the spine)* | the per-atom ↛ per-PR gap; the stranded-work failure mode above |
| **production gate** | the live URL changes today with no stamp from bdo (`.github/workflows/pages.yml` auto-deploys `main`) |
| **preview env** | bdo judges on the live URL and waits for `main`; a per-PR snapshot URL closes that |
| **staging rung** | there is no "integrated, not yet accepted" checkpoint to promote *from* |
| **runtime parity** | issue #245 — the paved pens don't work from web/mobile remote Claude Code |
| **served control plane** | the authenticated surface bdo steers from on any device — *remodeled from "served inbox," because an inbox is a queue;* the real piece is operable steering over the whole snapshot/environment economy, not a notification list |

## Two guardrails the arc holds itself to

- **Do not cargo-cult dev/staging/prod onto the loop substrate.** The loop is
  local files; the log is truth; there is nothing to deploy. Environments live
  only on the *served* and *runtime* surfaces. (Avoids the 1.0-on-AI-native
  category error.)
- **A deploy gate executes bdo's stamp; it never invents a verdict.** This is the
  `.github/` law (a server surface enforces *toward* truth, never as a second
  authority). Production-promotion becomes the same shape as confirm-arc: bdo
  confirms, the node lands.

## Horizon

Work moves as snapshots: every promotion across an environment is a frozen,
recorded checkpoint a second party accepts — served and operable wherever bdo is.

## What this arc deliberately does not double-build (§10)

The promotion-and-acceptance machinery composes existing organs rather than
re-deriving them: the merge-node and `loop/digest.py` (`epic.owner-harness`),
the off-log atom gate (`.github/`), the gateway economy (§13.10), and the
namespace-join groundwork in `loop/pull.py`. Where a piece overlaps one of these,
its glue cites it and refuses to re-build it. The first buildable slice is the
**production gate** — smallest real teeth, closing the unstamped-live gap directly.
