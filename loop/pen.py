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


def new(kind_or_path, slug, title):
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
    text = "\n".join(cfg["scaffold"]).format(
        id=f"{iid:04d}", slug=slug, title=title or slug.replace("-", " "))
    if not text.endswith("\n"):
        text += "\n"
    target.write_bytes(text.encode("utf-8"))  # LF bytes: identity-safe
    print(f"result: report — created {target.as_posix()} (id {iid:04d}); "
          "fill the placeholders before committing")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("new", help="create the next numbered record from the directory's form")
    n.add_argument("kind", help="done | reports | a path to a directory carrying .pen.json")
    n.add_argument("--slug", required=True, help="kebab-case filename part after the id")
    n.add_argument("--title", default=None, help="heading title (defaults to the slug, de-kebabed)")
    x = sub.add_parser("next", help="print the next id for a records directory")
    x.add_argument("kind")
    args = ap.parse_args(argv)
    if args.cmd == "new":
        return new(args.kind, args.slug, args.title)
    dirpath = resolve_dir(args.kind)
    if not dirpath.is_dir():
        print(f"result: needs-you — {dirpath} is not a directory here")
        return 2
    print(f"result: report — next id in {dirpath.as_posix()} is {next_id(dirpath):04d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
