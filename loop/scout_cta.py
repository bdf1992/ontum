#!/usr/bin/env python3
"""The ScoutCTA contract, before code (done-line 0141): the schema, a
hand-authored fixture, and the validator with teeth — the lawful shape of
*pre-evidence motion*, proven by example before any generating loop.

A ScoutCTA is the Scout lobe's one output: a marked, expiring, reversible
**call to action** drawn from priors toward a handed purpose+goal (see
strategy-metabolism.md §6). It is conjecture, never truth — so it carries
its marks in its own bytes (`status: conjecture`, `review_required: true`,
`truth_claim: false`, `minted: false`) and it can never land, mint, or
alter truth state (D-4). Scout develops and requisitions review; it never
self-lands.

This module is the contract made executable. It holds:
  - SCHEMA / MARKS  the §6 required fields and the mandatory marks
  - FIXTURE         one hand-authored ScoutCTA (committed, reviewable)
  - validate()      the teeth: schema + grounding + the expiry refusal

The teeth (§10), reusing causality's resolver with no second truth:
  1. ungrounded     a prior in `priors_consulted` that does not resolve on
                    disk is the ghost refusal — no prior, no conjecture.
                    `causality.term_economy.resolve_evidence` is the one
                    resolver (the same the term economy uses), never a copy.
  2. no expiry      an empty/absent `expiry` is refused — a conjecture
                    without decay is a ghost obligation (it never closes).
  3. fabricated     a constant/fabricated CTA cannot pass, because its
                    citations resolve to nothing (teeth #1).

The generating `loop/scout.py` (research over priors -> one CTA) and the
Claim and Prune parts are NAMED in strategy-metabolism.md but built by
later lines — this is the contract, not the loop.

Stdlib only, no network, no git. CLI ends with a clear result (D-6).
"""

import argparse
import json
import sys
from pathlib import Path

from causality.term_economy import resolve_evidence

REPO_ROOT = Path(__file__).resolve().parents[1]

# the §6 ScoutCTA schema: every field is required (absence is a refusal).
REQUIRED = (
    "status", "lobe", "purpose", "goal", "horizon", "priors_consulted",
    "uncertainty_held", "why_this_move_now", "cta", "cost", "risk",
    "reversibility", "review_required", "expiry", "truth_claim", "minted",
)

# the mandatory marks — the conjecture floor. A ScoutCTA that does not carry
# these in its own bytes is not a lawful Scout output, it is a truth claim.
MARKS = {
    "status": "conjecture",
    "lobe": "scout",
    "review_required": True,
    "truth_claim": False,
    "minted": False,
}

# One hand-authored fixture: a real frontier move, grounded, useful, clearly
# conjectural — it must NOT read as truth. Pointed at our own situation: the
# contract is frozen (0141) but Scout has no Claim part yet, so building the
# generator first risks the overgrowth strategy-metabolism.md §2 warns of.
FIXTURE = {
    "status": "conjecture",
    "lobe": "scout",
    "purpose": "epic.strategy — land lawful pre-evidence motion, smallest-first",
    "goal": "a working Scout -> Claim -> Build -> Prune cycle",
    "horizon": "Scout emits one marked CTA, Claim bounds it, Build routes it, Prune retires it",
    "priors_consulted": [
        {"file": "strategy-metabolism.md", "contains": "unmanaged possibility that consumes field-space"},
        {"file": "strategy-metabolism.md", "contains": "Claim is the missing bridge"},
        {"file": ".ai-native/done/0141-scout-cta-contract.md", "contains": "ScoutCTA contract"},
    ],
    "uncertainty_held": "whether Scout should ever self-aim (decision D) and the manifold's true axes — not collapsed here",
    "why_this_move_now": "the contract (0141) is frozen, but a Scout CTA has no lawful path to bounded work until Claim exists; building the generator first risks unmanaged conjecture (§2)",
    "cta": "Before loop/scout.py, author the Claim part's schema (strategy-metabolism.md §7) so a Scout CTA can become bounded work.",
    "cost": "one review pass + one small branch + one §10 test",
    "attention_class": "small",
    "risk": "low — a proposed schema; the real risk is sequencing (Scout's generator before Claim invites overgrowth)",
    "reversibility": "high — a proposed schema, superseded or pruned with no ledger effect",
    "review_required": True,
    "expiry": "next 3 sessions — if Build/Claim priorities shift, this conjecture decays",
    "truth_claim": False,
    "minted": False,
}


def validate(repo_root, cta):
    """The teeth. Returns a list of problems — empty means the ScoutCTA is
    schema-valid AND grounded AND carries a real expiry. A non-empty list is
    a refusal, each entry naming what disqualified it."""
    problems = []

    for k in REQUIRED:
        if k not in cta:
            problems.append(f"missing required field: {k}")
    for k, v in MARKS.items():
        if cta.get(k) != v:
            problems.append(f"mark {k} must be {v!r}, got {cta.get(k)!r} "
                            "(a ScoutCTA carries its conjecture marks in its bytes)")

    if not str(cta.get("cta") or "").strip():
        problems.append("cta is empty — Scout emits exactly one move")

    # the expiry refusal: a conjecture without decay is a ghost obligation
    if not str(cta.get("expiry") or "").strip():
        problems.append("expiry is empty/absent — a conjecture without decay "
                        "is a ghost obligation (it never closes)")

    # the ghost refusal: every prior must resolve on disk (one resolver,
    # reused from causality — no second truth)
    priors = cta.get("priors_consulted")
    if not isinstance(priors, list) or not priors:
        problems.append("priors_consulted must be a non-empty list of "
                        "file:substring citations — no prior, no conjecture")
    else:
        for ev in priors:
            if not (isinstance(ev, dict) and ev.get("file") and ev.get("contains")):
                problems.append(f"prior is not a file:substring citation: {ev!r}")
                continue
            if not resolve_evidence(repo_root, ev).get("resolved"):
                problems.append(f"prior does not resolve on disk (ghost): "
                                f"{ev.get('file')} ∌ {ev.get('contains')!r}")

    return problems


def is_grounded(repo_root, cta):
    """True iff the ScoutCTA passes every tooth — schema, marks, expiry, and
    grounding. Convenience over validate()."""
    return not validate(repo_root, cta)


def render(repo_root, cta):
    problems = validate(repo_root, cta)
    lines = ["# ScoutCTA — a marked call to action (conjecture, not truth)", ""]
    lines.append(json.dumps(cta, indent=2, ensure_ascii=False))
    lines.append("")
    if problems:
        lines.append("REFUSED — this is not a lawful ScoutCTA:")
        for p in problems:
            lines.append(f"  · {p}")
    else:
        lines.append("VALID — schema-shaped, grounded, expiring, marked conjecture; "
                     "review_required, cannot land or mint (D-4).")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=REPO_ROOT,
                    help="repo root for grounding citations (default: this repo)")
    ap.add_argument("--json", action="store_true",
                    help="emit the fixture as JSON, not the rendered prose")
    args = ap.parse_args(argv)

    if args.json:
        print(json.dumps(FIXTURE, indent=2, ensure_ascii=False))
    else:
        print(render(args.root, FIXTURE))
        print()
    problems = validate(args.root, FIXTURE)
    if problems:
        print(f"result: report — the fixture refuses ({len(problems)} problem(s)); "
              "the contract's teeth bit")
    else:
        print("result: done — the fixture is a lawful ScoutCTA: grounded, "
              "expiring, marked conjecture (cannot land or mint, D-4)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
