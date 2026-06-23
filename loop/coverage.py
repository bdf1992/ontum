#!/usr/bin/env python3
"""The discovered-coverage fold: which tracked files agents have reached.

bdo, 2026-06-22: he wants his VS Code viewport to carry a per-file MASK — which
files agents have NOT discovered yet (undiscovered) — alongside edited/red. And
edited/red VS Code already paints natively, so this fold owns ONLY the
"discovered" axis: a file is DISCOVERED once any session has read or edited it
(the sensor `.claude/hooks/file_touch.py` records every such touch to
`.ai-native/log/file-touch.jsonl`); a TRACKED file no session ever touched is
UNDISCOVERED — the mask the step-2 VS Code extension will paint.

Sibling of `census`/`forest`/`gaps` in their exact grain — a pure read-only
fold, stdlib, deterministic, `--json`, ending in a clear `done | report |
needs-you` line (D-6). It writes NOTHING; the touch log is a gitignored sensor
trace it only reads.

  - discovered   = the set of repo-relative paths the touch log ever records
                   (read OR edited);
  - undiscovered = a TRACKED file (`git ls-files`) absent from that set.

The §10 tooth lives in the pure classifier: a tracked file never touched reads
`undiscovered`, a touched file reads `discovered`. A constant 'all discovered'
classifier is caught — `tests/test_coverage.py` proves the fold non-vacuous.
edited/red is deliberately NOT computed here (native VS Code); this fold owns
discovered-coverage only. The painting extension is step 2 — out of scope.

CLI:
  python -m loop.coverage          per-directory discovered/undiscovered counts
  python -m loop.coverage --json   the raw dataset (the step-2 consumer reads this)
"""

import argparse
import json
import posixpath
import subprocess
import sys
from pathlib import Path

# loop/coverage.py -> loop/ -> repo root. Works the same in a worktree.
REPO = Path(__file__).resolve().parent.parent
TOUCH_LOG_REL = ".ai-native/log/file-touch.jsonl"


# ------------------------------------------------------------- reading the log

def discovered_set(touch_log):
    """The set of repo-relative paths the touch log records as ever read or
    edited. Torn-tail tolerant: a line that won't parse never happened, like the
    rest of the loop. Empty when the log is absent (absence is information)."""
    out = set()
    touch_log = Path(touch_log)
    if not touch_log.exists():
        return out
    try:
        lines = touch_log.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return out
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue  # torn tail or partial write — it never happened
        p = rec.get("path")
        if isinstance(p, str) and p:
            out.add(p)
    return out


# ----------------------------------------------------------- pure classifiers
# The §10 teeth live here, as pure functions over already-sensed inputs — so the
# test suite hits them directly without driving git (the forest/census pattern).

def file_status(path, discovered):
    """Pure: one tracked path's coverage status. The bite — a path in the
    discovered set is `discovered`, one absent is `undiscovered`; a constant
    classifier collapses the two and the test catches it."""
    return "discovered" if path in discovered else "undiscovered"


def coverage(tracked, discovered):
    """Pure: fold tracked paths + the discovered set into per-file status and
    per-directory counts. `tracked` is an iterable of repo-relative paths;
    `discovered` is the set from the touch log. Total — no I/O, no git."""
    files, dirs = [], {}
    for path in sorted(set(tracked)):
        status = file_status(path, discovered)
        files.append({"path": path, "status": status})
        d = posixpath.dirname(path) or "."
        bucket = dirs.setdefault(
            d, {"discovered": 0, "undiscovered": 0, "total": 0})
        bucket[status] += 1
        bucket["total"] += 1
    n_disc = sum(1 for f in files if f["status"] == "discovered")
    return {
        "files": files,
        "dirs": dirs,
        "discovered": sorted(discovered),
        "totals": {
            "tracked": len(files),
            "discovered": n_disc,
            "undiscovered": len(files) - n_disc,
            "touched_paths": len(discovered),
        },
    }


# ------------------------------------------------------------------- sensing
# The outward reach (subprocess to git) lives only here, never in the pure
# functions above. It fails soft: a sensor failure yields no tracked files
# (absence is information), never a crash.

def sense_tracked(repo):
    """Tracked files under `repo` via `git ls-files`, as repo-relative
    forward-slash paths. [] on any sensor failure."""
    try:
        proc = subprocess.run(
            ["git", "ls-files"], cwd=repo, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=30)
    except (OSError, subprocess.SubprocessError):
        return []
    if proc.returncode != 0:
        return []
    return [ln.strip() for ln in proc.stdout.splitlines() if ln.strip()]


def fold(repo=REPO, touch_log=None):
    """Sense the tracked files and the discovered set, and fold them into the
    coverage dataset. `repo` is the git root; `touch_log` defaults to the
    sensor's sink under it."""
    touch_log = touch_log or (Path(repo) / TOUCH_LOG_REL)
    tracked = sense_tracked(repo)
    discovered = discovered_set(touch_log)
    result = coverage(tracked, discovered)
    result["touch_log_present"] = Path(touch_log).exists()
    return result


# ------------------------------------------------------------------- rendering

def render(d):
    t = d["totals"]
    print(f"\ndiscovered coverage — {t['discovered']}/{t['tracked']} tracked "
          f"file(s) reached by some session ({t['undiscovered']} undiscovered)")
    if not d["touch_log_present"]:
        print("  (no touch log yet — every tracked file reads undiscovered; the "
              "sensor records as sessions read/edit files)")

    # lead with the directories carrying the most undiscovered files — the
    # darkest part of the mask, where attention has not yet reached.
    dirs = sorted(d["dirs"].items(),
                  key=lambda kv: (-kv[1]["undiscovered"], kv[0]))
    shown = [(name, c) for name, c in dirs if c["undiscovered"]]
    if shown:
        print(f"\nundiscovered by directory ({len(shown)}):")
        for name, c in shown[:40]:
            print(f"  {name}/  — {c['undiscovered']} undiscovered "
                  f"of {c['total']}")
        if len(shown) > 40:
            print(f"  …+{len(shown) - 40} more directories")
    print()
    if t["tracked"] == 0:
        print("result: needs-you — no tracked files enumerated (is this a git "
              "repo?). The fold reads `git ls-files`; without it there is "
              "nothing to mask.")
        return 1
    if t["undiscovered"] == 0:
        print(f"result: done — every tracked file ({t['tracked']}) has been "
              f"discovered by some session")
        return 0
    print(f"result: report — {t['undiscovered']} of {t['tracked']} tracked "
          f"file(s) undiscovered; the step-2 VS Code extension paints this mask "
          f"(`--json` is its data). edited/red is native VS Code, not here.")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo", type=Path, default=REPO,
                    help="git root to fold coverage of (default: this one)")
    ap.add_argument("--touch-log", type=Path, default=None,
                    help="the file-touch sensor log (default: "
                         "<repo>/.ai-native/log/file-touch.jsonl)")
    ap.add_argument("--json", action="store_true",
                    help="emit the raw dataset (the step-2 consumer reads this)")
    args = ap.parse_args(argv)
    d = fold(args.repo, args.touch_log)
    if args.json:
        print(json.dumps(d, indent=2, sort_keys=True))
        return 0
    return render(d)


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
