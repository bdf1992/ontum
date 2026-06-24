@echo off
REM ontum overnight administer tick — fires one bounded increment toward the
REM branded-surface parity marker. Modeled on ontum-loop-tick.cmd. Each fire is a
REM fresh, mortal `claude -p` run in this worktree that reads ADMINISTER.md and
REM does ONE increment, commits via the git pen, and pushes. State lives in the
REM committed tree (PROGRESS.md / PARITY-CHECKLIST.md), never in a tick's memory.
REM Disable by hand any time:  schtasks /change /tn ontum-overnight /disable
REM
REM Overlap is handled by the scheduler's native "do not start a new instance"
REM policy (default for schtasks-created tasks) — no lockfile (a stale lock from a
REM killed tick would otherwise block every future tick).
REM
REM MODEL is pinned explicitly: the bare default alias resolved to "opus" and the
REM API returned 404 (model: opus). Pin a full, valid id.
setlocal
set PATH=C:\Program Files\GitHub CLI;C:\Users\bdf19\AppData\Roaming\npm;C:\Users\bdf19\AppData\Local\Programs\Python\Python312;C:\Program Files\Git\cmd;%PATH%
set WT=C:\Users\bdf19\ontum-overnight
set LOG=C:\Users\bdf19\ontum-overnight-tick.log
set MODEL=claude-opus-4-8

cd /d %WT%

echo ==== overnight tick %DATE% %TIME% (model %MODEL%) ==== >> %LOG%
git pull --no-edit origin claude/overnight-branded-surface >> %LOG% 2>&1

claude -p "Run ONE overnight administer tick for the branded Claude surface. Read vscode/ontum-surface/ADMINISTER.md and follow it exactly: check the stop conditions FIRST (marker-met / STOPPED-infeasible / clock at-or-after 08:00), then do ONE bounded increment, verify it with a real check, update PROGRESS.md and PARITY-CHECKLIST.md, and COMMIT through the git pen (.claude/skills/branch-ritual/git.py — never raw git add/commit). Do NOT push — the wrapper pushes synchronously after you exit (a backgrounded in-tick push gets cut when this headless process ends). If the marker is met, run the self-grade + /code-review ultra peer grade + open the PR with GRADES.md per ADMINISTER.md, then set STATE so later ticks exit." --model %MODEL% --permission-mode bypassPermissions --append-system-prompt "You are an UNATTENDED overnight tick. Be conservative: exactly one increment, honest checkable evidence, commit (do NOT push — the wrapper does), then stop. Never push to main, never merge, never bypass the command_guard fence. Under-claim before you over-claim." >> %LOG% 2>&1

REM Synchronous push AFTER the agent exits — the root-cause fix: an in-tick
REM `pr.py push` backgrounds and is killed when the headless tick process ends,
REM stranding commits locally. Pushing here (the cmd waits for it) guarantees each
REM tick's commits reach origin. No-op when there is nothing new.
echo ---- wrapper push %DATE% %TIME% ---- >> %LOG%
python .claude\skills\branch-ritual\pr.py push >> %LOG% 2>&1

echo ==== tick done %DATE% %TIME% ==== >> %LOG%
endlocal
