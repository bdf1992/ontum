#!/usr/bin/env python3
"""The experience unit (atom.experience.v0 — epic.experience-layer, wave 3).

PROVISIONAL term, owed to the glyph-knolling grip ritual before it is minted:
an *experience* is a launched, bounded encounter — one ambient beat composed
with one place and one granted expectation, handed to one summoned backing,
that must terminate in an authored story or a verdict from a named set. Its
non-example is an ambient briefing line: context injected without obligation is
weather, not an experience, and weather is what the ambient hook already gives.

This module is the unit and its birth-gate, nothing more: the typed record and
the one rule that an experience which obligates nothing is refused at birth.
Launching experiences from beats is the launcher (the next piece); processing
one into a story is the author (wave 4). It composes the surface registry
(reflect), the trust ladder (the backing's rung), and the capability that the
return shape obligates. Stdlib only; reads the log, writes nothing.
"""

from __future__ import annotations

import argparse
import json
import sys

from loop.reconcile import DEFAULT_ROOT, Fold
from loop import reflect, trust

# The ambient beats an experience may be born from — the launcher's sources,
# each a pure fold that already exists somewhere in the loop.
SOURCE_BEATS = {
    "open-summons": "an atom awaits an admitted-real node (summon)",
    "surface-drift": "a registered surface lags the owner's queue (reflect)",
    "mock-temperature": "a fixed-verdict gate is still a mock (ambient)",
    "records-collision": "two records claim one address (placement)",
    "dropped-source": "a read-only source went unconverted to an atom",
}
# What a returned shape obligates -> the rung the backing must hold to make it.
SHAPE_RUNG = {"story": "author", "verdict": "judge"}
FIELDS = ("source_event", "surface", "context", "expectation", "backing")


def experience_refusal(exp, root=DEFAULT_ROOT):
    """Why an experience may not be born, or None. The birth-gate: an
    experience that obligates nothing is weather, and weather is refused. Pure
    over the log and the record, so the suite hits it directly."""
    beat = exp.get("source_event")
    if beat not in SOURCE_BEATS:
        return f"unknown source beat {beat!r}; born from a beat: " + ", ".join(SOURCE_BEATS)
    context = exp.get("context")
    if not context or (isinstance(context, str) and not context.strip()):
        return "no composed context — the place an experience stands in is required (D-9)"
    surface = exp.get("surface")
    if surface not in reflect.registered_surfaces(Fold(root)):
        return (f"surface {surface!r} is not registered — an experience lands on "
                "an admitted surface (the surface-registry pattern)")
    expectation = exp.get("expectation") or {}
    shape = expectation.get("shape")
    if shape not in SHAPE_RUNG:
        return f"expectation shape {shape!r} must be one of: " + ", ".join(SHAPE_RUNG)
    if not (expectation.get("terminal_set") or []):
        return ("the expectation obligates nothing — a non-empty terminal_set is "
                "required, or this is weather, not an experience")
    backing = exp.get("backing") or {}
    cls = backing.get("class")
    if cls not in trust.AGENT_CLASSES:
        return f"backing class {cls!r} is not an agent class: " + ", ".join(trust.AGENT_CLASSES)
    need = SHAPE_RUNG[shape]
    if not trust.permits(cls, need, root):
        return (f"backing {cls} holds no '{need}' rung — it cannot return a "
                f"{shape}; bdo grants it (admit-rung) before this experience runs")
    return None


def describe(exp):
    """A one-line cold-reader summary of an experience (provenance, not value)."""
    exp = exp or {}
    e = exp.get("expectation") or {}
    b = exp.get("backing") or {}
    return (f"{exp.get('source_event','?')} -> {exp.get('surface','?')}: a "
            f"{b.get('class','?')} must return a {e.get('shape','?')} from "
            f"{e.get('terminal_set', [])}")


# ----------------------------------------------------------------- read CLI

def cmd_beats(_ns):
    print("source beats an experience may be born from:")
    for beat, gloss in SOURCE_BEATS.items():
        print(f"  {beat} — {gloss}")
    print("return shapes (and the rung each obligates): "
          + ", ".join(f"{s}->{r}" for s, r in SHAPE_RUNG.items()))
    print("result: report — an experience composes a beat, a surface, a context, "
          "an obligating expectation, and a rung-checked backing")
    return 0


def cmd_check(ns):
    exp = json.loads(ns.json)
    reason = experience_refusal(exp, ns.root)
    if reason:
        print(f"result: needs-you — refused at birth: {reason}")
        return 2
    print(f"result: report — born: {describe(exp)}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("beats", help="the source beats and return shapes (read-only)")
    b.set_defaults(func=cmd_beats)
    c = sub.add_parser("check", help="validate one experience record (JSON) against the birth-gate")
    c.add_argument("--json", required=True, help="the experience record as JSON")
    c.add_argument("--root", default=DEFAULT_ROOT)
    c.set_defaults(func=cmd_check)
    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
