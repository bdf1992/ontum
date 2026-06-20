#!/usr/bin/env python3
"""fence/barrier.py — the gate/fence primitive (done-line 0148).

bdo's shape (2026-06-20): we have *gateways* (policy — they decide), but no
deterministic *gate* that closes a gateway and no *fence* around the route. A
gateway is political: it asks "is this *actor* permitted?" and answers from
admitted who-may records (RBAC, a trust rung, the owner's stamp). A gate and a
fence are *not* political and must not be — they are physical:

    you can see through it, you can't pass it, you can't climb it,
    and touching it bites.

Three terms, the atom first (bdo: "Barrier might be an atomic example"):

- **barrier-link** — the atom. A pure, actor-blind predicate over an act's
  *observable form*: `decide(link, act) -> {allow, reason}`. Its three laws are
  what make it physical rather than political:
    L1 deterministic — same act, same verdict, always (a pure function).
    L2 model-free    — no inference, no network in the decision path.
    L3 actor-blind   — THE discriminator. The verdict reads only the act and
                       the object (the argv, the raw command, the path, an
                       object flag), never *who* acts or what they are
                       authorized to do. A barrier gives every actor the same
                       answer; a gateway does not.

- **fence** — a *closed loop* of barrier-links around a named **territory**. A
  fence that does not loop accomplishes nothing — you walk around it. Its laws
  are bdo's physical adjectives, made into teeth:
    closed     — every route INTO the territory is covered. The route taxonomy
                 is front / seam / top: the obvious command (front), the
                 **meshed** seams between links (a `python` that shells `git`,
                 hidden from a quote-stripping front link), and the **tall**
                 top (an over-it route through a higher abstraction). Cover the
                 front alone and you have a wall segment, not a fence.
    barbed     — a blocked act is WITNESSED (recorded on contact), never a
                 silent deflection. Every link names a witness sink.
    not-opaque — every link carries a cold-reader reason: you can see THROUGH
                 the fence to why you are stopped. No black-box denial.

- **gate** — a barrier-link at a sanctioned opening *in* a fence: a link with
  `on_match="allow"` marks the one route the fence intends you to use. The
  opening mechanism is real in `decide` (an allow-link returns allow); gate
  *precedence* — an opening that admits an act an otherwise-closed fence would
  block — is NAMED here but not yet enforced by `validate_fence`/`covered`, a
  later increment like the installed fences. The fence is the loop; the gate is
  the opening in it.

This module is the CONTRACT + its validators, not yet an installed fence. It is
read-only and stdlib-only (fence/'s law): the gate is a predicate, deterministic
and side-effect-free. `validate_link` / `validate_fence` are the §10 teeth, and
`tests/test_barrier.py` proves each one bites on the real trunk-mutation
territory — including that our *own* git fence is torn at the seam.

CLI:
  python fence/barrier.py            the contract + the trunk-mutation reading
  python fence/barrier.py --json     the contract + reading as data
"""

from __future__ import annotations

import argparse
import copy
import fnmatch
import json
import pathlib
import re
import sys

# The fence package already owns ONE argv-prefix matcher (policy.prefix_matches)
# — reuse it rather than fork a twin (fence/CLAUDE.md: "one table, two surfaces,
# no twin lists to drift"). The path insert mirrors command_guard so both
# `python fence/barrier.py` and `from fence import barrier` resolve the sibling.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from fence.policy import prefix_matches  # noqa: E402

# ---------------------------------------------------------------------------
# the barrier-link atom: predicate kinds, each over the act's OBSERVABLE FORM.
# There is deliberately no kind that reads the actor or an authorization
# record — actor-blindness (L3) is structural: it cannot be expressed in the
# data, and validate_link refuses anything that tries.
# ---------------------------------------------------------------------------

ALLOWED_KINDS = {
    "argv-prefix",     # the argv list starts with a prefix (literals / tuples)
    "command-regex",   # a regex matches a named text field of the act
    "path-glob",       # the act's path matches a glob
    "object-flag",     # a named flag on the OBJECT being acted on is set
}

# Fragments a barrier-link's predicate key must never CONTAIN: they read WHO
# acts, not the act. Their presence turns a barrier into a gateway, so validate
# refuses them. The hard guarantee is that `decide` is never handed the actor at
# all (the structural half); this is the second tooth — a substring scan (so
# `actor_id`, `caller_role`, `principal` are all caught), the grain observe.py
# uses. It is a defensive name-denylist, not a completeness proof: a smuggled
# key under a wholly novel name still slips it, but stays inert because `decide`
# never reads it.
RESERVED_ACTOR_FRAGMENTS = (
    "actor", "caller", "grant", "author", "rung", "stamp", "ident", "who",
    "rbac", "permission", "credential", "user", "principal", "subject",
    "uid", "role", "owner", "agent",
)

# What text field a command-regex reads. "command" is the RAW command (sees a
# shelled git inside quotes — seals the seam); "command_guard_sees" is the
# post-quote-strip view (what command_guard actually inspects — and where the
# seam tear lives). Naming both lets a fence's links differ in what they read,
# which is exactly how one link closes a seam another leaves open.
COMMAND_FIELDS = ("command", "command_guard_sees")


def _predicate_matches(predicate, act):
    """Pure: does this predicate match this act's observable form? Reads only
    the act and the object — never the actor (it is not in scope)."""
    kind = predicate.get("kind")
    if kind == "argv-prefix":
        return prefix_matches(act.get("argv", []), predicate.get("prefix", ()))
    if kind == "command-regex":
        field = predicate.get("over", "command")
        return re.search(predicate.get("pattern", ""),
                         act.get(field, "") or "") is not None
    if kind == "path-glob":
        return fnmatch.fnmatch(act.get("path", "") or "",
                               predicate.get("glob", ""))
    if kind == "object-flag":
        obj = act.get("object", {}) or {}
        return bool(obj.get(predicate.get("flag", "")))
    # an unknown kind never matches; validate_link refuses it up front so a
    # fence can never be built on one (this is the unreachable-by-design path).
    return False


def decide(link, act):
    """The barrier-link, pure and actor-blind: does this link BLOCK this act?

    Returns {allow: bool, reason: str|None}. A link is a deny/allow rule with a
    deterministic predicate; with no match it has no opinion (allow, deny-list
    semantics). The `act` carries only observable form — argv, command(s),
    path, object flags — so there is nowhere here to read the actor (L3).
    """
    matched = _predicate_matches(link.get("predicate", {}), act)
    if not matched:
        return {"allow": True, "reason": None}
    if link.get("on_match") == "allow":
        return {"allow": True, "reason": link.get("reason")}
    return {"allow": False, "reason": link.get("reason")}


def validate_link(link):
    """The barrier-link's §10 teeth — the problems that disqualify it as a
    *physical* barrier, in cold-reader language. Empty list == a valid link."""
    problems = []
    predicate = link.get("predicate", {}) or {}
    kind = predicate.get("kind")

    # L3 actor-blind: only the observable-form kinds are admissible.
    if kind not in ALLOWED_KINDS:
        problems.append(
            f"reads outside the act's observable form: predicate kind {kind!r} "
            f"is not one of {sorted(ALLOWED_KINDS)} — a barrier decides on the "
            "act and the object, never on who acts (that is a gateway)")
    # L3, second tooth: no predicate key may NAME an authorization concept (a
    # substring scan, so actor_id / caller_role / principal are all caught).
    smuggled = sorted(k for k in predicate
                      if any(frag in k.lower() for frag in RESERVED_ACTOR_FRAGMENTS))
    if smuggled:
        problems.append(
            f"smuggles actor-authorization into the predicate ({', '.join(smuggled)}) "
            "— a barrier is actor-blind; route who-may decisions to a gateway")
    # a degenerate predicate matches EVERYTHING and would block all traffic
    # while looking like a real link — the validator's job is to refuse it. An
    # empty pattern (`re.search('', x)` always hits), an empty argv prefix
    # (matches any argv), an empty glob (`fnmatch('','')` is True), or a blank
    # object flag are each a block-all link wearing a kind. Require the
    # discriminating field per kind.
    if kind == "argv-prefix" and not predicate.get("prefix"):
        problems.append("argv-prefix names no prefix — an empty prefix matches "
                        "every argv (a block-all link); name the verbs")
    if kind == "path-glob" and not str(predicate.get("glob", "") or "").strip():
        problems.append("path-glob names no glob — an empty glob matches a "
                        "pathless act (a block-all link); name the glob")
    if kind == "object-flag" and not str(predicate.get("flag", "") or "").strip():
        problems.append("object-flag names no flag — name the object flag it reads")
    # a command-regex must read a known field, with a non-empty, compilable pattern.
    if kind == "command-regex":
        field = predicate.get("over", "command")
        if field not in COMMAND_FIELDS:
            problems.append(
                f"command-regex reads unknown field {field!r}; one of {COMMAND_FIELDS}")
        pattern = predicate.get("pattern", "")
        if not str(pattern or "").strip():
            problems.append("command-regex names no pattern — an empty pattern "
                            "matches every command (a block-all link)")
        else:
            try:
                re.compile(pattern)
            except re.error as exc:
                problems.append(f"command-regex pattern does not compile: {exc}")

    if link.get("on_match") not in ("block", "allow"):
        problems.append("on_match must be 'block' or 'allow'")
    # not-opaque: a cold-reader reason is mandatory — no black-box denial.
    if not str(link.get("reason", "") or "").strip():
        problems.append(
            "opaque: no cold-reader reason — a fence is not opaque, a session "
            "that hits it must see WHY it is stopped")
    # barbed: a blocked act must be witnessed (recorded on contact).
    if link.get("on_match") == "block" and \
            not str(link.get("witness", "") or "").strip():
        problems.append(
            "unbarbed: names no witness sink — touching the fence must bite "
            "(record the contact), never deflect silently")
    return problems


# ---------------------------------------------------------------------------
# the fence: a closed loop of links around a territory, validated for closure
# (front/seam/top), barbed-ness, and non-opacity.
# ---------------------------------------------------------------------------

ROUTE_CLASSES = ("front", "seam", "top")  # the perimeter the loop must close
ROUTE_GLOSS = {
    "front": "the obvious, direct command",
    "seam": "the meshed gap between links — a route that slips a link that "
            "reads the wrong view (e.g. a quote-stripped command)",
    "top": "the tall over-it route — the same effect through a higher "
           "abstraction or escalation",
}


def covered(fence, act):
    """Pure: does ANY link in the fence block this act? (closure is per-route
    'some link bites here'.)"""
    return any(not decide(link, act)["allow"] for link in fence.get("links", []))


def validate_fence(fence):
    """The fence's §10 teeth: a closed loop, barbed, not opaque. Returns the
    problems that make it not a fence (an open perimeter is a wall segment).
    Empty list == a real fence."""
    problems = []
    links = fence.get("links", [])
    routes = fence.get("routes", [])

    # every link must itself be a valid physical barrier.
    for link in links:
        for p in validate_link(link):
            problems.append(f"link {link.get('id', '?')!r}: {p}")

    # closed, part 1 — the route taxonomy must be ENUMERATED. A fence that
    # never names its seams and top has not looked for the ways around; an
    # un-enumerated class is an unguessed gap, the meshed/tall discipline.
    present = {r.get("class") for r in routes}
    for cls in ROUTE_CLASSES:
        if cls not in present:
            problems.append(
                f"closure: the territory enumerates no {cls!r} route "
                f"({ROUTE_GLOSS[cls]}) — a fence must cover front, seam, and "
                "top; an un-enumerated class is an unguessed gap")

    # closed, part 2 — every enumerated route must be covered by some link.
    for route in routes:
        cls = route.get("class")
        if cls not in ROUTE_CLASSES:
            problems.append(
                f"route {route.get('id','?')!r}: unknown class {cls!r}; "
                f"one of {ROUTE_CLASSES}")
            continue
        if not covered(fence, route.get("example_breach", {})):
            problems.append(
                f"closure: route {route.get('id','?')!r} ({cls}) is UNCOVERED — "
                f"the fence is open at the {cls} ({ROUTE_GLOSS[cls]}); "
                f"{route.get('note', 'a real act walks straight through')}")
    return problems


def is_closed(fence):
    """True when the fence loops with no gap — the one-line verdict."""
    return not validate_fence(fence)


# ---------------------------------------------------------------------------
# the reference territory: trunk-mutation. Every route that changes `main`.
# Used by the CLI and the kill-test to show the laws bite on real ground.
# ---------------------------------------------------------------------------

TRUNK_MUTATION_ROUTES = [
    {
        "id": "git-push-main",
        "class": "front",
        "note": "the direct push to trunk",
        "example_breach": {
            "argv": ["git", "push", "origin", "main"],
            "command": "git push origin main",
            "command_guard_sees": "git push origin main",
        },
    },
    {
        "id": "shelled-git-push",
        "class": "seam",
        "note": "command_guard strips quoted spans (so prose is not mistaken "
                "for a command), so the git inside the quotes is invisible to "
                "it — the seam our real git fence leaves open",
        "example_breach": {
            "argv": ["python", "-c",
                     "import subprocess;subprocess.run(['git','push','origin','main'])"],
            "command": "python -c \"import subprocess;subprocess.run("
                       "['git','push','origin','main'])\"",
            # what command_guard inspects AFTER strip_quoted removes the "..."
            "command_guard_sees": "python -c  ",
        },
    },
    {
        "id": "gh-pr-merge",
        "class": "top",
        "note": "merging the PR is the over-the-top route to changing main "
                "without a local push at all",
        "example_breach": {
            "argv": ["gh", "pr", "merge", "12", "--squash"],
            "command": "gh pr merge 12 --squash",
            "command_guard_sees": "gh pr merge 12 --squash",
        },
    },
]

# What command_guard ACTUALLY covers today, modelled as barrier-links: it
# reads the quote-stripped command, so it bites the front and the top — and
# misses the seam, because the shelled git lives in the stripped-out quotes.
_GIT_PEN = "the PR pen / git pen (.claude/skills/branch-ritual)"
COMMAND_GUARD_LINKS = [
    {
        "id": "cg-git-push",
        "predicate": {"kind": "command-regex", "over": "command_guard_sees",
                      "pattern": r"\bgit\s+push\b"},
        "on_match": "block",
        "reason": f"raw `git push` is denied; trunk lands via {_GIT_PEN} and "
                  "the merge-node, never a session push (fence/policy.py).",
        "witness": ".ai-native/log/tool-use.jsonl",
    },
    {
        "id": "cg-gh-pr-merge",
        "predicate": {"kind": "command-regex", "over": "command_guard_sees",
                      "pattern": r"\bgh\s+pr\s+merge\b"},
        "on_match": "block",
        "reason": "raw `gh pr merge` is denied; main lands only through the "
                  "independent merge-node after bdo confirms the arc (D-4).",
        "witness": ".ai-native/log/tool-use.jsonl",
    },
]

# The seam-sealing link: it reads the RAW command, so the shelled git can no
# longer hide in the quotes. Adding it to the command_guard links is what turns
# the torn perimeter into a closed fence.
SEAM_LINK = {
    "id": "raw-git-push",
    # bounded between git and push: only quotes, commas, and whitespace may sit
    # between them — enough to match the shelled `['git','push']` and the plain
    # `git push`, but NOT `git commit -m "fix the push bug"` (letters between
    # them break the match). A greedy `[\s\S]*` here would block the git pen's
    # own commit traffic — the false positive the review caught.
    "predicate": {"kind": "command-regex", "over": "command",
                  "pattern": r"\bgit\b['\"\s,]+push\b"},
    "on_match": "block",
    "reason": "a `git push` reached by shelling out (subprocess, a script) is "
              "still a push to trunk; it is denied however it is spelled. Land "
              f"through {_GIT_PEN}.",
    "witness": ".ai-native/log/tool-use.jsonl",
}


def command_guard_fence():
    """The trunk-mutation fence as command_guard constitutes it today — torn
    at the seam (the kill-test and the CLI both read this). A deep copy, so a
    caller that edits a returned link (even a nested predicate) can never reach
    back and mutate the module constants — purity is structural, not by luck."""
    return copy.deepcopy({
        "territory": "trunk-mutation",
        "routes": TRUNK_MUTATION_ROUTES,
        "links": list(COMMAND_GUARD_LINKS),
    })


def closed_trunk_fence():
    """The same fence with the seam sealed — the reference for what a closed
    trunk-mutation perimeter looks like."""
    fence = command_guard_fence()
    fence["links"].append(copy.deepcopy(SEAM_LINK))
    return fence


CONTRACT = {
    "primitive": "gate/fence",
    "barrier_link_laws": {
        "deterministic": "same act -> same verdict (a pure function)",
        "model_free": "no inference or network in the decision path",
        "actor_blind": "the verdict reads only the act and the object, never "
                       "who acts or their authorization (the discriminator "
                       "from a gateway)",
    },
    "fence_laws": {
        "closed": "every route into the territory is covered — front, seam "
                  "(meshed), and top (tall); a fence that does not loop is a "
                  "wall segment",
        "barbed": "a blocked act is witnessed, never silently deflected",
        "not_opaque": "every link carries a cold-reader reason",
    },
    "route_classes": {cls: ROUTE_GLOSS[cls] for cls in ROUTE_CLASSES},
    "allowed_predicate_kinds": sorted(ALLOWED_KINDS),
    "gate": "a barrier-link with on_match='allow' at a sanctioned opening; the "
            "opening is real in decide(), gate-precedence over a closed fence "
            "is a later increment (named, not yet enforced)",
}


def trunk_reading():
    """The read-only finding: is our real git fence (command_guard) a closed
    fence around trunk-mutation? Returns the territory, the gaps, and the
    closed reference."""
    torn = command_guard_fence()
    return {
        "territory": "trunk-mutation",
        "command_guard_fence_closed": is_closed(torn),
        "gaps": validate_fence(torn),
        "with_seam_sealed_closed": is_closed(closed_trunk_fence()),
    }


def render():
    print("the gate/fence primitive — physical, not political (read-only)\n")
    print("a barrier-link is actor-blind:")
    for law, gloss in CONTRACT["barrier_link_laws"].items():
        print(f"  {law:14s} {gloss}")
    print("\na fence loops around a territory:")
    for law, gloss in CONTRACT["fence_laws"].items():
        print(f"  {law:14s} {gloss}")
    print("\nthe route taxonomy a fence must close:")
    for cls in ROUTE_CLASSES:
        print(f"  {cls:6s} {ROUTE_GLOSS[cls]}")
    reading = trunk_reading()
    print(f"\nreading the real trunk-mutation fence (command_guard today):")
    print(f"  closed? {reading['command_guard_fence_closed']}")
    for gap in reading["gaps"]:
        print(f"  - {gap}")
    print(f"  with the seam sealed (a raw-command link): "
          f"closed? {reading['with_seam_sealed_closed']}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true",
                    help="emit the contract and the trunk reading as data")
    args = ap.parse_args(argv)
    if args.json:
        print(json.dumps({"contract": CONTRACT, "reading": trunk_reading()},
                         indent=2, ensure_ascii=False))
    else:
        render()
    print("\nresult: done — the gate/fence contract (read-only); a fence is "
          "real only when it loops closed, barbed, and not opaque")
    return 0


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
