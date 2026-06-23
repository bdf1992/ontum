#!/usr/bin/env python3
"""The reversibility gate (done-line 0088): the safety spine of
epic.digital-experience.

bdo, 2026-06-15, wants the system to handle the digital world "so I can live in
the physical world and not have to worry." That reads as autonomy — which
collides head-on with ontum's standing doctrine that the human acts by gesture
and the machine only proposes. The discussion found the one line that reconciles
them: cut on **reversibility / blast-radius**.

- A **reversible**, zero-commitment act — pre-stage a surface, render a view,
  draft, scan — the system does **autonomously, with no gesture**. Guessing
  wrong costs nothing but a dismissed panel.
- An **irreversible / outward** act — send, delete, purchase, publish — is
  **gated behind a gesture**, always.
- And the gate **never guesses an act safe**: an unclassified verb is treated as
  irreversible, blocked until a gesture authorizes it. An honest gap is refused
  conservatively, never silently allowed (the loop/tags.py rule: an unknown verb
  is a surfaced gap, not a guess).

This v0 is a verb-keyed classifier in the `loop/tags.py` grain; it composes with
the anima arc's Risk/blast-radius assay when that lands (the assay measures
*how* irreversible; this gate draws the autonomy line). Pure stdlib, read-only:
it decides and explains, it acts on nothing.
"""

import argparse
from dataclasses import dataclass
from pathlib import Path

# reversible, zero-commitment acts — autonomous, no gesture. Pre-staging is the
# whole point: anticipate cheaply, dismiss freely.
REVERSIBLE = frozenset({
    "pre-stage", "prestage", "open", "render", "draft", "scan", "read",
    "prepare", "cache", "preview", "suggest", "highlight", "propose", "stage",
})
# irreversible / outward acts — gated behind a gesture, always.
IRREVERSIBLE = frozenset({
    "send", "email", "post", "publish", "delete", "purchase", "pay", "submit",
    "overwrite", "share", "deploy", "install", "uninstall", "move", "rename",
})


def classify(verb):
    """The act's reversibility: 'reversible', 'irreversible', or 'unknown'.
    Unknown is honest — an unrecognised verb is a surfaced gap, and the gate
    treats it as irreversible rather than guessing it safe."""
    v = (verb or "").strip().lower()
    if v in REVERSIBLE:
        return "reversible"
    if v in IRREVERSIBLE:
        return "irreversible"
    return "unknown"


@dataclass(frozen=True)
class Decision:
    allowed: bool
    needs_gesture: bool
    reversibility: str
    reason: str


def gate(act, *, gesture=None):
    """Decide whether an act may proceed. `act` carries at least a `verb`;
    `gesture` is the person's authorization (truthy = authorized).

    Reversible -> allowed autonomously. Irreversible (or unknown, treated as
    irreversible) -> allowed only with a gesture; otherwise blocked with a
    legible reason. The gate never guesses an act safe."""
    verb = act.get("verb")
    rev = classify(verb)

    if rev == "reversible":
        return Decision(
            allowed=True, needs_gesture=False, reversibility=rev,
            reason=f"reversible act {verb!r}: done autonomously, no gesture "
                   "(zero-commitment, freely dismissed)")

    treated = ("irreversible/outward" if rev == "irreversible"
               else f"unclassified (treated as irreversible — the gate never "
                    f"guesses an act safe)")
    if gesture:
        return Decision(
            allowed=True, needs_gesture=True, reversibility=rev,
            reason=f"{treated} act {verb!r}: authorized by gesture {gesture!r}")
    return Decision(
        allowed=False, needs_gesture=True, reversibility=rev,
        reason=f"{treated} act {verb!r}: blocked — needs a gesture to proceed")


def operate(act, *, gesture=None, mark_root):
    """`gate`, but a blocked act leaves a mark (done-line 0092): a refused
    irreversible/unknown act becomes a recorded signal the harvest can farm.
    `mark_root` is the records root (`.ai-native`). The pure `gate`/`classify`
    are untouched; this seam is the only writer. Returns the Decision."""
    d = gate(act, gesture=gesture)
    if not d.allowed:
        from loop import signals
        signals.mark(mark_root, f"gate-block:{d.reversibility}",
                     str(act.get("verb")), d.reason)
    return d


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("verb", help="the act's verb (e.g. pre-stage, send, delete)")
    ap.add_argument("--gesture", default=None,
                    help="the person's authorization (truthy = authorized)")
    ap.add_argument("--mark-root", type=Path, default=Path(".ai-native"),
                    help="records root for block signals (default .ai-native)")
    args = ap.parse_args(argv)
    d = operate({"verb": args.verb}, gesture=args.gesture, mark_root=args.mark_root)
    verdict = "allowed" if d.allowed else "blocked"
    print(f"result: report — {verdict} ({d.reversibility}): {d.reason}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
