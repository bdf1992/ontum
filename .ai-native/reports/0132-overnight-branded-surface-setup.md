# Report 0132 — Overnight loop set up: branded-surface parity build, supervised spike GO, scheduled

## End-state

Set up and launched an unattended overnight administer-and-grade loop targeting `epic.digital-experience` (the ontum-branded VS Code surface over the Claude engine), per bdo's 2026-06-24 direction and his config-panel answers (build to full parity-green · peer = cloud `/code-review ultra` · run tonight → land a PR).

Built on worktree branch `claude/overnight-branded-surface` (at `C:\Users\bdf19\ontum-overnight`):

- **Arc homed:** `.ai-native/epics/epic.digital-experience.json` (PROPOSED) + the blueprint `.ai-native/proposals/branded-claude-surface.proposal.md`.
- **Marker:** done-line `0197` — parity checklist 18/18 green (or honest `STOPPED-infeasible`), self- + peer-graded, landed as a PR.
- **Pipeline:** `vscode/ontum-surface/{PARITY-CHECKLIST,PROGRESS,ADMINISTER,SPIKE-FINDINGS}.md` + `overnight-tick.cmd`. Each scheduled fire = a fresh `claude -p` tick that does ONE bounded increment, commits via the git pen, pushes; at the marker it self-grades, runs `/code-review ultra`, opens a PR with `GRADES.md`.
- **Supervised bridge spike = GO:** `@anthropic-ai/claude-code@2.0.19` present; CLI `--input/output-format stream-json` + `--include-partial-messages` + `--resume`/`--permission-mode` proven; observed `system/init` (env+tools+session_id loaded) and `result` (usage/cost) events. All `spike` checklist rows resolve to `inherit`; honest-stop did NOT trip.
- **Scheduled:** Windows task `ontum-overnight`, every 30 min from 02:46, bounded ~5h15m to ~08:00. Status: Ready. Log: `C:\Users\bdf19\ontum-overnight-tick.log`.

## Safety net

Nothing reaches main without bdo: sessions don't push main, the merge-node only lands confirmed-arc PRs it didn't author, and this arc is unconfirmed. Worst case = a messy branch + token spend, fully recoverable. The `command_guard` fence binds even under `bypassPermissions`. Kill switch: `schtasks /change /tn ontum-overnight /disable`.

## needs-you

- **Confirm-arc** `epic.digital-experience` when you've read the morning PR (`python -m loop.node confirm-arc --epic epic.digital-experience --by bdo`). I authored the epic FILE to home the work; that is not the confirm — the stamp stays yours (D-4).
- **The blueprint CTAs** (proposal §Calls to action) await your react — target, parity-first staging, the parity bar, build order, home.
- **Viewport anomaly:** the proposal file I first wrote into the viewport (`c:\Users\bdf19\ontum`) disappeared from disk before I could commit it — something swept the dirty viewport mid-session. Re-authored on the branch (no loss), but flagging that the viewport is being cleaned under you.
- **Auth assumption:** `claude -p` from a *scheduled task* (vs an interactive shell) is unproven to authenticate here; the 02:46 fire is the real test. If the log shows auth failure, the loop no-ops harmlessly and the setup still stands for a manual launch.
