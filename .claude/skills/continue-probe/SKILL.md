---
name: continue-probe
description: The firing edge of the session-lifecycle organ (done-line 0135) — resume idle, gateway-eligible sessions with a soft continue-probe. Use to run or inspect the standing watcher tick, to see which idle sessions are due to be nudged, or to wire/understand the external scheduler that ticks it. The pure fold is loop/watcher.py; this skill is the network-reaching pen that actually spawns `claude --resume`. It is dry-run by default and never fires unless asked.
---

# continue-probe — wake an idle session, softly

The session-lifecycle organ in three layers:

1. **Registration** (`.claude/hooks/session_register.py`, `SessionStart`) — every
   new session records `session_id -> {cwd}` into `~/.claude/ontum-sessions.json`.
   This is "enable for all new sessions"; nothing else needs doing per session.
2. **The fold** (`loop/watcher.py`) — pure, stdlib, no network: names which
   registered sessions have been idle past the threshold (transcript mtime is the
   activity signal) AND are gateway-eligible (`loop.retry.gateway_open`, default-
   deny). It emits the exact `claude --resume <id> -p <probe>` command; it never
   spawns it.
3. **The edge** (`probe.py`, this pen) — consumes the fold, budgets which targets
   are *due* (cooldown + a per-streak fire cap, so an away session is never
   hammered), and on `--fire` resumes them. Every firing is traced to
   `.ai-native/log/continue-probe-fires.jsonl` (gitignored — the trust rail).
   The resumed turn lands the soft, gateway-scoped reminder via the idle hook
   (`.claude/hooks/idle_reminder.py` → `loop.retry.compose`).

## Commands

```sh
# read-only: which registered sessions are idle and gateway-eligible
python -m loop.watcher
python -m loop.watcher --json

# dry-run: which idle sessions are DUE to fire right now (writes nothing)
python .claude/skills/continue-probe/probe.py

# fire for real: resume the due sessions (the standing scheduler runs this)
python .claude/skills/continue-probe/probe.py --fire
```

## Two activations (bdo's gestures, not a session's)

The organ is **silent until two stamps**, by design (default-deny everywhere):

1. **Open the gateway** — a continue-probe is denied until bdo admits a policy,
   with a tool-scope (the tier-2 lever; propose-only is the safe floor):

   ```sh
   python -m loop.inference policy --caller session --surface continue-probe \
       --mind '*' --scope propose-only --by bdo
   ```

   Until then the watcher returns nothing and the reminder stays silent, however
   idle a session is. `--scope full` widens a continued session from propose-only
   to executing — bdo's stamp only.

2. **Stand up the standing tick** — register an OS scheduler entry that runs the
   pen every few minutes (no daemon; external scheduling, the daily-digest shape).
   On Windows:

   ```powershell
   schtasks /Create /SC MINUTE /MO 5 /TN ontum-continue-probe ^
     /TR "python C:\Users\bdf19\ontum\.claude\skills\continue-probe\probe.py --fire"
   ```

   (cron elsewhere: `*/5 * * * * cd <repo> && python .claude/skills/continue-probe/probe.py --fire`)

A session that opens here registers itself automatically — layer 1 needs no
gesture. Layers 2–3 wake a *truly away* session; the idle hook alone re-orients a
session resumed by hand. Standing the scheduler up is a per-machine gesture; this
session leaves the pen and the exact command, and does not register OS tasks on
bdo's machine itself.
