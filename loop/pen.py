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
import subprocess
import sys
from pathlib import Path

# The fleet-safe id authority is the placement reach-tool under .claude/
# (done-line 0023): it folds record ids over ALL git refs. Git-reach lives
# there, never in pure-stdlib loop/ (placement's own rule), so the pen
# delegates to it by subprocess and never imports git of its own.
_PLACEMENT = Path(__file__).resolve().parents[1] / ".claude" / "hooks" / "placement.py"

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


def _fleet_next_id(dirpath):
    """The fleet-safe next id from the placement reach-tool, or None on any
    failure. Placement folds record ids over every git ref, so the id is
    clear across the whole shared-tree fleet, not just this checkout. The
    pen only delegates: git-reach stays in .claude/placement, and a broken
    sensor returns None so the caller falls back — it never blocks a mint."""
    if not _PLACEMENT.exists():
        return None
    d = Path(dirpath).resolve()
    try:
        out = subprocess.run(
            [sys.executable, str(_PLACEMENT), "next", str(d), "--quiet"],
            cwd=str(d) if d.is_dir() else None,
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=15)
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    m = re.search(r"\b(\d{4})\b", out.stdout)
    return int(m.group(1)) if m else None


def next_id(dirpath):
    """The next id, fleet-safe: one past the highest record id on ANY git
    ref (via the placement reach-tool), falling back to the local
    directory fold when git or placement is unreachable. Local-only
    allocation races a parallel fleet — two sessions minting the same id,
    the colliding 0011s and the 0057/0058/0059 cross-branch renumber saga
    this allocator closes; the commit fence caught those reactively, this
    claims a clear id up front. The write guard already folds the fleet
    this way; now the pen and the guard agree on the next id."""
    fleet = _fleet_next_id(dirpath)
    if fleet is not None:
        return fleet
    ids = [int(m.group(1)) for p in dirpath.iterdir()
           for m in [NUMBERED.match(p.name)] if m]
    return max(ids) + 1 if ids else 1


def _heading_re(cfg, iid, slug):
    """The pen's heading line (scaffold[0]) as a regex with the id pinned,
    the slug pinned, and the title left free — the structural signature the
    pen stamps on every record. Literal text is escaped; {title} becomes a
    wildcard because the caller owns it (the pen defaults it to the de-kebabed
    slug, but accepts any). A scaffold with no {title} is fully pinned."""
    parts = []
    for chunk in re.split(r"(\{id\}|\{slug\}|\{title\})", cfg["scaffold"][0]):
        if chunk == "{id}":
            parts.append(re.escape(f"{iid:04d}"))
        elif chunk == "{slug}":
            parts.append(re.escape(slug))
        elif chunk == "{title}":
            parts.append(r".+")
        else:
            parts.append(re.escape(chunk))
    return re.compile("^" + "".join(parts) + "$")


def carbon_divergences(cfg, name, content, expected_id):
    """The single definition of a faithful pen carbon copy (bdo's write-
    through model, 2026-06-13). A raw Write into a `.pen.json` directory is
    legitimate only if its bytes are what THIS pen would have produced for
    `name`: same fleet-safe id, the pen's heading, the required sections, and
    the LF/UTF-8, newline-terminated bytes `.ai-native` byte-identity depends
    on. Returns a list of human divergences; an empty list means the content
    IS the pen's own output, typed by another hand. The write guard imports
    this so the pen and the guard share ONE definition, never two (I-4) — and
    `new()` self-checks against it, so the pen can never emit a non-copy.

    `expected_id` is supplied by the caller (the guard folds the fleet via
    placement; `new()` passes the id it just claimed) — this stays pure and
    git-free, mirroring the reflect split."""
    problems = []
    pattern = cfg.get("pattern")
    if pattern and not re.match(pattern, name):
        problems.append(f"the name {name!r} does not fit the form {pattern}")
    m = NUMBERED.match(name)
    iid = int(m.group(1)) if m else None
    if iid is not None and expected_id is not None and iid != expected_id:
        problems.append(
            f"the id is {iid:04d} but the fleet-safe next id is "
            f"{expected_id:04d} — the pen claims the id from the fold, it is "
            "not yours to pick")
    if m and cfg.get("scaffold"):
        slug = name[m.end():].rsplit(".", 1)[0]
        first = next((ln for ln in content.splitlines() if ln.strip()), "")
        pinned = iid if iid is not None else 0
        if not _heading_re(cfg, pinned, slug).match(first):
            want = cfg["scaffold"][0].format(
                id=f"{pinned:04d}", slug=slug, title="<title>")
            problems.append(
                f"the first line is not the pen's heading (expected {want!r})")
    missing = [s for s in cfg.get("required_sections", []) if s not in content]
    if missing:
        problems.append("missing required section(s): " + ", ".join(missing))
    if "\r" in content:
        problems.append(
            r"the bytes carry CR (\r) — the pen writes LF only; CRLF breaks "
            "the byte-identity .ai-native depends on")
    if content and not content.endswith("\n"):
        problems.append(
            "the file does not end with a newline — the pen always "
            "terminates with LF")
    return problems


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
    text = text.replace("\r\n", "\n").replace("\r", "\n")  # the pen emits LF only
    if not text.endswith("\n"):
        text += "\n"
    # the pen is the authority for "what a carbon copy is" — so it proves its
    # own output is one (zero divergences). A failure here is a pen bug, never
    # a caller's: surface it rather than write bytes the guard would refuse.
    drift = carbon_divergences(cfg, name, text, iid)
    if drift:
        print("result: needs-you — the pen built a record that fails its own "
              "carbon-copy form (a pen bug): " + "; ".join(drift))
        return 2
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
