#!/usr/bin/env python3
"""The file-touch sensor (PostToolUse): which files each session discovers.

Part 2 of the activity-accounting witness (loop/activity.py, done-line 0143),
turned on the file tools. bdo, 2026-06-22: he wants his VS Code viewport to carry
a per-file MASK — which files agents have NOT discovered yet (undiscovered) —
alongside edited/red, which VS Code already paints natively. "Discovered" is the
one axis the harness must collect first: every Read or Edit of a file is the
sensor reading that says an agent's attention reached this path.

This hook is that sensor. On every file-tool use (Read, Edit, MultiEdit,
NotebookEdit) it appends ONE record {ts, session, action, path} to
.ai-native/log/file-touch.jsonl — action "read" for Read, "edit" for the
mutating tools; the path normalized repo-relative when it resolves under the
repo, else absolute. loop/coverage.py folds these into the discovered /
undiscovered set the step-2 VS Code extension will paint.

Declared in .claude/activity-register.json — the §10 teeth of loop.activity
refuse an undeclared collector, so this sensor cannot be wired silently. The sink
is gitignored telemetry, not truth: a sensor trace like tool-use.jsonl,
deletable and rebuilt by replaying sessions.

Fail-open, exit 0 ALWAYS: a sensor bug must never gate a file tool. Stdlib only.
A record with no concrete file_path is skipped — nothing to witness.
"""

from __future__ import annotations

import datetime
import json
import os
import pathlib
import sys

# file_touch.py -> hooks/ -> .claude/ -> repo root. The same `parents[2]` the
# sibling command_guard uses; resolves to the worktree root in a worktree.
ROOT = pathlib.Path(__file__).resolve().parents[2]
TOUCH_LOG = pathlib.Path(
    os.environ.get("ONTUM_FILE_TOUCH_LOG",
                   ROOT / ".ai-native" / "log" / "file-touch.jsonl")
)

# The file tools this sensor reads, mapped to the coverage action. A read is
# discovery without change; an edit is discovery WITH change — VS Code already
# paints the change/red, so this sensor records only THAT the path was reached.
READ_TOOLS = {"Read"}
EDIT_TOOLS = {"Edit", "MultiEdit", "NotebookEdit"}


def action_for(tool_name):
    """"read" for Read, "edit" for the mutating file tools, None otherwise."""
    if tool_name in READ_TOOLS:
        return "read"
    if tool_name in EDIT_TOOLS:
        return "edit"
    return None


def concrete_path(tool_input):
    """The concrete file path a file-tool acted on, or None. Read/Edit/MultiEdit
    carry `file_path`; NotebookEdit carries `notebook_path`. Anything without a
    non-empty string path is skipped (no concrete file_path, no record)."""
    if not isinstance(tool_input, dict):
        return None
    for key in ("file_path", "notebook_path"):
        val = tool_input.get(key)
        if isinstance(val, str) and val.strip():
            return val
    return None


def normalize(path_str):
    """Repo-relative (forward-slash) when the path resolves under the repo, else
    the absolute path. Forward slashes so the discovered set is one vocabulary
    across OSes — git already speaks them, and coverage.py reads tracked paths
    the same way."""
    try:
        resolved = pathlib.Path(path_str).resolve()
    except (OSError, ValueError):
        return path_str
    try:
        return resolved.relative_to(ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()


def record(entry):
    """Append one line-atomic record, ts first. Never raises — the sensor must
    not break the tool it watches (the command_guard watcher's law)."""
    line = {"ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            **entry}
    try:
        TOUCH_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(TOUCH_LOG, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(line, ensure_ascii=False) + "\n")
    except OSError:
        pass  # the sensor never breaks the command it watches


def hook(stdin_text):
    """Parse the PostToolUse stdin, and for a file tool with a concrete path,
    append one {ts, session, action, path} record. Returns 0 always."""
    try:
        payload = json.loads(stdin_text)
    except (json.JSONDecodeError, ValueError):
        return 0
    if not isinstance(payload, dict):
        return 0
    action = action_for(payload.get("tool_name"))
    if action is None:
        return 0
    path = concrete_path(payload.get("tool_input") or {})
    if path is None:
        return 0  # no concrete file_path — nothing to witness
    record({
        "session": payload.get("session_id") or "",
        "action": action,
        "path": normalize(path),
    })
    return 0


def main():
    try:
        stdin_text = sys.stdin.buffer.read().decode("utf-8", "replace")
    except Exception:  # noqa: BLE001 — fail-open: a read error never gates a tool
        return 0
    try:
        return hook(stdin_text)
    except Exception:  # noqa: BLE001 — any sensor bug fails open, exit 0 always
        return 0


if __name__ == "__main__":
    sys.exit(main())
