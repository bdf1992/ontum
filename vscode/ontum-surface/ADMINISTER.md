# The administer brief — what each overnight tick executes

This is the prompt the overnight tick runs (a fresh, mortal `claude` session in
this worktree, `C:\Users\bdf19\ontum-overnight`, branch
`claude/overnight-branded-surface`). You are the **administrator** of one
bounded increment toward parity-green for the branded Claude surface
(`epic.digital-experience`, blueprint:
`.ai-native/proposals/branded-claude-surface.proposal.md`).

## Your contract every tick

1. **Orient (read, don't assume).** Read `vscode/ontum-surface/PROGRESS.md` and
   `vscode/ontum-surface/PARITY-CHECKLIST.md`. They are the truth of where the
   build is. Read the blueprint if you need the why.
2. **Honor the stop conditions (check FIRST).** Stop this tick immediately,
   doing nothing else, if ANY hold:
   - `STATE: marker-met` or `STATE: STOPPED-infeasible` in PROGRESS.md — the run
     is already done; exit.
   - The local clock is **at or after 08:00** — the overnight window is closed;
     go to **§Marker reached** only if the marker is met, else just exit (a
     later run resumes).
   - Honest-stop: the bridge has been proven infeasible (SDK *and* headless CLI)
     — set `STATE: STOPPED-infeasible`, record the finding in PROGRESS.md and the
     checklist, then go to **§Land**.
3. **Do ONE bounded increment** (not the whole night's work):
   - If `STATE: not-started` or `spiking`: work
     **atom.branded-surface-bridge-spike.v0** — actually try to drive the engine
     from Node/JS via the **Claude Agent SDK** first (the same harness this repo
     runs on), then the **headless `claude` CLI** stream-json as fallback. Prove
     send-a-prompt-get-a-reply, and probe whether hooks / skills / MCP /
     permission-modes are inherited. Write the result into the checklist
     (`source` per row) and a short `SPIKE-FINDINGS.md`. Set `STATE: spiking`
     until the spike answers, then `building`.
   - If `STATE: building`: pick the **first non-green checklist row whose
     prerequisites are met** and build it to `green` with real evidence
     (a file, a passing `node` test, an observed behaviour). Prefer the
     blueprint's order: viewer (rows 1–4) → drive a turn (rows 5–6) → the rest.
   - Keep it small enough that you can verify it **this tick**.
4. **Verify.** Run whatever test proves the increment (`node ...test.js`, a
   manual check). A row goes `green` only with evidence a cold reader can check.
5. **Record + commit.** Update PROGRESS.md (green count, STATE, one tick-log
   line) and the checklist. Commit through the git pen
   (`python .claude/skills/branch-ritual/git.py add ... ` then `commit ...` —
   never raw `git add/commit`) and push the branch. The committed tree is the
   only thing the next tick inherits.
6. **Re-check the marker.** If all 18 rows are `green`, set `STATE: marker-met`
   and go to **§Marker reached**. Otherwise the tick ends; the next scheduled
   tick continues.

## §Marker reached — self-grade, peer-grade, land

When `STATE: marker-met` (or `STOPPED-infeasible`):

1. **Self-grade.** Write `vscode/ontum-surface/GRADES.md` — grade each checklist
   row honestly (green/partial/blocked + evidence), an overall parity score
   (green/18), what is solid, what is thin, and the riskiest unproven claim. Be
   adversarial with yourself (the §10 grain: if everything looks green on the
   first read, the grade isn't doing its job).
2. **Peer-grade (independent — never your own line, D-2).** Requisition the
   cloud review: run `/code-review ultra` on the branch's diff. Add its findings
   to GRADES.md under "Peer grade (/code-review ultra)". This is the second of
   the two acceptances.
3. **Leave bdo's section blank.** GRADES.md ends with `## bdo's grade (yours to
   fill)` — an empty section for his own grades and thoughts.
4. **Land a PR (never main).** Open the PR via the PR pen
   (`python .claude/skills/branch-ritual/pr.py ...`), titled for the arc,
   carrying the work + GRADES.md. Do **not** merge — the merge-node lands
   confirmed-arc PRs, and this arc is unconfirmed; bdo reads the PR, adds his
   grade, and confirms when ready.
5. **Self-disable.** Write `STATE: marker-met` (or `STOPPED-infeasible`) so every
   later scheduled tick exits at step 2. (The scheduled task may also be disabled
   by hand: `schtasks /change /tn ontum-overnight /disable`.)

## Hard limits (the guardrails)

- **One increment per tick.** No "finish everything" sprints.
- **Never push to main; never merge.** Sessions land PRs; the merge-node lands,
  and only confirmed arcs. bdo's stamp is the last gate.
- **The fence still binds.** Forbidden commands (raw `git push`/`gh pr` mutations,
  etc.) are blocked by `command_guard` regardless of permission mode — do not try
  to route around it; use the pens.
- **Absence is information.** If the spike proves the bridge can't be built, that
  is a real, valuable result — land it, don't fake green.
- **Honest evidence only.** A `green` row with no checkable evidence fails the
  grade and wastes the night. Under-claim before you over-claim.
