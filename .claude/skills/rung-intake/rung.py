#!/usr/bin/env python3
"""rung-intake pen (done-line 0051): the inbound half of bdo's GitHub
surface, for *trust rungs*.

Sibling of arc-intake (done-line 0038) and realness-intake (done-line 0042).
Those let bdo confirm an arc and make a gate real from GitHub; this lets him
grant a trust-ladder rung (loop/trust.py) the same way — never a CLI, never a
custom UI (his stated rule: he acts from GitHub on his phone). An agent class
that needs a capability becomes one issue he closes with a plain-language
comment; this pen is the deterministic gh I/O around that gesture: open the
issue, find the ones he closed, read his closing comment, reply with what the
system did.

What is deliberately NOT here: the judgment of his intent (confirm / decline /
unclear) and the privileged act it authorizes. Meaning is the model's to
recover (the rung-intake SKILL), and the act — `loop.node admit-rung --class
<c> --capability <p> --by bdo` — is run by the session only on a *clear
confirm*, because his closed-issue-with-comment is the authorization the
session executes (D-4: a node propels, bdo authorizes). This pen only moves
bytes to and from GitHub. Outward reach (gh) lives in the pen, never in loop/
(hard rule).

The LOCKED rung is refused at the pen: ontum-touch is not a question bdo gets
asked. Unlocking it is a deliberate change to the admission pen by bdo (the
lock is the pen itself, never a flag) — an issue inviting a yes would be a
gesture-shaped key to a door the system promised stays locked. The same
refusal covers an unknown class or capability: this pen opens only questions
the admission pen could answer (one vocabulary, imported from loop/trust.py —
no drift between what is asked and what can be granted).

Verbs:
  open    --class <agent-class> --capability <rung> --repo <owner/repo> [--body-file F]
            open the one rung-confirm issue (marked + labelled); refuses LOCKED
  pending --repo <owner/repo> [--json]
            the rung issues bdo has CLOSED and not yet acted on, each with the
            (class, capability) it carries and his closing comment — the worklist
  reply   --issue <n> --repo <owner/repo> --body <text> [--reopen] [--done]
            echo back what was done (always), reopen to ask again (unclear),
            or mark intake-done so a re-run never double-acts (I-2 at the surface)

Stdlib plus loop/trust.py for the ladder vocabulary; ends with a clear stdout
result (D-6): done | report | needs-you.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from loop import trust  # noqa: E402  (one vocabulary: classes, rungs, the lock)

LABEL = "rung-confirm"
DONE_LABEL = "intake-done"
# the marker carries both names; \S+? so a class or capability survives whole,
# and the two keys are order-fixed for a stable round-trip.
MARKER_RE = re.compile(
    r"<!--\s*ontum:rung-confirm\s+class=(\S+?)\s+capability=(\S+?)\s*-->")


def marker(agent_class, capability):
    return f"<!-- ontum:rung-confirm class={agent_class} capability={capability} -->"


def names_from_body(body):
    """The (agent_class, capability) a rung-intake issue carries, parsed from
    its hidden marker — or None if the body has none (not one of ours; never
    guessed at). Both names or neither: a half-marker is not a marker."""
    m = MARKER_RE.search(body or "")
    return (m.group(1), m.group(2)) if m else None


def open_refusal(agent_class, capability):
    """Why this rung may not even be ASKED, or None. Exactly the admission
    pen's own refusals (unknown class, unknown capability, the LOCKED top) —
    the pen opens no question `loop.node admit-rung` could not answer. The
    grantor check is satisfied with the only grantor there is: the issue is
    bdo's gesture by construction."""
    return trust.rung_refusal(agent_class, capability, trust.GRANTOR)


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
    reason = open_refusal(ns.agent_class, ns.capability)
    if reason:
        print(f"result: report — refused to open a rung-confirm issue: {reason}")
        return 2
    body = ""
    if ns.body_file:
        with open(ns.body_file, encoding="utf-8") as fh:
            body = fh.read()
    ladder = " < ".join(trust.CAPABILITIES)
    body = (body or
            f"The agent class **{ns.agent_class}** "
            f"({trust.AGENT_CLASSES[ns.agent_class]}) holds no "
            f"**'{ns.capability}'** rung, so every act needing it is refused — "
            "the trust ladder (loop/trust.py) denies what no admission grants. "
            f"Granting a rung is your trust stamp: it changes what this class "
            f"of summoned agent may do from then on (the ladder is cumulative: "
            f"{ladder}; ontum-touch stays LOCKED for everyone and is never "
            "asked). Close this issue with a comment in your own words — "
            "grant, hold, or decline — and the system will read your intent, "
            "run the admission on your authorization if you confirmed, and "
            "reply here with what it did."
            ) + "\n\n" + marker(ns.agent_class, ns.capability)
    url = _run(["gh", "issue", "create", "--repo", ns.repo,
                "--title", f"Grant {ns.agent_class} the '{ns.capability}' rung "
                           "— confirm to let it act",
                "--body", body, "--label", LABEL]).splitlines()[-1].strip()
    print(f"result: done — opened rung-confirm issue for {ns.agent_class} / "
          f"{ns.capability}: {url}. bdo closes it with a comment; rung-intake "
          "reads his intent.")
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
        names = names_from_body(it.get("body"))
        if not names:
            continue
        agent_class, capability = names
        view = _run(["gh", "issue", "view", str(it["number"]), "--repo", ns.repo,
                     "--json", "comments"])
        comments = (json.loads(view) or {}).get("comments", []) if view else []
        work.append({"number": it["number"], "agent_class": agent_class,
                     "capability": capability, "title": it.get("title", ""),
                     "comment": bdo_comment(comments, owner)})
    if ns.json:
        print(json.dumps(work))
        return 0
    if not work:
        print("result: report — no closed rung-confirm issues await reading")
        return 0
    print(f"result: report — {len(work)} closed rung issue(s) await your reading:")
    for w in work:
        print(f"  #{w['number']} {w['agent_class']} / {w['capability']} — bdo: "
              f"{w['comment'][:200] or '(closed with no comment)'}")
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
    o = sub.add_parser("open", help="open a class/capability rung-confirm issue")
    o.add_argument("--class", dest="agent_class", required=True,
                   help="agent class: " + ", ".join(trust.AGENT_CLASSES))
    o.add_argument("--capability", required=True,
                   help="the rung asked for (ontum-touch is LOCKED and refused here)")
    o.add_argument("--repo", required=True)
    o.add_argument("--body-file", dest="body_file", default=None)
    o.set_defaults(func=cmd_open)
    p = sub.add_parser("pending", help="closed rung issues awaiting a reading")
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
