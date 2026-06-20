# The served gateway — governed reach from every surface (PROPOSED)

*Captured 2026-06-20 (bdo + session), from issue #245 + the log-consistency
thread. PROPOSED: bdo names the epic and draws the served-tier boundary; this
file only frames the gap and cites what already exists so it is not
double-built.*

## The gap (one sentence)

ontum's governance — the pens — is **shell-local**: a pen is a local Python
script that shells out to `gh` and reads/writes a log on the *current branch's*
working tree. So governance breaks in two directions at once:

- **Across environments (#245):** from web/mobile Claude Code there is no `gh`
  and no local checkout, so the paved pens cannot run — and the only way to act
  (open a PR, confirm an arc) is to **bypass the pen** through the raw GitHub
  integration. That is "ink that skipped the pen," the one failure the substrate
  exists to refuse. PR #244 was opened exactly this way.
- **Across branches (the log-consistency thread):** a governance admission
  written on one branch's log is invisible to a fold reading another branch or
  the trunk until it merges. This is why the owner-ask backlog read 29 on one
  branch and 0 on another, and why the herald's arc-confirm had to be
  hand-pushed to the trunk.

Same root: **governance lives in the wrong place** — bolted to a local shell, a
local checkout, a local branch.

## The move (bdo, 2026-06-20): serve the pens as a gateway

Make the pens reachable as **MCP gateway tools**, and the two break-points heal
together — because they are the same problem. Every governed act
(`pr_create`, `confirm_arc`, `node_judge`, `admit_real`, `admit_rung`,
`policy`, log append) becomes a tool the **ontum gateway** serves. Then:

- **Environment parity (#245):** local, web, and mobile call the *same* gateway
  tools. The AI instance has identical governed reach everywhere; there is no
  `gh`-shaped hole to bypass through (this is #245's option (b), generalized
  past GitHub I/O to all governance).
- **Log-consistency:** the gateway is the *one* seam that holds and serves the
  canonical state, so consistency is true **by construction** — one gateway, one
  truth — instead of reconciled per-branch. The gateway *is* the
  `trunk_admit` / `trunk_read` seam the log-consistency thread proposed.
- **The gateway economy made real:** this is `inference.py`'s PEP, the trust
  ladder, and the herald (agent registration) as the *actual architecture*, not
  a metaphor. A call from mobile is a particle arriving at the gateway, judged
  before it acts.

## Don't double-build — what already exists (cite, compose)

- **`epic.inference-gateway`** (confirmed) — the PEP for *minds*: deny-by-default
  routing of which model may judge. The policy core of a gateway already exists.
- **`session-gateway.proposal.md` (§13) + `gateway-policy-spine.proposal.md` +
  `ambient-gateway.chapter.md`** — the gateway economy: legislation /
  enforcement / regulation spine, the herald, the contribution economy. The
  *design* is done; this proposal is its missing **served-reach** layer.
- **`loop/web.py`** — a *served* fold already (the owner inbox over HTTP). The
  precedent that ontum can serve a surface, not only shell locally.
- **Name-trap:** `epic.repoprompt-parity` (`loop/parity.py`) is a **different**
  parity — the RepoPrompt agent-*boundedness* matrix, not environment parity.
  Do not conflate them by the word.
- **Already fixed, so not in scope:** #245's *second* bug (an epic-introducing
  PR could not confirm its own arc) is resolved by `--from-ref` (done-line 0130,
  #246) + the no-ref hardening (#272). Only the *served-reach* half is open.

## The one load-bearing decision (name it, don't slide into it)

An MCP gateway reachable from web/mobile is a **served tier** — and "no broker,
no daemon, no network at runtime" is a hard rule. But that rule governs the
**runtime loop** (`reconcile`/`orchestrate` folding local files), which stays
local *beneath* this. The gateway is a *new* tier: the served governed seam. It
is already on the horizon ("a served, authenticated inbox where bdo steers arcs,
from whatever device he is on") — this generalizes that from one inbox to **the
front door of all governance**. Drawing that boundary — what the loop keeps
local vs. what the gateway serves — is bdo's, and is the first gate of the arc.

## The discipline that keeps it safe (I-4)

The MCP tool `pr_create` and the local `pr.py create` must be the **same**
governance code — story validation, atom-backing, D-2, rung checks, no-self-sign
— exactly as `command_guard` derives its deny-list from `fence/policy.py`. The
pen logic *is* the gateway logic. Two implementations would drift, and a remote
call would become the very bypass this exists to kill. One definition, two
surfaces (local CLI + MCP), never a twin list.

## §10 teeth (what a real build must let refuse)

- A gateway tool that lets a remote call **skip a gate the local pen enforces**
  (the bypass returning by another door) — the build must prove a malformed
  remote `pr_create` is refused exactly as the local one is.
- A **second** governance implementation behind the MCP path (drift from the
  pen) — refused by the one-definition rule; the tool must *call* the pen logic.
- A served tier that quietly makes the **runtime loop** network-dependent — the
  loop must still fold a local log with the gateway down.

## First slice (where the pain is live)

The `gh` seam: give the GitHub pens an MCP-backed I/O path (open PR, read checks,
comment) **behind the same pen logic**, so the paved path is whole in a remote
environment. That is #245 option (b) and the seed of the whole gateway — the
smallest piece that stops forcing a governance-bypass from mobile.

## Open (bdo's)

1. The **epic**: extend `epic.inference-gateway`, or name a new
   `epic.ontum-gateway` that cites it + the §13 proposals as `dont-double-build`.
2. The **served-tier boundary**: what the loop keeps local vs. what the gateway
   serves (the first gate).
3. **Where the gateway runs** and how a remote AI instance authenticates to it
   (the served-inbox auth question, now load-bearing for every governed act).
