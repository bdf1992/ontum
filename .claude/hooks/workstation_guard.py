#!/usr/bin/env python3
"""PreToolUse guard — a worker writes only inside its OWN workstation.

The workstation write-fence (done-line 0147), tooth #2 of bdo's rule
(2026-06-20): a worker edits only its own workstation (its worktree); reading
and organizing anywhere is fine, but flipping someone else's tree — above all
the viewport — is forbidden. Tooth #1 (the workstation fence, command_guard,
done-line 0145) closed the git HEAD dimension: a worker cannot `git switch`/
`reset`/… the viewport. This is the FILE dimension: a Write/Edit/MultiEdit/
NotebookEdit whose target path lands in a DIFFERENT worktree of the same repo
(a sibling bench, or the primary tree = the viewport) is refused.

The session's own workstation is the worktree containing its payload `cwd`
(NOT os.getcwd(): the harness runs the hook from the project dir — the primary
tree — for every session, so the process cwd is the viewport for all of them;
only the payload knows where the session stands, the way session_register.py
trusts it). A target in no git tree (a temp dir, the memory store) or in an
unrelated repo is not a workstation and is allowed — this guard fences the
benches of one repo against each other, nothing else.

Reads are never touched: this is wired only to the write/edit tools. Stdlib
only. Fails OPEN on its own errors and never gates on a guess — an unguarded
write is the cost of a broken guard, never a blocked one. Deny = exit 2 with
the reason and the paved path on stderr.
"""

from __future__ import annotations

import datetime
import json
import os
import pathlib
import subprocess
import sys

WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}

ROOT = pathlib.Path(os.environ.get("ONTUM_REPO_ROOT")
                    or pathlib.Path(__file__).resolve().parents[2])
WATCH_LOG = pathlib.Path(
    os.environ.get("ONTUM_TOOL_WATCH_LOG",
                   ROOT / ".ai-native" / "log" / "tool-use.jsonl"))


def record(entry):
    """Append a denial to the watch log so an ATTEMPT is witnessed — the
    prerequisite for the trespass shame beat (a denied write is still a
    trespass that tried). Best-effort: a failed write never blocks a turn."""
    entry["ts"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        WATCH_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(WATCH_LOG, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry) + "\n")
    except OSError:
        pass


def _git(args, cwd):
    """git stdout (stripped) run in `cwd`, or None on any failure."""
    try:
        out = subprocess.run(["git", *args], capture_output=True, text=True,
                             timeout=5, cwd=cwd)
    except Exception:
        return None
    return out.stdout.strip() if out.returncode == 0 else None


def _toplevel(cwd):
    out = _git(["rev-parse", "--show-toplevel"], cwd)
    try:
        return pathlib.Path(out).resolve() if out else None
    except Exception:
        return None


def _common_dir(cwd):
    out = _git(["rev-parse", "--git-common-dir"], cwd)
    if not out:
        return None
    try:
        p = pathlib.Path(out)
        if not p.is_absolute():
            p = pathlib.Path(cwd) / p
        return p.resolve()
    except Exception:
        return None


def _nearest_existing(path):
    """Walk up from `path` to the first directory that exists — a target file
    may not exist yet, but git resolves from a real directory."""
    d = path if path.is_dir() else path.parent
    while not d.exists() and d.parent != d:
        d = d.parent
    return d


def foreign_worktree(target, session_cwd):
    """The other-worktree root `target` lives in, or None.

    Foreign = the SAME repo (shared git common-dir) but a DIFFERENT worktree
    than the session's. A target in the session's own tree, in no git tree, or
    in an unrelated repo returns None (not foreign). Fails open to None."""
    tdir = str(_nearest_existing(target))
    t_top = _toplevel(tdir)
    if t_top is None:
        return None  # not inside any git tree — not a workstation
    s_top = _toplevel(session_cwd)
    if s_top is None:
        return None  # can't place the session — never gate on a guess
    if t_top == s_top:
        return None  # the session's own bench
    if _common_dir(tdir) and _common_dir(tdir) == _common_dir(session_cwd):
        return t_top  # same repo, different worktree — foreign
    return None  # a different repo entirely — not ours to fence


def hook():
    try:
        payload = json.loads(sys.stdin.buffer.read().decode("utf-8", "replace"))
    except (json.JSONDecodeError, ValueError):
        return 0
    if payload.get("tool_name") not in WRITE_TOOLS:
        return 0
    tool_input = payload.get("tool_input") or {}
    fp = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    if not fp:
        return 0
    session_cwd = payload.get("cwd") or os.getcwd()
    try:
        # resolve a relative path against the SESSION's cwd, not the process
        # cwd (the project dir) — else a relative file_path from a worktree
        # would mis-resolve into the viewport and false-positive (the review
        # of done-line 0147 caught this; the harness mandates absolute paths,
        # but the guard must not assume it)
        target = pathlib.Path(fp)
        if not target.is_absolute():
            target = pathlib.Path(session_cwd) / target
        target = target.resolve()
        foreign = foreign_worktree(target, session_cwd)
        if foreign is not None:
            record({"status": "denied", "rule": "foreign-worktree",
                    "session": payload.get("session_id") or "",
                    "path": str(target), "foreign": str(foreign)})
            print(
                "denied, firm: this path is in another WORKSTATION "
                f"({foreign}) — a worker writes only inside its OWN worktree "
                "(bdo, 2026-06-20 — the workstation fence). Reading and "
                "organizing another tree is fine; writing into it is not, and "
                "the viewport is no one's bench to edit. Write inside your own "
                "worktree; to move work to another tree, land it through the "
                "loop (PR + merge-node) so every tree fast-forwards to it on "
                "main — never reach into another bench.",
                file=sys.stderr)
            return 2
    except Exception:
        import traceback
        traceback.print_exc(file=sys.stderr)  # fail open, but never silently
        return 0
    return 0


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(hook())
