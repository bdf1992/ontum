#!/usr/bin/env python3
"""The PR pen — the one way a session opens or reshapes a PR.

Done-line 0011: the story is validated, not requested. The
branch-ritual skill (SKILL.md beside this file) is the form; this pen
is its enforcement, the way loop/node.py is the one pen for summoned
verdicts. The gh_guard hook (.claude/hooks/gh_guard.py) denies the raw
mutating verbs, so this is the only write path to a PR.

Verbs:
    create  validate the story, run the ritual checks, push, open the PR
    edit    rewrite an existing open PR's story through the same validation
    check   story audit — open PRs wearing the auto-title or an empty body
    push    the branded git push (done-line 0014): alive branch, green
            suite (or declared red), force only with lease — with
            feature parity: anything else git push takes is forwarded

Stdlib only. Every invocation ends with a clear stdout result:
done | report | needs-you. A refusal is a `report`: it tells the
session what the story is missing; nothing here escalates to bdo
except work arriving at the stamp.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
PEN = "python .claude/skills/branch-ritual/pr.py"
FOOTER = "🤖 Generated with [Claude Code](https://claude.com/claude-code)"
END_STATES = ("done", "report", "needs-you")
REF = re.compile(r"\d{4}(-[a-z0-9][a-z0-9-]*)?")


# ------------------------------------------------------------------ story

def _squash(text):
    """Normalize for the auto-title comparison: case, slashes, hyphens."""
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def validate_story(story, branch):
    """Return the list of reasons this story may not be submitted.

    `story` is a dict: title, landed (list of bullets), done_line,
    report, why, end_state, flags (list), red_reason. An empty list
    means the story holds.
    """
    problems = []
    title = (story.get("title") or "").strip()
    if not title:
        problems.append("a title is required — one line saying what this PR did")
    elif _squash(title) == _squash(branch):
        problems.append(
            "the title is the branch name — an unwritten story; "
            "say what the work did, not where it sat"
        )
    if not [b for b in story.get("landed", []) if b.strip()]:
        problems.append("--landed is required (repeatable) — what actually landed")
    why = (story.get("why") or "").strip()
    for field in ("done_line", "report"):
        value = (story.get(field) or "").strip()
        label = field.replace("_", "-")
        if value != "none" and not REF.fullmatch(value):
            problems.append(
                f"--{label} must be a numbered entry (0011 or 0011-slug) or 'none'"
            )
        elif value == "none" and not why:
            problems.append(
                f"--{label} none requires --why — absence is information, name it"
            )
    end_state = (story.get("end_state") or "").strip()
    if end_state not in END_STATES:
        problems.append("--end-state must be one of: " + " | ".join(END_STATES))
    if end_state == "needs-you" and not [f for f in story.get("flags", []) if f.strip()]:
        problems.append("end-state needs-you requires at least one --flag saying what")
    return problems


def _ref_line(directory, value, why):
    if value == "none":
        return f"none — {why.strip()}"
    if re.fullmatch(r"\d{4}", value):
        return f"{value} (under `{directory}/`)"
    return f"`{directory}/{value}.md`"


def compose_body(story):
    """The standard story form. Validation has already passed."""
    lines = ["## What landed", ""]
    lines += [f"- {b.strip()}" for b in story["landed"] if b.strip()]
    lines += ["", "## Done-line", ""]
    lines.append(_ref_line(".ai-native/done", story["done_line"], story["why"]))
    lines += ["", "## Report", ""]
    lines.append(_ref_line(".ai-native/reports", story["report"], story["why"]))
    red = (story.get("red_reason") or "").strip()
    if red:
        lines += ["", "## Red hand-off (declared)", "", red]
    lines += ["", f"## End-state: `{story['end_state']}`", ""]
    flags = [f.strip() for f in story.get("flags", []) if f.strip()]
    if flags:
        lines.append("Flagged for bdo:")
        lines += [f"- {f}" for f in flags]
    else:
        lines.append("Nothing flagged for bdo.")
    lines += ["", FOOTER, ""]
    return "\n".join(lines)


# ---------------------------------------------------------------- runtime

def _refuse(message):
    print(f"result: report — refused: {message}")
    sys.exit(1)


def _run(args):
    proc = subprocess.run(
        args, capture_output=True, text=True, encoding="utf-8",
        errors="replace", cwd=ROOT,
    )
    if proc.returncode != 0:
        _refuse(
            f"`{' '.join(args)}` failed:\n"
            f"{(proc.stderr or proc.stdout).strip()}"
        )
    return proc.stdout


def _story_from(ns):
    return {
        "title": ns.title,
        "landed": ns.landed,
        "done_line": ns.done_line,
        "report": ns.report,
        "why": ns.why,
        "end_state": ns.end_state,
        "flags": ns.flags,
        "red_reason": getattr(ns, "red_ok", "") or "",
    }


def _check_tests(story):
    proc = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-q"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=ROOT,
    )
    if proc.returncode == 0:
        if story["red_reason"]:
            print("note: tests are green — dropping --red-ok from the story")
            story["red_reason"] = ""
        return
    if not story["red_reason"]:
        tail = "\n".join((proc.stderr or proc.stdout).strip().splitlines()[-6:])
        _refuse(
            "the suite is red — fix or shrink scope (§9.5); handing off red "
            f"means declaring it: rerun with --red-ok \"<why>\"\n{tail}"
        )


def cmd_create(ns):
    branch = _run(["git", "branch", "--show-current"]).strip()
    if not branch or branch in ("main", "master"):
        _refuse(
            f"on '{branch or 'detached HEAD'}' — sessions PR from their "
            "claude/* branch, never the trunk"
        )
    story = _story_from(ns)
    problems = validate_story(story, branch)
    if problems:
        _refuse("the story does not hold:\n  - " + "\n  - ".join(problems))
    merged = json.loads(_run(
        ["gh", "pr", "list", "--head", branch, "--state", "merged",
         "--json", "number"]))
    if merged:
        nums = ", ".join(f"#{p['number']}" for p in merged)
        if not ns.recover:
            _refuse(
                f"branch '{branch}' is dead — PR {nums} already merged from "
                "it; cut a fresh branch from where you stand and run the pen "
                "there (the PR #6 → #8 stranding). If commits are already "
                "stranded here and this PR is the rescue, rerun with --recover"
            )
        print(f"note: recovering stranded work from a dead branch (PR {nums} "
              "already merged — the PR #4 pattern)")
    already = json.loads(_run(
        ["gh", "pr", "list", "--head", branch, "--state", "open",
         "--json", "number"]))
    if already:
        nums = ", ".join(f"#{p['number']}" for p in already)
        _refuse(
            f"exactly one PR per branch: {nums} is already open from "
            f"'{branch}' — reshape its story with: {PEN} edit "
            f"{already[0]['number']} ..."
        )
    _check_tests(story)
    dirty = _run(["git", "status", "--porcelain"]).strip()
    if dirty:
        print("note: the working tree is not clean — anything uncommitted stays behind:")
        print("  " + "\n  ".join(dirty.splitlines()))
    _run(["git", "push", "-u", "origin", branch])
    url = _run(["gh", "pr", "create", "--base", ns.base, "--head", branch,
                "--title", story["title"], "--body", compose_body(story)]).strip()
    print(f"result: done — PR at the stamp: {url}")
    print("do not merge it; tell bdo.")


def push_refusal(branch, merged_numbers):
    """The pure reasons a push may not happen. None means it may."""
    if not branch:
        return "detached HEAD — a session pushes its claude/* branch"
    if branch in ("main", "master"):
        return "never push the trunk — the stamp is bdo's (firm)"
    if merged_numbers:
        nums = ", ".join(f"#{n}" for n in merged_numbers)
        return (
            f"branch '{branch}' is dead — PR {nums} already merged from it; "
            "new work means a new branch (commits already stranded here go "
            "through create --recover)"
        )
    return None


def forward_refusal(tokens):
    """Feature parity, minus the two forbidden things: anything git push
    takes is forwarded, except plain force and the trunk by name."""
    for token in tokens:
        bare = token.strip("'\"")
        if bare in ("-f", "--force"):
            return "plain --force does not exist here; use --force-with-lease"
        if bare in ("main", "master") or re.fullmatch(r"[^:]*:(main|master)", bare):
            return "the trunk is not a push target — the stamp is bdo's (firm)"
    return None


def cmd_push(ns):
    forward = [t for t in getattr(ns, "forward", []) if t != "--"]
    reason = forward_refusal(forward)
    if reason:
        _refuse(reason)
    branch = _run(["git", "branch", "--show-current"]).strip()
    merged = []
    if branch and branch not in ("main", "master"):
        merged = [p["number"] for p in json.loads(_run(
            ["gh", "pr", "list", "--head", branch, "--state", "merged",
             "--json", "number"]))]
    reason = push_refusal(branch, merged)
    if reason:
        _refuse(reason)
    story = {"red_reason": ns.red_ok or ""}
    _check_tests(story)
    args = ["git", "push"]
    if ns.force_with_lease:
        args.append("--force-with-lease")
    # parity: forwarded args replace the defaults, they don't fight them
    args += forward if forward else ["-u", "origin", branch]
    _run(args)
    declared = (
        f"; pushed red, declared: {story['red_reason']} — carry this into "
        "the PR story at hand-off"
        if story["red_reason"] else ""
    )
    pushed = " ".join(forward) if forward else branch
    print(f"result: done — pushed {pushed}{declared}")


def cmd_edit(ns):
    info = json.loads(_run(
        ["gh", "pr", "view", str(ns.number), "--json", "state,headRefName"]))
    if info["state"] != "OPEN":
        _refuse(
            f"PR #{ns.number} is {info['state'].lower()} — only an open PR "
            "gets its story reshaped"
        )
    story = _story_from(ns)
    problems = validate_story(story, info["headRefName"])
    if problems:
        _refuse("the story does not hold:\n  - " + "\n  - ".join(problems))
    _run(["gh", "pr", "edit", str(ns.number),
          "--title", story["title"], "--body", compose_body(story)])
    print(f"result: done — story rewritten on PR #{ns.number}; the stamp is bdo's")


def cmd_check(_ns):
    prs = json.loads(_run(
        ["gh", "pr", "list", "--state", "open",
         "--json", "number,title,headRefName,body"]))
    unwritten = []
    for pr in prs:
        reasons = []
        if not (pr["body"] or "").strip():
            reasons.append("empty body")
        if _squash(pr["title"]) == _squash(pr["headRefName"]):
            reasons.append("auto-title")
        if reasons:
            unwritten.append((pr, reasons))
    if not unwritten:
        print(f"result: done — {len(prs)} open PR(s), every story written")
        return
    for pr, reasons in unwritten:
        print(f"PR #{pr['number']} '{pr['title']}': " + ", ".join(reasons))
    print(
        f"result: report — {len(unwritten)} unwritten story(ies); "
        f"repair each with: {PEN} edit <number> ..."
    )


def _story_args(parser):
    parser.add_argument("--title", required=True,
                        help="one line: what this PR did (never the branch name)")
    parser.add_argument("--landed", action="append", default=[],
                        metavar="BULLET", help="what landed; repeatable")
    parser.add_argument("--done-line", dest="done_line", required=True,
                        help="the .ai-native/done entry served (0011 or "
                             "0011-slug), or 'none' with --why")
    parser.add_argument("--report", required=True,
                        help="the .ai-native/reports entry (0013 or "
                             "0013-slug), or 'none' with --why")
    parser.add_argument("--why", default="",
                        help="required when done-line or report is 'none'")
    parser.add_argument("--end-state", dest="end_state", required=True,
                        choices=END_STATES)
    parser.add_argument("--flag", action="append", default=[], dest="flags",
                        metavar="FOR_BDO",
                        help="anything raised for bdo; repeatable; required "
                             "when end-state is needs-you")


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="pr.py", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    verbs = parser.add_subparsers(dest="verb", required=True)

    create = verbs.add_parser("create", help="open the session's one PR to main")
    _story_args(create)
    create.add_argument("--base", default="main")
    create.add_argument("--red-ok", dest="red_ok", default="",
                        metavar="WHY",
                        help="hand off a red suite anyway, declaring why in "
                             "the story (§9.5)")
    create.add_argument("--recover", action="store_true",
                        help="this PR rescues commits stranded on a merged "
                             "branch (the PR #4 pattern)")
    create.set_defaults(func=cmd_create)

    edit = verbs.add_parser("edit", help="rewrite an open PR's story")
    edit.add_argument("number", type=int)
    _story_args(edit)
    edit.set_defaults(func=cmd_edit)

    check = verbs.add_parser("check", help="audit open PRs for unwritten stories")
    check.set_defaults(func=cmd_check)

    push = verbs.add_parser(
        "push", help="the branded git push (feature parity: extra args "
                     "are forwarded to git push after the checks)")
    push.add_argument("--red-ok", dest="red_ok", default="", metavar="WHY",
                      help="push with a red suite anyway, declaring why "
                           "(§9.5); the declaration is owed to the PR story")
    push.add_argument("--force-with-lease", dest="force_with_lease",
                      action="store_true",
                      help="after rebasing your own branch; plain --force "
                           "does not exist here")
    push.set_defaults(func=cmd_push)

    ns, extra = parser.parse_known_args(argv)
    if extra and getattr(ns, "verb", None) != "push":
        parser.error("unrecognized arguments: " + " ".join(extra))
    ns.forward = extra
    ns.func(ns)


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    main()
