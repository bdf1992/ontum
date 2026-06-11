#!/usr/bin/env python3
"""arc-intake pen (done-line 0038): the inbound half of bdo's GitHub surface.

bdo steers from GitHub on his phone — never a CLI, never a custom UI. An arc
with PRs waiting becomes one issue he closes with a plain-language comment;
this pen is the deterministic gh I/O around that gesture: open the issue, find
the ones he closed, read his closing comment, reply with what the system did.

What is deliberately NOT here: the judgment of his intent (confirm / decline /
unclear). Meaning is the model's to recover, not a keyword's — a session reads
his words (the arc-intake SKILL) and decides. This pen only moves bytes to and
from GitHub. Outward reach (gh) lives in the pen, never in loop/ (hard rule).

Verbs:
  open    --epic <id> --repo <owner/repo> [--body-file F]
            open the arc's one confirm issue (marked + labelled so it is findable)
  pending --repo <owner/repo> [--json]
            the arc issues bdo has CLOSED and not yet acted on, each with the
            epic it carries and his closing comment — the session's worklist
  reply   --issue <n> --repo <owner/repo> --body <text> [--reopen] [--done]
            echo back what was done (always), reopen to ask again (unclear),
            or mark intake-done so a re-run never double-acts (I-2 at the surface)

Stdlib only; ends with a clear stdout result (D-6): done | report | needs-you.
"""

import argparse
import json
import re
import subprocess
import sys

LABEL = "arc-confirm"
DONE_LABEL = "intake-done"
MARKER_RE = re.compile(r"<!--\s*ontum:arc-confirm\s+epic=(\S+?)\s*-->")


def marker(epic):
    return f"<!-- ontum:arc-confirm epic={epic} -->"


def epic_from_body(body):
    """The epic an arc-intake issue carries, parsed from its hidden marker —
    or None if the body has none (not one of ours; never guessed at)."""
    m = MARKER_RE.search(body or "")
    return m.group(1) if m else None


def bdo_comment(comments, owner_login):
    """bdo's closing word: the last comment authored by the repo owner. His
    plain language is the intent the session reads — this only finds it."""
    mine = [c for c in (comments or [])
            if ((c.get("author") or {}).get("login") or "").lower()
            == (owner_login or "").lower()]
    return mine[-1].get("body", "").strip() if mine else ""


def has_label(labels, name):
    return any((l.get("name") if isinstance(l, dict) else l) == name
               for l in (labels or []))


def _run(args):
    proc = subprocess.run(args, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        print(f"result: needs-you — `{' '.join(args)}` failed: "
              f"{(proc.stderr or proc.stdout).strip()}")
        sys.exit(1)
    return proc.stdout.strip()


def cmd_open(ns):
    body = ""
    if ns.body_file:
        with open(ns.body_file, encoding="utf-8") as fh:
            body = fh.read()
    body = (body or f"Confirm the arc **{ns.epic}** to authorize the merge-node "
            "to land its open PRs. Close this issue with a comment in your own "
            "words — confirm, hold, or decline — and the system will read your "
            "intent, act, and reply here with what it did.") + "\n\n" + marker(ns.epic)
    url = _run(["gh", "issue", "create", "--repo", ns.repo,
                "--title", f"Arc {ns.epic} — confirm to land its work",
                "--body", body, "--label", LABEL]).splitlines()[-1].strip()
    print(f"result: done — opened arc-confirm issue for {ns.epic}: {url}. "
          "bdo closes it with a comment; arc-intake reads his intent.")


def _owner_login(repo):
    return repo.split("/")[0]


def cmd_pending(ns):
    raw = _run(["gh", "issue", "list", "--repo", ns.repo, "--state", "closed",
                "--label", LABEL, "--json", "number,title,body,labels"])
    issues = json.loads(raw) if raw else []
    owner = _owner_login(ns.repo)
    work = []
    for it in issues:
        if has_label(it.get("labels"), DONE_LABEL):
            continue  # already acted on — never double-land (I-2)
        epic = epic_from_body(it.get("body"))
        if not epic:
            continue
        view = _run(["gh", "issue", "view", str(it["number"]), "--repo", ns.repo,
                     "--json", "comments"])
        comments = (json.loads(view) or {}).get("comments", []) if view else []
        work.append({"number": it["number"], "epic": epic,
                     "title": it.get("title", ""),
                     "comment": bdo_comment(comments, owner)})
    if ns.json:
        print(json.dumps(work))
        return
    if not work:
        print("result: report — no closed arc-confirm issues await reading")
        return
    print(f"result: report — {len(work)} closed arc issue(s) await your reading:")
    for w in work:
        print(f"  #{w['number']} {w['epic']} — bdo: "
              f"{w['comment'][:200] or '(closed with no comment)'}")


def cmd_reply(ns):
    _run(["gh", "issue", "comment", str(ns.issue), "--repo", ns.repo,
          "--body", ns.body])
    if ns.reopen:
        _run(["gh", "issue", "reopen", str(ns.issue), "--repo", ns.repo])
    if ns.done:
        _run(["gh", "issue", "edit", str(ns.issue), "--repo", ns.repo,
              "--add-label", DONE_LABEL])
    state = "reopened to ask again" if ns.reopen else (
        "marked intake-done" if ns.done else "replied")
    print(f"result: done — {state} on issue #{ns.issue}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    o = sub.add_parser("open", help="open the arc's confirm issue")
    o.add_argument("--epic", required=True)
    o.add_argument("--repo", required=True)
    o.add_argument("--body-file", dest="body_file", default=None)
    o.set_defaults(func=cmd_open)
    p = sub.add_parser("pending", help="closed arc issues awaiting a reading")
    p.add_argument("--repo", required=True)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_pending)
    r = sub.add_parser("reply", help="echo back, reopen-to-ask, or mark done")
    r.add_argument("--issue", required=True, type=int)
    r.add_argument("--repo", required=True)
    r.add_argument("--body", required=True)
    r.add_argument("--reopen", action="store_true")
    r.add_argument("--done", action="store_true")
    r.set_defaults(func=cmd_reply)
    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
