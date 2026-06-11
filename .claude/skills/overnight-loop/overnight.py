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
import re
import subprocess
import sys
from typing import Iterable, NamedTuple

TRUNK = {"main", "master"}
SESSION_PREFIXES = ("codex/", "claude/")
DEFAULT_TESTS = ("python -m unittest discover -s tests -v",)
DEFAULT_PICKUP_TESTS = (
    "python -m unittest tests.test_overnight_loop -v",
    *DEFAULT_TESTS,
)


class Record(NamedTuple):
    name: str
    title: str
    text: str


class Worktree(NamedTuple):
    path: str
    branch: str


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


def recent_records(root: pathlib.Path, folder: str, limit: int = 8) -> list[Record]:
    record_dir = root / ".ai-native" / folder
    paths = sorted(record_dir.glob("*.md"), key=_record_sort_key, reverse=True)
    records: list[Record] = []
    for path in paths[:limit]:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            text = ""
        title = next((line.strip("# ").strip() for line in text.splitlines() if line.startswith("# ")), path.stem)
        records.append(Record(name=path.name, title=title, text=text))
    return records


def _record_sort_key(path: pathlib.Path) -> tuple[int, str]:
    match = re.match(r"(\d+)-", path.name)
    number = int(match.group(1)) if match else -1
    return number, path.name


def load_worktrees(root: pathlib.Path) -> list[Worktree]:
    text = _run_git(root, ["worktree", "list", "--porcelain"])
    worktrees: list[Worktree] = []
    current: dict[str, str] = {}
    for line in [*text.splitlines(), ""]:
        if not line.strip():
            if current:
                worktrees.append(
                    Worktree(
                        path=current.get("path", "(unknown)"),
                        branch=current.get("branch", "(detached)"),
                    )
                )
                current = {}
            continue
        if line.startswith("worktree "):
            current["path"] = line.split(" ", 1)[1].strip()
        elif line.startswith("branch "):
            ref = line.split(" ", 1)[1].strip()
            current["branch"] = ref.removeprefix("refs/heads/")
        elif line == "detached":
            current["branch"] = "(detached)"
    return worktrees


def open_summons(root: pathlib.Path) -> str:
    if not (root / "loop").is_dir():
        return "result: done - no open summons; loop.summon unavailable in fixture"
    proc = subprocess.run(
        [sys.executable, "-m", "loop.summon"],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    text = (proc.stdout or proc.stderr).strip()
    if proc.returncode != 0:
        raise RepoError(f"`python -m loop.summon` failed: {text}")
    return text


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


def pickup_refusal(
    *,
    branch: str,
    dirty_lines: list[str],
    requested_arc: str | None,
    epics: dict[str, dict],
    allow_dirty: bool = False,
) -> str | None:
    if not branch:
        return "detached HEAD; overnight-loop pickup needs a named session branch"
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
            "existing work this pickup is inheriting"
        )
    if requested_arc and requested_arc not in epics:
        known = ", ".join(sorted(epics)) or "(none)"
        return f"unknown arc `{requested_arc}`; known arcs: {known}"
    if not epics:
        return "no known arcs under `.ai-native/epics`; pickup has nothing safe to choose"
    return None


def summons_open(summons_text: str) -> bool:
    lower = summons_text.lower()
    return not ("no open summons" in lower or "nothing awaits" in lower)


def choose_arc(
    *,
    epics: dict[str, dict],
    requested_arc: str | None,
    summons_text: str,
    records: Iterable[Record],
    worktrees: Iterable[Worktree],
) -> tuple[str, str]:
    if requested_arc:
        return requested_arc, "requested with --arc and present in `.ai-native/epics`"

    lower_summons = summons_text.lower()
    corpus = "\n".join(
        [
            lower_summons,
            "\n".join(record.text.lower() for record in records),
            "\n".join(worktree.branch.lower() for worktree in worktrees),
        ]
    )
    open_signal = summons_open(summons_text)
    scores: dict[str, int] = {}
    for epic_id in sorted(epics):
        lower_id = epic_id.lower()
        short = lower_id.removeprefix("epic.")
        score = 0
        if open_signal and lower_id in lower_summons:
            score += 1000
        score += corpus.count(lower_id) * 20
        score += corpus.count(short) * 3
        if epic_id == "epic.substrate":
            score += 1
        scores[epic_id] = score

    chosen = sorted(epics, key=lambda epic_id: (-scores[epic_id], epic_id))[0]
    if open_signal and chosen.lower() in lower_summons:
        reason = "open summons mention this known arc"
    elif scores[chosen] > (1 if chosen == "epic.substrate" else 0):
        reason = "recent records or sibling worktrees mention this arc"
    elif chosen == "epic.substrate":
        reason = "no open summons override the harness arc"
    else:
        reason = "first known arc by deterministic ordering"
    return chosen, reason


def story_for_arc(arc: str) -> str:
    if arc == "epic.substrate":
        return "overnight-loop arc pickup"
    return f"{arc.removeprefix('epic.')} arc pickup"


def objective_for_arc(arc: str) -> str:
    if arc == "epic.substrate":
        return "extend the confident overnight loop from preflight into arc pickup"
    return f"pick one bounded increment inside {arc}"


def task_for_arc(arc: str) -> str:
    if arc == "epic.substrate":
        return (
            "Advance the overnight-loop harness by one executable, read-only "
            "selection step before any mutating work starts."
        )
    return (
        f"Read {arc}, pick one bounded increment, and stop before any owner-only "
        "stamp, language pin, or missing context."
    )


def record_names(records: Iterable[Record]) -> str:
    names = [record.name for record in records]
    return ", ".join(names) if names else "(none)"


def sibling_branches(worktrees: Iterable[Worktree], branch: str) -> str:
    siblings = sorted({worktree.branch for worktree in worktrees if worktree.branch and worktree.branch != branch})
    return ", ".join(siblings[:10]) if siblings else "(none)"


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


def build_pickup(
    *,
    root: pathlib.Path,
    branch: str,
    epics: dict[str, dict],
    arc: str,
    reason: str,
    summons_text: str,
    done_records: list[Record],
    report_records: list[Record],
    worktrees: list[Worktree],
    objective: str,
    tests: tuple[str, ...],
    allow_dirty: bool,
    dirty_count: int,
) -> str:
    story = story_for_arc(arc)
    task = task_for_arc(arc)
    summons_state = "open" if summons_open(summons_text) else "none"
    slug = story.replace(" ", "-")
    title = story.title()
    known = ", ".join(sorted(epics))
    lines = [
        "overnight-loop pickup",
        f"repo: {root}",
        f"branch: {branch}",
        f"dirty start: {'allowed' if allow_dirty else 'no'} ({dirty_count} path(s))",
        f"known arcs read: {known}",
        f"open summons read: {summons_state}",
        f"recent done read: {record_names(done_records)}",
        f"recent reports read: {record_names(report_records)}",
        f"sibling worktrees read: {sibling_branches(worktrees, branch)}",
        "",
        f"recommended arc: {arc}",
        f"next story: {story}",
        f"next task: {task}",
        f"selection basis: {reason}",
        "",
        "arc shape:",
        f"- {arc_summary(epics[arc])}",
        "",
        "first commands:",
        f"- python .claude/skills/overnight-loop/overnight.py brief --arc {arc} --objective \"{objective}\"",
        f"- python -m loop.pen new done --slug {slug} --title \"{title}\"",
        "- read the `CLAUDE.md` for each directory touched before editing",
        "",
        "authority boundaries:",
        "- do not confirm arcs, stamp owner gates, edit append-only logs, or choose owner-only language pins.",
        "- do not push or merge main; hand off through the branch ritual and leave bdo as last stop.",
        "",
        "stop conditions:",
        "- The done-line is satisfied.",
        "- The next action needs bdo's stamp, an owner-only pin, or missing context.",
        "- The branch is not a live session branch or the tree becomes unexpectedly dirty.",
        "- A sibling worktree is already landing the same files or story.",
        "- No safe next increment remains inside the recommended arc.",
        "",
        "tests:",
    ]
    lines.extend(f"- {test}" for test in tests)
    lines.append("")
    lines.append(f"result: report - overnight-loop pickup recommends {arc} / {story}")
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


def cmd_pickup(ns: argparse.Namespace) -> int:
    try:
        root = pathlib.Path(ns.repo_root).resolve() if ns.repo_root else repo_root()
        branch = current_branch(root)
        dirty = status_short(root)
        epics = load_epics(root)
        worktrees = load_worktrees(root)
    except RepoError as exc:
        print(f"result: needs-you - {exc}")
        return 2

    reason = pickup_refusal(
        branch=branch,
        dirty_lines=dirty,
        requested_arc=ns.arc,
        epics=epics,
        allow_dirty=ns.allow_dirty,
    )
    if reason:
        print(f"result: report - refused: {reason}")
        return 1

    try:
        summons_text = open_summons(root)
    except RepoError as exc:
        print(f"result: needs-you - {exc}")
        return 2

    done_records = recent_records(root, "done")
    report_records = recent_records(root, "reports")
    records = [*done_records, *report_records]
    arc, basis = choose_arc(
        epics=epics,
        requested_arc=ns.arc,
        summons_text=summons_text,
        records=records,
        worktrees=worktrees,
    )
    objective = ns.objective or objective_for_arc(arc)
    tests = tuple(ns.test or DEFAULT_PICKUP_TESTS)
    print(
        build_pickup(
            root=root,
            branch=branch,
            epics=epics,
            arc=arc,
            reason=basis,
            summons_text=summons_text,
            done_records=done_records,
            report_records=report_records,
            worktrees=worktrees,
            objective=objective,
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

    pickup = sub.add_parser(
        "pickup",
        help="recommend one safe next arc/story/task from live repo state",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    pickup.add_argument("--arc", help="prefer this known arc; unknown arcs are refused")
    pickup.add_argument("--objective", help="override the emitted first-command objective")
    pickup.add_argument("--allow-dirty", action="store_true", help="acknowledge inherited dirty work")
    pickup.add_argument("--repo-root", help=argparse.SUPPRESS)
    pickup.add_argument(
        "--test",
        action="append",
        help="handoff test command; repeat for multiple commands (defaults to focused overnight tests plus full suite)",
    )
    pickup.set_defaults(func=cmd_pickup)

    ns = parser.parse_args(argv)
    return ns.func(ns)


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
