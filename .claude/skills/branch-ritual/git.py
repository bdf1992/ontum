#!/usr/bin/env python3
"""The git pen — the one way a session stages or commits in this repo.

Done-line 0020. The git wrapper, mirroring the gh wrapper (pr.py beside
this file): raw mutating git is denied by the command_guard PreToolUse
hook and routed here, the way raw `gh pr` mutations are routed to the PR
pen. First cut is the two highest-risk verbs in the shared-tree fleet —
`add` and `commit` — where a single `git add .` would sweep in another
session's uncommitted work (the parallel-fleet hazard). Read-only git
(`status` / `log` / `diff`) stays raw-and-watched, exactly as `gh pr
list` does; this pen does not stand between a session and looking.

The spine bdo admitted (three refusals the pen owns, not passthrough):

  explicit-path  no sweep — `add .` / `-A` / `-u`, `commit -a` are
                 refused; name the paths or the commit names them.
  real message   a commit carries a step-shaped message (-m), never an
                 editor that hangs, never empty.
  never the trunk a session commits on its claude/* branch; main is
                 bdo's stamp (firm — the same line pr.py holds for push).

Everything else git add / git commit take is forwarded for parity — a
branded tool that loses features invites the workaround it exists to
prevent (the lesson pr.py push records, changelog 0.4.0).

Stdlib only. Every invocation ends with a clear stdout result:
done | report | needs-you. A refusal is a `report` — it tells the
session what the act is missing; nothing here escalates to bdo.
"""

from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
PEN = "python .claude/skills/branch-ritual/git.py"
TRUNK = ("main", "master")
END_STATES = ("done", "report", "needs-you")

# Tokens that stage more than the session named — the shared-tree hazard.
ADD_SWEEPS = {".", "*", "-A", "--all", "-u", "--update", ":/", ":(top)"}
ADD_INTERACTIVE = {"-i", "--interactive", "-p", "--patch", "-e", "--edit"}
# git commit: -a/--all auto-stages every tracked change (the sweep) and is
# refused; -i/--include and -o/--only are path-scoped (you name the paths)
# and stay allowed. -p/--patch, --interactive and -e/--edit open a TTY a
# hook-driven session does not have.
COMMIT_SWEEPS = {"-a", "--all"}
COMMIT_INTERACTIVE = {"-p", "--patch", "--interactive", "-e", "--edit"}


# ------------------------------------------------------------- pure refusals
# Mirrors pr.py's push_refusal / forward_refusal: the *reasons* an act may
# not happen are pure functions over their inputs, so the test suite hits
# them directly without driving git.

def add_refusal(tokens):
    """Why this `git add` may not run, or None. `tokens` is everything
    after `add`."""
    paths = []
    for token in tokens:
        bare = token.strip("'\"")
        if bare in ADD_SWEEPS:
            return (
                f"no sweep: `{bare}` stages more than you named — in the "
                "shared-tree fleet it pulls in another session's uncommitted "
                f"work. Name the paths: {PEN} add <path> <path>"
            )
        if bare in ADD_INTERACTIVE:
            return f"`{bare}` is interactive and cannot run here (no TTY) — name the paths instead"
        if not bare.startswith("-"):
            paths.append(bare)
    if not paths:
        return (
            "name at least one path to stage — explicit paths only "
            "(the shared-tree fleet; `add .` / `-A` / `-u` are refused)"
        )
    return None


def commit_refusal(branch, message, forwarded):
    """Why this `git commit` may not run, or None.

    `branch` is the current branch, `message` the list of -m values,
    `forwarded` every other token handed to commit.
    """
    if not branch:
        return "detached HEAD — a session commits on its claude/* branch, not a loose HEAD"
    if branch in TRUNK:
        return (
            f"never commit the trunk ('{branch}') — work lands on the session's "
            "claude/* branch; main carries only bdo's stamp (firm)"
        )
    has_file = False
    for token in forwarded:
        bare = token.strip("'\"")
        if bare in COMMIT_SWEEPS:
            return (
                f"no `{bare}`: it auto-stages every tracked change — in the "
                "shared-tree fleet that sweeps in another session's work. "
                f"Stage named paths first ({PEN} add ...) or pass them to commit"
            )
        if bare in COMMIT_INTERACTIVE:
            return f"`{bare}` is interactive and cannot run here (no TTY)"
        if bare == "--allow-empty-message":
            return "a commit carries a real message — --allow-empty-message is refused"
        if bare in ("-F", "--file"):
            has_file = True  # a message from a file is still a real message
    if not has_file and not (message and "".join(message).strip()):
        return (
            "a commit needs a real message: -m \"<what landed>\" (or -F <file>) "
            "— step-shaped, say what landed, not where it sat"
        )
    return None


# ------------------------------------------------------------------- runtime

def _refuse(message):
    print(f"result: report — refused: {message}")
    sys.exit(1)


def _run(args):
    proc = subprocess.run(
        args, capture_output=True, text=True, encoding="utf-8",
        errors="replace", cwd=ROOT,
    )
    if proc.returncode != 0:
        _refuse(f"`{' '.join(args)}` failed:\n{(proc.stderr or proc.stdout).strip()}")
    return proc.stdout


def cmd_add(ns):
    tokens = ns.forward
    reason = add_refusal(tokens)
    if reason:
        _refuse(reason)
    _run(["git", "add"] + tokens)
    staged = _run(["git", "diff", "--cached", "--name-only"]).strip()
    names = staged.splitlines()
    print(f"result: done — staged {len(names)} path(s): {', '.join(names) or '(none new)'}")


def cmd_commit(ns):
    branch = _run(["git", "branch", "--show-current"]).strip()
    reason = commit_refusal(branch, ns.message, ns.forward)
    if reason:
        _refuse(reason)
    args = ["git", "commit"]
    for message in ns.message:
        args += ["-m", message]
    args += ns.forward  # parity: paths and any other commit flags ride along
    out = _run(args).strip()
    if out:
        print(out)
    print(f"result: done — committed on {branch} "
          f"(hand-off still leaves the machine only through `{PEN.replace('git.py', 'pr.py')} push`)")


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="git.py", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    verbs = parser.add_subparsers(dest="verb", required=True)

    add = verbs.add_parser(
        "add", help="stage named paths only — `add .` / `-A` / `-u` are refused "
                    "(extra git-add flags forward for parity)")
    add.set_defaults(func=cmd_add)

    commit = verbs.add_parser(
        "commit", help="commit on the session's claude/* branch with a real "
                       "message; `-a`/`--all` refused; paths and other flags forward")
    commit.add_argument("-m", "--message", action="append", default=[],
                        metavar="MSG",
                        help="the commit message (repeatable, like git); a real "
                             "step-shaped line saying what landed")
    commit.set_defaults(func=cmd_commit)

    ns, extra = parser.parse_known_args(argv)
    ns.forward = extra
    ns.func(ns)


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    main()
