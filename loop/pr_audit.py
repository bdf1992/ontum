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
RECORD_DIRS = (".ai-native/reports/", ".ai-native/done/")
RECEIPTS_LOG = ".ai-native/log/receipts.jsonl"


def records_only(changed_paths):
    """True iff the branch changes ONLY records — session reports or done-lines
    (`.ai-native/reports|done/NNNN-*.md`) and nothing else (done-line 0172,
    bdo's records door). A record is *of* work, not work: a report written after
    its work PR already landed has no atom to carry and can never bundle
    retroactively, yet it belongs on main as the durable record. Such a PR is
    backed without an atom, the same shape as the phrasing door — and just as
    narrow: a single code, atom, log, or config change makes this False and the
    branch falls back to needing an atom (a report PR cannot smuggle work). An
    empty change set is not records-only (nothing to land)."""
    paths = [p.replace("\\", "/") for p in changed_paths if p.strip()]
    if not paths:
        return False
    return all(p.startswith(RECORD_DIRS) and p.endswith(".md") for p in paths)


def receipts_only(changed_paths):
    """True iff the branch changes ONLY the append-only receipts log
    (`.ai-native/log/receipts.jsonl`) and nothing else (done-line 0187, bdo's
    RAW door). A receipt is the substrate's one FREE layer (RAW vs RAI): a RAW
    append is a deterministic FACT that re-derives from its own bytes — a receipt
    id recomputes from its fields (`receipt_rederives`) — where an authored atom
    or report (RAI) cannot. The records and phrasing doors admit authored `.md`;
    this door admits the *provable* receipt the old extension-blind gate refused
    as an off-log orphan (the #617 stranded value-gate acceptance: an atom's code
    landed, its acceptance receipt stranded off-trunk because the append carried
    no `.md`). Narrow on purpose: a single other path — an atom, code, a sibling
    log — makes this False and the branch falls back to needing an atom, so no
    work can ride a receipt append. An empty change set is not receipts-only
    (nothing to land)."""
    paths = [p.replace("\\", "/") for p in changed_paths if p.strip()]
    if not paths:
        return False
    return all(p == RECEIPTS_LOG for p in paths)


def receipt_rederives(rc):
    """True iff a receipt's stored `id` RE-DERIVES from its own content by the
    one derivation that minted it: `loop.reconcile.short_hash` over
    `node|artifact_id|artifact_hash|event_id`, the exact key `make_receipt`
    hashes (reused, never re-invented here — I-4). This is what makes a receipt
    RAW: its id is a pure function of fields the line itself carries, so a
    faithful append PROVES itself and a fabricated or tampered line cannot — a
    changed field flips the hash. A line missing any keyed field, or carrying an
    id minted by a different scheme (e.g. a `rcp.merge.NNN` land receipt, which
    no PR appends), does not re-derive — refused, not admitted."""
    from loop.reconcile import short_hash
    stored = rc.get("id")
    keys = ("node", "artifact_id", "artifact_hash", "event_id")
    if not (isinstance(stored, str) and stored):
        return False
    if any(not (isinstance(rc.get(k), str) and rc.get(k)) for k in keys):
        return False
    return stored == "rcp." + short_hash(*(rc[k] for k in keys))


def receipts_door_reason(added_receipts):
    """Why a receipts-only append PR is off-log, or None when it is backed — the
    FOURTH backed shape (the RAW door, done-line 0187). Given the receipt lines
    the branch APPENDS to the log (the reach parses them from the diff), the
    branch is backed when there is at least one and EVERY one re-derives
    (`receipt_rederives`). A line that does not re-derive is RAI/smuggling — a
    fabricated or tampered receipt — and refuses the whole PR, named (one bad
    line poisons the batch: §10). An empty append set has nothing to back (a
    receipts-only diff that adds no parseable receipt — e.g. an edit/removal of
    existing history — is refused, not waved through)."""
    receipts = list(added_receipts or [])
    if not receipts:
        return ("changes only the receipts log but appends no parseable, "
                "re-deriving receipt line — the RAW door lands appended facts "
                "that prove themselves; there is nothing here to re-derive")
    bad = [rc.get("id") or "(no id)" for rc in receipts if not receipt_rederives(rc)]
    if bad:
        return (f"appends receipt line(s) {', '.join(bad)} whose stored id does "
                "NOT re-derive from its own content — a RAW receipt proves itself "
                "by recomputation; a line that fails it is authored/inferred "
                "(RAI), not a fact, and may not ride the receipts door")
    return None


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


def orphan_reason(added_atom_ids, receipt_artifact_ids, phrasing_clean=False,
                  records_only=False, receipts_only=False, added_receipts=None):
    """Why a PR's branch is off-log, or None when it is backed. Pure: given the
    atom ids the branch adds under `.ai-native/atoms/` and the `artifact_id`s
    the branch's added receipt lines name, a branch is atom-backed when at least
    one atom it adds also carries a receipt it adds — the invariant
    `atom_backed_refusal` enforces at open time, read from the branch side so a
    PR opened by any path (pen or not) is held to it.

    The SECOND way to be backed (done-line 0117, bdo's phrasing backdoor): a
    branch whose every non-log change `loop.phrasing` proves PHRASING-ONLY needs
    no atom — a pedantic prose edit the machine never branches on is not a
    work-particle. `phrasing_clean` is that proof, gathered AND re-verified by
    the reach (`pr.py audit`) with the same pure checker, so the prose door
    cannot be lied to: a code or schema change makes it False and the branch
    falls back to needing an atom.

    The THIRD way to be backed (done-line 0172, bdo's records door): a branch
    that changes ONLY records — reports/done-lines (`records_only`) — needs no
    atom, because a record is *of* work, not a work-particle. A session report
    written after its work landed cannot bundle retroactively and would otherwise
    strand off main forever. Like the phrasing proof, `records_only` is recomputed
    by the reach (`pr.py audit`) from the diff, so it cannot be lied to: any
    non-record change falls back to needing an atom.

    The FOURTH way to be backed (done-line 0187, bdo's RAW door): a branch whose
    ONLY change is appended lines to the receipts log (`receipts_only`) is backed
    without an atom WHEN every appended receipt re-derives to its stored id
    (`receipts_door_reason` over `added_receipts`). A RAW append is a
    deterministic fact that proves itself by recomputation — the doctrine's only
    free layer — where the old extension-blind gate refused it as an off-log
    orphan (the #617 stranded value-gate acceptance, RAW yet blocked while
    authored `.md` was waved through). Like the other doors, the file-scope and
    the re-derivation are recomputed by the reach from the diff, so the door
    cannot be lied to: any non-receipt change makes `receipts_only` False, and any
    line that does not re-derive refuses the whole PR.

    Otherwise, two ways to be an orphan, in the order the pen states them: no
    atom at all (the #107 case), or an atom that never entered the pipeline (a
    file with no receipt naming it)."""
    if phrasing_clean:
        return None  # backed through the phrasing door (low-impact, proven)
    if records_only:
        return None  # backed through the records door (a record is of work)
    if receipts_only:
        # the RAW door: backed iff every appended receipt re-derives; a line
        # that does not is named as smuggling, never silently let through
        return receipts_door_reason(added_receipts)
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
        phrasing_clean = bool(f.get("phrasing_clean", False))
        records = bool(f.get("records_only", False))
        receipts = bool(f.get("receipts_only", False))
        added_receipts = f.get("added_receipts", [])
        reason = orphan_reason(f.get("added_atom_ids", []),
                               f.get("receipt_artifact_ids", []),
                               phrasing_clean, records, receipts, added_receipts)
        row = {k: f[k] for k in ("number", "headRefName", "author") if k in f}
        if reason:
            orphans.append({**row, "reason": reason})
        else:
            if phrasing_clean:
                row["backed_by"] = ["phrasing-door"]  # proven prose-only, no atom
            elif records:
                row["backed_by"] = ["records-door"]  # reports/done-lines, no atom
            elif receipts:
                row["backed_by"] = ["receipts-door"]  # RAW re-deriving appends
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
