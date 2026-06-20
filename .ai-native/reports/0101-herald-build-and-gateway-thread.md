# Report 0101 — The herald built and landed; the landing-throughput chain diagnosed; the served-gateway captured

## What landed

The session began with bdo's idea — "as soon as we have a gateway we must register
agents; a **herald** generates a suitable agent and logs heralds, not agents" — and
carried it the whole distance, then surfaced the infrastructure that distance exposed.

**On `main`:**

- **The herald** (`loop/herald.py`, PR #243, `rcp.merge.244`'s sibling `rcp.merge.243`).
  Agents are an open set, so registration and reputation are **folds** over logged
  `herald_introduction` admissions, never a table: a dumb `introduce` pen mints a
  content-hash credential at the trust-ladder floor (`loop.trust`); `roster` folds who
  is registered; `reputation` derives **distributed value** along the log's provenance
  edges (exemplars net notorieties per credential, a herald's meta-reputation over whom
  it vouched — a bad voucher visible by construction). 11 §10 tests; the no-launder test
  fails any constant standing. `value_confirmed` through independent gates (value-gate
  `accept`, value-confirm `confirmed` against the code on disk).
- **The new-arc confirm hardening** (`establish_plan` in `pr.py`, PR #272, `rcp.merge.272`):
  a forward confirm of a brand-new arc with no `--from-ref` now refuses *naming the flag*
  instead of a raw "nothing to commit" git error. 5 §10 tests; `value_confirmed`.
- **`epic.three-marks` wave 1** (`atom.mark-label.v0`, PR #244, `rcp.merge.244`) —
  unblocked and landed the governed way (bdo's `--from-ref` confirm + independent
  merge-node), after the MCP bypass left it stale-based, CI-less, and unconfirmed.

**Captured (origin branch, awaiting bdo's shaping):**

- **The served-gateway proposal** (`served-gateway-reach.proposal.md`, branch
  `claude/served-gateway-proposal`): #245 (environment parity) and the log-consistency
  thread are **one root** — governance is *shell-local* (a pen shelling to `gh`, reading a
  per-branch log), so it breaks across environments *and* branches. The move (bdo): serve
  the pens as **MCP gateway tools** — parity + log-consistency-by-construction + the §13
  gateway economy made real, in one. Cites `epic.inference-gateway`, the §13 proposals,
  and `loop/web.py` as `dont-double-build`; the served-tier boundary and the I-4
  one-implementation discipline are named as bdo's first gates.

**The chain the herald-landing exposed (the landing-throughput problem, lived):** every
blocker was a real gap. (1) stale-base branches that would clobber main; (2) the #235
hook-path bug making worktrees cd-hostile — *fixed mid-session* (#240); (3) the handoff
gate correctly refusing design-captures with no `touches`/`hands_off_to`; (4) **value-confirm
correctly refusing an undelivered design** — the deepest finding: *you cannot land a concept
as delivered value; it must be built* (this is why bdo chose "B — build it"); (5) the
new-epic **trunk bootstrap** (the fix `--from-ref`/#246 had *already landed* — used, not
rebuilt); (6) GitHub stale-DIRTY mergeability (cured by merging main into the branch).
The diagnosis is richer than the original envoy review — earned by trying to land.

The **log-consistency** root and its fix (governance trunk-canonical: written and read at
`origin/main`, generalizing the proven `pr.py confirm` push + `pr.py land` read) is folded
into the served-gateway proposal — the gateway *is* that seam.

## needs-you

One genuine owner gesture, and it is the hinge for everything downstream:

- **Draw the served-tier boundary** for the gateway — what the runtime loop keeps *local*
  vs. what the gateway *serves* (and the where-it-runs / how-a-remote-instance-authenticates
  question). This is the one call `served-gateway-reach.proposal.md` reserves for you; the
  moment you draw the line, the epic writes itself off it. I deliberately did **not** draft
  the epic, because its pieces hang entirely on that boundary — drafting now would be
  guessing it (the "slide into it" the proposal warns against).

Already on surfaces you read (not parked in the dark): **#247** (the bounds-must-not-restrict
principle), **#245** (the env-parity decision the gateway proposal now answers), and the
gateway **epic-naming** (`epic.inference-gateway` extension vs. a new `epic.ontum-gateway`).

A note surfaced this session and now self-corrected: the "29 owner-asks parked invisibly"
the shame hook screamed were a **branch-stale false count** (the surfacing acks live in
per-branch logs not merged to main) — the genuinely-live asks were already GitHub issues.
That false count is itself the strongest argument *for* the gateway: one served seam, one
truth, no per-branch divergence.

## End-state

`report` — herald, the confirm-hardening, and `epic.three-marks` wave 1 are on `main`,
each value_confirmed and landed by an independent merge-node (no self-signed line); the
served-gateway proposal is captured awaiting bdo's served-tier boundary; #235/#225 landed
mid-session so worktrees are cd-safe again; no work stranded, all worktrees cleaned.
