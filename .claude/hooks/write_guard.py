#!/usr/bin/env python3
"""PreToolUse write guard (done-line 0013): a file lands only where the
place expects it.

Rule 1 — governance (D-9): creating a file requires a governing
CLAUDE.md at or above the target directory *within* the repo; the root
CLAUDE.md governs only the root level, so every subtree earns its own
environment. docs/ has none on purpose — its read-only hard rule
becomes mechanical for sessions.

Rule 2 — records form: a directory carrying `.pen.json` (the control
config) additionally requires the filename pattern, the exact next id,
and the required sections. The refusal names the paved path: the
records pen, loop/pen.py.

Gates sessions, not the owner. Passes untouched: edits to existing
files, dotfiles, new CLAUDE.md files (founding a governed directory),
anything outside the repo. Fails open on its own errors — a broken
guard must never block work it can't even parse. Denials are exit 2
with the reason on stderr, recorded to the watch log (a sensor trace,
gitignored, not truth).
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
NUMBERED = re.compile(r"^(\d{4})-")


def record(entry):
    entry["ts"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        WATCH_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(WATCH_LOG, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        pass  # the watcher never breaks the write it watches


def deny(rule, rel, message):
    record({"status": "denied", "rule": rule, "path": rel})
    print(message, file=sys.stderr)
    return 2


def next_id(dirpath):
    ids = [int(m.group(1)) for p in dirpath.iterdir()
           for m in [NUMBERED.match(p.name)] if m]
    return max(ids) + 1 if ids else 1


def hook():
    try:
        # the harness pipes UTF-8; Windows' default stdin is cp1252 — read
        # bytes, or any non-ASCII payload silently fails the guard open
        payload = json.loads(sys.stdin.buffer.read().decode("utf-8", "replace"))
    except (json.JSONDecodeError, ValueError):
        return 0
    if payload.get("tool_name") != "Write":
        return 0
    tool_input = payload.get("tool_input") or {}
    fp = tool_input.get("file_path") or ""
    content = tool_input.get("content") or ""
    try:
        target = pathlib.Path(fp).resolve()
        root = ROOT.resolve()
        try:
            rel = target.relative_to(root).as_posix()
        except ValueError:
            return 0  # outside the repo: not ours to gate
        if target.exists():
            return 0  # reshaping an existing file is Edit's land, not creation
        name = target.name
        if name.startswith("."):
            return 0  # dotfiles (configs) stay out of the form's way
        d = target.parent

        # the most specific rule first: a records directory's declared form
        cfg_path = d / ".pen.json"
        if cfg_path.exists():
            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
            pen = cfg.get("pen", "python -m loop.pen new <dir> --slug <slug>")
            pattern = cfg.get("pattern")
            if pattern and not re.match(pattern, name):
                return deny("write-form-pattern", rel,
                            f"denied: {name} does not fit this directory's form "
                            f"({pattern}). The paved path: {pen}")
            m = NUMBERED.match(name)
            if m:
                expected = next_id(d)
                if int(m.group(1)) != expected:
                    return deny("write-form-id", rel,
                                f"denied: the next id here is {expected:04d}, not "
                                f"{m.group(1)} — ids come from the fold, not the "
                                f"eyeball (two 0011s taught us). The paved path: {pen}")
            missing = [s for s in cfg.get("required_sections", []) if s not in content]
            if missing:
                return deny("write-form-sections", rel,
                            "denied: required section(s) missing: "
                            f"{', '.join(missing)}. The form is .pen.json; "
                            f"the pen scaffolds it: {pen}")
            return 0  # the control config IS governance: the place declared its form

        if name == "CLAUDE.md":
            return 0  # founding a governed directory is always allowed

        # governance walk: a CLAUDE.md strictly below the root governs its
        # subtree; the root CLAUDE.md governs root-level files only
        if d != root:
            cur, governed = d, False
            while cur != root and cur.parent != cur:
                if (cur / "CLAUDE.md").exists():
                    governed = True
                    break
                cur = cur.parent
            if not governed:
                return deny("write-ungoverned", rel,
                            f"denied: no CLAUDE.md governs {rel} — a file lands "
                            "only where an environment expects it (D-9, done-line "
                            "0013); the root file governs root-level files only. "
                            "Found the subtree (write its CLAUDE.md first) or "
                            "build where one already governs.")
        return 0
    except Exception:
        # fail open — but never silently: an invisible failure here is an
        # unguarded repo that still looks guarded (tonight taught us)
        traceback.print_exc(file=sys.stderr)
        return 0


if __name__ == "__main__":
    sys.exit(hook())
