#!/usr/bin/env python3
"""The Observable-as-gate (epic.relation-governed-exploration): observability
is gated FIRST, before an autonomous exploratory act runs.

The doctrine reordering this module enacts: Observable is the substrate from
which reversibility, boundedness, and learning-progress are all computed — you
cannot say an act is reversible, bounded, or that it taught you anything if you
cannot first attribute its effect back to the actor that caused it. So
Observable is not one gate among five; it is the gate the others stand on, and
it is checked before the act runs.

The action-gate (`fence/policy.py`, `command_guard.py`) answers a different
question: *is this command in the family of things a session may type?* A
read-only `git status`, an in-bounds Write, a `python -m loop.summon` — all
pass it, because none is a forbidden tool surface. But "the action is allowed"
is not "the act is observable": an autonomous exploratory act can be perfectly
in-bounds and still run *unattributable* — leaving an effect on the world that
no receipt ties back to its actor. That act is exactly what this gate refuses.
It is the consequence-gate the action-gate structurally cannot be: the
action-gate sees the verb, never the receipt path.

Before an autonomous exploratory act runs it must DECLARE:

  actor             who acts — the identity the effect attributes to
  action            the intended action (the command or act about to run)
  scope             the scope it touches (paths, records, surfaces)
  expected_receipt  the receipt the act will write — the sink the effect
                    lands in, so the act leaves a trace at all
  attribution_path  how the effect ties back to the actor: the chain
                    effect -> receipt -> actor. This is the load-bearing
                    field — the others can be named and the act can still be
                    un-attributable if this chain does not terminate at the
                    actor.
  rollback_path     how the act is rolled back or revisited
  relation_id       (exploratory acts only) the relation/probe the act
                    belongs to — what it is exploring

If the declaration cannot NAME its receipt path — if `expected_receipt` or
`attribution_path` is absent, or the attribution chain does not terminate at
the declared actor — the act HALTS and surfaces. It does not run. A halt is
not a failure; it is the gate doing its one job: refusing to let an effect
loose that nothing could trace home.

`gate(declaration)` is a pure function. Stdlib only, no log, no network — the
gate is a predicate over a declaration, deterministic and side-effect-free.
The CLI prints the contract read-only.

CLI:
  python -m loop.observe          the gate contract (required fields, refusal)
  python -m loop.observe --json   the contract as data (machine-readable)

Ends with a clear result on stdout (D-6): done.
"""

import argparse
import json
import sys

# The fields every autonomous exploratory act must declare, each with the
# story of why it is required (a cold reader of a halt knows what to add).
FIELDS = {
    "actor": "who acts — the identity the effect attributes to",
    "action": "the intended action (the command or act about to run)",
    "scope": "the scope it touches (paths, records, surfaces)",
    "expected_receipt": "the receipt the act will write — the sink the "
                        "effect lands in",
    "attribution_path": "how the effect ties back to the actor "
                        "(effect -> receipt -> actor)",
    "rollback_path": "how the act is rolled back or revisited",
}

# An exploratory act carries one more: the relation/probe it explores. Required
# only when the declaration marks itself exploratory (`exploratory: true`).
EXPLORATORY_FIELD = "relation_id"
EXPLORATORY_GLOSS = "the relation/probe this exploratory act belongs to"

# The two fields that ARE the receipt/attribution path — the consequence-gate's
# core. Naming them lets the well-formedness check target them, and lets a test
# prove the check is load-bearing by neutralizing exactly these.
RECEIPT_FIELDS = ("expected_receipt", "attribution_path")

REQUIRED_FIELDS = tuple(FIELDS)


def _present(value):
    """A declared field counts as named only when it is a non-empty string
    once stripped — None, "", and whitespace are all absence (the gate never
    accepts a blank as a name)."""
    if value is None:
        return False
    return bool(str(value).strip())


def required_fields(declaration):
    """The fields this declaration must carry — the base set, plus the
    relation/probe id when the act marks itself exploratory."""
    fields = list(REQUIRED_FIELDS)
    if declaration.get("exploratory"):
        fields.append(EXPLORATORY_FIELD)
    return fields


def missing_fields(declaration):
    """The required fields the declaration fails to name, in declared order."""
    return [f for f in required_fields(declaration)
            if not _present(declaration.get(f))]


def attribution_halt(declaration):
    """The receipt/attribution-path well-formedness check — the gate's core
    tooth. Returns a halt reason, or None when the path is well-formed.

    Presence of the fields is assumed (missing_fields runs first); this asks
    the harder question: does the named path actually attribute the effect?
    A receipt can be named and the chain can still dangle — name a sink but
    never tie it to the actor, and the effect lands somewhere that cannot be
    traced home. Well-formed means the attribution chain TERMINATES at the
    declared actor: the actor's identity appears in the path.
    """
    actor = str(declaration.get("actor") or "").strip()
    receipt = str(declaration.get("expected_receipt") or "").strip()
    path = str(declaration.get("attribution_path") or "").strip()
    if not receipt:
        return ("no expected receipt named — the act's effect lands in no "
                "sink that could attribute it")
    if not path:
        return ("no attribution path named — the effect cannot be traced "
                "back to its actor")
    if actor and actor not in path:
        return (f"attribution path does not terminate at the actor: {actor!r} "
                f"is absent from the chain, so the effect cannot be traced "
                f"home — the act halts and surfaces")
    return None


def gate(declaration):
    """The Observable-as-gate, pure: does this act declare an attributable
    receipt path, so its effect can be traced back to its actor?

    Returns a verdict {cleared, halt_reason, missing}. Cleared only when every
    required field is present AND the receipt/attribution path is well-formed.
    Anything less HALTS — the act surfaces rather than running unobserved.
    """
    decl = declaration if isinstance(declaration, dict) else {}
    missing = missing_fields(decl)
    if missing:
        return {
            "cleared": False,
            "halt_reason": ("under-declared: the act cannot name "
                            f"{', '.join(missing)}; it halts and surfaces "
                            "rather than running unobserved"),
            "missing": missing,
        }
    reason = attribution_halt(decl)
    if reason:
        return {"cleared": False, "halt_reason": reason, "missing": []}
    return {"cleared": True, "halt_reason": None, "missing": []}


CONTRACT = {
    "gate": "observable-as-gate",
    "doctrine": "Observable is gated first — it is the substrate reversibility, "
                "boundedness, and learning-progress are computed from",
    "rule": "before an autonomous exploratory act runs it must declare an "
            "attributable receipt path; if it cannot name one, the act halts "
            "and surfaces — it does not run",
    "required_fields": FIELDS,
    "exploratory_extra": {EXPLORATORY_FIELD: EXPLORATORY_GLOSS},
    "receipt_path_fields": list(RECEIPT_FIELDS),
    "well_formed": "expected_receipt names a sink AND attribution_path "
                   "terminates at the declared actor (effect -> receipt -> "
                   "actor)",
    "verdict_shape": {"cleared": "bool", "halt_reason": "str|None",
                      "missing": "[field]"},
}


def render_contract():
    print("observable-as-gate — observability is gated FIRST (before the act runs)")
    print()
    print("Every autonomous exploratory act must declare:")
    for field, gloss in FIELDS.items():
        marker = "  (the receipt path)" if field in RECEIPT_FIELDS else ""
        print(f"  {field:18s} {gloss}{marker}")
    print(f"  {EXPLORATORY_FIELD:18s} {EXPLORATORY_GLOSS} "
          "(exploratory acts only)")
    print()
    print("Refusal rule: if the act cannot NAME its receipt path — "
          "expected_receipt absent,")
    print("attribution_path absent, or the attribution chain not terminating "
          "at the actor —")
    print("the act HALTS and surfaces. It does not run. An allowed action is "
          "not an")
    print("observable act: the action-gate sees the verb, this gate sees the "
          "receipt path.")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true",
                    help="emit the gate contract as data")
    args = ap.parse_args(argv)

    if args.json:
        print(json.dumps(CONTRACT, indent=2, ensure_ascii=False))
    else:
        render_contract()
    print("result: done — the observable-as-gate contract (read-only); a "
          "declaration clears only when it names an attributable receipt path")
    return 0


if __name__ == "__main__":
    sys.exit(main())
