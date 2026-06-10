#!/usr/bin/env python3
"""PreToolUse guard and watcher — raw external commands are gated and seen.

Done-line 0011 / branch-ritual v0.3.0. Two jobs, one hook:

1. Guard: the firm rules are denied outright (exit 2) — raw `gh pr`
   mutations go through the pen (.claude/skills/branch-ritual/pr.py),
   nothing pushes to the trunk, no one merges or approves their own
   line. The deny-list is this file; tightening it is adding a rule.

2. Watcher: every other raw invocation of an external tool (gh, curl,
   network git, ...) is allowed but recorded to the watch log
   (.ai-native/log/tool-use.jsonl — a sensor trace, gitignored and
   deletable, not truth). `--report` folds the log into counts: the
   heaviest unwrapped tool is the next wrapper worth building. We only
   build what we use.

3. Shame (`--post`, a PostToolUse hook): using the generic brand when
   no branded wrapper exists gets called out *in the context window*
   via additionalContext — once per tool per session, with the running
   audit count. Surfaced, it becomes a judgment call (mint the wrapper
   or keep it raw); never surfaced, it stays silent. That asymmetry is
   the point.

Stdlib only. As a hook it reads the PreToolUse JSON on stdin and exits
0 (allow) or 2 (deny, stderr explains). Run `--report` by hand or
during branch gardening.
"""

from __future__ import annotations

import datetime
import json
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
WATCH_LOG = pathlib.Path(
    os.environ.get("ONTUM_TOOL_WATCH_LOG", ROOT / ".ai-native" / "log" / "tool-use.jsonl")
)
PEN = "python .claude/skills/branch-ritual/pr.py"

DENY_RULES = (
    ("gh-pr-create", r"\bgh\s+pr\s+create\b",
     "raw `gh pr create` is denied (branch-ritual): every PR to main carries "
     f"a validated story. Use the pen: {PEN} create ... (-h lists the required fields)"),
    ("gh-pr-edit", r"\bgh\s+pr\s+edit\b",
     "raw `gh pr edit` is denied (branch-ritual): reshape the story through "
     f"the pen: {PEN} edit <number> ..."),
    ("gh-pr-merge", r"\bgh\s+pr\s+merge\b",
     "denied, firm: never merge your own PR — the stamp is bdo's (branch-ritual)."),
    ("gh-pr-close", r"\bgh\s+pr\s+(close|reopen)\b",
     "denied: opening and closing PRs is ritual work — surface it to bdo "
     "instead of doing it raw."),
    ("gh-pr-review", r"\bgh\s+pr\s+review\b",
     "denied: no one signs their own line (CLAUDE.md) — a session does not "
     "review or approve PRs."),
)

# Heads that stay invisible to the watcher: local work, not external reach.
LOCAL_HEADS = {
    "python", "python3", "py", "cd", "ls", "dir", "cat", "type", "echo",
    "head", "tail", "grep", "rg", "find", "findstr", "sed", "awk", "sort",
    "wc", "tee", "jq", "mkdir", "rm", "cp", "mv", "touch", "pwd", "set",
    "export", "if", "for", "while", "do", "then", "else", "fi", "true",
    "false", "test", "exit", "select-object", "get-content", "get-childitem",
    "test-path", "write-output", "measure-object", "out-null",
}
GIT_NETWORK = {"push", "fetch", "pull", "clone", "remote", "ls-remote"}


def pushes_to_trunk(command):
    """True when a `git push` names main/master, in any refspec spelling."""
    for match in re.finditer(r"\bgit\s+push\b([^|;&\n]*)", command):
        for token in match.group(1).split():
            token = token.strip("'\"")
            if token in ("main", "master"):
                return True
            if re.fullmatch(r"[^:\s]*:(main|master)", token):
                return True
    return False


def external_bins(command):
    """The external tool heads a command reaches for, in order, deduped.

    Splits on shell joiners, takes each segment's first word, strips
    paths/.exe, and keeps what is neither local work nor plain local
    git. Heuristic by design — the watcher is a sensor, not a parser.
    """
    seen, found = set(), []
    for segment in re.split(r"[|;&\n]+", command):
        words = segment.strip().split()
        if not words:
            continue
        head = words[0].strip("'\"").rsplit("/", 1)[-1].rsplit("\\", 1)[-1].lower()
        head = head[:-4] if head.endswith(".exe") else head
        if head in LOCAL_HEADS or not re.fullmatch(r"[a-z][a-z0-9._-]*", head):
            continue
        if head == "git":
            sub = next((w for w in words[1:] if not w.startswith("-")), "")
            if sub not in GIT_NETWORK:
                continue
        if head not in seen:
            seen.add(head)
            found.append(head)
    return found


def record(entry):
    entry["ts"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        WATCH_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(WATCH_LOG, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        pass  # the watcher never breaks the command it watches


def _payload():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return None
    if payload.get("tool_name") not in ("Bash", "PowerShell"):
        return None
    return payload


def hook():
    payload = _payload()
    if payload is None:
        return 0
    command = (payload.get("tool_input") or {}).get("command") or ""
    session = payload.get("session_id") or ""

    for rule, pattern, message in DENY_RULES:
        if re.search(pattern, command):
            record({"status": "denied", "rule": rule, "command": command,
                    "session": session})
            print(message, file=sys.stderr)
            return 2
    if pushes_to_trunk(command):
        record({"status": "denied", "rule": "git-push-trunk",
                "command": command, "session": session})
        print(
            "denied, firm: never push to main — push the session's claude/* "
            "branch and PR it through the pen (branch-ritual).",
            file=sys.stderr,
        )
        return 2

    bins = external_bins(command)
    if bins:
        record({"status": "watched", "bins": bins, "command": command,
                "session": session})
    return 0


def _fold_counts(session):
    """Total and this-session use per tool, from the watch log."""
    total, in_session = {}, {}
    if WATCH_LOG.exists():
        for line in WATCH_LOG.read_text(encoding="utf-8").splitlines():
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue  # torn tail: it never happened
            if entry.get("status") != "watched":
                continue
            for bin_ in entry.get("bins", []):
                total[bin_] = total.get(bin_, 0) + 1
                if session and entry.get("session") == session:
                    in_session[bin_] = in_session.get(bin_, 0) + 1
    return total, in_session


def post():
    """PostToolUse: shame unbranded tool use into the context window."""
    payload = _payload()
    if payload is None:
        return 0
    command = (payload.get("tool_input") or {}).get("command") or ""
    bins = external_bins(command)
    if not bins:
        return 0
    session = payload.get("session_id") or ""
    total, in_session = _fold_counts(session)
    # The PreToolUse watcher already logged this very call, so a tool's
    # first use this session folds to 1. Beyond that it has been
    # surfaced — stay silent.
    fresh = [b for b in bins if in_session.get(b, 1) <= 1]
    if not fresh:
        return 0
    uses = ", ".join(f"`{b}` ×{total.get(b, 1)}" for b in fresh)
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PostToolUse",
        "additionalContext": (
            f"[command_guard] unbranded tool use, on the audit record: {uses}. "
            "No branded wrapper exists for this yet — the only branded verb "
            "set is the PR pen (.claude/skills/branch-ritual/pr.py). The "
            "ritual prefers branded tools over the generic brand: if this "
            "tool keeps recurring, surface it to bdo and mint its wrapper "
            "(`python .claude/hooks/command_guard.py --report` for the fold). "
            "Surfaced, it is a judgment call; unsurfaced, it stays silent."
        ),
    }}))
    return 0


def report():
    """Fold the watch log: which raw tools are actually in use."""
    counts, examples, denied = {}, {}, 0
    if WATCH_LOG.exists():
        for line in WATCH_LOG.read_text(encoding="utf-8").splitlines():
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue  # torn tail: it never happened
            if entry.get("status") == "denied":
                denied += 1
                continue
            for bin_ in entry.get("bins", []):
                counts[bin_] = counts.get(bin_, 0) + 1
                examples.setdefault(bin_, entry.get("command", "")[:100])
    if not counts:
        print(f"result: done — no unwrapped external use on record ({denied} denial(s))")
        return 0
    for bin_, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"{bin_}: {n} raw call(s) — e.g. {examples[bin_]}")
    print(
        f"result: report — {len(counts)} unwrapped tool(s) in use "
        f"({denied} denial(s)); the heaviest is the next wrapper worth building"
    )
    return 0


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    if "--report" in sys.argv[1:]:
        sys.exit(report())
    elif "--post" in sys.argv[1:]:
        sys.exit(post())
    else:
        sys.exit(hook())
