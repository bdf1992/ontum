#!/usr/bin/env python3
"""policy-intake pen (done-line 0102): the inbound half of bdo's GitHub
surface, for *gateway policies* — the inference-plane AuthZ.

Fourth sibling of arc-intake (done-line 0038), realness-intake (0042), and
rung-intake (0051). Those let bdo confirm an arc, make a gate real, and grant a
trust rung from GitHub; this lets him set a gateway *policy* — the default-deny
RBAC that authorizes a (caller, surface, mind) inference (loop/inference.py) —
the same way: never a CLI, never a custom UI (his stated rule: he acts from
GitHub on his phone). A gateway caller held for want of a policy becomes one
issue he closes with a plain-language comment; this pen is the deterministic gh
I/O around that gesture: open the issue, find the ones he closed, read his
closing comment, reply with what the system did.

This is how bdo sets the BOUND of the inference-as-composition layer (his
framing, 2026-06-17): the settled, owner-stamped edge inside which just-in-time
inference composes behavior. The cut-verifier (done-line 0100) is the first
caller it gates — the gardener's branch cut is held by default-deny until a
policy set here permits (branch-ritual.garden, branch-cut, a mind).

What is deliberately NOT here: the judgment of his intent (permit / decline /
unclear) and the privileged act it authorizes. Meaning is the model's to
recover (the policy-intake SKILL), and the act — `loop.inference policy
--caller <c> --surface <s> --mind <m> --by bdo` — is run by the session only on
a *clear confirm*, because his closed-issue-with-comment is the authorization
the session executes (D-4: a node propels, bdo authorizes). This pen only moves
bytes to and from GitHub. Outward reach (gh) lives in the pen, never in loop/
(hard rule).

The vocabulary is imported from loop/inference.py, so this pen opens only
questions the admission pen could answer (policy_refusal) — no drift between
what is asked and what can be set.

Verbs:
  open    --caller <c> --surface <s> --mind <m> [--deny] --repo <owner/repo> [--body-file F]
            open the one policy-confirm issue (marked + labelled); refuses a
            malformed policy exactly as the admission pen would
  pending --repo <owner/repo> [--json]
            the policy issues bdo has CLOSED and not yet acted on, each parsed
            back to its (caller, surface, mind, permit) with his closing
            comment — the worklist
  reply   --issue <n> --repo <owner/repo> --body <text> [--reopen] [--done]
            echo back what was done (always), reopen to ask again (unclear),
            or mark intake-done so a re-run never double-acts (I-2 at the surface)

Stdlib plus loop/inference.py for the policy vocabulary; ends with a clear
stdout result (D-6): done | report | needs-you.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from loop import inference  # noqa: E402  (one vocabulary: policy_refusal, GRANTOR)

LABEL = "policy-confirm"
DONE_LABEL = "intake-done"
# the marker carries the four policy fields; \S+? so a wildcard '*' or a dotted
# id survives whole, and the keys are order-fixed for a stable round-trip.
MARKER_RE = re.compile(
    r"<!--\s*ontum:policy-confirm\s+caller=(\S+?)\s+surface=(\S+?)\s+"
    r"mind=(\S+?)\s+permit=(true|false)\s*-->")


def marker(caller, surface, mind, permit):
    return (f"<!-- ontum:policy-confirm caller={caller} surface={surface} "
            f"mind={mind} permit={'true' if permit else 'false'} -->")


def policy_from_body(body):
    """The (caller, surface, mind, permit) a policy-intake issue carries,
    parsed from its hidden marker — or None if the body has none (not one of
    ours; never guessed at). All four fields or none: a half-marker is not a
    marker."""
    m = MARKER_RE.search(body or "")
    return (m.group(1), m.group(2), m.group(3), m.group(4) == "true") if m else None


def open_refusal(caller, surface, mind):
    """Why this policy may not even be ASKED, or None. Exactly the admission
    pen's own refusal (a missing field), so the pen opens no question
    `loop.inference policy` could not answer. The grantor check is satisfied
    with the only grantor there is: the issue is bdo's gesture by construction."""
    return inference.policy_refusal(caller, surface, mind, inference.GRANTOR)


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
    permit = not ns.deny
    reason = open_refusal(ns.caller, ns.surface, ns.mind)
    if reason:
        print(f"result: report — refused to open a policy-confirm issue: {reason}")
        return 2
    body = ""
    if ns.body_file:
        with open(ns.body_file, encoding="utf-8") as fh:
            body = fh.read()
    verb = "permit" if permit else "deny"
    body = (body or
            f"The inference gateway **denies ({ns.caller}, {ns.surface}, "
            f"{ns.mind}) by default** — RBAC admits no thought without a rule "
            "(loop/inference.py, default-deny). Until a policy says otherwise, "
            "every inference that caller would make at that surface is refused, "
            "and anything waiting on it is held (safe). Setting this policy is "
            "your **AuthZ stamp**: it authorizes that caller to consult that "
            "mind at that surface — the settled bound inside which just-in-time "
            "inference composes behavior. Close this issue with a comment in "
            "your own words — **permit**, hold, or decline — and the system "
            "will read your intent, run the admission on your authorization if "
            f"you confirmed (`{verb}`), and reply here with what it did."
            ) + "\n\n" + marker(ns.caller, ns.surface, ns.mind, permit)
    title = (f"{verb.capitalize()} inference ({ns.caller}, {ns.surface}, "
             f"{ns.mind}) — confirm to authorize it")
    url = _run(["gh", "issue", "create", "--repo", ns.repo,
                "--title", title, "--body", body,
                "--label", LABEL]).splitlines()[-1].strip()
    print(f"result: done — opened policy-confirm issue for ({ns.caller}, "
          f"{ns.surface}, {ns.mind}) [{verb}]: {url}. bdo closes it with a "
          "comment; policy-intake reads his intent.")
    return 0


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
        pol = policy_from_body(it.get("body"))
        if not pol:
            continue
        caller, surface, mind, permit = pol
        view = _run(["gh", "issue", "view", str(it["number"]), "--repo", ns.repo,
                     "--json", "comments"])
        comments = (json.loads(view) or {}).get("comments", []) if view else []
        work.append({"number": it["number"], "caller": caller, "surface": surface,
                     "mind": mind, "permit": permit, "title": it.get("title", ""),
                     "comment": bdo_comment(comments, owner)})
    if ns.json:
        print(json.dumps(work))
        return 0
    if not work:
        print("result: report — no closed policy-confirm issues await reading")
        return 0
    print(f"result: report — {len(work)} closed policy issue(s) await your reading:")
    for w in work:
        verb = "permit" if w["permit"] else "deny"
        print(f"  #{w['number']} {verb} ({w['caller']}, {w['surface']}, "
              f"{w['mind']}) — bdo: {w['comment'][:200] or '(closed with no comment)'}")
    return 0


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
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    o = sub.add_parser("open", help="open a (caller, surface, mind) policy-confirm issue")
    o.add_argument("--caller", required=True, help="agent class / node id / '*'")
    o.add_argument("--surface", required=True, help="surface name / '*'")
    o.add_argument("--mind", required=True, help="mind id / '*'")
    o.add_argument("--deny", action="store_true",
                   help="ask to set a DENY rule (default is permit)")
    o.add_argument("--repo", required=True)
    o.add_argument("--body-file", dest="body_file", default=None)
    o.set_defaults(func=cmd_open)
    p = sub.add_parser("pending", help="closed policy issues awaiting a reading")
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
    return args.func(args) or 0


if __name__ == "__main__":
    sys.exit(main())
