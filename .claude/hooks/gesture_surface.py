#!/usr/bin/env python3
"""SessionStart heartbeat: surface bdo's inbound GitHub gestures (done-line 0044).

bdo steers from GitHub — he closes an arc-confirm or realness-confirm issue with
a comment, and that gesture must reach a session **without a daemon and without
a poll** (his call, 2026-06-11: pub/sub on a known event, never a busy loop). The
summon hook is already the heartbeat — SessionStart + UserPromptSubmit injecting
ambient log state. This adds the one missing subscriber: the *inbound* direction.

On session start it asks the intake pens which gesture-issues bdo has closed and
not yet been answered on, and surfaces the count + which skill reads them. It
**judges nothing and acts on nothing** — reading bdo's words is the model's job
(the intake SKILLs), not a hook's; a hook that guessed his intent from keywords
is exactly what the intake doctrine forbids. This only wakes the session to the
fact that he acted; the session runs the skill and decides.

Pub/sub, level-triggered: the closed issue is the topic, the session is the
subscriber, the heartbeat is the known event. The `gh` reach lives here in the
hook layer, never in `loop/` (stdlib-only). **Fail-open and bounded:** no gh, no
auth, no registered surface, or a slow call — the hook stays silent and exits 0,
never delaying or gating a session. A broken sensor must never stand between bdo
and his session.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(os.environ.get("ONTUM_REPO_ROOT") or Path(__file__).resolve().parents[2])
ADMISSIONS = ROOT / ".ai-native" / "log" / "admissions.jsonl"

# the inbound subscribers: (label, pen path relative to root, the skill that reads it)
SUBSCRIBERS = [
    ("realness", ".claude/skills/realness-intake/realness.py", "realness-intake"),
    ("arc", ".claude/skills/arc-intake/intake.py", "arc-intake"),
]


def surface_repo():
    """The registered github-issues address (owner/repo), read from the log —
    latest admission wins, a disabled/null one deregisters. Pure; no network.
    None if nothing is registered (then there is nowhere bdo could have gestured
    and the hook stays silent)."""
    if not ADMISSIONS.exists():
        return None
    repo = None
    try:
        for line in ADMISSIONS.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                a = json.loads(line)
            except ValueError:
                continue
            if a.get("type") == "surface" and a.get("surface") == "github-issues":
                repo = a.get("address") if a.get("enabled", True) else None
    except OSError:
        return None
    return repo


def _pending(rel_pen, repo, timeout=12):
    """Ask one intake pen for the gestures bdo closed and we have not answered.
    Fail-open: any non-JSON / error / timeout yields an empty list, never an
    exception — a sensor that can't read returns 'nothing seen', not a crash."""
    pen = ROOT / rel_pen
    if not pen.exists():
        return []
    try:
        proc = subprocess.run(
            [sys.executable, str(pen), "pending", "--repo", repo, "--json"],
            capture_output=True, text=True, cwd=str(ROOT), timeout=timeout)
    except (subprocess.TimeoutExpired, OSError):
        return []
    for line in reversed((proc.stdout or "").splitlines()):
        line = line.strip()
        if line.startswith("["):
            try:
                return json.loads(line)
            except ValueError:
                return []
    return []


def _one_line(label, item):
    """A cold-reader line for one pending gesture: what bdo is being asked and
    what he said when he closed it (his words are the intent the session reads)."""
    comment = (item.get("comment") or "(closed with no comment)").strip()
    if len(comment) > 160:
        comment = comment[:157] + "…"
    if label == "realness":
        what = f"make {item.get('stage')} real ({item.get('node')})"
    else:
        what = f"confirm {item.get('epic')}"
    return f"  · {label} #{item.get('number')}: {what} — bdo: {comment}"


def format_surface(found):
    """Pure: given {label: [items]}, the wake text the hook injects — or '' when
    nothing waits (silence, never a noisy 'all clear'). Tested directly."""
    total = sum(len(v) for v in found.values())
    if total == 0:
        return ""
    lines = [f"[gesture] bdo acted on GitHub — {total} closed issue(s) await your "
             "reading (the heartbeat, not a poll):"]
    skills = []
    for label, _pen, skill in SUBSCRIBERS:
        items = found.get(label) or []
        if not items:
            continue
        for it in items:
            lines.append(_one_line(label, it))
        skills.append(skill)
    lines.append(f"  → run the {' / '.join(skills)} skill to read his intent and "
                 "act on a clear confirm. Read his words; never act on a guess — "
                 "reopen and ask if it's unclear.")
    return "\n".join(lines)


def main():
    try:
        sys.stdin.read()  # consume the hook event JSON; we don't need it
    except Exception:
        pass
    try:
        repo = surface_repo()
        if repo:
            found = {label: _pending(pen, repo) for label, pen, _skill in SUBSCRIBERS}
            text = format_surface(found)
            if text:
                print(text)
    except Exception:
        pass  # fail-open: a broken heartbeat never gates a session
    return 0


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
