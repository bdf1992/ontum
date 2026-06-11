#!/usr/bin/env python3
"""The overnight-loop brief pen.

This command is intentionally read-only. It turns "keep working until
you stop" into a bounded run contract against the live repo state before
the session starts mutating files.

Every invocation ends with a clear stdout result:
done | report | needs-you. A refusal is a `report`: it names what the
start is missing and leaves the working tree untouched.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import subprocess
import sys
from typing import Iterable

TRUNK = {"main", "master"}
SESSION_PREFIXES = ("codex/", "claude/")
DEFAULT_TESTS = ("python -m unittest discover -s tests -v",)


class RepoError(RuntimeError):
    """A repo fact could not be read."""


def _run_git(root: pathlib.Path, args: Iterable[str]) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip()
        raise RepoError(f"`git {' '.join(args)}` failed: {detail}")
    return proc.stdout


def repo_root(start: pathlib.Path | None = None) -> pathlib.Path:
    explicit = os.environ.get("ONTUM_REPO_ROOT")
    if explicit:
        return pathlib.Path(explicit).resolve()
    here = (start or pathlib.Path.cwd()).resolve()
    proc = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=here,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip()
        raise RepoError(f"not inside a git repo: {detail}")
    return pathlib.Path(proc.stdout.strip()).resolve()


def current_branch(root: pathlib.Path) -> str:
    return _run_git(root, ["branch", "--show-current"]).strip()


def status_short(root: pathlib.Path) -> list[str]:
    text = _run_git(root, ["status", "--short"])
    return [line for line in text.splitlines() if line.strip()]


def load_epics(root: pathlib.Path) -> dict[str, dict]:
    epics: dict[str, dict] = {}
    epic_dir = root / ".ai-native" / "epics"
    for path in sorted(epic_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        epic = data.get("epic")
        if isinstance(epic, dict) and isinstance(epic.get("id"), str):
            epics[epic["id"]] = epic
    return epics


def arc_summary(epic: dict, limit: int = 220) -> str:
    text = " ".join(str(epic.get("arc", "")).split())
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def brief_refusal(
    *,
    branch: str,
    dirty_lines: list[str],
    arc: str,
    epics: dict[str, dict],
    allow_dirty: bool = False,
) -> str | None:
    if not branch:
        return "detached HEAD; an overnight loop needs a named session branch"
    if branch in TRUNK:
        return (
            f"branch `{branch}` is the owner viewport; create a codex/* or "
            "claude/* worktree branch first"
        )
    if not any(branch.startswith(prefix) for prefix in SESSION_PREFIXES):
        prefixes = ", ".join(f"`{p}*`" for p in SESSION_PREFIXES)
        return f"branch `{branch}` is not a session branch ({prefixes})"
    if dirty_lines and not allow_dirty:
        return (
            "dirty tree; start clean or pass --allow-dirty after naming the "
            "existing work this run is inheriting"
        )
    if arc not in epics:
        known = ", ".join(sorted(epics)) or "(none)"
        return f"unknown arc `{arc}`; known arcs: {known}"
    return None


def build_brief(
    *,
    root: pathlib.Path,
    branch: str,
    arc: str,
    epic: dict,
    objective: str,
    tests: tuple[str, ...],
    allow_dirty: bool,
    dirty_count: int,
) -> str:
    lines = [
        "overnight-loop brief",
        f"repo: {root}",
        f"branch: {branch}",
        f"arc: {arc}",
        f"arc owner: {epic.get('owner', 'unknown')}",
        f"objective: {objective}",
        f"dirty start: {'allowed' if allow_dirty else 'no'} ({dirty_count} path(s))",
        "",
        "arc shape:",
        f"- {arc_summary(epic)}",
        "",
        "authority:",
        "- may: choose and finish bounded increments that serve the named objective.",
        "- must: mint a done-line through the records pen before code changes.",
        "- must: keep work on this session branch and path-scope every commit.",
        "- must not: stamp owner gates, push or merge main, hand-edit append-only logs, or hand-edit generated outputs.",
        "",
        "loop:",
        "1. Read the applicable repo and module contracts.",
        "2. Check ambient summons, inbox, and sibling work that can collide with the arc.",
        "3. Pick the smallest next increment that advances the objective.",
        "4. Implement it, run focused tests, then run the named handoff tests.",
        "5. Repeat only while the next increment remains inside this contract.",
        "",
        "stop conditions:",
        "- The done-line is satisfied.",
        "- The next step needs bdo's stamp, an owner-only pin, or missing context.",
        "- The same test failure survives two concrete fix attempts.",
        "- The branch or working tree stops matching this brief.",
        "- No safe next increment remains inside the named arc.",
        "",
        "handoff:",
        "- Mint a report through `python -m loop.pen new reports ...`.",
        "- Name every `needs-you` item instead of smoothing it over.",
        "- Leave merge and final sign-off to bdo.",
        "",
        "tests:",
    ]
    lines.extend(f"- {test}" for test in tests)
    lines.append("")
    lines.append(f"result: report - overnight-loop brief ready for {arc} on {branch}")
    return "\n".join(lines)


def cmd_brief(ns: argparse.Namespace) -> int:
    try:
        root = pathlib.Path(ns.repo_root).resolve() if ns.repo_root else repo_root()
        branch = current_branch(root)
        dirty = status_short(root)
        epics = load_epics(root)
    except RepoError as exc:
        print(f"result: needs-you - {exc}")
        return 2

    reason = brief_refusal(
        branch=branch,
        dirty_lines=dirty,
        arc=ns.arc,
        epics=epics,
        allow_dirty=ns.allow_dirty,
    )
    if reason:
        print(f"result: report - refused: {reason}")
        return 1

    tests = tuple(ns.test or DEFAULT_TESTS)
    print(
        build_brief(
            root=root,
            branch=branch,
            arc=ns.arc,
            epic=epics[ns.arc],
            objective=ns.objective,
            tests=tests,
            allow_dirty=ns.allow_dirty,
            dirty_count=len(dirty),
        )
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="overnight.py",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="verb", required=True)

    brief = sub.add_parser(
        "brief",
        help="emit the bounded run contract for a named arc",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    brief.add_argument("--arc", required=True, help="arc/epic id, e.g. epic.substrate")
    brief.add_argument("--objective", required=True, help="the concrete overnight objective")
    brief.add_argument("--allow-dirty", action="store_true", help="acknowledge inherited dirty work")
    brief.add_argument("--repo-root", help=argparse.SUPPRESS)
    brief.add_argument(
        "--test",
        action="append",
        help="handoff test command; repeat for multiple commands (defaults to the full suite)",
    )
    brief.set_defaults(func=cmd_brief)

    ns = parser.parse_args(argv)
    return ns.func(ns)


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
