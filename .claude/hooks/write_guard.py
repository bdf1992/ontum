#!/usr/bin/env python3
"""PreToolUse write guard (done-line 0013): a file lands only where the
place expects it.

Rule 1 — governance (D-9): creating a file requires a governing
CLAUDE.md at or above the target directory *within* the repo; the root
CLAUDE.md governs only the root level, so every subtree earns its own
environment. docs/ has none on purpose — its read-only hard rule
becomes mechanical for sessions.

Rule 2 — records carbon copy (done-line 0070): a directory carrying
`.pen.json` (the control config) is the records pen's land. A raw Write
here is allowed only as a faithful CARBON COPY of what the pen would
have produced for that filename — fleet-safe id, the pen's heading, the
required sections, LF/UTF-8 newline-terminated bytes. The single
definition of a carbon copy is `loop.pen.carbon_divergences`, imported
here so the pen and the guard never disagree (I-4); a divergent write is
refused with the divergences named — the refusal IS the fail
notification — and the paved path (the pen, loop/pen.py) offered.

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

try:  # the cross-ref fold lives beside this hook (done-line 0023); fail open
    import placement as _placement
except Exception:
    _placement = None

# The one definition of "a faithful pen carbon copy" lives in the records pen
# (loop/pen.py, done-line 0070); the guard imports it so the pen and the guard
# never disagree about what a valid record is (I-4). It comes from the guard's
# OWN repo (parents[2]) — not ONTUM_REPO_ROOT, which names the repo being
# written to and in tests is a temp dir with no loop/ package.
_GUARD_REPO = pathlib.Path(__file__).resolve().parents[2]
if str(_GUARD_REPO) not in sys.path:
    sys.path.insert(0, str(_GUARD_REPO))
try:
    from loop import pen as _pen
except Exception:
    _pen = None

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
    """The next id, folded across the whole fleet when git is reachable
    (placement.py), else the local directory fold. Cross-ref so a session
    writing its own record in its worktree is not handed an id another
    branch already claimed — the colliding 0020s (done-line 0023)."""
    if _placement is not None:
        try:
            return _placement.next_id(dirpath)
        except Exception:
            pass  # a broken sensor falls back; it never blocks the write
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

        # the most specific rule first: a records directory's declared form.
        # A raw Write here is allowed only as a faithful CARBON COPY of what
        # the pen would have produced (done-line 0070, bdo's write-through
        # model): the pen stays the authority, but a write whose bytes ARE the
        # pen's output is the pen's output, typed by another hand. Anything
        # that diverges is refused, and the refusal IS the fail notification.
        cfg_path = d / ".pen.json"
        if cfg_path.exists():
            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
            pen = cfg.get("pen", "python -m loop.pen new <dir> --slug <slug>")
            if _pen is None:
                # the shared definition is unreachable: fail open, but loudly —
                # an invisible failure here is an unguarded records dir that
                # still looks guarded. Never silently allow without saying so.
                record({"status": "fail-open", "rule": "carbon-copy-unreachable",
                         "path": rel})
                print("write_guard: loop.pen unreachable — records carbon-copy "
                      "check skipped (failing open); the repo may be broken.",
                      file=sys.stderr)
                return 0
            expected = next_id(d) if NUMBERED.match(name) else None
            problems = _pen.carbon_divergences(cfg, name, content, expected)
            if problems:
                return deny("write-not-carbon-copy", rel,
                            "denied: a raw Write into a pen-governed records "
                            "directory is allowed only as a faithful carbon copy "
                            "of what the pen would write — this is not:\n  - "
                            + "\n  - ".join(problems)
                            + f"\nThe pen writes it correctly in one move: {pen}")
            return 0  # a faithful carbon copy: structurally the pen's own output

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
