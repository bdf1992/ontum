#!/usr/bin/env python3
"""The ambient-run ledger: the surface that shows whether the loop's headless
and ambient runs *did anything worth a damn*.

bdo: headless and ambient runs "might as well not be happening" — no surface
shows them, so he can neither see nor close nor report on them together. The
deeper cut, his own: a run *might be useless*, and a surface that exposed
that would be doing its job. So this ledger's value is not "a run happened"
but *whether the run moved real work*. An empty run must confess; the surface
earns its keep by being able to embarrass the loop. Same logic as the part
census (`wired·idle` = plumbed in, never fires) — at run scale.

Two sources, read generically:
  - `tick` admissions, written by orchestrate every fast-loop tick.
  - `run` events, written by `record()` — the trace a headless or gate-
    launched process leaves so it stops being invisible.

The teeth: a zero-movement run is NOT automatically waste. A tick that spent
zero because it *cooled* (queue at cap) or *deferred* is the loop correctly
holding — backpressure, not spinning. A run that moved nothing with nothing
held is **barren**: it ran and has nothing to show. The ledger must NOT
smooth barren into "ran fine"; a span that is all barren reads as spinning.

Read-only like summon/census/digest, except `record` (the one write — the
loop noting its own activity, as orchestrate notes its ticks). Outward reach
(the GitHub issue per run) lives in the gate pen and the reflector pen, never
here.

CLI:
  python -m loop.runs                       the ledger, all-time, read-only
  python -m loop.runs --today               only today's runs (UTC)
  python -m loop.runs --since 2026-06-01 --until 2026-06-11
  python -m loop.runs --json                the raw dataset (machine-readable)
  python -m loop.runs record --kind gate-judgment --by claude --advanced 1 \\
        --note "value-gate.claude.v1 judged atom.x"

Stdlib only. Ends with a clear result on stdout (D-6): done | report.
"""

import argparse
import sys
from pathlib import Path

from loop.reconcile import (DEFAULT_ROOT, Fold, append_line, canon, now_ts,
                            short_hash)

# the movement dimensions a recorded run carries — what "worth a damn" means.
MOVED_KEYS = ("advanced", "receipts", "lands", "refusals")


def in_span(ts, since, until):
    """A record's date within [since, until] inclusive; a None bound is
    unbounded. ISO-8601 dates sort lexically, so string compare is the whole
    test — no clock, the fold stays pure (as digest)."""
    if not ts:
        return False
    day = ts[:10]
    if since and day < since:
        return False
    if until and day > until:
        return False
    return True


def record(root, kind, by, arc=None, moved=None, note=None):
    """Append one `run` event: a headless/ambient run's own trace. The write
    seam so a run stops being invisible. The id hashes the trace, not just the
    clock, so two distinct runs in one second stay distinct."""
    moved = {k: int((moved or {}).get(k, 0)) for k in MOVED_KEYS}
    evt = {
        "id": "evt.run." + short_hash(kind, str(by), str(arc), canon(moved),
                                      str(note), now_ts()),
        "type": "run",
        "kind": kind,
        "by": by,
        "arc": arc,
        "moved": moved,
        "note": note,
        "ts": now_ts(),
    }
    append_line(root / "log" / "events.jsonl", evt)
    return evt


def _classify(moved_total, held):
    """The verdict on one run's emptiness — the ledger's teeth.
      moved : moved real work; not empty.
      held  : moved nothing, but for a reason (cooled / deferred) — the loop
              correctly holding under backpressure, not waste.
      barren: moved nothing with nothing held — ran and has nothing to show.
    """
    if moved_total > 0:
        return "moved"
    return "held" if held else "barren"


def _from_tick(t):
    """A fast-loop tick, read as a run. budget_spent is its movement; a tick
    that cooled or deferred held work rather than spun."""
    spent = t.get("budget_spent", 0)
    deferred = t.get("deferred", []) or []
    held = t.get("mode") == "cool" or bool(deferred)
    return {
        "source": "tick",
        "id": t.get("id"),
        "kind": "tick",
        "tick_n": t.get("tick"),
        "by": "orchestrate",
        "arc": None,
        "ts": t.get("ts"),
        "moved": {"advanced": spent},
        "moved_total": spent,
        "deferred": len(deferred),
        "mode": t.get("mode"),
        "standing": _classify(spent, held),
    }


def _from_event(e):
    """A recorded `run` event, read as a run. A headless run that moved nothing
    is barren by definition — it is not under the fast loop's backpressure."""
    moved = {k: int((e.get("moved") or {}).get(k, 0)) for k in MOVED_KEYS}
    total = sum(moved.values())
    return {
        "source": "event",
        "id": e.get("id"),
        "kind": e.get("kind"),
        "by": e.get("by"),
        "arc": e.get("arc"),
        "ts": e.get("ts"),
        "moved": moved,
        "moved_total": total,
        "note": e.get("note"),
        "standing": _classify(total, held=False),
    }


def _sessions(ticks):
    """Roll fast-loop ticks up into the orchestrate invocations that produced
    them — bdo steers arcs, not ticks, so 30 ticks reading 'advanced 1' is
    noise; one line per invocation is signal. A new invocation restarts its
    tick counter at 1, so a non-increase in tick_n is a session boundary."""
    out = []
    cur = None
    last_n = None
    for t in ticks:  # chronological (log order)
        n = t.get("tick_n")
        if cur is None or last_n is None or n is None or n <= last_n:
            cur = {"start": t["ts"], "end": t["ts"], "ticks": 0,
                   "advanced": 0, "moved": 0, "held": 0, "barren": 0}
            out.append(cur)
        cur["end"] = t["ts"]
        cur["ticks"] += 1
        cur["advanced"] += t["moved_total"]
        cur[t["standing"]] += 1
        last_n = n
    for s in out:
        s["standing"] = ("moved" if s["moved"] else "held" if s["held"]
                         else "barren")
    return out


def runs(root, since=None, until=None):
    """The pure fold: every fast-loop tick and headless run event in span,
    each judged moved / held / barren, ticks rolled into sessions."""
    fold = Fold(root)
    ticks, events = [], []
    for t in fold.admissions:
        if t.get("type") == "tick" and in_span(t.get("ts"), since, until):
            ticks.append(_from_tick(t))
    for e in fold.events:
        if e.get("type") == "run" and in_span(e.get("ts"), since, until):
            events.append(_from_event(e))
    ticks.sort(key=lambda r: r.get("ts") or "")
    events.sort(key=lambda r: r.get("ts") or "")
    items = ticks + events

    sessions = _sessions(ticks)
    standings = {"moved": 0, "held": 0, "barren": 0}
    for r in items:
        standings[r["standing"]] += 1
    total = len(items)
    return {
        "span": {"since": since, "until": until},
        "runs": items,
        "sessions": sessions,
        "events": events,
        "total": total,
        "moved": standings["moved"],
        "held": standings["held"],
        "barren": standings["barren"],
        "spinning": total > 0 and standings["moved"] == 0 and standings["barren"] > 0,
    }


def _span_label(span):
    since, until = span.get("since"), span.get("until")
    if not since and not until:
        return "all time"
    return f"{since or 'start'} … {until or 'now'}"


def _clock(ts):
    return (ts or "")[11:16]


def render(d):
    """The dataset as prose — a finding, not a log dump (a per-tick list
    "means nothing"). One headline verdict; headless runs named individually
    (rare, and what bdo cannot otherwise see); fast-loop ticks rolled into one
    summary line per orchestrate invocation."""
    lines = ["# Ambient-run ledger", f"_span: {_span_label(d['span'])}_", ""]

    if d["total"] == 0:
        lines += ["_No ambient or headless runs in span — the loop has not run "
                  "here. Absence is information._", ""]
        return "\n".join(lines)

    if d["spinning"]:
        lines += [f"## ⚠ The loop spun — {d['barren']} barren run(s), 0 that "
                  "moved work",
                  "_It ran and produced nothing. Fix what the ambient loop does, "
                  "or prune it (the cut is yours, D-4)._", ""]
    elif d["barren"]:
        lines += [f"## ⚠ {d['barren']} barren run(s) — ran, moved nothing, "
                  "nothing held", ""]
    else:
        lines += [f"## Productive — every run moved work or held correctly "
                  f"({d['moved']} moved, {d['held']} held)", ""]

    ev = d["events"]
    lines.append("## Headless / recorded runs")
    if not ev:
        lines.append("- **none recorded.** Headless and overnight sessions leave "
                     "no trace yet — the real \"might as well not be happening\". "
                     "`loop.runs record` (and the gate pen) is where they land.")
    else:
        for r in ev:
            mark = {"moved": "·", "held": "○", "barren": "✗"}[r["standing"]]
            moved = ", ".join(f"{k} {v}" for k, v in r["moved"].items() if v) or "nothing"
            arc = f" [{r['arc']}]" if r.get("arc") else ""
            lines.append(f"- {mark} `{r['kind']}` {r.get('ts')}{arc} by "
                         f"{r.get('by')} — moved {moved}"
                         + (f" ({r['standing']})" if r["standing"] != "moved" else "")
                         + (f" — {r['note']}" if r.get("note") else ""))
    lines.append("")

    s = d["sessions"]
    if s:
        moved_steps = sum(x["advanced"] for x in s)
        lines.append(f"## Fast loop — {len(s)} orchestrate run(s), "
                     f"{sum(x['ticks'] for x in s)} ticks, {moved_steps} steps moved")
        for x in s:
            mark = {"moved": "·", "held": "○", "barren": "✗"}[x["standing"]]
            same = x["start"][:10] == x["end"][:10] and _clock(x["start"]) == _clock(x["end"])
            span = _clock(x["start"]) if same else f"{_clock(x['start'])}–{_clock(x['end'])}"
            day = x["start"][:10]
            tn = f"{x['ticks']} tick" + ("s" if x["ticks"] != 1 else "")
            note = (f"{x['advanced']} step" + ("s" if x["advanced"] != 1 else "")
                    + " moved" if x["standing"] == "moved"
                    else "all held (backpressure)" if x["standing"] == "held"
                    else "BARREN — moved nothing")
            lines.append(f"- {mark} {day} {span}: {tn}, {note}")
        if not d["barren"]:
            lines.append(f"\n_All {len(s)} fast-loop runs were productive — the "
                         "fast loop does not spin (it parks when there is nothing "
                         "to do, rather than ticking empty)._")
        lines.append("")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    ap.add_argument("--since", help="inclusive lower date bound, YYYY-MM-DD")
    ap.add_argument("--until", help="inclusive upper date bound, YYYY-MM-DD")
    ap.add_argument("--today", action="store_true",
                    help="only today's runs (UTC); the only place a clock is read")
    ap.add_argument("--json", action="store_true",
                    help="emit the raw dataset (machine-readable), not the prose")

    sub = ap.add_subparsers(dest="verb")
    rec = sub.add_parser("record", help="append a run event — a headless/ambient "
                         "run's own trace so it stops being invisible")
    rec.add_argument("--kind", required=True, help="run kind, e.g. gate-judgment, overnight")
    rec.add_argument("--by", required=True, help="who ran it")
    rec.add_argument("--arc", help="epic/arc id this run served, if any")
    rec.add_argument("--advanced", type=int, default=0, help="atoms advanced")
    rec.add_argument("--receipts", type=int, default=0, help="receipts written")
    rec.add_argument("--lands", type=int, default=0, help="lands")
    rec.add_argument("--refusals", type=int, default=0, help="refusals")
    rec.add_argument("--note", help="one line: what the run did")
    args = ap.parse_args(argv)

    if args.verb == "record":
        moved = {"advanced": args.advanced, "receipts": args.receipts,
                 "lands": args.lands, "refusals": args.refusals}
        evt = record(args.root, kind=args.kind, by=args.by, arc=args.arc,
                     moved=moved, note=args.note)
        standing = _classify(sum(moved.values()), held=False)
        print(f"result: report — recorded {evt['id']} ({evt['kind']}, {standing})")
        return 0

    since, until = args.since, args.until
    if args.today:
        since = until = now_ts()[:10]
    d = runs(args.root, since=since, until=until)
    if args.json:
        print(canon(d))
    else:
        print(render(d))
    if d["spinning"]:
        print(f"result: report — the loop spun: {d['barren']} barren run(s), "
              "0 that moved work; the cut is yours (D-4)")
    elif d["barren"]:
        print(f"result: report — {d['barren']} barren run(s) of {d['total']}; "
              "the rest moved work or held correctly")
    else:
        print(f"result: done — {d['total']} run(s), none barren "
              f"({d['moved']} moved, {d['held']} held)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
