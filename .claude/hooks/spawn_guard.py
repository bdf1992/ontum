#!/usr/bin/env python3
"""The branded spawn rail (done-line 0026, epic.experience-layer wave 2).

A session fills a loop node by spawning a mind — through the `Agent` tool or a
headless `claude` invocation. Raw, that spawn is anonymous: no prompt pinned,
no rung checked, no trace. This hook (the command_guard pattern, for spawns)
makes a node-spawn declare itself.

A spawn brands itself by naming the node it fills: `ontum-node:<id>` in the
Agent prompt/description, or in the headless `claude` command. When branded,
the rail pins the node's versioned prompt (`prompt_hash`, §7), checks the
spawning class holds the rung the act needs on the trust ladder (D-4), and
records the spawn as provenance — or refuses it (exit 2). An unbranded spawn
is a plain helper, not a node: it passes, watched, and the post hook shames it
once so a node-spawn that forgot its brand surfaces.

The brand lives here under .claude/ (the Agent tool is harness, not stdlib);
loop/ only supplies the read (trust, node_prompt) and never imports this — and
loop is imported lazily, only when a branded spawn is actually seen, so a plain
shell command pays nothing. Stdlib only, fail-open: any error allows the spawn
(a broken rail must never block work).
"""

from __future__ import annotations

import datetime
import json
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
AI_ROOT = ROOT / ".ai-native"  # the records root trust/node_prompt fold over
WATCH_LOG = pathlib.Path(
    os.environ.get("ONTUM_TOOL_WATCH_LOG", AI_ROOT / "log" / "tool-use.jsonl")
)
SPAWN_CLASS = "branded-subagent"   # the class a session spawns into
SPAWN_CAP = "judge"                # what a node-spawn does (a gate judges)
NODE_BRAND = re.compile(r"ontum-node:\s*([a-z0-9][a-z0-9._-]*)", re.I)

# Strip quoted content so a prompt that merely *mentions* `claude` or a brand
# in quotes is not misread as the acting command (command_guard's lesson).
_QUOTED = (
    re.compile(r"@'[\s\S]*?'@"), re.compile(r'@"[\s\S]*?"@'),
    re.compile(r"<<-?\s*'?(\w+)'?[\s\S]*?\n\s*\1\b"),
    re.compile(r"'[^']*'"), re.compile(r'"[^"]*"'),
)


def _strip(command):
    for pattern in _QUOTED:
        command = pattern.sub(" ", command or "")
    return command


_LOOP = {}


def _loop_read():
    """Import loop's read surface (trust, node_prompt) lazily and once — only a
    branded spawn needs it, so plain shell calls never pay the import."""
    if not _LOOP:
        _LOOP["trust"] = _LOOP["node_prompt"] = None
        try:
            sys.path.insert(0, str(ROOT))
            from loop import trust
            from loop.reconcile import node_prompt
            _LOOP["trust"], _LOOP["node_prompt"] = trust, node_prompt
        except Exception:
            pass  # degraded: cannot enforce, so do not block (fail-open)
    return _LOOP["trust"], _LOOP["node_prompt"]


def brand_of(tool_input):
    """The loop node a spawn declares it fills, or None (an unbranded helper).
    Reads the Agent description+prompt or the Bash command."""
    text = " ".join(str(tool_input.get(k) or "")
                    for k in ("description", "prompt", "command"))
    m = NODE_BRAND.search(text)
    return m.group(1) if m else None


def is_headless_claude(command):
    """True when a shell command invokes the `claude` CLI (a headless CC
    spawn), not merely mentions a .claude path."""
    for segment in re.split(r"[|;&\n{}()]+", _strip(command)):
        words = segment.strip().split()
        if not words:
            continue
        head = words[0].strip("'\"").rsplit("/", 1)[-1].rsplit("\\", 1)[-1].lower()
        head = head[:-4] if head.endswith(".exe") else head
        if head == "claude":
            return True
    return False


def node_spawn_refusal(node_id, root=None):
    """Why a branded node-spawn may not proceed, or None. Pure over the log and
    the node prompt, so the suite hits it directly."""
    trust, node_prompt = _loop_read()
    if trust is None or node_prompt is None:
        return None  # degraded: cannot enforce, so do not block
    root = pathlib.Path(root) if root else AI_ROOT
    _, phash = node_prompt(root, node_id)
    if not phash:
        return (f"node {node_id} has no versioned prompt in .ai-native/nodes/ to "
                "pin — a node-spawn must be prompt-pinned to be branded (§7)")
    if not trust.permits(SPAWN_CLASS, SPAWN_CAP, root):
        return (f"{SPAWN_CLASS} holds no '{SPAWN_CAP}' rung — the spawn cannot "
                f"{SPAWN_CAP} until bdo grants it: python -m loop.node admit-rung "
                f"--class {SPAWN_CLASS} --capability {SPAWN_CAP} --by bdo "
                "(the trust ladder gates the spawn, D-4)")
    return None


def _prompt_hash(node_id, root=None):
    _, node_prompt = _loop_read()
    if node_prompt is None:
        return None
    try:
        return node_prompt(pathlib.Path(root) if root else AI_ROOT, node_id)[1]
    except Exception:
        return None


def record(entry):
    entry["ts"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        WATCH_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(WATCH_LOG, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        pass  # the rail never breaks the spawn it watches


def _payload():
    try:
        return json.loads(sys.stdin.buffer.read().decode("utf-8", "replace"))
    except (json.JSONDecodeError, ValueError):
        return None


def _is_spawn(payload):
    """(kind, tool_input) when this tool-use is a spawn, else (None, None).
    A spawn is an Agent tool-use, or a Bash/PowerShell command running
    `claude` headless."""
    tool = payload.get("tool_name")
    tool_input = payload.get("tool_input") or {}
    if tool == "Agent":
        return "agent", tool_input
    if tool in ("Bash", "PowerShell") and is_headless_claude(tool_input.get("command")):
        return "headless", tool_input
    return None, None


def hook():
    payload = _payload()
    if payload is None:
        return 0
    kind, tool_input = _is_spawn(payload)
    if kind is None:
        return 0  # not a spawn — not ours
    session = payload.get("session_id") or ""
    node = brand_of(tool_input)
    if node is None:
        record({"status": "spawn-unbranded", "kind": kind, "session": session})
        return 0
    reason = node_spawn_refusal(node)
    if reason:
        record({"status": "spawn-denied", "kind": kind, "node": node,
                "session": session})
        print(f"denied: branded node-spawn of {node} — {reason}", file=sys.stderr)
        return 2
    record({"status": "spawn", "kind": kind, "node": node,
            "prompt_hash": _prompt_hash(node),
            "subagent_type": tool_input.get("subagent_type"), "session": session})
    return 0


def post():
    """PostToolUse: an unbranded spawn surfaces once per session — if it meant
    to fill a node, it forgot its brand."""
    payload = _payload()
    if payload is None:
        return 0
    kind, tool_input = _is_spawn(payload)
    if kind is None or brand_of(tool_input) is not None:
        return 0
    session = payload.get("session_id") or ""
    seen = 0
    if WATCH_LOG.exists():
        for line in WATCH_LOG.read_text(encoding="utf-8").splitlines():
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if entry.get("status") == "spawn-unbranded" and entry.get("session") == session:
                seen += 1
    if seen > 1:  # the pre hook already logged this one; beyond that, stay quiet
        return 0
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PostToolUse",
        "additionalContext": (
            "[spawn_guard] an unbranded spawn — a plain helper, not a loop node. "
            "If it fills a node, brand it `ontum-node:<id>` so the rail pins the "
            "node's prompt and checks the rung (the trust ladder gates node-spawns). "
            "Unbranded helpers stay raw; this surfaces once so a forgotten brand "
            "doesn't pass silently."
        ),
    }}))
    return 0


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    if "--post" in sys.argv[1:]:
        sys.exit(post())
    sys.exit(hook())
