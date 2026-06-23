#!/usr/bin/env python3
"""The loop-maker (done-line 0084): the Plan seam of the loop's MAPE-K cycle.

bdo, 2026-06-15: "make a loop maker based on the current state, from the
previous loop, into the next, and … braid, fold, knot, connect or loop together
in some sound way each previous and prior loop to create something
controllable." Named via the loops skill: this is MAPE-K, and the **K**
(Knowledge base) that braids one iteration to the next is the append-only
log/records on disk — never a session's memory.

This module owns only the **Plan** step: given the current state (a fold over
the records) it derives the *next increment* to build for a named epic. It does
NOT re-build the Monitor (`loop.reconcile`'s Fold), the Analyze
(`loop.temporal`, `loop.gaps` — the ranked pressure field), or the Execute (the
records pen). It is the missing seam between the pressure read and the next
done-line (§10: a composing addition, not a second fold).

The braid is sound because the connection is on disk: a landed increment ties
its done-line to its epic piece with a `> **Piece:** <atom-id>` line, so the
next derivation folds over `.ai-native/done/` and *cannot not-see* the prior
loop's work. Loop N writes a tie; loop N+1's fold reads it. That is the
controllable closed loop — setpoint (the epic's ordered pieces), error (the
unlanded ones), brake (Stop when converged or stuck).

Pure stdlib. `next_increment` is a read-only fold — it never writes a record.
`operate` is the thin marking seam (done-line 0092): a `Stop` leaves a foldable
signal so the harvest can farm the stopping point. The fold stays pure; only the
seam writes.
"""

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

from loop.reconcile import load_epics

# the tie a landed done-line carries back to its epic piece — the on-disk
# connection that makes the braid sound (a fold reads it; memory cannot fake it)
PIECE_TIE = re.compile(r"^>\s*\*\*Piece:\*\*\s*(\S+)", re.MULTILINE)
# atom.<core>.vN  ->  <core>  (the derived, boring slug for the next done-line)
_ATOM_CORE = re.compile(r"^atom\.(.+?)(?:\.v\d+)?$")


@dataclass(frozen=True)
class Increment:
    """The next increment the loop should build: an epic piece with no landed
    done-line tie yet, carried with the derived done-line slug/title and the
    arc's own words for what it is (the piece's glue)."""
    epic_id: str
    atom: str
    slug: str
    title: str
    glue: Optional[str] = None


@dataclass(frozen=True)
class Stop:
    """The brake. A healthy halt, not an error: `converged` (every piece is
    landed), `stuck` (the next piece is blocked on an unmet dependency), or
    `no-epic` (the named arc is on no epic file). The loop-maker refuses to
    fabricate a next step when state says there is none — that refusal is the
    §10 teeth."""
    reason: str
    detail: str = ""


def landed_pieces(root):
    """The set of epic-piece atom ids that already carry a landed done-line —
    the fold over `.ai-native/done/` for the `> **Piece:**` tie. This is the
    braid surface: the only thing connecting one loop to the next, and it lives
    on disk, so it survives mortal sessions and cannot be faked by memory."""
    done = Path(root) / "done"
    out = set()
    if not done.is_dir():
        return out
    for path in sorted(done.glob("*.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        for m in PIECE_TIE.finditer(text):
            out.add(m.group(1))
    return out


def _slug_of(atom_id):
    m = _ATOM_CORE.match(atom_id)
    core = m.group(1) if m else atom_id
    return core.replace(".", "-")


def _title_of(atom_id):
    return _slug_of(atom_id).replace("-", " ").strip().capitalize()


def _epic_by_id(epics, epic_id):
    for epic in epics:
        if epic.get("id") == epic_id:
            return epic
    return None


def next_increment(epic_id, *, root=Path(".ai-native")) -> Union[Increment, Stop]:
    """Derive the next increment for `epic_id` from current state, or a Stop.

    Pure over (the epic file, the landed-piece fold): deterministic, stdlib, no
    double-build. Walks the epic's pieces *in order* and returns the first one
    with no landed done-line tie — unless that piece is blocked on an unmet
    dependency (then `Stop("stuck")`), or every piece is landed (then
    `Stop("converged")`). Order is honoured strictly: a blocked next piece
    stops the loop rather than skipping ahead, so the braid never advances past
    a joint that has not set."""
    root = Path(root)
    epic = _epic_by_id(load_epics(root), epic_id)
    if epic is None:
        return Stop("no-epic",
                    f"{epic_id!r} is on no epic file under "
                    f"{(root / 'epics').as_posix()}")
    landed = landed_pieces(root)
    for piece in epic.get("pieces", []):
        atom = piece.get("atom")
        if not atom or atom in landed:
            continue
        # the first unlanded piece in arc order. Is its joint set? A piece may
        # declare machine-readable `depends` (atom ids); any unlanded one blocks.
        unmet = [d for d in piece.get("depends", []) if d not in landed]
        if unmet:
            return Stop("stuck",
                        f"next piece {atom} is blocked on unmet "
                        f"dependency: {', '.join(unmet)}")
        return Increment(epic_id=epic_id, atom=atom, slug=_slug_of(atom),
                         title=_title_of(atom), glue=piece.get("glue"))
    return Stop("converged",
                f"every piece of {epic_id} carries a landed done-line tie")


def operate(epic_id, *, root=Path(".ai-native")):
    """`next_increment`, but a `Stop` leaves a mark (done-line 0092): the loop's
    stopping point becomes a recorded signal the harvest can farm — "the refusal
    is the signal," landed. The pure derivation is untouched; this seam is the
    only writer. Returns the Increment or Stop unchanged."""
    result = next_increment(epic_id, root=root)
    if isinstance(result, Stop):
        from loop import signals
        signals.mark(root, f"loop-stop:{result.reason}", epic_id, result.detail)
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("epic_id", help="the arc to derive the next increment for")
    ap.add_argument("--root", type=Path, default=Path(".ai-native"),
                    help="the records root (defaults to .ai-native)")
    args = ap.parse_args(argv)
    result = operate(args.epic_id, root=args.root)
    if isinstance(result, Increment):
        print(f"result: report — next increment for {result.epic_id}: "
              f"{result.atom}")
        print(f"  slug : {result.slug}")
        print(f"  title: {result.title}")
        print("  mint : python -m loop.pen new done "
              f"--slug {result.slug} --title \"{result.title}\" --body -")
        print("         (the body must carry "
              f"`> **Piece:** {result.atom}` to braid it back)")
        if result.glue:
            print(f"  glue : {result.glue}")
        return 0
    print(f"result: report — stop ({result.reason}): {result.detail}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
