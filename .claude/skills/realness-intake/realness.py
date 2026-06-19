#!/usr/bin/env python3
"""realness-intake pen (done-line 0042): the inbound half of bdo's GitHub
surface, for *realness*.

Sibling to arc-intake (done-line 0038). arc-intake lets bdo confirm an *arc*
by closing an issue; this lets him make a *gate real* the same way — never a
CLI, never a custom UI (his stated rule: he acts from GitHub, on whatever device he's at). A
mock pipeline stage with a built, tested real backing becomes one issue he
closes with a plain-language comment; this pen is the deterministic gh I/O
around that gesture: open the issue, find the ones he closed, read his closing
comment, reply with what the system did.

What is deliberately NOT here: the judgment of his intent (confirm / decline /
unclear) and the privileged act it authorizes. Meaning is the model's to
recover (the realness-intake SKILL), and the act — `loop.node admit-real
--by bdo` — is run by the session only on a *clear confirm*, because his
closed-issue-with-comment is the authorization the session executes (D-4: a
node propels, bdo authorizes). This pen only moves bytes to and from GitHub.
Outward reach (gh) lives in the pen, never in loop/ (hard rule).

The marker carries TWO names, not one: the stage being made real and the real
node that backs it — because `admit-real` needs both, and a realness gesture
that named only the stage would leave the session guessing which backing bdo
meant (absence is information; we never guess the node).

Verbs:
  open    --stage <mock-node> --node <real-node> --repo <owner/repo> [--body-file F]
            open the stage's one realness-confirm issue (marked + labelled)
  pending --repo <owner/repo> [--json]
            the realness issues bdo has CLOSED and not yet acted on, each with
            the (stage, node) it carries and his closing comment — the worklist
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

LABEL = "realness-confirm"
DONE_LABEL = "intake-done"
# the marker carries both names; \S+? so a stage or node id with dots/dashes
# is captured whole, and the two keys are order-fixed for a stable round-trip.
MARKER_RE = re.compile(
    r"<!--\s*ontum:realness-confirm\s+stage=(\S+?)\s+node=(\S+?)\s*-->")


def marker(stage, node):
    return f"<!-- ontum:realness-confirm stage={stage} node={node} -->"


def names_from_body(body):
    """The (stage_node, real_node) a realness-intake issue carries, parsed from
    its hidden marker — or None if the body has none (not one of ours; never
    guessed at). Both names or neither: a half-marker is not a marker."""
    m = MARKER_RE.search(body or "")
    return (m.group(1), m.group(2)) if m else None


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
    body = (body or
            f"The gate **{ns.stage}** has a built, tested real backing "
            f"(**{ns.node}**) waiting. Making it the live gate is your realness "
            "stamp — it changes what the loop trusts to judge. Close this issue "
            "with a comment in your own words — make it real, hold, or decline — "
            "and the system will read your intent, run the admission on your "
            "authorization if you confirmed, and reply here with what it did."
            ) + "\n\n" + marker(ns.stage, ns.node)
    url = _run(["gh", "issue", "create", "--repo", ns.repo,
                "--title", f"Make {ns.stage} real ({ns.node}) — confirm to wire it live",
                "--body", body, "--label", LABEL]).splitlines()[-1].strip()
    print(f"result: done — opened realness-confirm issue for {ns.stage} "
          f"-> {ns.node}: {url}. bdo closes it with a comment; realness-intake "
          "reads his intent.")


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
            continue  # already acted on — never double-admit (I-2)
        names = names_from_body(it.get("body"))
        if not names:
            continue
        stage, node = names
        view = _run(["gh", "issue", "view", str(it["number"]), "--repo", ns.repo,
                     "--json", "comments"])
        comments = (json.loads(view) or {}).get("comments", []) if view else []
        work.append({"number": it["number"], "stage": stage, "node": node,
                     "title": it.get("title", ""),
                     "comment": bdo_comment(comments, owner)})
    if ns.json:
        print(json.dumps(work))
        return
    if not work:
        print("result: report — no closed realness-confirm issues await reading")
        return
    print(f"result: report — {len(work)} closed realness issue(s) await your reading:")
    for w in work:
        print(f"  #{w['number']} {w['stage']} -> {w['node']} — bdo: "
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
    o = sub.add_parser("open", help="open a stage's realness-confirm issue")
    o.add_argument("--stage", required=True, help="the mock stage node, e.g. placement-gate.mock.v0")
    o.add_argument("--node", required=True, help="the real backing node, e.g. placement-gate.det.v1")
    o.add_argument("--repo", required=True)
    o.add_argument("--body-file", dest="body_file", default=None)
    o.set_defaults(func=cmd_open)
    p = sub.add_parser("pending", help="closed realness issues awaiting a reading")
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
