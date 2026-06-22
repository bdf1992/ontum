# Done-line 0168 — The headless gate judge gets stdin=DEVNULL so the rail cannot hang

﻿# Done-line ? The headless gate judge gets stdin=DEVNULL, so the rail cannot hang

> **Done when:** the headless gate rail returns a verdict instead of hanging,
> because the launched `claude -p` no longer inherits the parent process's stdin.
> The bar is met when:
>
> 1. gate.py launch_claude passes stdin=subprocess.DEVNULL to the headless
>    `claude -p` subprocess (in addition to the existing neutral temp cwd and the
>    explicit model).
> 2. The git-rail test asserts it: a captured-runner test reads the kwargs passed
>    to the launch and asserts stdin is subprocess.DEVNULL. Non-vacuous: the
>    pre-fix call passed no stdin, so the assertion would read None and fail.
> 3. A live gate run through the previously-failing path lands a real verdict
>    (the same composed prompt that timed out at 600s completes in ~46s with a
>    DEVNULL stdin).
>
> Scope guard: this is the stdin redirect only. It does NOT change the judging
> prompt, the model, the verdict-landing pen path, or the neutral cwd.

## Why

A self-paced overnight loop requisitioned a value-gate on its own built work and
the headless rail timed out at 600s four times (issues #390/#391/#393/#396).
Isolation testing falsified every easy theory: auth and inference are fine (a
trivial headless call returns in ~1s; a valid-model call returns "pong" in
seconds); the model is not the cause (opus and sonnet hung identically); the
permission wall is not the cause (--dangerously-skip-permissions still hung); the
judge makes zero tool calls, so it is not a missing-file loop. The one variable
that mattered was the child process's stdin: spawned from an interactive-ish
parent (the PowerShell tool, in this case) the headless `claude` inherited a live
stdin and blocked on it; redirecting the child's stdin to DEVNULL completed the
exact same prompt through the exact same path in ~46s. A non-interactive judge
must never inherit a live stdin.

Serves epic.virtual-fleet: open summonses can only get judges without a human if
the headless gate rail actually returns a verdict. A rail that hangs on spawn is
the difference between the loop staffing its own gates and not.
