#!/usr/bin/env python3
"""loop/volume.py — the volume scoreboard (the generative setpoint, widened).

bdo (2026-06-21): the loop should FILL A VOLUME based on a setpoint — not one
dial (`step_budget_per_tick`) but a whole body of targets: work opened and
closed, workflows launched, skills used, named items refined → opened → worked
→ processed, owner items reported, docs/architecture/tests kept covered, "and so
on." And the rule that makes it generative (his correction): **the numbers are
examples and the named items are suggestions** — we define a *volume*, the
*expectations*, and the *rewards and consequences*, NOT the model. The how is
inference's; the frame is ours.

So a **volume** is an open set of *dimensions*, each a declared, admitted record
(setpoints are admitted records, never code constants — §14): a `name`, the
`measure` that counts it from the record, a `target`, and a `period`. A new
dimension is ADMITTED, never coded — declare a counter + a target and it is
tracked. Nothing is baked: no "1000", no fixed list of activity types.

The two halves:
  * the **measures** — small pluggable counters (the utensils): each reads one
    dimension's actual count from the log over a window. A handful are wired to
    what the record honestly carries today; a dimension whose measure is not
    registered reads as **no-gauge** (absence is information — never counted as
    filled, the vacuous-fill refusal, sibling of section.py's drain teeth).
  * the **meter** — the read-only fold that scores actual-vs-target per declared
    dimension and reports the fill and its pressure (under / at / over). This is
    the rewards-and-consequences sensor: under target is pressure, at target is
    ease — the same reflex orchestrate runs on one dial, across the whole body.

The loop FILLS the volume (picks under-target dimensions, spends utensils to
raise them); this module only DEFINES and MEASURES it. Read-only but for the
`admit` verb (a dimension is bdo's to declare, `--by`). Stdlib; the loop/ law.
"""

import argparse
import datetime
import json
import sys
from pathlib import Path

from loop import reconcile
from loop.reconcile import DEFAULT_ROOT


# ---- the measures: pluggable counters over the record (the utensils) ----------
# Each is fn(fold, since_dt) -> int: how many of this dimension happened in the
# window. Wired to what the log honestly carries today; a new dimension adds an
# entry here (a utensil) plus an admitted volume_dim (the target). Generative by
# construction — the registry is open, not a closed schema.

def _ts(rec):
    raw = rec.get("ts")
    if not raw:
        return None
    try:
        return datetime.datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
    except ValueError:
        return None


def _count(records, since, pred):
    n = 0
    for r in records:
        t = _ts(r)
        if t is not None and t >= since and pred(r):
            n += 1
    return n


def _issue_events(verb):
    return lambda fold, since: _count(fold.events, since,
                                      lambda r: r.get("type") == f"issue.{verb}")


MEASURES = {
    "issues_opened": _issue_events("opened"),
    "issues_closed": _issue_events("closed"),
    "issues_reopened": _issue_events("reopened"),
    "owner_acts": lambda fold, since: _count(  # acts on bdo's surface (issue pen)
        fold.events, since, lambda r: r.get("kind") == "issue-governance"),
    "merges_landed": lambda fold, since: _count(
        fold.receipts, since, lambda r: r.get("kind") == "merge"),
    "verdicts_written": lambda fold, since: _count(  # work processed (any receipt verdict)
        fold.receipts, since, lambda r: bool(r.get("verdict"))),
}


# ---- the volume: an open set of admitted dimensions ---------------------------

def read_volume(fold):
    """The declared volume: the latest admitted `volume_dim` per name (a name is
    superseded, never duplicated — the setpoint-record grain)."""
    dims = {}
    for a in fold.admissions:
        if a.get("type") == "volume_dim" and a.get("name"):
            dims[a["name"]] = a  # later wins
    return dims


def admit_dimension(root, name, measure, target, period_hours, by):
    """Declare one volume dimension (bdo's, --by). Refuses a missing signer and a
    non-positive target; a measure with no registered counter is allowed but
    flagged no-gauge by the meter until its utensil exists (declare the want, the
    gauge can follow — absence is information, not a block)."""
    if not (by or "").strip():
        raise ValueError("a volume dimension is a setpoint — refusing a missing "
                         "--by (an admitted record is signed)")
    if target <= 0:
        raise ValueError(f"a target is a positive expectation — refusing {target}")
    rec = {
        "type": "volume_dim", "name": name, "measure": measure,
        "target": target, "period_hours": period_hours, "by": by,
        "id": "adm." + reconcile.short_hash("volume_dim", name, measure,
                                            str(target), by),
        "ts": reconcile.now_ts(),
    }
    reconcile.append_line(Path(root) / "log" / "admissions.jsonl", rec)
    return rec


# ---- the meter: score actual-vs-target (rewards and consequences) -------------

def _verdict(actual, target):
    fill = actual / target if target else 0.0
    if fill >= 1.0:
        return "over" if fill > 1.0 else "at", fill
    return "under", fill


def meter(root, now=None):
    """Score every declared dimension: actual over its period vs its target →
    fill and pressure. A dimension whose measure has no registered counter is
    `no-gauge` (never filled — the teeth)."""
    now = now or datetime.datetime.now(datetime.timezone.utc)
    fold = reconcile.Fold(root)
    rows = []
    for name, dim in sorted(read_volume(fold).items()):
        measure = dim.get("measure")
        target = dim.get("target") or 0
        hours = dim.get("period_hours") or 24
        since = now - datetime.timedelta(hours=hours)
        if measure not in MEASURES:
            rows.append({"name": name, "measure": measure, "target": target,
                         "period_hours": hours, "actual": None,
                         "verdict": "no-gauge", "fill": None})
            continue
        actual = MEASURES[measure](fold, since)
        verdict, fill = _verdict(actual, target)
        rows.append({"name": name, "measure": measure, "target": target,
                     "period_hours": hours, "actual": actual,
                     "verdict": verdict, "fill": round(fill, 3)})
    return rows


def rates(root, now=None, hours=24):
    """Every registered measure's CURRENT count over the window — what we
    actually did, no targets needed. The honest mirror you can read before any
    volume is declared."""
    now = now or datetime.datetime.now(datetime.timezone.utc)
    since = now - datetime.timedelta(hours=hours)
    fold = reconcile.Fold(root)
    return {name: fn(fold, since) for name, fn in sorted(MEASURES.items())}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=Path(DEFAULT_ROOT))
    sub = ap.add_subparsers(dest="cmd")

    rp = sub.add_parser("rates", help="current measured activity (no targets needed)")
    rp.add_argument("--hours", type=int, default=24)
    rp.add_argument("--json", action="store_true")

    sp = sub.add_parser("list-measures", help="the registered measures (the utensils)")

    ap.add_argument("--json", action="store_true", help="emit the raw dataset")

    adm = sub.add_parser("admit", help="declare one volume dimension (bdo's, --by)")
    adm.add_argument("--name", required=True)
    adm.add_argument("--measure", required=True, help=f"one of: {', '.join(MEASURES)} (or a future gauge)")
    adm.add_argument("--target", required=True, type=float)
    adm.add_argument("--period-hours", type=int, default=24)
    adm.add_argument("--by", required=True)

    args = ap.parse_args(argv)
    cmd = args.cmd

    if cmd == "list-measures":
        print("# registered measures (the utensils a dimension can use)\n")
        for name in sorted(MEASURES):
            print(f"- {name}")
        print(f"\nresult: report — {len(MEASURES)} measure(s); a new dimension "
              "adds a measure here + an admitted target (generative, not a schema)")
        return 0

    if cmd == "rates":
        data = rates(args.root, hours=args.hours)
        if args.json:
            print(json.dumps({"hours": args.hours, "rates": data}, ensure_ascii=False))
            return 0
        print(f"# current activity — last {args.hours}h (no targets, just what happened)\n")
        for name, n in data.items():
            print(f"- {name}: {n}")
        print("\nresult: report — measured rates only; declare a volume to score "
              "them (loop.volume admit --by bdo)")
        return 0

    if cmd == "admit":
        try:
            rec = admit_dimension(args.root, args.name, args.measure, args.target,
                                  args.period_hours, args.by)
        except ValueError as e:
            print(f"result: report — refused: {e}")
            return 2
        gauge = "" if args.measure in MEASURES else " (no gauge yet — the meter will show no-gauge until its measure is registered)"
        print(f"  admitted volume_dim '{rec['name']}' — {rec['measure']} target "
              f"{rec['target']}/{rec['period_hours']}h ({rec['id']}){gauge}")
        print(f"result: done — dimension '{rec['name']}' declared; the scoreboard "
              "now tracks it")
        return 0

    # default: the scoreboard
    rows = meter(args.root)
    if args.json:
        print(json.dumps({"volume": rows}, ensure_ascii=False))
        return 0
    if not rows:
        print("# the volume scoreboard\n\nNo volume declared yet — the body has "
              "no targets.\nDeclare a dimension (bdo's): "
              "`python -m loop.volume admit --name <n> --measure <m> --target <t> --by bdo`\n"
              "See what is measurable now: `python -m loop.volume rates` / "
              "`list-measures`.")
        print("\nresult: needs-you — no volume is declared; the scoreboard is "
              "empty until bdo sets the expectations (D-4)")
        return 0
    print("# the volume scoreboard — actual vs target (under = pressure, at = ease)\n")
    under = 0
    for r in rows:
        if r["verdict"] == "no-gauge":
            print(f"- {r['name']}: NO GAUGE — measure '{r['measure']}' has no "
                  f"counter yet (target {r['target']}/{r['period_hours']}h)")
            continue
        bar = f"{r['actual']}/{r['target']}"
        if r["verdict"] == "under":
            under += 1
        print(f"- {r['name']}: {bar} per {r['period_hours']}h — {r['verdict']} "
              f"(fill {r['fill']})")
    verb = "report" if under else "done"
    print(f"\nresult: {verb} — {len(rows)} dimension(s), {under} under target; "
          "the loop's work is to fill what is under (it picks the how, not us)")
    return 0


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
