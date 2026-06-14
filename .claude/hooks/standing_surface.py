#!/usr/bin/env python3
"""SessionStart + UserPromptSubmit heartbeat: the standing open work on a
registered surface, ambient at every wake (done-line 0071).

The inbound twin of the reflector. `gesture_surface.py` wakes a session to the
fact that bdo *acted* (closed a confirm issue); this wakes it to the standing
*open work* a registered surface holds — issues and PRs for `github-issues` —
so a session no longer learns the surface state only when a human pastes a
screenshot. The pure projection is `loop/standing.py` (stdlib, vendor-free);
this layer is the part that may touch the network: the adapter that turns a
live surface into a normalized snapshot, the per-session baseline, and the
throttle. GitHub is not glued into the projection — it is one entry in the
adapter table, keyed by surface kind, exactly as the reflector pen's
translator is keyed by `SURFACE_KINDS`.

Two events, one script (Claude Code passes the event name on stdin):
  - SessionStart    -> the full standing picture, and (re)seed the baseline.
  - UserPromptSubmit -> the delta only, and only past the throttle window, so
                        a change ticks up once without taxing every turn or
                        re-printing the list (bdo's 'tick up, not spam').

Pub/sub, level-triggered, no daemon: the surface is the topic, the session is
the subscriber, the wake is the known event, the baseline is the ack, the
delta is the unconsumed change. **Fail-open and bounded:** no gh, no auth, no
registered surface, an unknown surface kind, or a slow call -> the hook stays
silent (the SessionStart picture may name an adapterless surface, never guess
it) and exits 0. A broken sensor must never stand between bdo and his session.
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(os.environ.get("ONTUM_REPO_ROOT") or Path(__file__).resolve().parents[2])
ADMISSIONS = ROOT / ".ai-native" / "log" / "admissions.jsonl"
STATE = ROOT / ".ai-native" / "standing-state.json"

# The per-prompt poll is throttled to this window: most UserPromptSubmit turns
# skip the network entirely and stay log-fast; a change still ticks up within
# one window. A hook-layer constant for now (config, not loop/) — it can
# graduate to an admitted dial when a second surface needs a different cadence.
POLL_THROTTLE_SECONDS = 90

# ensure `import loop.standing` resolves to THIS tree's package (the pure
# projection); the hook runs as a script, so the repo root is not yet on path.
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def registered_github_surface():
    """The seam reuse: the registered `github-issues` surface (id, kind,
    address), folded from the same admissions reflect reads — latest wins, a
    null address deregisters. Returns (surface_id, kind, address) or None.
    Hand-folded (no loop import) to keep the hook light and path-robust, but
    semantically identical to reflect.registered_surfaces."""
    if not ADMISSIONS.exists():
        return None
    chosen = None
    try:
        for line in ADMISSIONS.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                a = json.loads(line)
            except ValueError:
                continue
            if a.get("type") == "surface" and a.get("surface"):
                if a.get("address"):
                    chosen = (a["surface"], a.get("kind"), a["address"])
                elif chosen and chosen[0] == a["surface"]:
                    chosen = None  # deregistered
    except OSError:
        return None
    return chosen


def _gh_json(args, timeout):
    proc = subprocess.run(args, capture_output=True, text=True,
                          cwd=str(ROOT), timeout=timeout)
    if proc.returncode != 0:
        return []
    data = json.loads(proc.stdout or "[]")
    return data if isinstance(data, list) else []


def _github_issues_snapshot(address, timeout=12):
    """Adapter: a live `github-issues` surface -> a normalized snapshot the
    pure projection folds. The ONLY place the gh reach lives. `gh issue list`
    excludes PRs already; PRs come from `gh pr list` and carry their branch."""
    items = []
    for it in _gh_json(["gh", "issue", "list", "--repo", address, "--state",
                        "open", "--json", "number,title", "--limit", "100"],
                       timeout):
        items.append({"kind": "issue", "number": it.get("number"),
                      "title": it.get("title", "")})
    for pr in _gh_json(["gh", "pr", "list", "--repo", address, "--state", "open",
                        "--json", "number,title,headRefName", "--limit", "100"],
                       timeout):
        items.append({"kind": "pr", "number": pr.get("number"),
                      "title": pr.get("title", ""),
                      "branch": pr.get("headRefName", "")})
    return items


# The adapter table — the 'not glued to GitHub' seam. A surface kind with no
# entry here is named at SessionStart, never guessed (reflect's discipline).
ADAPTERS = {"github-issues": _github_issues_snapshot}


def _read_state():
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _write_state(state):
    try:
        STATE.write_text(json.dumps(state), encoding="utf-8")
    except OSError:
        pass  # ephemeral UI state; losing it just re-seeds next wake


def _session_id(event):
    return str(event.get("session_id") or "default")


def _event_name(event):
    # Claude Code passes the event name; be tolerant of either key/casing.
    return event.get("hook_event_name") or event.get("hookEventName") or ""


def run(event, now):
    """The decision, given the parsed hook event and a clock reading — kept
    separate from main() so the throttle/baseline logic is exercisable. Returns
    the text to print (possibly '') and never raises for an expected miss."""
    import loop.standing as standing  # the pure projection (this tree's copy)

    surface = registered_github_surface()
    if not surface:
        return ""  # nowhere registered -> silent, never a guess
    surface_id, kind, address = surface
    event_name = _event_name(event)
    is_start = event_name == "SessionStart"

    adapter = ADAPTERS.get(kind)
    if adapter is None:
        # named at start (so the gap is visible), silent thereafter
        if is_start:
            return (f"[standing] {surface_id} is registered as kind {kind!r}, "
                    f"which has no adapter — its open work is not projected "
                    f"(a new kind is a new adapter, never a gh-shaped guess)")
        return ""

    state = _read_state()
    sid = _session_id(event)
    mine = state.get(sid) or {}

    if not is_start:
        # throttle: skip the network unless the window has elapsed
        last = mine.get("last_poll", 0)
        if now - last < POLL_THROTTLE_SECONDS:
            return ""

    try:
        items = adapter(address)
    except (subprocess.TimeoutExpired, OSError, ValueError):
        return ""  # a sensor that can't read says nothing, never crashes

    ids = standing.snapshot_ids(items)
    if is_start:
        text = standing.format_standing(surface_id, items)
    else:
        delta = standing.compute_delta(mine.get("baseline", []), items)
        text = standing.format_delta(surface_id, delta)

    state[sid] = {"baseline": ids, "last_poll": now}
    _write_state(state)
    return text


def main():
    try:
        raw = sys.stdin.read()
    except Exception:
        raw = ""
    try:
        event = json.loads(raw) if raw.strip() else {}
    except ValueError:
        event = {}
    try:
        text = run(event, time.time())
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
