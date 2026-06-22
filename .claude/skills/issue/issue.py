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
  python .claude/skills/issue/issue.py open --title "<t>" --body "<text>" --by <who>
  python .claude/skills/issue/issue.py close <number> --reason "<why>" --by <who>
  python .claude/skills/issue/issue.py comment <number> --body "<text>" --by <who>

`open` is the verb the owner-harness was missing: a session puts a decision
(an audit, an arc-confirm, an owner-ask) onto bdo's GitHub surface — recorded
on the log — instead of handing bdo a CLI command or bypassing with raw `gh`
(the gap that forced the CLI-at-owner fallback; named the day this was built).
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


def do_open(title, body, by, *, repo=None, gh_run=None, events_path=None):
    """Open a new issue with title+body and append ONE issue.opened provenance
    record. Refuses an empty title, an empty body, or a missing signer BEFORE
    any gh call — and records ONLY after the create succeeds (an open GitHub
    refused is never written as if it happened). Parses the new issue number
    from the URL `gh issue create` prints on stdout."""
    title = (title or "").strip()
    if not title:
        raise ValueError("a governed open carries a title — refusing an empty "
                         "--title")
    body = (body or "").strip()
    if not body:
        raise ValueError("a governed open carries a body — refusing an empty "
                         "--body/--body-file (an issue with no body is no ask)")
    by = (by or "").strip()
    if not by:
        raise ValueError("a governed open carries a signer — refusing a missing "
                         "--by (no act on the log is unattributed)")
    gh_run = gh_run or gh
    args = ["issue", "create", "--title", title, "--body", body]
    if repo:
        args += ["--repo", repo]
    proc = gh_run(args)
    if proc.returncode != 0:
        raise RuntimeError(f"gh issue create failed (exit {proc.returncode}): "
                           f"{(proc.stderr or proc.stdout or '').strip()}")
    url = ""
    for line in (proc.stdout or "").splitlines():
        line = line.strip()
        if "/issues/" in line:
            url = line
    number = url.rstrip("/").split("/")[-1] if "/issues/" in url else None
    rec = _record("issue.opened", number, by, title=title, url=url or None)
    append_line(events_path or default_events_path(), rec)
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


def do_reopen(number, reason, by, *, repo=None, gh_run=None, events_path=None):
    """Reopen a closed issue and post the reason as a comment, then append ONE
    issue.reopened provenance record. The recovery verb: a governed close can be
    wrong (a stale auto-close, a premature one), and un-closing must carry the
    same accountability as closing — a reason and a signer — so the reversal is
    itself a recorded act, never a silent un-doing. Refuses an empty reason or a
    missing signer before any gh call; records ONLY after the reopen succeeds."""
    reason = (reason or "").strip()
    if not reason:
        raise ValueError("a governed reopen carries a reason — why the close was "
                         "wrong IS the provenance; refusing an empty --reason")
    by = (by or "").strip()
    if not by:
        raise ValueError("a governed reopen carries a signer — refusing a "
                         "missing --by (no act on the log is unattributed)")
    gh_run = gh_run or gh
    args = ["issue", "reopen", str(number), "--comment", reason]
    if repo:
        args += ["--repo", repo]
    proc = gh_run(args)
    if proc.returncode != 0:
        raise RuntimeError(f"gh issue reopen failed (exit {proc.returncode}): "
                           f"{(proc.stderr or proc.stdout or '').strip()}")
    rec = _record("issue.reopened", number, by, reason=reason)
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


def cmd_open(ns):
    body = ns.body
    if ns.body_file:
        body = Path(ns.body_file).read_text(encoding="utf-8")
    try:
        rec = do_open(ns.title, body, ns.by, repo=ns.repo)
    except ValueError as e:
        print(f"result: report — refused: {e}")
        return 2
    except RuntimeError as e:
        print(f"result: needs-you — {e}")
        return 2
    where = rec.get("url") or f"#{rec['number']}"
    print(f"  opened issue {where}; provenance {rec['id']} on the log")
    print(f"result: done — issue opened ({where}); the act is recorded "
          f"({rec['id']})")
    return 0


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


def cmd_reopen(ns):
    try:
        rec = do_reopen(ns.number, ns.reason, ns.by, repo=ns.repo)
    except ValueError as e:
        print(f"result: report — refused: {e}")
        return 2
    except RuntimeError as e:
        print(f"result: needs-you — {e}")
        return 2
    print(f"  reopened issue #{ns.number}; provenance {rec['id']} on the log")
    print(f"result: done — issue #{ns.number} reopened with its reason; the act "
          f"is recorded ({rec['id']})")
    return 0


def cmd_comment(ns):
    body = ns.body
    if ns.body_file:
        body = Path(ns.body_file).read_text(encoding="utf-8")
    try:
        rec = do_comment(ns.number, body, ns.by, repo=ns.repo)
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


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    op = sub.add_parser("open", help="open a new issue with title+body; record the act")
    op.add_argument("--title", required=True, help="the issue title")
    op.add_argument("--body", default=None, help="the issue body text")
    op.add_argument("--body-file", default=None, help="read the body from a file")
    op.add_argument("--by", required=True, help="who opened it (the signer)")
    op.add_argument("--repo", default=None, help="owner/repo (default: inferred from cwd)")
    op.set_defaults(func=cmd_open)

    cp = sub.add_parser("close", help="close an issue with a reason; record the act")
    cp.add_argument("number", help="the issue number")
    cp.add_argument("--reason", required=True, help="the closing comment / provenance")
    cp.add_argument("--by", required=True, help="who closed it (the signer)")
    cp.add_argument("--repo", default=None, help="owner/repo (default: inferred from cwd)")
    cp.set_defaults(func=cmd_close)

    rp = sub.add_parser("reopen", help="reopen a closed issue with a reason; record the act")
    rp.add_argument("number", help="the issue number")
    rp.add_argument("--reason", required=True, help="why the close was wrong / the provenance")
    rp.add_argument("--by", required=True, help="who reopened it (the signer)")
    rp.add_argument("--repo", default=None, help="owner/repo (default: inferred from cwd)")
    rp.set_defaults(func=cmd_reopen)

    mp = sub.add_parser("comment", help="comment on an issue; record the act")
    mp.add_argument("number", help="the issue number")
    mp.add_argument("--body", default=None, help="the comment text")
    mp.add_argument("--body-file", default=None, help="read the comment from a file (for long/structured bodies — avoids shell escaping)")
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
