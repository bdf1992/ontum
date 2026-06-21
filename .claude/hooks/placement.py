#!/usr/bin/env python3
"""Placement: the deterministic cross-ref address check (done-line 0022).

The records pen (loop/pen.py) and the write guard both fold record ids over
the LOCAL directory only — blind to sibling branches in the shared-tree
fleet. So two branches mint the same id and neither notices: the colliding
0020 done-lines (git-commit-pen, reflection-automates, editor-fidelity-gate,
and story-gate before it was renumbered) are the live case. This folds
numbered-record ids over ALL git refs, so an address already claimed
anywhere in the fleet is seen before a third branch claims it again.

Reading git refs is reach beyond the append-only log, so the git-touching
judge lives here under .claude/, never in pure-stdlib loop/ (the reflect
split: the fold is data, the reach is a pen). Fail-open: no git, no refs,
or any error and it behaves as if only the local directory is known — a
broken sensor must never block work.

Stdlib only. Every run ends with a clear result: report | needs-you.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys
from collections import defaultdict

NUMBERED = re.compile(r"(\d{4})-")  # the id prefix of a numbered record


def repo_root():
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, encoding="utf-8", errors="replace")
        if out.returncode == 0 and out.stdout.strip():
            return pathlib.Path(out.stdout.strip())
    except OSError:
        pass
    return pathlib.Path(__file__).resolve().parents[2]


def _git(root, args):
    """Run a read-only git command from the repo root; '' on any failure."""
    try:
        out = subprocess.run(
            ["git"] + args, cwd=str(root), capture_output=True, text=True,
            encoding="utf-8", errors="replace")
        return out.stdout if out.returncode == 0 else ""
    except OSError:
        return ""


def _reldir(root, dirpath):
    d = pathlib.Path(dirpath).resolve()
    try:
        return d.relative_to(root.resolve()).as_posix()
    except ValueError:
        return pathlib.Path(dirpath).as_posix()


def _worktree_dirs(root):
    """Every working tree of this repo (``git worktree list``). The allocator
    must see a SIBLING worktree's uncommitted record, not just the current
    checkout's — the concurrent-mint blind spot: two worktrees mint the same id
    before either commits, and only the commit-check catches it (the 0149
    collision, two parallel sessions). Falls back to the current checkout if
    git can't list worktrees (fail-open)."""
    out = _git(root, ["worktree", "list", "--porcelain"])
    paths = [pathlib.Path(line[len("worktree "):].strip())
             for line in out.splitlines() if line.startswith("worktree ")]
    return paths or [pathlib.Path(root)]


def claims(dirpath, root=None):
    """Fold the fleet: id -> {filename -> set(refs claiming it)}.

    Every ref's tree plus EVERY worktree's working directory, so an uncommitted
    record — in this checkout or a sibling worktree — is counted against
    committed siblings too."""
    root = root or repo_root()
    rel = _reldir(root, dirpath)
    seen: dict = defaultdict(lambda: defaultdict(set))
    refs = [r for r in _git(
        root, ["for-each-ref", "--format=%(refname)",
               "refs/heads", "refs/remotes"]).splitlines() if r.strip()]
    for ref in refs:
        for path in _git(
                root, ["ls-tree", "-r", "--name-only", ref, "--", rel]).splitlines():
            name = path.rsplit("/", 1)[-1]
            m = NUMBERED.match(name)
            if m:
                seen[m.group(1)][name].add(ref)
    # Every worktree's working tree, not just the current checkout (dirpath):
    # a sibling worktree's uncommitted mint is invisible to refs and to this
    # checkout's dir, and that invisibility is what lets two worktrees pick one
    # id. The current dirpath is one of these worktrees, so it is still counted.
    for wt in _worktree_dirs(root):
        wdir = wt / rel
        if not wdir.is_dir():
            continue
        label = "(working tree)" if wt.resolve() == root.resolve() \
            else f"(worktree: {wt.name})"
        for p in wdir.iterdir():
            m = NUMBERED.match(p.name)
            if m:
                seen[m.group(1)][p.name].add(label)
    return seen


def collisions(dirpath, root=None):
    """An id claimed by more than one distinct filename across the fleet —
    the same address, two different records. That is what must refuse to
    fit."""
    return {iid: dict(files) for iid, files in claims(dirpath, root).items()
            if len(files) > 1}


def next_id(dirpath, root=None):
    """The fleet-safe next id: one past the highest claimed on ANY ref, not
    just the highest on disk locally."""
    ids = [int(i) for i in claims(dirpath, root)]
    return max(ids) + 1 if ids else 1


# ----------------------------------------------------------------- runtime

def cmd_check(ns):
    found = collisions(ns.dir)
    if not found:
        print(f"result: report — no address collisions in {ns.dir} across the fleet")
        return 0
    for iid in sorted(found):
        where = "; ".join(
            f"{name} ({', '.join(sorted(refs))})"
            for name, refs in sorted(found[iid].items()))
        print(f"collision {iid}: {where}")
    print(f"result: needs-you — {len(found)} colliding address(es) in {ns.dir}; "
          "two records claim one id — renumber the later one to "
          f"{next_id(ns.dir):04d} or higher (the fleet-safe next id)")
    return 1


def cmd_next(ns):
    nid = next_id(ns.dir)
    if getattr(ns, "quiet", False):
        print(f"{nid:04d}")  # machine output: the records pen parses this
    else:
        print(f"result: report — fleet-safe next id in {ns.dir} is {nid:04d}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="report ids claimed by >1 record across all refs")
    c.add_argument("dir", help="a numbered-record directory, e.g. .ai-native/done")
    c.set_defaults(func=cmd_check)
    n = sub.add_parser("next", help="the fleet-safe next id (folds all refs, not just local)")
    n.add_argument("dir")
    n.add_argument("--quiet", action="store_true",
                   help="print only the zero-padded id (for tooling, e.g. the records pen)")
    n.set_defaults(func=cmd_next)
    ns = ap.parse_args(argv)
    return ns.func(ns)


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
