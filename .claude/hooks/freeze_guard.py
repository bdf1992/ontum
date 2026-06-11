#!/usr/bin/env python3
"""PreToolUse freeze guard (done-line 0033): a written done-line is a
contract, and a contract is not edited in place.

A done-line is written *before* the work (§9.4) — it is the bar you set
for yourself. The log's own rule is "never edit a line, only append";
this guard extends that rule to the done directory. Codex, mid-overnight
loop, edited its own done-line to add an exhaustion clause — moving the
bar instead of meeting it. That edit is exactly what this guard refuses.

Mechanism: a records directory declares itself frozen in its `.pen.json`
(`"frozen": true`). Any *existing* file in that directory whose name
fits the directory's `pattern` is then immutable to a session — Edit
and Write (overwrite) are denied, absolutely, with no owner exception.
The way to change what "done" meant is never in place: it is the
additive, owner-gated supersede ritual the refusal names
(`.pen.json`'s `change_request` story; `loop.pen supersede-done`).

Gates sessions; passes everything that is not a frozen record:
creation (no existing file — that is write_guard's land), files in
unfrozen directories, dotfiles/config (the `.pen.json` itself is not a
record), anything outside the repo, and garbage stdin. Fails open on
its own errors — a broken guard must never block work it can't parse —
but never silently: an invisible failure here is an unguarded repo that
still looks guarded (write_guard learned this first). Denials are exit 2
with the loud reason on stderr, recorded to the gitignored watch log.
"""

import datetime
import json
import os
import pathlib
import re
import sys
import traceback

ROOT = pathlib.Path(os.environ.get("ONTUM_REPO_ROOT")
                    or pathlib.Path(__file__).resolve().parents[2])
WATCH_LOG = pathlib.Path(
    os.environ.get("ONTUM_TOOL_WATCH_LOG", ROOT / ".ai-native" / "log" / "tool-use.jsonl")
)
# the tools that change a file in place; Write overwrites, Edit/MultiEdit
# patch, NotebookEdit reshapes a cell — all of them mutate an existing file
EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}


def record(entry):
    entry["ts"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        WATCH_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(WATCH_LOG, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        pass  # the watcher never breaks the write it watches


def deny(rel, message):
    record({"status": "denied", "rule": "frozen-record", "path": rel})
    print(message, file=sys.stderr)
    return 2


def hook():
    try:
        # the harness pipes UTF-8; Windows' default stdin is cp1252 — read
        # bytes, or any non-ASCII payload silently fails the guard open
        payload = json.loads(sys.stdin.buffer.read().decode("utf-8", "replace"))
    except (json.JSONDecodeError, ValueError):
        return 0
    if payload.get("tool_name") not in EDIT_TOOLS:
        return 0
    tool_input = payload.get("tool_input") or {}
    fp = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    if not fp:
        return 0
    try:
        target = pathlib.Path(fp).resolve()
        root = ROOT.resolve()
        try:
            rel = target.relative_to(root).as_posix()
        except ValueError:
            return 0  # outside the repo: not ours to gate
        if not target.exists():
            return 0  # creation, not mutation — that is write_guard's land
        cfg_path = target.parent / ".pen.json"
        if not cfg_path.exists():
            return 0  # no declared form here, nothing to freeze
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        if not cfg.get("frozen"):
            return 0  # the directory has a form but did not declare itself frozen
        pattern = cfg.get("pattern")
        if pattern and not re.match(pattern, target.name):
            return 0  # not one of the records the form governs (e.g. the config)
        story = cfg.get("change_request") or (
            "This record is frozen — it is not edited in place. The directory's "
            ".pen.json declares the additive path that changes it."
        )
        return deny(rel,
                    f"denied, frozen: {rel} is a written {cfg.get('kind', 'record')} "
                    "and cannot be edited in place — moving the bar is not meeting "
                    f"it.\n\n{story}")
    except Exception:
        # fail open — but loudly: a silent failure here is an unguarded repo
        # that still looks guarded
        traceback.print_exc(file=sys.stderr)
        return 0


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(hook())
