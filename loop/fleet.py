"""fleet.py — the Administrator's eyes (v0): a read-only fold over the live fleet.

The Administrator (administrator.proposal.md, PR #416) oversees a network of
Conductors (each a `Workflow` run) and their Agents. Today a managing session
monitors that fleet *by hand* — reading `journal.jsonl` and `agent-*.jsonl` out
of the workflow transcript dirs. This fold is the first requirement that
by-hand work surfaced: one glance over every in-flight and recent conductor and
its agents, so "monitoring admin over them" stops being a grep.

Eyes before hand — the same order the merge digest (loop/digest.py) preceded the
merge-node. This is the digest for the live agent network instead of the merge
queue. Read-only, stdlib, local-first: it folds the workflow *transcripts* (the
conductors' runtime), distinct from the atom log the rest of loop/ folds. It
mints nothing and the cut stays the Administrator's (D-4).

    python -m loop.fleet            # the fleet glance
    python -m loop.fleet --json     # the raw dataset (machine-readable)
    python -m loop.fleet --all      # every session under the project, not just live

A conductor is RUNNING when its journal has more `started` than `result`
events; COMPLETE when they match; UNKNOWN when the journal is unreadable (the
torn-tail rule — an absence, never a crash).
"""

from __future__ import annotations

import json
import os
import pathlib
import sys
import time


def project_slug(cwd: pathlib.Path) -> str:
    """The .claude/projects dir name is the path with every separator folded to
    '-' and lowercased: C:\\Users\\bdf19\\ontum -> c--Users-bdf19-ontum.
    (Drive 'C:' -> 'c' + '-' from ':' + '-' from the first '\\'.)"""
    s = str(cwd)
    out = []
    for ch in s:
        out.append("-" if ch in ":\\/" else ch)
    # the scheme lowercases only the drive letter in practice; fold the whole
    # head defensively — projects dirs are matched case-insensitively below.
    return "".join(out)


def projects_root() -> pathlib.Path:
    return pathlib.Path(os.path.expanduser("~")) / ".claude" / "projects"


def find_project_dir(cwd: pathlib.Path):
    """Resolve this repo's projects dir by case-insensitive slug match — robust
    to the drive-letter casing the runtime uses."""
    root = projects_root()
    if not root.is_dir():
        return None
    want = project_slug(cwd).lower()
    for child in root.iterdir():
        if child.is_dir() and child.name.lower() == want:
            return child
    return None


def read_jsonl(path: pathlib.Path):
    """Tolerant fold: an unparseable line never happened (the torn-tail rule)."""
    rows = []
    if not path.exists():
        return rows
    for line in path.read_bytes().decode("utf-8", "replace").splitlines():
        try:
            rows.append(json.loads(line))
        except (json.JSONDecodeError, ValueError):
            continue
    return rows


def script_names(session_dir: pathlib.Path):
    """Map run-id -> authored workflow name, read from the persisted script
    filenames (<name>-wf_<hash>.js under <session>/workflows/scripts/)."""
    names = {}
    scripts = session_dir / "workflows" / "scripts"
    if scripts.is_dir():
        for p in scripts.glob("*-wf_*.js"):
            stem = p.name[:-3]  # drop .js
            i = stem.rfind("-wf_")
            if i > 0:
                names[stem[i + 1:]] = stem[:i]
    return names


def fold_run(run_dir: pathlib.Path, name: str | None):
    journal = read_jsonl(run_dir / "journal.jsonl")
    started = sum(1 for e in journal if e.get("type") == "started")
    results = sum(1 for e in journal if e.get("type") == "result")
    agents = sorted(run_dir.glob("agent-*.jsonl"))
    last = 0.0
    for p in (*agents, run_dir / "journal.jsonl"):
        try:
            last = max(last, p.stat().st_mtime)
        except OSError:
            pass
    if not journal:
        state = "UNKNOWN"
    elif results >= started and started > 0:
        state = "COMPLETE"
    else:
        state = "RUNNING"
    return {
        "run_id": run_dir.name,
        "name": name or "(unnamed)",
        "state": state,
        "agents": len(agents),
        "started": started,
        "results": results,
        "in_flight": max(0, started - results),
        "last_activity": last,
    }


STALE_SECONDS = 900  # a RUNNING run idle past this is a zombie, not a worker (R8)


def fold_fleet(project_dir: pathlib.Path, every_session: bool,
               now: float, stale_seconds: int = STALE_SECONDS):
    runs = []
    if project_dir is None or not project_dir.is_dir():
        return runs
    sessions = [p for p in project_dir.iterdir() if p.is_dir()]
    # newest session first; without --all, only sessions with a live run matter,
    # but we fold all and let the caller filter.
    for session_dir in sessions:
        wf_root = session_dir / "subagents" / "workflows"
        if not wf_root.is_dir():
            continue
        names = script_names(session_dir)
        for run_dir in wf_root.glob("wf_*"):
            if run_dir.is_dir():
                row = fold_run(run_dir, names.get(run_dir.name))
                row["session"] = session_dir.name
                # liveness (R8): a RUNNING run with no activity past the staleness
                # line is STALLED — a zombie. A live admin must not count it filled.
                if row["state"] == "RUNNING" and \
                        (now - row["last_activity"]) > stale_seconds:
                    row["state"] = "STALLED"
                runs.append(row)
    runs.sort(key=lambda r: r["last_activity"], reverse=True)
    return runs


def ago(ts: float, now: float) -> str:
    if ts <= 0:
        return "—"
    d = max(0, int(now - ts))
    if d < 90:
        return f"{d}s"
    if d < 5400:
        return f"{d // 60}m"
    if d < 172800:
        return f"{d // 3600}h"
    return f"{d // 86400}d"


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    as_json = "--json" in argv
    every = "--all" in argv
    stale = STALE_SECONDS
    for a in argv:
        if a.startswith("--stale-mins="):
            try:
                stale = max(60, int(a.split("=", 1)[1]) * 60)
            except ValueError:
                pass
    now = time.time()  # display-only; never enters a record (this is a glance)

    project_dir = find_project_dir(pathlib.Path.cwd())
    runs = fold_fleet(project_dir, every, now, stale)
    live = [r for r in runs if r["state"] == "RUNNING"]
    stalled = [r for r in runs if r["state"] == "STALLED"]
    done = [r for r in runs if r["state"] not in ("RUNNING", "STALLED")]
    recent = runs if every else (live + stalled + done[:8])

    if as_json:
        print(json.dumps({
            "project": project_dir.name if project_dir else None,
            "live": len(live),
            "stalled": len(stalled),
            "in_flight_agents": sum(r["in_flight"] for r in live),
            "runs": runs,
        }, ensure_ascii=False, indent=2))
        return 0

    if project_dir is None:
        print("result: report — no .claude/projects dir for this repo yet; "
              "the fleet is empty until a Workflow runs here.")
        return 0
    if not runs:
        print("result: report — no conductors on record. Launch one with the "
              "Workflow tool; it appears here while it runs.")
        return 0

    stale_note = f", {len(stalled)} STALLED" if stalled else ""
    print(f"FLEET — {len(live)} running{stale_note}, "
          f"{sum(r['in_flight'] for r in live)} agent(s) in flight  "
          f"({len(runs)} conductor(s) on record)\n")
    print(f"  {'state':8} {'agents':>6} {'flight':>6} {'last':>5}  conductor")
    for r in recent:
        flight = str(r["in_flight"]) if r["in_flight"] else "·"
        print(f"  {r['state']:8} {r['agents']:>6} {flight:>6} "
              f"{ago(r['last_activity'], now):>5}  {r['name']}  ({r['run_id']})")
    if not every and len(runs) > len(recent):
        print(f"\n  … +{len(runs) - len(recent)} older (--all to show every session)")
    print("\nresult: report — the fleet, folded. The cut stays yours (D-4); "
          "this surface only watches.")
    return 0


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
