# Report 0088 — recommend — the generative branching tree, built shape-first

## What landed

**done-line 0125 — recommend: /ask expanded into a generative branching tree, with the code bound.** Built this session as a sibling of /ask (done-line 0119), serving `epic.owner-harness` as the synchronous wide-decision render beside /ask's single fork.

- `.claude/skills/recommend/SKILL.md` — the ritual: a compositum is a generative branching tree of `AskUserQuestion` panels (≤4 tabs × ≤4 options); a route selected in a tab GENERATES the next set of checkboxes, composed live by the session (the inference) from the route + the gesture. The composer is prompt-as-code (the session), because `AskUserQuestion` is a session tool no subprocess can reach.
- `.claude/skills/recommend/policy.md` — inherits /ask's whole law (R1–R7 + refusal teeth) as its floor and adds RC1–RC5 (routed tree, routing-generates-next, bounded generation, session-composer, real-decision-space-not-dump) with its own refusal teeth.
- `.claude/skills/recommend/compose.py` — the code bound: REUSES `ask_guard.shape_problems` (I-4, one definition) and adds the tree bound (the 4×4 cap + header cap), refusing any generated panel before it renders. `--selftest` is the §10 teeth (passes a good panel, refuses a bad one with five distinct refusals).
- `atom.recommend-generative-tree.v0` — announced and judged **accept** by an INDEPENDENT value-gate (D-2; `rcp.f66494ea58cb`), which verified on disk that the bound is real, not decorative.
- **PR #234** (`claude/recommend-skill`, off `origin/main`), full suite green (930 tests, OK).

The shape took **two corrections to transfer**, both surfaced by the R7 checklist: a "document + decision-pens" render was rejected, and my "inverse ask / confirm-not-select" framing was a mis-read and rejected too. bdo's true shape — "multiple tabs of 4 options with routing, so one route prompts a second set of checkboxes" — is the generative branching tree. The generative step was demonstrated live (bdo walked the LAND route; it generated that route's scope checklist). bdo also caught an option I offered with no risk/impact stated ("IS this actually a choice?") — a near-false choice (a second hook beside ask_guard) that was dropped; recorded as a learning in the shared `ontum-ask-surface-discipline` memory.

## needs-you

Nothing new is parked on bdo by this piece. PR #234 is merge-node-eligible and lands under `epic.owner-harness`'s standing arc confirmation once the suite is green — no new gesture required.

Conflict named (not silently resolved): the shared primary worktree (on `claude/terminal-pull-gateway`) carried another session's uncommitted log appends and an untracked proposal file, so a clean checkout of `origin/main` was impossible. Resolved without disturbing that work by building the PR in an **isolated git worktree** from `origin/main`, replaying only this session's two log lines (the announce event + the value-gate receipt). The isolated worktree (`../ontum-recommend-wt`) is removed at session end.

## End-state

`report` — recommend shipped shape-first (two corrections, R7 the transfer mechanism); PR #234 open, suite green, atom value-gate-accepted; the generative-composer learning loop and any live PreToolUse enforcement of the bound are the named next increments (out of scope, the gateway-policy-spine owns enforcement).
