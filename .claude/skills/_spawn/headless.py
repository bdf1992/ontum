#!/usr/bin/env python3
"""The one headless-spawn helper for the skill pens (issue #411).

A headless model child (`claude -p`, `claude --resume … -p …`) must never
inherit the parent's stdin: spawned from an interactive-ish parent (the
PowerShell tool) it blocks on the live stdin and HANGS — the 600s timeouts of
issues #390/#391/#393/#396, fixed once in `gate.py launch_claude` with
`stdin=subprocess.DEVNULL` (done-line 0168). That guard lived at exactly one
call site as a lone correct call plus a prose comment, so a second spawner
(`continue-probe/probe.py:_spawn`) re-introduced the exact bug — it set
stdout/stderr to DEVNULL and left stdin inherited.

This helper makes the guard STRUCTURAL: there is now one place a headless child
is born, and that place ALWAYS sets `stdin=subprocess.DEVNULL` with no override.
A spawner cannot forget the guard, because the guard is not the spawner's to set.

The helper owns only the three std streams + timeout, never the command shape:
the caller hands the full argv and cwd; the helper decides stdin (always
DEVNULL), stdout/stderr (PIPE when capturing, DEVNULL when not), and whether the
child is awaited (`subprocess.run` with the timeout) or detached
(`subprocess.Popen`, returned unwaited for fire-and-forget).

Lives under `.claude/skills/`, never `loop/`: spawning a model is outward reach
(network, subprocess) and that belongs to the pens, never the loop substrate
(loop/'s local-first, no-subprocess law). Stdlib only.
"""

import subprocess


def headless_spawn(argv, *, cwd, timeout=None, detached=False, capture=True,
                   runner=subprocess.run):
    """Spawn a headless child with stdin ALWAYS closed (the whole point).

    argv      the full command (the caller owns the command shape).
    cwd       the working directory the child runs in.
    timeout   seconds, passed only on the awaited (detached=False) path.
    detached  False -> subprocess.run(...) awaited, returns CompletedProcess;
              True  -> subprocess.Popen(...) returned unwaited (fire-and-forget).
    capture   True  -> stdout/stderr=PIPE, text-decoded (the caller reads them);
              False -> stdout/stderr=DEVNULL (the caller wants no output).
    runner    injectable so a test drives both paths without a live spawn.

    stdin is MANDATORY subprocess.DEVNULL — there is deliberately no parameter to
    override it; that immovability is the entire reason this helper exists.
    """
    streams = {"stdin": subprocess.DEVNULL}
    if capture:
        streams["stdout"] = subprocess.PIPE
        streams["stderr"] = subprocess.PIPE
        streams["text"] = True
    else:
        streams["stdout"] = subprocess.DEVNULL
        streams["stderr"] = subprocess.DEVNULL
    if detached:
        # Popen does not take a timeout (it is returned unwaited); a detached
        # caller bounds the run itself if it cares.
        return runner(argv, cwd=cwd, **streams)
    return runner(argv, cwd=cwd, timeout=timeout, **streams)
