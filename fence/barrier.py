#!/usr/bin/env python3
"""fence/barrier.py — the barrier primitive (epic.barriers, done-line 0175).

A barrier is the genus of bounded control, and its NATURE is an attribute, not
the epic (bdo, 2026-06-21 — the reframe that re-cut this from the stale
epic.physical-barriers): a barrier is either PHYSICAL (the gate/fence — what
this module builds) or POLITICAL (the gateway). This module is the
**physical-nature** primitive.

bdo's shape (2026-06-20): we have *gateways* (the political-nature barriers —
they decide), but no deterministic *gate* that closes a gateway and no *fence*
around the route. A gateway is political: it asks "is this *actor* permitted?"
and answers from admitted who-may records (RBAC, a trust rung, the owner's
stamp). A gate and a fence are *not* political and must not be — they are
physical:

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

Where this sits in the per-directory gateway stack (change-management.proposal.md,
the gatekeeping layers `fence · policy · guard · gate · threshold`). That
proposal's term-economy fix governs the words here: the repo's `*_guard` hooks
(`command_guard`, `write_guard`, …) are **gates** — they decide pass/deny on a
*thing flowing through* ("guard" is overloaded). So, mapped to the stack:
  - a **barrier-link** is one firm denial — an element of the stack's **Fence**
    layer (the `fence/policy.py` deny-list, generalized here past argv).
  - this module's **fence** is that Fence layer seen as a CLOSED perimeter around
    a territory — the deny-set a gate enforces. `command_guard_fence()` therefore
    means "the fence the `command_guard` *gate* enforces," NOT that `command_guard`
    is itself a fence (it is the gate).
  - this module's **gate** (an `on_match="allow"` opening) is a NARROWER sense
    than the stack's **Gate** layer (the pass/deny decider): here the opening *in*
    the fence, there the decider *at* the seam. The overload is flagged, not
    silently merged (the term-economy way); reconciling the two senses in code
    (renaming) is a later atom, not this prose.

This module is the CONTRACT + its validators, and — since done-line 0150 — the
home of the first INSTALLED instance: `SEAM_LINK` is the raw-command seam tooth
that `command_guard` now imports and runs to seal the shelled-git-push the
prefix registry cannot reach. It is read-only and stdlib-only (fence/'s law):
the gate is a predicate, deterministic and side-effect-free. `validate_link` /
`validate_fence` are the §10 teeth, and `tests/test_barrier.py` proves each one
bites on the real trunk-mutation territory — including that command_guard's
prefix-rule REGISTRY alone is torn at the seam (a prefix rule runs over the
quote-stripped command; it structurally cannot read the raw command where the
shelled git lives), and that the raw seam tooth seals it.

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
        # A barrier-link is JSON, so a position-union arrives as a LIST
        # (`["push", "pull"]`); the shared policy matcher reads a union only as
        # a TUPLE (a bare list is one literal). Bridge it here so the same
        # union the Codex prefix rules express works from a JSON link too.
        prefix = tuple(tuple(p) if isinstance(p, list) else p
                       for p in predicate.get("prefix", ()))
        return prefix_matches(act.get("argv", []), prefix)
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

# command_guard's PREFIX-RULE registry (fence/policy.py), modelled as
# barrier-links: each prefix rule is compiled to a regex over the QUOTE-STRIPPED
# command, so it bites the front and the top — and structurally misses the seam,
# because the shelled git lives in the stripped-out quotes a prefix rule never
# sees. This is the torn-perimeter the seam tooth (SEAM_LINK) was built to seal.
_GIT_PEN = "the PR pen / git pen (.claude/skills/branch-ritual)"
PREFIX_RULE_LINKS = [
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
    "id": "shelled-git-push",
    # The prose-safe key to the shelled push: the argv-LIST shape — git and push
    # as separate quoted tokens joined by a comma (`['git','push']`,
    # `("git", "push")`). A commit message that merely mentions "git push" uses a
    # SPACE between unquoted words, never quote-comma-quote, so this never
    # false-blocks the git pen's own traffic (the trap a `git[\s'",]+push`
    # pattern fell into — it matched the space form in prose too). The plain
    # `git push` is the FRONT link's job (command_guard's existing git-push
    # rule); this link seals only the seam the quote-strip opens.
    "predicate": {"kind": "command-regex", "over": "command",
                  "pattern": r"""['"]git['"]\s*,\s*['"]push"""},
    "on_match": "block",
    "reason": "a `git push` reached by shelling out (subprocess with an argv "
              "list like ['git','push']) is still a push to trunk; it is denied "
              f"however it is spelled. Land through {_GIT_PEN}.",
    "witness": ".ai-native/log/tool-use.jsonl",
}


def prefix_rules_fence():
    """The trunk-mutation fence as command_guard's PREFIX-RULE registry covers
    it ALONE — torn at the seam (a prefix rule reads the quote-stripped command
    and structurally cannot reach the shelled git). This is the BEFORE: the
    finding that motivated the seam tooth. A deep copy, so a caller that edits a
    returned link (even a nested predicate) can never reach back and mutate the
    module constants — purity is structural, not by luck."""
    return copy.deepcopy({
        "territory": "trunk-mutation",
        "routes": TRUNK_MUTATION_ROUTES,
        "links": list(PREFIX_RULE_LINKS),
    })


def command_guard_fence():
    """The fence the LIVE `command_guard` *gate* enforces since done-line 0150:
    the prefix registry PLUS the raw seam tooth (SEAM_LINK) it now runs over the
    RAW command. Closed — the seam is sealed. Installed reality, not a reference:
    `command_guard` (the gate) imports SEAM_LINK and enforces exactly this."""
    fence = prefix_rules_fence()
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
    """The read-only reading of the trunk-mutation perimeter: the prefix
    registry alone (torn — the finding) versus the live command_guard with the
    seam tooth installed (closed — the seal)."""
    return {
        "territory": "trunk-mutation",
        "prefix_registry_closed": is_closed(prefix_rules_fence()),
        "prefix_registry_gaps": validate_fence(prefix_rules_fence()),
        "live_command_guard_closed": is_closed(command_guard_fence()),
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
    print(f"\nreading the trunk-mutation perimeter:")
    print(f"  prefix-rule registry alone — closed? "
          f"{reading['prefix_registry_closed']}")
    for gap in reading["prefix_registry_gaps"]:
        print(f"    - {gap}")
    print(f"  live command_guard (prefix registry + the raw seam tooth) — "
          f"closed? {reading['live_command_guard_closed']}")


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
