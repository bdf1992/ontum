#!/usr/bin/env python3
"""UserPromptSubmit shame beat — a trespass against a workstation is shamed
even though it was denied (done-line for tooth #3).

The two fences refuse a worker that tries to flip the viewport's HEAD
(command_guard, rule `viewport-flip`, done-line 0145) or write into a tree that
isn't its own (workstation_guard, rule `foreign-worktree`, done-line 0147). The
deny is the wall; this beat is the social signal that you tried to climb it
(bdo, 2026-06-20: "it's shamed if it's attempted"). A blocked attempt is still
an attempt, and a worker that keeps reaching for a foreign bench should hear it
get louder until it stops and works in its own worktree.

Pure fold over the append-only watch log (`.ai-native/log/tool-use.jsonl`) — the
attempts are witnessed there (command_guard already records its viewport-flip
denials; workstation_guard now records its foreign-worktree denials too). The
shame is keyed to THIS session (the one being prompted) and grows with the
count of NEW attempts since the last beat; it goes quiet the moment the session
stops trespassing. The per-session high-water mark is gitignored nag state
(`.ai-native/trespass-shame.json`) — the watch log is the truth. Fail-open,
exit 0 always — a broken shame beat must never block the owner's prompt.
"""

import json
import os
import pathlib
import sys

TRESPASS_RULES = {"viewport-flip", "foreign-worktree"}
STATE = ".ai-native/trespass-shame.json"


def project_root():
    return pathlib.Path(os.environ.get("ONTUM_REPO_ROOT")
                        or pathlib.Path(__file__).resolve().parents[2])


def watch_log(ai_native):
    return pathlib.Path(os.environ.get("ONTUM_TOOL_WATCH_LOG",
                                       ai_native / "log" / "tool-use.jsonl"))


def trespass_count(log_path, session):
    """This session's witnessed trespass attempts — a denied viewport-flip or
    foreign-worktree act on the watch log. Torn/garbage lines never happened."""
    n = 0
    if not log_path.exists():
        return 0
    for line in log_path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        if (e.get("status") == "denied" and e.get("rule") in TRESPASS_RULES
                and e.get("session") == session):
            n += 1
    return n


def seen_before(state_path, session):
    try:
        return int(json.loads(state_path.read_text(encoding="utf-8")).get(session, 0))
    except (OSError, ValueError, json.JSONDecodeError):
        return 0


def remember(state_path, session, count):
    try:
        data = json.loads(state_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            data = {}
    except (OSError, ValueError, json.JSONDecodeError):
        data = {}
    data[session] = count
    try:
        state_path.write_text(json.dumps(data), encoding="utf-8")
    except OSError:
        pass  # nag state; failing to persist never blocks a turn


def banner(total, new):
    """Louder the more a session reaches for a tree that isn't its own."""
    if total <= 2:
        return (f"[trespass-shame] this session tried to flip or write a tree "
                f"that isn't its own ({new} new this turn, {total} so far) — and "
                "the fence refused it. A worker edits only its OWN workstation.")
    if total <= 6:
        return (f"[trespass-shame] {total} blocked trespasses this session "
                f"({new} new). You keep reaching into the viewport or another "
                "bench. Stop — make your own worktree and work there.")
    return (f"[TRESPASS-SHAME] {total} TIMES this session has tried to flip or "
            f"write a foreign tree ({new} new this turn). Every one was denied. "
            "This is the shape of a worker editing the wrong tree — STOP and "
            "move to your own bench before anything else.")


def scream(total, new):
    print(banner(total, new))
    print("[trespass-shame] make your workstation and work inside it:")
    print("  git worktree add -b claude/<slug> ../ontum-wt/<slug> origin/main")
    print("  (to advance the viewport to the trunk, the one move is: "
          "python .claude/skills/branch-ritual/git.py sync)")


def main():
    try:
        payload = json.loads(sys.stdin.buffer.read().decode("utf-8", "replace"))
    except (json.JSONDecodeError, ValueError):
        return 0
    try:
        session = payload.get("session_id") or ""
        if not session:
            return 0
        ai_native = project_root() / ".ai-native"
        total = trespass_count(watch_log(ai_native), session)
        state_path = ai_native / "trespass-shame.json"
        prior = seen_before(state_path, session)
        if total > prior:                     # new attempts this turn → shame
            scream(total, total - prior)
        remember(state_path, session, total)  # quiet once it stops trying
    except Exception:
        pass  # fail-open: a broken shame beat never blocks the owner's prompt
    return 0


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
