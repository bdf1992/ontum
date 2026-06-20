# Done-line 0134 — epic.environments captured — snapshots that cross gated environments

> **Done when:** `epic.environments` is on the record as a confirmable arc — the
> proposal (`environments.proposal.md`) and the epic record
> (`.ai-native/epics/epic.environments.json`) capture the snapshot-spine design
> bdo blessed and authorized in session (2026-06-19), the work is atom-backed on
> the log so the PR is a landable unit, and bdo's confirm-arc is recorded. When
> the arc is captured and confirmed, stop — the pieces (the production gate
> first) are later done-lines, not this one.

## Why

bdo asked whether named environments and recorded deployments would have helped,
even just toward the requirement that someone else accepts your work (D-2). The
evidence answered yes: the recurring failure mode is work with no clean
checkpoint between "built" and "accepted" — one session's garden report alone
carried 13 stranded branches and a run of "merged PR, but the cut is held —
commits not on origin/main." That is the same per-atom pipeline ↛ per-PR git
namespace gap `loop/pull.py` was chipping at. bdo's reframe is the spine: a
snapshot is the natural unit a second party accepts, immutable and named the way
an atom's identity already is its content hash, and a deployment promotes a
snapshot from one environment to the next — acceptance attaching to the snapshot,
not the mutable branch.

## What is captured

Two records: `environments.proposal.md` (the design and its evidence) and
`.ai-native/epics/epic.environments.json` (the arc, its two axes — deploy and
runtime — and its pieces, each pinned to a real need). The arc composes existing
organs (the merge-node, `loop/digest.py`, the off-log gate, the gateway economy,
`loop/pull.py`) and refuses to double-build them (§10); it holds two guardrails —
no dev/staging/prod cargo-culted onto the local loop, and a deploy gate that
executes bdo's stamp rather than inventing a verdict (the `.github/` law).
