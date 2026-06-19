#!/usr/bin/env python3
"""The workspace binding — a branch belongs to its work, not the session.

Done-line 0121, increment #2 of the session-gateway arc
(`session-gateway.proposal.md` §4, §5, fork §12b.4). The root cause the arc
fights: a git working tree has one HEAD, so "the current branch" is a shared
mutable global a mortal session treats as private state. Increment #1 (the
HEAD-intent guard, done-line 0118) made a session assert *which branch* it is
on. This makes a branch belong to its **work**: a `workspace_claimed`
admission binds a branch to the durable claim it serves (an atom id, a
work-id), attributed `--by`. A branch tied to a mortal session is born to be
orphaned (session dies → branch strands); a branch tied to the claimed work
survives — a new session re-claims and continues (§4).

The shape mirrors `trust.py`: a focused governance module that folds one
admission kind into current state, plus a pure refusal the git pen imports.
The git pen enforces (it imports `binding_refusal`); this module never drives
git and never reaches the network (loop's hard rules).

One active binding per branch, by construction: a re-claim **supersedes** the
branch's current binding (a new session taking the work over), and `release`
supersedes it with nothing (the route home — the branch is free; the full
gardener reclaim is increment #4). History is never erased — every claim and
release stands on the log; the fold reads the live ones (I: superseding
admissions, never erasure).

Enforcement is opt-in via the git pen's `--claim`, exactly as the HEAD-intent
guard is opt-in via `--on`: omitting it skips the check (backward
compatible), until a later chapter of the arc makes binding the default once
provisioning (#3/#4) guarantees every workspace carries one.

Stdlib only. Every CLI invocation ends with a clear result on stdout:
done | report | needs-you.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from loop.reconcile import DEFAULT_ROOT, append_line, now_ts, short_hash

CLAIMED = "workspace_claimed"
RELEASED = "workspace_released"


def _admissions(root):
    """Every admission line, torn-tail tolerant — a half-written line is
    dropped and re-derived next pass (the log-is-truth property). The same
    small fold `trust.py` and the other governance modules each keep; reading
    the log is deliberately not abstracted behind a shared reader, so a change
    to one fold can never quietly change another's truth."""
    path = Path(root) / "log" / "admissions.jsonl"
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def active_bindings(root=DEFAULT_ROOT):
    """The fold: {branch: binding}, where a binding is the live
    `workspace_claimed` record for that branch — after dropping every
    admission a later one supersedes (a re-claim or a release). Because a
    claim auto-supersedes the branch's prior binding and a release supersedes
    a claim with nothing, this yields exactly the branches that are currently
    bound, each to one claim."""
    adms = _admissions(root)
    superseded = {a["supersedes"] for a in adms if a.get("supersedes")}
    bound = {}
    for a in adms:
        if a.get("type") != CLAIMED or a.get("id") in superseded:
            continue
        branch = a.get("branch")
        if not branch:
            continue
        bound[branch] = a  # one live claim per branch, by construction
    return bound


def binding_for(branch, root=DEFAULT_ROOT):
    """The live binding record for `branch`, or None if the branch is
    unbound. The one read the git pen needs at commit time."""
    return active_bindings(root).get(branch)


# ----------------------------------------------------------- the pure refusal
# Mirrors trust.rung_refusal / git pen's commit_refusal: the *reason* a commit
# may not happen is a pure function over its inputs, so the suite hits it
# directly without writing the log or driving git.

def binding_refusal(branch, claim, bindings):
    """Why a commit asserting it serves `claim` may not run on `branch`, or
    None. `bindings` is {branch: binding-record} (from `active_bindings`).

    The contract the git pen enforces when a session passes `--claim`:

      - an UNBOUND branch is refused — claim the workspace first, so the
        branch belongs to its work and a later session can find it;
      - a branch BOUND TO A DIFFERENT claim is refused — the §10 bite: "I am
        doing work W" and "this branch serves W2" are each locally fine and
        must not fit (the collision turned into a clean deny);
      - a branch bound to THIS claim passes.

    Omitting `--claim` never reaches here (the pen skips the check) — opt-in,
    like the HEAD-intent guard's `--on`."""
    if not claim:
        return None  # opt-in: no asserted claim, no binding check
    if not branch:
        return ("detached HEAD has no branch to bind — a session commits on its "
                "claude/* branch, claimed for its work")
    live = (bindings or {}).get(branch)
    if live is None:
        return (
            f"branch '{branch}' is not bound to any work — claim it first so it "
            f"belongs to '{claim}', not to a mortal session:\n"
            f"  python -m loop.workspace claim --branch {branch} --claim {claim} --by <you>\n"
            "a branch tied to no claim strands when the session dies (the "
            "session-gateway arc, §4)."
        )
    bound_claim = live.get("claim")
    if bound_claim != claim:
        return (
            f"branch '{branch}' is bound to '{bound_claim}', not '{claim}' — "
            f"you are committing under the wrong claim (binding {live.get('id')}, "
            f"by {live.get('by')}). This is the branch collision turned into a "
            "clean deny (done-line 0121): work for a different claim does not "
            "ride this branch. Use that work's own branch/worktree, or re-claim "
            "this branch if the work has genuinely changed hands:\n"
            f"  python -m loop.workspace claim --branch {branch} --claim {claim} --by <you>"
        )
    return None


# --------------------------------------------------------------- the writers

def claim(root, branch, work, by, supersedes=None):
    """Bind `branch` to `work`, attributed `--by`. A re-claim auto-supersedes
    the branch's current live binding (one binding per branch, by
    construction), unless an explicit `supersedes` is given. Returns the
    admission written."""
    if supersedes is None:
        current = binding_for(branch, root)
        if current is not None:
            supersedes = current["id"]
    adm = {
        "id": "adm." + short_hash(CLAIMED, branch, str(work), str(by), now_ts()),
        "type": CLAIMED,
        "branch": branch,
        "claim": work,
        "by": by,
        "supersedes": supersedes,
        "ts": now_ts(),
    }
    append_line(root / "log" / "admissions.jsonl", adm)
    return adm


def release(root, branch, by):
    """Free `branch` — the route home (§3). A `workspace_released` admission
    that supersedes the branch's live binding; the branch is then unbound and
    can be re-claimed. Returns the admission, or None if the branch was not
    bound (nothing to release — surfaced by the caller)."""
    current = binding_for(branch, root)
    if current is None:
        return None
    adm = {
        "id": "adm." + short_hash(RELEASED, branch, str(by), now_ts()),
        "type": RELEASED,
        "branch": branch,
        "by": by,
        "supersedes": current["id"],
        "ts": now_ts(),
    }
    append_line(root / "log" / "admissions.jsonl", adm)
    return adm


# ----------------------------------------------------------------- read CLI

def binding_lines(root):
    bound = active_bindings(root)
    if not bound:
        return ["no branches are bound — every workspace is free "
                "(claim one: python -m loop.workspace claim --branch <b> "
                "--claim <work> --by <you>)"]
    lines = [f"{len(bound)} bound branch(es):"]
    for branch, b in sorted(bound.items()):
        lines.append(f"  {branch}  ->  {b.get('claim')}  (by {b.get('by')}, {b.get('id')})")
    return lines


def cmd_list(ns):
    for line in binding_lines(ns.root):
        print(line)
    print("result: report — read-only fold over workspace_claimed admissions")


def cmd_claim(ns):
    adm = claim(ns.root, ns.branch, ns.claim, ns.by)
    sup = f" (superseding {adm['supersedes']})" if adm.get("supersedes") else ""
    print(f"result: done — bound '{ns.branch}' to '{ns.claim}' by {ns.by}{sup} "
          f"[{adm['id']}]")


def cmd_release(ns):
    adm = release(ns.root, ns.branch, ns.by)
    if adm is None:
        print(f"result: report — '{ns.branch}' was not bound; nothing to release")
        return
    print(f"result: done — released '{ns.branch}' by {ns.by} [{adm['id']}]")


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="workspace", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT,
                        help=argparse.SUPPRESS)
    verbs = parser.add_subparsers(dest="verb")

    lst = verbs.add_parser("list", help="the active binding per branch — read-only fold")
    lst.set_defaults(func=cmd_list)

    cl = verbs.add_parser("claim", help="bind a branch to its work (a re-claim supersedes)")
    cl.add_argument("--branch", required=True)
    cl.add_argument("--claim", required=True, metavar="WORK",
                    help="the durable work the branch serves (an atom id / work-id)")
    cl.add_argument("--by", required=True, help="who claims it (attribution)")
    cl.set_defaults(func=cmd_claim)

    rel = verbs.add_parser("release", help="free a branch — the route home (re-claimable after)")
    rel.add_argument("--branch", required=True)
    rel.add_argument("--by", required=True)
    rel.set_defaults(func=cmd_release)

    ns = parser.parse_args(argv)
    if not getattr(ns, "func", None):
        ns.func = cmd_list
    ns.func(ns)


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    main()
