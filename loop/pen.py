#!/usr/bin/env python3
"""The records pen (done-line 0013): deterministic creation for numbered
record directories.

Two sessions allocated done-line 0011 within eleven minutes of each
other — id allocation by eyeball is a race. This pen folds over the
directory to allocate the next id, scaffolds the required sections from
the directory's control config (`.pen.json`), and writes LF bytes. The
config is the form; the write guard (`.claude/hooks/write_guard.py`) is
the enforcement; this pen is the paved path through it.

Stdlib only. Ends with a clear result on stdout (D-6): report | needs-you.
"""

import argparse
import json
import re
import sys
from pathlib import Path

# the supersede ritual records its act on the log; the loop's one append
# (done-line 0033). Imported lazily inside the verb so the creation paths
# stay pure stdlib + filesystem and never depend on the fold to write a file.

ALIASES = {
    "done": Path(".ai-native/done"),
    "report": Path(".ai-native/reports"),
    "reports": Path(".ai-native/reports"),
}
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]*$")
NUMBERED = re.compile(r"^(\d{4})-")


def resolve_dir(kind_or_path):
    return ALIASES.get(kind_or_path, Path(kind_or_path))


def load_config(dirpath):
    cfg = dirpath / ".pen.json"
    if not cfg.exists():
        return None
    return json.loads(cfg.read_text(encoding="utf-8"))


def next_id(dirpath):
    """The fold: the next id is one past the highest on disk — never
    re-used, never guessed (two 0011s taught us)."""
    ids = [int(m.group(1)) for p in dirpath.iterdir()
           for m in [NUMBERED.match(p.name)] if m]
    return max(ids) + 1 if ids else 1


def new(kind_or_path, slug, title, body=None):
    dirpath = resolve_dir(kind_or_path)
    if not dirpath.is_dir():
        print(f"result: needs-you — {dirpath} is not a directory here; "
              f"kinds: {', '.join(sorted(set(ALIASES)))} (run from the repo root)")
        return 2
    cfg = load_config(dirpath)
    if cfg is None:
        print(f"result: needs-you — {dirpath} carries no .pen.json control "
              "config; this pen only writes where the place declares its form")
        return 2
    if not SLUG.match(slug):
        print(f"result: needs-you — slug {slug!r} doesn't fit [a-z0-9-]; "
              "the filename is an address, keep it boring")
        return 2
    iid = next_id(dirpath)
    name = f"{iid:04d}-{slug}.md"
    target = dirpath / name
    if target.exists():  # the fold makes this near-impossible; refuse anyway
        print(f"result: needs-you — {target} already exists; the fold and the "
              "directory disagree, look before writing")
        return 2
    if body is None:
        # a frozen records dir is write-once: freeze_guard denies the Edit
        # that would fill a scaffolded stub, so scaffold-then-fill is a dead
        # path here. Refuse it at the source — bring the whole thing via
        # --body, in one move (done-line 0057). Non-frozen dirs scaffold as
        # before; the fix lives entirely here, not in the guard.
        if cfg.get("frozen"):
            sections = cfg.get("required_sections", [])
            need = (f" (required section(s): {', '.join(sections)})"
                    if sections else "")
            print(f"result: needs-you — {dirpath.as_posix()} is a frozen, "
                  "write-once records directory: a scaffolded fill-later stub "
                  "would be frozen the instant it is written, and the Edit to "
                  "fill it in is denied by freeze_guard. Bring the complete "
                  f"content in one move with --body{need}; the form is "
                  f"{(dirpath / '.pen.json').as_posix()}. Nothing was written.")
            return 2
        text = "\n".join(cfg["scaffold"]).format(
            id=f"{iid:04d}", slug=slug, title=title or slug.replace("-", " "))
        note = "; fill the placeholders before committing"
    else:
        # one-move mint: the pen owns the id-bearing heading (scaffold's
        # first line), the caller brings the rest — and the form still holds
        heading = cfg["scaffold"][0].format(
            id=f"{iid:04d}", slug=slug, title=title or slug.replace("-", " "))
        text = heading + "\n\n" + body.strip("\n") + "\n"
        missing = [s for s in cfg.get("required_sections", []) if s not in text]
        if missing:
            print("result: needs-you — the body is missing required "
                  f"section(s): {', '.join(missing)}; the form is "
                  f"{(dirpath / '.pen.json').as_posix()}")
            return 2
        note = ""
    if not text.endswith("\n"):
        text += "\n"
    target.write_bytes(text.encode("utf-8"))  # LF bytes: identity-safe
    print(f"result: report — created {target.as_posix()} (id {iid:04d}){note}")
    return 0


def find_done(dirpath, abandoned):
    """The existing done-line file for an id (any spelling: 31, 0031), or
    None. You cannot abandon a bar that was never set."""
    m = re.search(r"\d+", str(abandoned))
    if not m:
        return None
    want = f"{int(m.group(0)):04d}"
    for p in dirpath.iterdir():
        hit = NUMBERED.match(p.name)
        if hit and hit.group(1) == want:
            return p
    return None


MIN_REFLECTION = 40  # a glib excuse is not a reflection — the bar must hurt


def supersede_done(kind_or_path, abandoning, slug, done_when, reason, by,
                   title=None, root=None):
    """The only way to change what "done" meant (done-line 0033) — and it
    is bdo's alone. A written done-line is frozen (freeze_guard); to move
    the bar you do not edit it, you ABANDON it loudly and additively: the
    original stands forever as history, a NEW line carries the new bar
    *and* the reflection on why the old one failed, recorded as a
    `done_superseded` admission. A session is refused outright here, before
    anything is written — letting a session author even a *pending* new bar
    would be a free "stop working" card (no one signs their own line, D-4).
    A blocked session surfaces the bad bar in its report and keeps working;
    bdo supersedes it himself if he agrees. Stdlib + the one log append."""
    from loop.reconcile import append_line, now_ts, short_hash

    dirpath = resolve_dir(kind_or_path)
    if not dirpath.is_dir():
        print(f"result: needs-you — {dirpath} is not a directory here "
              "(run from the repo root)")
        return 2
    cfg = load_config(dirpath)
    if cfg is None or not cfg.get("frozen"):
        print(f"result: needs-you — {dirpath} is not a frozen records "
              "directory; supersede is the ritual for frozen contracts only")
        return 2
    if (by or "").strip().lower() != "bdo":
        print("result: needs-you — moving a done-line is bdo's alone (D-4). A "
              "session does not get to change what done meant — that would be a "
              "free 'stop working' card, a new bar you wrote for yourself. If "
              "the bar is genuinely wrong, name it in your report's needs-you "
              "and KEEP WORKING; bdo supersedes it himself if he agrees. "
              "Nothing is written here.")
        return 2
    old = find_done(dirpath, abandoning)
    if old is None:
        print(f"result: needs-you — no done-line {abandoning!r} in "
              f"{dirpath.as_posix()}; you cannot abandon a bar that was "
              "never set")
        return 2
    if not SLUG.match(slug or ""):
        print(f"result: needs-you — slug {slug!r} doesn't fit [a-z0-9-]")
        return 2
    if not (done_when or "").strip():
        print("result: needs-you — --done is required: a supersede still sets "
              "a bar, it does not remove one")
        return 2
    reason = (reason or "").strip()
    if len(reason) < MIN_REFLECTION:
        print(f"result: needs-you — --reason is the reflection, and it must "
              f"be honest (at least {MIN_REFLECTION} characters). Why could "
              "the bar you set not be met? 'ran out of time' is not a reason; "
              "what about the bar was wrong, or what did the work reveal?")
        return 2

    old_id = NUMBERED.match(old.name).group(1)
    iid = next_id(dirpath)
    name = f"{iid:04d}-{slug}.md"
    target = dirpath / name
    if target.exists():
        print(f"result: needs-you — {target} already exists; the fold and the "
              "directory disagree, look before writing")
        return 2
    heading = cfg["scaffold"][0].format(
        id=f"{iid:04d}", slug=slug, title=title or slug.replace("-", " "))
    body = (
        f"Written before code, per §9.4. When this line is met, stop.\n\n"
        f"**This line SUPERSEDES done-line {old_id}** — a bar set before the "
        f"work, then abandoned. The original stands as history; the shame is "
        f"recorded, not erased.\n\n"
        f"> **Why {old_id} was abandoned:** {reason}\n\n"
        f"> **Done when:** {done_when.strip()}\n"
    )
    text = heading + "\n\n" + body
    missing = [s for s in cfg.get("required_sections", []) if s not in text]
    if missing:
        print("result: needs-you — the new line is missing required "
              f"section(s): {', '.join(missing)}")
        return 2
    target.write_bytes(text.encode("utf-8"))  # LF bytes: identity-safe

    # only bdo reaches here (the gate above refuses every session), so a
    # supersede on the record is always the owner's own act — there is no
    # session-authored bar, pending or otherwise (D-4)
    adm = {
        "id": "adm." + short_hash("done_superseded", old_id, name, str(by), now_ts()),
        "type": "done_superseded",
        "abandoned": old_id,
        "abandoned_path": old.as_posix(),
        "new_line": target.as_posix(),
        "reason": reason,
        "by": by,
        "authorized": True,
        "authorized_by": "bdo",
        "ts": now_ts(),
    }
    append_line(dirpath.parent / "log" / "admissions.jsonl", adm)
    print(f"result: report — done-line {old_id} superseded by "
          f"{target.as_posix()} (id {iid:04d}), by bdo. The original stands "
          f"as history; the abandonment is on the record ({adm['id']}).")
    return 0


# --------------------------------------------------------------- whiteout
# The Whiteout pen (done-line 0064): correction fluid for the log. It LEAVES
# A MARK (a visible superseding append, never an edit), you can STILL SEE
# UNDER IT (the original stays on the append-only log; the fold reads the
# chain now/covered/why), and it does NOT work on HUGE mistakes (a target
# anything downstream has consumed is un-whiteoutable — that needs a retro
# or bdo's hand, not correction fluid). It is the generalization of
# supersede_done into a bounded, marked, general correction: supersede_done
# is the specific, owner-gated whiteout of a frozen done-line; this is the
# session-usable whiteout of an ordinary log record, refused the moment a
# correction would lie about a past that already propagated.
WHITEOUT = "whiteout"  # the admission type a correction writes


def _refs_value(rec, needle):
    """True if ``needle`` appears as a value anywhere inside ``rec`` — walks
    nested dicts/lists. This is how the consumption test asks 'did this later
    record cite the target's id', without knowing which field carried the
    reference (event_id, authorized_by, cites, abandoned, …)."""
    if isinstance(rec, dict):
        return any(_refs_value(v, needle) for v in rec.values())
    if isinstance(rec, list):
        return any(_refs_value(v, needle) for v in rec)
    return rec == needle


def find_log_record(fold, record_id):
    """The record ``record_id`` names, and which stream it lives on, or
    (None, None). A whiteout cites a real record (the discharge discipline,
    done-line 0063): a pointer at nothing is refused, never honoured."""
    for name, stream in (("events", fold.events),
                         ("receipts", fold.receipts),
                         ("admissions", fold.admissions)):
        for rec in stream:
            if rec.get("id") == record_id:
                return rec, name
    return None, None


def whiteout_of(fold, target_id):
    """The latest whiteout correction for ``target_id``, or None. Latest-wins
    like every superseding admission — a correction can itself be corrected;
    history stays additive, never erased."""
    latest = None
    for adm in fold.admissions:
        if adm.get("type") == WHITEOUT and adm.get("target") == target_id:
            latest = adm
    return latest


def consumers(fold, target):
    """The records that have CONSUMED the target: any record (other than the
    target itself, and other than a whiteout correcting it) that cites the
    target's id. Citation is the pure-log consumption signal — a later record
    built on this exact record (a receipt's ``event_id``, an
    ``authorized_by``, a ``cites`` list…). A correction is not a use, so a
    whiteout pointing at the target never counts as consuming it."""
    tid = target.get("id")
    found = []
    for stream in (fold.events, fold.receipts, fold.admissions):
        for rec in stream:
            if rec.get("id") == tid:
                continue  # the target itself
            if rec.get("type") == WHITEOUT and rec.get("target") == tid:
                continue  # a correction of the target is not a consumption
            if _refs_value(rec, tid):
                found.append(rec.get("id"))
    return found


def is_terminal(fold, target):
    """True if the target's work already reached the terminal/landed state —
    its atom has the TERMINAL_EVENT on the log, so the value propagated all
    the way through the pipeline. A whiteout here would rewrite a settled
    past; that is a retro's job, not correction fluid. (The git
    'landed-to-main' reach is the deferred extension — it lives under
    .claude/, never in pure-stdlib loop/; this pure-log terminal check is the
    in-substrate half of the same 'already propagated' signal.)"""
    from loop.reconcile import TERMINAL_EVENT
    thash = target.get("artifact_hash")
    if not thash:
        return False
    return fold.event(TERMINAL_EVENT, thash) is not None


def _frozen_done_line(root, target):
    """If ``target`` names a frozen done-line (by path, or by 4-digit id under
    .ai-native/done), return its path. Softening a contract is bdo's
    supersede, never a session's whiteout — so whiteout refuses these
    outright, before it ever folds the log (done-line 0064; the no-free-
    stop-card rule of 0033)."""
    t = (target or "").strip()
    if not t:
        return None
    candidates = []
    p = Path(t)
    if p.is_file():
        candidates.append(p)
    m = re.fullmatch(r"\D*?(\d{4})", t)  # a bare id form like 0033 / done:0033
    done_dir = Path(root) / "done"
    if m and done_dir.is_dir():
        for f in done_dir.iterdir():
            hit = NUMBERED.match(f.name)
            if hit and hit.group(1) == m.group(1):
                candidates.append(f)
    for c in candidates:
        cfg = c.parent / ".pen.json"
        if cfg.exists():
            try:
                if json.loads(cfg.read_text(encoding="utf-8")).get("frozen"):
                    return c
            except ValueError:
                pass
    return None


def whiteout(root, target, correction, reason, by):
    """Append a MARKED correction for a prior log record (done-line 0064).

    Refuses, writing nothing, when:
      - the target is a frozen done-line's bar (that is bdo's supersede — no
        free stop-card, done-line 0033);
      - the target names no record on the log (a whiteout cites a real
        record, the discharge discipline of 0063 — a pointer at nothing);
      - the target is a contract admission (``done_superseded``) — also
        supersede territory;
      - the target has been CONSUMED downstream (a later record cites it, or
        its atom is terminal/landed): a whiteout would lie about a past that
        already propagated, and the refusal names the escalation (a retro, or
        bdo's hand).

    On success it appends one ``whiteout`` admission carrying the cited target,
    a snapshot of what it covers (so a cold reader sees the chain without a
    second lookup), the correction, and the reason — never an edit to the
    original line. Stdlib + the one log append. Returns 0 | 2."""
    from loop.reconcile import Fold, append_line, now_ts, short_hash

    correction = (correction or "").strip()
    reason = (reason or "").strip()
    if not correction:
        print("result: needs-you — a whiteout carries the correction "
              "(--correction): the marked, now-current view that covers the "
              "mistake. Nothing was written.")
        return 2
    if not reason:
        print("result: needs-you — a whiteout carries its reason (--reason): "
              "why the prior record was wrong. The mark is not silent.")
        return 2
    if not (by or "").strip():
        print("result: needs-you — a whiteout is signed (--by) like every "
              "record on the log.")
        return 2

    frozen = _frozen_done_line(root, target)
    if frozen is not None:
        print("result: needs-you — "
              f"{frozen.as_posix()} is a frozen done-line, not an ordinary "
              "record: softening a contract's bar is bdo's supersede, never a "
              "session's whiteout (no free 'stop working' card, done-line "
              "0033). The path is `python -m loop.pen supersede-done "
              "--abandoning <id> --slug <new> --done \"<new bar>\" --reason "
              "\"<honest reflection>\" --by bdo`. Nothing was written.")
        return 2

    fold = Fold(Path(root))
    rec, stream = find_log_record(fold, target)
    if rec is None:
        print(f"result: needs-you — {target!r} is on no log stream (events, "
              "receipts, admissions): a whiteout corrects a real record, never "
              "a pointer at nothing. If you mean a done-line, that is bdo's "
              "supersede. Nothing was written.")
        return 2
    if rec.get("type") == "done_superseded":
        print(f"result: needs-you — {target!r} is a done_superseded admission "
              "— a contract move, bdo's alone (supersede-done). A whiteout does "
              "not correct a contract. Nothing was written.")
        return 2

    cited = consumers(fold, rec)
    terminal = is_terminal(fold, rec)
    if cited or terminal:
        why = []
        if cited:
            why.append("cited by " + ", ".join(sorted(cited)))
        if terminal:
            why.append("its atom reached the terminal/landed state")
        print(f"result: needs-you — record {target!r} has been consumed "
              f"downstream ({'; '.join(why)}): a whiteout here would lie about "
              "a past that already propagated. This is not correction-fluid "
              "territory — escalate. Write a retro (a numbered report in "
              ".ai-native/reports naming what propagated and the correction), "
              "or if it is a frozen contract, bdo's supersede. Nothing was "
              "written.")
        return 2

    adm = {
        # content-derived over (target, signer, correction): a re-run of the
        # same correction in one tick folds to one (I-2).
        "id": "adm." + short_hash(WHITEOUT, target, by, now_ts(), correction),
        "type": WHITEOUT,
        "target": target,
        "target_stream": stream,
        "covered": rec,          # the original, snapshotted for a cold reader
        "correction": correction,  # the now-current view (the mark)
        "reason": reason,        # why
        "by": by,
        "ts": now_ts(),
    }
    append_line(Path(root) / "log" / "admissions.jsonl", adm)
    print(f"result: report — whiteout written for {target} on the {stream} "
          f"stream (correction {adm['id']}, by {by}). The original stands on "
          "the log underneath the mark; read the chain with `python -m "
          f"loop.pen whiteout --target {target} --show`.")
    return 0


def effective_record(fold, record_id):
    """The correction-honouring view of a record (done-line 0064): the fold
    that makes a whiteout's correction the default ``now`` and keeps the
    original foldable underneath as ``covered``, with ``why``. The original is
    never erased — it is still on the log; this only reads the chain. Returns
    {now, covered, why, marked, stream, whiteout_id?} or None if the record is
    on no stream."""
    rec, stream = find_log_record(fold, record_id)
    if rec is None:
        return None
    wo = whiteout_of(fold, record_id)
    if wo is None:
        return {"now": rec, "covered": None, "why": None,
                "marked": False, "stream": stream}
    return {"now": wo.get("correction"), "covered": rec, "why": wo.get("reason"),
            "marked": True, "stream": stream, "whiteout_id": wo.get("id")}


def whiteout_show(root, target):
    """Read-only: print the correction chain (now / covered / why) for a
    record, writing nothing. This is 'seeing under the whiteout'."""
    from loop.reconcile import Fold

    view = effective_record(Fold(Path(root)), target)
    if view is None:
        print(f"result: needs-you — {target!r} is on no log stream; there is "
              "nothing to show.")
        return 2
    if not view["marked"]:
        print(f"result: report — {target} on the {view['stream']} stream is "
              "not whited out; the record stands as written (no mark).")
        return 0
    print(f"result: report — whiteout chain for {target} "
          f"({view['stream']} stream):")
    print(f"  now    (the mark): {view['now']}")
    print(f"  covered (original): "
          f"{json.dumps(view['covered'], sort_keys=True)}")
    print(f"  why    (reason)  : {view['why']}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("new", help="create the next numbered record from the directory's form")
    n.add_argument("kind", help="done | reports | a path to a directory carrying .pen.json")
    n.add_argument("--slug", required=True, help="kebab-case filename part after the id")
    n.add_argument("--title", default=None, help="heading title (defaults to the slug, de-kebabed)")
    n.add_argument("--body", default=None,
                   help="everything after the heading, complete (one-move "
                        "mint); '-' reads stdin; required sections still hold")
    s = sub.add_parser("supersede-done",
                       help="the painful, owner-gated path to change what a "
                            "frozen done-line meant (done-line 0033)")
    s.add_argument("--kind", default="done",
                   help="done | a path to a frozen records directory")
    s.add_argument("--abandoning", required=True,
                   help="the id of the done-line whose bar you are abandoning")
    s.add_argument("--slug", required=True, help="kebab-case filename for the new line")
    s.add_argument("--title", default=None, help="heading title (defaults to the slug)")
    s.add_argument("--done", required=True, dest="done_when",
                   help="the new bar — what done means now")
    s.add_argument("--reason", required=True,
                   help="the honest reflection: why the bar you set could not "
                        "be met (glib excuses are refused)")
    s.add_argument("--by", required=True, help="who is moving the bar")
    w = sub.add_parser("whiteout",
                       help="append a marked, recoverable correction to a prior "
                            "log record (done-line 0064); refuses a consumed target")
    w.add_argument("--target", required=True,
                   help="the id of the log record to correct (a done-line is "
                        "bdo's supersede, not a whiteout)")
    w.add_argument("--correction", default=None,
                   help="the now-current view that covers the mistake")
    w.add_argument("--reason", default=None,
                   help="why the prior record was wrong — the mark is not silent")
    w.add_argument("--by", default=None, help="who is writing the correction")
    w.add_argument("--root", type=Path, default=Path(".ai-native"),
                   help="the records root (defaults to .ai-native)")
    w.add_argument("--show", action="store_true",
                   help="read-only: print the now/covered/why chain, write nothing")
    x = sub.add_parser("next", help="print the next id for a records directory")
    x.add_argument("kind")
    args = ap.parse_args(argv)
    if args.cmd == "new":
        body = sys.stdin.read() if args.body == "-" else args.body
        return new(args.kind, args.slug, args.title, body)
    if args.cmd == "supersede-done":
        return supersede_done(args.kind, args.abandoning, args.slug,
                              args.done_when, args.reason, args.by, args.title)
    if args.cmd == "whiteout":
        if args.show:
            return whiteout_show(args.root, args.target)
        return whiteout(args.root, args.target, args.correction,
                        args.reason, args.by)
    dirpath = resolve_dir(args.kind)
    if not dirpath.is_dir():
        print(f"result: needs-you — {dirpath} is not a directory here")
        return 2
    print(f"result: report — next id in {dirpath.as_posix()} is {next_id(dirpath):04d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
