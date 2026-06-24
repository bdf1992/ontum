@echo off
REM ontum overnight administer tick — fires one bounded increment toward the
REM branded-surface parity marker. Modeled on ontum-loop-tick.cmd. Each fire is a
REM fresh, mortal `claude -p` run in this worktree that reads ADMINISTER.md and
REM does ONE increment, commits via the git pen, and pushes. State lives in the
REM committed tree (PROGRESS.md / PARITY-CHECKLIST.md), never in a tick's memory.
REM Disable by hand any time:  schtasks /change /tn ontum-overnight /disable
setlocal
set PATH=C:\Program Files\GitHub CLI;C:\Users\bdf19\AppData\Roaming\npm;C:\Users\bdf19\AppData\Local\Programs\Python\Python312;C:\Program Files\Git\cmd;%PATH%
set WT=C:\Users\bdf19\ontum-overnight
set LOG=C:\Users\bdf19\ontum-overnight-tick.log
set LOCK=%WT%\.overnight-tick.lock

cd /d %WT%

REM --- lockfile: skip if a previous tick is still running (no two claudes on one branch) ---
if exist "%LOCK%" (
  echo ==== %DATE% %TIME% skipped: tick already running ==== >> %LOG%
  goto :eof
)
echo locked %DATE% %TIME% > "%LOCK%"

echo ==== overnight tick %DATE% %TIME% ==== >> %LOG%
git pull --no-edit origin claude/overnight-branded-surface >> %LOG% 2>&1

claude -p "Run ONE overnight administer tick for the branded Claude surface. Read vscode/ontum-surface/ADMINISTER.md and follow it exactly: check the stop conditions FIRST (marker-met / STOPPED-infeasible / clock at-or-after 08:00), then do ONE bounded increment, verify it with a real check, update PROGRESS.md and PARITY-CHECKLIST.md, commit through the git pen (.claude/skills/branch-ritual/git.py — never raw git add/commit), and push the branch. If the marker is met, run the self-grade + /code-review ultra peer grade + open the PR with GRADES.md per ADMINISTER.md, then set STATE so later ticks exit." --permission-mode bypassPermissions --append-system-prompt "You are an UNATTENDED overnight tick. Be conservative: exactly one increment, honest checkable evidence, commit, then stop. Never push to main, never merge, never bypass the command_guard fence. Under-claim before you over-claim." >> %LOG% 2>&1

del "%LOCK%" 2>nul
echo ==== tick done %DATE% %TIME% ==== >> %LOG%
endlocal
