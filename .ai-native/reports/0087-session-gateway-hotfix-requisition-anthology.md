# Report 0087 — Session-gateway routing hotfix, the requisition lesson, and the dedicated-space + code-review-gate decisions

## What landed

bdo opened with "better session start" and it widened, over the session, into the session-gateway thread's core: a session must be **insulated, requisition independently, and not consider work landed until reviewed**.

- **#223 — fence read-only git diagnostics (done-line 0120, epic.substrate).** Split the broad `git-branch-topology` fence rule into `git-branch-mutate` + `git-worktree-mutate`; read-only introspection (`git branch --show-current`, `git worktree list`) now falls through to allowed on the Codex surface (it was prompted — friction on the single most common session-opening move: a fold over the last 50 sessions found 30/50 probe `git branch`/`git status` in their first 3 shell calls). `tests.test_fence` green; matcher proof = read-only allowed / mutating prompted. **Driven the full requisition chain** (bdo's correction — "you must requisition, not stop short"): signed (atom.created) → submitted (parked on the summon queue) → requisitioned the independent judge through the **branded spawn rail** (`ontum-node:value-gate.claude.v1` — the rail refused the unbranded spawn, pinned the §7 prompt + checked the rung before the node acted: the gateway request made real) → independent accept **rcp.7414a2af3224** (D-2) → off-log green → readied for the merge-node.
- **#232 — the landing-contract intent rule (phrasing lane, epic.owner-harness).** Added a root-CLAUDE.md hard rule: *work is not landed until an independent review is requisitioned and processed; a session that stops at "I built it" has landed nothing.* Prose-only via the phrasing lane (phrasing-clean adm.aa2eb1e09f28, no atom). It obeys its own rule the only way available pre-gate: the phrasing lane's server-side re-verification is its independent check (the bootstrap).
- **This consolidation PR** — the anthology bless draft (`anthology-self-governing-loop.proposal.md`) + this report, phrasing-clean.

Reshape of bdo's 3-part hotfix: **P2 (commit-pen `--on`/head-intent) was already on main** (#219/0118) — dropped, not re-ported. **P3 (workspace binding)** was already built/shipped on #225 (done-line 0121) by a parallel stream — I started porting it, the fleet-id fence exposed the existing branch, and I **backed out the duplicate** rather than create a second copy (the sprawl the work fights).

## needs-you

- **Bless the anthology** (`anthology-self-governing-loop.proposal.md`): set its name, fix its boundary (are #224/#230 in?). Drafted for your stamp; naming is yours (D-4).
- Everything else is the loop's or a node's, not yours: the merge digest reads **"your move: nothing — every arc with live work is confirmed."** #223 and #232 are merge-node-eligible (need a merge-node *run*, not a gesture; auto-requisition is `loop.pull`/#226). The code-review gate (the intent rule's structural teeth) is shape-locked and deferred to a fresh dedicated session — a high-blast-radius `PIPELINE` change, deliberately not rushed at the tail of this session.

## End-state

`report` — fence diagnostics + the landing-contract intent rule shipped and driven through every gate a session may; the dedicated-space decision and the code-review-gate shape are locked and captured (memory `ontum-session-gateway-governed-folding`); the anthology is drafted and awaits bdo's bless. Three findings on the record: 60% of sessions open by orienting to where they are (the dedicated-space case), hook-config contamination from the shared viewport (change_guard pinned to a parallel branch), and the inflight-cap clog jamming the requisition queue.
