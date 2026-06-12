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


# a body that is only a path or a bare numbered ref is homework, not writing
_POINTER = re.compile(
    r"^[`'\"\s]*(\.?(ai-native|\.\.)/\S+|[\w./\-]+\.md|\d{4}(-[a-z0-9-]+)?)[`'\"\s]*$",
    re.I)


def _is_pointer(text):
    return bool(_POINTER.match(text.strip()))


def validate_story(story, branch):
    """The pen's deterministic floor, nothing more. A pen carries the author's
    written narrative whole; it does not break it into fields and does not judge
    whether it reads as a story — that flow is the author's to write and the
    Reader's to grade (story-gate.claude.v1), in the loop, before this reaches
    the owner. The pen refuses only what is plainly not writing: an empty title
    or body, a title that is just the branch name, or a body that is only a
    path/ref.
    """
    problems = []
    title = (story.get("title") or "").strip()
    if not title:
        problems.append("a title is required — one line saying what this PR did")
    elif _squash(title) == _squash(branch):
        problems.append(
            "the title is the branch name — an unwritten story; "
            "say what the work did, not where it sat")
    text = (story.get("story") or "").strip()
    if not text:
        problems.append("--story is required — the written narrative this PR carries")
    elif _is_pointer(text):
        problems.append(
            "--story is a pointer, not writing — a path/ref is homework; write "
            "the narrative for a cold reader")
    return problems


ROLLING_BANNER = (
    "> 🟡 **Still being worked — please don't merge yet.** This is a draft the\n"
    "> session is still adding to; when it's final it flips out of draft.\n"
    "> Open and not a draft means it's ready for you."
)


def compose_body(story, rolling=False):
    """A pen carries the author's written narrative, whole — it imposes no
    shape. The flow is the author's; the verdict is the Reader's. The body is
    the story it was handed and nothing else."""
    lines = [ROLLING_BANNER, ""] if rolling else []
    lines += [story["story"].strip(), ""]
    red = (story.get("red_reason") or "").strip()
    if red:
        lines += [f"*Handed off with a declared-red suite: {red}*", ""]
    lines += [FOOTER, ""]
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
        "story": ns.story,
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
    create_args = ["gh", "pr", "create", "--base", ns.base, "--head", branch,
                   "--title", story["title"],
                   "--body", compose_body(story, rolling=ns.rolling)]
    if ns.rolling:
        create_args.append("--draft")
    url = _run(create_args).strip()
    if ns.rolling:
        print(f"result: done — rolling draft opened (NOT at the stamp): {url}")
        print(f"keep appending; flip when final with: {PEN} ready <number> ...")
    else:
        print(f"result: done — PR at the stamp: {url}")
        print("do not merge it; tell bdo. (open + not a draft = please merge)")


def push_refusal(branch, merged_numbers, open_numbers=()):
    """The pure reasons a push may not happen. None means it may.

    A branch with a merged PR is dead — unless an open PR also exists from
    it: that open PR is a recovery (create --recover opens exactly this),
    and the rescue must be updatable or a conflicted recovery PR can never
    be rebased (the PR #20 incident)."""
    if not branch:
        return "detached HEAD — a session pushes its claude/* branch"
    if branch in ("main", "master"):
        return "never push the trunk — the stamp is bdo's (firm)"
    if merged_numbers and not open_numbers:
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
    open_prs = []
    if branch and branch not in ("main", "master"):
        merged = [p["number"] for p in json.loads(_run(
            ["gh", "pr", "list", "--head", branch, "--state", "merged",
             "--json", "number"]))]
        open_prs = [p["number"] for p in json.loads(_run(
            ["gh", "pr", "list", "--head", branch, "--state", "open",
             "--json", "number"]))]
    reason = push_refusal(branch, merged, open_prs)
    if reason:
        _refuse(reason)
    if merged and open_prs:
        nums = ", ".join(f"#{n}" for n in open_prs)
        print(f"note: dead branch carrying open recovery PR {nums} — "
              "this push updates the rescue")
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


def cmd_ready(ns):
    """The merge signal (done-line 0017): re-validate the story, require a
    green (or declared red) suite, flip the draft. The flip is the one
    unambiguous 'bdo, it's yours now' — accidental merges die here."""
    info = json.loads(_run(
        ["gh", "pr", "view", str(ns.number),
         "--json", "state,headRefName,isDraft"]))
    if info["state"] != "OPEN":
        _refuse(
            f"PR #{ns.number} is {info['state'].lower()} — only an open PR "
            "can come to the stamp"
        )
    if not info["isDraft"]:
        _refuse(
            f"PR #{ns.number} is already at the stamp (open, not a draft) — "
            "nothing to flip"
        )
    story = _story_from(ns)
    problems = validate_story(story, info["headRefName"])
    if problems:
        _refuse("the story does not hold:\n  - " + "\n  - ".join(problems))
    _check_tests(story)
    _run(["gh", "pr", "edit", str(ns.number),
          "--title", story["title"], "--body", compose_body(story)])
    _run(["gh", "pr", "ready", str(ns.number)])
    print(f"result: done — PR #{ns.number} is AT THE STAMP. Open and not a "
          "draft means please merge (done-line 0017); bdo, it's yours.")


def cmd_unready(ns):
    """Back to a rolling draft — the de-escalation needs no story; it only
    takes the merge button away."""
    info = json.loads(_run(
        ["gh", "pr", "view", str(ns.number), "--json", "state,isDraft"]))
    if info["state"] != "OPEN":
        _refuse(f"PR #{ns.number} is {info['state'].lower()} — nothing to roll back")
    if info["isDraft"]:
        _refuse(f"PR #{ns.number} is already a rolling draft")
    _run(["gh", "pr", "ready", str(ns.number), "--undo"])
    print(f"result: done — PR #{ns.number} is a rolling draft again (NOT at "
          f"the stamp); flip back when final with: {PEN} ready {ns.number} ...")


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


def integrate_refusal(base):
    """Why a session may not integrate a PR, or None. The trunk is bdo's alone
    (firm); a session integrates a piece into an epic/integration branch — the
    human second set of eyes is bdo's one merge into main, where the finished
    arc lands (bdo's directive, 2026-06-10: he merges main only at arc/epic
    completion; the loop integrates pieces below)."""
    if base in ("main", "master"):
        return ("the trunk is bdo's — the stamp is bdo's (firm). A session "
                "integrates a piece into an epic branch, never main; the "
                "finished arc PRs to main and waits for him")
    return None


def cmd_integrate(ns):
    """Merge a piece-PR into its epic branch (done-line 0029). Main stays
    bdo's; this lands a piece on a non-trunk integration branch so the owner
    only merges a finished arc into main."""
    info = json.loads(_run(
        ["gh", "pr", "view", str(ns.number),
         "--json", "state,baseRefName,headRefName,mergeable"]))
    if info["state"] != "OPEN":
        _refuse(f"PR #{ns.number} is {info['state'].lower()} — only an open PR integrates")
    reason = integrate_refusal(info["baseRefName"])
    if reason:
        _refuse(reason)
    if info.get("mergeable") == "CONFLICTING":
        _refuse(f"PR #{ns.number} conflicts with {info['baseRefName']} — rebase the "
                "piece onto its epic branch first, then integrate")
    args = ["gh", "pr", "merge", str(ns.number), "--squash"]
    if ns.delete_branch:
        args.append("--delete-branch")
    _run(args)
    print(f"result: done — integrated PR #{ns.number} "
          f"({info['headRefName']} -> {info['baseRefName']}); main stays bdo's "
          "(the finished arc is the PR he merges)")


# ----------------------------------------------------------- land (merge-node)
# bdo's amendment, 2026-06-11: he no longer merges PRs — that became
# performative. An independent merge-node lands a *confirmed-arc* PR on main.
# D-4 holds at arc scale (done-line 0028): bdo's confirm-arc is the
# authorization this verb executes; the node propels, it never authorizes, and
# bdo's confirmation — an independent human stamp — is what satisfies "no one
# signs their own line" even when the Claude family authored the PR.

def _now():
    import time
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + "Z"


def _capture(args):
    """Run without _run's exit-on-failure: the merge-node asks questions where
    'no' is an answer (does this confirmation exist?), not a crash."""
    proc = subprocess.run(args, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", cwd=ROOT)
    return proc.returncode, proc.stdout, proc.stderr


def arc_confirmed_in(admissions_text, epic):
    """The active arc_confirmed admission id for an epic in a log dump, or
    None. Pure. Latest enabled confirmation by bdo wins; `enabled:false`
    withdraws (superseded, never erased)."""
    active = None
    for line in admissions_text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            adm = json.loads(line)
        except ValueError:
            continue
        if (adm.get("type") == "arc_confirmed" and adm.get("epic") == epic
                and (adm.get("by") or "").strip().lower() == "bdo"):
            active = adm["id"] if adm.get("enabled", True) else None
    return active


def node_admitted_in(admissions_text, node_id):
    """Is this node id admitted-real in a log dump? Pure. A node_real
    admission admits its `real_node` and supersedes its `stage_node` — so
    an id later named as someone's stage side stops being admitted (the
    one lifecycle every seat shares, done-line 0049). An id no admission
    ever named is self-asserted: effectively mock, and not admitted."""
    admitted = set()
    for line in admissions_text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            adm = json.loads(line)
        except ValueError:
            continue
        if adm.get("type") == "node_real":
            admitted.discard(adm.get("stage_node"))
            if adm.get("real_node"):
                admitted.add(adm["real_node"])
    return node_id in admitted


def _trunk_admissions():
    """The trunk's admissions log — the pushed `origin/main`, never a local
    `main` ref that drifts stale when a viewport falls behind, never the
    working branch (a piece branch may predate the stamp). Fetch first so
    the read is current. None when the trunk cannot be read."""
    _capture(["git", "fetch", "origin", "main"])
    rc, out, _ = _capture(["git", "show", "origin/main:.ai-native/log/admissions.jsonl"])
    return out if rc == 0 else None


def _trunk_confirmation(epic):
    """Read bdo's arc confirmation from the trunk; `confirm` below pushes
    the stamp here."""
    out = _trunk_admissions()
    return arc_confirmed_in(out, epic) if out is not None else None


# ---------------------------------------------------- the atom invariant
# Retro 0037: the substrate has always required every particle of work to be
# an atom on the log — ambient control senses field-state as a fold over the
# log (§15/D-5), so a work-particle that is not an atom emits nothing to fold
# and the controller is blind to it. These pure refusals make that invariant
# executable at the seam where it was breached:
#     no atom id + no backing receipt  = no PR   (atom_backed_refusal)
#     no real (non-mock) gate receipt  = no land (real_gate_refusal)
# They are pure (text in, reason-or-None out) like arc_confirmed_in, and not
# yet wired into the live verbs — activation is bdo's stamp, the invariant is
# not. A receipt is mock evidence when its node carries the ".mock" marker the
# PIPELINE stamps on every skeleton stage (reconcile.PIPELINE); the first such
# mock replaced is what makes a stage real (node_real admission).

def _receipts_for_atom(receipts_text, atom_id):
    """Every receipt on the log naming this atom (by artifact_id). Pure,
    torn-tail tolerant — a half-written line never happened (D-5)."""
    out = []
    for line in receipts_text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rc = json.loads(line)
        except ValueError:
            continue
        if rc.get("artifact_id") == atom_id:
            out.append(rc)
    return out


def _is_mock_receipt(rc):
    return ".mock" in (rc.get("node") or "")


def atom_backed_refusal(atom_id, receipts_text):
    """Why a PR may not open, or None. A PR must name the atom it serves and
    that atom must already be on the log — work that never became an atom is
    invisible to the loop. No atom id + no backing receipt = no PR."""
    if not (atom_id or "").strip():
        return ("no --atom: a PR names the atom it serves; work that is not an "
                "atom on the log is invisible to the ambient loop (§15/D-5)")
    if not _receipts_for_atom(receipts_text, atom_id):
        return (f"atom '{atom_id}' has no receipt on the log — it never entered "
                "the loop; create it and let a gate judge it before it is a PR")
    return None


def real_gate_refusal(atom_id, receipts_text):
    """Why the merge-node may not land, or None. Landing requires a real
    (non-mock) gate verdict for the atom: a mock returning a constant is a
    story about a gate event, not one. No real gate receipt = no merge."""
    receipts = _receipts_for_atom(receipts_text, atom_id)
    if not receipts:
        return (f"atom '{atom_id}' has no receipt on the log — it never entered "
                "the loop; nothing to land")
    if all(_is_mock_receipt(rc) for rc in receipts):
        return (f"atom '{atom_id}' has only mock receipts — a gate is real only "
                "when a real node judged it; a constant verdict does not land")
    return None


def cmd_confirm(ns):
    """bdo's arc stamp that actually reaches the merge-node. `loop.node
    confirm-arc` only appends to the working tree; the merge-node reads the
    pushed trunk. This is the missing seam: append the same admission and push
    it to `origin/main` in one command, so one stamp authorizes the node — no
    hand-git. The owner's act (D-4): refused unless `--by bdo`. Done on a fresh
    worktree off origin/main, so a stale or dirty viewport never blocks it."""
    import shutil
    import tempfile
    if (ns.by or "").strip().lower() != "bdo":
        _refuse("arc confirmation is bdo's stamp — run with --by bdo (D-4)")
    _run(["git", "fetch", "origin", "main"])
    wt = pathlib.Path(tempfile.mkdtemp(prefix="ontum-confirm-"))
    try:
        _run(["git", "worktree", "add", "--detach", str(wt), "origin/main"])
        sys.path.insert(0, str(ROOT))
        from loop.node import confirm_arc  # the schema, not a second copy
        adm = confirm_arc(wt / ".ai-native", ns.epic, "bdo", enabled=not ns.off)
        rel = ".ai-native/log/admissions.jsonl"
        _run(["git", "-C", str(wt), "add", rel])
        word = "withdraw" if ns.off else "confirm"
        _run(["git", "-C", str(wt), "commit", "-m", f"{word} arc {ns.epic} (bdo)"])
        _run(["git", "-C", str(wt), "push", "origin", "HEAD:main"])
        did = "withdrew" if ns.off else "confirmed"
        print(f"result: done — bdo {did} arc {ns.epic} on the trunk ({adm['id']}). "
              "The merge-node can land its PRs now: "
              "python .claude/skills/branch-ritual/pr.py land <n> "
              f"--epic {ns.epic} --by merge-node.claude.v0")
    finally:
        _capture(["git", "worktree", "remove", str(wt), "--force"])
        if wt.exists():
            shutil.rmtree(wt, ignore_errors=True)


CHECK_OK = {"SUCCESS", "NEUTRAL", "SKIPPED"}


def checks_green(rollup):
    """Every status check is success-like, or there are none. A pending or
    failing check is not green — the merge-node never lands on a yellow light."""
    for c in rollup or []:
        state = (c.get("conclusion") or c.get("state") or "UNKNOWN").upper()
        if state not in CHECK_OK:
            return False
    return True


def land_refusal(info, confirmation, by, by_admitted=False):
    """Why the merge-node may not land this PR on main, or None. Default is
    refuse: it lands only a confirmed-arc, green, written, non-draft,
    non-conflicting PR based on main, and only as an *admitted* node — a
    free-text identity is effectively mock and does not land (done-line
    0049; "the merge-node does not move until bdo admits it real" was
    prose, this makes it executable). by_admitted is the trunk's answer
    (node_admitted_in over origin/main's admissions)."""
    if not (by or "").strip():
        return "the merge-node lands as a named node (--by) — no one signs their own line"
    if not by_admitted:
        return (f"--by {by!r} is not an admitted node on the trunk — a "
                "self-asserted identity is effectively mock and does not "
                "land; bdo's realness gesture admits the seat: python -m "
                f"loop.node admit-real --stage <superseded-id> --node {by} "
                "--by bdo (done-line 0049)")
    if info.get("state") != "OPEN":
        return f"PR is {str(info.get('state')).lower()} — only an open PR lands"
    if info.get("baseRefName") not in ("main", "master"):
        return (f"land targets the trunk; this PR is based on "
                f"{info.get('baseRefName')} — an epic piece uses `integrate`")
    if info.get("isDraft"):
        return "PR is a draft — a draft is 'not ready'; the merge-node never lands one"
    if not confirmation:
        return ("the arc is not confirmed by bdo on the trunk — the merge-node "
                "lands only confirmed arcs (his confirm-arc is the authorization, D-4)")
    if info.get("mergeable") == "CONFLICTING":
        return f"PR conflicts with {info.get('baseRefName')} — rebase it first"
    if not checks_green(info.get("statusCheckRollup")):
        return "the suite is not green (a check is failing or pending) — the merge-node waits"
    title = (info.get("title") or "").strip()
    if not title or _squash(title) == _squash(info.get("headRefName") or ""):
        return "the PR wears an unwritten story (auto-title) — not at landing readiness"
    if not (info.get("body") or "").strip():
        return "the PR has an empty body — an unwritten story does not land"
    return None


def _merge_receipt(pr, epic, by, authorized_by, head):
    """The merge receipt (D-5): the land as an act on the record, citing the
    arc confirmation that authorized it. Built here; pushed to the trunk by
    _push_receipt_to_trunk — never left in a worktree (the bug that left every
    real merge unrecorded: a receipt in a throwaway worktree is no receipt)."""
    return {
        "id": f"rcp.merge.{pr}",
        "kind": "merge",
        "node": by,
        "pr": pr,
        "epic": epic,
        "head": head,
        "verdict": "landed",
        "authorized_by": authorized_by,
        "ts": _now(),
    }


def _append_receipt_line(path, receipt):
    """Append one receipt as a line, torn-tail tolerant (mirrors the loop's
    own append). Pure file I/O — the unit-testable core of the push below."""
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(receipt, sort_keys=True, separators=(",", ":"))
    with open(path, "a+b") as f:
        f.seek(0, 2)
        if f.tell() > 0:
            f.seek(-1, 2)
            if f.read(1) != b"\n":
                f.write(b"\n")
        f.write((line + "\n").encode())
        f.flush()


def _push_receipt_to_trunk(receipt):
    """The receipt belongs on the trunk, where the digest and the next
    merge-node read it — not in this throwaway worktree. Append it to
    origin/main's log and push, on a fresh worktree off origin/main so a
    held or dirty `main` never blocks it (the same seam `confirm` paves for
    bdo's stamp). Returns True on success; the caller turns False into a loud
    needs-you — the merge stands, the record must be reconciled."""
    import shutil
    import tempfile
    if _capture(["git", "fetch", "origin", "main"])[0] != 0:
        return False
    wt = pathlib.Path(tempfile.mkdtemp(prefix="ontum-receipt-"))
    try:
        if _capture(["git", "worktree", "add", "--detach", str(wt), "origin/main"])[0] != 0:
            return False
        _append_receipt_line(wt / ".ai-native" / "log" / "receipts.jsonl", receipt)
        for args in (["git", "-C", str(wt), "add", ".ai-native/log/receipts.jsonl"],
                     ["git", "-C", str(wt), "commit", "-m",
                      f"merge receipt {receipt['id']} (PR #{receipt['pr']} -> main)"],
                     ["git", "-C", str(wt), "push", "origin", "HEAD:main"]):
            if _capture(args)[0] != 0:
                return False
        return True
    finally:
        _capture(["git", "worktree", "remove", str(wt), "--force"])
        if wt.exists():
            shutil.rmtree(wt, ignore_errors=True)


def cmd_land(ns):
    """The merge-node's hand: land a confirmed-arc PR on main. bdo no longer
    merges — he confirms arcs and reads the digest; this lands what he
    confirmed, refuses by default, and records every land. Run it as a node
    that did not author the PR (the merge-node SKILL is explicit)."""
    info = json.loads(_run(
        ["gh", "pr", "view", str(ns.number), "--json",
         "state,baseRefName,headRefName,isDraft,mergeable,title,body,statusCheckRollup,author"]))
    trunk = _trunk_admissions()
    confirmation = arc_confirmed_in(trunk, ns.epic) if trunk is not None else None
    by_admitted = node_admitted_in(trunk, ns.by) if trunk is not None else False
    reason = land_refusal(info, confirmation, ns.by, by_admitted)
    if reason:
        _refuse(reason)
    head = info.get("headRefName")
    if ns.dry_run:
        print(f"result: report — DRY RUN: would land PR #{ns.number} "
              f"({head} -> main) on arc {ns.epic} confirmed by bdo "
              f"({confirmation}); nothing merged")
        return
    # Merge only — never --delete-branch. Across the fleet the head branch is
    # checked out in a worktree, and `gh pr merge --delete-branch` fails on the
    # LOCAL branch delete *after* the remote merge has already succeeded — which
    # raised here before the receipt was written, leaving the loop blind to real
    # merges. The SessionStart gardener (done-line 0037) prunes the merged
    # worktree and branch; GitHub's delete_branch_on_merge clears the remote head.
    _run(["gh", "pr", "merge", str(ns.number), "--squash"])
    receipt = _merge_receipt(ns.number, ns.epic, ns.by, confirmation, head)
    if _push_receipt_to_trunk(receipt):
        print(f"result: done — merge-node landed PR #{ns.number} ({head} -> main) "
              f"on bdo's confirmed arc {ns.epic}; receipt {receipt['id']} on the trunk. "
              "bdo was not asked — he confirmed the arc, the node landed it.")
    else:
        print(f"result: needs-you — PR #{ns.number} is MERGED to main, but its receipt "
              f"{receipt['id']} did not reach the trunk (push failed). The merge stands; "
              "the log is missing the record — reconcile it. Nothing was double-merged.")


def _story_args(parser):
    parser.add_argument("--title", required=True,
                        help="one line: what this PR did (never the branch name)")
    parser.add_argument("--story", required=True, metavar="TEXT",
                        help="the written narrative — one flowing story for a cold "
                             "reader: not fields, not a path, not a synopsis")


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
    create.add_argument("--rolling", action="store_true",
                        help="open as a GitHub draft: the session keeps "
                             "appending and the merge button stays disabled "
                             "until `ready` flips it (done-line 0017)")
    create.set_defaults(func=cmd_create)

    edit = verbs.add_parser("edit", help="rewrite an open PR's story")
    edit.add_argument("number", type=int)
    _story_args(edit)
    edit.set_defaults(func=cmd_edit)

    ready = verbs.add_parser(
        "ready", help="flip a rolling draft to AT THE STAMP — the one "
                      "merge signal (done-line 0017)")
    ready.add_argument("number", type=int)
    _story_args(ready)
    ready.add_argument("--red-ok", dest="red_ok", default="", metavar="WHY",
                       help="come to the stamp with a red suite anyway, "
                            "declaring why in the story (§9.5)")
    ready.set_defaults(func=cmd_ready)

    unready = verbs.add_parser(
        "unready", help="roll an at-the-stamp PR back to a draft (takes "
                        "the merge button away; no story needed)")
    unready.add_argument("number", type=int)
    unready.set_defaults(func=cmd_unready)

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

    integrate = verbs.add_parser(
        "integrate", help="merge a piece-PR into its epic branch (never main — "
                          "the trunk is bdo's)")
    integrate.add_argument("number", type=int)
    integrate.add_argument("--delete-branch", dest="delete_branch",
                           action="store_true",
                           help="delete the piece branch after integrating")
    integrate.set_defaults(func=cmd_integrate)

    land = verbs.add_parser(
        "land", help="the merge-node lands a confirmed-arc PR on main (bdo's "
                     "2026-06-11 amendment; never run on a PR you authored)")
    land.add_argument("number", type=int)
    land.add_argument("--epic", required=True,
                      help="the arc this PR serves; bdo's confirm-arc on the "
                           "trunk is the authorization the node executes (D-4)")
    land.add_argument("--by", required=True,
                      help="the merge-node's identity, e.g. merge-node.claude.v0")
    land.add_argument("--dry-run", dest="dry_run", action="store_true",
                      help="run every guard and print the decision; merge nothing")
    land.set_defaults(func=cmd_land)

    confirm = verbs.add_parser(
        "confirm", help="bdo's arc stamp, pushed to the trunk: confirm-arc that "
                        "actually reaches origin/main so the merge-node reads it")
    confirm.add_argument("--epic", required=True,
                         help="the arc to confirm, e.g. epic.owner-harness")
    confirm.add_argument("--by", required=True,
                         help="bdo — the owner's stamp, refused otherwise (D-4)")
    confirm.add_argument("--off", action="store_true",
                         help="withdraw a prior confirmation (supersede, never erase)")
    confirm.set_defaults(func=cmd_confirm)

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
