#!/usr/bin/env python3
"""The session write-posture witness (done-line 0196,
`session-read-write-mode.proposal.md`): a session's most basic posture — was it
a **reader** or a **writer**, and when did it cross? — made a recorded fact at
the cheapest possible grain.

bdo, 2026-06-23: *"We should start every single session in READ only mode, and
turning write on is a named event that happens alongside the first actual
write … when you read, you're good… for now."* Every session is born read-only;
a session's first deliberate write is preceded by a `session_write_on` line on
the log that names the read → write crossing. So a session's posture is never a
stored flag — it is a **fact folded from the log** (the log is truth; everything
else is a fold). A session that only reads writes no such record and never
appears as a writer.

This is the **witness** increment — the record + the pen + the read-only fold.
It **stops nothing and breaks nothing**: there is no gate, no guard, no fence
here. The consequence-fence under policy (the L1 `append_line` chokepoint + the
L2 working-tree/log-diff observer, with the full bypass red-team suite) is
**increment 2**, named in the proposal, not built here (witness before
actuator, the `heal`/`consequence_graph` discipline).

What this is, and is NOT:

  - It is the **session** axis of the substrate's self-sensing, the sibling
    `gradient.py` (the *act* axis: respond/retune/author) and `forest.py` (the
    *work-item* axis: parked/stranded/merged) do not carry.
  - It is **not** a permission system: read mode is a *state*, not a
    *prohibition*; the crossing is *recorded*, not *gated-against* (increment 2).
  - It does **not** mint a session identity — the local Claude `session_id`
    already exists (the transcript + `~/.claude/ontum-sessions.json`, the
    `watcher.load_registry` reader, reused here, not re-implemented, I-4). The
    posture attaches to that existing id.
  - The `write_posture` axis (`reader | writer`) is deliberately **not** named
    `mode` — `reconcile.active_mode` already means the `normal`/`train`
    *security* posture; the two never collide (the proposal's CTA-4).

The narration is the heart (CTA-5): a `session_write_on` does not say "1" — it
carries a warm, first-person **monologue** a cold reader can pick up
(justification for picking up the pen · the way you'll write · authorship
context). The pen checks the narration is **present and non-empty**; it never
judges its quality (a cold-reader's call, never machine-gated).

The `write-on` pen is the **one write path** (I-2): it appends through
`reconcile.append_line` (line-atomic, torn-tail tolerant) and is **write-once**
— a second declaration for a session that already crossed is a no-op (the
`node.py` write-once discipline). Read-only, stdlib only; every CLI invocation
ends with a clear `done | report | needs-you` line (D-6).
"""

import argparse
import os
import sys
from pathlib import Path

from loop.reconcile import DEFAULT_ROOT, Fold, append_line, now_ts, short_hash
from loop.watcher import load_registry

# The one new log shape, and the env the local Claude session id is read from
# (confirmed present in-process). One door, no `--session-id` to forget.
WRITE_ON = "session_write_on"
SESSION_ENV = "CLAUDE_CODE_SESSION_ID"


def resolve_session_id(env=None):
    """This session's local Claude id from the environment, or None if unset.
    `env` is injected so the §10 teeth can drive the unset path."""
    src = os.environ if env is None else env
    return (src.get(SESSION_ENV) or "").strip() or None


def write_on_records(fold):
    """`{session_id: the FIRST session_write_on for it}` — a single linear pass
    over the events (bounded, never quadratic). Write-once: the first crossing
    per session wins, so a (refused) second declaration never displaces it.
    The one shared reader the pen and the fold both cross against (no second
    definition of "has this session crossed", I-4)."""
    out = {}
    for ev in fold.events:
        if ev.get("type") == WRITE_ON:
            sid = ev.get("session_id")
            if sid and sid not in out:
                out[sid] = ev
    return out


def write_on(root, session_id, narration, by=None, emergency=False,
             triggering_act=None):
    """Append one `session_write_on` for this session — the read → write
    crossing — or no-op if the session already crossed (write-once, I-2).

    Returns `(record, created)`: `created` is True on a fresh append, False on
    the write-once no-op (the record returned is the existing one). Returns
    `(None, False)` on a refusal, having printed the `needs-you` line — an
    unset session id or an empty narration is refused at the door (the witness
    will not invent an id, and a blank narration defeats the whole habit)."""
    if not (session_id or "").strip():
        print(f"result: needs-you — no session id: ${SESSION_ENV} is unset, and "
              "the witness will not invent one (declare from a real session)")
        return None, False
    if not (narration or "").strip():
        print("result: needs-you — narration required: name your justification "
              "for picking up the pen, the way you'll write, the authorship "
              "context (a warm monologue a cold reader can pick up)")
        return None, False

    fold = Fold(root)
    existing = write_on_records(fold).get(session_id)
    if existing is not None:
        return existing, False  # write-once: already crossed, no second line

    rec = {
        # deterministic per session: a re-run mints the same id, so even a
        # racing double-append dedups to one (write-once belt and suspenders).
        "id": "swon." + short_hash(WRITE_ON, session_id),
        "type": WRITE_ON,
        "session_id": session_id,
        "by": (by or session_id),
        "ts": now_ts(),
        "narration": narration.strip(),
        "emergency": bool(emergency),
        "triggering_act": triggering_act,
    }
    append_line(root / "log" / "events.jsonl", rec)
    return rec, True


def posture(root, registry=None, session=None):
    """The read: per-session `write_posture` (`reader | writer`), crossing the
    **local session set** against the `session_write_on` records.

    Bounded by construction — one linear pass over the events to fold the
    crossings, one over the (already-pruned) registry; never the quadratic
    session × record scan (the `trespass_count` grain). `registry` is injected
    so the fold never has to touch the real `~/.claude` registry under test.
    `session` scopes the read to a single id (the cheap hot-path read) when
    given. Returns None when there is no log on this root (absence, not a false
    all-reader census)."""
    if not (Path(root) / "log").is_dir():
        return None
    fold = Fold(root)
    writeons = write_on_records(fold)
    reg = registry if registry is not None else load_registry()

    # the known session set: the local registry ∪ every session that crossed.
    # a writer whose registry entry was pruned still reads as a writer — the
    # crossing is truth, the registry only a convenience.
    sids = set(reg) | set(writeons)
    if session is not None:
        sids = {session} & sids if session in sids else {session}

    sessions = []
    for sid in sorted(sids):
        wo = writeons.get(sid)
        sessions.append({
            "session_id": sid,
            "write_posture": "writer" if wo else "reader",
            "crossed_at": wo.get("ts") if wo else None,
            "emergency": bool(wo.get("emergency")) if wo else False,
            "by": wo.get("by") if wo else None,
            "triggering_act": wo.get("triggering_act") if wo else None,
            "narration": wo.get("narration") if wo else None,
            "in_registry": sid in reg,
        })
    writers = sum(1 for s in sessions if s["write_posture"] == "writer")
    return {
        "sessions": sessions,
        "census": {
            "total": len(sessions),
            "writers": writers,
            "readers": len(sessions) - writers,
        },
    }


def render(data, here=None):
    """Print the per-session posture and the reader/writer census. `here` is
    this session's id, if known — so the session *knows* its own posture (the
    proposal's "it knows", the read-only half; the ambient briefing is
    increment 2)."""
    for s in data["sessions"]:
        mark = " ← you" if here and s["session_id"] == here else ""
        line = f"session {s['session_id']}: {s['write_posture'].upper()}{mark}"
        if s["write_posture"] == "writer":
            tag = " (emergency)" if s["emergency"] else ""
            line += f" — crossed {s['crossed_at']}{tag}, by {s['by']}"
        if not s["in_registry"]:
            line += " [crossed; not in local registry]"
        print(line)
        if s["narration"]:
            print(f"  narration: {s['narration']}")
    c = data["census"]
    print(f"census: {c['writers']} writer(s), {c['readers']} reader(s) "
          f"of {c['total']} known session(s)")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    ap.add_argument("--json", action="store_true", help="emit the raw dataset")
    ap.add_argument("--session", default=None,
                    help="scope the read to one session id (the cheap read)")
    sub = ap.add_subparsers(dest="cmd")

    w = sub.add_parser("write-on",
                       help="declare this session's read → write crossing")
    w.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    w.add_argument("--narration", required=True,
                   help="the warm first-person monologue (justification · the "
                        "way you'll write · authorship context)")
    w.add_argument("--emergency", action="store_true",
                   help="a hurried crossing: recorded alongside the write, never silent")
    w.add_argument("--by", default=None,
                   help="the author (defaults to the session id)")
    w.add_argument("--triggering-act", default=None,
                   help="the write this crossing precedes (file / atom / pen)")
    args = ap.parse_args(argv)

    if args.cmd == "write-on":
        session_id = resolve_session_id()
        rec, created = write_on(args.root, session_id, args.narration,
                                by=args.by, emergency=args.emergency,
                                triggering_act=args.triggering_act)
        if rec is None:
            return 2  # refusal already printed
        if not created:
            print(f"result: report — session {rec['session_id']} already declared "
                  f"write-on ({rec['id']}); no-op (write-once, I-2)")
            return 0
        tag = " (emergency)" if rec["emergency"] else ""
        print(f"result: report — {rec['id']}: session {rec['session_id']} crossed "
              f"into WRITE mode{tag} — its crossing is on the ledger")
        return 0

    # default: the read-only fold
    data = posture(args.root, session=args.session)
    if data is None:
        print("result: report — no log on this root; no posture to read")
        return 0
    if args.json:
        import json
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    render(data, here=resolve_session_id())
    c = data["census"]
    print(f"result: report — {c['writers']} writer(s), {c['readers']} reader(s); "
          "a reader is a known local session with no write-on (witness-only, "
          "stops nothing)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
