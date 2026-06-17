#!/usr/bin/env python3
"""The training fold: a session's would-deny readings become a PROPOSED mode.

The second half of train mode (done-line 0097, on 0096's sensor). Node 1 made
the guard *observe* under train — every operation normal mode would deny is
allowed (exit 0) and recorded to the sensor trace (tool-use.jsonl) as
`status:"would-deny"` carrying the fence rule it would have hit, the
tags.classify intent, the surface, and the opening admission id
(`train_session`). This fold is the *lesson*: it reads those readings back and
proposes a stricter mode — but only what the evidence supports.

The teeth (§10): a training session that recorded *no* would-deny readings
yields *no* proposal. The fold refuses to invent a mode from no evidence — the
same refusal `causality/term_economy.py` makes (no evidence, no mint) and
`loop/gaps.py` lives by. If the empty session ever produced a proposal, the
fold would be fabricating.

It PROPOSES; it never installs. A stricter mode that relaxes nothing and tightens
the guard is still a posture change, and a posture change is bdo's alone to admit
(D-4) — this fold writes nothing and names his stamp as the only door. Read-only
like summon / census / digest / runs: it folds the log and the sensor trace, and
ends with a clear stdout result (D-6): report | needs-you.

CLI:
  python -m loop.train                      known training sessions + op counts
  python -m loop.train --session <id>       the profile + would-block set + proposal
  python -m loop.train --session <id> --json  the raw dataset (machine-readable)

`<id>` is the opening `security_mode` admission id (the `train_session` stamped
on every reading). Stdlib only, no network, no subprocess.
"""

import argparse
import sys
from pathlib import Path

from loop.reconcile import DEFAULT_ROOT, Fold, canon, read_jsonl

# the intent buckets the profile splits readings into — the recorded
# tags.classify value, with None ("untagged") kept honest, never folded away.
INTENT_BUCKETS = ("mutate", "read", None)


def sensor_path(root):
    """The sensor trace the guard writes (done-line 0096) — a gitignored,
    deletable log under the same root as the truth log, not truth itself."""
    return root / "log" / "tool-use.jsonl"


def training_sessions(fold):
    """Every opened training session, read from `security_mode` admissions
    (never a constant). An opener is an enabled `security_mode` admission; its
    id is the `train_session` stamped on each reading. A later `enabled:false`
    admission closes the posture (it supersedes; the opener stands as history),
    so the opener is reported with whether it was since closed."""
    openers, closed = [], False
    out = []
    for adm in fold.admissions:
        if adm.get("type") != "security_mode":
            continue
        if adm.get("enabled", True):
            out.append({
                "id": adm.get("id"),
                "mode": adm.get("mode", "train"),
                "session": adm.get("session"),
                "by": adm.get("by"),
                "ts": adm.get("ts"),
                "closed": False,
            })
        else:
            # a close supersedes the matching open(s) for the same scope
            for o in out:
                if o["session"] == adm.get("session"):
                    o["closed"] = True
    return out


def _surface_of(reading):
    """The tool family a reading is filed under: the would-deny record's
    `surface` when present (done-line 0096), else the first watched `bin`,
    else None. One reading, one surface line — read generically so a watched
    call and a would-deny call profile the same way."""
    if reading.get("surface"):
        return reading["surface"]
    bins = reading.get("bins") or []
    return bins[0] if bins else None


def profile(readings):
    """The operation profile over one session's readings: counts by intent
    (the recorded tags.classify value, None kept as 'untagged') and by tool
    surface. Pure tally, no judgment — the shape of what the session did."""
    by_intent = {b: 0 for b in INTENT_BUCKETS}
    by_surface = {}
    for r in readings:
        intent = r.get("intent")
        if intent not in by_intent:
            intent = None  # an unknown tag value is honest 'untagged', not a lie
        by_intent[intent] += 1
        surface = _surface_of(r)
        by_surface[surface] = by_surface.get(surface, 0) + 1
    return {
        # JSON-safe: None intent renders as the string "untagged"
        "by_intent": {(k if k is not None else "untagged"): v
                      for k, v in by_intent.items()},
        "by_surface": dict(sorted(by_surface.items(),
                                  key=lambda kv: (-kv[1], str(kv[0])))),
    }


def would_block_set(readings):
    """The would-block set: {fence-rule -> count} over the `would-deny`
    readings — every operation normal mode would have denied, by the rule it
    would have hit. This *is* the evidence; an empty set is an empty proposal."""
    out = {}
    for r in readings:
        if r.get("status") != "would-deny":
            continue
        rule = r.get("rule")
        if not rule:
            continue
        out[rule] = out.get(rule, 0) + 1
    return dict(sorted(out.items(), key=lambda kv: (-kv[1], kv[0])))


def proposal(session_id, block_set):
    """The lesson: a candidate stricter mode that would deny *exactly* the
    would-block set — or nothing, when there is no evidence. The fold proposes;
    it never installs, and the cut stays bdo's (D-4).

    The refusal with teeth: an empty block set yields `proposed: False` and an
    empty `guards` list. A mode is never invented from no readings — if this
    ever proposed under no evidence, the fold would be fabricating."""
    guards = [{"rule": rule, "evidence_count": n} for rule, n in block_set.items()]
    if not guards:
        return {
            "proposed": False,
            "guards": [],
            "reason": ("no would-deny readings on this session — nothing to "
                       "propose; the fold refuses to invent a mode from no "
                       "evidence"),
        }
    return {
        "proposed": True,
        "guards": guards,
        # named, not installed: the candidate posture this evidence supports
        "candidate_mode": "guarded",
        "scope": session_id,
        "admits_only": "bdo",
        "reason": (f"{len(guards)} fence rule(s) fired in training; a stricter "
                   "mode that denies exactly these is supported by the trace"),
    }


def fold_session(root, session_id):
    """The whole fold for one training session: its readings, profile,
    would-block set, and proposal. Pure — reads the truth log (for the opener)
    and the sensor trace (for the readings); writes nothing."""
    fold = Fold(root)
    opener = next((s for s in training_sessions(fold) if s["id"] == session_id), None)
    readings_raw, _dropped = read_jsonl(sensor_path(root))
    readings = [r for r in readings_raw if r.get("train_session") == session_id]
    block = would_block_set(readings)
    return {
        "session": session_id,
        "opener": opener,
        "op_count": len(readings),
        "would_deny_count": sum(1 for r in readings if r.get("status") == "would-deny"),
        "profile": profile(readings),
        "would_block_set": block,
        "proposal": proposal(session_id, block),
    }


def overview(root):
    """The read-only summary: every known training session and its op count
    (readings stamped with its id on the sensor trace)."""
    fold = Fold(root)
    sessions = training_sessions(fold)
    readings_raw, _dropped = read_jsonl(sensor_path(root))
    counts = {}
    blocks = {}
    for r in readings_raw:
        ts = r.get("train_session")
        if ts is None:
            continue
        counts[ts] = counts.get(ts, 0) + 1
        if r.get("status") == "would-deny":
            blocks[ts] = blocks.get(ts, 0) + 1
    for s in sessions:
        s["op_count"] = counts.get(s["id"], 0)
        s["would_deny_count"] = blocks.get(s["id"], 0)
    return {"sessions": sessions}


def render_overview(d):
    lines = ["# Training sessions", ""]
    sessions = d["sessions"]
    if not sessions:
        lines += ["_No training sessions on record — no `security_mode` admission "
                  "has opened train. Absence is information._", ""]
        return "\n".join(lines)
    for s in sessions:
        state = "closed" if s["closed"] else "open"
        lines.append(
            f"- `{s['id']}` — {s['mode']}, scope {s['session']}, by {s['by']} "
            f"({state}); {s['op_count']} op(s) recorded, {s['would_deny_count']} "
            "would-deny")
    lines += ["", "_Run `python -m loop.train --session <id>` for a session's "
              "profile and proposed mode._"]
    return "\n".join(lines)


def render_session(d):
    lines = [f"# Training session `{d['session']}`", ""]
    op = d["opener"]
    if op is None:
        lines += [f"_No `security_mode` admission with this id — it is not a known "
                  "training session. (A reading's `train_session` is the opening "
                  "admission id.)_", ""]
    else:
        state = "closed" if op["closed"] else "open"
        lines += [f"_opened by {op['by']} for scope {op['session']} ({state})_", ""]

    lines.append(f"## Profile — {d['op_count']} operation(s)")
    if d["op_count"] == 0:
        lines.append("- _no readings stamped with this session — nothing observed._")
    else:
        intent = d["profile"]["by_intent"]
        lines.append("- by intent: " + ", ".join(
            f"{k} {v}" for k, v in intent.items() if v) or "- by intent: none")
        surf = d["profile"]["by_surface"]
        if surf:
            lines.append("- by surface: " + ", ".join(
                f"{k or 'unknown'} {v}" for k, v in surf.items()))
    lines.append("")

    block = d["would_block_set"]
    lines.append(f"## Would-block set — {d['would_deny_count']} would-deny reading(s)")
    if not block:
        lines.append("- _empty: normal mode would have denied nothing this session._")
    else:
        for rule, n in block.items():
            lines.append(f"- `{rule}` — {n} time(s)")
    lines.append("")

    p = d["proposal"]
    lines.append("## Proposal")
    if not p["proposed"]:
        lines += [f"- **nothing to propose.** {p['reason']}.",
                  "- The fold proposes only what the evidence supports; with no "
                  "would-deny readings there is no mode to propose (no evidence, "
                  "no mint)."]
    else:
        lines.append(f"- **candidate stricter mode `{p['candidate_mode']}`** "
                     f"(scope {p['scope']}) — would deny exactly the would-block set:")
        for g in p["guards"]:
            lines.append(f"    - `{g['rule']}` (seen {g['evidence_count']}×)")
        lines += ["- This is a **proposal only**. Installing a posture that "
                  "tightens the guard is a security-mode change, and that is "
                  "bdo's alone to admit (D-4) — `--by bdo`. This fold writes "
                  "nothing; it names the door, it does not walk through it."]
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    ap.add_argument("--session", help="a training session id (opening "
                    "security_mode admission) to profile and propose from")
    ap.add_argument("--json", action="store_true",
                    help="emit the raw dataset (machine-readable), not the prose")
    args = ap.parse_args(argv)

    if args.session:
        d = fold_session(args.root, args.session)
        if args.json:
            print(canon(d))
        else:
            print(render_session(d))
        if d["proposal"]["proposed"]:
            n = len(d["proposal"]["guards"])
            print(f"\nresult: needs-you — a stricter mode guarding {n} rule(s) is "
                  "proposed from this session's trace; admitting it is bdo's "
                  "(--by bdo, D-4). Proposed, not installed.")
        else:
            print("\nresult: report — no would-deny readings on this session; "
                  "nothing to propose (the fold refuses to invent a mode from "
                  "no evidence).")
        return 0

    d = overview(args.root)
    if args.json:
        print(canon(d))
    else:
        print(render_overview(d))
    n = len(d["sessions"])
    if n == 0:
        print("\nresult: report — no training sessions on record.")
    else:
        print(f"\nresult: report — {n} training session(s); "
              "`--session <id>` reads one's profile and proposed mode.")
    return 0


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
