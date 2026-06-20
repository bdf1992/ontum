# Report 0099 — The production session-lifecycle organ — every new session registered, watched, softly continued within a tool-scoped gateway

## What landed

Tier-1 production of the continue-probe lift (memory `ontum-continue-probe-session-lifecycle`; done-line 0135), backed by `atom.session-lifecycle-gateway.v0` and an **independent** value-gate receipt `rcp.8c7e1ea8939a` (D-2: a separate branded node `ontum-node:value-gate.claude.v1` read the work, ran 62 tests itself, verified the teeth / default-deny / no-network / clean retirement, and accepted — I authored it, so I did not judge it). Full suite green at **1058**.

**The retirement.** The continue-beat (done-line 0127) — a `Stop`-hook that *forced* a session to continue every turn, blind to whether bdo is present — is retired. `.claude/hooks/continue_beat.py` is deleted and unwired from `Stop`; `loop/patrol.py` is slimmed from the forcing `decide` fold down to the **escalate marker** it always carried (the part the new soft organ composes), its state file renamed `continue-beat.json` -> `patrol.json`. `tests/test_patrol.py` rewritten to the surviving marker. The done-line 0127 stands as history.

**The production organ (three layers, replacing the block):**
- **Registration** — `.claude/hooks/session_register.py` (`SessionStart`) records `session_id -> {cwd}` into `~/.claude/ontum-sessions.json` for EVERY new session, pruning the dead. This is "enable for all new sessions": no per-session wire, just opening here. The pure add-and-prune is `loop.watcher.register_session` (tested).
- **The fold** — `loop/watcher.py`: pure, stdlib, no-network. `idle_sessions(now, registry, gateway, mtime)` names which registered sessions are idle past threshold (transcript mtime is the activity signal) AND gateway-eligible (default-deny), emitting the exact `claude --resume <id> -p <probe>` command without ever spawning it.
- **The edge** — `.claude/skills/continue-probe/probe.py` (+ SKILL): consumes the fold, budgets which targets are *due* (`due_targets`: cooldown + a per-streak fire cap with a reset-on-activity, so an away session is never hammered), and on `--fire` resumes them, tracing each firing. Dry-run by default. The standing tick is an external OS scheduler entry (no daemon — the daily-digest shape).
- **The soft reminder** — `loop/retry.py` + `.claude/hooks/idle_reminder.py` (`UserPromptSubmit`): injects a gateway-bounded, session-first, **decaying** suggestion the agent reads and decides on — never a `decision: block`.

**The gateway tool-scope (the tier-2 lever).** Proven empirically: a resumed session is tool-permission-gated — it can *propose/draft* but not *execute*. So `loop/inference.py` policy records gain a `scope` (`propose-only` | `full`, default `propose-only`); `inference.policy_scope(...)` returns the granted scope or `None` (default-deny honoured); `loop.retry.compose` reads it and NAMES it in the reminder (propose-only forbids execution; full permits). A permit alone no longer licenses a continued session to act.

**The §10 teeth.** A constant decider fails everywhere: `test_watcher` (active excluded / idle-in-window included / gateway-closed excluded / presumed-closed not resurrected / exact resume argv / register add-and-prune), `test_retry` (each silence condition / session-first content / the named scope changes the reminder / decay), `test_gateway` TestPolicyScope (denied->None, permit->propose-only, explicit full, deny overrides, bad scope refused), `test_continue_probe` (cooldown / cap / streak-reset), `test_patrol` (the marker is derived, both states reachable).

## needs-you

Two activation gestures — the organ is **silent until both**, by design (default-deny everywhere). Neither is a chore; each is one gesture, and the work is preserved waiting on it:

1. **Open the gateway** (one stamp, sets the tool-scope): `python -m loop.inference policy --caller session --surface continue-probe --mind "*" --scope propose-only --by bdo`. Until then the watcher returns nothing and the reminder stays silent, however idle a session is. `--scope full` would let a continued session execute, not just propose — propose-only is the safe floor.
2. **Stand up the standing tick** — register an OS scheduler entry that runs `probe.py --fire` every few minutes (Windows `schtasks` / cron; the exact command is in `.claude/skills/continue-probe/SKILL.md`). This is a per-machine gesture; a session does not register OS tasks on bdo's machine. The idle hook alone already re-orients a session resumed by hand — the scheduler is what reaches a *truly away* session.

**Note (not a needs-you):** `epic.owner-harness` is already confirmed (the atom serves it), so the PR is merge-node-eligible once green; the merge-node lands it. No merge gesture from bdo.

## Deferred — the named next increment

The **observation / tier-3 lift** (memory's second lift): the session-lifecycle as an OBSERVED fold (a sibling of census/retro/heal/reflect in the regulatory branch, [[ontum-gateway-separation-of-powers]]) plus an inferring management agent that reads a session's state and recommends close / compact / escalate. This atom lands the *capability*; the realization (use-traces) and the observation lift are the next done-lines, not this bar. (`/compact` from headless is still unverified — test before relying.)

## End-state

`report` — tier-1 production is built, tested (1058 green), dogfooded (atom + independent value-gate `rcp.8c7e1ea8939a`), and ready as a PR under the confirmed `epic.owner-harness`. The continue-beat block is retired; every new session now registers itself for the watch. The organ is inert until bdo opens the gateway policy and stands up the scheduler — both named above. The observation/tier-3 lift is the next increment.
