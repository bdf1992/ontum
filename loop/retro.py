#!/usr/bin/env python3
"""The retrospective fold (done-line 0098): the loop reads its own history
for recurring patterns to refine on.

Every instrument the loop grew senses a *present* state — `gaps` (what is
open now), `census` (which organs are alive now), `digest` (one span of
the merge). Self-critique *across the whole history* stayed a hand-run
chat exercise, so patterns no single span or session reveals slipped
through: an atom re-derived again and again, a control valve advertised
but never opened, a divergence that recurs un-reconciled. This module is
that critique made an organ — a pure fold over the entire log that
surfaces recurring patterns, each carrying the one refinement move.

It is a sibling of `digest`, on a new axis: the digest folds *one span*;
retro folds *all of history* and asks what keeps happening. To stay on
the right side of §10 it does not build a second truth — it folds the
same append-only log every organ folds (`reconcile.Fold`) and *reuses*
the digest's version-split and divergence detection rather than
re-deriving them. Evidence is cited to log records, never to report prose
(the grip rule: a finding points at records, not sentences). It is
read-only: it names a pattern and the move; it never judges, admits,
dials, or edits — the fix stays a session's or bdo's (D-4).

Three detectors today (the first node; more ride later increments):

  churn               an atom re-derived ≥2× — multiple versions on the
                      record, and/or repeated negating verdicts before it
                      landed. The rework the shame beat cannot see: shame
                      senses *stalling*, this senses *churning*.
  dead-valve          a control path the loop advertises but never takes —
                      a tick mode that ran 0 times across a meaningful run
                      (today: cool, 0 of 91). Either the trigger never
                      fired and should say so, or it is dead behaviour.
  standing-divergence a digest divergence that has stood un-reconciled
                      across the history, carrying its age — the
                      cross-history form of the digest's within-span teeth.

CLI:
  python -m loop.retro            the retrospective, all history, read-only
  python -m loop.retro --json     the raw dataset (machine-readable)

Stdlib only. Ends with a clear result on stdout (D-6): done | report.
"""

import argparse
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from loop.reconcile import DEFAULT_ROOT, Fold, canon, now_ts
from loop import digest as digest_mod

# The verdicts that did NOT advance the work — a refusal/rework signal,
# read from the real verdict vocabulary on the log. (Not the absent-event
# heuristic the span digest uses for its count, which a merge/confirm
# receipt trips merely by carrying no next event; this is the honest
# "this got pushed back" set.)
NEGATING_VERDICTS = frozenset({
    "reject_no_value", "send_back", "amend", "collision", "missed",
})

MIN_TICKS = 5      # below this sample a never-taken valve is not yet a pattern
CHURN_MIN = 2      # ≥2 versions, or ≥2 negating verdicts, is re-derivation
STANDING_DAYS = 3  # a divergence older than this still on the books is standing
KIND_ORDER = ("churn", "dead-valve", "standing-divergence")


def _base(atom_id):
    """The version-blind atom base, via the digest's own split (no second
    copy of the .vN rule — done-line 0098's no-double-build)."""
    return digest_mod._base_version(atom_id)[0]


def _age_days(ts):
    """Whole days between an ISO-8601 record ts and now. None if unparseable
    — an absence is information, never a fabricated age."""
    try:
        then = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        now = datetime.fromisoformat(now_ts().replace("Z", "+00:00"))
        return (now - then).days
    except Exception:
        return None


def churn_findings(fold):
    """Atoms re-derived again and again. Two signals folded per atom base:
    distinct versions on the record (each .vN restarts the pipeline from
    scratch — identity is the content hash), and negating verdicts that
    pushed the work back. ≥2 of either is rework worth questioning before a
    next rewrite. Every finding's evidence cites real receipt ids — a
    fabricated classifier has nothing to point at (§10)."""
    versions = defaultdict(set)   # base -> {full atom ids seen}
    negs = defaultdict(list)      # base -> [negating receipt, ...]
    for rc in fold.receipts:
        aid = rc.get("artifact_id")
        if not aid:
            continue
        base = _base(aid)
        versions[base].add(aid)
        if rc.get("verdict") in NEGATING_VERDICTS:
            negs[base].append(rc)
    out = []
    for base in sorted(set(versions) | set(negs)):
        nver, nneg = len(versions.get(base, ())), len(negs.get(base, ()))
        if nver < CHURN_MIN and nneg < CHURN_MIN:
            continue
        evidence = []
        if nver >= CHURN_MIN:
            evidence.append(f"{nver} versions on the record: "
                            + ", ".join(sorted(versions[base])))
        for rc in negs[base][:4]:
            evidence.append(f"{rc.get('verdict')} by {rc.get('node')} "
                            f"({rc.get('id')}): "
                            f"{digest_mod._glance(rc.get('reason'))}")
        out.append({
            "kind": "churn",
            "subject": base,
            "trend": f"{nver} version(s), {nneg} negating verdict(s)",
            "evidence": evidence,
            "move": "read why it kept coming back before re-deriving again — "
                    "a fourth version is cheaper to question than to write; if "
                    "the spec is what is unstable, fix the spec, not the atom",
        })
    return out


def dead_valve_findings(fold):
    """A control mode the orchestrator can take but never has across a
    meaningful run. Today the modes are heat/cool; cool has run 0 of 91. A
    valve that never opens is either a trigger that never fires (say so, or
    lower it) or dead behaviour the loop claims but never shows. Evidence
    cites the tick span by id, so the finding resolves to real records."""
    ticks = [a for a in fold.admissions if a.get("type") == "tick"]
    if len(ticks) < MIN_TICKS:
        return []
    modes = Counter(t.get("mode") for t in ticks)
    taken = ", ".join(f"{m}×{n}" for m, n in sorted(modes.items()))
    out = []
    for mode in ("cool", "heat"):
        if modes.get(mode, 0) == 0:
            out.append({
                "kind": "dead-valve",
                "subject": f"orchestrate:{mode}",
                "trend": f"0 of {len(ticks)} ticks ran '{mode}' ({taken})",
                "evidence": [f"ticks {ticks[0].get('id')} … {ticks[-1].get('id')} "
                             f"({len(ticks)} records): {taken}"],
                "move": f"either the '{mode}' valve is real and the field never "
                        "met its condition — then make that explicit or lower "
                        "the trigger — or it is dead code claiming a behaviour "
                        "the loop never shows; exercise it or prune it",
            })
    return out


def standing_divergence_findings(fold, root):
    """Digest divergences (its within-span teeth) that have stood
    un-reconciled across the whole history, each with its age. Reuses
    `digest.digest` over no span — the divergence math is the digest's, the
    only thing new here is the time axis: a contradiction nobody resolved
    for days is a refinement signal a single span cannot show."""
    d = digest_mod.digest(root)  # no span = all history
    out = []
    for x in d.get("divergences", []):
        ts = _divergence_ts(fold, x)
        age = _age_days(ts) if ts else None
        if age is not None and age < STANDING_DAYS:
            continue  # fresh — let the span digest carry it, not a retro pattern
        subject = x.get("atom") or f"tick {x.get('tick')}"
        out.append({
            "kind": "standing-divergence",
            "subject": subject,
            "trend": (f"un-reconciled {age} day(s)" if age is not None
                      else "un-reconciled (age unknown)"),
            "evidence": [f"{x['kind']}: " + ", ".join(
                f"{k}={v}" for k, v in x.items() if k != "kind")],
            "move": "reconcile it (amend or retire the refused piece, re-dial "
                    "the breached cap) or surface it to bdo — a divergence that "
                    "stands for days is no longer just a span's note",
        })
    return out


def _divergence_ts(fold, x):
    """First-seen ts of a divergence, looked up on the record so the age is
    evidence-backed, not invented."""
    if x.get("kind") == "refusal-under-confirmed-arc":
        for rc in fold.receipts:
            if (rc.get("artifact_id") == x.get("atom")
                    and rc.get("node") == x.get("node")
                    and rc.get("verdict") == x.get("verdict")):
                return rc.get("ts")
    elif x.get("kind") == "queue-over-cap":
        for t in fold.admissions:
            if t.get("type") == "tick" and t.get("tick") == x.get("tick"):
                return t.get("ts")
    return None


def retro(root):
    """The fold: all of history, recurring patterns first. Returns the plain
    dataset render() turns into prose and --json emits verbatim."""
    fold = Fold(root)
    findings = (churn_findings(fold)
                + dead_valve_findings(fold)
                + standing_divergence_findings(fold, root))
    ticks = sum(1 for a in fold.admissions if a.get("type") == "tick")
    return {
        "findings": findings,
        "counts": dict(Counter(f["kind"] for f in findings)),
        "scanned": {"receipts": len(fold.receipts),
                    "events": len(fold.events),
                    "admissions": len(fold.admissions),
                    "ticks": ticks},
    }


def render(d):
    lines = ["# Retrospective — all history", "",
             "_a fold across the whole record for what keeps happening; "
             "read-only, the fix stays yours._", ""]
    s = d["scanned"]
    lines.append(f"Scanned {s['receipts']} receipts, {s['ticks']} ticks, "
                 f"{s['admissions']} admissions.")
    lines.append("")
    if not d["findings"]:
        lines.append("No recurring pattern stands out — the history is clean "
                     "on the detectors we have. (If it always is, the "
                     "detectors are not yet doing their job — §10.)")
        return "\n".join(lines)
    by_kind = defaultdict(list)
    for f in d["findings"]:
        by_kind[f["kind"]].append(f)
    titles = {
        "churn": "## Churn — work re-derived again and again",
        "dead-valve": "## Dead valves — behaviour advertised but never taken",
        "standing-divergence": "## Standing divergences — contradictions left to sit",
    }
    for kind in KIND_ORDER:
        items = by_kind.get(kind)
        if not items:
            continue
        lines.append(titles[kind])
        for f in items:
            lines.append(f"- `{f['subject']}` — {f['trend']}")
            for ev in f["evidence"]:
                lines.append(f"    · {ev}")
            lines.append(f"    → {f['move']}")
        lines.append("")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    ap.add_argument("--json", action="store_true",
                    help="emit the raw dataset (machine-readable), not the prose")
    args = ap.parse_args(argv)

    d = retro(args.root)
    if args.json:
        print(canon(d))
    else:
        print(render(d))
        print()
    n = len(d["findings"])
    if n:
        kinds = ", ".join(f"{k}×{v}" for k, v in sorted(d["counts"].items()))
        print(f"result: report — {n} recurring pattern(s) [{kinds}]; "
              f"each carries one refinement move (the fix is yours, D-4)")
    else:
        print("result: done — no recurring pattern on the current detectors")
    return 0


if __name__ == "__main__":
    sys.exit(main())
