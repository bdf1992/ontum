#!/usr/bin/env python3
"""The issue pen: a governed door for GitHub issue mutations (#412).

GitHub issue creation, closing, and commenting were *ungoverned*: a session
typed raw `gh issue close` / `gh issue comment` and the act left no trace on
the log. Worse, the fence rule that should have caught it was decision
`prompt` — and a `prompt` rule is a silent no-op on the Claude surface (only
`forbidden` rules compile into `command_guard.DENY_RULES`). So raw `gh issue`
slipped straight through: the prompt-parity hole.

This pen is the paved path the fence now points at (the `gh-issue-mutate`
rule is `forbidden`). It is the issue-side sibling of the PR pen: a mutation
goes through one writer, and that writer **records the act on the log** with
provenance — who did it, why, when — so a governed issue close is a fact the
loop can fold, never a side effect that vanished into GitHub.

Like the reflector pen (`reflect.py`) and the gate pen (`gate.py`), outward
reach (the `gh` CLI) lives here, in the pen, via subprocess — never in
`loop/`, which is network-free. Forbidding raw `gh issue` at the
command_guard layer does NOT block this pen: the guard watches the *Bash*
tool, and the pen shells out to `gh` from inside Python where no Bash hook
sees it — exactly as raw `gh pr` is forbidden while `pr.py` works.

The provenance record is the teeth: a governed close carries a reason and a
`--by`, refused at the door otherwise (an empty reason or a missing signer is
a close with no accountability — the thing this pen exists to prevent). The
record lands ONLY after the gh call succeeds — a close that GitHub refused is
never written as if it happened.

Usage:
  python .claude/skills/issue/issue.py create --title "<t>" --body "<text>" --by <who>
  python .claude/skills/issue/issue.py close <number> --reason "<why>" --by <who>
  python .claude/skills/issue/issue.py comment <number> --body "<text>" --by <who>
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

# The repo root: the real worktree (it carries loop/), overridable for tests
# that point the provenance log elsewhere. loop/ is imported from here.
ROOT = Path(os.environ.get("ONTUM_REPO_ROOT") or Path(__file__).resolve().parents[3])
sys.path.insert(0, str(ROOT))

from loop.reconcile import append_line, now_ts, short_hash  # noqa: E402


def default_events_path():
    """Where provenance lands: the append-only truth log (the only writer
    is loop.reconcile.append_line — line-atomic, torn-tail tolerant)."""
    return ROOT / ".ai-native" / "log" / "events.jsonl"


def gh(args):
    """The one outward reach. Runs `gh` from the repo so it infers the repo
    from the git remote; returns the completed process. Injectable as
    `gh_run` so the §10 test drives the verbs without touching the network."""
    return subprocess.run(["gh"] + args, capture_output=True, text=True,
                          cwd=str(ROOT), timeout=120)


def _record(type_, number, by, **fields):
    """One provenance record, id minted as a short content hash the way the
    loop mints event ids (loop.reconcile.short_hash), ts in UTC iso."""
    payload = {k: v for k, v in fields.items() if v is not None}
    rec = {
        "type": type_,
        "number": number,
        "by": by,
        "kind": "issue-governance",
        "id": "evt." + short_hash(type_, str(number), by, *map(str, payload.values())),
        "ts": now_ts(),
    }
    rec.update(payload)
    return rec


def do_close(number, reason, by, *, repo=None, gh_run=None, events_path=None):
    """Post the reason as a closing comment and close the issue, then append
    ONE issue.closed provenance record. Refuses an empty reason or a missing
    signer BEFORE any gh call — and records ONLY after the close succeeds."""
    reason = (reason or "").strip()
    if not reason:
        raise ValueError("a governed close carries a reason — the closing "
                         "comment IS the provenance; refusing an empty --reason")
    by = (by or "").strip()
    if not by:
        raise ValueError("a governed close carries a signer — refusing a "
                         "missing --by (no act on the log is unattributed)")
    gh_run = gh_run or gh
    args = ["issue", "close", str(number), "--comment", reason]
    if repo:
        args += ["--repo", repo]
    proc = gh_run(args)
    if proc.returncode != 0:
        raise RuntimeError(f"gh issue close failed (exit {proc.returncode}): "
                           f"{(proc.stderr or proc.stdout or '').strip()}")
    rec = _record("issue.closed", number, by, reason=reason)
    append_line(events_path or default_events_path(), rec)
    return rec


def do_comment(number, body, by, *, repo=None, gh_run=None, events_path=None):
    """Post a comment, then append ONE issue.commented provenance record.
    Refuses an empty body or a missing signer before any gh call."""
    body = (body or "").strip()
    if not body:
        raise ValueError("a governed comment carries a body — refusing an "
                         "empty --body")
    by = (by or "").strip()
    if not by:
        raise ValueError("a governed comment carries a signer — refusing a "
                         "missing --by (no act on the log is unattributed)")
    gh_run = gh_run or gh
    args = ["issue", "comment", str(number), "--body", body]
    if repo:
        args += ["--repo", repo]
    proc = gh_run(args)
    if proc.returncode != 0:
        raise RuntimeError(f"gh issue comment failed (exit {proc.returncode}): "
                           f"{(proc.stderr or proc.stdout or '').strip()}")
    rec = _record("issue.commented", number, by, body=body)
    append_line(events_path or default_events_path(), rec)
    return rec


def do_create(title, body, by, *, repo=None, gh_run=None, events_path=None):
    """Create an issue, then append ONE issue.created provenance record carrying
    the new number and url. Refuses an empty title/body or a missing signer
    before any gh call — and records ONLY after the create succeeds (an issue
    GitHub refused is never written as if it happened). This is the verb the
    fence's forbid-raw-`gh issue` left without a paved path: a session could
    close/comment governed but had no governed way to OPEN one, so a new issue
    could only go raw — now forbidden — or not at all."""
    title = (title or "").strip()
    if not title:
        raise ValueError("a governed create carries a title — refusing an empty "
                         "--title")
    body = (body or "").strip()
    if not body:
        raise ValueError("a governed create carries a body — refusing an empty "
                         "--body (an issue with no statement is not accountable)")
    by = (by or "").strip()
    if not by:
        raise ValueError("a governed create carries a signer — refusing a "
                         "missing --by (no act on the log is unattributed)")
    gh_run = gh_run or gh
    args = ["issue", "create", "--title", title, "--body", body]
    if repo:
        args += ["--repo", repo]
    proc = gh_run(args)
    if proc.returncode != 0:
        raise RuntimeError(f"gh issue create failed (exit {proc.returncode}): "
                           f"{(proc.stderr or proc.stdout or '').strip()}")
    url = (proc.stdout or "").strip().splitlines()[-1].strip() if proc.stdout else ""
    number = url.rsplit("/", 1)[-1] if url else None
    rec = _record("issue.created", number, by, title=title, url=url or None)
    append_line(events_path or default_events_path(), rec)
    return rec


def cmd_close(ns):
    try:
        rec = do_close(ns.number, ns.reason, ns.by, repo=ns.repo)
    except ValueError as e:
        print(f"result: report — refused: {e}")
        return 2
    except RuntimeError as e:
        print(f"result: needs-you — {e}")
        return 2
    print(f"  closed issue #{ns.number}; provenance {rec['id']} on the log")
    print(f"result: done — issue #{ns.number} closed with its reason; the act "
          f"is recorded ({rec['id']})")
    return 0


def cmd_comment(ns):
    try:
        rec = do_comment(ns.number, ns.body, ns.by, repo=ns.repo)
    except ValueError as e:
        print(f"result: report — refused: {e}")
        return 2
    except RuntimeError as e:
        print(f"result: needs-you — {e}")
        return 2
    print(f"  commented on issue #{ns.number}; provenance {rec['id']} on the log")
    print(f"result: done — comment posted on issue #{ns.number}; the act is "
          f"recorded ({rec['id']})")
    return 0


def cmd_create(ns):
    try:
        rec = do_create(ns.title, ns.body, ns.by, repo=ns.repo)
    except ValueError as e:
        print(f"result: report — refused: {e}")
        return 2
    except RuntimeError as e:
        print(f"result: needs-you — {e}")
        return 2
    where = f" (#{rec['number']})" if rec.get("number") else ""
    print(f"  created issue{where} {rec.get('url') or ''}; provenance {rec['id']} on the log")
    print(f"result: done — issue created{where}; the act is recorded ({rec['id']})")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    np_ = sub.add_parser("create", help="open a new issue; record the act")
    np_.add_argument("--title", required=True, help="the issue title")
    np_.add_argument("--body", required=True, help="the issue body (the statement)")
    np_.add_argument("--by", required=True, help="who opened it (the signer)")
    np_.add_argument("--repo", default=None, help="owner/repo (default: inferred from cwd)")
    np_.set_defaults(func=cmd_create)

    cp = sub.add_parser("close", help="close an issue with a reason; record the act")
    cp.add_argument("number", help="the issue number")
    cp.add_argument("--reason", required=True, help="the closing comment / provenance")
    cp.add_argument("--by", required=True, help="who closed it (the signer)")
    cp.add_argument("--repo", default=None, help="owner/repo (default: inferred from cwd)")
    cp.set_defaults(func=cmd_close)

    mp = sub.add_parser("comment", help="comment on an issue; record the act")
    mp.add_argument("number", help="the issue number")
    mp.add_argument("--body", required=True, help="the comment text")
    mp.add_argument("--by", required=True, help="who commented (the signer)")
    mp.add_argument("--repo", default=None, help="owner/repo (default: inferred from cwd)")
    mp.set_defaults(func=cmd_comment)

    ns = ap.parse_args(argv)
    return ns.func(ns)


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
