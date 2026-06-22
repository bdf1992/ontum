#!/usr/bin/env python3
"""loop/health.py - the health board (bdo 2026-06-22): is every expected
standing process actually running, what is scheduled, and what is live right now
- for bdo and any session both, surfaced at session start.

A standing process can die silently and nobody would know. This is the watchdog
- a read-only board with three panels:
  * ALERTS   - each EXPECTED process (declared in .claude/expected-processes.json)
               checked up/down: its OS task registered + enabled, and its
               freshness signal recent. A down process screams; that is the alert.
  * SCHEDULE - the standing tasks and when they next run.
  * LIVE     - what acted on the log in the last window, attributed by actor, so
               bdo and a session both see what is moving right now.

Read-only; stdlib + a guarded schtasks probe (degrades to freshness-only off
Windows). Fail-open: the board never blocks a session. Ends done|report|needs-you.
"""

import argparse
import datetime
import json
import subprocess
import sys
from pathlib import Path

from loop import reconcile
from loop.reconcile import DEFAULT_ROOT


def _repo(root):
    return Path(root).resolve().parent


def expected_processes(root):
    p = _repo(root) / ".claude" / "expected-processes.json"
    if not p.is_file():
        return []
    try:
        return json.loads(p.read_text(encoding="utf-8")).get("processes", [])
    except Exception:
        return []


def _ts(rec):
    raw = rec.get("ts")
    if not raw:
        return None
    try:
        return datetime.datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
    except ValueError:
        return None


def _file_age_min(path, now):
    p = Path(path)
    if not p.exists():
        return None
    mtime = datetime.datetime.fromtimestamp(p.stat().st_mtime, datetime.timezone.utc)
    return (now - mtime).total_seconds() / 60.0


def probe_task(task):
    try:
        out = subprocess.run(["schtasks", "/query", "/tn", task, "/fo", "LIST", "/v"],
                             capture_output=True, text=True, timeout=10)
    except Exception:
        return None
    if out.returncode != 0:
        return {"registered": False}
    info = {"registered": True}
    for line in out.stdout.splitlines():
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        k = k.strip().lower()
        v = v.strip()
        if k == "scheduled task state":
            info["state"] = v
        elif k == "next run time" and v:
            info["next_run"] = v
        elif k == "last run time" and v:
            info["last_run"] = v
        elif k == "last result" and v:
            info["last_result"] = v
    return info


def check_process(proc, now, probe=probe_task):
    name = proc.get("name", "?")
    reasons = []
    verdict = "up"
    task = proc.get("os_task")
    pr = probe(task) if task else None
    if pr is not None:
        if not pr.get("registered"):
            verdict = "down"
            reasons.append("OS task " + repr(task) + " is NOT registered")
        elif str(pr.get("state", "")).lower() == "disabled":
            verdict = "down"
            reasons.append("OS task " + repr(task) + " is DISABLED")
    fresh_file = proc.get("freshness_file")
    max_age = proc.get("max_age_minutes", 90)
    age = _file_age_min(fresh_file, now) if fresh_file else None
    if fresh_file:
        if age is None:
            verdict = "down"
            reasons.append("never ran (no freshness signal at " + str(fresh_file) + ")")
        elif age > max_age:
            verdict = "down"
            reasons.append("STALE: last ran " + str(int(age)) + "m ago (max " + str(max_age) + "m)")
    if verdict == "up":
        ran = ("ran " + str(int(age)) + "m ago") if age is not None else "no freshness file declared"
        reasons.append("registered, enabled, " + ran)
    return {"name": name, "why": proc.get("why", ""), "verdict": verdict,
            "reasons": reasons, "age_min": age, "next_run": (pr or {}).get("next_run")}


def schedule(root, probe=probe_task):
    rows = []
    for proc in expected_processes(root):
        t = proc.get("os_task")
        if not t:
            continue
        pr = probe(t)
        rows.append({"name": proc.get("name"), "task": t,
                     "next_run": (pr or {}).get("next_run"),
                     "registered": bool(pr and pr.get("registered"))})
    return rows


def live(root, now, window_min=45):
    fold = reconcile.Fold(root)
    since = now - datetime.timedelta(minutes=window_min)
    acts = {}
    for rec in list(fold.events) + list(fold.receipts) + list(fold.admissions):
        t = _ts(rec)
        if t is None or t < since:
            continue
        actor = rec.get("by") or rec.get("node") or rec.get("from_node") or "system"
        acts[actor] = acts.get(actor, 0) + 1
    return dict(sorted(acts.items(), key=lambda kv: -kv[1]))


def board(root=DEFAULT_ROOT, now=None, window_min=45, probe=probe_task):
    now = now or datetime.datetime.now(datetime.timezone.utc)
    procs = [check_process(p, now, probe=probe) for p in expected_processes(root)]
    return {"alerts": procs, "schedule": schedule(root, probe=probe),
            "live": live(root, now, window_min),
            "down": [p["name"] for p in procs if p["verdict"] == "down"]}


def render(b):
    out = []
    if b["down"]:
        out.append("[ALERT] loop health - DOWN: " + ", ".join(b["down"]))
    out.append("# loop health board\n")
    out.append("## alerts (expected standing processes)")
    if not b["alerts"]:
        out.append("- (none declared)")
    for p in b["alerts"]:
        mark = "DOWN" if p["verdict"] == "down" else "up"
        out.append("- " + p["name"] + ": " + mark + " - " + "; ".join(p["reasons"]))
        if p["why"]:
            out.append("    (" + p["why"] + ")")
    out.append("\n## schedule")
    for s in b["schedule"]:
        if s["registered"]:
            out.append("- " + str(s["name"]) + ": next run " + str(s.get("next_run") or "(unknown)"))
        else:
            out.append("- " + str(s["name"]) + ": NOT registered")
    out.append("\n## live (last 45m, by actor)")
    if not b["live"]:
        out.append("- (quiet - nothing on the log in the window)")
    for actor, n in b["live"].items():
        out.append("- " + str(actor) + ": " + str(n) + " act(s)")
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=Path(DEFAULT_ROOT))
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--hook", action="store_true",
                    help="session-start mode: speak only when something is DOWN; exit 0 always")
    args = ap.parse_args(argv)
    try:
        b = board(args.root)
    except Exception as e:
        if not args.hook:
            print("result: report - health board could not run: " + str(e))
        return 0
    if args.json:
        print(json.dumps(b, ensure_ascii=False))
        return 0
    if args.hook:
        if b["down"]:
            print("[ALERT] loop health - DOWN: " + ", ".join(b["down"]) + " (run: python -m loop.health)")
        return 0
    print(render(b))
    verb = "needs-you" if b["down"] else "done"
    if b["down"]:
        tail = str(len(b["down"])) + " expected process(es) DOWN - a standing process died; restart or re-register it"
    else:
        tail = str(len(b["alerts"])) + " expected process(es), all up"
    print("\nresult: " + verb + " - " + tail)
    return 0


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
