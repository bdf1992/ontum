# Report 0128 — Agent runs on the books: the training-posture + monitor layer, and feedback

## What I did

bdo asked, across a refining conversation, to "run [the agents-launching-subagents
admin] on the books as a training program so to speak but ensure it gets monitored
by some process." This is the action trace.

1. **Read the frame, not just the task.** Three corrections reshaped the work:
   make is *filling a volume* (agents are utensils), "not done -> still making"
   (stranded branches are abandoned *making*, not a backlog), and agents strand
   because they are *summoned wrong* (a sticky-note string, no governed prompt /
   rung / receipt). "On the books as a training program, monitored" is the unlock:
   a probationary, recorded, watched run that asserts nothing as done.

2. **Recovered abandoned work.** The viewport was dirty; `git.py whiteout`
   preserved 8 paths on `claude/rescue-viewport-2026-06-22-3` (pushed) and cleaned
   it. Inside: C1 (`tend-heal.claude.v1.md`, a governed node prompt) and C3
   (`loop/prompt_req.py` + test) — already built, abandoned mid-make. The
   conversation made literal.

3. **Built the missing layer — `loop/agent_run.py`.** Agent runs ON THE BOOKS:
   an `agent_training_run` posture admission (opened, attributed), every run
   booked as an `agent_run` receipt stamped `training: true`, and `fold_run` as
   the monitor read. It mirrors `loop/train.py` one axis over (fence-readings ->
   agent-runs). §10 teeth, proven non-vacuous in `tests/test_agent_run.py`: a
   **ghost node** or a **mismatched prompt hash** is REFUSED at the write seam —
   you cannot book an ungoverned run; an empty run reads empty, never a false
   all-clear; re-book is idempotent.

4. **Wired the composition.** `tend-heal.js` gained an **Open** phase (open the
   posture) and a **Book** phase (book each disposition under it) — every agent
   the workflow spends is witnessed by construction.

5. **Verified.** Full suite **1401 tests, OK**. New + recovered tests green.

## What's real now (facts, not claims)

- Branch `claude/agent-training-run` (off the rescue branch): `loop/agent_run.py`,
  `tests/test_agent_run.py`, `tend-heal.js` Open/Book wiring. Suite 1401 green.
- Recovered and green: C1 node prompt, C3 validator (`prompt_req`, 6/6).
- UNLANDED. No atom announced yet, no PR, no independent review.

## Feedback (honest, the part you asked for)

- **The workstation-fence trap is still biting, and its deny message points the
  wrong way.** From this viewport-rooted session, Write was denied to BOTH the
  viewport AND a manually-created worktree. The deny message recommends
  `git worktree add` — which leads straight into the trap (you make the worktree,
  then Write is still denied). The escape that actually works is the harness
  `EnterWorktree` tool, which I only knew from memory. **Fix worth making:** the
  workstation_guard's deny message should name `EnterWorktree`, not
  `git worktree add`. This has now cost multiple sessions (#355, #415).

- **Your owner surface is being spammed.** The reflector is minting DUPLICATE
  owner-ask mirror issues — this turn alone #525-#544 duplicate #511-#530 (~36
  issues for ~6 reports). That is the opposite of the digest's purpose; it makes
  the inbox unreadable. The drift fold or the reflect beat is double-firing —
  worth a heal/retro look before it buries a real ask.

- **The captured ledger claimed files that don't exist** (`volume.py`,
  `section.py`, `fleet.py` named as "built this session" — none on disk). I
  verified rather than trusting the prose, but it's a live instance of the same
  "prose outran reality" pattern, in our own records. A reality-check pass on
  `agent-summoning-requirements.md` is owed.

- **On myself:** I over-deliberated early and nearly handed you a "which way
  through the fence?" fork that I could resolve myself — the EnterWorktree escape
  was already in my memory. I should reach for the recorded escape hatches before
  surfacing a choice to you. Caught it, but late.

- **What went right:** the reframe to "training, on the books, monitored" was the
  correct unlock — it dissolved the production-land deadlock and the bootstrap
  ("can't summon on a rail that doesn't exist"). Building by mirroring `train.py`
  kept it to one small, tested module instead of a new subsystem.

## needs-you

1. **Name the arc.** No confirmed epic exists for this (home is the PROPOSED
   `authoring-platform` / `agent-summoning-requirements.md`). Recommendation: a
   new `epic.agent-summoning`, or fold into `epic.virtual-fleet` (this is the
   Administrator's hands). One confirm-arc lets the merge-node land it.
2. Then I drive atom -> independent value-gate -> PR myself; the live monitored
   `tend-heal` run fires AFTER it is on main (agents must see the code).

## End-state

`report` — the on-the-books + training-posture + monitor layer is built and
green (suite 1401), composing recovered C1/C3; unlanded, awaiting one arc-naming
from bdo before the atom/gate/PR drive and the first live monitored run.
