#!/usr/bin/env python3
"""The act-fence (done-line 0174): ask-forgiveness as a risk-tiered authority
dial over ACTS — the disposer's bounded standing auto-admit, lifted off the
setpoint dials and onto acts in general.

bdo, 2026-06-21: *"we might also want to install ask for forgiveness on some
risk levels."* The repo already had ask-forgiveness in exactly one place —
`loop/disposer.py` auto-admits an in-fence *setpoint* change citing bdo's
standing fence, never signing its own line. This module is that pattern
generalized: the question "may this act run unattended, or must it stop and ask
bdo?" is answered by where the act falls on a reversibility x blast-radius cut
bdo draws once.

Three tiers — the middle the action-gate's `forbidden | prompt` never had:

  FORGIVENESS  reversible + contained -> act, log, surface as FYI (self-admit)
  PERMISSION   reversible-but-wide, or anything bdo must weigh -> stop and ask
  FORBIDDEN    irreversible / outward / as-the-owner -> never, no fence saves it

The cut is keyed to ontum's *real gestures*, not abstract "risk":
  - an owner gesture (`confirm-arc`, `admit-real`, drawing a fence) is FORBIDDEN
    to self-admit — it IS bdo's authorization; only he makes it (D-4);
  - anything that reaches *outside the repo* or acts *as the owner*, or that no
    utensil can undo, is FORBIDDEN — no fence authorizes it;
  - **landing a PR to main is the hinge**: FORGIVENESS *iff* a confirmed arc
    already authorized it (the merge-node executing bdo's standing stamp, and
    git-revertable), else PERMISSION — the tier reads the *authorization
    context*, not the verb;
  - reversible and contained to the record or a branch (drafting, a local
    commit, writing a proposal, a read-only fold) is FORGIVENESS;
  - everything else weighs out to PERMISSION.

Composition, not a new engine (no double-build, §10):
  - `observe.gate` runs FIRST (`loop/observe.py`): an act that cannot name an
    attributable receipt path HALTS before any tier is read — you cannot call an
    act reversible if you cannot trace its effect home. Observable is the
    substrate the tier is computed on.
  - the fence is an `act_fence` admission, bdo-signed, naming which
    forgiveness-scoped acts may self-admit — read at runtime (I-8), inert until
    drawn, exactly like the disposer's `auto_admit_fence`. Default-safe: with no
    fence, nothing self-admits — every forgiveness act escalates.
  - an `admit` cites the fence as `authorized_by` (the loop executes bdo's
    standing stamp, it never signs its own line — the disposer / merge-node
    shape). `fence/policy.py` is *not* the home: it denies static argv, and acts
    are data-dependent (the same verb is forgiveness or permission by its scope).

Read-only / propose-only in this slice: it classifies and SHOWS; it actuates no
real act. The actuator (a session act actually self-admitting through this) and
bdo's first fence ride later done-lines, gated on his stamp (D-4). Witness
before actuator — the grain of `gaps` / `heal` / `census`.

CLI:
  python -m loop.act_fence          the cut + each catalogued act's tier (read-only)
  python -m loop.act_fence --json   the dataset (machine-readable)
"""

import argparse
import json
import sys
from pathlib import Path

from loop.reconcile import DEFAULT_ROOT, Fold
from loop.observe import gate as observe_gate

FENCE_TYPE = "act_fence"

# The tiers, widest-authority last (forbidden is the floor no fence lifts).
FORGIVENESS = "forgiveness"
PERMISSION = "permission"
FORBIDDEN = "forbidden"
TIERS = (FORGIVENESS, PERMISSION, FORBIDDEN)

# The blast radii, narrowest first. "contained" (record/branch) is the band a
# forgiveness act may live in; main is the hinge; outward leaves our reach.
CONTAINED = ("record", "branch")

# The acts that ARE bdo's authorization — a fence can never self-admit one,
# because that would be the loop authorizing itself (D-4). Distinct from merely
# high-risk: these are owner gestures by their nature, forbidden at any fence.
OWNER_GESTURES = frozenset({
    "confirm-arc", "admit-real", "draw-fence", "supersede-done",
    "admit-setpoint", "grant-rung", "admit-policy",
})

# A coarse verb -> family map for acts that do not declare a family explicitly.
# Modest on purpose: the catalogue and real callers declare `family` directly;
# this only keeps a bare `action` string from being unclassifiable.
_FAMILY_HINTS = (
    ("confirm-arc", "confirm-arc"),
    ("admit-real", "admit-real"),
    ("force", "destructive"),
    ("reset --hard", "destructive"),
    ("land", "land-main"),
    ("merge", "land-main"),
)


def infer_family(action):
    """A best-effort family for an act that did not declare one. Returns the
    family string, or None when the verb is unknown (an honest gap — the gate
    then leans on blast_radius/reversible, never a silent guess at the verb)."""
    a = (action or "").lower()
    for needle, family in _FAMILY_HINTS:
        if needle in a:
            return family
    return None


def classify(act):
    """Pure: the tier this act falls in, and why. Reads `family` (or infers it),
    `blast_radius`, `reversible`, and — for the landing hinge — `arc_confirmed`.

    The teeth (§10): the tier reads the *authorization context*, not the verb.
    The same `land-main` act is forgiveness under a confirmed arc and permission
    without one; and declaring an outward act `reversible` does not buy it
    forgiveness — blast radius is read before reversibility for the wide bands.

    Returns (tier, reason).
    """
    family = act.get("family") or infer_family(act.get("action"))
    blast = act.get("blast_radius")
    reversible = bool(act.get("reversible"))

    if family in OWNER_GESTURES:
        return FORBIDDEN, (f"{family!r} is an owner gesture (D-4) — a fence can "
                           "never self-admit bdo's own authorization; only he makes it")
    if family == "destructive":
        return FORBIDDEN, ("irreversible / history-rewriting — no fence "
                           "authorizes it, no utensil undoes it")
    if blast == "outward":
        return FORBIDDEN, ("reaches outside the repo / acts as the owner — past "
                           "the reach of our rollback utensils, so no fence authorizes it")

    if family == "land-main":
        if act.get("arc_confirmed") and reversible:
            return FORGIVENESS, ("landing under a confirmed arc — the merge-node "
                                 "executing bdo's standing stamp, and git-revertable")
        return PERMISSION, ("landing to main without a confirmed arc — bdo weighs "
                            "it; the arc-confirm is the authorization that would lift it")

    if blast in CONTAINED and reversible:
        return FORGIVENESS, (f"reversible and contained to {blast} — undoable by an "
                             "existing utensil, nothing escapes the record/branch")

    # reversible-but-wide (e.g. a main-scoped non-landing act), or contained but
    # not reversible: bdo weighs it. The catch-all is PERMISSION, never silent allow.
    if not reversible:
        return PERMISSION, ("no rollback path to make it reversible — contained, "
                            "but bdo weighs an un-undoable act")
    return PERMISSION, (f"reversible but blast_radius {blast!r} is wider than a "
                        "contained record/branch — bdo weighs it")


def valid_fence(forgivable):
    """A fence authorizes a non-empty set of forgiveness *scope tags* (families)
    for self-admission. Returns (ok, reason)."""
    if not isinstance(forgivable, (list, tuple)) or not forgivable:
        return False, "a fence names at least one forgivable scope tag"
    if not all(isinstance(x, str) and x.strip() for x in forgivable):
        return False, "every forgivable scope tag is a non-empty string"
    return True, None


def read_fence(admissions):
    """The act-fence in force, read at runtime (I-8): the latest well-formed
    `act_fence` admission wins. None when bdo has drawn none — the dial is then
    inert (every forgiveness act escalates, default-safe)."""
    fence = None
    for adm in admissions:
        if adm.get("type") == FENCE_TYPE:
            ok, _ = valid_fence(adm.get("forgivable"))
            if ok:
                fence = adm
    return fence


def fence_authorizes(fence, act):
    """Does the drawn fence authorize self-admission of this act's scope? The
    act's `family` (or its declared `scope_tag`) must be one the fence names."""
    if not fence:
        return False
    tag = act.get("family") or infer_family(act.get("action")) or act.get("scope_tag")
    return tag in set(fence.get("forgivable", []))


def evaluate(fence, act):
    """The decision over (fence, act): halt | deny | escalate | admit, composing
    the consequence-gate first.

    Order is load-bearing: `observe.gate` runs before any tier is read — an act
    whose effect cannot be traced home HALTS, because reversibility and
    containment are claims you cannot make about an unobservable act. Then the
    tier; then, only for a forgiveness act, the fence.

    Returns {"verdict", "tier", "reason", ...}.
    """
    obs = observe_gate(act)
    if not obs["cleared"]:
        return {"verdict": "halt", "tier": None,
                "reason": obs["halt_reason"], "observe": obs}

    tier, reason = classify(act)
    if tier == FORBIDDEN:
        return {"verdict": "deny", "tier": tier, "reason": reason}
    if tier == PERMISSION:
        return {"verdict": "escalate", "tier": tier, "reason": reason}

    # FORGIVENESS — the only tier a fence can lift to self-admission.
    if fence_authorizes(fence, act):
        return {"verdict": "admit", "tier": tier, "reason": reason,
                "authorized_by": fence["id"]}
    return {"verdict": "escalate", "tier": tier,
            "reason": reason + " — but no act_fence authorizes this scope; "
            "inert until bdo draws one"}


# A handful of representative ontum acts, each a complete declaration (the
# observe.gate fields + the tier inputs), so the read-only render shows the cut
# made legible. The landing hinge appears twice — confirmed and not — to show
# the tier reading the authorization context.
ACT_CATALOG = [
    {
        "label": "run a read-only fold (loop.gaps)",
        "actor": "session", "action": "python -m loop.gaps",
        "scope": "none (read-only)", "family": "read-fold",
        "blast_radius": "record", "reversible": True,
        "expected_receipt": "stdout (no write)",
        "attribution_path": "effect -> stdout -> session",
        "rollback_path": "none needed — reads nothing it could break",
    },
    {
        "label": "draft on a branch + local commit",
        "actor": "session", "action": "git commit on claude/act-fence",
        "scope": "loop/act_fence.py (a branch)", "family": "draft",
        "blast_radius": "branch", "reversible": True,
        "expected_receipt": "the commit object + branch ref",
        "attribution_path": "commit -> branch ref -> session",
        "rollback_path": "git restore / delete the branch (whiteout)",
    },
    {
        "label": "land a PR to main UNDER a confirmed arc",
        "actor": "merge-node", "action": "pr.py land --epic <id>",
        "scope": "main", "family": "land-main",
        "blast_radius": "main", "reversible": True, "arc_confirmed": True,
        "expected_receipt": "rcp.merge.<n> on receipts.jsonl",
        "attribution_path": "merge receipt -> confirm-arc -> bdo (authorized) / merge-node (executed)",
        "rollback_path": "git revert the merge commit",
    },
    {
        "label": "land a PR to main with NO confirmed arc",
        "actor": "merge-node", "action": "pr.py land",
        "scope": "main", "family": "land-main",
        "blast_radius": "main", "reversible": True, "arc_confirmed": False,
        "expected_receipt": "rcp.merge.<n> on receipts.jsonl",
        "attribution_path": "merge receipt -> ??? -> merge-node",
        "rollback_path": "git revert the merge commit",
    },
    {
        "label": "confirm an arc (bdo's gesture)",
        "actor": "session", "action": "loop.node confirm-arc",
        "scope": "admissions.jsonl", "family": "confirm-arc",
        "blast_radius": "record", "reversible": True,
        "expected_receipt": "arc_confirmed admission",
        "attribution_path": "admission -> session",
        "rollback_path": "supersede (--off)",
    },
    {
        "label": "force-push (history rewrite)",
        "actor": "session", "action": "git push --force",
        "scope": "a remote branch", "family": "destructive",
        "blast_radius": "main", "reversible": False,
        "expected_receipt": "the rewritten ref",
        "attribution_path": "ref -> session",
        "rollback_path": "none — history is gone",
    },
    {
        "label": "send outward AS the owner (an unobservable act)",
        "actor": "session", "action": "post a comment as bdo",
        "scope": "an external surface", "family": "outward-as-owner",
        "blast_radius": "outward", "reversible": False,
        # deliberately omits expected_receipt/attribution -> halts at observe
        "rollback_path": "none",
    },
]


def catalogue(root):
    """The catalogue evaluated under the fence in force — the read-only witness.
    Each act carries its tier (the cut) and its verdict today (what would
    happen). Pure fold; writes nothing."""
    fold = Fold(Path(root))
    fence = read_fence(fold.admissions)
    rows = []
    for act in ACT_CATALOG:
        decision = evaluate(fence, act)
        rows.append({"label": act["label"], **decision})
    return {"fence": fence, "rows": rows}


_VERDICT_GLOSS = {
    "admit": "act -> log -> FYI (self-admits under the fence)",
    "escalate": "stop and ask bdo",
    "deny": "refused outright (no fence lifts it)",
    "halt": "halts before the tier — unobservable",
}


def render(root):
    data = catalogue(root)
    fence = data["fence"]
    if fence:
        print(f"act-fence — by {fence['by']}: forgivable scopes "
              f"{', '.join(fence['forgivable'])}")
    else:
        print("act-fence — none drawn; the dial is inert (every forgiveness act "
              "escalates, default-safe). bdo draws one to let a scope self-admit.")
    print()
    print("the cut (reversibility x blast-radius, keyed to ontum's gestures):")
    print(f"  {FORGIVENESS:11s} reversible + contained -> act, log, FYI")
    print(f"  {PERMISSION:11s} reversible-but-wide / weigh-worthy -> stop and ask")
    print(f"  {FORBIDDEN:11s} irreversible / outward / owner-gesture -> never")
    print()
    for row in data["rows"]:
        tier = row["tier"] or "—"
        print(f"  [{tier:11s}] {row['label']}")
        print(f"      would: {row['verdict'].upper()} "
              f"({_VERDICT_GLOSS[row['verdict']]})")
        print(f"      why: {row['reason']}")
    return data


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    ap.add_argument("--json", action="store_true",
                    help="emit the catalogue dataset as data")
    args = ap.parse_args(argv)

    if args.json:
        print(json.dumps(catalogue(args.root), indent=2, ensure_ascii=False))
    else:
        render(args.root)
    print("result: done — the act-fence cut (read-only); it classifies and "
          "shows, it actuates no real act until bdo draws a fence (D-4)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
