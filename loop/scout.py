#!/usr/bin/env python3
"""The Scout generator (done-line 0148): joins the explore-fold's derivation
to the ScoutCTA contract, with teeth that bite a *real* move.

This is the piece that makes the Scout lobe real. `loop/explore.py` derives
the forward move (the frontier between what an arc claims and what the record
shows); `loop/scout_cta.py` is the lawful conjecture contract (schema +
grounding + the expiry refusal). This module composes them: given a handed
purpose+goal, it derives the move and emits ONE **ScoutCTA** — validated
through `scout_cta.validate` before it is ever emitted.

It **closes review finding #1** on PR #321. explore.py's grounding was
vacuous on the real path: its arc-doc antecedent (the epic file contains its
own id) *always* resolves, so the ghost refusal could never bite a real move
— only directly-constructed test fakes. Scout grounds on **substantive,
non-self-referential** priors instead: real log records / done-lines that
name the subject or the epic, resolved against committed bytes, explicitly
**excluding** the epic-file self-reference. A move whose substantive priors
do not resolve is **REFUSED as ungrounded** — the teeth bite a real move, not
just a fabricated dict. A brand-new epic with no log activity grounds nothing
and is refused, where explore.py would have "grounded" it on its own name.

Read-only and propose-only (D-4): Scout derives, grounds, and emits a marked
conjecture; it never judges, stamps, mints, writes the log, or lands. Taking
the move stays a session's or bdo's.

CLI:
  python -m loop.scout epic.<id>          one grounded ScoutCTA toward an arc
  python -m loop.scout <purpose> --json   the raw dataset (machine-readable)

Stdlib only, no network, no git. Ends with a clear result (D-6).
"""

import argparse
import json
import sys
from pathlib import Path

from loop.reconcile import DEFAULT_ROOT
from loop.explore import resolve_purpose, derive_move
from loop import scout_cta
from causality.term_economy import resolve_evidence


def substantive_priors(repo_root, eid, subject):
    """Real, NON-self-referential priors for a move: log records / done-lines
    that name the subject or the epic id, resolved on disk. The arc-doc
    self-reference (the epic file containing its own id/piece) is EXCLUDED —
    it always resolves and made explore.py's teeth vacuous (finding #1). A
    move with no substantive prior here is ungrounded: the arc *naming* a
    piece is not evidence the move is warranted; real activity on the record
    is. Deduped; each entry is a {file, contains} the caller can re-resolve."""
    repo_root = Path(repo_root)
    cands = []
    for ledger in ("admissions", "events", "receipts"):
        for needle in (subject, eid):
            if needle:
                cands.append({"file": f".ai-native/log/{ledger}.jsonl",
                              "contains": needle, "source": f"log:{ledger}"})
    ddir = repo_root / ".ai-native" / "done"
    for p in sorted(ddir.glob("*.md")):
        try:
            if subject and subject in p.read_text(encoding="utf-8", errors="replace"):
                cands.append({"file": f".ai-native/done/{p.name}",
                              "contains": subject, "source": "done-line"})
        except OSError:
            continue
    seen, out = set(), []
    for ev in cands:
        key = (ev["file"], ev["contains"])
        if key in seen:
            continue
        seen.add(key)
        if resolve_evidence(repo_root, ev).get("resolved"):
            out.append(ev)
    return out


def build_scout_cta(epic, kind, subject, move, priors):
    """Assemble the §6 ScoutCTA from the derived move and its grounded priors.
    Carries the conjecture marks in its own bytes — it is never truth."""
    eid = epic["id"]
    return {
        "status": "conjecture",
        "lobe": "scout",
        "purpose": eid,
        "goal": epic.get("value") or f"advance {eid} toward its horizon",
        "horizon": epic.get("horizon") or "the arc's stated horizon",
        "priors_consulted": [{"file": p["file"], "contains": p["contains"]}
                             for p in priors],
        "uncertainty_held": ("whether this is the highest-leverage move, and the "
                             "arc's open forks — not collapsed; Scout proposes, it "
                             "does not decide (D-4)"),
        "why_this_move_now": f"[{kind}] {move}",
        "cta": move,
        "cost": "one review pass + one small branch + one §10 test",
        "attention_class": "small",
        "risk": "low — a marked conjecture; reversible, expiring, never landed by Scout",
        "reversibility": "high — superseded or pruned with no ledger effect (it never minted)",
        "review_required": True,
        "expiry": "next 3 sessions — re-evaluate; if the arc's priorities shift it decays",
        "truth_claim": False,
        "minted": False,
    }


def scout(root, purpose):
    """The generator: point at a handed purpose, derive the move, ground it on
    substantive priors, validate through the contract, and emit ONE ScoutCTA —
    or refuse. Writes nothing."""
    root = Path(root)
    repo_root = root.resolve().parent
    res = resolve_purpose(root, purpose)
    if res is None:
        return {"status": "refused", "subject": purpose,
                "reason": "no epic or outcome resolves — Scout is pointed, never free"}
    if res[0] != "epic":
        return {"status": "refused", "subject": purpose,
                "reason": "Scout v2 grounds handed EPIC purposes; outcome purposes are a later slice"}
    epic = res[1]
    eid = epic["id"]
    kind, subject, move = derive_move(root, epic)
    priors = substantive_priors(repo_root, eid, subject)
    if not priors:
        return {"status": "refused", "subject": subject, "toward": eid,
                "reason": ("no substantive, non-self-referential prior resolves for this "
                           "move — ungrounded (the arc naming the piece is not enough; "
                           "the teeth bite)")}
    cta = build_scout_cta(epic, kind, subject, move, priors)
    problems = scout_cta.validate(repo_root, cta)
    if problems:
        return {"status": "refused", "subject": subject, "toward": eid,
                "reason": "the ScoutCTA failed its own contract: " + "; ".join(problems)}
    return cta


def render(out):
    if out.get("status") == "refused":
        return ("# Scout — REFUSED (no ungrounded conjecture emitted)\n"
                f"  subject: {out.get('subject')}\n  why: {out.get('reason')}")
    return scout_cta.render(scout_cta.REPO_ROOT, out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("purpose", help="an epic id (epic.<x>) — the goal to point Scout at")
    ap.add_argument("--root", type=Path, default=Path(DEFAULT_ROOT))
    ap.add_argument("--json", action="store_true",
                    help="emit the raw dataset (machine-readable), not the prose")
    args = ap.parse_args(argv)

    out = scout(args.root, args.purpose)
    if args.json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        print(render(out))
        print()
    if out.get("status") == "refused":
        print(f"result: report — Scout refused ({out.get('reason', '')[:70]}…); "
              "no ungrounded conjecture left the lobe")
    else:
        print(f"result: done — one grounded ScoutCTA toward {out['purpose']}, marked "
              "conjecture (review-required, expiring, never landed by Scout — D-4)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
