# Report 0131 — Codex heartbeat hook hotfix

## End-state

Patched the Codex-native hook renderer so SessionStart runs `python -m loop.heartbeat --hook` before `python -m loop.summon --hook`. Regenerated `.codex/hooks.json` through `python fence/render_codex.py` and updated the local `.codex/` and `fence/` contracts plus `tests/test_fence.py` to pin the hook order.

## Why

Current `main` showed `python -m loop.summon` reporting no open summons while `python -m loop.orchestrate --status` showed 81 in-flight atoms, mostly at `derive:value.accepted`. Claude sessions already run the safe heartbeat on SessionStart, but Codex sessions only rendered summon+probe hooks. That left a guest Codex session able to observe the queue but not turn the level-triggered crank that creates the next parked gate.

## Verification

- `python fence/render_codex.py`
- `python -m unittest tests.test_fence tests.test_heartbeat -v` passed.
- `python -m loop.activity` reported all wired hooks accounted.
- `python -m unittest discover -s tests -v` ran 1526 tests with one unrelated failure: `tests.test_git_pen.TestGitGuard.test_local_mutating_git_is_now_watched` expects `git checkout -b claude/x` to pass as watched, but the live guard returned 2. Re-running that single test reproduced the same failure with no changes in `tests/test_git_pen.py`, `.claude/hooks/command_guard.py`, or `fence/policy.py`.

## Needs-you

The full-suite residual above is a separate command-guard/test-contract mismatch. I did not widen this hotfix into that area.
