"""The off-log-PR audit (done-line 0066): the pure half of the gate that
makes it impossible for work to reach main outside the machinery.

bdo named the hole: it should be impossible to create work in GitHub
without going through the loop, and it is not. The atom invariant — every
work-particle is an atom on the log (§15/D-5) — lives only in two
client-side places: the PR pen refuses to *open* a non-atom PR
(`atom_backed_refusal`) and the lander refuses to *land* one. Both bind
only a hooked session's tool calls; the GitHub web UI, bdo's phone, Codex
and the API are all unbound. PR #107 is the proof — authored straight on
GitHub, zero atoms, zero receipts, invisible to every fold the loop runs.

This module is the *detection* half (the server-side required check is its
hard backstop, a separate node). It is the same split reflect uses: the
**check is pure and lives here** (no `gh`, no `git`, no network — loop/'s
hard rule), the **reach lives in the PR pen** (`pr.py audit`), which hands
this fold the branch facts it gathered. The check mirrors the pen's own
`atom_backed_refusal` from the branch side, so the audit and the open-time
gate cannot drift: a branch is atom-backed when it adds at least one atom
under `.ai-native/atoms/` that a receipt it also adds names by
`artifact_id`. Anything else is an off-log orphan — surfaced, never edited,
its disposition (re-home through the pen, or close) bdo's call (D-4).
"""
from __future__ import annotations

ATOM_DIR = ".ai-native/atoms/"


def atom_id_of(path):
    """The atom id a changed path carries, or None. The pipeline identity is
    the file stem under `.ai-native/atoms/` (the receipt's `artifact_id`);
    `atom.inbound-envoy-seam.v0.json` -> `atom.inbound-envoy-seam.v0`. A path
    outside the atoms tree carries no atom id."""
    p = path.replace("\\", "/")
    if ATOM_DIR not in p:
        return None
    name = p.rsplit("/", 1)[-1]
    return name[:-5] if name.endswith(".json") else name


def orphan_reason(added_atom_ids, receipt_artifact_ids):
    """Why a PR's branch is off-log, or None when it is atom-backed. Pure:
    given the atom ids the branch adds under `.ai-native/atoms/` and the
    `artifact_id`s the branch's added receipt lines name, a branch is backed
    when at least one atom it adds also carries a receipt it adds — the
    invariant `atom_backed_refusal` enforces at open time, read from the
    branch side so a PR opened by any path (pen or not) is held to it.

    Two ways to be an orphan, in the order the pen states them: no atom at
    all (the #107 case), or an atom that never entered the pipeline (a file
    with no receipt naming it)."""
    added = set(added_atom_ids)
    named = set(receipt_artifact_ids)
    if not added:
        return ("adds no atom under .ai-native/atoms/ — work that is not an "
                "atom on the log is invisible to the ambient loop (§15/D-5)")
    backed = added & named
    if not backed:
        return (f"adds atom(s) {', '.join(sorted(added))} but no receipt on "
                "the branch names them — the atom never entered the pipeline "
                "(no atom + backing receipt = off the log)")
    return None


def audit(pr_facts):
    """The fold: classify each open PR from the branch facts the pen gathered.

    `pr_facts` is a list of dicts, each carrying at least `number`,
    `headRefName`, `added_atom_ids`, `receipt_artifact_ids` (and any passthrough
    the pen attaches, e.g. `author`). Returns `{"orphans": [...], "clean": [...]}`
    — an orphan carries its `reason`; both keep the PR's identifying fields.
    Pure and order-stable: the field is the pen's to gather, the verdict the
    fold's to compute, the disposition bdo's to make."""
    orphans, clean = [], []
    for f in pr_facts:
        reason = orphan_reason(f.get("added_atom_ids", []),
                               f.get("receipt_artifact_ids", []))
        row = {k: f[k] for k in ("number", "headRefName", "author") if k in f}
        if reason:
            orphans.append({**row, "reason": reason})
        else:
            row["backed_by"] = sorted(set(f.get("added_atom_ids", []))
                                      & set(f.get("receipt_artifact_ids", [])))
            clean.append(row)
    return {"orphans": orphans, "clean": clean}


def render(result):
    """A cold reader's view: every off-log PR named with why, then a count of
    the clean ones. Read-only; names orphans, never touches them (D-4)."""
    orphans, clean = result["orphans"], result["clean"]
    if not orphans:
        print(f"clean — all {len(clean)} open PR(s) are atom-backed; "
              "no work reached GitHub outside the machinery")
        return
    print(f"OFF-LOG — {len(orphans)} open PR(s) bypassed the loop "
          f"({len(clean)} clean):\n")
    for o in orphans:
        who = f" by {o['author']}" if o.get("author") else ""
        print(f"  PR #{o.get('number')} ({o.get('headRefName')}){who}")
        print(f"    {o['reason']}")
    print("\nthe move: re-home each orphan's change through the PR pen as a "
          "proper atom, or close it — a judgment call surfaced to bdo, "
          "never an edit (D-4)")


def main(argv=None):
    """Read PR facts as JSON (a file path, or '-'/none for stdin) and emit the
    audit — the human render by default, or the raw verdict dataset under
    `--json` (the *consumer port*: a generic reader gets the structured result,
    symmetric to the `--range` enforcer port the providers gate on). The facts
    are gathered by the reach that has the network — `pr.py audit` — never here:
    loop/ stays pure stdlib, no `gh`, no `git`."""
    import argparse
    import json
    import sys
    ap = argparse.ArgumentParser(prog="loop.pr_audit", description=__doc__)
    ap.add_argument("facts", nargs="?", default="-",
                    help="JSON facts file, or '-' for stdin")
    ap.add_argument("--json", dest="as_json", action="store_true",
                    help="emit the verdict dataset for a consumer, not the "
                         "human render (the reader's port)")
    ns = ap.parse_args(sys.argv[1:] if argv is None else argv)
    raw = (open(ns.facts, encoding="utf-8").read()
           if ns.facts not in ("-", "") else sys.stdin.read())
    facts = json.loads(raw) if raw.strip() else []
    result = audit(facts)
    n = len(result["orphans"])
    if ns.as_json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        render(result)
        print(f"\nresult: {'needs-you' if n else 'report'} — "
              f"{n} off-log PR(s), {len(result['clean'])} atom-backed")
    return 1 if n else 0  # non-zero on an orphan: any caller (CI) can gate on it


if __name__ == "__main__":
    raise SystemExit(main())
