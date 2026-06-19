#!/usr/bin/env python3
"""PreToolUse change-management guard (arc.aim): a protected experience
surface may not land an edit that DROPS a pinned feature.

bdo's lesson: a session forked a feature-poor compare.html from
experience.html (no slider, skin, hover, gestures) — a regression that a
change-management policy node exists to refuse. Pinning the exemplar
(aim-exemplars.md) without the gate that enforces it is no protection;
this is the gate. It is the BITE-axis sibling of mock_shame and the retro
fold: shame senses stalling, retro senses churn, this senses a good
surface QUIETLY LOSING what it had.

Mechanism: the DON'T-REGRESS invariants live in one registry,
`causality/change-policy.invariants.json` (shared with the JS judge
`causality/change_policy.js` so the two never drift — the fence-registry
pattern). On a Write/Edit/MultiEdit to a `protectedSurfaces` file, the
guard reconstructs the post-edit text and checks every required feature's
markers are still present. A dropped feature is denied (exit 2, the loud
reason on stderr); everything else passes.

Adding features is fine (amplify); only LOSING one bites. A deliberate
retirement edits the registry itself, on the record — bdo's call, never a
silent drop. Fails open on its own errors, but loudly — an invisible
failure here is an unguarded surface that still looks guarded.
"""

import datetime
import json
import os
import pathlib
import sys
import traceback

ROOT = pathlib.Path(os.environ.get("ONTUM_REPO_ROOT")
                    or pathlib.Path(__file__).resolve().parents[2])
WATCH_LOG = pathlib.Path(
    os.environ.get("ONTUM_TOOL_WATCH_LOG", ROOT / ".ai-native" / "log" / "tool-use.jsonl")
)
REGISTRY = ROOT / "causality" / "change-policy.invariants.json"
EDIT_TOOLS = {"Edit", "Write", "MultiEdit"}


def record(entry):
    entry["ts"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        WATCH_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(WATCH_LOG, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        pass


def deny(rel, dropped):
    record({"status": "denied", "rule": "change-policy", "path": rel,
            "dropped": [d["id"] for d in dropped]})
    lines = [
        f"denied, regression: {rel} would drop {len(dropped)} pinned "
        "experience invariant(s) — a surface may not quietly lose what it had.",
        "",
    ]
    for d in dropped:
        lines.append(f"  ✗ {d['id']} — {d.get('why', '')}")
    lines += [
        "",
        "Fix the surface so the feature stays (do not fork a poorer one). A "
        "deliberate retirement edits causality/change-policy.invariants.json, "
        "on the record — bdo's call.",
    ]
    print("\n".join(lines), file=sys.stderr)
    return 2


def post_text(tool_name, tool_input, current):
    """The text the surface would have AFTER this tool call."""
    if tool_name == "Write":
        return tool_input.get("content", "")
    text = current
    if tool_name == "Edit":
        edits = [tool_input]
    else:  # MultiEdit
        edits = tool_input.get("edits", []) or []
    for e in edits:
        old, new = e.get("old_string", ""), e.get("new_string", "")
        if old == "":
            continue
        text = text.replace(old, new) if e.get("replace_all") else text.replace(old, new, 1)
    return text


def hook():
    try:
        payload = json.loads(sys.stdin.buffer.read().decode("utf-8", "replace"))
    except (json.JSONDecodeError, ValueError):
        return 0
    if payload.get("tool_name") not in EDIT_TOOLS:
        return 0
    tool_input = payload.get("tool_input") or {}
    fp = tool_input.get("file_path") or ""
    if not fp:
        return 0
    try:
        root = ROOT.resolve()
        try:
            rel = pathlib.Path(fp).resolve().relative_to(root).as_posix()
        except ValueError:
            return 0  # outside the repo
        reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
        protected = set(reg.get("protectedSurfaces") or [])
        if rel not in protected:
            return 0  # not a guarded surface
        required = reg.get("required") or []
        target = pathlib.Path(fp).resolve()
        current = target.read_text(encoding="utf-8") if target.exists() else ""
        text = post_text(payload["tool_name"], tool_input, current)
        dropped = [f for f in required if not all(m in text for m in f.get("markers", []))]
        if dropped:
            return deny(rel, dropped)
        return 0
    except Exception:
        traceback.print_exc(file=sys.stderr)  # fail open, loudly
        return 0


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(hook())
