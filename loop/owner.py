#!/usr/bin/env python3
"""The owner-gesture index (epic.graded-speed / the owner-harness): the one
place that answers *"bdo needs to decide X — what is the gesture surface?"*

bdo authorizes by a gesture on a SURFACE (closing/commenting a GitHub issue in
plain language, wherever he is), never by running a command. The openers that
put a decision on that surface already exist — but scattered across five files
(`arc-intake`, `realness-intake`, `rung-intake`, `policy-intake`, `issue.py`),
with no index. A session that cannot *find* the surface falls back to the thing
it can name: a CLI line at bdo (the offload the hard rules forbid; the failure
this index exists to end).

This is the `gaps`/`parity` grain on a new axis: a read-only fold that maps each
owner-decision KIND to the **one opener pen** that surfaces it, and **refuses a
CLI-at-owner route** — every row either names a resolvable opener pen, or is
flagged `no-surface` as a real gap (a decision with no GitHub surface yet, today
only reachable by a bdo-only command — which the index surfaces rather than
papering over with "hand bdo the command").

The §10 teeth (`validate`, proven non-vacuous in `tests/test_owner.py`): a row
whose opener does not RESOLVE to a real pen on disk is a ghost; a row that smells
like a CLI-at-owner route (an `--by bdo` confirm command dressed as an opener) is
refused. The index can never legitimise handing bdo a command.

Read-only, stdlib. CLI ends `done | report` (D-6).
"""

import argparse
import sys
from pathlib import Path

from loop.reconcile import DEFAULT_ROOT

# Repo root = the .ai-native root's parent (the gaps/census convention).
def _repo(root):
    return Path(root).resolve().parent

# The index: owner-decision KIND -> the one opener pen that surfaces it.
# `opener` is a repo-relative pen path that must resolve (the teeth). A decision
# with no GitHub surface yet carries opener=None and no_surface=True — a named
# gap, never a CLI-at-owner fallback.
DECISIONS = (
    {
        "kind": "arc-confirm",
        "what": "confirm an arc, authorizing the merge-node to land its work",
        "opener": ".claude/skills/arc-intake/intake.py",
        "open_verb": "intake.py open --epic <epic.id> --repo <owner/repo>",
        "label": "arc-confirm",
        "no_surface": False,
    },
    {
        "kind": "realness-confirm",
        "what": "trust a built mock stage to judge for real",
        "opener": ".claude/skills/realness-intake/realness.py",
        "open_verb": "realness.py open --stage <stage.id> --repo <owner/repo>",
        "label": "realness-confirm",
        "no_surface": False,
    },
    {
        "kind": "rung-grant",
        "what": "grant a class/capability a trust-ladder rung",
        "opener": ".claude/skills/rung-intake/rung.py",
        "open_verb": "rung.py open --class <id> --repo <owner/repo>",
        "label": "rung-confirm",
        "no_surface": False,
    },
    {
        "kind": "gateway-policy",
        "what": "permit a (caller, surface, mind) inference-gateway policy",
        "opener": ".claude/skills/policy-intake/policy.py",
        "open_verb": "policy.py open --caller <c> --surface <s> --mind <m> --repo <owner/repo>",
        "label": "policy-confirm",
        "no_surface": False,
    },
    {
        "kind": "owner-ask",
        "what": "any other owner decision, audit, FYI, or question",
        "opener": ".claude/skills/issue/issue.py",
        "open_verb": "issue.py open --title <t> --body <body> --by <who>",
        "label": None,
        "no_surface": False,
    },
    {
        "kind": "done-supersede",
        "what": "move a frozen done-line's bar (bdo's alone)",
        "opener": None,
        "open_verb": "python -m loop.pen supersede-done ... --by bdo  (NO GitHub surface today)",
        "label": None,
        "no_surface": True,
    },
)

# A CLI-at-owner smell: an "opener" that is really a confirm command run at bdo.
_CLI_AT_OWNER = ("--by bdo", "confirm-arc", "admit-real", "admit-rung")


def validate(decisions=DECISIONS, root=DEFAULT_ROOT):
    """Return the list of problems (empty == sound). The teeth:
    - a row with no_surface=False MUST cite an opener pen that RESOLVES on disk
      (a ghost opener is caught);
    - no row's opener may be a CLI-at-owner command (a raw `--by bdo` confirm
      dressed as a surface) — the index can never legitimise the offload;
    - a no_surface row must NOT cite a resolvable pen (it would not be a gap)."""
    repo = _repo(root)
    problems = []
    seen = set()
    for d in decisions:
        kind = d.get("kind", "?")
        if kind in seen:
            problems.append(f"{kind}: duplicate decision kind")
        seen.add(kind)
        verb = (d.get("open_verb") or "")
        if not d.get("no_surface"):
            op = d.get("opener")
            if not op:
                problems.append(f"{kind}: no_surface is false but no opener pen named")
            elif not (repo / op).is_file():
                problems.append(f"{kind}: ghost opener — {op} does not resolve on disk")
            # the CLI-at-owner refusal: a surfaced decision's verb must route
            # through a pen's `open`, never a confirm command run at bdo
            if any(s in verb for s in _CLI_AT_OWNER):
                problems.append(f"{kind}: opener is a CLI-at-owner route "
                                f"({verb!r}) — route through the pen's open, "
                                "never a command run at bdo")
        else:
            if d.get("opener") and (repo / d["opener"]).is_file():
                problems.append(f"{kind}: flagged no-surface but a pen resolves "
                                f"({d['opener']}) — it is not a gap")
    return problems


def index(root=DEFAULT_ROOT):
    """The owner-decision -> surface map, validated. Each entry carries the one
    move; a no-surface decision is a named gap, never a CLI-at-owner route."""
    problems = validate(root=root)
    if problems:  # a broken index must not silently hand out routes
        raise ValueError("owner-gesture index is unsound: " + "; ".join(problems))
    return list(DECISIONS)


def surface_for(kind, root=DEFAULT_ROOT):
    """The one opener for a decision kind, or None if no such kind. The answer to
    'bdo needs to decide X — what is the gesture surface?'"""
    for d in index(root=root):
        if d["kind"] == kind:
            return d
    return None


def render(decisions):
    for d in decisions:
        if d.get("no_surface"):
            print(f"decision: {d['kind']} — {d['what']}")
            print(f"  surface: NONE YET (gap) — {d['open_verb']}")
        else:
            print(f"decision: {d['kind']} — {d['what']}")
            print(f"  surface: bdo closes/comments a `{d['label'] or 'issue'}` "
                  f"issue; open it with  {d['open_verb']}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=Path(DEFAULT_ROOT))
    ap.add_argument("--kind", default=None,
                    help="name the surface for one decision kind")
    args = ap.parse_args(argv)

    problems = validate(root=args.root)
    if problems:
        print("result: report — the owner-gesture index is UNSOUND:")
        for p in problems:
            print(f"  - {p}")
        return 1
    if args.kind:
        d = surface_for(args.kind, root=args.root)
        if not d:
            kinds = ", ".join(x["kind"] for x in DECISIONS)
            print(f"result: report — no owner-decision kind '{args.kind}'. "
                  f"Known: {kinds}")
            return 1
        render([d])
        print("result: done — that is the surface; open it, then bdo gestures "
              "on GitHub (never a command handed to him)")
        return 0
    render(DECISIONS)
    gaps = sum(1 for d in DECISIONS if d.get("no_surface"))
    print(f"result: done — {len(DECISIONS)} owner-decision surfaces "
          f"({gaps} without a GitHub surface yet — the named gaps); a session "
          "routes every owner decision here, never a CLI line at bdo")
    return 0


if __name__ == "__main__":
    sys.exit(main())
