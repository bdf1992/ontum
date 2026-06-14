#!/usr/bin/env python3
"""The outcome-pressure fold (done-line 0069): the gap to a desired reality,
measured against committed evidence so it survives session-end.

ontum represents *work* well and *outcomes* poorly (proposal:
`outcome-pressure-fold.proposal.md`). Every atom, receipt, done-line and
report is a unit of work that *completes*; nothing carries the tension of an
outcome that persists *while* work completes underneath it. So a session
behaves like a contractor — read context, finish a task, leave — and the
continuity lives in bdo's head, not in the environment.

This is the substrate's sensing half of the doctrine's slow loop (§14, the
two time-scales: the fast loop holds the setpoint each pass; the slow loop
moves it from accumulated outcomes). Before the dial can be re-admitted from
outcomes, the outcome's gap must be *measured*. That is this fold:

    Outcome Pressure = Fold(Current Reality, Desired Reality)

A fold, never a record (the loop's law): a record needs a session to maintain
it, and continuity-by-diligence is the contractor failure. Desired reality is
a set of falsifiable PROBES, each carrying its own check that resolves
**met / partial / unmet** against committed bytes or log records — the same
refusal `causality/term_economy.py` makes (no evidence, no mint) and
`loop/gaps.py` lives by (a finding names its own check). A probe whose check
this fold cannot resolve is **refused at load** — aspirational prose cannot
enter the desired-reality set, because a thing the fold can't check is not a
probe (outcomes/CLAUDE.md, the one hard rule).

Current reality = which probes resolve today. Pressure = the unmet and partial
probes, ranked by leverage. Decay is automatic: a probe flips unmet->met the
moment its evidence resolves; no session marks anything done, the fold
re-derives. *That is the inheritance* — the next session sees a smaller gap
without being told, and the unresolved probes stay visible as continuing
pressure rather than vanishing when the session that touched them ends.

The fold reports a **phase** (discover / build / realize), so a discovery move
reads as progress and a built capability is told apart from an adopted one:

  discover  no capability probes defined yet — the move is to define checkable
            probes (raising coverage); discovery is progress, not stalling.
  build     a capability probe is unmet or partial — buildable gap remains.
  realize   every capability probe is met; a use-trace (outcome) probe is not
            — built, awaiting proof of adoption.
  met       every probe resolves. Only here does the fold say "done"; it never
            declares victory on partial work.

Outcome probes (class `out`, resolved by a use-trace on the log) stay
**dormant** until their capability preconditions are met — dependencies
control nagging. A dormant probe is carried (still listed) but not counted as
pressure: you cannot build your way to an adoption probe.

Read-only (I-3), stdlib only (loop/ hard rule). CLI ends with a clear result
on stdout (D-6): done | report.

CLI:
  python -m loop.pressure                 the Causality outcome's pressure
  python -m loop.pressure --probes <path> over an alternate probe-set
  python -m loop.pressure --json          the dataset, machine-readable
"""

import argparse
import json
import re
import sys
from pathlib import Path

from loop.reconcile import DEFAULT_ROOT, Fold

# loop/pressure.py -> loop/ -> repo root. Works the same in a worktree.
REPO = Path(__file__).resolve().parent.parent

# The default desired-reality input: the checkable projection of the
# Causality outcome doc (the first outcome, done-line 0069 / PR #122).
DEFAULT_PROBES = REPO / "outcomes" / "causality-outcome-pressure.probes.json"

CLASSES = ("cap", "out")          # capability (build it) | outcome (use-trace)
CHECK_KINDS = ("path_exists", "file_contains", "log_record", "all_of", "any_of")
LEDGERS = ("events", "receipts", "admissions")


# --- check validity (the refusal: an uncheckable probe is not a probe) ------

def check_is_valid(check):
    """A check the fold can resolve deterministically. Recursive for the
    compound kinds. Anything else is refused at load — narrative cannot enter
    the desired-reality set (outcomes/CLAUDE.md, the one hard rule)."""
    if not isinstance(check, dict):
        return False
    kind = check.get("kind")
    if kind not in CHECK_KINDS:
        return False
    if kind == "path_exists":
        return isinstance(check.get("path"), str) and bool(check["path"])
    if kind == "file_contains":
        return (isinstance(check.get("path"), str) and bool(check["path"])
                and isinstance(check.get("pattern"), str) and bool(check["pattern"]))
    if kind == "log_record":
        return (check.get("ledger") in LEDGERS
                and isinstance(check.get("match"), dict) and bool(check["match"]))
    # all_of / any_of: a non-empty list of valid sub-checks
    subs = check.get("checks")
    return (isinstance(subs, list) and bool(subs)
            and all(check_is_valid(s) for s in subs))


# --- check resolution (current reality, against committed evidence) ---------

def resolve_check(check, repo, fold):
    """Resolve one check against committed bytes / log records. Returns
    (ok, evidence). Evidence is a file:line, a record id, or a join — never
    prose, the way term_economy/gaps/census cite (an auditable pointer)."""
    kind = check["kind"]
    if kind == "path_exists":
        p = repo / check["path"]
        return (p.exists(), check["path"] if p.exists() else None)
    if kind == "file_contains":
        p = repo / check["path"]
        if not p.is_file():
            return (False, None)
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return (False, None)
        rx = re.compile(check["pattern"])
        for i, line in enumerate(text.splitlines(), 1):
            if rx.search(line):
                return (True, f"{check['path']}:{i}")
        return (False, None)
    if kind == "log_record":
        records = getattr(fold, check["ledger"]) if fold else []
        for rec in records:
            if all(want in str(rec.get(k, "")) for k, want in check["match"].items()):
                return (True, rec.get("id", "<record>"))
        return (False, None)
    subs = check["checks"]
    results = [resolve_check(s, repo, fold) for s in subs]
    if kind == "all_of":
        ok = all(r[0] for r in results)
    else:  # any_of
        ok = any(r[0] for r in results)
    ev = "; ".join(r[1] for r in results if r[1]) or None
    return (ok, ev)


# --- loading (desired reality, with refusal at the door) --------------------

def load_probes(path):
    """Read a probe-set. Returns (probes, refused). A probe is refused — kept
    out of the resolved set, surfaced loudly — when it lacks a valid id/class
    or a checkable check. The committed sets are clean; refusal is the teeth a
    fixture exercises (done-line 0069)."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    probes, refused = [], []
    for raw in data.get("probes", []):
        pid = raw.get("id")
        if not isinstance(pid, str) or not pid:
            refused.append({"probe": raw.get("id", "<no-id>"),
                            "reason": "no id"})
            continue
        if raw.get("class") not in CLASSES:
            refused.append({"probe": pid,
                            "reason": f"class must be one of {CLASSES}"})
            continue
        if not check_is_valid(raw.get("check")):
            refused.append({"probe": pid,
                            "reason": "uncheckable: missing or unresolvable "
                                      "check (a thing the fold can't check is "
                                      "not a probe)"})
            continue
        if "partial" in raw and not check_is_valid(raw["partial"]):
            refused.append({"probe": pid,
                            "reason": "uncheckable partial check"})
            continue
        probes.append(raw)
    return probes, refused, data.get("outcome", str(path))


# --- the fold (current vs desired -> phase, leverage, next move) ------------

def _transitive_deps(pid, by_id, seen=None):
    seen = seen if seen is not None else set()
    for dep in by_id.get(pid, {}).get("depends", []):
        if dep not in seen:
            seen.add(dep)
            _transitive_deps(dep, by_id, seen)
    return seen


def compute(probes, repo, fold):
    """The fold: resolve every probe, settle dormancy, derive phase, leverage
    and the next safe move. Pure over its inputs."""
    by_id = {p["id"]: p for p in probes}

    # 1. raw state from each probe's own check (met | partial | unmet)
    raw, evidence = {}, {}
    for p in probes:
        ok, ev = resolve_check(p["check"], repo, fold)
        if ok:
            raw[p["id"]], evidence[p["id"]] = "met", ev
        elif "partial" in p and resolve_check(p["partial"], repo, fold)[0]:
            raw[p["id"]], evidence[p["id"]] = "partial", \
                resolve_check(p["partial"], repo, fold)[1]
        else:
            raw[p["id"]], evidence[p["id"]] = "unmet", None
    met_ids = {pid for pid, s in raw.items() if s == "met"}

    # 2. dormancy: an outcome probe is dormant until every dep is met. A cap
    #    probe is never dormant (you can always build toward it). A missing or
    #    refused dependency reads as not-met (absence is information).
    state = {}
    for p in probes:
        pid = p["id"]
        if p["class"] == "out" and not all(d in met_ids for d in p.get("depends", [])):
            state[pid] = "dormant"
        else:
            state[pid] = raw[pid]

    met = [p["id"] for p in probes if state[p["id"]] == "met"]
    partial = [p["id"] for p in probes if state[p["id"]] == "partial"]
    unmet = [p["id"] for p in probes if state[p["id"]] == "unmet"]
    dormant = [p["id"] for p in probes if state[p["id"]] == "dormant"]

    cap = [p for p in probes if p["class"] == "cap"]
    out = [p for p in probes if p["class"] == "out"]
    cap_notmet = [p for p in cap if state[p["id"]] in ("unmet", "partial")]
    out_active_notmet = [p for p in out if state[p["id"]] in ("unmet", "partial")]

    # 3. phase — discovery is progress, build is possible-not-real, realize is
    #    built-not-adopted; "met" (and only "met") is done.
    if not cap:
        phase = "discover"
    elif cap_notmet:
        phase = "build"
    elif out_active_notmet:
        phase = "realize"
    else:
        phase = "met"

    # 4. leverage: among not-met cap probes, the one the most other not-met cap
    #    probes (transitively) depend on — closing it unblocks the most build.
    #    Dormant outcome probes never count: you cannot build toward adoption.
    notmet_cap_ids = {p["id"] for p in cap_notmet}
    leverage = {}
    for cand in cap_notmet:
        dependents = sum(1 for other in cap_notmet
                         if other["id"] != cand["id"]
                         and cand["id"] in _transitive_deps(other["id"], by_id))
        leverage[cand["id"]] = dependents

    top = None
    if cap_notmet:
        top_id = max(
            cap_notmet,
            key=lambda p: (leverage[p["id"]],
                           -sum(1 for d in p.get("depends", []) if d not in met_ids),
                           # stable, deterministic final tiebreak
                           -ord(p["id"][0]) if p["id"] else 0),
        )["id"]
        tp = by_id[top_id]
        top = {"id": top_id, "statement": tp.get("statement", top_id),
               "unblocks": leverage[top_id], "move": tp.get("move", "")}

    if top:
        next_move = top["move"] or f"close {top['id']}"
    elif out_active_notmet:
        nm = out_active_notmet[0]
        next_move = nm.get("move", "") or (
            f"adopt {nm['id']}: it resolves on a use-trace, not a build")
    elif phase == "discover":
        next_move = ("define checkable capability probes for this outcome — "
                     "discovery raises coverage and is progress, not stalling")
    else:
        next_move = "outcome met — every probe resolves"

    return {
        "outcome": None,  # filled by caller
        "phase": phase,
        "measures": {
            "capability": f"{len(met_ids & {p['id'] for p in cap})}/{len(cap)}",
            "realization": f"{sum(1 for p in out if state[p['id']] == 'met')}/"
                           f"{len([p for p in out if state[p['id']] != 'dormant'])}",
        },
        "met": met, "partial": partial, "unmet": unmet, "dormant": dormant,
        "state": state, "evidence": evidence, "by_id": by_id,
        "top_leverage": top, "next_move": next_move,
        "resolved_count": len(probes),
    }


def pressure(probes_path=DEFAULT_PROBES, repo=REPO, root=None):
    """The full read: load (with refusal), fold, return the result + refused."""
    probes, refused, outcome = load_probes(probes_path)
    root = root if root is not None else (repo / DEFAULT_ROOT)
    fold = Fold(Path(root)) if (Path(root) / "log").is_dir() else None
    result = compute(probes, repo, fold)
    result["outcome"] = outcome
    result["refused"] = refused
    return result


# --- render -----------------------------------------------------------------

PHASE_GLOSS = {
    "discover": "no capability probes defined yet — define them (discovery is progress)",
    "build": "a capability is unmet or partial — buildable gap remains",
    "realize": "every capability is met; a use-trace probe is not — awaiting adoption",
    "met": "every probe resolves",
}


def render(result):
    by_id = result["by_id"]
    state = result["state"]
    print(f"outcome-pressure — {result['outcome']}")
    print(f"  phase: {result['phase']} — {PHASE_GLOSS[result['phase']]}")
    print(f"  capability {result['measures']['capability']} met · "
          f"realization {result['measures']['realization']} met")

    if result["refused"]:
        print(f"  refused ({len(result['refused'])}) — not admitted to "
              f"desired reality:")
        for r in result["refused"]:
            print(f"    {r['probe']}: {r['reason']}")

    if result["top_leverage"]:
        t = result["top_leverage"]
        print(f"  top leverage: {t['id']} — {t['statement']} "
              f"(unblocks {t['unblocks']} more)")
    print(f"  next move: {result['next_move']}")

    # Every unresolved probe stays visible — the whole point. Never dropped,
    # never collapsed into a count; carried across session-end as pressure.
    unresolved = result["partial"] + result["unmet"] + result["dormant"]
    if unresolved:
        print(f"  unresolved ({len(unresolved)}) — continuing outcome-pressure:")
        for pid in [p["id"] for p in by_id.values() if p["id"] in unresolved]:
            mark = state[pid]
            note = " (dormant: a precondition is unmet)" if mark == "dormant" else ""
            print(f"    [{mark}] {pid} — {by_id[pid].get('statement', pid)}{note}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--probes", type=Path, default=DEFAULT_PROBES,
                    help="the desired-reality probe-set (default: Causality)")
    ap.add_argument("--root", type=Path, default=None,
                    help="records root for log_record checks (default: repo .ai-native)")
    ap.add_argument("--json", action="store_true", help="emit the dataset")
    args = ap.parse_args(argv)

    result = pressure(args.probes, root=args.root)
    if args.json:
        emit = {k: v for k, v in result.items() if k != "by_id"}
        print(json.dumps(emit, indent=2, sort_keys=True))
        return 0

    render(result)
    if result["refused"]:
        print(f"result: report — {len(result['refused'])} probe(s) refused as "
              f"uncheckable; fix the probe-set")
    elif result["phase"] == "met":
        print("result: done — outcome met; every probe resolves")
    else:
        unresolved = len(result["partial"]) + len(result["unmet"]) + len(result["dormant"])
        print(f"result: report — outcome NOT met: phase {result['phase']}, "
              f"{unresolved} probe(s) unresolved (carried as continuing "
              f"pressure). The top-leverage move is the work.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
