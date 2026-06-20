# Done-line 0157 — The trespass shame beat

# Done when

> **Done when:** a session that ATTEMPTS to flip the viewport (command_guard rule `viewport-flip`) or write a foreign tree (workstation_guard rule `foreign-worktree`) is SHAMED on its next prompt — even though the attempt was denied — and the shame grows louder per new attempt and goes silent once the session stops trying. Requires the attempts to be witnessed: workstation_guard now records its denials to the watch log (command_guard already did). Proven by a §10 test: the beat screams on a new attempt, stays silent with none, stays silent on replay (no new attempt), screams again on a fresh one, and the write-fence denial is recorded.

## Why

bdo, 2026-06-20: "its shamed if its attempted." The two fences (done-lines 0145, 0147) DENY a worker that reaches into a tree that isnt its own — but a blocked attempt is still an attempt, and a worker that keeps reaching should hear it get louder until it stops and works in its own worktree. The deny is the wall; the shame is the social signal that you tried to climb it. This is tooth #3 of the workstation fence, and it completes the set: deny the act (1, 2), name the trespasser (3).

## Shape

- `workstation_guard.py` records each foreign-worktree denial to the watch log (the prerequisite — an unwitnessed attempt cannot be shamed); its activity-register entry becomes `witnessed: true`.
- `trespass_shame.py` is a UserPromptSubmit beat (sibling of mock_shame/owner_ask_shame): a pure fold over the watch log for this sessions denied `viewport-flip`/`foreign-worktree` acts, louder with the count, quiet when no new attempt since the last beat (a gitignored per-session high-water mark, not truth — the watch log is truth). Fail-open, exit 0 always.

## Not in scope

The source fix (spawning workers into worktrees so they are never born in the viewport) stays a later chapter; with the fences live the shame names what still tries, it does not need to prevent the birth.
