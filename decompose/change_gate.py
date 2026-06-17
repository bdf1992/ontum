#!/usr/bin/env python3
"""The change-axis gate (done-line 0104) — the decomposition procedure's teeth.

A pure, read-only fold in the grain of `causality/term_economy.py` and
`loop/gaps.py`: stdlib only, no network, no subprocess, no writes. It reads
a *declared* decomposition manifest (a human or agent authors it, the same
way a `*.seed.json` is declared input) and **refuses** the cuts the
procedure forbids. A manifest is never made correct by passing here; the
gate only judges the one handed to it.

The load-bearing claim it defends (bdo, 2026-06-17): **modules align with
axes of independent change, not with categories of thing.** A module
boundary is justified only when it isolates one axis of independent
variation — a distinct *reason*, *rate*, or *authority* of change. The
change test (procedure step 6) is: a cut is good if you can change a
module's internals without touching its neighbours except through the
contract. This module makes that test mechanical.

The fork bdo confirmed (AI-native specialized): a seam-contract carries
`trust` / `authority` / `change_rate` as first-class required fields,
because the modules of an AI-native engine span code / model / agent /
context / memory — the contract between them *is* the protocol discipline
that lets them coexist. A seam without those fields is a smuggled seam.

The refusals, each a hardened invariant:

    smeared-axis       two modules declare the same change-axis — the §10
                       teeth: two locally-fine modules refuse to fit
    incomplete-axis    a module's axis lacks reason/rate/authority/kind
    dependency-cycle   depends_on forms a cycle — a false boundary
    uncontracted-seam  a dependency edge crosses no named contract
    smuggled-seam      a contract names a non-module, or omits the
                       AI-native fields trust/authority/change_rate

The teeth (§10, proven by tests/test_change_gate.py): bdo's coherent UI
split passes with zero findings, and each broken sibling — derived by
mutating that one coherent manifest — is refused for its own named
reason. A constant / always-coherent gate fails the broken cases; a
constant / always-refuse gate fails the coherent one.
"""

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "decompose" / "examples" / "ui-split.manifest.json"

# a module's axis must carry all four to be reasoned about (procedure step 2):
# the reason is its identity, the rate/authority/kind are how it varies.
AXIS_FIELDS = ("reason", "rate", "authority", "kind")

# the AI-native specialization (bdo's confirmed fork): a seam-contract must
# carry the protocol discipline as first-class fields, or it is smuggled.
CONTRACT_FIELDS = ("crosses", "trust", "authority", "change_rate")


def _norm(s):
    """An axis reason's identity: case- and whitespace-insensitive. Two
    modules that change for 'Aesthetic change' and 'aesthetic  change' are
    changing for the same reason — the smear the gate must catch."""
    return " ".join(str(s).split()).strip().lower()


def _finding(kind, subject, why):
    return {"kind": kind, "subject": subject, "why": why}


def incomplete_axis_findings(modules):
    """An axis that can't be reasoned about (procedure step 3): a module
    with no axis, or one missing any of reason/rate/authority/kind."""
    out = []
    for m in modules:
        name = m.get("name", "<unnamed>")
        axis = m.get("axis") or {}
        missing = [f for f in AXIS_FIELDS if not str(axis.get(f, "")).strip()]
        if missing:
            out.append(_finding(
                "incomplete-axis", name,
                f"axis missing {', '.join(missing)} — a module whose reason "
                "to change is undeclared cannot be cut against"))
    return out


def smeared_axis_findings(modules):
    """The §10 teeth: two modules declaring the same change-axis. Each is
    locally fine; together they refuse to fit, because one axis smeared
    across two modules means the boundary between them is false (overcut)."""
    by_reason = {}
    for m in modules:
        axis = m.get("axis") or {}
        reason = axis.get("reason")
        if not str(reason or "").strip():
            continue  # the missing-axis case; incomplete_axis owns it
        by_reason.setdefault(_norm(reason), []).append(m.get("name", "<unnamed>"))
    out = []
    for reason, names in by_reason.items():
        if len(names) > 1:
            out.append(_finding(
                "smeared-axis", " + ".join(sorted(names)),
                f"these modules change for one reason ({reason!r}) — one axis "
                "smeared across many modules is a false boundary (overcut); "
                "they are really one module"))
    return out


def cycle_findings(modules):
    """A dependency cycle (procedure step 4): the things in the cycle are
    really one module, or there is a missing third they both point to. A
    DAG is the orientation a coherent decomposition admits."""
    names = {m.get("name") for m in modules}
    graph = {m.get("name"): [d for d in (m.get("depends_on") or []) if d in names]
             for m in modules}
    WHITE, GREY, BLACK = 0, 1, 2
    colour = {n: WHITE for n in graph}
    out = []
    seen = set()

    def visit(node, stack):
        colour[node] = GREY
        for nxt in graph.get(node, []):
            if colour.get(nxt) == GREY:
                cyc = stack[stack.index(nxt):] + [nxt]
                key = frozenset(cyc)
                if key not in seen:
                    seen.add(key)
                    out.append(_finding(
                        "dependency-cycle", " -> ".join(cyc),
                        "depends_on forms a cycle — a false boundary; the "
                        "modules in the cycle are one module, or a missing "
                        "third they both depend on is uncut"))
            elif colour.get(nxt) == WHITE:
                visit(nxt, stack + [nxt])
        colour[node] = BLACK

    for n in graph:
        if colour[n] == WHITE:
            visit(n, [n])
    return out


def seam_findings(modules, contracts):
    """The seams (procedure step 5): every dependency edge must cross a
    *named* contract, and every contract must be a real, fully-specified
    seam. Two refusals share this fold:

    - smuggled-seam     a contract naming a non-module, or omitting the
                        AI-native fields (trust/authority/change_rate) —
                        the seam exists but smuggles its protocol past
    - uncontracted-seam a dependency edge A->B with no contract listing
                        both — the agreement that crosses the seam is
                        unnamed, so it cannot stay minimal or stable
    """
    names = {m.get("name") for m in modules}
    out = []
    # contracts: real endpoints + full protocol discipline (the AI-native fork)
    pairs = set()
    for cid, c in (contracts or {}).items():
        c = c or {}
        between = c.get("between") or []
        unknown = [b for b in between if b not in names]
        missing = [f for f in CONTRACT_FIELDS if not str(c.get(f, "")).strip()]
        if len(between) != 2 or unknown or missing:
            problems = []
            if len(between) != 2:
                problems.append(f"between must name exactly two modules "
                                f"(got {between!r})")
            if unknown:
                problems.append(f"names non-module(s) {unknown}")
            if missing:
                problems.append(f"missing {', '.join(missing)}")
            out.append(_finding(
                "smuggled-seam", cid,
                "; ".join(problems) + " — a seam-contract must name two real "
                "modules and carry the protocol discipline trust/authority/"
                "change_rate (the AI-native fork, done-line 0104)"))
        if len(between) == 2 and not unknown:
            pairs.add(frozenset(between))
    # every dependency edge must be covered by some valid contract
    for m in modules:
        a = m.get("name")
        for b in (m.get("depends_on") or []):
            if b not in names:
                out.append(_finding(
                    "uncontracted-seam", f"{a} -> {b}",
                    f"depends on {b!r}, which is not a declared module"))
            elif frozenset((a, b)) not in pairs:
                out.append(_finding(
                    "uncontracted-seam", f"{a} -> {b}",
                    "this dependency crosses no named contract — the only "
                    "thing two modules share must be a minimal stable "
                    "interface, declared as the seam (procedure step 5)"))
    return out


def findings(manifest):
    """All findings for a declared manifest, in a fixed order (cheap
    structural checks before the graph walk). Empty means coherent."""
    modules = manifest.get("modules") or []
    contracts = manifest.get("contracts") or {}
    out = []
    out += incomplete_axis_findings(modules)
    out += smeared_axis_findings(modules)
    out += cycle_findings(modules)
    out += seam_findings(modules, contracts)
    return out


def verdict(manifest):
    """('coherent', []) when the decomposition survives the change test,
    else ('refused', findings)."""
    found = findings(manifest)
    return ("refused" if found else "coherent"), found


def render(name, status, found):
    print(f"decomposition: {name}")
    if status == "coherent":
        print("  the change test holds: every module owns one axis, the "
              "graph is a DAG, every seam is contracted")
        return
    for f in found:
        print(f"  refused: {f['kind']} — {f['subject']}")
        print(f"    why: {f['why']}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd")
    chk = sub.add_parser("check", help="judge a declared manifest")
    chk.add_argument("--manifest", type=pathlib.Path, default=DEFAULT_MANIFEST)
    args = ap.parse_args(argv)
    if args.cmd is None:
        args.cmd, args.manifest = "check", DEFAULT_MANIFEST

    try:
        manifest = json.loads(pathlib.Path(args.manifest).read_text("utf-8"))
    except FileNotFoundError:
        print(f"result: needs-you — no manifest at {args.manifest}; declare "
              "the decomposition before the gate can judge it")
        return 0
    except (json.JSONDecodeError, ValueError) as e:
        print(f"result: needs-you — manifest is not valid JSON: {e}")
        return 0

    status, found = verdict(manifest)
    render(manifest.get("decomposition", str(args.manifest)), status, found)
    if status == "coherent":
        print("result: done — coherent: the decomposition passes the change test")
    else:
        kinds = len({f["kind"] for f in found})
        print(f"result: report — refused: {len(found)} finding(s) across "
              f"{kinds} kind(s); each is the cut to fix, not an error to dodge")
    return 0


if __name__ == "__main__":
    sys.exit(main())
