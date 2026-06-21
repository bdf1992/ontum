#!/usr/bin/env python3
"""The Claim part (done-line 0158): the bridge from a conjectural ScoutCTA to
bounded work — read-only, propose-only.

The Scout lobe emits one marked call to action (a ScoutCTA). Left alone, that
is overgrowth: a possibility floating with no edge. Claim gives it an edge. It
does **not** prove the CTA — proving is the Build loop's job (gate -> stamp ->
land). Claim only says: *this frontier is bounded enough to work or watch.* It
turns a conjecture into a `claimed_frontier` — a typed, budgeted, expiring unit
of intent that a session or bdo can pick up, or that Prune can later retire.

The teeth (§10), reusing the contract with no second truth: Claim only ever
bounds a **valid** conjecture — it runs `scout_cta.validate` first and REFUSES
to claim an invalid or ungrounded ScoutCTA (you cannot bound what was never a
lawful conjecture). Every claim it produces is itself **bounded** — it carries
a non-empty `exit_condition` and `expiry` (an unbounded claim is the overgrowth
this part exists to prevent). And it never **proves**: the claim adds no truth,
carries provenance that is not `minted`, and never sets `truth_claim`/`minted`.

Read-only and propose-only (D-4): Claim bounds; it never judges, proves, mints,
or lands. The bounded work, once owned, runs through the normal pipeline.

CLI:
  python -m loop.claim --cta <path.json>     bound one ScoutCTA (from a file)
  python -m loop.claim --demo                bound the ScoutCTA fixture (demo)

Stdlib only, no network, no git. Ends with a clear result (D-6).
"""

import argparse
import json
import sys
from pathlib import Path

from loop import scout_cta

REPO_ROOT = Path(__file__).resolve().parents[1]

CLAIM_TYPES = ("arc", "epic", "spike", "branch", "watch", "defer")


def _derive_claim_type(cta):
    """The bounded form a ScoutCTA wants, read from the move's own shape — a
    real derivation (different CTAs -> different types), never a constant."""
    why = cta.get("why_this_move_now") or ""
    attn = (cta.get("attention_class") or "").lower()
    if why.startswith("[open-question"):
        return "watch"      # a fork to monitor, not yet actionable
    if why.startswith("[ready-for-confirm"):
        return "defer"      # it is bdo's stamp, not session work — hold
    if why.startswith("[advance-parked"):
        return "branch"     # resume an existing atom's work
    if attn == "small":
        return "spike"      # a bounded first cut at a new piece
    return "arc"            # a large move wants its own arc


def _derive_exit(cta, claim_type):
    """A bounded exit, from the claim type — never empty (an unbounded claim is
    overgrowth). The expiry is the other bound and is inherited from the CTA."""
    return {
        "watch": "the watched signal fires (re-Scout), or the expiry passes (then Prune)",
        "defer": "the blocking precondition clears (re-evaluate), or the expiry passes",
        "branch": "the atom advances through the pipeline, or the expiry passes (then Prune)",
        "spike": "the bounded cut is built and gated, or the expiry passes (then Prune)",
        "arc": "the arc is proposed and bdo confirms it, or the expiry passes",
        "epic": "the arc is proposed and bdo confirms it, or the expiry passes",
    }.get(claim_type, "the work lands or the expiry passes (then Prune)")


def claim(repo_root, cta):
    """Bound one ScoutCTA into a claimed_frontier — or refuse. Writes nothing.
    Proves nothing: it only gives a valid conjecture an edge."""
    problems = scout_cta.validate(repo_root, cta)
    if problems:
        return {"status": "refused", "subject": cta.get("cta"),
                "reason": ("cannot claim an invalid or ungrounded ScoutCTA — Claim "
                           "bounds a real conjecture, it does not prove one: "
                           + "; ".join(problems))}
    ctype = _derive_claim_type(cta)
    expiry = cta.get("expiry")  # inherit the conjecture's decay — the claim is mortal too
    return {
        "status": "claimed_frontier",
        "source_purpose": cta.get("purpose"),
        "source_cta": cta.get("cta"),
        "claim_type": ctype,
        "owner": "unassigned — a session or bdo picks it up",
        "guard_policy": ("read-only until owned; the bounded work then runs through "
                         "the normal pipeline (value-gate -> owner-stamp -> land)"),
        "budget": cta.get("cost") or "one review pass",
        "review_date": expiry,
        "exit_condition": _derive_exit(cta, ctype),
        "expiry": expiry,
        "provenance": "proposed",
        "truth_claim": False,
        "minted": False,
    }


def render(out):
    if out.get("status") == "refused":
        return ("# Claim — REFUSED (an unlawful conjecture is not claimable)\n"
                f"  subject: {out.get('subject')}\n  why: {out.get('reason')}")
    lines = ["# Claimed frontier — a conjecture given an edge (not proven)", "",
             json.dumps(out, indent=2, ensure_ascii=False), "",
             "BOUNDED — carries an exit_condition and an expiry; proposed, not "
             "minted; the work runs the normal pipeline once owned (D-4)."]
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--cta", type=Path, help="a ScoutCTA JSON file to bound")
    ap.add_argument("--demo", action="store_true",
                    help="bound the ScoutCTA fixture (loop.scout_cta.FIXTURE)")
    ap.add_argument("--root", type=Path, default=REPO_ROOT)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    if args.demo:
        cta = scout_cta.FIXTURE
    elif args.cta:
        cta = json.loads(args.cta.read_text(encoding="utf-8"))
    else:
        ap.error("pass --cta <path.json> or --demo")

    out = claim(args.root, cta)
    if args.json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        print(render(out))
        print()
    if out.get("status") == "refused":
        print(f"result: report — Claim refused ({out.get('reason', '')[:70]}…); "
              "nothing bounded")
    else:
        print(f"result: done — one bounded claimed_frontier [{out['claim_type']}] "
              "from a valid conjecture; proposed, not proven (D-4)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
