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
    x = sub.add_parser("next", help="print the next id for a records directory")
    x.add_argument("kind")
    args = ap.parse_args(argv)
    if args.cmd == "new":
        body = sys.stdin.read() if args.body == "-" else args.body
        return new(args.kind, args.slug, args.title, body)
    if args.cmd == "supersede-done":
        return supersede_done(args.kind, args.abandoning, args.slug,
                              args.done_when, args.reason, args.by, args.title)
    dirpath = resolve_dir(args.kind)
    if not dirpath.is_dir():
        print(f"result: needs-you — {dirpath} is not a directory here")
        return 2
    print(f"result: report — next id in {dirpath.as_posix()} is {next_id(dirpath):04d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
